from requests_html import HTML
from datetime import datetime
from math import ceil
from .store import ChromeStore


class Extension:

    def __init__(self, extension_id, extension_name_slug=None):
        if len(extension_id) != 32:
            raise ValueError(f'Chrome Extension Id needs to be 32 char long: {extension_id}')
        # --
        self.id = extension_id
        self.name_slug = extension_name_slug
        if extension_name_slug:
            self.url = f'{ChromeStore.base_url}/webstore/detail/{extension_name_slug}/{extension_id}'
        else:
            self.url = f'{ChromeStore.base_url}/webstore/detail/{extension_id}'
        self.data = None
        self._meta = None

    def get_details(self):
        store = ChromeStore()
        page = store.get_page(url=self.url)
        noscript = page.html.find('noscript', first=True)
        if noscript is None:
            raise ValueError(f'Extension page {self.url} doesnt contain noscript data.')
        else:
            self.data = HTML(html=noscript.html)
            self._meta = [meta for meta in self.data.find('meta')]

    def itemprop_check(self, key):
        ret = None
        for meta in self._meta:
            if 'itemprop' in meta.attrs.keys() and meta.attrs['itemprop'] == key:
                ret = meta.attrs['content']
        return ret

    def dict(self):
        data = {}
        for property_name in [p for p in dir(Extension) if isinstance(getattr(Extension, p), property)]:
            data[property_name] = getattr(self, property_name)
        return data

    @property
    def summary(self):
        return self.data.find('div.C-b-p-j-Pb', first=True).text

    @property
    def description(self):
        return self.data.find('pre.C-b-p-j-Oa', first=True).text

    @property
    def image(self):
        if self.data.find('div.h-C-b-i-k', first=True):
            if self.data.find('div.h-C-b-i-k', first=True).find('img', first=True):
                return self.data.find('div.h-C-b-i-k', first=True).find('img', first=True).attrs['src']
        else:
            return None

    @property
    def website(self):
        if self.data.find('a.h-C-b-p-D-xd-y', first=True):
            return self.data.find('a.h-C-b-p-D-xd-y', first=True).attrs['href']
        else:
            return None

    @property
    def updated(self):
        return datetime.strptime(self.data.find('span.h-C-b-p-D-xh-hh', first=True).text, '%B %d, %Y')

    @property
    def size(self):
        sizes = {'MiB': 1048576, 'KiB': 2014, }
        text = self.data.find('span.h-C-b-p-D-za', first=True).text
        for size in sizes.keys():
            if size in text:
                return ceil(float(text.replace(size, '')) * sizes[size])
        return None

    @property
    def owner_url(self):
        return self.data.find('a.e-f-y', first=True).attrs['href'] if self.data.find('a.e-f-y') else None

    @property
    def owner_address(self):
        xpath = 'div.C-b-lmDd0-Q7Zjwb'
        return self.data.find(xpath, first=True).text if self.data.find(xpath) else None

    @property
    def offered_by(self):
        xpath = 'span.e-f-Me'
        return self.data.find(xpath, first=True).text.replace('offered by', '') if self.data.find(xpath) else None

    @property
    def owner_image(self):
        return self.itemprop_check(key='image')

    @property
    def rating_count(self):
        value = self.itemprop_check(key='ratingCount')
        return int(value) if value is not None else None

    @property
    def rating_value(self):
        value = self.itemprop_check(key='ratingValue')
        return float(value) if value is not None else None

    @property
    def interaction_count(self):
        value = self.itemprop_check(key='interactionCount')
        return int(value.replace('UserDownloads:', '').replace('+', '').replace(',', '')) if value is not None else None

    @property
    def name(self):
        value = self.itemprop_check(key='name')
        return value

    @property
    def operating_system(self):
        value = self.itemprop_check(key='operatingSystem')
        return value

    @property
    def price(self):
        value = self.itemprop_check(key='price')
        return float(value) if value is not None else None

    @property
    def currency(self):
        value = self.itemprop_check(key='priceCurrency')
        return value

    @property
    def version(self):
        value = self.itemprop_check(key='version')
        return value

    @classmethod
    def download(cls, extension_id):
        # @todo: Able to download and analyze chrome extension files
        pass
