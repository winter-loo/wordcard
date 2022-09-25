import requests
import pyjson5

def SearchImage(keyword, dump_sr=False):
    url = f'https://www.google.com/search?q={keyword}&tbm=isch'
    print(url)

    headers = {
        "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
    }

    try:
        res = requests.get(url, headers=headers)
        if res.status_code != 200:
            print(f'status: {res.status_code}')
            return []
    except Exception as e:
        print(e)
        return []
    page_source = res.text
    with open("foo.html", "w") as f:
      f.write(page_source)

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

imgs = SearchImage("beaver")
for i in imgs:
    print(i)
