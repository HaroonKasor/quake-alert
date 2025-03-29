import requests
import os

LINE_TOKEN = os.getenv("LINE_TOKEN")
USGS_API = 'https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/significant_week.geojson'

def send_line_notify(message):
    url = 'https://notify-api.line.me/api/notify'
    headers = {'Authorization': f'Bearer {LINE_TOKEN}'}
    data = {'message': message}
    requests.post(url, headers=headers, data=data)

try:
    response = requests.get(USGS_API)
    data = response.json()
    print("📡 ข้อมูลที่ได้:", data)  # debug

    if data['features']:
        event = data['features'][0]
        event_id = event['id']
        mag = event['properties']['mag']
        place = event['properties']['place']

        message = f"🌍 แผ่นดินไหว ขนาด {mag} บริเวณ {place}"
        send_line_notify(message)
        print("✅ แจ้งเตือน:", message)

    else:
        print("ℹ️ ไม่มีข้อมูลแผ่นดินไหวในช่วงเวลานี้")

except Exception as e:
    print("❌ Error:", e)
