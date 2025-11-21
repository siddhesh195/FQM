{% macro wallpapers(selector, enable_reddit=False, overlay="rgba(0,0,0,0.7)", duration=60) %}
// Macro to set the background wallpapers for a given element via `selector`
$('{{ selector }}').css({
    'background-size': 'cover',
    'background-repeat': 'no-repeat',
    'background-position': 'center',
    'background-attachment': 'fixed',
    'background-color': '#ffffff',   // pure white background
    'background-image': 'none'       // removes image wallpaper
})
{% endmacro %}