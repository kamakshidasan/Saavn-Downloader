#!/usr/bin/python3

from bs4 import BeautifulSoup
import os
import requests
from json import JSONDecoder
import base64
import os
import json
from pyDes import *
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, error
import mutagen
import html

music_folder = './music'
images_folder = './images'
proxy_ip = ''

# set http_proxy from environment
if('http_proxy' in os.environ):
    proxy_ip = os.environ['http_proxy']

proxies = {
  'http': proxy_ip,
  'https': proxy_ip,
}
# proxy setup end here

headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:49.0) Gecko/20100101 Firefox/49.0'
}
base_url = 'http://h.saavncdn.com'
json_decoder = JSONDecoder()

# Key and IV are coded in plaintext in the app when decompiled
# and its preety insecure to decrypt urls to the mp3 at the client side
# these operations should be performed at the server side.
des_cipher = des(b"38346591", ECB, b"\0\0\0\0\0\0\0\0" , pad=None, padmode=PAD_PKCS5)


input_url = input('Enter the song url:').strip()
#input_url = "https://www.saavn.com/p/song/hindi/Raavan/Behene-De-Mujhe-Behene-De/PiAAZRpzBkk"

try:
    res = requests.get(input_url, proxies=proxies, headers=headers)
except Exception as e:
    print('Error accesssing website error: '+e)
    sys.exit()

soup = BeautifulSoup(res.text,"lxml")

# Just the single song
songs_json = soup.find('div',{'class':'hide song-json'})

# All songs
# songs_json = soup.find_all('div',{'class':'hide song-json'})

for song in songs_json:

    # Just the single song
	obj = json_decoder.decode(songs_json.text)

    # All songs
    # obj = json_decoder.decode(song.text)

	enc_url = base64.b64decode(obj['url'].strip())
	dec_url = des_cipher.decrypt(enc_url,padmode=PAD_PKCS5).decode('utf-8')
	dec_url = base_url + dec_url.replace('mp3:audios','') + '.mp3'

	#print(dec_url,'\n')
	#print(json.dumps(obj, indent=4, sort_keys=True))

	image_url = obj["image_url"]

	os.system('wget -P ' + music_folder + ' ' + dec_url)
	os.system('wget -P ' + images_folder + ' ' + image_url)

	file_name = dec_url.split("/")[-1]
	file_path = music_folder + os.path.sep + file_name

	image_name = image_url.split("/")[-1]
	image_path = images_folder + os.path.sep + image_name

	try:
		audio = EasyID3(file_path)
	except mutagen.id3.ID3NoHeaderError:
		audio = mutagen.File(file_path, easy=True)
		audio.add_tags()

	audio["album"] = obj["album"]
	audio["length"] = obj["duration"]
	audio["title"] = html.unescape(obj["title"])
	audio["language"] = obj["language"]
	audio["date"] = obj["year"]
	audio["artist"] = obj["singers"]
	audio["composer"] = obj["music"]
	audio.save()

	image_audio = MP3(file_path, ID3=ID3)

	image_audio.tags.add(
		APIC(
		    encoding=3, # 3 is for utf-8
		    mime='image/jpeg', # image/jpeg or image/png
		    type=3, # 3 is for the cover image
		    desc=u'covr',
		    data=open(image_path,"rb").read()
		)
	)
	image_audio.save()


	newname = music_folder + os.path.sep + audio["title"][0] + ".mp3"
	newname.replace(" ", "_")
	os.rename(file_path, newname)

	print(audio['album'],'-',audio['title'])
