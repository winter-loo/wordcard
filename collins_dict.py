from bs4 import BeautifulSoup
import cloudscraper
import sys

def searchWord(word):
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
        def_el = sense_el.find("div", class_="def")
        if def_el:
            sense["def"] = def_el.text.strip().replace('\n', ' ')
        elif "def" in sense_el["class"]:
            sense["def"] = sense_el.text.strip().replace('\n', ' ')
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
        senses.append(sense)
    defs["senses"] = senses
    return defs

if __name__ == '__main__':
    word = 'commute'
    if len(sys.argv) > 1:
      word = sys.argv[1]
    print(searchWord(word))
