from flask import Flask, request, jsonify
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os

app = Flask(__name__)

# 必要なAPIキーと情報
OPENAI_API_KEY = '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'
CHATWORK_API_TOKEN = 'e8569277706907361d23b440a7ba7edf'
CHATWORK_ROOM_ID = '368727934'
CHATWORK_ACCOUNT_ID = '7143943'  # 自動で返信させたいChatworkのアカウントID
SHEET_ID = '1ukpI8yUeW6fwokESJadTMNGU65vXBwquqMKGlXNnJ-8'
SHEET_NAME = 'Chatwork-ChatGPT連携用'
GOOGLE_CREDENTIALS_FILE = 'path/to/credentials.json'  # GoogleサービスアカウントのJSONファイルパス

# Google Sheets APIの認証設定
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_CREDENTIALS_FILE, scope)
client = gspread.authorize(creds)
sheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)

@app.route('/webhook', methods=['POST'])
def webhook():
    # ChatworkからのWebhookリクエストを受信
    data = request.json
    print("Received data:", data)

    if not data or 'webhook_event' not in data:
        return jsonify({'status': 'error', 'message': 'Invalid request'}), 400

    message = data['webhook_event']['body']
    account_id = data['webhook_event']['account_id']
    room_id = data['webhook_event']['room_id']

    # メンションされたかどうか確認
    if f"[To:{CHATWORK_ACCOUNT_ID}]GROOVE Ops＠林さん" in message:
        question = message.split("\n", 1)[-1].strip()  # メンションを除いた質問部分

        # OpenAI APIを使って質問に回答を生成
        answer = get_openai_response(question)

        # Chatworkに回答を投稿
        post_to_chatwork(room_id, account_id, answer)

        # スプレッドシートにログを記録
        log_to_sheet(message, answer)

        return jsonify({'status': 'success'}), 200
    else:
        return jsonify({'status': 'ignored', 'message': 'No mention to target user'}), 200

def get_openai_response(question):
    url = 'https://api.openai.com/v1/completions'
    headers = {
        'Authorization': f'Bearer {OPENAI_API_KEY}',
        'Content-Type': 'application/json'
    }
    payload = {
        'model': 'gpt-4',  # 使用するモデル
        'prompt': question,
        'max_tokens': 150
    }

    response = requests.post(url, json=payload, headers=headers)
    response_data = response.json()

    if 'choices' in response_data and len(response_data['choices']) > 0:
        return response_data['choices'][0]['text'].strip()
    else:
        return "I'm sorry, I couldn't understand your question."

def post_to_chatwork(room_id, account_id, message):
    url = f'https://api.chatwork.com/v2/rooms/{room_id}/messages'
    headers = {
        'X-ChatWorkToken': CHATWORK_API_TOKEN
    }
    payload = {
        'body': f'[To:{account_id}] {message}'
    }

    requests.post(url, headers=headers, data=payload)

def log_to_sheet(question, answer):
    try:
        sheet.append_row([question, answer])
    except Exception as e:
        print(f"Error logging to sheet: {e}")

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
