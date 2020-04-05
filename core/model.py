import requests
import json
from datetime import datetime, timedelta

class Model:
    def __init__(self, api_key):
        r = requests.get('https://api.openweathermap.org/data/2.5/forecast?lat=37.7740&lon=-122.4728&appid=%s'%api_key)
        self.data = r.json()

    def predict(self, time_range):
        now = datetime.now() + timedelta(hours=time_range)
        limit = now.timestamp()
        ret = []
        
        for h in self.data['list']:
            if float(h['dt'])  > limit:
                break
            ret.append({
                'hour': datetime.utcfromtimestamp(h['dt']).strftime("%Y-%m-%d %H:%M:%S"),
                'temp': h['main']['temp'],
                'hum': h['main']['humidity'],
            })

        return ret