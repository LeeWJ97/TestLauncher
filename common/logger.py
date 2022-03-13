import logging,os


path = '../log/'
logfile = 'AllLog.log'
logger = None


formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

if not os.path.exists(path):
    os.mkdir(path)
c = logging.FileHandler(f'{path}/{logfile}', mode='a', encoding='utf8')
logger = logging.getLogger('frame log')
logger.setLevel(logging.DEBUG)
c.setFormatter(formatter)
logger.addHandler(c)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)
logger.addHandler(ch)

# 打印debug级别日志
def debug(str):
    global logger
    try:
        #logger.debug(str)
        print(str)
    except:
        return

# 打印info级别日志
def info(str):
    global logger
    try:
        #logger.info(str)
        print(str)
    except:
        return

# 打印warn级别日志
def warn(str):
    global logger
    try:
        #logger.warning(str)
        print(str)
    except:
        return

# 打印error级别日志，错误日志增加！！！高亮显示
def error(str):
    global logger
    try:
        #logger.error(f'!!! {str}')
        print(str)
    except:
        return

# 打印异常日志，异常日志增加！！！高亮显示
def exception(e):
    global logger
    try:
        #logger.exception(f'!!! {e}')
        print(str)
    except:
        return

# 调试
if __name__ == '__main__':
    debug('test debug')
    info('test info')
    warn('test warn')
    error('test error')
    exception('test exception')


