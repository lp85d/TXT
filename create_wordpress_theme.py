import os

# Путь к папке темы
base_path = r"E:\OSPanel\home\dkscapital.ru\wp-content\themes\custom-theme"

# Структура папок
folders = [
    "css",
    "js",
    "images"
]

# Файлы и их содержимое
files = {
    "style.css": """/*
Theme Name: Custom Theme
Author: Ваше Имя
Description: Уникальная тема, основанная на дизайне dkscapital.ru
Version: 1.0
*/
body {
    font-family: Arial, sans-serif;
    color: #333;
    background-color: #fff;
}
""",
    "header.php": """<!DOCTYPE html>
<html <?php language_attributes(); ?>>
<head>
    <meta charset="<?php bloginfo('charset'); ?>">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <?php wp_head(); ?>
</head>
<body <?php body_class(); ?>>
    <header>
        <div class="container">
            <div class="logo">
                <a href="<?php echo home_url(); ?>">
                    <img src="<?php echo get_template_directory_uri(); ?>/images/logo.png" alt="Логотип">
                </a>
            </div>
            <nav>
                <?php wp_nav_menu(array(
                    'theme_location' => 'header-menu',
                    'container' => false,
                    'menu_class' => 'nav'
                )); ?>
            </nav>
        </div>
    </header>
""",
    "footer.php": """<footer>
    <div class="container">
        <p>&copy; <?php echo date('Y'); ?> <?php bloginfo('name'); ?></p>
        <nav>
            <?php wp_nav_menu(array(
                'theme_location' => 'footer-menu',
                'container' => false,
                'menu_class' => 'footer-nav'
            )); ?>
        </nav>
    </div>
</footer>
<?php wp_footer(); ?>
</body>
</html>
""",
    "functions.php": """<?php
function custom_theme_enqueue_styles() {
    wp_enqueue_style("main-style", get_stylesheet_uri());
    wp_enqueue_style("bootstrap", get_template_directory_uri() . "/css/bootstrap.min.css");
    wp_enqueue_script("bootstrap-js", get_template_directory_uri() . "/js/bootstrap.bundle.min.js", array("jquery"), null, true);
}
add_action("wp_enqueue_scripts", "custom_theme_enqueue_styles");

function register_my_menus() {
    register_nav_menus(array(
        "header-menu" => __("Header Menu"),
        "footer-menu" => __("Footer Menu")
    ));
}
add_action("init", "register_my_menus");
?>
""",
    "index.php": """<?php
get_header();
if (have_posts()) :
    while (have_posts()) : the_post();
        the_content();
    endwhile;
else :
    echo "<p>Записей нет.</p>";
endif;
get_footer();
?>
"""
}

# Создание структуры папок
os.makedirs(base_path, exist_ok=True)
for folder in folders:
    os.makedirs(os.path.join(base_path, folder), exist_ok=True)

# Создание файлов
for file_name, content in files.items():
    file_path = os.path.join(base_path, file_name)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(content)

print("Все файлы и папки успешно созданы!")
