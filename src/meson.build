python = import('python').find_installation('python3')

python.install_sources(
  'quran_reader/__init__.py',
  'quran_reader/constants.py',
  'quran_reader/db.py',
  'quran_reader/window.py',
  subdir: 'quran_reader',
)

configure_file(
  input:        'quran-reader.in',
  output:       'quran-reader',
  configuration: {'PYTHON': python.full_path()},
  install:      true,
  install_dir:  get_option('bindir'),
  install_mode: 'rwxr-xr-x',
)
