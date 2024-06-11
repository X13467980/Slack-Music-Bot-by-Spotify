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

# 過去に送信した曲のIDを保持するリスト
sent_track_ids = []

# ランダムに1曲を選択（過去に送信した曲は除外）
while True:
    track = random.choice(tracks)['track']
    track_id = track['id']
    if track_id not in sent_track_ids:
        break

# 曲の情報を取得
track_name = track['name']
artist_name = track['artists'][0]['name']
album_name = track['album']['name']
track_url = track['external_urls']['spotify']

# 送信済みの曲IDリストに追加
sent_track_ids.append(track_id)

# プレイリストの全曲を送信し終わった場合
if len(sent_track_ids) == len(tracks):
    sent_track_ids.clear()  # sent_track_idsリストを初期化

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