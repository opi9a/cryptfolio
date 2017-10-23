from bs4 import BeautifulSoup
import requests
from datetime import datetime as dt
from collections import OrderedDict
import calendar

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

	for day in out:
		for game in out[day]['games']:
			if game['raw_game'].startswith("Live"):
				game['type'] = 'live'
			elif game['raw_game'].endswith("Hlts"):
				game['type'] = 'highlights'
			else:
				game['type'] = 'unknown'
			game['time'] = game['raw_time'].split(",")[0]

			# game['day'] = calendar.day_name[]

				

		last_date = date


	return out