import requests
import os
from datetime import datetime

LINE_TOKEN = os.getenv("LINE_TOKEN")
USGS_API = 'https://earthquake.usgs.gov/earthquakes/feed/v1.0/summary/significant_week.geojson'

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
        0.0 <= lat <= 25.0 and    # ละติจูดในภูมิภาคเอเชียตะวันออกเฉียงใต้
        90.0 <= lon <= 110.0      # ลองจิจูดประมาณไทย-มาเลย์
    )

    return keyword_match or lat_lon_match

try:
    response = requests.get(USGS_API)
    data = response.json()
    features = data.get("features", [])

    count = 0
    log_entries = []
    for event in features:
        props = event["properties"]
        geo = event["geometry"]
        mag = props.get("mag", 0)
        place = props.get("place", "")
        coords = geo.get("coordinates", [None, None])  # [lon, lat, depth]
        lon, lat = coords[0], coords[1]

        if mag >= 5.0 and is_in_target_region(lat, lon, place):
            message = f"🌍 แผ่นดินไหว {mag} บริเวณ {place}"
            send_line_notify(message)
            print("✅ แจ้งเตือน:", message)

            log_entries.append(f"[{datetime.now()}] {message}")
            count += 1

    if count == 0:
        print("ℹ️ ไม่มีเหตุการณ์เข้าเงื่อนไข")

    # เขียน log ลงไฟล์
    if log_entries:
        with open("quake_log.txt", "a", encoding="utf-8") as f:
            f.write("\n".join(log_entries) + "\n")

except Exception as e:
    print("❌ Error:", e)
