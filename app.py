from flask import Flask, request, jsonify
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import openai
import os

app = Flask(__name__)

# Chatwork and Google Sheets setup
CHATWORK_API_TOKEN = 'e8569277706907361d23b440a7ba7edf'
ROOM_ID = '368727934'
MENTION_NAME = '[To:7143943] GROOVE Ops＠林さん'
SHEET_ID = '1ukpI8yUeW6fwokESJadTMNGU65vXBwquqMKGlXNnJ-8'
SHEET_NAME = 'Chatwork-ChatGPT連携用'

# OpenAI setup
openai.api_key = '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'

# Google Sheets setup
GOOGLE_CREDENTIALS_FILE = 'path/to/credentials.json'  # 必ず正しいパスに変更
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets", "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(GOOGLE_CREDENTIALS_FILE, scope)
client = gspread.authorize(creds)
sheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)

@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    if data and 'webhook_event' in data:
        event = data['webhook_event']
        message = event['body']
        if MENTION_NAME in message:
            question = message.split(MENTION_NAME)[-1].strip()
            answer = get_openai_response(question)
            post_to_chatwork(answer)
            log_to_sheet(question, answer)
            return jsonify({"status": "success"}), 200
    return jsonify({"status": "failed"}), 400

def get_openai_response(question):
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=question,
        max_tokens=150
    )
    return response.choices[0].text.strip()

def post_to_chatwork(message):
    url = f"https://api.chatwork.com/v2/rooms/{ROOM_ID}/messages"
    headers = {"X-ChatWorkToken": CHATWORK_API_TOKEN}
    payload = {"body": message}
    requests.post(url, headers=headers, data=payload)

def log_to_sheet(question, answer):
    sheet.append_row([question, answer])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000, debug=True)
