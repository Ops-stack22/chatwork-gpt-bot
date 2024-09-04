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

const targetRoomId = process.env.CHATWORK_ROOM_ID; 
const myChatworkId = process.env.CHATWORK_ID;
const userName = process.env.USER_NAME;

let latestMessageId = 0;

async function checkMentionsAndReply() {
  try {
    // ルーム内のメンションをチェック
    const roomMessages = await chatwork.getMessages(targetRoomId, { force: 0, after_id: latestMessageId }); 

    for (const message of messages) {
      if (message.body.includes(`[To:${myChatworkId}]`) && message.account.account_id !== myChatworkId) { 
        const suggestedReply = await generateReplyWithChatGPT(message.body);
        const finalReply = processSuggestedReply(suggestedReply); 
        await chatwork.postMessage(targetRoomId, finalReply);  
        await logToSpreadsheet(message.body, suggestedReply, finalReply);
      }
      latestMessageId = Math.max(latestMessageId, message.message_id);
    }

  } catch (error) {
    console.error('Error checking mentions and replying:', error);
  }
}

async function generateReplyWithChatGPT(message) {
  try {
    const completion = await openai.createCompletion({ 
      model: "text-davinci-003", 
      prompt: message,
      max_tokens: 100, 
    });
    return completion.data.choices[0].text.trim(); 
  } catch (error) {
    console.error('Error generating reply with ChatGPT:', error);
    return '申し訳ありません、現在返信を生成できません。'; 
  }
}

function processSuggestedReply(suggestedReply) {
  // 必要に応じて、suggestedReply を編集する処理を追加
  return suggestedReply; 
}

async function logToSpreadsheet(mention, suggestedReply, finalReply) {
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
      suggestedReply,
      finalReply,
    ],
  ];

  try {
    await sheets.spreadsheets.values.append({
      spreadsheetId,
      range: `${sheetName}!A:D`, // ログの列数を4に変更
      valueInputOption: 'USER_ENTERED',
      resource: { values },
    });
    console.log('Logged to spreadsheet successfully.');
  } catch (err) {
    console.error('Error logging to spreadsheet:', err);
  }
}

setInterval(checkMentionsAndReply, 60000); 

app.get('/', (req, res) => {
  res.send('Chatwork bot is running!');
});

app.listen(port, () => {
  console.log(`Server is running on port ${port}`);
});
