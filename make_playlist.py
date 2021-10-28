import requests
from bs4 import BeautifulSoup
import unicodedata
import re
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy.util as util
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

def get_list(URL):
  #on cherche la page et on test la validité
  page = requests.get(URL)
  try:
        page.raise_for_status()
  except Exception as exc:
        print("there was a problem: %s" % (exc))
        exit(2)
  #on parse avec Bsoup
  soup = BeautifulSoup(page.text, 'html.parser')
  #On cherche la liste en bullet dans html
  list_container = soup.find_all('ul')
  #on renvoi la liste avec artiste/titre/album
  return list_container[27]

def get_title(URL):
  page = requests.get(URL)
  #on parse avec Bsoup
  soup = BeautifulSoup(page.text, 'html.parser')
  #On cherche le titre dans le h1
  title_container = soup.find('h1')
  #on renvoi le titre en format string
  vgt = 'Very good trip : '+title_container.text
  return vgt

def get_artist(liste):
  #récupération des balises STRONG dans la liste
  children = liste.findChildren("strong" , recursive=True)
  artiste = []
  #parsing et nettoyage du format
  for child in children:
    childo = child.text.rsplit(':',1)[0]
    childi = childo.rsplit(',')[0]
    child_clean = unicodedata.normalize("NFKD", childi)
    artiste.append(child_clean.rstrip())
  return artiste 

def get_track(liste):
  #nettoyage des lignes vides
  s = liste.text.split('\n')
  while("" in s) :
    s.remove("")
  #récupération du titre par regex entre « »
  pattern = "«\s(.*?)\s»"
  track = []
  #nettoyage de l'encodage
  for line in s :
     titre_dirty = re.search(pattern, line).group(1)
     titre_clean = unicodedata.normalize("NFKD", titre_dirty)
     track.append(titre_clean)
  return track

def get_uri_artiste(artiste):
  artist_genre = []
  uri = []
  artist_id = []
  artist_name = []
  popularity = []
  for count,artiste in enumerate(artiste):
    track_result = sp.search(q=artiste, type = 'artist', limit = 50)
    for j in range(len(track_result['artists']['items'])):
      A = track_result['artists']['items'][j]
      fuzz_ratio = fuzz.ratio(A['name'].lower(), artiste.lower())
      if fuzz.ratio(A['name'].lower(), artiste.lower()) > 95:
        artist_name.append(A['name'])
        artist_genre.append(A['genres'])
        artist_id.append(A['id'])
        uri.append(A['uri'])
        popularity.append(A['popularity'])    
        print("l\'artiste {} été trouvé avec une correspondance de {}%. Son ID est {}".format(artiste,fuzz_ratio,A['id']))
        break
      else:
        print("lartiste {} n'a pas été trouvé".format(artiste))
  return artist_name,uri,artist_id,popularity,artist_genre

def get_uri_track(titre):
  artist_genre = []
  uri = []
  artist_id = []
  artist_name = []
  popularity = []
  for i in titre:
    track_result = sp.search(q=i, type = 'track')
    A = track_result['artists']['items'][0]
    artist_genre.append(A['genres'])
    artist_id.append(A['id'])
    uri.append(A['uri'])
    artist_name.append(A['name'])
    popularity.append(A['popularity'])

  return artist_name,uri,artist_id,popularity,artist_genre

def get_track_id(titre):
  T_list = dict(zip(titre,info_artiste[2]))
  A_list = dict(zip(titre,info_artiste[0]))
  A_id = []
  T_id = []
  track_id = []
  for a,b in T_list.items():
    for retry in range(10):
      track_result = sp.search(q=(A_list[a],a), type=('track','artist'),limit = 50 )
      for i in range(len(track_result['tracks']['items'])):
        for j in range (len(track_result['tracks']['items'][i]['artists'])):
          id_artiste = track_result['tracks']['items'][i]['artists'][j]['id']
          id_track = track_result['tracks']['items'][i]['id']
          A_id.append(id_artiste)
          T_id.append(id_track)
          if track_result['tracks']['total'] == 0: #if track isn't on spotify as queried, go to next track
            print('titre absent de spotify :/')
            continue
    Id_list = dict(zip(A_id,T_id)) 
    if T_list[a] in Id_list:
      print('le track id est {} pour le titre {} de lartiste {}'.format(Id_list[T_list[a]],a, A_list[a]))
      track_id.append(Id_list[T_list[a]])
      continue
    else :
      print('Recherche plus précise pour pour le titre {} de lartiste {}'.format(Id_list[T_list[a]],a, A_list[a]))
      w = 0
      track_result = sp.search(q=a, type= 'track', limit=50)
      w += 1
      for item in range(len(track_result['tracks']['items'])):
        for artist_name in range (len(track_result['tracks']['items'][item]['artists'])):
          artiste = track_result['tracks']['items'][item]['artists'][artist_name]['name']
          id_artiste = track_result['tracks']['items'][item]['artists'][artist_name]['id']
          id_track = track_result['tracks']['items'][item]['id']
          for k in range(len(info_artiste[2])):
            if id_artiste == info_artiste[2][k]:       
              print('trouvé lartiste : ' + artiste+ ' id track est = ' +id_track+ ' id artiste est = ' + id_artiste)
              track_id.append(id_track)
              k += 1
          if len(track_id) == w:
            break 
  return track_id

def GetPlaylistID(username, titre_playlist):
    playlist_id = ''
    playlists = sp.user_playlists(username)
    print('recherche du numéro de playlist')
    for playlist in playlists['items']:  # iterate through playlists I follow
        if playlist['name'] == titre_playlist:  # filter for newly created playlist
            playlist_id = playlist['id']
    print('l\'id de la playlist est {}'.format(playlist_id))
    return playlist_id


#connecton spotify
cid = ''
secret = ''
client_credentials_manager = SpotifyClientCredentials(client_id=cid, client_secret=secret)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
username=''
scope="playlist-modify-private,playlist-modify-public"

token = util.prompt_for_user_token(username,scope,client_id=cid,client_secret=secret,redirect_uri='http://localhost:8888/callback') 
sp = spotipy.Spotify(auth=token) 

#récupération de la liste
URL_test = 'https://www.franceinter.fr/emissions/very-good-trip/very-good-trip-du-jeudi-21-octobre-2021'
Liste_entiere = get_list(URL_test)
titre_playlist = get_title(URL_test)
print('la playlist a pour titre : {}'.format(titre_playlist))
#récupération des artistes
print('récupération de la liste des artistes')
artiste = get_artist(Liste_entiere)  
print(artiste) 
#récupération des titres
print('récupération de la liste de titre')
titre = get_track(Liste_entiere)
print(titre)
#récupération des Uri/id
print('récupération des ID artiste')
info_artiste = get_uri_artiste(artiste)
#création de la playlist
print('création de la playlist {}'.format(titre_playlist))
sp.user_playlist_create(username, name = titre_playlist)

#test_df = pd.DataFrame({'artistes' : info_artiste[0], 'titres' : titre, 'uri' : info_artiste[1], 'artist_id' : info_artiste[2], 'popularity' : info_artiste[3], 'artist_genre' : info_artiste[4]})

playlist_id = GetPlaylistID(username, titre_playlist)
#récupération des id des morceau de la playlist
print('récupération des ids des morceaux pour la playlist {} : {}'.format(playlist_id,titre_playlist))
track_ids = get_track_id(titre)
#ajout des id à la playlist
print('ajout des morceaux pour la playlist {} : {}'.format(playlist_id,titre_playlist))
sp.user_playlist_add_tracks(username, playlist_id, track_ids)