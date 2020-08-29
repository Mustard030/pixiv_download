import time
from .config import *
from .utils import *
from threading import *
from queue import Queue
from .search_picture import *
import logging

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s-%(levelname)s:%(message)s')

__version__ = '2.1'


class Download(object):

    def __init__(self):
        self.open_flag = False
        self.download_path, \
        self.storage_path, \
        self.bin_path, \
        self.quick_path, \
        self.api_key = read_config()
        self.input_queue = Queue()
        self.search_queue = Queue()  # 接收文件路径，上传到saucenao.com获取图片发布链接
        self.download_queue = Queue()  # 接收图片链接获得二进制内容和文件名，放置到save_queue中
        self.save_queue = Queue()  # 接收二进制内容和文件名进行保存
        self.open_queue = Queue()  # file path
        self._set_lock = RLock()

    # 切换自动打开
    def switch_open(self):
        with self._set_lock:
            self.open_flag = not self.open_flag
            logging.info(f'自动打开: {self.open_flag}')

    # 切换是否使用配额
    def switch_key(self):
        with self._set_lock:
            if not self.api_key:
                i_config = configparser.ConfigParser()
                i_config.read(SETTING_FILE, encoding='UTF-8')
                config_dict = dict(i_config.items('USER'))
                self.api_key = config_dict.get('api_key', '')
                if not self.api_key:
                    logging.error('你没有API KEY，请先设定API KEY再使用切换功能')
                else:
                    logging.info(f'切换至API KEY: {self.api_key}')
            else:
                self.api_key = ''
                logging.info('切换至不使用API KEY配额模式')

    # 设置 saucenao.com 的 API_KEY
    def reset_key(self):
        with self._set_lock:
            self.api_key = input("输入你的 saucenao.com API_KEY:")
            self.api_key = self.api_key.replace(' ', '')
            write_config(api_key=self.api_key)

    # 更换快速搜图路径
    def reset_quick_path(self):
        with self._set_lock:
            root = tk.Tk()
            # root.withdraw()
            self.quick_path = tkinter.filedialog.askdirectory(title='快速搜索路径:')
            root.destroy()
            if self.quick_path:
                logging.info(f'快速搜索路径: {self.quick_path}')
                write_config(cache_path=self.quick_path)
            else:
                logging.info('取消选择快速搜索路径')

    # 更换图片仓库路径
    def reset_hub(self):
        with self._set_lock:
            root = tk.Tk()
            # root.withdraw()
            self.storage_path = tkinter.filedialog.askdirectory(title='图片仓库路径:')
            root.destroy()
            if self.storage_path:
                logging.info(f'图片仓库路径: {self.storage_path}')
                write_config(storage_path=self.storage_path)
            else:
                logging.info('取消选择图片仓库路径')

    # 更换下载路径
    def reset_download(self):
        with self._set_lock:
            root = tk.Tk()
            # root.withdraw()
            while True:
                self.download_path = tkinter.filedialog.askdirectory(title='下载路径:')
                if self.download_path:
                    logging.info(f'下载路径: {self.download_path}')
                    write_config(download_path=self.download_path)
                    root.destroy()
                    break
                else:
                    logging.info('此路径为程序运行必须路径，请进行设置')

    # 更换垃圾箱路径
    def reset_bin(self):
        with self._set_lock:
            root = tk.Tk()
            # root.withdraw()
            while True:
                self.bin_path = tkinter.filedialog.askdirectory(title='垃圾箱路径:')
                if self.bin_path:
                    logging.info(f'垃圾箱路径: {self.bin_path}')
                    write_config(bin_path=self.bin_path)
                    root.destroy()
                    break
                else:
                    logging.info('此路径为程序运行必须路径，请进行设置')

    # 启动快速搜图
    def quick_search(self):
        with self._set_lock:
            if self.quick_path:
                self.input_queue.put(self.quick_path)
            else:
                logging.error('快速搜索图片路径缺失,请选择文件夹路径!')
                self.reset_quick_path()

    # 获取用户输入
    def user_input(self):
        switch = {
            'help': helper,
            '?': helper,
            '？': helper,
            '#': self.switch_open,
            'open': self.switch_open,
            '@': self.switch_key,
            '!': self.quick_search,
            '！': self.quick_search,
            'download': self.reset_download,
            'hub': self.reset_hub,
            'key': self.reset_key,
            'quick': self.reset_quick_path,
            'bin': self.reset_bin
        }
        while True:
            input_str = input('>>>')
            pic_num_list = format_input_str(input_str)

            for pic_num in pic_num_list:
                if cmd := switch.get(pic_num, ''):
                    cmd()
                elif re.search(r'[a-zA-z]+://[^\s]*', pic_num):  # 网址格式
                    if 'pixiv' in pic_num and ('illust' in pic_num or 'artworks' in pic_num):
                        pixiv_id = get_pixiv_url(pic_num)
                        if path := self.is_exist(pixiv_id):
                            logging.info(f'{pixiv_id} 已存在')
                            if self.open_flag:
                                self.open_queue.put(path)
                        elif path is None:
                            self.download_queue.put((pixiv_id, 'pixiv', False, None))
                            logging.info(f'{pixiv_id} 已添加到下载队列')
                    elif 'twitter' in pic_num:
                        logging.info('抱歉，暂不支持此链接')
                        # fuck twitter api
                        # twitter_urls = get_twitter_url(pic_num)
                        # for url in twitter_urls:
                        #     self.download_queue.put((url, 'twitter'))
                    else:
                        logging.info(f'无法识别的链接: {pic_num}')
                else:
                    self.input_queue.put(pic_num)
                    # path or file or xxx-x#

    # 文件存在检查 忽略 #
    # xxx.jpg/.png folder_list -> real_folder\xxx.jpg
    def is_exist(self, input_str: str):
        # input_str maybe whole_file_path or xxx-x
        if os.path.isfile(input_str):
            filename = os.path.basename(input_str)
            return get_real_path(filename, [self.download_path, self.storage_path])
        else:  # is xxx-x or xxx
            input_str = input_str.replace('#', '')
            pid = to_pid(input_str)  # return XXX_pX.png
            return get_real_path(pid, [self.download_path, self.storage_path])

    # 识别输入内容
    # 区分文件夹或文件或ID
    def get_folder_or_file_or_pid(self):
        while True:
            input_str = self.input_queue.get()
            # input_str maybe path or file or xxx-x(#)

            if os.path.isfile(input_str):  # most of situation
                if pid := useful_name(input_str):
                    # pid from xxx.jpg or xxx_px.jpg  ->  xxx-x
                    logging.info(f'识别到{pid}')
                    if exist_path := self.is_exist(input_str):
                        if self.open_flag:  # open
                            self.open_queue.put(exist_path)
                        # exist
                        logging.info(f'{pid} 已存在,将被移除')
                        os.remove(input_str)
                    else:  # is xxx-x but not exist
                        self.download_queue.put((pid, 'pixiv', False, input_str))
                        # logging.info(f'已移除{input_str}')
                    # os.remove(input_str)
                else:
                    self.search_queue.put(input_str)
            elif os.path.isdir(input_str):  # sometimes
                file_list = unzip_the_folder(input_str)
                for file in file_list:
                    self.input_queue.put(file)
                #
            else:  # many situations but
                if not right_str(input_str):  # 格式错误
                    logging.info(f'{input_str} 格式错误')
                # 格式正确且存在
                elif exist_path := self.is_exist(input_str):
                    if '#' in input_str or self.open_flag:
                        self.open_queue.put(exist_path)
                    else:
                        input_str = input_str.replace('#', '')
                        logging.info(f'{input_str} 已存在')
                else:  # 格式正确但不存在
                    open_flag = False
                    if '#' in input_str:
                        open_flag = True
                        input_str = input_str.replace('#', '')
                    self.download_queue.put((input_str, 'pixiv', open_flag, None))

    # 识别网站中的图片链接
    def search(self):
        while True:
            file = self.search_queue.get()
            search_handler = SearchAllResult(file, api_key=self.api_key)
            try:
                result, short_remaining, long_remaining = search_handler.get_one_id()
            except (ApiError, requests.exceptions.SSLError):
                time.sleep(20)
                logging.info(f'{file}重新进入搜索队列')
                self.search_queue.put(file)
            except (ConnectionError, BadImageError, requests.exceptions.ProxyError):
                time.sleep(10)
                logging.info(f'{file}重新进入搜索队列')
                self.search_queue.put(file)
            except ApiKeyError:
                logging.info('APIKey is wrong,please check your key')
                break
            except Non200Error:
                logging.info('一般出现此错误说明超出了查询配额，请明天再试')
                break
            else:
                if result is not None:
                    logging.info(f'搜索到结果 {result}')
                    if os.path.dirname(file) == self.quick_path:
                        self.download_queue.put((result, 'pixiv', False, file))
                    else:
                        self.download_queue.put((result, 'pixiv', False, None))
                else:
                    send_to_bin(file, self.bin_path)
                    logging.info(f'{file},已转移到垃圾箱')
                if long_remaining == '0':
                    logging.info('long_remaining == 0,sleep 1h')
                    time.sleep(3600)
                elif short_remaining == '0':
                    logging.info('short_remaining == 0,sleep 10s')
                    time.sleep(10)

    # 从图片链接获取二进制文件
    def download(self):
        pixiv_base_url = 'http://pixiv.re/{pixiv_id}.png'
        while True:
            number, source, open_flag, src_path = self.download_queue.get()
            logging.info(f'下载队列中还有{self.download_queue.qsize()}个任务')
            if source == 'pixiv':
                pixiv_url = pixiv_base_url.format(pixiv_id=number)
                success = self.downloadIt(pixiv_url, number, open_flag, src_path)
                if success and src_path:
                    logging.info(f'{number}下载完成,删除原路径')
                    os.remove(src_path)
            elif source == 'twitter':  # 开发中
                pass

    # 下载单元
    def downloadIt(self, url, number, open_flag, src_path):
        logging.info(f'开始下载{number}')
        try:
            response = requests.get(url, timeout=15)
        except (requests.exceptions.ConnectionError,
                requests.exceptions.ReadTimeout,
                requests.exceptions.ChunkedEncodingError,
                ):
            logging.info(f'{number}重新进入下载队列')
            self.download_queue.put((number, 'pixiv', open_flag, src_path))
            # self.downloadIt(url, number, open_flag)
        else:
            html = response.text
            html_title = re.findall('<title>(.*?)</title>', html)  # 通过获取网页标题判断是否为图片
            if len(html_title) > 0:  # 网页有标题则代表非图片
                pic_num = re.findall('中有 (.*?) 張', html)  # 寻找是否多图
                if len(pic_num) > 0:  # 若存在图片数量则循环递归调用访问单元获取所有图片
                    logging.info(number + '共 {} 张'.format(pic_num[0]))  # 多图数量反馈
                    for i in range(1, int(pic_num[0]) + 1):  # 网站约束图片下标为1开始
                        add_pixivid = str(number) + '-' + str(i)
                        if not (path := self.is_exist(add_pixivid)):
                            logging.info(f'{add_pixivid}进入下载队列')
                            self.download_queue.put((add_pixivid, 'pixiv', open_flag, src_path))
                        else:
                            if open_flag or self.open_flag:
                                self.open_queue.put(path)
                            continue  # 已存在的跳过该图继续查询
                else:
                    logging.info(f'{number}被删除或不存在')  # 所有异常情况与图片被删除无异 故直接归类为图片被删除
                    return False
            else:  # 是图片
                content = response.content  # 若为图片获得图片的二进制内容
                self.save_queue.put((content, to_pid(number), open_flag))
                return True
                # logging.info(f'{number}下载完成')

    # 保存图片
    def save(self):
        while True:
            content, filename, open_flag = self.save_queue.get()
            path = os.path.join(self.download_path, filename)
            if not os.path.exists(self.download_path):  # 检测图片下载文件夹是否存在，不存在则创建
                os.mkdir(self.download_path)
            with open(path, "wb") as f:  # 二进制格式写入图片
                f.write(content)
                logging.info(f'{filename} 保存成功')
            if open_flag or self.open_flag:
                self.open_queue.put(path)

    # 打开图片
    def open_file(self):
        while True:
            path = self.open_queue.get()
            os.system(path)

    def run(self):
        thread_list = list()

        # range(线程数)

        # 1、获取用户输入
        for i in range(1):
            t_input = Thread(target=self.user_input)
            thread_list.append(t_input)

        # 2、解析用户输入为命令或图片id或路径
        for i in range(1):
            t_parse = Thread(target=self.get_folder_or_file_or_pid)
            thread_list.append(t_parse)

        # 3、发起搜图请求
        for i in range(1):
            # 单线程搜图，建议 1 或 2 ，线程 >5 会超出配额变相减慢速度
            t_search = Thread(target=self.search)
            thread_list.append(t_search)

        # 4、下载图片线程
        for i in range(5):
            t_download = Thread(target=self.download)
            thread_list.append(t_download)

        # 5、保存图片线程
        for i in range(1):
            t_save = Thread(target=self.save)
            thread_list.append(t_save)
        # 6、打开图片线程
        for i in range(1):
            t_open = Thread(target=self.open_file)
            thread_list.append(t_open)

        for t in thread_list:
            # t.setDaemon(True)  # 子线程设置为后台线程
            t.start()
