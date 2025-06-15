import requests
import time

def get_ngrok_url():
    try:
        tunnels = requests.get("http://ngrok:4040/api/tunnels").json()
        for tunnel in tunnels['tunnels']:
            if tunnel['proto'] == 'https':
                return tunnel['public_url']
        return tunnels['tunnels'][0]['public_url']
    except Exception as e:
        print(f"Could not fetch ngrok URL: {e}")
        return None

def get_ngrok_url_with_retry(retries=5, delay=2):
    for _ in range(retries):
        url = get_ngrok_url()
        if url:
            return url
        time.sleep(delay)
    return None
