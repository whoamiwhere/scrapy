
import pandas as pd
from urllib.request import urlopen
from bs4 import BeautifulSoup
import time
import random

# first step 
url = f'https://bj.lianjia.com/zufang/'
html = urlopen(url)
bs = BeautifulSoup(html, "html.parser")
dataList = bs.find('div', {'class': 'filter'}).find('ul',{'data-target':"area"}).findAll('a')
DistrictInfo = pd.DataFrame(columns=('District','District_url'))

for i,data in enumerate(dataList):
    if i != 0:
        DistrictInfo.loc[i] = [data.get_text(),'https://bj.lianjia.com'+data['href']]
    else:
        pass
# print(DistrictInfo)
# we have District and District_url now

# second step
Detailed_DistrictInfo = pd.DataFrame(columns=('District','Street','Street_url'))

for num in range(len(DistrictInfo)):

    temp_district = DistrictInfo.iloc[num, 0]  # District
    temp_url = DistrictInfo.iloc[num, 1]   # District_url

    temp_html = urlopen(temp_url)
    temp_bs = BeautifulSoup(temp_html, "html.parser")
    temp_dataList = temp_bs.find('div', {'class': 'filter'}).find_all('ul',{'data-target':"area"})[1].find_all('a')
    # print(temp_dataList)
    temp_DistrictInfo = pd.DataFrame(columns=('District','Street','Street_url'))
    # we have temp_district's info

    for i,data in enumerate(temp_dataList):
        if i != 0:
            temp_DistrictInfo.loc[i] = [temp_district,data.get_text(),'https://bj.lianjia.com'+data['href']]
        else:
            pass
    Detailed_DistrictInfo = pd.concat([Detailed_DistrictInfo,temp_DistrictInfo],ignore_index=True)
    print(temp_district+'is over!!!')
    time.sleep(random.randint(2,5))
# we have a final dataframe

# write into csv 
txt_path = f"C:/Users/28440/Desktop/data/Detailed_DistrictInfo_zufang.csv"
Detailed_DistrictInfo.to_csv(txt_path,encoding='utf-8')
