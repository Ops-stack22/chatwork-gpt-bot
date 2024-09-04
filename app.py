import base64
import json
from flask import Flask, request, jsonify
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import os

app = Flask(__name__)

# 環境変数からAPIキーを取得
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
CHATWORK_API_TOKEN = os.getenv('CHATWORK_API_TOKEN')
CHATWORK_ROOM_ID = '368727934'
CHATWORK_ACCOUNT_ID = '7143943'  # 自動で返信させたいChatworkのアカウントID
SHEET_ID = '1ukpI8yUeW6fwokESJadTMNGU65vXBwquqMKGlXNnJ-8'
SHEET_NAME = 'Chatwork-ChatGPT連携用'

# 環境変数からエンコードされた認証情報を取得しデコード
encoded_credentials = os.getenv('GOOGLE_CREDENTIALS_FILE')
decoded_credentials = base64.b64decode(encoded_credentials)

# 認証情報をJSON形式でロード
creds_dict = json.loads(decoded_credentials)

# Google Sheets APIの認証設定
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
client = gspread.authorize(creds)
sheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    print("Received data:", data)

    if not data or 'webhook_event' not in data:
        return jsonify({'status': 'error', 'message': 'Invalid request'}), 400

    message = data['webhook_event']['body']
    account_id = data['webhook_event']['account_id']
    room_id = data['webhook_event']['room_id']

    if f"[To:{CHATWORK_ACCOUNT_ID}]GROOVE Ops＠林さん" in message:
        question = message.split("\n", 1)[-1].strip()

        answer = get_openai_response(question)
        post_to_chatwork(room_id, account_id, answer)
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
        'model': 'gpt-4',
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
