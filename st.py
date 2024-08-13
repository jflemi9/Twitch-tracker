
import socket
import ssl
import time
import requests
import streamlit as st

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

# Streamlit elements for displaying data
st.title("Fl0m Chat Tracker made by me")
st.image("imageidk.webp")
warning_placeholder = st.text("give it a sec to start tracking...")
viewer_count_placeholder = st.empty()
active_percentage_placeholder = st.empty()

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
        st.error(f"Error fetching viewer count: {response.status_code} - {response.text}")
        return None

def monitor_chat():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock = ssl.wrap_socket(sock)
        sock.connect((server, port))

        sock.send(f"PASS {token}\n".encode('utf-8'))
        sock.send(f"NICK {nickname}\n".encode('utf-8'))

        sock.send(f"JOIN {channel}\n".encode('utf-8'))

        last_viewer_count = get_viewer_count()
        last_update_time = time.time()

        while True:
            current_time = time.time()
            resp = sock.recv(2048).decode('utf-8')
            
            if resp.startswith('PING'):
                sock.send("PONG\n".encode('utf-8'))
                st.write("Responded to PING with PONG.")
            
            elif len(resp) > 0:
                warning_placeholder = st.empty()
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
                active_chatter_info = f"{active_percentage:.2f}% ({len(active_users)} chatters)"
                
                # Update the Streamlit placeholders
                viewer_count_placeholder.metric("Total Viewers", last_viewer_count)
                active_percentage_placeholder.metric("Active Chatters", active_chatter_info)

                last_update_time = current_time

            # To prevent infinite loop in Streamlit and allow UI updates
            time.sleep(1)

    except Exception as e:
        st.error(f"Error: {e}")

if __name__ == "__main__":
    monitor_chat()