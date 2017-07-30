from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from cryptfolio import *
import numpy as np
import pandas as pd
import os
import datetime

app = Flask(__name__)

bootstrap = Bootstrap(app)

@app.route('/')
def home():

	out_dict, total =crypt_get("config.txt")

	debg=None

	names = np.array([x for x in out_dict])
	prices = np.array([out_dict[x][0] for x in out_dict])
	vols = np.array([out_dict[x][1] for x in out_dict])
	values = np.array([out_dict[x][2] for x in out_dict])

	try:
		os.remove('static/pie.jpg')
	except OSError:
		pass

	timestamp = datetime.datetime.now()

# open last
	price_record = pd.DataFrame(data=prices, index = names, columns=[timestamp])

	if os.path.isfile('hist.csv'):
		hist = pd.read_csv('hist.csv', index_col=0)
		hist.columns=pd.to_datetime(hist.columns)
		# debg = hist.columns

		last_prices = hist.iloc[:,-1]
		for coin in last_prices.index:
			out_dict[coin].append(last_prices[coin])
		hist.join(price_record).to_csv('hist.csv')
		last_total = sum(last_prices*vols)
		last_time=hist.iloc[:,-1].name
	else:
		price_record.to_csv('hist.csv')
		for coin in out_dict:
			out_dict[coin].append(0)
		last_total = 0
		last_time=0

	val_hist = hist.T*vols
	val_hist.plot(kind='area', stacked=True, ylim=0).get_figure().savefig('static/history.jpg')

	pie =  pd.Series(values, index=names)
	pie.plot(kind='pie', 
			figsize=(15,6)).get_figure().savefig('static/pie.jpg')


	return render_template('table.html', 
							out_dict=out_dict,
							timestamp=timestamp.strftime('%d/%m/%Y %H:%M:%S'),
							total=total,
							last_total=last_total,
							last_time=last_time.strftime('%d/%m/%Y %H:%M:%S'),
							debg=debg,
							blockh=get_blockh())

if __name__ == '__main__':
	app.run()
