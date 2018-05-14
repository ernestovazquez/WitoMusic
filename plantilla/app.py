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



@app.route('/',methods=["GET","POST"])
def inicio():
	return render_template('index.html')




@app.route('/login', method='GET')
def login():
  if token_valido():
    redirect("#playlist")
  else:
    response.set_cookie("token", '',max_age=0)
    oauth2 = OAuth2Session(client_id, redirect_uri=redirect_uri,scope=scope)
    authorization_url, state = oauth2.authorization_url('https://accounts.spotify.com/authorize/')
    response.set_cookie("oauth_state", state)
    redirect(authorization_url)



@app.route('/callback', method='GET')
def get_token():
  oauth2 = OAuth2Session(client_id, state=request.cookies.oauth_state,redirect_uri=redirect_uri)
  token = oauth2.fetch_token(token_url, client_secret=client_secret,authorization_response=request.url)
  response.set_cookie("token", token,secret='some-secret-key')
  redirect("/playlist")




@app.route('/playlist', method='GET')
def personal():
	token = request.get_cookie("token", secret='some-secret-key')
	tokens = token["token_type"]+" "+token["access_token"]
	headers = {"Accept":"aplication/json","Authorization":tokens}
	perfil = requests.get("https://api.spotify.com/v1/me", headers=headers)
	if perfil.status_code == 200:
		cuenta = perfil.json()
		cuenta = cuenta["id"]
		url_playlists = "https://api.spotify.com/v1/users/"+str(cuenta)+"/playlists"
	listas = requests.get(url_playlists, headers=headers)
	if listas.status_code == 200:
		playlists_usuario = json.loads(listas.text)
		return template('playlist.html', listas_usuario=playlists_usuario)




if __name__ == '__main__':
	app.run('127.0.0.1', debug=True)