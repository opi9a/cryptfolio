from flask import Flask, render_template, session, redirect, url_for
from flask_bootstrap import Bootstrap
from cryptfolio import *
import numpy as np
import pandas as pd
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY']="AJFPRG"

bootstrap = Bootstrap(app)

@app.route('/')
def home(conf="config.txt"):

	t_base = session.setdefault('timestamp', 
					datetime.now().strftime('%a %-d %b, %-H:%M:%S'))
	t_now = datetime.now().strftime('%a %-d %b, %-H:%M:%S')
	# need to make a useful data structure here. can't use df
	# (NB can't use setdefault here, as default is still evaluated)

	if 'basics' in session.keys():
		basics=session['basics']

	else:
		basics=get_basics(conf)#[ticks,vols]
		session['basics']=basics

	# Get 24h change, mktcap

	# Build df

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

	return render_template('test_frame.html', 
							df=df, 
							total=total, total_ch=total_ch, total_perc_ch=total_perc_ch,
							t_now=t_now)

@app.route('/reset/')
def reset():
	print("\nin reset\n")
	session.clear()
	return redirect(url_for('home'))

if __name__ == '__main__':
	app.run()