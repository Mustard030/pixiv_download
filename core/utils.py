import re
import os
import shutil


class Utils(object):

    # 帮助
    @staticmethod
    def helper():
        print('1、文件setting.cfg为储存设定路径和APIKEY的文本文件，可直接右键编辑，但是建议根据下列命令设定。')
        print('2、在图片ID后增加 # 号可以在下载完成后自动打开，已存在的图片加上 # 也会直接打开。')
        print('3、使用《 open 》或《 # 》命令可以《 切换 》自动打开模式，自动模式打开时不输入#号也会自动打开图片。')
        print('4、图片ID下若有多张图，直接输入ID会《 全部 》下载;\n   若已知图片分p可以使用XXX-X格式《 单独 》下载，序号从1开始（如:80428675-1）。')
        print('5、拖动本地文件到窗口中并回车可以直接进入搜图并下载模式，此模式下只有open命令能打开图片，输入#会导致路径错误。')
        print('6、使用《 key 》命令可以设置saucenao.com的API_KEY以加大您的搜图配额。')
        print('7、使用中/英文的！可以在你设置的快速搜索路径批量搜图。')
        print('8、遇到图片下载不全，实为代理网络问题，这种情况请重新下载此图，极大概率会解决。')
        print('命令大全：')
        print("""
                help'，'?'，'？': 帮助,
                'download': 重设下载路径
                'hub': 设置图片仓库路径,
                'open'，'#': 自动打开切换,
                'key': 设定API_KEY,
                '!'，'！': 在设定的路径快速搜索,
                '@': 切换是否使用API_KEY配额,
                'cache': 设定快速搜索路径,
                'bin': 设定图片回收箱路径""")
        print('使用愉快!')

    # 格式化URL
    @staticmethod
    def get_url(pixiv_id) -> str:
        url = f'http://pixiv.re/{pixiv_id}.png'  # 格式化访问网址
        return url

    # 格式化图片id XXX-X -> XXX_pX.png
    @staticmethod
    def to_pid(id_p):
        found = re.findall(r'(\d{8})(.*?)$', id_p)[0]
        if found[1]:
            return found[0] + '_p' + str(abs(int(found[1])) - 1) + '.png'
        else:
            return found[0] + '_p0' + '.png'

    # 删除文件名空格
    @staticmethod
    def delete_space(search_dir):
        file_list = next(os.walk(search_dir))[2]
        for file in file_list:
            old_path = os.path.join(search_dir, file)
            no_space = file.replace(' ', '')
            new_nospace = os.path.join(search_dir, no_space)
            os.rename(old_path, new_nospace)

    # 图片回收至垃圾箱
    @staticmethod
    def send_to_bin(search_file, bin_path):
        file_name = os.path.basename(search_file)
        # print(f'图片{file_name}将转移至垃圾箱')
        shutil.move(search_file, os.path.join(bin_path, file_name))
        # print('转移完成')

    # 判断文件名是否有图片id信息
    @staticmethod
    def useful_name(filename):
        pattern = re.compile(r'^(\d{8})_?[p.]([0-9]{0,2})')
        base_name = os.path.basename(filename)
        if result := pattern.search(base_name):
            if not result.group(2):
                return result.group(1)
            else:
                return result.group(1) + '-' + str(int(result.group(2)) + 1)
        else:
            return None

    # 格式化输入字符串
    @staticmethod
    def format_input_str(input_str) -> list:
        str_list = input_str.split(' ')
        while '' in str_list:
            str_list.remove('')
        return str_list

    # 将文件夹内的图片解包到队列，供分析使用
    @staticmethod
    def unzip_the_folder(folder):
        file_list = next(os.walk(folder))[2]
        for file in file_list:
            file_name = os.path.join(folder, file)
            yield file_name

    # 检查输入格式
    @staticmethod
    def right_string(input_str):
        if input_str[-1] == '#':
            input_str = input_str[:-1]
        split_num = input_str.split('-')
        if len(split_num[0]) == 8:
            return True
        else:
            return False

    # 将需要打开的文件放入打开队列
    @staticmethod
    def open_it(_queue, file_path):
        _queue.put(file_path)

    # 获得图片的本地的路径
    @staticmethod
    def get_real_path(filename, path_list: list):
        suffix = os.path.splitext(filename)[-1]
        if suffix == '.jpg':
            filename_su = filename[:-4] + '.png'
        elif suffix == '.png':
            filename_su = filename[:-4] + '.jpg'
        else:
            filename_su = filename
        for path in path_list:
            for file in [filename, filename_su]:
                if real_path := os.path.join(path, file):
                    if os.path.isfile(real_path):
                        return real_path

        return None

    # 获得pixiv代理的链接
    # 多图情况将在download方法中处理
    @staticmethod
    def get_pixiv_id(src):
        result = re.search(r'\d{8}', src)
        if isinstance(result, re.Match):
            return result.group()

        return None

    # 获得twitter代理的链接
    @staticmethod
    def get_twitter_url(src):
        pass

        # print(pics)
        # for pic in pics:
        #     yield pic

    # 文件存在检查 忽略'#'
    # (xxx.jpg/.png or XXX-X) folder_list -> real_folder\xxx.jpg
    @staticmethod
    def is_exist_in(input_str: str, folder_list: list) -> str:
        # input_str maybe whole_file_path or xxx-x
        if os.path.isfile(input_str):
            filename = os.path.basename(input_str)
            return get_real_path(filename, folder_list)
        else:  # is xxx-x or xxx
            input_str = input_str.replace('#', '')
            pid = to_pid(input_str)  # return XXX_pX.png
            return get_real_path(pid, folder_list)

    # 是否为网址
    @staticmethod
    def is_url(url):
        return re.search(r'[a-zA-z]+://[^\s]*', url)

    # 判断是否pixiv或其代理的网址
    @staticmethod
    def is_pixiv_url(url):
        return ('pixiv' in url) and ('illust' in url or 'artworks' in url or '/i/' in url or '.re' in url)

    # 判断是否为twitter网址
    @staticmethod
    def is_twitter_url(url):
        return 'twitter' in url

helper = Utils.helper
get_url = Utils.get_url
to_pid = Utils.to_pid
delete_space = Utils.delete_space
send_to_bin = Utils.send_to_bin
useful_name = Utils.useful_name
format_input_str = Utils.format_input_str
unzip_the_folder = Utils.unzip_the_folder
right_string = Utils.right_string
open_it = Utils.open_it
get_real_path = Utils.get_real_path
get_pixiv_id = Utils.get_pixiv_id
get_twitter_url = Utils.get_twitter_url
is_exist_in = Utils.is_exist_in
is_url = Utils.is_url
is_pixiv_url = Utils.is_pixiv_url
is_twitter_url = Utils.is_twitter_url

# 搜图配置项
index_hmags = '0'
index_reserved = '0'
index_hcg = '0'  # 1
index_ddbobjects = '0'
index_ddbsamples = '0'
index_pixiv = '1'
index_pixivhistorical = '1'
index_reserved = '0'
index_seigaillust = '0'  # 1
index_danbooru = '0'
index_drawr = '0'  # 1
index_nijie = '0'  # 1
index_yandere = '0'  # 1
index_animeop = '0'
index_shutterstock = '0'
index_fakku = '0'
index_hmisc = '0'
index_2dmarket = '0'
index_medibang = '0'
index_anime = '0'
index_hanime = '0'
index_movies = '0'
index_shows = '0'
index_gelbooru = '0'
index_konachan = '0'
index_sankaku = '0'
index_animepictures = '0'
index_e621 = '0'
index_idolcomplex = '0'
index_bcyillust = '0'
index_bcycosplay = '0'
index_portalgraphics = '0'
index_da = '0'  # 1
index_pawoo = '0'  # 1
index_madokami = '0'
index_mangadex = '0'

db_bitmask = int(
    index_mangadex + index_madokami + index_pawoo + index_da + \
    index_portalgraphics + index_bcycosplay + index_bcyillust + \
    index_idolcomplex + index_e621 + index_animepictures + \
    index_sankaku + index_konachan + index_gelbooru + index_shows + \
    index_movies + index_hanime + index_anime + index_medibang + \
    index_2dmarket + index_hmisc + index_fakku + index_shutterstock + \
    index_reserved + index_animeop + index_yandere + index_nijie + \
    index_drawr + index_danbooru + index_seigaillust + index_anime + \
    index_pixivhistorical + index_pixiv + index_ddbsamples + \
    index_ddbobjects + index_hcg + index_hanime + index_hmags
    , 2)
