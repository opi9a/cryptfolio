from bs4 import BeautifulSoup
import requests
from datetime import datetime as dt
from collections import OrderedDict
import calendar


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
			print("\nShowstrings are", showstrings)
			print("This showstring is", showstring)


			# test if it's already been put in the day's shows
			if showstring in showstrings:
				print("it's already in")
				ignore = True

			# test if it's in the past
			if day == today:
				t_mins = get_time_mins(raw_show['raw_time'].split(",")[0])
				if t_mins == 720: t_mins = 0 # prev midnight
				if (t_mins < time_now_mins - 180): #
					ignore = True


			if not ignore:
				print("have a show")
				show={}
				
				show['game'] = clean_game(raw_show['raw_game'])
				
				t = raw_show['raw_time'].split(",")[0]
				show['time'] = " ".join([t[:-2], " ", t[-2:]])

				if raw_show['raw_game'].startswith("Live"):
					show['type'] = 'live'


				elif "hlts" in raw_show['raw_game'].lower():
					show['type'] = 'HIGHLIGHTS'

				else:
					show['type'] = 'unknown'
					show['game'] = raw_show['raw_game']

				

				# append it to the games list
				tidy_out[day]['games'].append(show)
				print("adding a showstring")
				showstrings.add(showstring)
				print("showstrings now, ", showstrings)

	
	return tidy_out
				



def get_shows(days_hence):

	url_base = "http://www.skysports.com/watch/tv-guide/"

	mon_yr = "".join(["-", str(dt.now().month), "-", str(dt.now().year)])
	start_day = dt.now().day
	start_weekday = dt.now().weekday()

	days = days_hence
	out = OrderedDict()
	last_date = None

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

		for a in soup.find_all('a'):
			txt = str(a).lower()
			show = []
			if "nfl" in txt and (("hlts" in txt) or ("live" in txt)):
				for h in a.find_all('h4'):
					show.append(h.text.strip())
				for p in a.find_all('p'):
					show.append(p.text.strip())
				
				out[date]['games'].append(dict(raw_game=show[0],
										raw_time=show[1]))

		last_date = date


	return out