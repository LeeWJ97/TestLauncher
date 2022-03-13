import os,threading
import traceback,time
import psutil

from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.ie.options import Options as IEOptions
from common import logger

class UI():
    def __init__(self,username,password,companyname,
                 url,headless=False,
                 count=5000,refresh_count=500,type='Chrome',proxy=False,proxyipport='127.0.0.1:8080',holdpage=False,rootpath='..'):
        self.initcount = count
        self.count = count
        self.username = username
        self.password = password
        self.companyname = companyname
        self.url = url
        self.headless = headless
        self.type = type
        self.proxy = proxy
        self.holdpage = holdpage
        self.rootpath = rootpath
        self.proxyipport = proxyipport
        try:
            self.auth(refresh_count)
        except Exception as e:
            print(e)
            try:
                import tkinter.messagebox
                tkinter.messagebox.showerror('Error', e)
            except:
                pass



    def auth(self,refresh_count):
        refresh_count_mark = refresh_count
        if self.type == 'IE':
            ie_options = IEOptions()
            ie_options.ignore_protected_mode_settings = True   #忽略IE保护模式
            ie_options.ignore_zoom_level = True   #忽略IE缩放带来的错误，但是如果实际IE缩放不是100%，可能会点不对坐标
            ie_options.initial_browser_url = self.url   # 解决可能出现的NoSuchWindowException: Unable to find element on closed报错

            #ie_options.require_window_focus = True   #点击元素时是否需要鼠标移动到元素上
            #ie_options.persistent_hover = True     #是否允许持久性hover

            self.driver = webdriver.Ie(rf'{self.rootpath}/webdriver/IEDriverServer.exe',options=ie_options)

        elif self.type == 'FF':
            self.driver = webdriver.Firefox(executable_path=rf'{self.rootpath}/webdriver/geckodriver.exe')
        elif self.type == 'Edge':
            self.driver = webdriver.Edge(rf'{self.rootpath}/webdriver/msedgedriver.exe')


        else:
            chrome_options = Options()
            if self.headless == True:
                chrome_options.add_argument("--headless")
            if self.proxy == True:
                logger.info('启动代理！！！！！！！！！！')
                chrome_options.add_argument(f'--proxy-server=http://{self.proxyipport}')
            chrome_options.add_experimental_option('useAutomationExtension', False)
            chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
            self.driver = webdriver.Chrome(rf'{self.rootpath}/webdriver/chromedriver.exe',chrome_options=chrome_options)

        t = threading.Thread(target=self.check_browser,args=())
        t.start()
        #print(self.url)
        self.driver.maximize_window()
        self.driver.get(self.url)
        while 1:
            try:
                self.driver.find_element_by_xpath("//*[@id='userName']")
                break
            except Exception as e:
                if ('Currently focused window has been closed' in str(e)) or ('NoSuchWindowException' in str(e))or ('chrome not reachable' in str(e)):
                    print('Currently focused window has been closed')
                    return
                time.sleep(0.5)
                logger.info(f'{refresh_count}未检测到登录框')
                #print(e)
                refresh_count -= 1
                if refresh_count <= 0:
                    logger.info(f'{refresh_count}刷新登录页')
                    self.driver.get(self.url)
                    refresh_count = refresh_count_mark

        self.inputele("//*[@id='userName']",self.username)
        self.inputele("//*[@id='password']",self.password)
        self.inputele("//*[@id='companyName']",self.companyname)
        self.clickele("//button")
        while self.holdpage:
            time.sleep(10)

    #检查浏览器是否被手工杀掉，如是则结束driver进程
    def check_browser(self):
        print('check browser pid')
        driver = self.getdriver()
        try:   #init check pid
            if self.type == "Edge":
                print(self.type)
                psutil.Process(driver.edge_service.process.pid)
            elif self.type == "IE":
                print(self.type)
                psutil.Process(driver.iedriver.process.pid)
            else:
                psutil.Process(driver.service.process.pid)
        except:
            print("get pid failed")
            return
        while 1:
            try:
                if self.type == "Edge":
                    driver_process = psutil.Process(driver.edge_service.process.pid)
                elif self.type == "IE":
                    driver_process = psutil.Process(driver.iedriver.process.pid)
                else:
                    driver_process = psutil.Process(driver.service.process.pid)

                #print(driver_process)
                if driver_process.is_running():
                    #print(f"driver is running, pid: {driver_process}")

                    browser_process = driver_process.children()

                    if browser_process:
                        #print(browser_process)
                        browser_process = browser_process[1]

                        if browser_process.is_running():
                            #print(f"broswer is running, pid: {browser_process}")
                            pass
                        else:
                            print("Browser is dead. Quit the driver.")
                            self.holdpage = 0
                            driver.quit()
                            return
                    else:
                        print("driver has died")
                        self.holdpage = 0
                        driver.quit()
                        return
                time.sleep(10)
            except:
                print('pid is missed')
                self.holdpage = 0
                driver.quit()
                return


    def getdriver(self):
        return self.driver

    def tryit(self, exec):
        driver = self.driver
        while 1:
            try:
                ele = eval(exec)
                return ele
            except Exception as e:
                logger.info(
                    f'---------------------------------出错{self.count}：{exec}\n\n\n{traceback.format_exc()}\n\n---------------------------------')
                time.sleep(0.5)
                self.count -= 1
                if not self.count:
                    logger.error(
                        f'---------------------------------超过容忍次数出错{self.count}：{exec}\n\n\n{traceback.format_exc()}\n\n---------------------------------')
                    time.sleep(0.5)
                    raise Exception

    def tryit_w(func):
            def wrapper(self, *args, **kwargs):
                while 1:
                    try:
                        returnfunc =  func(self, *args, **kwargs)
                        self.count = self.initcount
                        return returnfunc

                    except Exception as e:
                        if ('Currently focused window has been closed' in str(e)) or ('NoSuchWindowException' in str(e))or ('chrome not reachable' in str(e)):
                            print('Currently focused window has been closed')
                            return
                        logger.info(
                            f'---------------------------------出错{self.count}：{args}\n\n\n{traceback.format_exc()}\n\n---------------------------------')
                        time.sleep(0.5)
                        self.count -= 1
                        if not self.count:
                            logger.error(
                                f'---------------------------------超过容忍次数出错{self.count}：{args}\n\n\n{traceback.format_exc()}\n\n---------------------------------')
                            time.sleep(999999)
            return wrapper

    def catch_exception(origin_func):
        def wrapper(*args, **kwargs):
            try:
                u = origin_func(*args, **kwargs)
                return u
            except Exception:
                return 'an Exception raised.'

        return wrapper

    def assertstr(self,acutal,expect,pass_comment='',fail_comment=''):
        if acutal == expect:
            logger.info(f'[PASS] {acutal} = {expect}  {pass_comment}')
        else:
            logger.info(f'[FAIL] {acutal} != {expect}  {fail_comment}')

    def screenshot(self,savepath,filename):
        try:
            if not os.path.exists(savepath):
                os.mkdir(savepath)
            self.driver.save_screenshot(rf'{savepath}\{filename}')
            logger.info(f'截图成功，路径为：{savepath}\{filename}')
        except Exception as e:
            logger.info(f'[FAIL to save screenshot] {str(e)}')

    @tryit_w
    def getele(self, xpath, index = 0):
        driver = self.driver
        self.ele = driver.find_elements_by_xpath(xpath)[index]
        logger.info(f'成功获取元素：{xpath} ，index为{index}')
        return self.ele

    @tryit_w
    def geteles(self, xpath):
        driver = self.driver
        self.eles = driver.find_elements_by_xpath(xpath)
        logger.info(f'成功获取元素elements列表：{xpath},列表长度为{len(self.eles)}，详情：{self.eles}')
        return self.eles

    @tryit_w
    def clickele(self, xpath, index=0):
        driver = self.driver
        self.ele = driver.find_elements_by_xpath(xpath)[index]
        self.ele.click()
        logger.info(f'成功点击元素：{xpath} ，index为{index}')
        return self.ele

    #js点击
    @tryit_w
    def jsclickele(self, xpath, index=0):
        driver = self.driver
        self.ele = driver.find_elements_by_xpath(xpath)[index]
        driver.execute_script(f"arguments[0].click();", self.ele);
        logger.info(f'成功js点击元素：{xpath} ，index为{index}')
        return self.ele

    #js脚本
    @tryit_w
    def js(self, script):
        driver = self.driver
        driver.execute_script(script);
        logger.info(f'成功执行js：{script} ')
        return self.ele

    @tryit_w
    def inputele(self, xpath, key='',index=0):
        driver = self.driver
        self.ele = driver.find_elements_by_xpath(xpath)[index]
        self.ele.send_keys(key)
        logger.info(f'成功向元素 {xpath} 输入文本：{key}，index为{index}')
        return self.ele


    @tryit_w
    def getelesinnerHTML(self, xpath):
        self.ele = self.geteles(xpath)
        return_list = list()
        for i in self.ele:
            return_list.append(i.get_attribute('innerHTML'))
        logger.info(f"成功获取元素 {xpath} 的innerHTML，该返回是所有符合xpath的innerHTML列表，请自行遍历")
        return return_list

    @tryit_w
    def geteletext(self, xpath, index=0):
        driver = self.driver
        self.ele = driver.find_elements_by_xpath(xpath)[index]
        logger.info(f'成功获取元素 {xpath} 的文本：{self.ele.text}，index为{index}')
        return self.ele.text

    @tryit_w
    def movetoele(self,xpath,index=0):
        driver = self.driver
        self.ele = driver.find_elements_by_xpath(xpath)[index]
        ActionChains(driver).move_to_element(self.ele).perform()
        logger.info(f'成功悬浮元素 {xpath} ：{self.ele.text}，index为{index}')
        return self.ele

    @tryit_w
    def getdriver(self):
        return self.driver

    @tryit_w
    def iframe(self,index):
        driver = self.driver
        driver.switch_to.frame(index)
        return self.driver

    @tryit_w
    def switch_to_default(self):
        driver = self.driver
        driver.switch_to.default_content()
        return self.driver





