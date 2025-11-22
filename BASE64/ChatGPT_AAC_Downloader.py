import os
import json
from pathlib import Path
from PIL import Image, ImageDraw

# Создаём папку плагина
plugin_dir = Path("ChatGPT_AAC_Downloader")
plugin_dir.mkdir(exist_ok=True)

# manifest.json
manifest = {
    "manifest_version": 3,
    "name": "ChatGPT AAC Auto Downloader",
    "version": "2.3",
    "description": "Автоматически скачивает AAC-файлы с удобным плеером",
    "permissions": ["downloads", "storage", "webRequest"],
    "host_permissions": [
        "https://chatgpt.com/*",
        "https://*.chatgpt.com/*",
        "https://*.oaiusercontent.com/*",
        "https://cdn.oaistatic.com/*"
    ],
    "action": {
        "default_popup": "popup.html",
        "default_icon": {
            "16": "icon16.png",
            "48": "icon48.png",
            "128": "icon128.png"
        }
    },
"content_scripts": [{
    "matches": ["https://chatgpt.com/*"],
    "js": ["inject.js"],
    "run_at": "document_start",
    "all_frames": False  # ✅ Python булевый литерал
}],
    "background": {
        "service_worker": "background.js"
    },
    "web_accessible_resources": [{
        "resources": ["interceptor.js"],
        "matches": ["https://chatgpt.com/*"]
    }],
    "icons": {
        "16": "icon16.png",
        "48": "icon48.png",
        "128": "icon128.png"
    }
}
(plugin_dir / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")

# popup.html и popup.css остаются те же
popup_html = """<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ChatGPT AAC Downloader</title>
    <link rel="stylesheet" href="popup.css">
</head>
<body>
    <div class="container">
        <header>
            <div class="header-content">
                <div class="logo">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                        <path d="M12 2C10.89 2 10 2.89 10 4V12C10 13.11 10.89 14 12 14C13.11 14 14 13.11 14 12V4C14 2.89 13.11 2 12 2Z" fill="#10a37f"/>
                        <path d="M12 16C8.13 16 5 13.31 5 10H7C7 12.21 9.24 14 12 14C14.76 14 17 12.21 17 10H19C19 13.31 15.87 16 12 16Z" fill="#10a37f"/>
                        <path d="M11 18H13V22H11V18Z" fill="#10a37f"/>
                        <path d="M8 22H16V20H8V22Z" fill="#10a37f"/>
                    </svg>
                    <h1>AAC Downloader</h1>
                </div>
                <div class="stats">
                    <span id="totalFiles">0</span> файлов
                </div>
            </div>
        </header>

        <div class="controls">
            <button id="clearAll" class="btn btn-danger">
                <svg width="16" height="16" viewBox="0 0 16 16" fill="currentColor">
                    <path d="M5.5 5.5A.5.5 0 0 1 6 6v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm2.5 0a.5.5 0 0 1 .5.5v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm3 .5a.5.5 0 0 0-1 0v6a.5.5 0 0 0 1 0V6z"/>
                    <path d="M14.5 3a1 1 0 0 1-1 1H13v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4h-.5a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1H6a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1h3.5a1 1 0 0 1 1 1v1zM4.118 4 4 4.059V13a1 1 0 0 0 1 1h6a1 1 0 0 0 1-1V4.059L11.882 4H4.118zM2.5 3V2h11v1h-11z"/>
                </svg>
                Очистить всё
            </button>
            <label class="switch">
                <input type="checkbox" id="autoDownload" checked>
                <span class="slider"></span>
                <span class="label">Авто-скачивание</span>
            </label>
        </div>

        <div id="emptyState" class="empty-state">
            <svg width="64" height="64" viewBox="0 0 64 64" fill="none">
                <circle cx="32" cy="32" r="30" stroke="#e5e7eb" stroke-width="2"/>
                <path d="M32 16C28.69 16 26 18.69 26 22V34C26 37.31 28.69 40 32 40C35.31 40 38 37.31 38 34V22C38 18.69 35.31 16 32 16Z" fill="#e5e7eb"/>
                <path d="M32 44C25.37 44 20 38.93 20 32.5H23C23 37.19 27.04 41 32 41C36.96 41 41 37.19 41 32.5H44C44 38.93 38.63 44 32 44Z" fill="#e5e7eb"/>
                <path d="M30 46H34V54H30V46Z" fill="#e5e7eb"/>
                <path d="M26 54H38V52H26V54Z" fill="#e5e7eb"/>
            </svg>
            <p>Голосовые сообщения ещё не загружены</p>
            <small>Откройте ChatGPT и попросите озвучить текст</small>
        </div>

        <div id="filesList" class="files-list"></div>
    </div>

    <script src="popup.js"></script>
</body>
</html>
"""
(plugin_dir / "popup.html").write_text(popup_html, encoding="utf-8")

# Используем предыдущий CSS
with open(plugin_dir / "popup.css", "w", encoding="utf-8") as f:
    f.write("""* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    width: 450px;
    min-height: 300px;
    max-height: 600px;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: #f9fafb;
}

.container {
    display: flex;
    flex-direction: column;
    height: 100%;
}

header {
    background: linear-gradient(135deg, #10a37f 0%, #0d8c6c 100%);
    color: white;
    padding: 16px 20px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.header-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.logo {
    display: flex;
    align-items: center;
    gap: 10px;
}

.logo svg {
    filter: brightness(0) invert(1);
}

.logo h1 {
    font-size: 18px;
    font-weight: 600;
}

.stats {
    background: rgba(255,255,255,0.2);
    padding: 6px 12px;
    border-radius: 20px;
    font-size: 13px;
    font-weight: 500;
}

.controls {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 16px 20px;
    background: white;
    border-bottom: 1px solid #e5e7eb;
}

.btn {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 8px 14px;
    border: none;
    border-radius: 6px;
    font-size: 13px;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s;
}

.btn-danger {
    background: #fee;
    color: #dc2626;
}

.btn-danger:hover {
    background: #fdd;
}

.switch {
    display: flex;
    align-items: center;
    gap: 8px;
    cursor: pointer;
}

.switch input {
    display: none;
}

.slider {
    width: 40px;
    height: 22px;
    background: #cbd5e1;
    border-radius: 11px;
    position: relative;
    transition: 0.3s;
}

.slider::before {
    content: '';
    position: absolute;
    width: 18px;
    height: 18px;
    border-radius: 50%;
    background: white;
    top: 2px;
    left: 2px;
    transition: 0.3s;
}

.switch input:checked + .slider {
    background: #10a37f;
}

.switch input:checked + .slider::before {
    transform: translateX(18px);
}

.switch .label {
    font-size: 13px;
    font-weight: 500;
    color: #374151;
}

.empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    padding: 60px 40px;
    text-align: center;
    color: #9ca3af;
}

.empty-state svg {
    margin-bottom: 16px;
}

.empty-state p {
    font-size: 15px;
    font-weight: 500;
    color: #6b7280;
    margin-bottom: 4px;
}

.empty-state small {
    font-size: 12px;
}

.files-list {
    flex: 1;
    overflow-y: auto;
    padding: 12px;
}

.file-item {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 8px;
    padding: 12px;
    margin-bottom: 10px;
    transition: all 0.2s;
}

.file-item:hover {
    box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}

.file-header {
    display: flex;
    justify-content: space-between;
    align-items: start;
    margin-bottom: 10px;
}

.file-info {
    flex: 1;
}

.file-name {
    font-size: 13px;
    font-weight: 600;
    color: #111827;
    margin-bottom: 4px;
    word-break: break-all;
}

.file-meta {
    display: flex;
    gap: 12px;
    font-size: 11px;
    color: #6b7280;
}

.file-actions {
    display: flex;
    gap: 6px;
}

.icon-btn {
    width: 28px;
    height: 28px;
    display: flex;
    align-items: center;
    justify-content: center;
    border: 1px solid #e5e7eb;
    background: white;
    border-radius: 6px;
    cursor: pointer;
    transition: all 0.2s;
}

.icon-btn:hover {
    background: #f3f4f6;
    border-color: #d1d5db;
}

.icon-btn.delete:hover {
    background: #fee;
    border-color: #fca5a5;
    color: #dc2626;
}

.player {
    display: flex;
    align-items: center;
    gap: 10px;
    background: #f9fafb;
    padding: 8px;
    border-radius: 6px;
}

.play-btn {
    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #10a37f;
    color: white;
    border: none;
    border-radius: 50%;
    cursor: pointer;
    transition: 0.2s;
}

.play-btn:hover {
    background: #0d8c6c;
    transform: scale(1.05);
}

.progress-bar {
    flex: 1;
    height: 4px;
    background: #e5e7eb;
    border-radius: 2px;
    cursor: pointer;
    position: relative;
}

.progress-fill {
    height: 100%;
    background: #10a37f;
    border-radius: 2px;
    transition: width 0.1s;
}

.time {
    font-size: 11px;
    color: #6b7280;
    font-variant-numeric: tabular-nums;
}

::-webkit-scrollbar {
    width: 6px;
}

::-webkit-scrollbar-track {
    background: #f1f1f1;
}

::-webkit-scrollbar-thumb {
    background: #cbd5e1;
    border-radius: 3px;
}

::-webkit-scrollbar-thumb:hover {
    background: #94a3b8;
}
""")

# popup.js - используем предыдущий
with open(plugin_dir / "popup.js", "w", encoding="utf-8") as f:
    f.write("""let currentAudio = null;
let currentPlayingId = null;

document.addEventListener('DOMContentLoaded', async () => {
    await loadFiles();
    await loadSettings();
    setInterval(loadFiles, 2000);
});

async function loadSettings() {
    const result = await chrome.storage.local.get(['autoDownload']);
    const autoDownload = result.autoDownload !== undefined ? result.autoDownload : true;
    document.getElementById('autoDownload').checked = autoDownload;
}

document.getElementById('autoDownload').addEventListener('change', async (e) => {
    await chrome.storage.local.set({ autoDownload: e.target.checked });
});

document.getElementById('clearAll').addEventListener('click', async () => {
    if (confirm('Удалить все записи? (Скачанные файлы останутся на диске)')) {
        await chrome.storage.local.set({ files: [] });
        await loadFiles();
    }
});

async function loadFiles() {
    const result = await chrome.storage.local.get(['files']);
    const files = result.files || [];
    
    document.getElementById('totalFiles').textContent = files.length;
    
    const filesList = document.getElementById('filesList');
    const emptyState = document.getElementById('emptyState');
    
    if (files.length === 0) {
        filesList.style.display = 'none';
        emptyState.style.display = 'flex';
        return;
    }
    
    filesList.style.display = 'block';
    emptyState.style.display = 'none';
    
    filesList.innerHTML = files.map((file, index) => `
        <div class="file-item" data-index="${index}">
            <div class="file-header">
                <div class="file-info">
                    <div class="file-name">${file.filename}</div>
                    <div class="file-meta">
                        <span>📅 ${new Date(file.timestamp).toLocaleString('ru')}</span>
                        <span>💾 ${(file.size / 1024).toFixed(1)} KB</span>
                    </div>
                </div>
                <div class="file-actions">
                    <button class="icon-btn download" data-index="${index}" title="Скачать">
                        <svg width="14" height="14" viewBox="0 0 16 16" fill="currentColor">
                            <path d="M8 12L3 7h3V1h4v6h3l-5 5z"/>
                            <path d="M2 14h12v2H2z"/>
                        </svg>
                    </button>
                    <button class="icon-btn delete" data-index="${index}" title="Удалить">
                        <svg width="14" height="14" viewBox="0 0 16 16" fill="currentColor">
                            <path d="M5.5 5.5A.5.5 0 0 1 6 6v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm2.5 0a.5.5 0 0 1 .5.5v6a.5.5 0 0 1-1 0V6a.5.5 0 0 1 .5-.5zm3 .5a.5.5 0 0 0-1 0v6a.5.5 0 0 0 1 0V6z"/>
                            <path d="M14.5 3a1 1 0 0 1-1 1H13v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V4h-.5a1 1 0 0 1-1-1V2a1 1 0 0 1 1-1H6a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1h3.5a1 1 0 0 1 1 1v1z"/>
                        </svg>
                    </button>
                </div>
            </div>
            
            <div class="player" data-index="${index}">
                <button class="play-btn">
                    <svg width="12" height="12" viewBox="0 0 16 16" fill="currentColor" class="play-icon">
                        <path d="M3 2v12l10-6z"/>
                    </svg>
                    <svg width="12" height="12" viewBox="0 0 16 16" fill="currentColor" class="pause-icon" style="display:none;">
                        <path d="M5 3h2v10H5zm4 0h2v10H9z"/>
                    </svg>
                </button>
                <div class="progress-bar">
                    <div class="progress-fill" style="width: 0%"></div>
                </div>
                <span class="time">0:00</span>
            </div>
        </div>
    `).join('');
    
    attachEventListeners();
}

function attachEventListeners() {
    document.querySelectorAll('.play-btn').forEach(btn => {
        btn.addEventListener('click', handlePlayPause);
    });
    
    document.querySelectorAll('.progress-bar').forEach(bar => {
        bar.addEventListener('click', handleProgressClick);
    });
    
    document.querySelectorAll('.download').forEach(btn => {
        btn.addEventListener('click', handleDownload);
    });
    
    document.querySelectorAll('.delete').forEach(btn => {
        btn.addEventListener('click', handleDelete);
    });
}

async function handlePlayPause(e) {
    const player = e.target.closest('.player');
    const index = player.dataset.index;
    const playIcon = player.querySelector('.play-icon');
    const pauseIcon = player.querySelector('.pause-icon');
    
    if (currentPlayingId === index && currentAudio && !currentAudio.paused) {
        currentAudio.pause();
        playIcon.style.display = 'block';
        pauseIcon.style.display = 'none';
    } else {
        if (currentAudio) {
            currentAudio.pause();
            resetPlayer(currentPlayingId);
        }
        
        const result = await chrome.storage.local.get(['files']);
        const files = result.files || [];
        const file = files[index];
        
        if (!file || !file.blobUrl) {
            alert('Файл не готов. Подождите немного.');
            return;
        }
        
        currentAudio = new Audio(file.blobUrl);
        currentPlayingId = index;
        
        playIcon.style.display = 'none';
        pauseIcon.style.display = 'block';
        
        currentAudio.addEventListener('timeupdate', () => updateProgress(index));
        currentAudio.addEventListener('ended', () => {
            resetPlayer(index);
            currentPlayingId = null;
        });
        
        try {
            await currentAudio.play();
        } catch (err) {
            console.error('Ошибка воспроизведения:', err);
            alert('Не удалось воспроизвести файл.');
            resetPlayer(index);
        }
    }
}

function updateProgress(index) {
    const player = document.querySelector(`[data-index="${index}"] .player`);
    if (!player || !currentAudio) return;
    
    const progress = (currentAudio.currentTime / currentAudio.duration) * 100;
    const progressFill = player.querySelector('.progress-fill');
    const timeDisplay = player.querySelector('.time');
    
    progressFill.style.width = progress + '%';
    timeDisplay.textContent = formatTime(currentAudio.currentTime);
}

function resetPlayer(index) {
    const player = document.querySelector(`[data-index="${index}"] .player`);
    if (!player) return;
    
    const playIcon = player.querySelector('.play-icon');
    const pauseIcon = player.querySelector('.pause-icon');
    const progressFill = player.querySelector('.progress-fill');
    
    playIcon.style.display = 'block';
    pauseIcon.style.display = 'none';
    progressFill.style.width = '0%';
}

function handleProgressClick(e) {
    if (!currentAudio) return;
    
    const bar = e.currentTarget;
    const rect = bar.getBoundingClientRect();
    const percent = (e.clientX - rect.left) / rect.width;
    currentAudio.currentTime = percent * currentAudio.duration;
}

async function handleDownload(e) {
    const index = parseInt(e.currentTarget.dataset.index);
    const result = await chrome.storage.local.get(['files']);
    const files = result.files || [];
    const file = files[index];
    
    if (!file) return;
    
    chrome.runtime.sendMessage({
        action: 'download_file',
        url: file.url,
        filename: file.filename
    });
}

async function handleDelete(e) {
    const index = parseInt(e.currentTarget.dataset.index);
    const result = await chrome.storage.local.get(['files']);
    const files = result.files || [];
    
    if (files[index] && files[index].blobUrl) {
        URL.revokeObjectURL(files[index].blobUrl);
    }
    
    files.splice(index, 1);
    await chrome.storage.local.set({ files });
    await loadFiles();
    
    if (currentPlayingId == index) {
        if (currentAudio) currentAudio.pause();
        currentAudio = null;
        currentPlayingId = null;
    }
}

function formatTime(seconds) {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
}
""")

# interceptor.js - КРИТИЧЕСКИ ВАЖНЫЕ ИЗМЕНЕНИЯ
interceptor_js = """(function() {
  'use strict';
  
  console.log('%c🎤 AAC Interceptor v2.3 LOADED', 'background: #10a37f; color: white; padding: 4px 8px; border-radius: 4px;');
  
  const processedUrls = new Set();
  const originalFetch = window.fetch;
  
  window.fetch = async function(...args) {
    let url = args[0];
    let options = args[1] || {};
    
    // Извлекаем URL
    if (typeof url === 'object') {
      if (url.url) url = url.url;
      else if (url.href) url = url.href;
      else url = String(url);
    }
    
    // КРИТИЧЕСКИ ВАЖНО: проверяем ДО вызова оригинального fetch
    const isAAC = typeof url === 'string' && url.includes('/backend-api/synthesize');
    
    if (isAAC) {
      console.log('%c🎵 AAC DETECTED!', 'background: #22c55e; color: white; padding: 2px 6px; border-radius: 3px;', url.substring(0, 100) + '...');
      
      if (!processedUrls.has(url)) {
        processedUrls.add(url);
        
        // Извлекаем заголовки
        const headers = {};
        if (options.headers) {
          if (options.headers instanceof Headers) {
            for (const [key, value] of options.headers.entries()) {
              headers[key] = value;
            }
          } else if (typeof options.headers === 'object') {
            Object.assign(headers, options.headers);
          }
        }
        
        console.log('%c📨 Sending to background...', 'color: #3b82f6;');
        
        // Отправляем СРАЗУ
        window.postMessage({
          type: 'AAC_DETECTED',
          url: url,
          headers: headers,
          timestamp: Date.now()
        }, '*');
        
        console.log('%c✅ Message sent!', 'color: #22c55e;');
      } else {
        console.log('%c⏭️  Already processed', 'color: #f59e0b;');
      }
    }
    
    // Вызываем оригинальный fetch
    return originalFetch.apply(this, args);
  };
  
  console.log('%c✅ Fetch interceptor ready!', 'color: #22c55e; font-weight: bold;');
  
  // Тестовый лог каждые 5 секунд
  setInterval(() => {
    console.log('%c💚 Interceptor is alive, processed:', 'color: #10a37f;', processedUrls.size, 'files');
  }, 5000);
})();
"""
(plugin_dir / "interceptor.js").write_text(interceptor_js, encoding="utf-8")

# inject.js - КРИТИЧЕСКИ ВАЖНЫЕ ИЗМЕНЕНИЯ
inject_js = """(function() {
  'use strict';
  
  console.log('%c🔧 Inject script starting...', 'background: #3b82f6; color: white; padding: 4px 8px; border-radius: 4px;');
  
  // Инжектируем скрипт КАК МОЖНО РАНЬШЕ
  const script = document.createElement('script');
  script.src = chrome.runtime.getURL('interceptor.js');
  script.type = 'text/javascript';
  
  // Вставляем В САМОЕ НАЧАЛО
  const target = document.documentElement;
  target.insertBefore(script, target.firstChild);
  
  script.onload = () => {
    console.log('%c✅ Interceptor injected!', 'color: #22c55e; font-weight: bold;');
    script.remove();
  };
  
  script.onerror = (err) => {
    console.error('%c❌ Interceptor injection failed!', 'color: #ef4444; font-weight: bold;', err);
  };
  
  // Слушаем сообщения от interceptor
  let messageCount = 0;
  
  window.addEventListener('message', (event) => {
    if (event.source !== window) return;
    
    if (event.data.type === 'AAC_DETECTED') {
      messageCount++;
      console.log('%c📬 Message #' + messageCount + ' received from interceptor', 'background: #8b5cf6; color: white; padding: 2px 6px; border-radius: 3px;');
      console.log('URL:', event.data.url.substring(0, 80) + '...');
      
      // Отправляем в background
      chrome.runtime.sendMessage({
        action: 'aac_detected',
        url: event.data.url,
        headers: event.data.headers,
        timestamp: event.data.timestamp
      }, (response) => {
        if (chrome.runtime.lastError) {
          console.error('%c❌ Failed to send to background:', 'color: #ef4444;', chrome.runtime.lastError);
        } else {
          console.log('%c✅ Sent to background successfully!', 'color: #22c55e;');
        }
      });
    }
  });
  
  console.log('%c👂 Message listener active!', 'color: #22c55e; font-weight: bold;');
})();
"""
(plugin_dir / "inject.js").write_text(inject_js, encoding="utf-8")

# background.js - с детальным логированием
background_js = """console.log('%c🚀 Background v2.3 starting...', 'background: #10a37f; color: white; font-size: 14px; padding: 6px 12px; border-radius: 4px;');

let fileCounter = 0;
const pendingRequests = new Map();

// WebRequest перехват
chrome.webRequest.onBeforeRequest.addListener(
  (details) => {
    const url = details.url;
    
    if (url.includes('/backend-api/synthesize')) {
      console.log('%c🌐 WebRequest intercepted:', 'background: #3b82f6; color: white; padding: 2px 6px;', url.substring(0, 80) + '...');
      
      pendingRequests.set(details.requestId, {
        url: url,
        timestamp: Date.now()
      });
    }
  },
  {
    urls: [
      "https://chatgpt.com/*",
      "https://*.chatgpt.com/*"
    ]
  }
);

chrome.webRequest.onCompleted.addListener(
  async (details) => {
    const requestInfo = pendingRequests.get(details.requestId);
    
    if (requestInfo) {
      console.log('%c✅ WebRequest completed:', 'color: #22c55e;', requestInfo.url.substring(0, 80) + '...');
      
      setTimeout(() => {
        handleAACDetected(requestInfo.url, {}, requestInfo.timestamp);
      }, 1000);
      
      pendingRequests.delete(details.requestId);
    }
  },
  {
    urls: [
      "https://chatgpt.com/*",
      "https://*.chatgpt.com/*"
    ]
  }
);

// Слушаем сообщения от content script
chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  console.log('%c📨 Message received:', 'background: #8b5cf6; color: white; padding: 2px 6px;', msg.action);
  
  if (msg.action === 'aac_detected') {
    console.log('%c🎵 AAC message from content script!', 'color: #22c55e; font-weight: bold;');
    handleAACDetected(msg.url, msg.headers, msg.timestamp);
    sendResponse({ success: true });
  } else if (msg.action === 'download_file') {
    downloadFileManually(msg.url, msg.filename);
    sendResponse({ success: true });
  }
  
  return true; // Keep channel open
});

async function handleAACDetected(url, headers, timestamp) {
  console.log('%c🔄 Processing AAC file...', 'background: #f59e0b; color: white; padding: 4px 8px; border-radius: 4px;');
  console.log('URL:', url);
  
  try {
    const settings = await chrome.storage.local.get(['autoDownload', 'files']);
    const autoDownload = settings.autoDownload !== undefined ? settings.autoDownload : true;
    const files = settings.files || [];
    
    // Проверка дубликатов
    if (files.some(f => f.url === url)) {
      console.log('%c⏭️  File already exists in storage', 'color: #f59e0b;');
      return;
    }
    
    fileCounter++;
    const filename = `chatgpt_voice_${fileCounter}_${Date.now()}.aac`;
    
    console.log('%c⬇️  Downloading file from server...', 'color: #3b82f6;');
    console.log('Filename:', filename);
    
    // Создаём заголовки для fetch
    const fetchHeaders = new Headers();
    
    if (headers && typeof headers === 'object') {
      for (const [key, value] of Object.entries(headers)) {
        if (typeof value === 'string') {
          fetchHeaders.append(key, value);
        }
      }
    }
    
    // Загружаем файл
    const response = await fetch(url, {
      headers: fetchHeaders,
      credentials: 'include',
      mode: 'cors'
    });
    
    console.log('%c📊 Response status:', 'color: #3b82f6;', response.status, response.statusText);
    
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    
    const blob = await response.blob();
    console.log('%c✅ Blob created!', 'color: #22c55e; font-weight: bold;');
    console.log('Size:', (blob.size / 1024).toFixed(2), 'KB');
    console.log('Type:', blob.type);
    
    const blobUrl = URL.createObjectURL(blob);
    console.log('%c🔗 Blob URL:', 'color: #8b5cf6;', blobUrl.substring(0, 60) + '...');
    
    // Добавляем в storage
    files.unshift({
      url: url,
      blobUrl: blobUrl,
      filename: filename,
      timestamp: timestamp || Date.now(),
      size: blob.size
    });
    
    await chrome.storage.local.set({ 
      files: files.slice(0, 50) 
    });
    
    console.log('%c💾 Saved to storage!', 'color: #22c55e;');
    
    // Автоскачивание
    if (autoDownload) {
      console.log('%c📥 Auto-downloading...', 'color: #3b82f6;');
      await downloadBlob(blob, filename);
    } else {
      console.log('%c⏸️  Auto-download disabled', 'color: #f59e0b;');
    }
    
    // Обновляем badge
    chrome.action.setBadgeText({ text: files.length.toString() });
    chrome.action.setBadgeBackgroundColor({ color: '#10a37f' });
    
    console.log('%c🎉 SUCCESSFULLY PROCESSED!', 'background: #22c55e; color: white; font-size: 14px; padding: 6px 12px; border-radius: 4px;');
    
  } catch (err) {
    console.error('%c❌ ERROR:', 'background: #ef4444; color: white; font-size: 14px; padding: 6px 12px; border-radius: 4px;');
    console.error('Error details:', err);
    console.error('Stack:', err.stack);
  }
}

async function downloadBlob(blob, filename) {
  try {
    const blobUrl = URL.createObjectURL(blob);
    const downloadId = await chrome.downloads.download({
      url: blobUrl,
      filename: filename,
      saveAs: false
    });
    
    console.log('%c✅ Download started, ID:', 'color: #22c55e;', downloadId);
    
    // Очистка blob URL с задержкой
    setTimeout(() => {
      URL.revokeObjectURL(blobUrl);
    }, 30000);
    
  } catch (err) {
    console.error('%c❌ Download error:', 'color: #ef4444;', err);
  }
}

async function downloadFileManually(url, filename) {
  try {
    const settings = await chrome.storage.local.get(['files']);
    const files = settings.files || [];
    const file = files.find(f => f.url === url);
    
    if (file && file.blobUrl) {
      await chrome.downloads.download({
        url: file.blobUrl,
        filename: filename,
        saveAs: true
      });
      console.log('%c✅ Manual download:', 'color: #22c55e;', filename);
    } else {
      console.error('%c❌ Blob URL not found', 'color: #ef4444;');
    }
  } catch (err) {
    console.error('%c❌ Manual download error:', 'color: #ef4444;', err);
  }
}

// Инициализация
chrome.storage.local.get(['files'], (result) => {
  const count = (result.files || []).length;
  if (count > 0) {
    chrome.action.setBadgeText({ text: count.toString() });
    chrome.action.setBadgeBackgroundColor({ color: '#10a37f' });
  }
  console.log('%c📊 Initial file count:', 'color: #3b82f6;', count);
});

console.log('%c✅ Background ready!', 'background: #22c55e; color: white; font-size: 14px; padding: 6px 12px; border-radius: 4px;');
console.log('%cWatch this console for detailed logs when audio is generated!', 'color: #6b7280; font-style: italic;');
"""
(plugin_dir / "background.js").write_text(background_js, encoding="utf-8")

# Генерация иконок
def create_microphone_icon(size):
    img = Image.new('RGBA', (size, size), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)

    scale = size / 128

    # Microphone body
    mic_width = int(40 * scale)
    mic_height = int(60 * scale)
    mic_x = (size - mic_width) // 2
    mic_y = int(20 * scale)

    draw.rounded_rectangle(
        [mic_x, mic_y, mic_x + mic_width, mic_y + mic_height],
        radius=int(18 * scale),
        fill=(16, 163, 127, 255)
    )

    # Bottom stick
    stick_w = int(10 * scale)
    stick_h = int(30 * scale)
    stick_x = (size - stick_w) // 2
    stick_y = mic_y + mic_height + int(5 * scale)

    draw.rectangle(
        [stick_x, stick_y, stick_x + stick_w, stick_y + stick_h],
        fill=(16, 163, 127, 255)
    )

    # Base
    base_w = int(50 * scale)
    base_h = int(10 * scale)
    base_x = (size - base_w) // 2
    base_y = stick_y + stick_h + int(5 * scale)

    draw.rounded_rectangle(
        [base_x, base_y, base_x + base_w, base_y + base_h],
        radius=int(6 * scale),
        fill=(16, 163, 127, 255)
    )

    return img

# Generate icons
for size in [16, 48, 128]:
    img = create_microphone_icon(size)
    img.save(plugin_dir / f"icon{size}.png")
