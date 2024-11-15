const { app, BrowserWindow,screen, ipcMain, exec } = require('electron');
const path = require('path');
const fs = require('fs');
const { spawn } = require('child_process');

let mainWindow;

function createWindow() {
  const mainWindow = new BrowserWindow({
    width: 800,
    height: 600,
    webPreferences: {
      nodeIntegration: true, // Enable Node integration
      contextIsolation: false, // Disable context isolation
      preload: path.join(__dirname, 'preload.js'), // Set the path to your preload script
      
    }
  });
  mainWindow.maximize();

  mainWindow.loadFile('register.html');

  mainWindow.on('closed', function () {
    mainWindow = null;
  });
}

app.on('ready', createWindow);


ipcMain.on('run-script', (event, formData) => {
  const { name, id, password, email } = formData;

  // Directory path where Python script is located
  const pythonScriptPath = path.join(__dirname, 's.py');
  console.log('Python script path:', pythonScriptPath);
  // Execute Python script
  const pythonProcess = spawn('python', [pythonScriptPath, email, password, name, id]);

  pythonProcess.stdout.on('data', (data) => {
    console.log(`Python script output: ${data}`);
  });

  pythonProcess.stderr.on('data', (data) => {
    console.error(`Error from Python script: ${data}`);
    event.reply('script-executed', { error: data.toString() });
  });

  pythonProcess.on('close', (code) => {
    if (code === 0) {
      console.log('Python script executed successfully.');
      event.reply('script-executed', { success: 'Python script executed successfully.' });
    } else {
      console.error(`Python script exited with code ${code}`);
      event.reply('script-executed', { error: `Python script exited with code ${code}` });
    }
  });
});
