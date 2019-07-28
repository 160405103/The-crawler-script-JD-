'''
2019.7.10
自动化爬取京东苹果8手机的售卖信息（名字 价格 超链接）
1.自动搜索
2.爬取元素
3.存入txt文件

'''
import datetime
import os
import time

import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

driver = webdriver.Chrome()
url = "https://www.jd.com"
wait = WebDriverWait(driver, 10)  # 每隔10秒看一眼，如果条件成立了，则执行下一步，否则继续等待，直到超过设置的最长时间，然后抛出TimeoutException。
KEYWORD = "苹果8"
time_start=time.time()
path="JD_Info2"

def search():
    driver.get(url)
    print('正在搜索')
    try:
        # 获取输入框
        input = wait.until(
            # 判断该元素是否加载完成  输入框
            EC.presence_of_element_located((By.CSS_SELECTOR, '#key'))
        )
        # 获取搜索点击按钮
        submit = wait.until(
            # 判断该元素是否可以点击   查询按钮
            EC.element_to_be_clickable((By.XPATH, '//*[@id="search"]/div/div[2]/button'))
        )
        # 输入查询关键字
        input.send_keys(KEYWORD)
        submit.click()
        total = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="J_topPage"]/span/i')))
        print('一共' + total.text + "页")
       # save_good_list(get_good_list())
        return total.text
    except TimeoutException:
        print("用时过长，自动退出")
        driver.close()
        return search()

def save_good_list(good_list):
    print("[当前页面商品数]",len(good_list))
    length=len(good_list)
    index=0
    #print("进入save_good_list函数")
    #print(len(good_list))
    for temp in good_list:
        with open("./"+path+"/jindong.txt", 'a', encoding='utf-8') as f:
            #print(temp)
            f.write(temp['good_price'] + "     " + temp['good_name'] + "     " + temp['good_href'] )
        with open("./"+path+"/img/" + temp['good_name'] + ".jpg", 'bw') as fi:
            if temp['good_image']!="http://None":
                resp = requests.get(temp['good_image'])
                fi.write(resp.content)
        index+=1
        print('\r'+'[保存进度]:%s%.2f%%' %('>'*int(index*50/length),float(index/length*100)),end='')     #%%百分号



def get_good_list():
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    good_list1 = soup.select("div#J_goodsList >ul>li")

    good_list = []
    for temp in good_list1:  # 对于每个li 获取价格 div class="p-price" <i>4299</i>
        # 获取链接和名字  div class="p-name p-name-type-2"    <a href=> <em>  名字</em>
        good_price = temp.find("div", class_="p-price").get_text()
        #print(good_price)
        # print(good_price.get_text())  #html为  <div> <em>$</em> <i>3499</i><div>    get_text()结果为$3499
        good_info = temp.find("div", class_="p-name p-name-type-2")
        good_name1 = good_info.em.get_text()
        #str = './test/Apple 苹果/iPhone8Plus手机【白条3期免息0首付】 金色 64G.jpg'
        good_name = eval(repr(good_name1).replace('/', 'or'))

        good_href = good_info.a['href']

        good_image = temp.find("img").get("data-lazy-img")
        if good_image =='done':
            good_image=temp.find("img").get("src")

        if good_image == None:
            good_image="//None"
        #print(good_image)

        product = {
            'good_price': good_price,
            'good_name': good_name,
            'good_href': str("http:" + good_href),
            'good_image':str("http:"+ good_image)
        }


        good_list.append(product)

    #print(good_list)
    return good_list



def make_dir(floder):
    path = os.getcwd() + '/' + floder  # 在当前目录下创建文件夹
    path1=path+'/'+'img'
    if not os.path.isdir(path):  # 不存在才创建文件夹
        os.makedirs(path)
        os.makedirs(path1)
    return path


def next_page(i):
    print("\n")
    print('正在搜索保存第' + str(i) + "页")
    good_list = get_good_list()
    save_good_list(good_list)
    try:
        submit = wait.until(
            # 判断该元素是否可以点击   查询按钮
            EC.element_to_be_clickable((By.XPATH, '// *[ @ id = "J_bottomPage"] / span[1] / a[9]'))
        )

        submit.click()

    except TimeoutException:
        print("用时过长，自动退出")
        driver.close()
        return next_page()

def downloader(url,path):
    start=time.time()
    size=0
    response=requests.get(url,stream=True)
    chunk_size=1024
    content_size=int(response.headers['content-length'])#返回的response的headers中获取文件大小信息
    print("文件大小：" + str(round(float(content_size / chunk_size / 1024), 4)) + "[MB]")

def time_change():
    time_end=time.time()
    return time_end-time_start



def main():
    make_dir(path)
    #print(path)
    #print(time.time())
    search()
    print("输入要几页的信息")
    page=input()
    for i in range(1, int(page)+1):
       next_page(i)
    print("\n")
    print("搜索并保存完毕，花费时间为",time_change(),'s')



if __name__=='__main__':
    main()

'''一个python的文件有两种使用的方法，第一是直接作为脚本执行，
第二是import到其他的python脚本中被调用（模块重用）执行。
因此if __name__ == 'main': 的作用就是控制这两种情况执行代码的过程，
在if __name__ == 'main': 下的代码只有在第一种情况下（即文件作为脚本直接执行）才会被执行，
而import到其他脚本中是不会被执行的。'''
# search()

'''repr() 函数可以将字符串转换为python的原始字符串（即忽视各种特殊字符的作用）
然后再使用eval() 函数将原始字符串转换为正常的字符串，不使用eval 输出的字符串会带有 ' ' 引号。
str() 和 repr() 都是把对象转换为字符串，但 str() 转换的字符串对用户友好， repr() 转换的字符串对python友好。'''



