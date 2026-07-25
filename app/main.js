const { app, BrowserWindow, globalShortcut, ipcMain, screen } = require('electron');
const path = require('path');

let overlayWindow = null;

function createOverlayWindow() {
  const primaryDisplay = screen.getPrimaryDisplay();
  const { width, height } = primaryDisplay.size;

  overlayWindow = new BrowserWindow({
    width: width,
    height: height,
    x: 0,
    y: 0,
    frame: false,
    transparent: true,
    alwaysOnTop: true,
    skipTaskbar: true,
    resizable: false,
    hasShadow: false,
    webPreferences: {
      nodeIntegration: true,
      contextIsolation: false
    }
  });

  // Cho phép click xuyên qua phần kính/trong suốt trừ các vùng UI
  overlayWindow.setIgnoreMouseEvents(true, { forward: true });

  overlayWindow.loadFile(path.join(__dirname, 'index.html'));

  // Ẩn ban đầu, chỉ hiện khi gọi phím tắt
  overlayWindow.hide();

  // Đảm bảo không block chuột/bàn phím khi không kích hoạt
  // Ở dạng trong suốt hoàn toàn lúc ban đầu, ta ẩn hẳn cửa sổ đi
  overlayWindow.on('closed', () => {
    overlayWindow = null;
  });
}

app.whenReady().then(() => {
  createOverlayWindow();

  // Đăng ký phím tắt Shift+Z
  const ret = globalShortcut.register('Shift+Z', () => {
    if (overlayWindow) {
      if (overlayWindow.isVisible()) {
        // Gửi sự kiện ẩn để thực hiện animation slide out trước khi ẩn cửa sổ
        overlayWindow.webContents.send('toggle-overlay', 'hide');
      } else {
        overlayWindow.show();
        overlayWindow.focus();
        overlayWindow.webContents.send('toggle-overlay', 'show');
      }
    }
  });

  if (!ret) {
    console.log('Registration failed');
  }

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createOverlayWindow();
    }
  });
});

app.on('will-quit', () => {
  globalShortcut.unregisterAll();
});

// IPC communication to hide window after animation
ipcMain.on('hide-window', () => {
  if (overlayWindow) {
    overlayWindow.hide();
  }
});

// IPC communication to handle dynamic click-through
ipcMain.on('set-ignore-mouse-events', (event, ignore, options) => {
  if (overlayWindow) {
    overlayWindow.setIgnoreMouseEvents(ignore, options);
  }
});

