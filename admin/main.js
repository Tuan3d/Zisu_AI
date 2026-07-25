const { app, BrowserWindow } = require('electron');
const path = require('path');

let adminWindow = null;

function createAdminWindow() {
  adminWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    backgroundColor: '#090d16',
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false
    }
  });

  adminWindow.loadFile(path.join(__dirname, 'index.html'));

  adminWindow.on('closed', () => {
    adminWindow = null;
  });
}

app.whenReady().then(() => {
  createAdminWindow();

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createAdminWindow();
    }
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') {
    app.quit();
  }
});
