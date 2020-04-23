import requests


def safe_api_call(url: str, params: dict = {}) -> dict:
    try:
        req = requests.get(url, params=params, timeout=(30, 120), headers={
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:75.0) Gecko/20100101 Firefox/75.0'
        })
        if req.status_code != 200:
            print('Error received from %s: %s' % (url, req.text))
        else:
            try:
                return req.json()
            except ValueError:
                print('Unknown response from %s: %s' % (url, req.text))
    except Exception:
        print('Unable to connect to %s' % url)
    return {}
