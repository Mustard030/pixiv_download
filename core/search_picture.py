from .utils import *
from .myException import *


class SearchAllResult:

    def __init__(self, local_path, minsim='65!', api_key="!!! INPUT YOUR KEY"):

        self.local_path = local_path
        self.minsim = minsim
        self.api_key = api_key
        self.__URL = 'http://saucenao.com/search.php?output_type=2&numres=4&minsim=' + self.minsim + '&dbmask=' + str(
            db_bitmask) + '&api_key=' + self.api_key

    def __post_data(self):  # 上传图片到URL
        # print(self.__URL)
        files = {'file': open(self.local_path, 'rb')}
        logging.info(f'正在搜索{self.local_path}')
        try:
            response = requests.post(self.__URL, files=files)
        except (requests.exceptions.SSLError, requests.exceptions.ProxyError, requests.exceptions.ConnectionError):
            logging.info('Error occurred')
            raise

        if response.status_code != 200:
            if response.status_code == 403:
                raise ApiKeyError
            else:
                # generally non 200 statuses are due to either overloaded servers or the user is out of searches
                raise Non200Error("status code: " + str(
                    response.status_code) + "\ngenerally non 200 statuses are due to either overloaded servers or the user is out of searches")

        else:
            results = response.json()
            # api responded
            logging.info('Remaining Searches 30s|24h: ' + (
                short_remaining := str(results['header']['short_remaining'])) + '|' + (
                             long_remaining := str(results['header']['long_remaining'])))
            if int(results['header']['status']) == 0:
                # search succeeded for all indexes, results usable
                search_results = list()
                for i in range(len(results['results'])):
                    if float(results['results'][i]['header']['similarity']) > float(
                            results['header']['minimum_similarity']):
                        search_results.append(results['results'][i]['data'])
                return search_results, short_remaining, long_remaining
            else:
                if int(results['header']['status']) > 0:
                    # One or more indexes are having an issue.
                    # This search is considered partially successful, even if all indexes failed, so is still counted against your limit.
                    # The error may be transient, but because we don't want to waste searches, allow time for recovery.
                    raise ApiError

                else:
                    # Problem with search as submitted, bad image, or impossible request.
                    # Issue is unclear, so don't flood requests.
                    raise BadImageError

    def get_all_id(self):
        print('searching...')
        try:
            results = self.__post_data()
        except:
            raise
        else:
            if results:  # 结果列表非空
                print(results)
            else:
                print('偏差范围内无结果!')

    def get_one_id(self):
        try:
            results, short_remaining, long_remaining = self.__post_data()
        except:
            raise
        else:
            for result in results:  # 选取第一个PixivID
                pid = result.get('pixiv_id', None)
                if pid:
                    # logging.info(f'搜索到结果{pid}')
                    return str(pid), short_remaining, long_remaining

            return None, short_remaining, long_remaining


def helper():
    print('你现在调用的是单独的搜图程序，并不包含下载功能，但是会返回所有匹配结果')
    print('你可以自行判断搜图结果然后去下载该图片（仅能下载P站的图）')


def main():
    while True:
        local_path = input('拖动图片到此窗口然后回车键开始搜索(输入help查看帮助)\n')
        if local_path == 'help':
            helper()
        else:
            pic = SearchAllResult(local_path)  # 创建一个搜索对象
            pic.get_all_id()  # 获取所有返回结果


if __name__ == '__main__':  # 自身调用则为搜索所有ID
    main()

if __name__ == 'search_picture':  # 被调用则返回1个pixiv_id
    pass
