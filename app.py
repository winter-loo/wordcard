import flask
from flask import make_response, request
import requests
from bs4 import BeautifulSoup
import json
import base64
import pyjson5

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
def textToSpeech(text):
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


def searchImages(keyword, dump_sr=False):
    """ return a list of image url which parsed from google search results"""

    url = f'https://www.google.com/search?q={keyword}&tbm=isch'

    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
    }

    try:
        res = requests.get(url, headers=headers)
        if res.status_code != 200:
            return []
    except Exception as e:
        print(e)
        return []
    page_source = res.text

    def scrape_search_result(page_source):
        init_data_cbs = []
        pattern = "AF_initDataCallback("
        start = 0
        while True:
            start = page_source.find(pattern, start)
            if start == -1:
                break
            end = page_source.find('</script>', start)
            init_data_cbs.append(page_source[start+len(pattern):end-2])
            start = end
        return pyjson5.loads(init_data_cbs[1])

    def getAllImages(data, imgs):
        for idx, item in enumerate(data):
            if type(item) != type([]) and type(item) != type({}):
                if item != None and type(item) == type("") and \
                    item.startswith("http") and \
                    item.find("gstatic.com") == -1 and \
                    idx + 2 < len(data) and \
                    type(data[idx+1]) == type(0) and \
                    type(data[idx+2]) == type(0):
                    imgs.append(item)
                    return
            else:
                if type(item) == type({}):
                    for k in item:
                        getAllImages(item[k], imgs)
                else:
                    getAllImages(item, imgs)
    imgs = []
    search_results = scrape_search_result(page_source)
    if dump_sr:
        import json
        with open('foo.json', 'w') as f:
            f.write(json.dumps(search_results))
    getAllImages(search_results["data"], imgs)
    return imgs

# ------- API list --------------

@app.route("/word/<word>/pron/url")
def request_pron_url_for(word):
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
  res = make_response(textToSpeech(txt))
  res.mimetype = "audio/mp3"
  return res

@app.route("/images/for/<keyword>")
def search_images(keyword):
  imgs = searchImages(keyword)
  return { "data": imgs }

# ------- end API list --------------
