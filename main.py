import os
import requests
import json
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import random
from dotenv import load_dotenv

# .envファイルから環境変数をロード
load_dotenv()

# Spotify APIにアクセスするための認証情報を環境変数から取得
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
REDIRECT_URI = os.getenv('REDIRECT_URI')
SCOPE = os.getenv('SCOPE')

# Slackの割り込み用Webhook URL
WEBHOOK_URL = os.getenv('WEBHOOK_URL')

# SpotifyのAPIにアクセスするためのオブジェクトを作成
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(CLIENT_ID, CLIENT_SECRET, REDIRECT_URI, scope=SCOPE))

# 指定したプレイリストのIDを入力
playlist_id = '7Dnr7tujQCxUlDWFQq4awh'

# 指定したプレイリストの曲を取得
playlist = sp.playlist_tracks(playlist_id)
tracks = playlist['items']

# ランダムに1曲を選択
track = random.choice(tracks)['track']

# 曲の情報を取得
track_name = track['name']
artist_name = track['artists'][0]['name']
album_name = track['album']['name']
track_url = track['external_urls']['spotify']

# Slackに送信するメッセージを作成（Spotify）
spotify_message = {
    "blocks": [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Today's Recommended Song : *\n*{artist_name} - {track_name} (Spotify):*\n<{track_url}|Listen on Spotify>"
            }
        }
    ]
}

# ペイロードを定義
spotify_payload = json.dumps(spotify_message)

# POSTリクエストを送信（Spotify）
response = requests.post(WEBHOOK_URL, headers={'Content-Type': 'application/json'}, data=spotify_payload)

# レスポンスのステータスコードをチェック
if response.status_code == 200:
    print("Spotify メッセージが送信されました")
else:
    print(f"エラーが発生しました: {response.status_code}")

# iTunes Search APIを使ってApple Musicの曲を検索
query = f"{artist_name} {track_name}"
response = requests.get(f"https://itunes.apple.com/search?term={query}&entity=song")
data = response.json()

if data['resultCount'] > 0:
    song = data['results'][0]
    apple_music_url = song['trackViewUrl']
    apple_music_message = {
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{artist_name} - {track_name} (Apple Music):*\n<{apple_music_url}|Listen on Apple Music>"
                }
            }
        ]
    }
    apple_music_payload = json.dumps(apple_music_message)
    response = requests.post(WEBHOOK_URL, headers={'Content-Type': 'application/json'}, data=apple_music_payload)
    
    if response.status_code == 200:
        print("Apple Music メッセージが送信されました")
    else:
        print(f"エラーが発生しました: {response.status_code}")
else:
    print("Apple Musicで曲が見つかりませんでした")