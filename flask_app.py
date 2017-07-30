from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from cryptfolio import *
import numpy as np
import pandas as pd
import os
import time

app = Flask(__name__)

bootstrap = Bootstrap(app)

@app.route('/')
def home():

	out_dict, total =crypt_get("config.txt")

	# plot shares: 
	# if True:
	# 	pass

	names = np.array([x for x in out_dict])
	values = np.array([out_dict[x][2] for x in out_dict])

	try:
		os.remove('static/pie.jpg')
	except OSError:
		pass

	pie =  pd.Series(values, index=names)


	pie.plot(kind='pie').get_figure().savefig('static/pie.jpg')

	return render_template('table.html', 
							out_dict=out_dict,
							total=total,
							blockh=get_blockh())

if __name__ == '__main__':
	app.run()
