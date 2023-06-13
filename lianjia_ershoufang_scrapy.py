#1.爬取主页面的详情页面网址
# def info_url(self,page_url):
#     href_list = []
#     driver = webdriver.Chrome(
#         executable_path="")#chromedriver的启动路径
#     # chromedriver下载网站：https://registry.npmmirror.com/binary.html?path=chromedriver
#     wait = WebDriverWait(driver, 10)
#     wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
#     driver.get(page_url)
#     li_list = driver.find_elements_by_xpath("//div[@class='info']")
#     for li in li_list:
#         title = li.find_element_by_xpath("./div[@class='title']/a").text
#         print(title)
#         href = li.find_element_by_xpath("./div[@class='title']/a").get_attribute("href")
#         href_list.append(href)
#     driver.quit()
#     return href_list[0:10]


import requests
from pyquery import PyQuery as pq
from fake_useragent import UserAgent
import time
import random
import pandas as pd


UA = UserAgent()
headers = {
'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6,pl;q=0.5',
'Cookie': f'lianjia_uuid=4173cd2d-214b-4694-874f-d19dc6714f9f; select_city=110000; _jzqc=1; _jzqy=1.1683858877.1683858877.1.jzqsr=baidu.-; _jzqckmp=1; _smt_uid=645da5bc.25733fd3; sajssdk_2015_cross_new_user=1; _gid=GA1.2.363603714.1683858878; Hm_lvt_9152f8221cb6243a53c83b956842be8a=1683858883; _ga_TJZVFLS7KV=GS1.1.1683859068.1.1.1683859214.0.0.0; _ga=GA1.2.898548915.1683858878; lianjia_ssid=6addef62-5bad-420c-81a3-5e5dd0ecc51a; _jzqa=1.2984572686701254000.1683858877.1683858877.1683878251.2; _jzqx=1.1683878251.1683878251.1.jzqsr=bj%2Elianjia%2Ecom|jzqct=/xiaoqu/.-; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%221880dcf69ad880-0931b430b49ad1-7b515477-1327104-1880dcf69ae12c6%22%2C%22%24device_id%22%3A%221880dcf69ad880-0931b430b49ad1-7b515477-1327104-1880dcf69ae12c6%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_referrer%22%3A%22%22%2C%22%24latest_referrer_host%22%3A%22%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%7D%7D; _gat=1; _gat_past=1; _gat_global=1; _gat_new_global=1; _gat_dianpu_agent=1; Hm_lpvt_9152f8221cb6243a53c83b956842be8a=1683878560; _jzqb=1.4.10.1683878251.1',
'Host': 'bj.lianjia.com',
'Referer': 'https://bj.lianjia.com/ershoufang/',
'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.35',
}
num_page = 2
class Lianjia_Crawer:
    def __init__(self,txt_path):
        super(Lianjia_Crawer,self).__init__()
        self.file = str(txt_path)
        self.df = pd.DataFrame(columns = ['Title','PositionInfo','HouseInfo','FollowInfo','Tag_taxfree','Tag_subway','TotalPrice','UnitPrice'])


    def run(self):
        '''启动脚本'''
        for i in range(num_page):
            url = "https://bj.lianjia.com/ershoufang/haidian/pg{}/".format(str(i+1))
            self.parse_url(url)
            time.sleep(random.randint(2,5))
            print('正在爬取的 url 为 {}'.format(url))
        print('爬取完毕！！！！！！！！！！！！！！')
        self.df.to_csv(self.file,encoding='utf-8')
    def parse_url(self,url):

        headers['User-Agent'] = UA.chrome
        res = requests.get(url, headers=headers)
        doc = pq(res.text)
        for i in doc('.clear.LOGCLICKDATA .info.clear'):
            try:
                data_list = []
                pq_i = pq(i)
                Title = pq_i('.title').text()         # .replace('必看好房', '')
                PositionInfo = pq_i('.flood .positionInfo').text()

                HouseInfo = pq_i('.address .houseInfo').text()
                FollowInfo = pq_i('.followInfo').text()
                Tag_taxfree = pq_i('.tag .taxfree').text() + pq_i('.tag .five').text()
                Tag_subway = pq_i('.tag .subway').text()
                TotalPrice = pq_i('.priceInfo .totalPrice').text()
                UnitPrice = pq_i('.priceInfo .unitPrice').text()

                data_dict ={
                    'Title':Title,
                               'PositionInfo':PositionInfo,
                               'HouseInfo':HouseInfo,
                               'FollowInfo':FollowInfo,
                               'Tag_taxfree':Tag_taxfree,
                               'Tag_subway':Tag_subway,
                               'TotalPrice':TotalPrice,
                    'UnitPrice':UnitPrice
                }
                # print(Community,CityDirct)
                # self.df = self.df.append(data_dict,ignore_index=True)
                data_list.append(data_dict)
                self.df = pd.concat([self.df, pd.DataFrame(data_list)], ignore_index=True)
                #self.file.write(','.join([title, Community, CityDirct, HouseInfo, DateInfo, TagList, TotalPrice, UnitPrice]))
                # print([title, Community, CityDirct, HouseInfo, DateInfo, TagList, TotalPrice, UnitPrice])
            except Exception as e:
                print(e)
                print("索引提取失败，请重试！！！！！！！！！！！！！")



if __name__ =="__main__":
    txt_path = "C:/Users/28440/Desktop/data/ershoufang_lianjia.csv"
    Crawer = Lianjia_Crawer(txt_path)
    Crawer.run() # 启动爬虫脚本