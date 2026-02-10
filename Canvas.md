```markdown
# 🧩 Скрипт для редактируемого водяного знака на Canvas

## Описание

Этот скрипт предназначен для **графической настройки позиции и размера водяного знака** внутри элемента `.p-chart canvas` на веб‑странице.  
Он создаёт интерактивный прямоугольник, который можно:
- перемещать мышкой;
- растягивать за края;
- после настройки нажать кнопку **"Скопировать код"**, которая сгенерирует и скопирует в буфер обновлённый JavaScript‑код с актуальными координатами и размерами водяного знака.

Это полезно для визуального позиционирования элементов на канвасе без ручного подбора чисел.

---

## 🚀 Как использовать

1. **Откройте сайт**, где есть элемент с классом `.p-chart` и вложенный `<canvas>`.  
   Например: (https://github.com/lp85d/TXT/blob/main/Canvas.html)
   ```html
   <div class="p-chart">
     <canvas></canvas>
   </div>
   ```

2. **Откройте консоль браузера:**
   - Нажмите **F12** или **Ctrl + Shift + I** (для Windows / Linux),
   - Либо **Option + ⌘ + I** (на macOS).

3. Перейдите на вкладку **Console** и вставьте весь приведённый ниже код, затем нажмите **Enter**.

4. На холсте появится **прямоугольник**:
   - Тяните его мышкой, чтобы задать позицию;
   - Тяните за границы/углы, чтобы изменить размер.

5. После любого движения появится кнопка **"Скопировать код"** в правом верхнем углу экрана.

6. Нажмите **кнопку — и ваш вариант функции будет скопирован в буфер обмена** с точными параметрами:
   - `wx`, `wy`, `wWidth`, `wHeight` — учитывают реальное положение и размеры прямоугольника относительно `canvas`.

7. Вставьте скопированный код в свой проект — теперь водяной знак будет находиться точно там, где вы его настроили.

---

## 💻 Полный код для вставки в консоль

```js
(function() {
  const container = document.querySelector(".p-chart");
  const canvas = container?.querySelector("canvas");

  if (!canvas) {
    alert("❌ Canvas не найден (.p-chart canvas)");
    return;
  }

  // === Создаём draggable + resizable прямоугольник ===
  const box = document.createElement("div");
  const btn = document.createElement("button");

  Object.assign(box.style, {
    position: "absolute",
    left: "70%",
    top: "20%",
    width: "80px",
    height: "50px",
    background: "rgba(252,252,253,0.9)",
    border: "2px solid #007bff",
    cursor: "move",
    resize: "both",
    overflow: "auto",
    zIndex: 999999
  });

  Object.assign(btn.style, {
    position: "fixed",
    top: "10px",
    right: "10px",
    padding: "6px 10px",
    fontSize: "14px",
    background: "#007bff",
    color: "#fff",
    border: "none",
    borderRadius: "4px",
    cursor: "pointer",
    zIndex: 999999,
    display: "none"
  });

  btn.textContent = "Скопировать код";
  container.style.position = "relative";
  container.appendChild(box);
  document.body.appendChild(btn);

  // === Логика перетаскивания ===
  let isDragging = false, offsetX = 0, offsetY = 0;

  box.addEventListener("mousedown", e => {
    if (e.target !== box) return;
    isDragging = true;
    offsetX = e.clientX - box.offsetLeft;
    offsetY = e.clientY - box.offsetTop;
  });

  document.addEventListener("mousemove", e => {
    if (!isDragging) return;
    const rect = container.getBoundingClientRect();
    const newLeft = e.clientX - rect.left - offsetX;
    const newTop = e.clientY - rect.top - offsetY;

    box.style.left = `${Math.max(0, Math.min(rect.width - box.offsetWidth, newLeft))}px`;
    box.style.top = `${Math.max(0, Math.min(rect.height - box.offsetHeight, newTop))}px`;
    btn.style.display = "block";
  });

  document.addEventListener("mouseup", () => isDragging = false);

  // === Копирование ===
  btn.addEventListener("click", () => {
    const rect = box.getBoundingClientRect();
    const canvasRect = canvas.getBoundingClientRect();

    // Координаты относительно canvas
    const wx = (rect.left - canvasRect.left).toFixed(0);
    const wy = (rect.top - canvasRect.top).toFixed(0);
    const wWidth = rect.width.toFixed(0);
    const wHeight = rect.height.toFixed(0);

    const code = `(function hideWatermarkPermanently() {
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", hideWatermarkPermanently);
    return;
  }

  const container = document.querySelector(".p-chart");
  if (!container) return;

  const canvas = container.querySelector("canvas");
  if (!canvas) return;

  function applyWatermarkFix() {
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    const { width, height } = canvas;

    // ✅ ЛЕВАЯ полоска
    const leftX = 5;
    const leftY = 30;
    const leftWidth = 8;
    const leftHeight = height * 0.7;

    // ✅ ПРАВАЯ полоска
    const rightX = width - 5;
    const rightY = 5;
    const rightWidth = 8;
    const rightHeight = height * 0.7;

    // ✅ Водяной знак
    const wx = ${wx};
    const wy = ${wy};
    const wWidth = ${wWidth};
    const wHeight = ${wHeight};

    ctx.save();
    ctx.fillStyle = "#FCFCFD";
    ctx.fillRect(leftX, leftY, leftWidth, leftHeight);
    ctx.fillRect(rightX, rightY, rightWidth, rightHeight);
    ctx.fillRect(wx, wy, wWidth, wHeight);
    ctx.restore();

    const newDataUrl = canvas.toDataURL("image/png");
    canvas.style.backgroundImage = \`url(\${newDataUrl}) !important\`;
    canvas.style.backgroundSize = "100% 100% !important";
  }

  applyWatermarkFix();
  const observer = new MutationObserver(applyWatermarkFix);
  observer.observe(container, { attributes: true, childList: true, subtree: true });
  setInterval(applyWatermarkFix, 1000);
})();`;

    navigator.clipboard.writeText(code)
      .then(() => alert("✅ Точный код скопирован — позиция и размер учтены!"))
      .catch(err => alert("Ошибка копирования: " + err.message));
  });
})();
```

---

## 🔍 Что делает каждая часть

| Блок кода | Назначение |
|------------|------------|
| `document.querySelector(".p-chart canvas")` | Ищет холст, внутри которого будет позиционироваться прямоугольник |
| `box` | Визуальный элемент-«водяной знак», который можно двигать и растягивать |
| `btn` | Кнопка "Скопировать код" |
| Mouse/resize обработчики | Отслеживают перемещение и размер для интерактивного редактирования |
| `navigator.clipboard.writeText()` | Копирует готовый код в буфер обмена |
| `wx`, `wy`, `wWidth`, `wHeight` | Точные координаты и размеры внутри канваса (в пикселях) |

---

## ⚙️ Примечания

- Прямоугольник выводится **внутри** контейнера `.p-chart`, а кнопка “Скопировать код” **зафиксирована на экране**.  
- Скрипт ничего не ломает в DOM — после перезагрузки страницы всё исчезает.  
- Работает в Chrome, Firefox, Edge, Safari (современные версии).  

---

## 🧠 Идея проекта

Инструмент создан для разработчиков, работающих с canvas‑графикой, которым важно **визуально подобрать координаты водяных знаков и вспомогательных элементов**, чтобы потом использовать их в коде без ручного подбора пикселей.

---

```

***
