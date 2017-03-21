#coding=utf-8
#模拟登陆成功
#服务器有时候会拒绝我的请求（已解决，这是因为移动访问P站时经常丢包所致

import requests
import re
import time
import random
import os
import zipfile
import TestGif
import shutil

#post登陆数据的地址
loginurl = 'https://accounts.pixiv.net/api/login?lang=zh'
#获取postkey的地址
getpkurl = 'https://accounts.pixiv.net/login?lang=zh&source=pc&view_type=page&ref=wwwtop_accounts_index'
#构造请求头
headers = {
    #'Accept':'application/json, text/javascript, */*; q=0.01',
    #'Accept-Encoding':'gzip, deflate',
    'Accept-Language':'zh-CN,zh;q=0.8',
    #'Connection':'keep-alive',
    #'Content-Length':'114',
    #'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
    #'Host':'accounts.pixiv.net',
    #'Origin':'https://accounts.pixiv.net',
    'Referer':'https://accounts.pixiv.net/login?lang=zh&source=pc&view_type=page&ref=wwwtop_accounts_index',
    'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.75 Safari/537.36'
    #'X-Requested-With':'XMLHttpRequest'
    }

#使用登陆Cookie信息
session = requests.session()

def login(username,password):

    #获取登陆时需要用到的post_key
    '''post_key是一个动态变化的参数'''
    page = session.get(getpkurl,headers=headers)
    #获取页面源码
    html = page.text
    #进行正则匹配
    pattern = r'name="post_key" value="(.*?)"'
    #这里的post_key返回的是一个list，但里面只有一个post_key
    postkey = re.findall(pattern,html)
    pk = postkey[0]
    #print pk

    #构造表单
    postdata = {
        'pixiv_id':username,
        'password':password,
        'captcha':'',
        'g_recaptcha_response':'',
        'post_key':pk,
        'source':'pc',
        }

    session.post(loginurl,data=postdata,headers=headers)
    time.sleep(3)


#具体要哪天的日榜（普通）
def getwhichday(date):

    dailyurl = 'http://www.pixiv.net/ranking.php?mode=daily&date='+date
    f = session.get(dailyurl,headers=headers)
    #print f.text
    print '——————————————————————————————————————————————'


    #获取当天日期
    #date = time.strftime('%Y-%m-%d',time.localtime(time.time()))
    #因为添加了参数，故以你输入的date为文件名
    if os.path.exists(date):
        #切换当前目录
        os.chdir(date)
    else:
        #创建当前日期的文件夹
        os.mkdir(date)
        os.chdir(date)

    #获取id
    for i in range(0,10):
        #因为日榜上的图片可能会被删，此时当前顺位的图会被轮空，故修改正则表达式
        #pattern = 'member_illust\.php\?mode=medium&amp;illust_(id=\d+)&amp;uarea=daily&amp;ref=rn-b-'+str(i)+'-thumbnail-3'
        pattern = 'member_illust\.php\?mode=medium&amp;illust_(id=\d+)&amp;uarea=daily&amp;ref=rn-b-'
        pid = re.findall(pattern,f.text,re.S)
        print pid[i]
        #拼接地址进入图片页面
        downloadurl = 'http://www.pixiv.net/member_illust.php?mode=medium&illust_'+pid[i]
        print downloadurl
        #print 
        r = session.get(downloadurl,headers=headers)
        #暂停3+s
        time.sleep(3+random.randint(3,7))
        #判断是否为动图（特征为源码中是否存在ugokuIllustFullscreenData）
        gif_pattern = 'pixiv.context.ugokuIllustFullscreenData  = {"src":"(.*?zip)"'
        gif = re.findall(gif_pattern,r.text,re.S)
        if len(gif):
            #删除转义字符'\'
            gif[0] = gif[0].replace('\\','')
            print u'这是动图，下载zip'
            filename = pid[i]+'.zip'
            #下载文件
            g = session.get(gif[0],headers=headers,stream=True)
            if g.status_code == 200:
                with open(filename,'wb')as dlg:
                    for chunk in g:
                        dlg.write(chunk)

            images = []
            #新建文件夹来保存解压出来的每帧图片
            if os.path.exists(pid[i]) == None:
                os.mkdir(pid[i])
            fz = zipfile.ZipFile(filename,'r')
            for file in fz.namelist():
                images.append(file)
                fz.extract(file,pid[i]+'/')
            os.chdir(pid[i])
            gifname = pid[i]+'.gif'
            #合成gif
            TestGif.images2gif(images,gifname,durations=0.05)
            if os.path.exists(os.path.abspath('..')+'\\'+gifname):
                os.chdir(os.path.abspath('..'))
                os.remove(gifname)
                os.chdir(pid[i])
                #将gif移动到上级目录
                shutil.move(pid[i]+'.gif',os.path.abspath('..'))
            else:
                shutil.move(pid[i]+'.gif',os.path.abspath('..'))
            #返回上级目录
            os.chdir(os.path.abspath('..'))
            '''发现Image.open()这个方法打开的文件在关闭时存在一些问题，有时候文件列表还没关闭完就执行删除操作了，干脆暴力让它停几秒'''
            time.sleep(10)
            #删除那文件夹
            shutil.rmtree(pid[i])
        
        else:
            o_pattern = r'data-src="(http://i\d\.pixiv\.net/img-original.*?)" class="original-image"'
            temp = re.findall(o_pattern,r.text,re.S)
            if len(temp):
                print u'这是单图'
                print temp
                k = session.get(temp[0],headers=headers,stream=True)
                if k.status_code == 200:
                    with open(pid[i]+'.jpg','wb')as dl:
                        for chunk in k:
                            dl.write(chunk)
            else:
                print u'这是多图'
                tempurl = 'http://www.pixiv.net/member_illust.php?mode=manga&illust_'+pid[i]
                print tempurl
                k = session.get(tempurl,headers=headers)
                m_pattern = 'data-src="(http://i\d\.pixiv\.net/c/1200x1200/img-master/img.*?)"'
                temp = re.findall(m_pattern,k.text,re.S)
                #print temp
                no = 1
                for w in temp:
                    print w
                    j = session.get(w,headers=headers,stream=True)
                    if j.status_code == 200:
                        with open(pid[i]+'_'+str(no)+'.jpg','wb')as dlm:
                            for chunk in j:
                                dlm.write(chunk)
                    no += 1


#具体要哪天的日榜（R-18，并且默认是男性向）
def getwhichdayr18(date):

    dailyurl = 'http://www.pixiv.net/ranking.php?mode=male_r18&date='+date
    f = session.get(dailyurl,headers=headers)
    #print f.text
    print '——————————————————————————————————————————————'

    #date_r18为文件名
    date = date+'_r18'
    if os.path.exists(date):
        #切换当前目录
        os.chdir(date)
    else:
        #创建当前日期的文件夹
        os.mkdir(date)
        os.chdir(date)

    #获取id
    for i in range(0,10):
        pattern = 'member_illust\.php\?mode=medium&amp;illust_(id=\d+)&amp;uarea=male_r18&amp;ref=rn-b-'
        pid = re.findall(pattern,f.text,re.S)
        print pid[i]
        #拼接地址进入图片页面
        downloadurl = 'http://www.pixiv.net/member_illust.php?mode=medium&illust_'+pid[i]
        print downloadurl
        #print 
        r = session.get(downloadurl,headers=headers)
        #暂停3+s
        time.sleep(3+random.randint(3,7))
        #判断是否为动图（特征为源码中是否存在ugokuIllustFullscreenData）
        gif_pattern = 'pixiv.context.ugokuIllustFullscreenData  = {"src":"(.*?zip)"'
        gif = re.findall(gif_pattern,r.text,re.S)
        if len(gif):
            #删除转义字符'\'
            gif[0] = gif[0].replace('\\','')
            print u'这是动图，下载zip'
            filename = pid[i]+'.zip'
            #下载文件
            g = session.get(gif[0],headers=headers,stream=True)
            if g.status_code == 200:
                with open(filename,'wb')as dlg:
                    for chunk in g:
                        dlg.write(chunk)

            images = []
            #新建文件夹来保存解压出来的每帧图片
            if os.path.exists(pid[i]) == None:
                os.mkdir(pid[i])
            fz = zipfile.ZipFile(filename,'r')
            for file in fz.namelist():
                images.append(file)
                fz.extract(file,pid[i]+'/')
            os.chdir(pid[i])
            gifname = pid[i]+'.gif'
            #合成gif
            TestGif.images2gif(images,gifname,durations=0.05)
            if os.path.exists(os.path.abspath('..')+'\\'+gifname):
                os.chdir(os.path.abspath('..'))
                os.remove(gifname)
                os.chdir(pid[i])
                #将gif移动到上级目录
                shutil.move(pid[i]+'.gif',os.path.abspath('..'))
            else:
                shutil.move(pid[i]+'.gif',os.path.abspath('..'))
            #返回上级目录
            os.chdir(os.path.abspath('..'))
            '''同理'''
            time.sleep(10)
            #删除那文件夹
            shutil.rmtree(pid[i])
        
        else:
            o_pattern = r'data-src="(http://i\d\.pixiv\.net/img-original.*?)" class="original-image"'
            temp = re.findall(o_pattern,r.text,re.S)
            if len(temp):
                print u'这是单图'
                print temp
                k = session.get(temp[0],headers=headers,stream=True)
                if k.status_code == 200:
                    with open(pid[i]+'.jpg','wb')as dl:
                        for chunk in k:
                            dl.write(chunk)
            else:
                print u'这是多图'
                tempurl = 'http://www.pixiv.net/member_illust.php?mode=manga&illust_'+pid[i]
                print tempurl
                k = session.get(tempurl,headers=headers)
                m_pattern = 'data-src="(http://i\d\.pixiv\.net/c/1200x1200/img-master/img.*?)"'
                temp = re.findall(m_pattern,k.text,re.S)
                #print temp
                no = 1
                for w in temp:
                    print w
                    j = session.get(w,headers=headers,stream=True)
                    if j.status_code == 200:
                        with open(pid[i]+'_'+str(no)+'.jpg','wb')as dlm:
                            for chunk in j:
                                dlm.write(chunk)
                    no += 1

####################################################################
if __name__ == '__main__':
    print u'请输入用户名'
    username = raw_input('username:')
    print u'请输入密码'
    password = raw_input('password:')
    login(username,password)
    print u'请输入要获取哪日的榜单'
    print u'格式如20160901，注意只能获取前一天的，因为当天的日榜要等明天才出'
    date = raw_input('date:')
    print u'想要普通的还是R-18的，想要输y，不要输n'
    r18 = raw_input('r18:')
    if r18 == 'y':
        getwhichdayr18(date)
    else:
        getwhichday(date)
