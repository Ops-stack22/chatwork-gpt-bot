from flask import Flask, request, jsonify
import json
import base64
from oauth2client.service_account import ServiceAccountCredentials
import gspread
import openai

# Flaskアプリケーションのインスタンスを作成
app = Flask(__name__)

# Google Sheets APIの設定
GOOGLE_CREDENTIALS_JSON = 'YOUR_BASE64_ENCODED_JSON_KEY'
SCOPE = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']

# JSONキーをデコードし、Google認証情報をセットアップ
creds_json = json.loads(base64.b64decode(GOOGLE_CREDENTIALS_JSON))
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_json, SCOPE)
client = gspread.authorize(creds)

# ChatGPTの設定
OPENAI_API_KEY = 'YOUR_OPENAI_API_KEY'
openai.api_key = OPENAI_API_KEY

# ルートエンドポイント
@app.route('/', methods=['GET', 'HEAD'])
def home():
    return 'Hello, this is the home page!', 200

# Chatwork Webhookエンドポイント
@app.route('/webhook', methods=['POST'])
def webhook():
    # Chatworkからのデータを処理
    data = request.json
    # 必要な処理をここで実行
    return jsonify({'status': 'success'}), 200

# アプリケーションのエントリーポイント
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000, debug=True)
