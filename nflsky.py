from bs4 import BeautifulSoup
import requests
from datetime import datetime as dt
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


def get_time_mins(string):
    ampm = string[-2:]
    mins = int(string.split(":")[1][:-2])
    hours = int(string.split(":")[0])
    if ampm == "pm": hours = hours + 12
    return (hours*60) + mins


def tidy_shows(raw_shows):
	
	tidy_out = OrderedDict()
	time_now_mins = (dt.now().hour * 60) + dt.now().minute
	today = "-".join([str(dt.now().day), str(dt.now().month), str(dt.now().year)])
	

	for day in raw_shows:
		# make an entry in the final dictionary (for the day)
		print("\nnew day: ", day)
		tidy_out[day] = dict(day=raw_shows[day]['day'], games=[])
		showstrings = set()

		# go through the games for that day in the raw output
		for i, raw_show in enumerate(raw_shows[day]['games']):
			ignore = False
			showstring = (raw_show['raw_game'] + " " + raw_show['raw_time']).strip()

			t_raw = raw_show['raw_time'].split(",")[0]
			t_mins = get_time_mins(t_raw)
			if t_mins == 720: t_mins = 0 # prev midnight

			# test if it's already been put in the day's shows
			if showstring in showstrings:
				ignore = True

			# test if it's in the past
			if day == today:			
				if (t_mins < time_now_mins - 180): #
					ignore = True


			if not ignore:
				print("have a show")
				show={}
				
				show['game'] = clean_game(raw_show['raw_game'])		
				show['time'] = " ".join([t_raw[:-2], " ", t_raw[-2:]])
				show['t_mins'] = t_mins
				show['channel'] = raw_show['channel']

				if raw_show['raw_game'].startswith("Live"):
					show['type'] = 'live'


				elif "hlts" in raw_show['raw_game'].lower():
					show['type'] = 'HIGHLIGHTS'

				else:
					show['type'] = 'unknown'
					show['game'] = raw_show['raw_game']

				

				# append it to the games list
				tidy_out[day]['games'].append(show)
				showstrings.add(showstring)

		# sort the games
		tidy_out[day]['games'] = sorted(tidy_out[day]['games'], key=lambda k: k['t_mins'])
	
	return tidy_out
				



def get_shows(days_hence):

	url_base = "http://www.skysports.com/watch/tv-guide/"

	mon_yr = "".join(["-", str(dt.now().month), "-", str(dt.now().year)])
	start_day = dt.now().day
	start_weekday = dt.now().weekday()

	days = days_hence
	out = OrderedDict()
	last_date = None

	# get list of channels (ordered)
	print("getting initial page for channel list..")
	try:
		r = requests.get(url_base+"".join([str(start_day), mon_yr]))
		soup = BeautifulSoup(r.text, 'html.parser')
		print("..OK")

	except: 
		print(".. failed")
		return 1
	
	chan_list = [x.split(" src=")[0][1:-1] for x in str(soup.find_all('img')).split("alt=")][1:-1]
	print("chan list is ", chan_list)


	# now go through for real
	for d in range(days):
		date = "".join([str(start_day+d), mon_yr])
		
		out[date] = dict(day=calendar.day_name[(start_weekday+d)%7])
		out[date]['games'] = []
		
		print("Getting shows for", out[date]['day'], end=".. ")
		
		url = "".join([url_base, date])
		
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
		        out[date]['games'].append(dict(raw_game=s[0], raw_time=s[1], channel=chan))
		

		last_date = date


	return out