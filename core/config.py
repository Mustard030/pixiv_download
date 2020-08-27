import configparser
import tkinter as tk
import tkinter.filedialog

SETTING_FILE = 'setting.ini'
# 读取配置文件
def read_config(setting_file=SETTING_FILE):
    config = configparser.ConfigParser()
    config.read(setting_file, encoding='UTF-8')
    config_dict = dict()
    try:
        config_dict = dict(config.items('USER'))
    except configparser.NoSectionError:
        print('配置文件损坏或不存在,进行初始化设置')

    download_path = config_dict.get('download_path', '')
    storage_path = config_dict.get('storage_path', '')
    bin_path = config_dict.get('bin_path', '')
    quick_path = config_dict.get('quick_path', '')
    api_key = config_dict.get('api_key', '')

    if download_path:
        print('图片下载路径:', download_path)
    else:
        root = tk.Tk()
        root.withdraw()
        while True:
            print('图片下载路径缺失,请选择文件夹路径!')
            download_path = tkinter.filedialog.askdirectory()
            if not download_path:
                print('此路径为程序运行必须路径，请进行设置')
            else:
                print('图片下载路径:', download_path)
                break

    if storage_path:
        print('图片仓库路径:', storage_path)

    if bin_path:
        print('无法查找的图片路径:', bin_path)
    else:
        root = tk.Tk()
        root.withdraw()
        while True:
            print('图片回收箱路径缺失,请选择文件夹路径!')
            bin_path = tkinter.filedialog.askdirectory()
            if not bin_path:
                print('此路径为搜图功能必须路径，请进行设置')
            else:
                print('无法查找的图片路径:', bin_path)
                break

    if quick_path:
        print('快速搜索图片路径:', quick_path)

    if api_key:
        print('API_KEY:', api_key)

    write_config(setting_file, download_path=download_path,
                 storage_path=storage_path, bin_path=bin_path,
                 quick_path=quick_path, api_key=api_key)
    return download_path, storage_path, bin_path, quick_path, api_key


# 写入配置文件
def write_config(setting_file=SETTING_FILE, **kwargs):
    config = configparser.ConfigParser()
    config.read(setting_file, encoding='UTF-8')
    if not config.has_section('USER'):
        config.add_section('USER')
    config.set('DEFAULT', 'API_KEY', '')

    for key in kwargs:
        config.set('USER', key, kwargs.get(key, ''))
    # config.set('USER', 'DOWNLOAD_ROOT_PATH', kwargs.get('download_path', ''))
    # config.set('USER', 'SAVE_ROOT_PATH', kwargs.get('save_root_path', ''))
    # config.set('USER', 'BIN_PATH', kwargs.get('bin_path', ''))
    # config.set('USER', 'CACHE_PATH', kwargs.get('cache_path', ''))
    # config.set('USER', 'API_KEY', kwargs.get('api_key', ''))

    with open(setting_file, 'w', encoding='UTF-8') as setting_file:  # 写入配置文件
        config.write(setting_file)
