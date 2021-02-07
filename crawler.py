import requests
import re
import cssutils
from bs4 import BeautifulSoup as bs
from urllib import request, parse

url = 'https://stackoverflow.com/questions/11592347/what-is-the-pythonic-way-to-implement-a-css-parser-replacer'

links = []
assets = []


def web_crawler(url, depth=0, page_assets=False):

    if depth >= 0:
        opener = request.build_opener()
        opener.add_headers = [{'User-Agent' : 'Mozilla'}]
        request.install_opener(opener)

        base_url = "{0.scheme}://{0.netloc}/".format(parse.urlsplit(url))
        if url not in links:
            links.append(url)
        raw = requests.get(url).text
        if page_assets:
            try:
                sheet = cssutils.parseString(requests.get(url).content)
                urls = cssutils.getUrls(sheet)
                for url in urls:
                    if url not in links:
                        links.append(url)

                        path = request.urlopen(url)
                        meta = path.info()
                        print(url, ' size: ',meta.get(name="Content-Length"))
            except:
                pass

        soup = bs(raw, 'html.parser')

        for script in soup.find_all("script"):
            if script.attrs.get("src"):
                script_url = parse.urljoin(url, script.attrs.get("src"))
                if script_url not in assets:
                    path = request.urlopen(script_url)
                    meta = path.info()
                    print(script_url, ' size: ', meta.get(name="Content-Length"))
                    assets.append(script_url)
                    if page_assets and script_url not in links:
                        links.append(script_url)
                        web_crawler(script_url, depth-1, page_assets)

        for css in soup.find_all("link",{"rel":"stylesheet"}):
            if css.attrs.get("href"):
                css_url = parse.urljoin(url, css.attrs.get("href"))
                if css_url not in assets:
                    try:
                        path = request.urlopen(css_url)
                        meta = path.info()
                        print(css_url, ' ', 'size: ', meta.get(name="Content-Length"))
                        assets.append(css_url)
                        if page_assets and css_url not in links:
                            links.append(css_url)
                            web_crawler(css_url, depth-1, page_assets)
                    except:
                        pass

        for img in soup.find_all("img"):
            if img.get("src"):
                img_url = parse.urljoin(url, img.get("src"))
                try:
                    path = request.urlopen(img_url)
                    meta = path.info()

                    if img_url not in assets:
                        print(img_url, ' ', 'size: ', meta.get(name="Content-Length"))
                        assets.append(img_url)
                except:
                    pass

        for a in soup.find_all('a'):
            href = str(a.get('href'))

            if 'http://' not in href and 'https://' not in href and base_url not in href:
                href = base_url + href[1:]

            if href not in links:
                path = request.urlopen(href)
                meta = path.info()

                print(href, ' ', 'size: ', meta.get(name="Content-Length"))

                links.append(href)
                web_crawler(href, depth-1, page_assets)


web_crawler(url, 2, False)

