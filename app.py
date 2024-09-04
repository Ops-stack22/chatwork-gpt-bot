import os
import json
import base64
import openai
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from flask import Flask, request, jsonify

app = Flask(__name__)

# Google Sheetsの設定
SHEET_ID = "1ukpI8yUeW6fwokESJadTMNGU65vXBwquqMKGlXNnJ-8"
SHEET_NAME = "Chatwork-ChatGPT連携用"

# OpenAI APIキー
openai.api_key = os.getenv("OPENAI_API_KEY")

# Googleサービスアカウントの認証情報を環境変数から読み込み
GOOGLE_CREDENTIALS_JSON = os.getenv("GOOGLE_CREDENTIALS")

# Base64でデコードしてjson形式に戻す
creds_json = json.loads(base64.b64decode(GOOGLE_CREDENTIALS_JSON))

scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_json, scope)
client = gspread.authorize(creds)

sheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)

# Flaskのルートとエンドポイントを定義する
@app.route('/', methods=['POST'])
def chatwork_webhook():
    data = request.json
    # ここにデータ処理とOpenAIの処理を追加
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
