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


redirect_uri = 'https://witomusic.herokuapp.com/callback'
scope = ['playlist-read-private', 'playlist-read-collaborative']
token_url = "https://accounts.spotify.com/api/token"
URL_BASE = 'https://api.spotify.com/v1/search'

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

def espacioencanciones(cadena):
    cad = cadena.replace(' ', '+')
    return cad

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


@app.route('/search', methods=["GET", "POST"])
def search():
    if request.method == 'GET':
        return render_template('buscadores.html')
    else:
        titulo = request.form['titulo']
        if "token_sp" in session:
            if token_valido():
                token = json.loads(session['token_sp'])
                oauth2 = OAuth2Session(os.environ['client_id'], token = token)
                headers = {'Accept': 'application/json', 'Content-Type': 'application-json', 'Authorization': 'Bearer ' + session['token_sp']}
                pl_sp = {'q': espacioencanciones(titulo), 'type': 'track', 'limit': 1, 'market': 'ES'}
                r_sp = oauth2.get(URL_BASE, params = pl_sp, headers = headers)    
                if r_sp.status_code == 200:
                    js_sp = r_sp.json()
                    if len(js_sp['tracks']['items']) != 0:
                        datos_sp = {'titulo': js_sp['tracks']['items'][0]['name'], 'url': js_sp['tracks']['items'][0]['external_urls']['spotify']}
                        return render_template('buscadores.html', datos = datos_sp)
            else:
                return redirect('/')
        else:
            return redirect('/spotify')

@app.route('/nueva')
def nueva():
    return render_template("segundaplaylists.html")

@app.route('/creador', methods=["GET", "POST"])
def creador():
    if "token_sp" in session:
        if token_valido():
            token=json.loads(session["token_sp"])
            oauth2 = OAuth2Session(os.environ["client_id"], token=token, scope=scope)
            nombre = request.form.get('nombre')
            desc = request.form.get('desc')
            public = request.form.get('public')
            headers = {'Accept': 'application/json', 'Content-Type': 'application-json', 'Authorization': 'Bearer ' + session['token_sp']}
            payload={'name':nombre, 'description':desc, 'public':public}
            r = oauth2.post('https://api.spotify.com/v1/users/{}/playlists' .format(session["id"]), data=json.dumps(payload), headers=headers)
            doc=json.loads(r.content.decode("utf-8"))
            return redirect('/playlist')
        else:
            return redirect('/')
    else:
        return redirect('/spotify')

port=os.environ["PORT"]
app.run('0.0.0.0',int(port), debug=True)