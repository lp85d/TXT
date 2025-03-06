const express = require('express');
const multer = require('multer');
const fs = require('fs');
const path = require('path');

const app = express();
const upload = multer({ dest: 'uploads/' });

app.post('/upload-file', upload.single('file'), (req, res) => {
  if (!req.file) {
    console.error("Файл не был загружен.");
    return res.status(400).json({ success: false, message: "Файл не был загружен." });
  }

  // Путь для сохранения файла на рабочем столе удаленной машины
  const destinationPath = '/root/Desktop/' + req.file.originalname;

  console.log(`Получен файл: ${req.file.originalname}`);
  console.log(`Размер: ${req.file.size} байт`);
  console.log(`Тип MIME: ${req.file.mimetype}`);
  console.log(`Временный путь: ${req.file.path}`);
  console.log(`Файл будет сохранен в: ${destinationPath}`);

  // Перемещение файла в нужное место
  fs.rename(req.file.path, destinationPath, (err) => {
    if (err) {
      console.error("Ошибка перемещения файла:", err);
      return res.status(500).json({ success: false, message: "Не удалось сохранить файл." });
    }
    console.log("Файл успешно загружен на сервер.");
    res.json({
      success: true,
      message: "Файл успешно загружен на сервер.",
      fileName: req.file.originalname,
      fileSize: req.file.size,
      fileType: req.file.mimetype,
      destination: destinationPath
    });
  });
});

app.listen(3000, () => {
  console.log('Server running on port 3000');
});
