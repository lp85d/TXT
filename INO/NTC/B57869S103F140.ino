#include <Arduino.h>

// Константы термистора (проверьте соответствие вашему термистору)
const float NOMINAL_RESISTANCE = 900.0;  // Сопротивление термистора при 25°C (900 Ом)
const float NOMINAL_TEMPERATURE = 25.0;  // Номинальная температура (°C)
const float BETA_COEFFICIENT = 3950.0;   // B-коэффициент термистора
const float SERIES_RESISTOR = 10000.0; // Значение резистора в делителе напряжения

// Пин, к которому подключен термистор
const int THERMISTOR_PIN = 34;  // Пин, к которому подключен термистор (в вашем случае P34)

// Начальная температура в комнате
const float INITIAL_TEMPERATURE = 23.40; 

// Переменная для хранения последней измеренной температуры
float lastTemperature = INITIAL_TEMPERATURE;

void setup() {
  Serial.begin(115200);
  pinMode(THERMISTOR_PIN, INPUT);
}

void loop() {
  // Чтение аналогового значения с пина
  int analogValue = analogRead(THERMISTOR_PIN);

  // Преобразуем значение в напряжение
  float voltage = analogValue * (3.3 / 4096.0);  // Преобразование в напряжение, учитывая 12-битный АЦП

  // Рассчитываем сопротивление термистора
  float resistance;
  if (voltage == 3.3) { // Если термистор замкнут, сопротивление бесконечно большое
    resistance = 1000000; // Большое значение, чтобы избежать деления на ноль
  } else {
    resistance = SERIES_RESISTOR * (3.3 / voltage - 1); // Исправленная формула для делителя напряжения
  }

  // Расчет температуры по инвертированной формуле Steinhart-Hart
  float temperature = -calculateTemperature(resistance) + 2 * INITIAL_TEMPERATURE; // Инвертируем результат и корректируем

  // Вычисляем изменение температуры относительно последнего измерения
  float temperatureChange = temperature - lastTemperature;
  
  // Обновляем температуру, добавляя изменение к последнему значению
  float currentTemperature = lastTemperature + temperatureChange;

  // Обновляем lastTemperature для следующего измерения
  lastTemperature = currentTemperature;

  // Выводим результаты в монитор порта
  Serial.print("Аналоговое значение: ");
  Serial.print(analogValue);
  Serial.print("\tНапряжение: ");
  Serial.print(voltage, 3);
  Serial.print(" В\tСопротивление термистора: ");
  Serial.print(resistance, 2);
  Serial.print(" Ом\tТемпература: ");
  Serial.print(currentTemperature, 2); // Выводим текущую температуру
  Serial.println(" °C");

  delay(1000);  // Задержка 1 секунда
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
