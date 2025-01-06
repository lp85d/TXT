@echo off
setlocal enabledelayedexpansion

:: Путь к папке сайта
set SITE_PATH=E:\OSPanel\home\dkscapital.ru\wp-content\themes\custom-theme

:: Создание структуры папок
echo Создаю структуру папок...
mkdir "%SITE_PATH%"
mkdir "%SITE_PATH%\css"
mkdir "%SITE_PATH%\js"
mkdir "%SITE_PATH%\images"

:: Создание файла style.css
echo Создаю файл style.css...
(
echo /*
echo Theme Name: Custom Theme
echo Author: Ваше Имя
echo Description: Уникальная тема, основанная на дизайне dkscapital.ru
echo Version: 1.0
echo */
echo body {
echo     font-family: Arial, sans-serif;
echo     color: #333;
echo     background-color: #fff;
echo }
) > "%SITE_PATH%\style.css"

:: Создание файла header.php
echo Создаю файл header.php...
(
echo ^<!DOCTYPE html^>
echo ^<html ^<?php language_attributes(); ^?>^>
echo ^<head^>
echo     ^<meta charset=^"<?php bloginfo('charset'); ^?>^">
echo     ^<meta name=^"viewport^" content=^"width=device-width, initial-scale=1.0^">
echo     ^<?php wp_head(); ^?>
echo ^</head^>
echo ^<body ^<?php body_class(); ^?>^>
echo     ^<header^>
echo         ^<div class="container"^>
echo             ^<div class="logo"^>
echo                 ^<a href=^"<?php echo home_url(); ^?>"^>
echo                     ^<img src=^"<?php echo get_template_directory_uri(); ?>/images/logo.png^" alt="Логотип"^>
echo                 ^</a^>
echo             ^</div^>
echo             ^<nav^>
echo                 ^<?php wp_nav_menu(array(^
echo                     'theme_location' => 'header-menu',
echo                     'container' => false,
echo                     'menu_class' => 'nav'
echo                 ^)); ^?>
echo             ^</nav^>
echo         ^</div^>
echo     ^</header^>
) > "%SITE_PATH%\header.php"

:: Создание файла footer.php
echo Создаю файл footer.php...
(
echo ^<footer^>
echo     ^<div class="container"^>
echo         ^<p>&copy; ^<?php echo date('Y'); ^?> ^<?php bloginfo('name'); ^?></p^>
echo         ^<nav^>
echo             ^<?php wp_nav_menu(array(^
echo                 'theme_location' => 'footer-menu',
echo                 'container' => false,
echo                 'menu_class' => 'footer-nav'
echo             ^)); ^?>
echo         ^</nav^>
echo     ^</div^>
echo ^</footer^>
echo ^<?php wp_footer(); ^?>
echo ^</body^>
echo ^</html^>
) > "%SITE_PATH%\footer.php"

:: Создание файла functions.php
echo Создаю файл functions.php...
(
echo ^<?php
echo function custom_theme_enqueue_styles() {
echo     wp_enqueue_style('main-style', get_stylesheet_uri());
echo     wp_enqueue_style('bootstrap', get_template_directory_uri() . '/css/bootstrap.min.css');
echo     wp_enqueue_script('bootstrap-js', get_template_directory_uri() . '/js/bootstrap.bundle.min.js', array('jquery'), null, true);
echo }
echo add_action('wp_enqueue_scripts', 'custom_theme_enqueue_styles');
echo
echo function register_my_menus() {
echo     register_nav_menus(array(
echo         'header-menu' => __('Header Menu'),
echo         'footer-menu' => __('Footer Menu')
echo     ));
echo }
echo add_action('init', 'register_my_menus');
echo ^?>
) > "%SITE_PATH%\functions.php"

:: Создание файла index.php
echo Создаю файл index.php...
(
echo ^<?php
echo get_header();
echo if (have_posts()) :
echo     while (have_posts()) : the_post();
echo         the_content();
echo     endwhile;
echo else :
echo     echo '<p>Записей нет.</p>';
echo endif;
echo get_footer();
echo ^?>
) > "%SITE_PATH%\index.php"

echo Все файлы успешно созданы в %SITE_PATH%.
pause
