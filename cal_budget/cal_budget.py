import os
import platform
import inspect
import time

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5 import uic

# C:/Python39/python.exe c:/TimfDev/workspace_py/cal_budget.py 명령어로 수행 
# 카드 영수증 얼마나 있는지 확인하는 로직임

class CalBudget:

    def __init__(self, dialog , ui, **kwargs):
        driver_path = None

        if platform.system() == 'Windows':
            current_folder = os.path.realpath(
                os.path.abspath(os.path.split(inspect.getfile(inspect.currentframe()))[0]))
            driver_path = os.path.join(current_folder, 'chromedriver.exe')
        elif platform.system() == 'Linux':
            current_folder = os.path.dirname(os.path.realpath(__file__))
            driver_path = os.path.join(current_folder, 'chromedriver')

        self.browser = webdriver.Chrome(driver_path)

        self.dialog = dialog
        self.ui = ui

        self.id = kwargs['id']
        self.pw = kwargs['pw']
        self.startDtTt = kwargs['startDtTt']
        self.endDtTt = kwargs['endDtTt']
        self.workBudget = kwargs['workBudget']
        self.diningBudget = kwargs['diningBudget']

    def test(self, **kwargs):
        #ver react
        url = "https://www.bizplay.co.kr/login_0001_01.act"
        id = self.id # 아이디
        pw =  self.pw # 비번

        self.browser.get(url)

        # text로 가져와서 찾을수 있음 
        #El = browser.find_element_by_link_text() 

        time.sleep(1.5)
        userEl = self.browser.find_element_by_id("USER_ID")
        userEl.send_keys(id)

        pwEl = self.browser.find_element_by_id("PWD")
        pwEl.send_keys(pw)
        pwEl.send_keys(Keys.ENTER)

        time.sleep(1.5)

        # // root 
        El = self.browser.find_element_by_xpath("//span[@title='카드영수증']").find_element_by_xpath('..')
        El.click()

        #아 iframe은 좀 기다렸다가... 해야댐 -- 개짜증

        #브라우저를 1번으로 띄워지면 핸들링해야댐
        window_after = self.browser.window_handles[1]
        self.browser.switch_to.window(window_after)

        print("=========================================================================")
        time.sleep(6)
        self.browser.implicitly_wait(5)

        self.browser.switch_to.default_content()
        self.browser.get("https://webank.appplay.co.kr/rcard_main.act")

        # 팝업창 있으면 닫는 로직
        self.browser.switch_to.frame(self.browser.find_element_by_css_selector("iframe[id^='commonLayer']"))
        # print(browser.page_source)
        popupCloseBtn = self.browser.find_element_by_xpath("//button[@class='bt_popClose']")
        popupCloseBtn.send_keys(Keys.ENTER)

        #상세 버튼 클릭
        self.browser.switch_to.default_content()
        self.browser.switch_to.frame("ifrm_page")
        detailBtn = self.browser.find_element_by_xpath("//a[@id='search_detail']")
        detailBtn.click()
        time.sleep(3)

        print(self.startDtTt+"~"+self.endDtTt)
        #값 세팅
        startDt = self.browser.find_element_by_xpath("//input[@id='START_DT']")
        startDt.send_keys(self.startDtTt)

        endDt = self.browser.find_element_by_xpath("//input[@id='END_DT']")
        endDt.send_keys(self.endDtTt)

        cmItem = Select(self.browser.find_element_by_xpath("//select[@id='cmItem_list']"))
        cmItem.select_by_value("00")

        cmItemNm = self.browser.find_element_by_xpath("//input[@id='cmItem_nm']")
        cmItemNm.send_keys("회식비")

        searchBtn =  self.browser.find_element_by_xpath("//a[@class='btn_search_tb tab_index tab_focus1']")
        searchBtn.send_keys(Keys.ENTER)
        time.sleep(2)
        
        diningAmont = int(self.diningBudget) - int(self.browser.find_element_by_xpath("//span[@class='txt_unit fwb totalSum']").find_element_by_xpath("em").text.replace(",", "",3))
        print(self.diningBudget + '/' + self.browser.find_element_by_xpath("//span[@class='txt_unit fwb totalSum']").find_element_by_xpath("em").text.replace(",", "",3))


        cmItemNm.clear()
        cmItemNm.send_keys("업무협의비")
        searchBtn.send_keys(Keys.ENTER)
        time.sleep(2)
        
        workAmout = int(self.workBudget) - int(self.browser.find_element_by_xpath("//span[@class='txt_unit fwb totalSum']").find_element_by_xpath("em").text.replace(",", "",3))
        print(self.workBudget + '/' + self.browser.find_element_by_xpath("//span[@class='txt_unit fwb totalSum']").find_element_by_xpath("em").text.replace(",", "",3))

        self.ui.logUpdate(f'남은 업무협의비 :'+ str(workAmout))
        self.ui.logUpdate(f'남은 회식비 :'+str(diningAmont))