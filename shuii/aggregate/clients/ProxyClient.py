# proxy, request, retrieve
import ssl

class ProxyClient:
    def __init__(self, proxies):
        self.SSL_CONTEXT = ssl.create_default_context(cafile=certifi.where())
        self.proxies = proxies

    def request(self, url):
        pass