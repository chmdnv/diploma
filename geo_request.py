import requests
import time
from configparser import ConfigParser  # write your GEO_API_KEY for api.opentripmap.com in config.ini


def get_coords(place: str) -> tuple[float, float]:
    url = 'https://api.opentripmap.com/0.1'
    url_coord = 'places/geoname'

    config = ConfigParser()
    config.read('config.ini')
    key = config['GEO_API']['key']

    lang = 'en'

    params = {
        'name': place,
        'apikey': key
    }

    req = requests.get(f"{url}/{lang}/{url_coord}", params=params)
    time.sleep(0.1)

    if req.status_code == 200:
        lat = req.json().get('lat', 0.0)
        lon = req.json().get('lon', 0.0)
        return lat, lon
    else:
        return 0, 0


if __name__ == '__main__':
    print(get_coords('moscow'))
