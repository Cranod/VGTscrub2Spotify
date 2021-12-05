import requests
from bs4 import BeautifulSoup
import unicodedata
import re
import pandas as pd
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy.util as util
from fuzzywuzzy import fuzz
from time import sleep
from time import time
from random import randint

def get_url():
  file = open("VGTscrub2Spotify/sitemap.xml", "r")
  url = []
  for k,line in enumerate(file) :
    tag = 'loc'
    reg_str = "<" + tag + ">(.*very-good-trip-.*?)</" + tag + ">"
    res = re.findall(reg_str, line)
    if res == []:
        continue
    url.append(res[0])
  return url 

def delete_url(url):
  a_file = open("sitemap.xml", "r")
  lines = a_file.readlines()
  a_file.close()
  new_file = open("sitemap.xml", "w")
  for line in lines:
      if line.strip("\n") != ('<url><loc>'+url+'</loc></url>'):
        new_file.write(line)
  new_file.close()

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
  print('récupération du titre de la playlist')
  page = requests.get(URL)
  #on parse avec Bsoup
  soup = BeautifulSoup(page.text, 'html.parser')
  #On cherche le titre dans le h1
  title_container = soup.find('h1')
  #on renvoi le titre en format string
  vgt = 'Very good trip : '+title_container.text
  print('la playlist du jour est : {}'.format(vgt))
  return vgt

def get_artist(liste):
  #récupération des balises STRONG dans la liste
  children = liste.findChildren("strong" , recursive=True)
  artiste = []
  #liste d'exclusion si l'artiste contient un charactère spécial
  exception = ['Siouxsie and the Banshees','Peter, Bjorn and John','Amyl and the Sniffers','Frank Carter & the Rattlesnakes','Black Country, New Road','Shannon & the Clams']
  exclusion = ['»','« Dead Can Dance & Neil Young »','« Do Easy »','Un extrait du concert de lundi 20 novembre','et','Lamp Lit Prose','- The Crouch End Festival Chorus']
  #parsing et nettoyage du format
  for child in children:
    childo = child.text.rsplit(':',1)[0].rstrip()
    if childo in exclusion:
      continue
    if not childo:
        continue
    if childo in exception:
      artiste.append(childo)
      print("exception : {}".format(childo))
      continue
    else:
      childu = childo.replace('ö','ö')
      childr = childu.replace('ü','ü')
      childpo = childr.replace('.','')
      Splity = [',','&','•','with','(','/',' et',' and','&amp;']
      for i in Splity:
        childran = childpo.rsplit(i)[0]
      #child_clean = unicodedata.normalize("NFKD", childa)
      artiste.append(childran.rstrip())
  return artiste

def get_track(liste):
  #nettoyage des lignes vides
  s = liste.text.split('\n')
  while("" in s) :
    s.remove("")
  #récupération du titre par regex entre « »
  pattern = "«\s?(.*?)\s?»"
  pattern_alt3 = "«\s?(.*?)\s?«"
  pattern_alt = "\“(.*?)\”"
  pattern_alt2 = "\“(.*?)\”"
  pattern_alt4 = "«\s?(.*?)\s?\""
  track = []
  exception = []
  regexList = [pattern, pattern_alt, pattern_alt2,pattern_alt3,pattern_alt4]
  line = 'line of data'
  for line in s :
    for regex in regexList:
        titre_dirty = re.findall(regex,line)
        if len(titre_dirty) == 0:
          continue
        childo = titre_dirty[0].rsplit(':',1)[0].rstrip()
        if childo in exception:
          artiste.append(childo)
          print("exception : {}".format(childo))
          continue
        else:
          childu = childo.replace('ö','ö')
          childp = childu.replace('Part','Pt')
          childa = childp.replace('ï','i')
          childr = childa.replace('ü','ü')
          childpo = childr.replace('.','')
          Splity = [',','&','•','with','(','/',' et',' and',' -']
          for i in Splity:
            childran = childpo.rsplit(i)[0]
          #child_clean = unicodedata.normalize("NFKD", childa)
        track.append(childran)
        break
  return track

def get_uri_artiste(artiste):
  artist_genre = []
  uri = []
  artist_id = []
  artist_name = []
  popularity = []
  remove_titre = []
  for count,artiste in enumerate(artiste):
    track_result = sp.search(q=artiste, type = 'artist', limit = 50)
    if track_result["artists"]["total"] == 0:
      print('Artiste {} absent de spotify malheureusement'.format(artiste))
      remove_titre.append(count)
    countdown = 0
    if artiste.lower() == "X".lower():
      artist_name.append('X')
      artist_genre.append('unknown')
      artist_id.append('54NqjhP2rT524Mi2GicG4K')
      uri.append('spotify:artist:54NqjhP2rT524Mi2GicG4K')
      popularity.append('unknown')    
      print("Moyen moins : l\'artiste {} été trouvé avec de façon pas naturelle, ça craint".format(artiste))
      continue
    track_result = sp.search(q=artiste, type = 'artist', limit = 50)
    for j in range(len(track_result['artists']['items'])):
      A = track_result['artists']['items'][j]
      pattern = r'\’'
      new = re.sub(pattern, '', artiste )
      fuzz_ratio = fuzz.ratio(A['name'].lower(), new.lower())
      if fuzz_ratio >= 88:
        artist_name.append(A['name'])
        artist_genre.append(A['genres'])
        artist_id.append(A['id'])
        uri.append(A['uri'])
        popularity.append(A['popularity'])    
        print("All Good ! l\'artiste {} été trouvé avec une correspondance de {}%. Son ID est {}".format(artiste,fuzz_ratio,A['id']))
        break
      else:
        if countdown == len(track_result['artists']['items'])-1:
          remove_titre.append(count)
          break
        countdown += 1
        print("l\'artiste {} n'a pas été trouvé avec {} et une correspondance de {}".format(artiste,A['name'],fuzz_ratio))
  for i in sorted(remove_titre, reverse=True):
    titre.pop(i)
  return artist_name,uri,artist_id,popularity,artist_genre

def get_track_id(titre):
  A_list = list(zip(titre,info_artiste[2]))
  B_list = list(zip(titre,info_artiste[0]))
  track_id = []
  for a,b in enumerate(A_list):
    for k in range(20):
      print('recherche pour {}, {}'.format(b[0],B_list[a][1]))
      track_result = sp.search(q=(b[0],B_list[a][1]), type= ('track','artist'), limit=50, offset=k*50)  
      track_result2 = sp.search(q=(B_list[a][1],b[0]), type= ('track','artist'), limit=50, offset=k*50)
      id_artiste = [track_result['tracks']['items'][x]['artists'][y]['id'] for x in range(len(track_result['tracks']['items'])) for y in range(len(track_result['tracks']['items'][x]['artists']))]
      id_artiste2 = [track_result2['tracks']['items'][x]['artists'][y]['id'] for x in range(len(track_result2['tracks']['items'])) for y in range(len(track_result2['tracks']['items'][x]['artists']))]
      id_track = [track_result['tracks']['items'][x]['id'] for x in range(len(track_result['tracks']['items']))]
      id_track2 = [track_result2['tracks']['items'][x]['id'] for x in range(len(track_result2['tracks']['items']))]
      Dict_id = dict(zip(id_artiste,id_track))
      Dict_id2 = dict(zip(id_artiste2,id_track2))
      if b[1] in Dict_id:
        track_id.append(Dict_id[b[1]])
        panda_titre.append(b[0])
        titres.append(b[0])
        print("le titre {} de l'artiste {} a un track id {}".format(b[0],B_list[a][1],Dict_id[b[1]]))
        break
      elif b[1] in Dict_id2:
        track_id.append(Dict_id2[b[1]])
        panda_titre.append(b[0])
        titres.append(b[0])
        print("le titre {} de l'artiste {} a un track id {}".format(b[0],B_list[a][1],Dict_id2[b[1]]))
        break
      elif k == 19:
        print("aucune correspondance pour le titre {} de l'artiste {}".format(b[0],B_list[a][1]))
        titres.append(b[0])
        panda_titre.append(b[0])
        Erreur.append(' '.join([B_list[a][1],b[0]]))
      else:
        continue
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
#recherche url
URL_test = get_url()

#gestion erreur
Erreur_liste = []
Erreur_titre = []
Erreur_artiste = []
Erreur = []
file = open("site_erreur.xml", "a")

#panda :
panda_rtiste = []
panda_titre = []
panda_genre = []
panda_pop = []

#control du crawl
requète = 0
start_time = time()

for u in URL_test:
  titres = []
  requète +=1
  sleep(randint(1,3))
  elapsed_time = time() - start_time
  print('Request: {}; Frequency: {} requests/s'.format(requète, requète/elapsed_time))
  #recherche du titre
  print('recherche pour l\'émission du {}'.format(u))
  try:
    titre_playlist = get_title(u)
  except TypeError:
    print('ERREUR'+ ' erreur get title')
    file.write(u)
    file.write("\n")
    delete_url(u)
    continue

  #récupération de la liste
  Liste_entiere = get_list(u)
  if Liste_entiere == [] or (len(Liste_entiere) < 5):
    print('ERREUR')
    print('€€€€€€€€€€€€€€€€€€€€€€€€€€#####################################prochaine playlist')
    print('\n')
    file.write(u + ' erreur get_list')
    file.write("\n")
    delete_url(u)
    continue
    
  #récupération des artistes
  artiste = get_artist(Liste_entiere)  
  if artiste == [] or (len(artiste) < 5):
    print('ERREUR')
    print('€€€€€€€€€€€€€€€€€€€€€€€€€€#####################################prochaine playlist')
    print('\n') 
    file.write(u + ' erreur get_artist')
    file.write("\n")
    delete_url(u)
    continue

  #récupération des titres
  titre = get_track(Liste_entiere)
  if titre == [] or (len(titre) < 5):
    print('ERREUR')
    print('€€€€€€€€€€€€€€€€€€€€€€€€€€#####################################prochaine playlist')
    print('\n')
    file.write(u + ' erreur get_track')
    file.write("\n")
    delete_url(u)
    continue

  #récupération des Uri/id
  print('récupération des ID artiste')
  info_artiste = get_uri_artiste(artiste)
  if info_artiste == [] or (len(info_artiste) < 5):
    print('ERREUR')
    print('€€€€€€€€€€€€€€€€€€€€€€€€€€#####################################prochaine playlist')
    print('\n')
    file.write(u + ' erreur get_uri_artiste')
    file.write("\n")
    delete_url(u)
    continue
  #récupération des Uri/id
  print('récupération des ID track')
  info_track = get_track_id(titre)
  if info_track == [] or (len(info_track) < 5):
    print('ERREUR')
    print('€€€€€€€€€€€€€€€€€€€€€€€€€€#####################################prochaine playlist')
    print('\n')
    file.write(u + ' erreur info_track')
    file.write("\n")
    delete_url(u)
    continue
  print('€€€€€€€€€€€€€€€€€€€€€€€€€€#####################################prochaine playlist')
  print('\n')
  print(len(info_artiste[0]))
  print(len(info_artiste[1]))
  print(len(info_artiste[2]))
  print(len(info_artiste[3]))
  print(len(info_artiste[4]))
  print(len(titres))
  test_df = pd.DataFrame({'artistes' : info_artiste[0], 'titres' : titres, 'uri' : info_artiste[1], 'artist_id' : info_artiste[2], 'popularity' : info_artiste[3], 'artist_genre' : info_artiste[4]})
  print(test_df)
  
  delete_url(u)

  #création de la playlist
  #print('création de la playlist {}'.format(titre_playlist))
  #sp.user_playlist_create(username, name = titre_playlist)

  #print(test_df.artistes)
"""     playlist_id = GetPlaylistID(username, titre_playlist)
    try:
      track_ids = get_track_id(titre)
    except TypeError:
      break
    print(track_ids)
    print(len(track_ids))
    sp.user_playlist_add_tracks(username, playlist_id, track_ids)
 """
print(Erreur_titre)
print(Erreur_artiste)
print(len(panda_rtiste))
print(len(panda_titre))
print(len(panda_genre))
print(len(panda_pop))



test_df = pd.DataFrame({'artistes' : panda_rtiste, 'titres' : panda_titre, 'popularity' : panda_genre, 'artist_genre' : panda_pop})
#print(test_df)
print(Erreur)