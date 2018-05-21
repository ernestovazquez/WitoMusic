from flask import Flask,render_template,redirect,request,session
import requests
from requests_oauthlib import OAuth1
from requests_oauthlib import OAuth2Session
from urllib.parse import parse_qs
import os,json

app = Flask(__name__)   

redirect_uri = 'https://witomusic.herokuapp.com/callback'
scope = ['playlist-read-private', 'playlist-read-collaborative']
token_url = "https://accounts.spotify.com/api/token"

app.secret_key= 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

def token_valido():
    try:
        token=json.loads(session["token_sp"])
    except:
        token = False
    if token:
        token_ok = True
        try:
            oauth2 = OAuth2Session(os.environ["client_id"], token=token)
            r = oauth2.get('https://api.spotify.com/v1/me')
        except TokenExpiredError as e:
            token_ok = False
    else:
        token_ok = False
    return token_ok


@app.route('/spotify')
def spotify():
    return render_template("oauth2_spotify.html")


@app.route('/perfil_spotify')
def info_perfil_spotify():
  if token_valido():
    return redirect("/perfil_usuario_spotify")
  else:
    oauth2 = OAuth2Session(os.environ["client_id"], redirect_uri=redirect_uri,scope=scope)
    authorization_url, state = oauth2.authorization_url('https://accounts.spotify.com/authorize')
    session.pop("token_sp",None)
    session["oauth_state_sp"]=state
    return redirect(authorization_url)  


@app.route('/callback')
def get_token_spotify():
    oauth2 = OAuth2Session(os.environ["client_id"], state=session["oauth_state_sp"],redirect_uri=redirect_uri)
    print (request.url)
    token = oauth2.fetch_token(token_url, client_secret=os.environ["client_secret"],authorization_response=request.url[:4]+"s"+request.url[4:])
    session["token_sp"]=json.dumps(token)
    return redirect("/perfil_usuario_spotify")


@app.route('/perfil_usuario_spotify')
def info_perfil_usuario_spotify():
    if token_valido():
        token=json.loads(session["token_sp"])
        oauth2 = OAuth2Session(os.environ["client_id"], token=token)
        r = oauth2.get('https://api.spotify.com/v1/me')
        doc=json.loads(r.content.decode("utf-8"))
        return render_template("perfil.html", datos=doc)
    else:
        return redirect('/perfil')


@app.route('/logout_spotify')
def salir_spotify():
    session.pop("token_sp",None)
    return redirect("/spotify")


@app.route('/')
def inicio():
	return render_template('index.html')



@app.route('/contact')
def contact():
	return render_template('contacto.html')


@app.route('/login')
def login():
  if token_valido():
    redirect("/playlist")
  else:
    response.set_cookie("token", '',max_age=0)
    oauth2 = OAuth2Session(client_id, redirect_uri=redirect_uri,scope=scope)
    authorization_url, state = oauth2.authorization_url('https://accounts.spotify.com/authorize/')
    response.set_cookie("oauth_state", state)
    redirect(authorization_url)




port=os.environ["PORT"]
app.run('0.0.0.0',int(port), debug=True)