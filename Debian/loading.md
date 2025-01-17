![image](https://github.com/user-attachments/assets/3898d107-fea4-43d0-9b84-2760e419adc7)

# Временная загрузка Linux без графического интерфейса  

Если вы хотите загрузить систему в текстовом режиме, то добавление systemd.unit=multi-user.target корректно.

# Способ применения:  

Эта строка должна быть временным параметром загрузки, если вы изменяете параметры непосредственно в меню GRUB.  
Если хотите сделать изменения постоянными, нужно редактировать файл конфигурации GRUB:  

  sudo nano /etc/default/grub  
  
В строке GRUB_CMDLINE_LINUX добавьте:  

  GRUB_CMDLINE_LINUX="systemd.unit=multi-user.target"  
После этого обновите конфигурацию GRUB:  

  sudo update-grub  
Дополнительно:  
Если вы просто хотите переключиться в текстовый режим, без редактирования GRUB, выполните:  

  sudo systemctl set-default multi-user.target  
Чтобы вернуться к графическому интерфейсу, выполните:   

  sudo systemctl set-default graphical.target  
