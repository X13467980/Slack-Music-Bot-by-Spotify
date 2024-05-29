import requests
import json
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import random

# Spotify APIにアクセスするための認証情報
CLIENT_ID = '801c2d22bb02478886affc4ea38f0e45'
CLIENT_SECRET = '88f463df5cb64dd3aebe8ea7cc5f0e0a'
REDIRECT_URI = 'http://localhost:3000/redirect'
SCOPE = 'user-library-read'

# Slackの割り込み用Webhook URL
WEBHOOK_URL = 'https://hooks.slack.com/services/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'

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

# iTunes Search APIを使ってApple Musicの曲を検索
query = f"{track_name} {artist_name}"
response = requests.get(f"https://itunes.apple.com/search?term={query}&entity=song")
data = response.json()

if data['resultCount'] > 0:
    song = data['results'][0]
    apple_music_url = song['trackViewUrl']
else:
    apple_music_url = "曲が見つかりませんでした"

# Slackに送信するメッセージを作成（Spotify）
spotify_message = {
    "blocks": [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Today's Recommended Song (Spotify):*\n<{track_url}|{artist_name} - {track_name}>"
            }
        }
    ]
}

# Slackに送信するメッセージを作成（Apple Music）
apple_music_message = {
    "blocks": [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*Today's Recommended Song (Apple Music):*\n<{apple_music_url}|{artist_name} - {track_name}>"
            }
        }
    ]
}

# ペイロードを定義
spotify_payload = json.dumps(spotify_message)
apple_music_payload = json.dumps(apple_music_message)

# POSTリクエストを送信（Spotify）
response = requests.post(WEBHOOK_URL, headers={'Content-Type': 'application/json'}, data=spotify_payload)

# POSTリクエストを送信（Apple Music）
response = requests.post(WEBHOOK_URL, headers={'Content-Type': 'application/json'}, data=apple_music_payload)

# レスポンスのステータスコードをチェック
if response.status_code == 200:
    print("メッセージが送信されました")
else:
    print(f"エラーが発生しました: {response.status_code}")