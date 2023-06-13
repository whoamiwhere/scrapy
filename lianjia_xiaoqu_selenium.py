 
# 导入所需库
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from retrying import retry   # @retry(wait_fixed=10, stop_max_attempt_number=1)
import pandas as pd
import random
import time

class Spider():
    def __init__(self):
        # 设置浏览器参数
        options = Options()
        options.binary_location = r"C:/Program Files/Mozilla Firefox/firefox.exe"
        options.add_argument('--headless')                     # 开启无界面模式
        options.add_argument("--disable-gpu")                  # 禁用gpu
        options.add_argument('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36 Edg/113.0.1774.35')  # 配置对象添加替换User-Agent的命令
        options.add_argument('blink-settings=imagesEnabled=false')  # 不加载图片, 提升速度
        options.set_preference("permissions.default.image", 2)
        options.add_argument('--no-sandbox') # 禁用沙盒模式
        # options.page_load_strategy = 'eager'
        self.driver = webdriver.Firefox(options=options)

        self.batch = 10
        self.rows = 0 
        self.url = ''
        self.position_info = pd.Series(index = ['District','Street','xiaoqu'],dtype = object)

    def create_dataframe(self):
        # 创建DataFrame
        global xiaoquInfoLabel,nearbylabel,nebour_label
        xiaoquInfoLabel = ['建筑年代', '建筑类型', '物业费用', '物业公司', '开发商','楼栋总数', '房屋总数']
        nearbylabel = ['附近小区{}'.format(i+1) for i in range(5)]
        nebour_label = ['交通-地铁站','交通-公交站','教育-幼儿园','教育-小学','教育-中学','教育-大学'] + \
        ['医疗-医院','医疗-药店','购物-商场','购物-超市','购物-市场'] + \
        ['生活-银行','生活-ATM','生活-餐厅','生活-咖啡馆','娱乐-公园','娱乐-电影院','娱乐-健身房','娱乐-体育馆']
        # create dataframe to load data
        dfcolumns = ['District','Street','xiaoqu'] + xiaoquInfoLabel + ['小区关注人数'] + nearbylabel + nebour_label
        df = pd.DataFrame(columns=dfcolumns)
        return df
        
    # part 1
    def write_to_dataframe_xiaoquInfoLabel(self,df):
        xiaoquInfoContent = self.driver.find_elements(By.CLASS_NAME , 'xiaoquInfoContent')
        xiaoquInfocontent_list = []
        for Content in xiaoquInfoContent[:-1]:
            xiaoquInfocontent_list.append(Content.text)
        # df = pd.concat([df,pd.Series(xiaoquInfocontent_list,index=xiaoquInfoLabel).to_frame().T],
        #  axis = 0,ignore_index=True)
        # 将数据写入DataFrame
        df.loc[self.rows,xiaoquInfoLabel] = pd.Series(xiaoquInfocontent_list,index=xiaoquInfoLabel)
        df.loc[self.rows,['District','Street','xiaoqu']] = self.position_info

    # part 2
    def write_to_dataframe_followNumber(self,df):
        # 将数据写入DataFrame
        df['小区关注人数'][self.rows] = self.driver.find_element(By.CLASS_NAME , 'detailFollowedNum').text
    
    # part 3
    def write_to_dataframe_nearbylabel(self,df):
        nearbyContent1 = self.driver.find_elements(By.CLASS_NAME , 'nearbyItemTitle')
        nearbyContent2 = self.driver.find_elements(By.CLASS_NAME , 'nearbyItemType')
        nearbyContent_list = [nearbyContent1[i].text + '-' + nearbyContent2[i].text for i in range(len(nearbyContent1))]
        # 将数据写入DataFrame
        df.loc[self.rows,nearbylabel] = pd.Series(nearbyContent_list,index=nearbylabel)

    # part 4
    def write_to_dataframe_nebour_label(self,element_nebour_label,df):
        # time.sleep(random.uniform(0, 0.1))
        nebour_info = self.driver.find_elements(By.CLASS_NAME , 'contentBox')
        nebour_info = ','.join([i.text.replace('\n', '--') for i in nebour_info])
        # 将数据写入DataFrame
        df[element_nebour_label][self.rows] = nebour_info

    # 异常重试2次
    @retry(stop_max_attempt_number=2)
    def click_data_bl(self,data_bl):
        # 模拟点击一级标签
        click_element = self.driver.find_elements(By.CSS_SELECTOR  , '.LOGCLICK')
        click_element = [i for i in click_element if i.text == data_bl][0]
        self.driver.execute_script('arguments[0].scrollIntoView(true);',click_element)
        # ActionChains(self.driver).move_to_element(click_element).click(click_element).perform()
        self.driver.execute_script('arguments[0].click()',click_element)

        WebDriverWait(self.driver,10,0.5).until(EC.text_to_be_present_in_element(
            (By.CSS_SELECTOR,'.LOGCLICK.selectTag'),data_bl))
    def click_data_key(self,data_key):
        # 模拟点击二级标签
        click_element = self.driver.find_elements(By.CSS_SELECTOR  , '.tagStyle.LOGCLICK')
        click_element = [i for i in click_element if i.text == data_key][0]
        self.driver.execute_script("arguments[0].scrollIntoView(true);",click_element)
        self.driver.execute_script('arguments[0].click()',click_element)

        WebDriverWait(self.driver,10,0.5).until(EC.text_to_be_present_in_element(
            (By.CSS_SELECTOR,'div.tagStyle.LOGCLICK.select'),data_key))

    def scrapy_nebour(self,df):
        for element_nebour_label in nebour_label:

            data_bl = element_nebour_label.split('-')[0]
            data_key = element_nebour_label.split('-')[-1]

            if element_nebour_label in ('交通-地铁站','教育-幼儿园','医疗-医院','购物-商场','生活-银行','娱乐-公园'):

                if element_nebour_label == '交通-地铁站':
                    pass
                else:
                    self.click_data_bl(data_bl = data_bl)
            else:

                if self.driver.find_element(By.CSS_SELECTOR  , '.LOGCLICK.selectTag').text == data_bl:
                    self.click_data_key(data_key = data_key)
                else :
                    # 点击异常的处理(重新点击一级再点击二级)
                    self.click_data_bl(data_bl = data_bl)
                    self.click_data_key(data_key = data_key)
            # 写入dataframe
            self.write_to_dataframe_nebour_label(element_nebour_label = element_nebour_label,df = df)



    def run(self,xiaoqu_df ):

        for i in range(len(xiaoqu_df)):

            # 运行爬虫
            # update -- url,position_info,rows
            self.url = xiaoqu_df['url'][i]
            self.position_info = xiaoqu_df.loc[i,['District','Street','xiaoqu']]
            self.rows = i % self.batch
            if self.rows == 0:
                df = self.create_dataframe()
            else:
                pass

            try:
                start_time = time.time()
                # 打开网页
                self.driver.get(self.url)
                # 等待元素加载完成
                self.driver.implicitly_wait(10) # seconds
                # 写入常规页面元素
                self.write_to_dataframe_xiaoquInfoLabel(df = df)
                self.write_to_dataframe_followNumber(df = df)
                self.write_to_dataframe_nearbylabel(df = df)
                end_time_temp1 = time.time()
                elapsed_time_temp1 = end_time_temp1 - start_time
                print("加载和常规写入程序耗时：", elapsed_time_temp1, "秒")

                # 写入邻近周边信息
                self.scrapy_nebour(df = df)
                end_time = time.time()
                elapsed_time = end_time - start_time
                print("总程序耗时：", elapsed_time, "秒")
                print('----第{}个小区爬取完毕！'.format(i))

            except Exception as e:
                print('程序报错如下：----')
                print(e)
        
        # 关闭浏览器
        self.driver.quit()
        return df

if __name__ == '__main__':

    scrapy_num = 3
    Detail_xiaoqu_lianjia = pd.read_csv(f'C:/Users/28440/Desktop/data/Detail_xiaoqu_lianjia.csv',encoding='gbk')
    Detail_xiaoqu_lianjia = Detail_xiaoqu_lianjia.loc[:(scrapy_num-1),:]
    xiaoqu_df = pd.DataFrame()
    xiaoqu_df['District'] = pd.Series([i.split('?')[0] for i in Detail_xiaoqu_lianjia['PositionInfo']])
    xiaoqu_df['Street'] = pd.Series([i.split('?')[1] for i in Detail_xiaoqu_lianjia['PositionInfo']])
    xiaoqu_df['xiaoqu'] = Detail_xiaoqu_lianjia['Title']
    xiaoqu_df['url'] = Detail_xiaoqu_lianjia['Url']

    spider = Spider()
    df = spider.run(xiaoqu_df = xiaoqu_df)
    print(df)
    
    
