from flask import Flask,request,url_for,render_template
from lxml import etree
from sys import argv
from requests_oauthlib import OAuth1
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import TokenExpiredError
import requests
import json
import os
app = Flask(__name__)

redirect_url = 'https://witomusic.herokuapp.com/callback'
scope = ['playlist-read-private', 'playlist-read-collaborative']
token_url = "https://accounts.spotify.com/api/token"
client_id=["7d037969ceb2431da15d42a216c2d9e3"]
client_secret=["87dd513deba04006a9e97557857a066d"]


def token_valido():
	token=request("token", secret='some-secret-key')
	if token:
		token_ok = True
		try:
			oauth2 = OAuth2Session(client_id, token=token)
			r = oauth2.get('https://www.googleapis.com/oauth2/v1/userinfo')
		except TokenExpiredError as e:
			token_ok = False
	else:
		token_ok = False
	return token_ok


@app.route('/')
def inicio():
	return render_template('index.html')


@app.route('/search',methods=["GET","POST"])
def search():
	return render_template('buscadores.html')


@app.route('/contact')
def contact():
	return render_template('contacto.html')



@app.route('/login')
def login():
  if token_valido():
    redirect("/playlist")
  else:
    response.set_cookie("token", '',max_age=0)
    oauth2 = OAuth2Session(client_id, redirect_url=redirect_url,scope=scope)
    authorization_url, state = oauth2.authorization_url('https://accounts.spotify.com/authorize/')
    response.set_cookie("oauth_state", state)
    redirect(authorization_url)




port=os.environ["PORT"]
app.run('0.0.0.0',int(port), debug=True)