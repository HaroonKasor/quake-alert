import requests
import time
import os

LINE_TOKEN = os.getenv("ujZdTKxVRv3KTdkkdMhWpKAO5C6MZuiWdOI8Kuj1U3C")
USGS_API = 'https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/significant_hour.geojson'

latest_event_id = None

def send_line_notify(message):
    url = 'https://notify-api.line.me/api/notify'
    headers = {'Authorization': f'Bearer {LINE_TOKEN}'}
    data = {'message': message}
    requests.post(url, headers=headers, data=data)

while True:
    try:
        response = requests.get(USGS_API)
        data = response.json()

        if data['features']:
            event = data['features'][0]
            event_id = event['id']
            mag = event['properties']['mag']
            place = event['properties']['place']

            if event_id != latest_event_id:
                latest_event_id = event_id
                message = f"🌍 แผ่นดินไหว ขนาด {mag} บริเวณ {place}"
                send_line_notify(message)
                print("✅ แจ้งเตือน:", message)

    except Exception as e:
        print("❌ Error:", e)

    time.sleep(300)  # รอ 5 นาที
