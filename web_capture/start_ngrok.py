from pyngrok import ngrok
import time

try:
    # Connect directly to port 5000
    public_url = ngrok.connect(5000).public_url
    print(f" * Ngrok Tunnel URL: {public_url}")
    
    # Keep the script running
    while True:
        time.sleep(1)
except Exception as e:
    print(f"Error starting ngrok: {e}")
