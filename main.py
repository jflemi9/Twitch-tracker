# import socket
# import ssl
# import time

# server = 'irc.chat.twitch.tv'
# port = 6697
# nickname = 'jamesschoolaccount2'
# token = 'oauth:7095t3dnc5rv5ldka6yxsqdcykqkzl'
# channel = '#fl0m'

# # Dictionary to track the last message time for each unique user
# user_activity = {}

# # Time window for considering a user active (60 seconds)
# active_window = 60

# try:
#     print("Connecting to server...")
#     sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     sock = ssl.wrap_socket(sock)
#     sock.connect((server, port))
#     print("Connected to server.")

#     print("Authenticating...")
#     sock.send(f"PASS {token}\n".encode('utf-8'))
#     sock.send(f"NICK {nickname}\n".encode('utf-8'))
#     print(f"Authenticated as {nickname}.")

#     print(f"Joining {channel}'s chatroom...")
#     sock.send(f"JOIN {channel}\n".encode('utf-8'))
#     print(f"Joined {channel}'s chatroom.")

#     while True:
#         resp = sock.recv(2048).decode('utf-8')
        
#         if resp.startswith('PING'):
#             sock.send("PONG\n".encode('utf-8'))
#             print("Responded to PING with PONG.")
        
#         elif len(resp) > 0:
#             # Split the message into components
#             parts = resp.split(' ')
#             if len(parts) > 1 and parts[1] == "PRIVMSG":
#                 username = parts[0].split('!')[0][1:]  # Extract the username
#                 current_time = time.time()

#                 # Update the last message time for the user
#                 user_activity[username] = current_time

#                 # Remove users who are no longer active (last message older than 60 seconds)
#                 active_users = {user: timestamp for user, timestamp in user_activity.items()
#                                 if current_time - timestamp <= active_window}

#                 # Calculate the percentage of active users
#                 total_users = len(user_activity)
#                 active_percentage = (len(active_users) / total_users) * 100 if total_users > 0 else 0

#                 print(f"Active chatters percentage: {active_percentage:.2f}%")

# except Exception as e:
#     print(f"Error: {e}")

import requests
import time

# Twitch API credentials (replace with your own)
client_id = 'wwzwkqcag0y1swzv8x4wbazhs6vun1'
access_token = '7095t3dnc5rv5ldka6yxsqdcykqkzl'
headers = {
    'Client-ID': client_id,
    'Authorization': f'Bearer {access_token}'
}

# Streamer's username
streamer = 'fl0m'

def get_viewer_count():
    url = 'https://api.twitch.tv/helix/streams'
    params = {'user_login': streamer}
    
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

def main():
    last_viewer_count = -1  # Initialize with an impossible count
    print("Starting viewer count monitor...")

    while True:
        current_viewer_count = get_viewer_count()
        
        if current_viewer_count is not None and current_viewer_count != last_viewer_count:
            print(f"Current viewers: {current_viewer_count}")
            last_viewer_count = current_viewer_count
        
        time.sleep(10)  # Wait 10 seconds before checking again

if __name__ == "__main__":
    main()