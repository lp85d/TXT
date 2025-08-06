apt update && apt install -y apache2 mariadb-server php php-mysql php-curl php-gd php-mbstring php-xml php-xmlrpc unzip
systemctl enable apache2 mariadb
mysql -e "CREATE DATABASE wordpress; CREATE USER 'wp_user'@'localhost' IDENTIFIED BY 'strongpassword'; GRANT ALL ON wordpress.* TO 'wp_user'@'localhost'; FLUSH PRIVILEGES;"
wget https://wordpress.org/latest.zip
unzip latest.zip -d /var/www/html/
chown -R www-data:www-data /var/www/html/wordpress
chmod -R 755 /var/www/html/wordpress
echo "<VirtualHost *:80>
    DocumentRoot /var/www/html/wordpress
    <Directory /var/www/html/wordpress>
        AllowOverride All
    </Directory>
</VirtualHost>" > /etc/apache2/sites-available/wordpress.conf
a2enmod rewrite
a2ensite wordpress.conf
systemctl restart apache2
rm latest.zip
