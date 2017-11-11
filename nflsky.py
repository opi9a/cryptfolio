from bs4 import BeautifulSoup
import requests
from datetime import datetime as dt
from datetime import timedelta
from collections import OrderedDict
import calendar
from pprint import pprint


def clean_game(game):
	if game.endswith("Hlts"):
		game = game[:-4]
	if game.startswith("Live NFL"):
		game = game[8:]
	if game.startswith("NFL"):
		game = game[4:]	
	if game.startswith("Hlts"):
		game = game[4:]
	if game.startswith(":"):
		game = game[1:]		

	return(game.strip())


def get_u_time(raw_date, raw_time):
	'''Returns unix standard datetime object for the show.

	Parameters: 

		a raw date string ('DD-MM-YYYY') for the day of the Sky listing

		a raw time string, scraped from the Sky listing
	'''
	h = int(raw_time.split(",")[0].split(":")[0])
	m = raw_time.split(",")[0].split(":")[1][:2]
	ampm = raw_time.split(",")[0].split(":")[1][-2:]


	if h == 12: h = 0
	if ampm == "pm": h = h + 12

	return dt.strptime(raw_date+"-"+"-".join([str(h),m]), "%d-%m-%Y-%H-%M")



def tidy_shows(raw_shows, _debug=False, _scrape_fail=False):
	
	tidy_out = OrderedDict()
	time_now_mins = (dt.now().hour * 60) + dt.now().minute
	# today = "-".join([str(dt.now().day), str(dt.now().month), str(dt.now().year)])
	today = dt.now().strftime("%d-%m-%Y")
	show_started_buffer = 180 # number of mins into past to include shows
	morning_cutoff = 240 # defines the time (in mins) before which a game is assigned to prev night
	prev_day = None
	prev_showstrings = set()
	pad = 30

	if _debug: 
		print("today is".ljust(pad), today)
		print("debug".ljust(pad), _debug)
		print("scrape_fail".ljust(pad), _scrape_fail)

	for day in raw_shows:
		# make an entry in the final dictionary (for the day)
		if _debug: 
			print("\n\n" + "+"*110)
			print("day is".ljust(pad), day)
		tidy_out[day] = dict(day=raw_shows[day]['day'], games=[])
		showstrings = set()

		if _debug: print("prev showstrings ", prev_showstrings)

		# go through the games for that day in the raw output
		for raw_show in raw_shows[day]['games']:
			if _debug: 
				print("\n" + "-"*100)
				pprint(raw_show)
				print("")

			# initialise some variables	
			ignore = False
			showstring = (raw_show['raw_game'] + " " + raw_show['raw_time']).strip()
			game_dt = get_u_time(day, raw_show['raw_time']) # the universal time as a datetime object

			if _debug: 
				print("raw time:".ljust(pad), raw_show['raw_time'])
				print("game_dt:".ljust(pad), game_dt.strftime("%c"))

			# test if it's already been put in the day's shows
			if showstring in showstrings:
				ignore = True
				if _debug: print("ignoring as already found")


			# test if it's in the past - only if scrape has not failed
			if game_dt.timestamp() < (dt.now().timestamp() - (show_started_buffer * 60)) and not _scrape_fail:
				ignore = True
				if _debug: print("ignoring as in the past")

			# test if it's a live game, and there's a string in prev day's strings (can't justify doing for highlights, in case of genuine repetition)
			if showstring in prev_showstrings and "live" in showstring.lower():
				ignore = True
				if _debug: print("ignoring as it's a live game from previous day")

			# go ahead and add it, if not to be ignored
			if not ignore:
				show = {}  # the dictionary to build for this show
			
				show['game'] = clean_game(raw_show['raw_game'])	
				show['time'] = game_dt.strftime("%-I:%M %P")

				if game_dt.hour == 0: show['time'] = "0" + show['time'][2:]

				show['channel'] = raw_show['channel']
				show['u_time'] = game_dt.timestamp()//60

				# determine the type of show

				if raw_show['raw_game'].startswith("Live"):
					show['type'] = 'live'

				elif "hlts" in raw_show['raw_game'].lower():
					show['type'] = 'HIGHLIGHTS'

				else:
					show['type'] = 'unknown'
					show['game'] = raw_show['raw_game']

				# check if it needs moving to previous night

				revised_day = day
				day_mins = (game_dt.hour * 60) + game_dt.minute

				if _debug: print("day_mins is".ljust(pad), day_mins)

				if day_mins < morning_cutoff and prev_day is not None:
					if _debug: print("shifting to".ljust(pad), prev_day)
					revised_day = prev_day

				# append it to the games list
				tidy_out[revised_day]['games'].append(show)
				showstrings.add(showstring)

				if _debug: 
					print("")
					pprint(show)
					print("\nshowstrings ", showstrings)

		prev_day = day	
		prev_showstrings = showstrings

		# sort the games
		tidy_out[day]['games'] = sorted(tidy_out[day]['games'], key=lambda k: k['u_time'])

	return tidy_out
				



def get_by_game(tidied):
	'''Takes a dict organised by date, and returns on organised by game (then date)
	'''
	by_game = {}

	# make the dict
	for day in tidied:
	    for show in tidied[day]['games']:
	        # print("show is ", show)
	        show['day']=tidied[day]['day']
	        show['date']=day
	        
	        # can do this better with dict.setdefault() I think
	        if show['game'] not in by_game:
	            by_game[show['game']]=[show]
	        else: 
	            by_game[show['game']].append(show)


	# take out redzone	
	by_game.pop('Redzone', None)

	return by_game




def get_shows(days_hence):

	url_base = "http://www.skysports.com/watch/tv-guide/"

	# mon_yr = "".join(["-", str(dt.now().month), "-", str(dt.now().year)])
	start_day = dt.now().day
	start_weekday = dt.now().weekday()

	out = OrderedDict()
	last_date = None

	# get list of channels (ordered)
	print("getting initial page for channel list..")
	try:
		r = requests.get(url_base+dt.now().strftime("%d-%m-%Y"))
		soup = BeautifulSoup(r.text, 'html.parser')
		print("..OK")

	except: 
		print(".. failed")
		return 1
	
	chan_list = [x.split(" src=")[0][1:-1] for x in str(soup.find_all('img')).split("alt=")][1:-1]
	# print("chan list is ", chan_list)


	# now go through for real
	for d in range(days_hence):
		dt_new = dt.now() + timedelta(days=d)
		dt_string = dt_new.strftime("%d-%m-%Y")
		print("dt_string", dt_string)

	
		out[dt_string] = dict(day=calendar.day_name[(start_weekday+d)%7])
		out[dt_string]['games'] = []
		
		print("Getting shows for", out[dt_string]['day'], end=".. ")
		
		url = "".join([url_base, dt_string])
		print("url is ", url)
		
		try:
			r = requests.get(url)
			soup = BeautifulSoup(r.text, 'html.parser')
			print("..OK")

		except: print(".. failed")

		# get the shows for each channel
		chan_shows = []
		for i, tag in enumerate(soup.find_all("div", class_='row-table')):
		    shows = []
		    shows.extend([h.text.strip() for h in tag.find_all("h4")])
		    times = []
		    times.extend([p.text.strip() for p in tag.find_all("p")])
		    chan_shows.append(list(zip(shows, times)))
		chan_shows = chan_shows[1:]		

		# winnow down to only nfl shows
		nfl_shows = []
		for c in chan_shows:
		    nfl_shows.append([x for x in c if 
		    		("nfl" in x[0].lower()) and("live" in x[0].lower() or "hlts" in x[0].lower())])


		# now append out list
		for i, chan in enumerate(chan_list):
		    for s in nfl_shows[i]:
		        out[dt_string]['games'].append(dict(raw_game=s[0], raw_time=s[1], channel=chan))
		

		last_date = dt_string


	return out