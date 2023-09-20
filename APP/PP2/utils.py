from django.conf import settings
import requests
import threading

hashids = settings.HASHIDS


def h_encode(id):
    return hashids.encode(id)


def h_decode(h):
    z = hashids.decode(h)
    if z:
        return z[0]


class HashIdConverter:
    regex = '[a-zA-Z0-9]{8,}'

    def to_python(self, value):
        return h_decode(value)

    def to_url(self, value):
        return h_encode(value)


def get_filename(filename, request):
    return filename.upper()


def request_task(url, json, headers):
    requests.post(url, json=json, headers=headers)


def fire_and_forget(url, json, headers):
    threading.Thread(target=request_task, args=(url, json, headers)).start()
