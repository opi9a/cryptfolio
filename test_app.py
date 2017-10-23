from flask import Flask, render_template, session, redirect, url_for
from flask_bootstrap import Bootstrap
from cryptfolio import *
import numpy as np
import pandas as pd
from datetime import datetime
import calendar
import json

import nflsky

app = Flask(__name__)
app.config['SECRET_KEY']="YeCqhrYGgBqrwH5XRHuj4XFBmY"

bootstrap = Bootstrap(app)

@app.route('/')
def home(conf="config.txt"):

	# get `basics` of portfolio (coins, vols, tickers) from session dict 
	# if it exists, or create it (NB: *once*, that's the point) if it doesn't

	# (NB can't use setdefault here, as default is still evaluated, 
	# defeating the purpose - so just use if else)

	if 'basics' in session.keys():
		basics=session['basics']

	else:
		basics=get_basics(conf)#[ticks,vols]
		session['basics']=basics

	# also get time portfolio was read from session dictionary.
	# (don't care if default called as no resources needed)
	t_base = session.setdefault('timestamp', 
					datetime.now().strftime('%a %-d %b, %-H:%M:%S'))

	# and time now
	t_now = datetime.now().strftime('%a %-d %b, %-H:%M:%S')


	# Build df with all the info, starting with `basics`

	df=pd.DataFrame(basics).set_index('coins')

	df=df.join(get_multi(list(df['ticks'])),on='ticks')
	df['pcent_24h_ch']=df['ch24h_gbp']/(df['ch24h_gbp']+df['prices_gbp'])

	df['values']=df['prices_gbp']*df['vols']
	total = sum(df['values'])
	df['value_24h_ch']=df['ch24h_gbp']*df['vols']
	df['val_pcent_24h_ch']=df['value_24h_ch']/(df['value_24h_ch']+df['values'])

	total_ch = sum(df['value_24h_ch'])
	total_perc_ch = total_ch/(total_ch+total)

	df['shares']=df['values']/total

	btc_proportion=df.loc['bitcoin','values']/df.loc['bitcoin','cap_gbp']
	df['weight']=((df['values']/df['cap_gbp'])/btc_proportion)
	df['£PPPW']=btc_proportion*df['cap_gbp']*0.01

	temp_dict = {df.loc[i,'ticks']:df.loc[i,'values'] for i in df.index.values}

	print(temp_dict)

	return render_template('test_frame.html', 
							df=df, 
							total=total, total_ch=total_ch, total_perc_ch=total_perc_ch,
							temp_dict = json.dumps(temp_dict), t_now=t_now)

@app.route('/reset/')
def reset():
	print("\nin reset\n")
	session.clear()
	return redirect(url_for('home'))

@app.route('/nfl/')
def nfl():
	
	start_day = datetime.now().weekday()
	out = nflsky.get_shows(6)
	print(out)
	print(nflsky.tidy_shows(out))
	return render_template('nflsky.html', out=nflsky.tidy_shows(out), start_day=calendar.day_name[start_day])



if __name__ == '__main__':
	app.run()