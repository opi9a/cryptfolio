from flask import Flask, render_template, session, redirect, url_for
from flask_bootstrap import Bootstrap
from cryptfolio import *
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import calendar
import json
import pickle
import os
import getpass

import nflsky

app = Flask(__name__)
app.config['SECRET_KEY']="YeCqhrYGgBqrwH5XRHuj4XFBmY"

bootstrap = Bootstrap(app)

conf = "config.txt"


@app.route('/')
def home():

	# get `basics` of portfolio (coins, vols, tickers) from session dict 
	# if it exists, or create it (NB: *once*, that's the point) if it doesn't

	if 'basics' in session.keys():
		basics=session['basics']

	else:
		basics=get_basics(conf)#[ticks,vols]
		session['basics']=basics

	# get time portfolio was read from session dictionary, and time now.
	t_base = session.setdefault('timestamp', 
					datetime.now().strftime('%a %-d %b, %-H:%M:%S'))

	t_now = datetime.now().strftime('%a %-d %b, %-H:%M:%S')


	# Build df with all the info, taking `basics` as input
	df=make_df(basics)

	# calculate meta values
	totals = {}
	totals['total'] = sum(df['values'])
	totals['total_btc'] = sum(df['values_btc'])
	totals['total_ch'] = sum(df['value_24h_ch'])
	totals['total_perc_ch'] = totals['total_ch'] /(totals['total_ch'] +totals['total'] )

	print('totals', totals)

	# the following is for exploring js/d3 stuff - not actually used
	temp_dict = {df.loc[i,'ticks']:df.loc[i,'values'] for i in df.index.values}

	# this is a hack so I can show my total including fiat from crypto sold
	user = getpass.getuser()
	bonus = 0
	if user == 'gav': bonus = 68000

	return render_template('test_frame.html', df=df, totals=totals, bonus=bonus, user=user,
							temp_dict = json.dumps(temp_dict), t_now=t_now)

@app.route('/reset/')
def reset():
	print("\nin reset\n")
	session.clear()
	return redirect(url_for('home'))

@app.route('/historical/')
def historical():
	
	if 'basics' in session.keys():
		basics=session['basics']

	else:
		basics=get_basics(conf)#[ticks,vols]
		session['basics']=basics

	if not os.path.isdir('static/figs'):
		if not os.path.isdir('static'):
			os.makedirs('static/')
		os.makedirs('static/figs')

	plotfile = "".join(["/", plot_history(basics, session=session)])


	return render_template('historical_template.html', plotfile = plotfile)


@app.route('/interactive_history/')
def interactive_history():
	
	if 'basics' in session.keys():
		basics=session['basics']

	else:
		basics=get_basics(conf)#[ticks,vols]
		session['basics']=basics

	script, div = plot_history(basics, session=session, interactive=True)

	return render_template('interactive_historical_template.html', script = script, div=div)



@app.route('/nfl/')
def nfl():
	
	start_day = datetime.now().weekday()
	start_date=datetime.now()
	end_date=start_date + timedelta(days=7)
	scrape_fail = False
	
	# try:
	tidied = nflsky.tidy_shows(nflsky.get_shows(7))
	start_date=start_date.strftime("%-d %b")
	end_date=end_date.strftime("%-d %b")
		
		# with open("out.pkl", 'wb') as f:
		# 	pickle.dump(out, f, pickle.HIGHEST_PROTOCOL)
	
	# except:
	# 	# use a pickled version - only when internet down
	# 	scrape_fail = True
	# 	with open("out.pkl", 'rb') as f: 
	# 		out = pickle.load(f)
	# 	tidied = nflsky.tidy_shows(out, _debug=True, _scrape_fail=True)
	# 	start_date = "SCRAPING FAILED - showing last cached record, "
	# 	end_date = out[list(out.keys())[-1]]['day'] + " " + list(out.keys())[-1]
	
	by_game = nflsky.get_by_game(tidied)
	return render_template('nflsky.html', out=tidied, by_game=by_game, 
										start_date=start_date,
										end_date=end_date)



if __name__ == '__main__':
	app.run()