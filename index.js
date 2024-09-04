const { google } = require('googleapis');

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
