from requests_html import HTMLSession, MaxRetries
from requests.exceptions import ConnectionError
from urllib.parse import unquote
from fake_useragent import UserAgent
ua = UserAgent()


class ChromeStore(object):
    base_url = 'https://chrome.google.com'
    sitemap_url = base_url + '/webstore/sitemap'

    def __init__(self):
        self.session = HTMLSession()
        self.session.headers.update({'User-Agent': ua.chrome})

    def get_page(self, url):
        try:
            page = self.session.get(url)
        except (MaxRetries, ConnectionError) as e:
            print(f'Unable to connect to {url} : {e}')
            return None
        else:
            return page

    def get_sitemaps(self, sitemap=sitemap_url):
        sitemaps = self.get_page(url=sitemap)
        return [loc.text for loc in sitemaps.html.find('loc')]
    
    def sitemap_to_extensions(self, sitemap):
        results = self.get_page(url=sitemap)
        extensions = []
        for extension in results.html.find('url'):
            url_arr = extension.find('loc', first=True).text.split('?')[0].split('/')
            extensions.append((url_arr[-1], unquote(url_arr[-2])))
        return extensions

    def get_extensions(self, extensions):
        urls = [f'{self.base_url}/webstore/detail/{e[1]}/{e[0]}' for e in extensions]
        tasks = [lambda url=u: self._get_page(url=url) for u in urls]
        results = self.session.run(*tasks)
        return list(filter(None, results))
