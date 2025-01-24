#include <WiFi.h>
#include <ESPAsyncWebServer.h>

// Константы термистора (проверьте соответствие вашему термистору)
const float NOMINAL_RESISTANCE = 900.0;  // Сопротивление термистора при 25°C (900 Ом)
const float NOMINAL_TEMPERATURE = 25.0;  // Номинальная температура (°C)
const float BETA_COEFFICIENT = 3950.0;   // B-коэффициент термистора
const float SERIES_RESISTOR = 10000.0;   // Значение резистора в делителе напряжения

// Пин, к которому подключен термистор
const int THERMISTOR_PIN = 34;  // Пин, к которому подключен термистор (в вашем случае P34)

// Начальная температура в комнате
const float INITIAL_TEMPERATURE = 23.40; 

// Переменная для хранения последней измеренной температуры
float lastTemperature = INITIAL_TEMPERATURE;

// Настройка Wi-Fi
const char* ssid = "YOUR_SSID";  // Замените на ваше имя сети
const char* password = "YOUR_PASSWORD";  // Замените на ваш пароль

// Создаем объект веб-сервера
AsyncWebServer server(80);

void setup() {
  // Инициализация серийного порта и пина термистора
  Serial.begin(115200);
  pinMode(THERMISTOR_PIN, INPUT);

  // Подключение к Wi-Fi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Подключение к Wi-Fi...");
  }
  Serial.println("Подключено к Wi-Fi!");

  // Обработчик для основной страницы, который будет загружать HTML с температурой
  server.on("/", HTTP_GET, [](AsyncWebServerRequest *request){
    String html = "<!DOCTYPE html><html><head><title>Температура</title>";
    html += "<style>body { font-family: Arial, sans-serif; margin: 0; padding: 0; display: flex; justify-content: center; align-items: center; height: 100vh; background-color: #f0f0f0; }";
    html += "h1 { font-size: 100px; }</style></head><body><h1 id='temp'>Загрузка...</h1>";
    html += "<script>function fetchTemperature() {";
    html += "  fetch('/temperature').then(response => response.json()).then(data => {";
    html += "    document.getElementById('temp').innerText = data.temperature.toFixed(2) + ' °C';";
    html += "  });";
    html += "  setTimeout(fetchTemperature, 1000);";
    html += "}</script></body></html>";
    html += "<script>fetchTemperature();</script></html>";
    request->send(200, "text/html", html);
  });

  // Обработчик для получения температуры в формате JSON
  server.on("/temperature", HTTP_GET, [](AsyncWebServerRequest *request){
    int analogValue = analogRead(THERMISTOR_PIN);
    float voltage = analogValue * (3.3 / 4096.0);  // Преобразование в напряжение
    float resistance;
    if (voltage == 3.3) {
      resistance = 1000000; // Если термистор замкнут
    } else {
      resistance = SERIES_RESISTOR * (3.3 / voltage - 1);
    }

    float temperature = -calculateTemperature(resistance) + 2 * INITIAL_TEMPERATURE;
    float temperatureChange = temperature - lastTemperature;
    float currentTemperature = lastTemperature + temperatureChange;
    lastTemperature = currentTemperature;

    String json = "{\"temperature\": " + String(currentTemperature) + "}";
    request->send(200, "application/json", json);
  });

  // Запуск сервера
  server.begin();
}

void loop() {
  // Сервер работает асинхронно, нет необходимости в цикле
}

// Функция для расчета температуры
float calculateTemperature(float resistance) {
  float steinhart;
  steinhart = resistance / NOMINAL_RESISTANCE;     // (R/Ro)
  steinhart = log(steinhart);                      // ln(R/Ro)
  steinhart /= BETA_COEFFICIENT;                   // 1/B * ln(R/Ro)
  steinhart += 1.0 / (NOMINAL_TEMPERATURE + 273.15); // + (1/To)
  steinhart = 1.0 / steinhart;                 // Инвертируем
  steinhart -= 273.15;                         // Преобразуем в °C

  return steinhart;
}
