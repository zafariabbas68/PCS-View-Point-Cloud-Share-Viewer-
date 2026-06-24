const { app, BrowserWindow, Menu, ipcMain, dialog, shell } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

// Simple isDev check - no external dependency
const isDev = !app.isPackaged;

let mainWindow;
let serverProcess;

// ===== START FASTAPI SERVER =====
function startServer() {
    const serverPath = path.join(__dirname, '..', 'run.py');
    
    console.log('🚀 Starting FastAPI server...');
    
    serverProcess = spawn('python3', [serverPath], {
        cwd: path.join(__dirname, '..'),
        env: { ...process.env, PORT: '8000', PCS_DESKTOP: 'true' },
        stdio: 'pipe'
    });

    serverProcess.stdout.on('data', (data) => {
        console.log(`📡 Server: ${data}`);
    });

    serverProcess.stderr.on('data', (data) => {
        console.error(`⚠️ Server Error: ${data}`);
    });

    serverProcess.on('close', (code) => {
        console.log(`Server process exited with code ${code}`);
    });

    // Wait for server to start
    return new Promise((resolve) => {
        setTimeout(resolve, 3000);
    });
}

// ===== CREATE MAIN WINDOW =====
function createWindow() {
    mainWindow = new BrowserWindow({
        width: 1400,
        height: 900,
        minWidth: 1024,
        minHeight: 768,
        webPreferences: {
            nodeIntegration: false,
            contextIsolation: true,
            preload: path.join(__dirname, 'preload.js')
        },
        show: false,
        frame: true,
        titleBarStyle: 'default',
        backgroundColor: '#f0f4f8'
    });

    // Load the app
    const url = 'http://127.0.0.1:8000';
    mainWindow.loadURL(url);

    // Show window when ready
    mainWindow.once('ready-to-show', () => {
        mainWindow.show();
        mainWindow.setTitle('PCS-View - Professional Point Cloud Platform');
    });

    // Handle window closed
    mainWindow.on('closed', () => {
        mainWindow = null;
    });

    // Open DevTools in development
    if (isDev) {
        mainWindow.webContents.openDevTools();
    }

    // ===== CUSTOM MENU =====
    const template = [
        {
            label: 'PCS-View',
            submenu: [
                { 
                    label: 'About PCS-View', 
                    click: () => { 
                        dialog.showMessageBox(mainWindow, {
                            type: 'info',
                            title: 'About PCS-View',
                            message: 'PCS-View v2.0.0',
                            detail: 'Professional Point Cloud Platform\n\n' +
                                   'Developed by: Ghulam Abbas Zafari\n' +
                                   'Email: ghalambabas.zafari@gmail.com\n' +
                                   'Institution: Politecnico di Milano\n\n' +
                                   '© 2026 All Rights Reserved',
                            buttons: ['OK']
                        });
                    } 
                },
                { type: 'separator' },
                { 
                    label: 'Preferences', 
                    click: () => { mainWindow.webContents.send('menu-settings'); } 
                },
                { type: 'separator' },
                { label: 'Quit', accelerator: 'CmdOrCtrl+Q', click: () => { app.quit(); } }
            ]
        },
        {
            label: 'File',
            submenu: [
                { label: 'Import Point Cloud', accelerator: 'CmdOrCtrl+I', click: () => { mainWindow.webContents.send('menu-import'); } },
                { label: 'Export Point Cloud', accelerator: 'CmdOrCtrl+E', click: () => { mainWindow.webContents.send('menu-export'); } },
                { type: 'separator' },
                { label: 'Close', accelerator: 'CmdOrCtrl+W', click: () => { mainWindow.close(); } }
            ]
        },
        {
            label: 'View',
            submenu: [
                { label: 'Reset View', accelerator: 'CmdOrCtrl+R', click: () => { mainWindow.webContents.send('menu-reset'); } },
                { label: 'Toggle Grid', accelerator: 'CmdOrCtrl+G', click: () => { mainWindow.webContents.send('menu-grid'); } },
                { type: 'separator' },
                { label: 'Toggle Fullscreen', accelerator: 'F11', role: 'togglefullscreen' },
                { label: 'Reload', accelerator: 'CmdOrCtrl+Shift+R', role: 'reload' },
                { label: 'Developer Tools', accelerator: 'CmdOrCtrl+Shift+I', role: 'toggleDevTools' }
            ]
        },
        {
            label: 'Tools',
            submenu: [
                { label: 'Volume Calculator', click: () => { mainWindow.webContents.send('menu-volume'); } },
                { label: 'Cut & Fill', click: () => { mainWindow.webContents.send('menu-cutfill'); } },
                { label: 'Classification', click: () => { mainWindow.webContents.send('menu-classify'); } },
                { type: 'separator' },
                { label: 'Orthophoto', click: () => { mainWindow.webContents.send('menu-orthophoto'); } },
                { label: 'Superelevation', click: () => { mainWindow.webContents.send('menu-superelevation'); } },
                { label: 'Esplanade', click: () => { mainWindow.webContents.send('menu-esplanade'); } }
            ]
        },
        {
            label: 'Help',
            submenu: [
                { 
                    label: 'Documentation', 
                    click: () => { 
                        shell.openExternal('https://github.com/zafariabbas68/PCS-View-Point-Cloud-Share-Viewer-');
                    } 
                },
                { 
                    label: 'GitHub Repository', 
                    click: () => { 
                        shell.openExternal('https://github.com/zafariabbas68/PCS-View-Point-Cloud-Share-Viewer-');
                    } 
                },
                { 
                    label: 'Contact Developer', 
                    click: () => { 
                        shell.openExternal('mailto:ghalambabas.zafari@gmail.com');
                    } 
                },
                { type: 'separator' },
                { 
                    label: 'About PCS-View', 
                    click: () => { mainWindow.webContents.send('menu-about'); } 
                }
            ]
        }
    ];

    const menu = Menu.buildFromTemplate(template);
    Menu.setApplicationMenu(menu);
}

// ===== APP LIFE CYCLE =====
app.whenReady().then(async () => {
    await startServer();
    createWindow();
});

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

// ===== CLEANUP =====
app.on('before-quit', () => {
    if (serverProcess) {
        serverProcess.kill();
    }
});

// ===== IPC HANDLERS =====
ipcMain.handle('dialog:openFile', async () => {
    const result = await dialog.showOpenDialog(mainWindow, {
        properties: ['openFile'],
        filters: [
            { name: 'Point Clouds', extensions: ['las', 'laz', 'ply', 'e57', 'xyz', 'txt', 'cx3d'] },
            { name: 'All Files', extensions: ['*'] }
        ]
    });
    return result;
});

console.log('🌍 PCS-View Desktop Application Started');
console.log('👨‍💻 Author: Ghulam Abbas Zafari');
console.log('📧 Email: ghalambabas.zafari@gmail.com');
console.log('🏛️  Politecnico di Milano');
