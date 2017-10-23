from bs4 import BeautifulSoup
import requests
from datetime import datetime as dt
from collections import OrderedDict
import calendar


def tidy_shows(raw_shows):
	
	tidy_out = OrderedDict()

	for day in raw_shows:
		# make an entry in the final dictionary (for the day)
		tidy_out[day] = dict(day=raw_shows[day]['day'], games=[])
		showstrings = set()
		print("the day is ", raw_shows[day]['day'])
		print("length of games is ", len(raw_shows[day]['games']))

		# go through the games for that day in the raw output
		for i, raw_show in enumerate(raw_shows[day]['games']):
			print("In game number ", i)
			print("number of showstrings is ", len(showstrings))
			showstring = raw_show['raw_game'] + " " + raw_show['raw_time']
			print("looking at ", showstring)

			# test if it's already been put in the day's shows
			if showstring in showstrings:
				print("found ", showstring, " in showstrings")

			else:
				# build a show dict to append to the games list
				show={}

				if "redzone" in raw_show['raw_game'].lower():
					show['type'] = 'redzone'
				
				elif raw_show['raw_game'].startswith("Live"):
					show['type'] = 'live'


				elif "hlts" in raw_show['raw_game'].lower():
					show['type'] = 'highlights'

				else:
					show['type'] = 'unknown'
				
				show['game'] = raw_show['raw_game']
				show['time'] = raw_show['raw_time'].split(",")[0]

				# append it to the games list
				tidy_out[day]['games'].append(show)

				print("adding showstring ", showstring)
				showstrings.add(showstring)
				print("number of showstrings is ", len(showstrings))

		print("showstrings for ", day, " are: ", showstrings)
	
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
		
		url = "".join([url_base, date])
		r = requests.get(url)
		soup = BeautifulSoup(r.text, 'html.parser')

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