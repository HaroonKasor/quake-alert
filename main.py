import requests
import os
from datetime import datetime

LINE_TOKEN = os.getenv("LINE_TOKEN")
USGS_API = 'https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/significant_week.geojson'
EVENT_LOG = "notified_ids.txt"

def send_line_notify(message):
    url = 'https://notify-api.line.me/api/notify'
    headers = {'Authorization': f'Bearer {LINE_TOKEN}'}
    data = {'message': message}
    requests.post(url, headers=headers, data=data)

def is_in_target_region(lat, lon, place):
    southeast_asia_keywords = [
        "Thailand", "Malaysia", "Myanmar", "Laos", "Vietnam", "Cambodia",
        "Indonesia", "Philippines", "Asia"
    ]
    keyword_match = any(keyword in place for keyword in southeast_asia_keywords)
    lat_lon_match = (
        lat is not None and lon is not None and
        0.0 <= lat <= 25.0 and
        90.0 <= lon <= 110.0
    )
    return keyword_match or lat_lon_match

# โหลด event_id ที่เคยแจ้งเตือน
if os.path.exists(EVENT_LOG):
    with open(EVENT_LOG, "r") as f:
        notified_ids = set(line.strip() for line in f)
else:
    notified_ids = set()

try:
    response = requests.get(USGS_API)
    data = response.json()
    features = data.get("features", [])
    count = 0

    print(f"🔍 พบทั้งหมด {len(features)} เหตุการณ์")

    for event in features:
        props = event["properties"]
        geo = event["geometry"]
        raw_event_id = event.get("id")
        mag = props.get("mag", 0)
        place = props.get("place", "")
        coords = geo.get("coordinates", [None, None])
        lon, lat = coords[0], coords[1]

        # ใช้ event_id ลูกผสม เพื่อป้องกันซ้ำแบบแน่นอน
        event_id = f"{raw_event_id}_{round(mag, 1)}"

        print(f"🧾 ตรวจสอบ: {event_id} | {place} | M{mag} | lat={lat}, lon={lon}")

        if event_id not in notified_ids and mag >= 5.0 and is_in_target_region(lat, lon, place):
            message = f"🌍 แผ่นดินไหว {mag} บริเวณ {place}"
            send_line_notify(message)
            print("✅ แจ้งเตือน:", message)

            with open("quake_log.txt", "a", encoding="utf-8") as f:
                f.write(f"[{datetime.now()}] {message}\n")

            with open(EVENT_LOG, "a") as f:
                f.write(event_id + "\n")

            notified_ids.add(event_id)
            count += 1
        else:
            print("🚫 ยังไม่เข้าเงื่อนไข หรือเคยแจ้งแล้ว\n")

    if count == 0:
        print("ℹ️ ไม่มีเหตุการณ์ใหม่")

except Exception as e:
    print("❌ Error:", e)
