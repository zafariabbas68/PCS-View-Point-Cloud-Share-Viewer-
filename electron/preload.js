const { contextBridge, ipcRenderer } = require('electron');

// Expose protected methods that allow the renderer process to use
// the ipcRenderer without exposing the entire object
contextBridge.exposeInMainWorld(
    'electron',
    {
        openFile: () => ipcRenderer.invoke('dialog:openFile'),
        onMenuImport: (callback) => ipcRenderer.on('menu-import', callback),
        onMenuExport: (callback) => ipcRenderer.on('menu-export', callback),
        onMenuReset: (callback) => ipcRenderer.on('menu-reset', callback),
        onMenuGrid: (callback) => ipcRenderer.on('menu-grid', callback),
        onMenuVolume: (callback) => ipcRenderer.on('menu-volume', callback),
        onMenuCutfill: (callback) => ipcRenderer.on('menu-cutfill', callback),
        onMenuClassify: (callback) => ipcRenderer.on('menu-classify', callback),
        onMenuOrthophoto: (callback) => ipcRenderer.on('menu-orthophoto', callback),
        onMenuSuperelevation: (callback) => ipcRenderer.on('menu-superelevation', callback),
        onMenuEsplanade: (callback) => ipcRenderer.on('menu-esplanade', callback),
        onMenuAbout: (callback) => ipcRenderer.on('menu-about', callback),
        onMenuSettings: (callback) => ipcRenderer.on('menu-settings', callback),
        onMenuHelp: (callback) => ipcRenderer.on('menu-help', callback)
    }
);

console.log('🔌 Preload script loaded');
