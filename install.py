from install_packages import check_and_install_packages, check_torch_cuda
check_and_install_packages([
    {'module_name': 'keyboard',    'install_name': 'keyboard'},
    {'module_name': 'pyperclip',   'install_name': 'pyperclip'},
    {'module_name': 'trafilatura', 'install_name': 'trafilatura'},
    {'module_name': 'langdetect',  'install_name': 'langdetect'},
    {'module_name': 'RealtimeTTS', 'install_name': 'RealtimeTTS[edge,kokoro,jp,zh]'},
    {'module_name': 'pyautogui',   'install_name': 'pyautogui'},
    {'module_name': 'requests',    'install_name': 'requests'},
    {'module_name': 'bs4',         'install_name': 'beautifulsoup4'},
    {'module_name': 'newspaper',   'install_name': 'newspaper3k'},
    {'module_name': 'readability', 'install_name': 'readability-lxml'},
    {'module_name': 'pythoncom',   'install_name': 'pywin32'},
    {'module_name': 'pywinauto',   'install_name': 'pywinauto'},
])

check_torch_cuda()