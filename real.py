import socket
import ssl
import time
import requests

# Twitch IRC and API credentials
server = 'irc.chat.twitch.tv'
port = 6697
nickname = 'jamesschoolaccount2'
token = 'oauth:7095t3dnc5rv5ldka6yxsqdcykqkzl'
channel = '#fl0m'

client_id = 'wwzwkqcag0y1swzv8x4wbazhs6vun1'
access_token = '7095t3dnc5rv5ldka6yxsqdcykqkzl'
headers = {
    'Client-ID': client_id,
    'Authorization': f'Bearer {access_token}'
}

# Dictionary to track the last message time for each unique user
user_activity = {}

# Time window for considering a user active (60 seconds)
active_window = 60

def get_viewer_count():
    url = 'https://api.twitch.tv/helix/streams'
    params = {'user_login': 'fl0m'}
    
    response = requests.get(url, headers=headers, params=params)
    
    if response.status_code == 200:
        data = response.json()
        if data['data']:
            return data['data'][0]['viewer_count']
        else:
            return 0  # Stream is offline
    else:
        print(f"Error fetching viewer count: {response.status_code} - {response.text}")
        return None

def monitor_chat():
    try:
        print("Connecting to server...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock = ssl.wrap_socket(sock)
        sock.connect((server, port))
        print("Connected to server.")

        print("Authenticating...")
        sock.send(f"PASS {token}\n".encode('utf-8'))
        sock.send(f"NICK {nickname}\n".encode('utf-8'))
        print(f"Authenticated as {nickname}.")

        print(f"Joining {channel}'s chatroom...")
        sock.send(f"JOIN {channel}\n".encode('utf-8'))
        print(f"Joined {channel}'s chatroom.")

        last_viewer_count = get_viewer_count()
        last_update_time = time.time()

        while True:
            current_time = time.time()
            resp = sock.recv(2048).decode('utf-8')
            
            if resp.startswith('PING'):
                sock.send("PONG\n".encode('utf-8'))
                print("Responded to PING with PONG.")
            
            elif len(resp) > 0:
                parts = resp.split(' ')
                if len(parts) > 1 and parts[1] == "PRIVMSG":
                    username = parts[0].split('!')[0][1:]  # Extract the username
                    user_activity[username] = current_time

            # Update every 10 seconds
            if current_time - last_update_time >= 10:
                last_viewer_count = get_viewer_count()
                active_users = {user: timestamp for user, timestamp in user_activity.items()
                                if current_time - timestamp <= active_window}

                active_percentage = (len(active_users) / last_viewer_count) * 100 if last_viewer_count > 0 else 0
                print(f"Active chatters percentage: {active_percentage:.2f}% with {len(active_users)} active out of {last_viewer_count} viewers.")

                last_update_time = current_time

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    monitor_chat()