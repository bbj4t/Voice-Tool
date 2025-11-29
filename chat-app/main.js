const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');

let mainWindow;

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    minWidth: 800,
    minHeight: 600,
    webPreferences: {
      nodeIntegration: false,
      contextIsolation: true,
      preload: path.join(__dirname, 'preload.js')
    },
    titleBarStyle: 'hiddenInset',
    backgroundColor: '#1a1a2e',
    show: false
  });

  mainWindow.loadFile('index.html');

  // Show window when ready
  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
  });

  // Open DevTools in dev mode
  if (process.argv.includes('--dev')) {
    mainWindow.webContents.openDevTools();
  }
}

app.whenReady().then(createWindow);

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});

// IPC handlers for settings persistence
ipcMain.handle('get-settings', () => {
  const Store = require('electron-store');
  const store = new Store();
  return store.get('settings', {
    voiceServiceUrl: 'http://localhost:8765',
    ttsExaggeration: 0.5,
    ttsTemperature: 0.8,
    ttsCfgWeight: 0.5
  });
});

ipcMain.handle('save-settings', (event, settings) => {
  const Store = require('electron-store');
  const store = new Store();
  store.set('settings', settings);
  return true;
});
