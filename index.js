const express = require('express');
const Chatwork = require('chatwork-api');
const { Configuration, OpenAIApi } = require("openai");
const { google } = require('googleapis');
require('dotenv').config();

const app = express();
const port = process.env.PORT || 3000;

const chatwork = new Chatwork({ token: process.env.CHATWORK_API_TOKEN });
const configuration = new Configuration({
  apiKey: process.env.OPENAI_API_KEY,
});
const openai = new OpenAIApi(configuration);

const roomId = process.env.CHATWORK_ROOM_ID;
const myChatworkId = process.env.CHATWORK_ID;
const userName = process.env.USER_NAME;

let latestMessageId = 0;

async function checkMentionsAndReply() {
  try {
    const messages = await chatwork.getMessages(roomId, { force: 0, after_id: latestMessageId }); 

    for (const message of messages) {
      if (message.body.includes(`[To:${myChatworkId}]`) && message.account.account_id !== myChatworkId) {
        const reply = await generateReplyWithChatGPT(message.body);
        await chatwork.postMessage(roomId, reply);  
        await logToSpreadsheet(message.body, reply);
      }
      latestMessageId = Math.max(latestMessageId, message.message_id);
    }
  } catch (error) {
    console.error('Error checking mentions and replying:', error);
  }
}

async function generateReplyWithChatGPT(message) {
  try {
    const completion = await openai.createCompletion({ // 修正: createCompletion を使用
      model: "text-davinci-003", // モデルを適切なものに変更してください
      prompt: message,
      max_tokens: 100, // 必要に応じて調整してください
    });
    return completion.data.choices[0].text; 
  } catch (error) {
    console.error('Error generating reply with ChatGPT:', error);
    return '申し訳ありません、現在返信を生成できません。';
  }
}

async function logToSpreadsheet(mention, reply) {
  const auth = new google.auth.GoogleAuth({
    credentials: JSON.parse(Buffer.from(process.env.GOOGLE_APPLICATION_CREDENTIALS, 'base64').toString()),
    scopes: ['https://www.googleapis.com/auth/spreadsheets'],
  });

  const sheets = google.sheets({ version: 'v4', auth });

  const spreadsheetId = process.env.GOOGLE_SPREADSHEET_ID;
  const sheetName = process.env.GOOGLE_SPREADSHEET_SHEET_NAME;

  const values = [
    [
      new Date().toISOString(),
      mention,
      reply,
    ],
  ];

  try {
    await sheets.spreadsheets.values.append({
      spreadsheetId,
      range: `${sheetName}!A:C`,
      valueInputOption: 'USER_ENTERED',
      resource: { values },
    });
    console.log('Logged to spreadsheet successfully.');
  } catch (err) {
    console.error('Error logging to spreadsheet:', err);
  }
}

setInterval(checkMentionsAndReply, 60000); // 1分ごとに実行

app.get('/', (req, res) => {
  res.send('Chatwork bot is running!');
});

app.listen(port, () => {
  console.log(`Server is running on port ${port}`);
});
