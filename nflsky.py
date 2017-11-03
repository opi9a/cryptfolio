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

def get_time_str(string):
    ampm = string[-2:]
    mins = string.split(":")[1][:-2]
    hours = string.split(":")[0]
    if hours == '12' and ampm == "am": hours = '0'
    return "".join([hours, ":", mins, " ", ampm])

# def get_time_mins(string):
#     ampm = string[-2:]
#     mins = int(string.split(":")[1][:-2])
#     hours = int(string.split(":")[0])
#     print("\ninitial hours, ", str(hours).rjust(4), ampm)
#     if hours == 12: hours = 0
#     if ampm == "pm": hours = hours + 12
#     print("subsequent hours, ", str(hours))
#     return (hours*60) + mins

def get_u_min(string):
	'''Takes a date string DD-MM-YY and returns min in unix time
	'''
	return int(dt.strptime(string, "%d-%m-%Y").timestamp()//60)

def tidy_shows(raw_shows):
	
	tidy_out = OrderedDict()
	time_now_mins = (dt.now().hour * 60) + dt.now().minute
	today = "-".join([str(dt.now().day), str(dt.now().month), str(dt.now().year)])
	morning_cutoff = 240 # defines the time (in mins) before which a game is assigned to prev night
	prev_day = None

	for day in raw_shows:
		# make an entry in the final dictionary (for the day)
		tidy_out[day] = dict(day=raw_shows[day]['day'], games=[])
		showstrings = set()

		# go through the games for that day in the raw output
		for i, raw_show in enumerate(raw_shows[day]['games']):
			ignore = False
			showstring = (raw_show['raw_game'] + " " + raw_show['raw_time']).strip()

			t_raw = raw_show['raw_time'].split(",")[0]
			print("t_raw ", t_raw)
			print("after split ", t_raw[:-2])
			print("get str ", get_time_str(t_raw[:-2]).split(" ")[0])
			t_mins = get_u_min(get_time_str(t_raw[:-2]).split(" ")[0])
			# if t_mins == 720: t_mins = 0 # prev midnight

			# test if it's already been put in the day's shows
			if showstring in showstrings:
				ignore = True

			# test if it's in the past
			if day == today:			
				if (t_mins < time_now_mins - 180): #
					ignore = True


			if not ignore:
				show={}
				
				show['game'] = clean_game(raw_show['raw_game'])	
				raw_h = t_raw.split(":")[0]
				if raw_h == '12': raw_h = '0'
				show['time'] = get_time_str(t_raw)
				show['t_mins'] = t_mins
				show['channel'] = raw_show['channel']
				show['u_time'] = get_u_min(day) + t_mins

				if raw_show['raw_game'].startswith("Live"):
					show['type'] = 'live'


				elif "hlts" in raw_show['raw_game'].lower():
					show['type'] = 'HIGHLIGHTS'

				else:
					show['type'] = 'unknown'
					show['game'] = raw_show['raw_game']

				# check if it needs moving to previous night				
				revised_day = day
				# print("revised day", revised_day)
				if t_mins < morning_cutoff and prev_day is not None:
					revised_day = prev_day

				# append it to the games list
				# print("show ", show)
				tidy_out[revised_day]['games'].append(show)
				showstrings.add(showstring)

		prev_day = day	

		# sort the games
		tidy_out[day]['games'] = sorted(tidy_out[day]['games'], key=lambda k: k['t_mins'])



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

	# sort each game
	# for game in by_game:
	    # by_game[game] = sorted(by_game[game], key=lambda k:k['min_ad'])

	# now sort whole thing
	# by_game = sorted(by_game, key=lambda k:k[0]['min_ad'])

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