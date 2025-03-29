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
    features = data.get("features", [])

    count = 0
    for event in features:
        props = event["properties"]
        geo = event["geometry"]
        mag = props.get("mag", 0)
        place = props.get("place", "")
        coords = geo.get("coordinates", [None, None])  # [lon, lat, depth]
        lon, lat = coords[0], coords[1]

        # เงื่อนไขกรอง
        in_asia = (
            any(keyword in place for keyword in [
                "Thailand", "Asia", "Myanmar", "Laos", "Vietnam", "Malaysia"
            ])
            or (lat is not None and 0 <= lat <= 40 and 60 <= lon <= 120)
        )

        if mag >= 5.0 and in_asia:
            message = f"🌍 แผ่นดินไหว {mag} บริเวณ {place}"
            send_line_notify(message)
            print("✅ แจ้งเตือน:", message)
            count += 1

    if count == 0:
        print("ℹ️ ไม่มีเหตุการณ์เข้าเงื่อนไข")

except Exception as e:
    print("❌ Error:", e)
