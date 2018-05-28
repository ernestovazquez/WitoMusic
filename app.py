from flask import Flask,render_template,redirect,request,session
import requests
from requests_oauthlib import OAuth1
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import TokenExpiredError
from urllib.parse import parse_qs
import os,json
import uuid

app = Flask(__name__)   
app.secret_key= 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
app.jinja_env.filters['zip'] = zip

redirect_uri = 'https://witomusic.herokuapp.com/callback'
scope = ['playlist-read-private', 'playlist-read-collaborative']
token_url = "https://accounts.spotify.com/api/token"


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
        session["id"]=doc["id"]
        return render_template("perfil.html", datos=doc)
    else:
        return redirect('/perfil')



@app.route('/spotify')
def spotify():
    return render_template("oauth2_spotify.html")


@app.route('/logout_spotify')
def salir_spotify():
    session.pop("token_sp",None)
    return render_template('index.html')


@app.route('/')
def inicio():
    return render_template('index.html')

@app.route('/contact')
def contact():
	return render_template('contacto.html')

@app.route('/search')
def search():
    return render_template('buscadores.html')

    

@app.route('/playlist')
def playlist():
    if "token_sp" in session:
        if token_valido():
            token=json.loads(session["token_sp"])
            oauth2 = OAuth2Session(os.environ["client_id"], token=token)
            r = oauth2.get('https://api.spotify.com/v1/users/{}/playlists' .format(session["id"]))
            doc=json.loads(r.content.decode("utf-8"))
            return render_template("playlist.html", datos=doc)
        else:
            return redirect('/')
    else:
        return redirect('/spotify')


port=os.environ["PORT"]
app.run('0.0.0.0',int(port), debug=True)