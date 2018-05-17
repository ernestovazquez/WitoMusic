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

redirect_uri = 'https://witomusic.herokuapp.com/callback'
scope = ['playlist-read-private', 'playlist-read-collaborative']
token_url = "https://accounts.spotify.com/api/token"



def token_valido():
	token=request.get_cookie("token", secret='some-secret-key')
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


@app.route('/playlist')
def playlist():
	return render_template('playlist.html')



port=os.environ["PORT"]
app.run('0.0.0.0',int(port), debug=True)