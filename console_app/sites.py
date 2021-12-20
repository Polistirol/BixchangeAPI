import requests as r


class Site:
    def __init__(self, url='http://127.0.0.1:8000/console'):
        self.url = url

    def ping(self):
        try:
            r.get(self.url)
            return True
        except Exception as e:
            print(e)
            return False
