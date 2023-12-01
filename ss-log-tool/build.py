import PyInstaller.__main__
import os

dll_path = os.path.join(os.path.abspath(os.path.curdir), "dll")
dlls = ""

add_data = []
for file in os.listdir(dll_path):
    abs_file = os.path.join(dll_path, file)
    add_data.append('--add-data')
    add_data.append(abs_file + ";.")

options = [
    'ss-log-tool.py',
    '--onefile',
    #'--windowed',  dont use this option
    '-p',
    dll_path,
    '-n',
    'ss-log-debug.exe',
    '--upx-exclude',
    os.path.join(os.path.abspath(os.path.curdir), "upx", "upx.exe")
]
options.extend(add_data)
print("options: \n" + str(options))
PyInstaller.__main__.run(options)

