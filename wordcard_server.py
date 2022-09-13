import flask
from flask import make_response, request
import requests
from bs4 import BeautifulSoup
import json
import base64

app = flask.Flask(__name__)

def getWordPronunciationUrl(word):
    queryUrl = f"https://www.merriam-webster.com/dictionary/{word}"
    res = requests.get(queryUrl)
    res.raise_for_status()
    html = res.text
    soup = BeautifulSoup(html, 'html.parser')

    playPronElement = soup.select("a[class*='play-pron hw-play-pron']")
    if len(playPronElement) == 0:
        return ""
    hwPlayPronEl = playPronElement[0]
    aProps = {
        "lang": hwPlayPronEl.get("data-lang"),
        "dir": hwPlayPronEl.get("data-dir"),
        "file": hwPlayPronEl.get("data-file"),
        "title": hwPlayPronEl.get("data-title"),
        "type": hwPlayPronEl.get("data-type")
    }

    pronUrl = ""
    if aProps["type"] == "spell_it":
        pronUrl = f"https://merriam-webster.com/assets/mw/spellit-files/{aProps['file']}.mp3"
    else:
        pronUrl = f"https://media.merriam-webster.com/audio/prons/{aProps['lang'].replace('_', '/')}/mp3/{aProps['dir']}/{aProps['file']}.mp3"

    return pronUrl


# another method: use gtts package which utilize translate.google.com
API_KEY = "AIzaSyBmPoJhNtlJlI0eNvTsKiPvGNcyu678q-4"
def TextToSpeech(text):
  ttsUrl = f"https://texttospeech.googleapis.com/v1/text:synthesize?key={API_KEY}"
  headers = {
    "Accept": "application/json",
    "Content-Type": "application/json"
  }
  data = {
    "input": {
      "text": text
    },
    "voice": {
      "languageCode": "en-US",
      "name": "en-US-Wavenet-F"
    },
    "audioConfig": {
      "audioEncoding": "MP3"
    }
  }
  res = requests.post(url=ttsUrl, headers=headers, data=str(data))
  jr = json.loads(res.text)["audioContent"]
  if jr == None:
    return None
  return base64.b64decode(jr)

@app.route("/word/<word>/pron/url")
def requestPronUrlFor(word):
    res = make_response(getWordPronunciationUrl(word))
    res.mimetype = "text/plain"
    return res


@app.route("/tts", methods=["POST", "GET"])
def tts():
  if request.method == "POST":
    txt = request.form["text"]
  elif request.method == "GET":
    txt = request.args.get("text")
  if txt == None or len(txt) == 0:
    txt = "oops! Empty text!"
  res = make_response(TextToSpeech(txt))
  res.mimetype = "audio/mp3"
  return res