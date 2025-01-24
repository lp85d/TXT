#include <WiFi.h>
#include <ESPAsyncWebServer.h>

// Настройки Wi-Fi
const char* ssid = "TP-Link_2EC8";
const char* password = "84338839";

// Пин для проверки кабеля
#define PROBE_PIN 23
unsigned long MAX_DISCHARGE_TIME = 5000; // Максимальное время ожидания разрядки
unsigned long THRESHOLD = 6200;          // Порог времени разряда

// Создаем объект веб-сервера
AsyncWebServer server(80);
String logData = "";       // Логи событий
String statusLog = "";     // Логи статусов

// Лимит строк логов
const int MAX_LOG_LINES = 20;

// Таймер для проверки кабеля
unsigned long lastCheck = 0;
const unsigned long CHECK_INTERVAL = 1000; // Check every second

// Функция добавления логов
void addLog(String message, String &logBuffer) {
  String logEntry = "[" + String(millis() / 1000) + "s] " + message + "\n";
  logBuffer = logEntry + logBuffer; // Add new log at the top for correct display order

  // Удаляем старые строки, если они превышают лимит
  int lineCount = 0;
  for (int i = 0; i < logBuffer.length(); i++) {
    if (logBuffer[i] == '\n') lineCount++;
  }
  while (lineCount > MAX_LOG_LINES) {
    int lastNewline = logBuffer.lastIndexOf('\n');
    logBuffer = logBuffer.substring(0, lastNewline);
    lineCount--;
  }
}

// Функция калибровки порога
unsigned long calibrateThreshold() {
  pinMode(PROBE_PIN, OUTPUT);
  digitalWrite(PROBE_PIN, HIGH);
  delayMicroseconds(10);

  pinMode(PROBE_PIN, INPUT);
  unsigned long startTime = micros();
  while (digitalRead(PROBE_PIN) == HIGH) {
    if (micros() - startTime > MAX_DISCHARGE_TIME) break;
  }
  return micros() - startTime;
}

void setup() {
  Serial.begin(115200);
  pinMode(PROBE_PIN, OUTPUT);

  // Подключение к Wi-Fi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Подключение к Wi-Fi...");
  }
  Serial.println("Подключено к Wi-Fi!");
  Serial.print("IP адрес: ");
  Serial.println(WiFi.localIP());

  addLog("Wi-Fi подключен. IP: " + WiFi.localIP().toString(), logData);

  // Главная страница
  server.on("/", HTTP_GET, [](AsyncWebServerRequest *request) {
    String html = "<!DOCTYPE html><html><head><meta charset='UTF-8'><title>Проверка кабеля</title>";
    html += "<style>body { font-family: Arial, sans-serif; background-color: #f8f9fa; margin: 0; padding: 20px; }";
    html += "h1 { color: #343a40; } .container { margin: 10px 0; display: flex; justify-content: space-between; }";
    html += "input, button { font-size: 16px; padding: 10px; margin: 5px; } input[type='range'] { width: 300px; }";
    html += ".log-section { display: flex; justify-content: space-between; margin-top: 20px; }";
    html += ".log-container { width: 48%; max-height: 300px; overflow-y: scroll; border: 1px solid #ccc; padding: 10px; background: #ffffff; }";
    html += "</style></head>";
    html += "<body><h1>Проверка кабеля</h1>";

    // Ползунки и поля ввода
    html += "<div class='container'>";
    html += "<div><label>Порог калибровки: </label>";
    html += "<input type='number' id='thresholdInput' value='" + String(THRESHOLD) + "'>";
    html += "<input type='range' id='thresholdSlider' min='500' max='10000' step='100' value='" + String(THRESHOLD) + "'>";
    html += "<button onclick='updateThreshold()'>Сохранить</button></div>";

    html += "<div><label>Время разрядки: </label>";
    html += "<input type='number' id='dischargeInput' value='" + String(MAX_DISCHARGE_TIME) + "'>";
    html += "<input type='range' id='dischargeSlider' min='1000' max='20000' step='500' value='" + String(MAX_DISCHARGE_TIME) + "'>";
    html += "<button onclick='updateDischargeTime()'>Сохранить</button></div>";
    html += "</div>";

    // Логи
    html += "<div class='log-section'>";
    html += "<div class='log-container'><h2>Логи событий:</h2><pre id='logs'>Загрузка логов...</pre></div>";
    html += "<div class='log-container'><h2>Статус кабеля:</h2><pre id='statusLogs'>Загрузка статуса...</pre></div>";
    html += "</div>";

    // Скрипты
    html += "<script>";
    html += "document.getElementById('thresholdSlider').addEventListener('input', function() {";
    html += "  document.getElementById('thresholdInput').value = this.value; });";
    html += "document.getElementById('thresholdInput').addEventListener('input', function() {";
    html += "  document.getElementById('thresholdSlider').value = this.value; });";
    html += "document.getElementById('dischargeSlider').addEventListener('input', function() {";
    html += "  document.getElementById('dischargeInput').value = this.value; });";
    html += "document.getElementById('dischargeInput').addEventListener('input', function() {";
    html += "  document.getElementById('dischargeSlider').value = this.value; });";
    html += "function updateThreshold() {";
    html += "  let newThreshold = document.getElementById('thresholdInput').value;";
    html += "  fetch('/set_threshold?value=' + newThreshold).then(() => alert('Порог обновлен!'));";
    html += "}";
    html += "function updateDischargeTime() {";
    html += "  let newTime = document.getElementById('dischargeInput').value;";
    html += "  fetch('/set_discharge_time?value=' + newTime).then(() => alert('Время разрядки обновлено!'));";
    html += "}";
    html += "setInterval(() => { fetch('/logs').then(res => res.text()).then(data => { document.getElementById('logs').innerText = data; }); }, 1000);";
    html += "setInterval(() => { fetch('/status_logs').then(res => res.text()).then(data => { document.getElementById('statusLogs').innerText = data; }); }, 1000);";
    html += "</script></body></html>";

    request->send(200, "text/html; charset=UTF-8", html);
  });

  // API для логов
  server.on("/logs", HTTP_GET, [](AsyncWebServerRequest *request) {
    request->send(200, "text/plain; charset=UTF-8", logData);
  });

  // API для логов статусов
  server.on("/status_logs", HTTP_GET, [](AsyncWebServerRequest *request) {
    request->send(200, "text/plain; charset=UTF-8", statusLog);
  });

  // API для изменения порога
  server.on("/set_threshold", HTTP_GET, [](AsyncWebServerRequest *request) {
    if (request->hasParam("value")) {
      THRESHOLD = request->getParam("value")->value().toInt();
      addLog("Порог установлен вручную: " + String(THRESHOLD), logData);
      request->send(200, "text/plain; charset=UTF-8", "Порог обновлен");
    } else {
      request->send(400, "text/plain; charset=UTF-8", "Не указан параметр 'value'");
    }
  });

  // API для изменения времени разрядки
  server.on("/set_discharge_time", HTTP_GET, [](AsyncWebServerRequest *request) {
    if (request->hasParam("value")) {
      MAX_DISCHARGE_TIME = request->getParam("value")->value().toInt();
      addLog("Время разрядки установлено вручную: " + String(MAX_DISCHARGE_TIME), logData);
      request->send(200, "text/plain; charset=UTF-8", "Время разрядки обновлено");
    } else {
      request->send(400, "text/plain; charset=UTF-8", "Не указан параметр 'value'");
    }
  });

  server.begin();
  addLog("Сервер запущен.", logData);
}

void loop() {
  // Проверка кабеля раз в секунду
  if (millis() - lastCheck >= CHECK_INTERVAL) {
    lastCheck = millis(); // Сброс таймера
    
    unsigned long chargeTime = measureCapacitance();
    String status = (chargeTime > THRESHOLD) ? "Yes" : "No";
    Serial.println(status); // Вывод статуса в Serial Monitor
    addLog(status, statusLog);
  }
}

// Функция измерения времени разряда
unsigned long measureCapacitance() {
  pinMode(PROBE_PIN, OUTPUT);
  digitalWrite(PROBE_PIN, HIGH);
  delayMicroseconds(10);

  pinMode(PROBE_PIN, INPUT);
  unsigned long startTime = micros();
  while (digitalRead(PROBE_PIN) == HIGH) {
    if (micros() - startTime > MAX_DISCHARGE_TIME) {
      addLog("Превышено максимальное время разрядки.", logData);
      break;
    }
  }
  unsigned long dischargeTime = micros() - startTime;
  addLog("Время разряда: " + String(dischargeTime) + " мкс.", logData);
  return dischargeTime;
}
