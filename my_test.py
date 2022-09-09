# -- coding: utf-8 --
# @Time : 2022/9/1 9:42
# @Author : Liu Hui
# @Email : 1073811240@qq.com
# @File : my_test.py
# @Software: PyCharm
from selenium import webdriver

options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
driver = webdriver.Chrome(chrome_options=options)
driver.get('https:www.baidu.com')
print(driver.title)
driver.close()