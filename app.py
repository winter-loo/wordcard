import os
import flask
from flask import make_response, request
from flask_cors import CORS, cross_origin
import requests
from bs4 import BeautifulSoup
import json
import base64
import pyjson5
import cloudscraper
from google.cloud import translate

app = flask.Flask(__name__)
CORS(app)

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


def searchWordInCollinsDict(word):
    """
    A requests.get(url) is forbiddened by collins website.
    Solution is to use cloudscraper module.

    returns python dictionary:
    [{
        "def": ".....",
        "cits": [{"quote": ".....", "sound": ".....mp3"}]
     }]
    """
    url = f'https://www.collinsdictionary.com/us/dictionary/english/{word}'

    scraper = cloudscraper.create_scraper()
    try:
        res = scraper.get(url)
    except Exception as e:
        print(e)
        return []

    source = res.text
    soup = BeautifulSoup(source, 'html.parser')
    defs = {}
    defs["pronUrl"] = soup.select("div.cobuild .hwd_sound.audio_play_button")[0]["data-src-mp3"]

    sense_els = soup.select("div.cobuild div.sense")
    senses = []
    for sense_el in sense_els:
        sense = {}
        has_def = True
        def_el = sense_el.find("div", class_="def")
        if def_el:
            sense["def"] = def_el.text.strip().replace('\n', ' ')
        elif "def" in sense_el["class"]:
            sense["def"] = sense_el.text.strip().replace('\n', ' ')
        else:
            has_def = False
        cit_els = sense_el.find_all("div", class_="cit")
        cits = []
        for cit_el in cit_els:
            cit = {}
            quote_el = cit_el.find("span", class_="quote")
            sound_el = cit_el.find("a", class_="hwd_sound")
            if quote_el:
                cit["quote"] = quote_el.text.strip().replace('\n', ' ')
            if sound_el:
                cit["sound"] = sound_el["data-src-mp3"]
            if quote_el or sound_el:
                cits.append(cit)
        if len(cits):
            sense["cits"] = cits
        if has_def or len(cits):
            senses.append(sense)
    defs["senses"] = senses
    return  defs


def searchWordInWebsterDict(word):
    url = f"https://www.merriam-webster.com/dictionary/{word}"

    try:
        res = requests.get(url)
    except Exception as e:
        print(e)
        return {}
    source = res.text
    soup = BeautifulSoup(source, "html.parser")

    def getPronSoundUrl(soup):
        play_pron_el = soup.find("a", class_="hw-play-pron")
        if play_pron_el == None:
            return ""
        a_props = {
            "lang": play_pron_el.get("data-lang"),
            "dir": play_pron_el.get("data-dir"),
            "file": play_pron_el.get("data-file"),
            "title": play_pron_el.get("data-title"),
            "type": play_pron_el.get("data-type")
        }

        sound_url = ""
        if a_props["type"] == "spell_it":
            sound_url = f"https://merriam-webster.com/assets/mw/spellit-files/{a_props['file']}.mp3"
        else:
            sound_url = f"https://media.merriam-webster.com/audio/prons/{a_props['lang'].replace('_', '/')}/mp3/{a_props['dir']}/{a_props['file']}.mp3"
        return sound_url

    word_def = {
        "pronUrl": getPronSoundUrl(soup),
        "senses": []
    }

    sense_els = soup.select("#dictionary-entry-1 .sense .dt")

    senses = []
    for sense_el in sense_els:
        sense = {}
        sense["def"] = sense_el.find("span", class_="dtText").text[2:]
        quote_els = sense_el.select(".ex-sent.t")
        quotes = []
        for quote_el in quote_els:
            quote = { "quote": quote_el.text }
            quotes.append(quote)
        if len(quotes):
            sense["cits"] = quotes
        senses.append(sense)
    word_def["senses"] = senses
    return word_def


def translateText(text):
  """
  done by  using google translate api

  GOOGLE_APPLICATION_CREDENTIALS environment variable must be set
  """
  if len(text) == 0:
    return ""
  parent = "projects/tts-ldd-cool"
  client = translate.TranslationServiceClient()

  target_language_code = "zh-cn"

  response = client.translate_text(
      contents=[text],
      target_language_code=target_language_code,
      parent=parent,
  )
  if len(response.translations) > 0:
    return response.translations[0].translated_text
  return ""

# ------- API list --------------

@app.route("/word/<word>/def/from/webster")
def search_word_from_webster(word):
  return searchWordInWebsterDict(word)


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

ImageExtMap = {
    "image/jpeg": "jpg",
    "image/gif": "gif",
    "image/png": "png",
    "image/svg+xml": "svg",
    "image/webp": "webp"
}

@app.route("/word/<word>/images")
def search_images(word):
    imgs = searchImages(word)
    count = 0
    new_urls = []
    try:
        os.makedirs(f"static/images/{word}")
    except FileExistsError:
        pass
    except Exception as e:
        print(e)
        return []
    for img_url in imgs:
        r = requests.get(img_url)
        if r.status_code != 200:
            continue
        img_ext = ImageExtMap.get(r.headers["Content-Type"])
        if img_ext == None:
            continue
        count += 1
        filename = f"static/images/{word}/{count}.{img_ext}"
        with open(filename, "wb") as out:
            out.write(r.content)
        new_urls.append(f"{request.scheme}://{request.host}/{filename}")
        # it seems that swiftui cannot receive a lot of data in a rush
        if count >=  10:
            break
    return { "data": new_urls }

@app.route("/word/<word>/def/from/collins")
def search_word_from_collins(word):
  return searchWordInCollinsDict(word)  

@app.route("/translation", methods=["POST", "GET"])
def translate_text():
  text = ""
  if request.method == "POST":
    text = request.form["text"]
  elif request.method == "GET":
    text = request.args.get("text")
  return { "translated": translateText(text) }

@app.route("/add", methods=["POST"])
@cross_origin()
def add_word():
  text = request.form["text"]
  print(f"----add text: {text}-----")
  return {"echo": text}

# ------- end API list --------------
