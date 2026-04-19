project(
  'quran-reader',
  version: '0.1.0',
  meson_version: '>= 0.62.0',
)

python  = import('python').find_installation('python3')
gnome   = import('gnome')

subdir('data')
subdir('src')

gnome.post_install(
  gtk_update_icon_cache:   true,
  update_desktop_database: true,
)
