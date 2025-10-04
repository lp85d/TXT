Чтобы собрать твой `Program.cs` в готовый **exe**:

---

### 1. Создаём новый проект

```bat
dotnet new console -n MyApp
cd MyApp
```

### 2. Кладём туда твой `Program.cs`

```bat
move /Y "C:\Users\user\Downloads\Program.cs" .
```

### 3. Подключаем библиотеку dnlib

```bat
dotnet add package dnlib
```

### 4. Проверяем запуск

```bat
dotnet run
```

(здесь программа уже отработала и создала `Laitis_clean.exe`)

---

### 5. Компиляция в exe (обычный вариант)

```bat
dotnet publish -c Release -r win-x64 --self-contained true
```

👉 результат лежит в:

```
bin\Release\net9.0\win-x64\publish\MyApp.exe
```

---

### 6. Компиляция в **один файл**

```bat
dotnet publish -c Release -r win-x64 -p:PublishSingleFile=true --self-contained true
```

👉 получаешь **один exe** (но размер будет больше, ~70–100 МБ, т.к. весь рантайм .NET зашит внутрь).

---

### 7. Если хочешь ещё уменьшить размер

```bat
dotnet publish -c Release -r win-x64 -p:PublishSingleFile=true -p:PublishTrimmed=true --self-contained true
```

⚠️ Здесь возможны предупреждения (как у тебя про dnlib), потому что trim иногда вырезает "лишние" методы. Обычно это не критично, exe запускается нормально.

---

✅ В итоге тебе достаточно помнить **три ключевые команды**:

1. `dotnet add package dnlib` — подключить библиотеку.
2. `dotnet run` — проверить, что всё работает.
3. `dotnet publish -c Release -r win-x64 -p:PublishSingleFile=true --self-contained true` — собрать один exe.

---
