import flask
import requests
from bs4 import BeautifulSoup

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

u = getWordPronunciationUrl("alga")


@app.route("/word/<word>/pron/url")
def requestPronUrlFor(word):
    return getWordPronunciationUrl(word)