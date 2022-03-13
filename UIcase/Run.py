from driver.commonUI import UI
from common import excel
import threading

def login(url,username,password,company,rootpath,type,proxy,proxyipport):
    browserdict = {
        '1':'Chrome',
        '2':'FF',
        '3':'Edge',
        '4':'IE'
    }
    type = browserdict[str(type)]
    ui = UI(username, password,company,url,type=type,proxy=proxy,proxyipport=proxyipport,count=500,holdpage=True,rootpath=rootpath)


def run(rownumlist,type='Chrome',proxy=False,proxyipport='127.0.0.1:8080',rootpath='.'):
    try:
        e = excel.Excel(rf'{rootpath}/data/data.xlsx','account')
        row = rownumlist
        for i in row:
            i = int(i)
            url = e.read(i,1)
            username = e.read(i,2)
            password = e.read(i,3)
            company = e.read(i,4)
            thread = threading.Thread(target=login, args=(url,username,password,company,rootpath,type,proxy,proxyipport))
            thread.start()
    except Exception as e:
        print(e)
        try:
            import tkinter.messagebox
            tkinter.messagebox.showerror('Error', e)
        except:
            pass
        return