from multiprocessing.dummy import Pool as ThreadPool
import requests
from bs4 import BeautifulSoup as Bs
import math
import common


class coll_osc:

    def __init__(self, prefix):
        self.url_prefix = prefix
        self.proj_urls = []

    def get_pagination_urls(self, base_url):
        """获取采集项目数据信息的分页URL"""

        url = base_url + '1'
        r = requests.get(url, headers=common.get_header())

        soup = Bs(r.text)
        page_data = Bs(str(soup.find_all(class_='ProjectList'))).find_all(class_='stat')
        max_page = math.ceil(int(page_data[0].next_sibling.next_sibling.text) / 20)

        return (base_url + str(i) for i in range(1, max_page + 1))

    def parse_project_baseinfo(self, url):
        """解析库的基本信息"""

        r = requests.get(url, headers=common.get_header())

        project_data = Bs(str(Bs(r.text).find_all(class_='ProjectList')))
        list_data = project_data.find_all(class_='List')
        page = project_data.find_all(class_='stat')[0].next_sibling.next_sibling.text

        projects = []
        for w in Bs(str(list_data)).find_all('h3'):
            link = w.select('a')
            link = 'http://www.oschina.net' + Bs(str(link[0])).a.get('href')
            projects.append({'url': link})

        return projects

    def get_proj_urls(self):
        """获取库的url"""

        for info_list in self.proj_base_info:
            for proj in info_list:
                self.proj_urls.append(proj['url'])
        return self

    @common.exe_time
    def get_lib_baseinfo(self):
        """获取收录库的基本信息"""
        urls = self.get_pagination_urls(self.url_prefix)

        pool = ThreadPool(10)
        self.proj_base_info = pool.map(self.parse_project_baseinfo, urls)
        pool.close()
        pool.join()
        return self

    @common.exe_time
    def start_detail_parse(self):
        pool = ThreadPool(10)
        results = pool.map(self.parse_proj_detail_info, self.proj_urls)
        pool.close()
        pool.join()
        return results

    def parse_proj_detail_info(self, url):
        """解析项目详细信息"""
        r = requests.get(url, headers=common.get_header())
        item = [None, None]

        soup = Bs(r.text)
        attrs_data = str(soup.find_all(class_='attrs'))

        if soup.find(class_='name'):
            name = soup.find(class_='name').u.text
        else:
            return item

        if attrs_data.find('年') and attrs_data.find('月'):
            item = [attrs_data[attrs_data.find('年') - 4: attrs_data.find('月')].replace('年', '-').replace('月', '-'), name]
            print(item[0], '\t', item[1])
        return item


if __name__ == '__main__':
    #收集golang库的数据
    coll_osc = coll_osc('http://www.oschina.net/project/lang/358/go?tag=0&os=0&sort=time&p=')
    coll_osc\
        .get_lib_baseinfo()\
        .get_proj_urls()\
        .start_detail_parse()

    # 'http://www.oschina.net/project/lang/25/python?tag=0&os=0&sort=time&p='
    # 'http://www.oschina.net/project/lang/22/php?tag=0&os=0&sort=time&p='