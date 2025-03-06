const express = require('express');
const multer = require('multer');
const fs = require('fs');
const path = require('path');

const app = express();
const upload = multer({ dest: 'uploads/' });

app.post('/upload-file', upload.single('file'), (req, res) => {
  if (!req.file) {
    return res.status(400).json({ success: false, message: "Файл не был загружен." });
  }

  // Путь для сохранения файла на рабочем столе удаленной машины
  const destinationPath = '/root/Desktop/' + req.file.originalname;

  // Перемещение файла в нужное место
  fs.rename(req.file.path, destinationPath, (err) => {
    if (err) {
      return res.status(500).json({ success: false, message: "Не удалось сохранить файл." });
    }
    res.json({ success: true, message: "Файл успешно загружен на сервер." });
  });
});

app.listen(3000, () => {
  console.log('Server running on port 3000');
});