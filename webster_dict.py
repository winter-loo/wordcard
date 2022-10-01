import requests
from bs4 import BeautifulSoup


def searchWord(word):
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
        "pron": getPronSoundUrl(soup),
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

print(searchWord('coincide'))
