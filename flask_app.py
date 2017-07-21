from flask import Flask, render_template
from flask_bootstrap import Bootstrap
from cryptfolio import *

app = Flask(__name__)

bootstrap = Bootstrap(app)


tlist=[1,3,5]

@app.route('/')
def home():

	out_dict, total =crypt_get("config.txt")

	return render_template('table.html', 
							out_dict=out_dict,
							total=total)

if __name__ == '__main__':
	app.run(debug=True)