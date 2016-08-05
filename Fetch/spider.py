# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
from lxml import etree
import pymongo
from collections import deque
import random
import time
import mail163


def login(se):
    info_url_list = ['https://www.linkedin.com/', 'https://www.linkedin.com/uas/login']
    info_url = random.choice(info_url_list)
    r = se.get(info_url)
    soup = BeautifulSoup(r.text, 'lxml')
    loginCsrfParam = soup.find('input', id='loginCsrfParam-login')['value']
    sourceAlias = soup.find('input', id='sourceAlias-login')['value']

    payload = {
        'session_key': '599595429@qq.com',   # 登录账号
        'session_password': 'leoadmir5',         # 登录密码
        'loginCsrfParam': loginCsrfParam,
        'sourceAlias': sourceAlias
    }
    headers_base = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept-Language': 'zh-CN,zh;q=0.8',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.84 Safari/537.36',
        'Host': 'www.linkedin.com',
        'Origin': 'https://www.linkedin.com',
        'Referer': 'https://www.linkedin.com/',
        'Connection': 'keep-alive',
    }
    res1 = se.post('https://www.linkedin.com/uas/login-submit', data=payload, headers=headers_base)
    return res1


# 判断是否仅高级账户可见
def divide():
    try:
        class_nm = selector.xpath('//*[@id="profile"]/div/@class')[0]
        if class_nm == "noticeMsg":     # 仅高级账户可见
            return True
    except:
        return False


# 判断该主页是否有效
def user_exit():
    msg = selector.xpath('//body/@id')[0]
    if msg == 'pagekey-nprofile-public-not-found':  # 无效的网页元素标识
        return False     # 无效
    else:
        return True


# 获取姓名
def get_name():
    try:
        nm = selector.xpath('//*[@id="name"]/h1/span/span/text()')[0]
        profile['name'] = nm

    except:
        mail.send('No Name', 'Do Have A Check ASAP.')
        print '                 Mail Sent: No Name        ' + time.ctime()
        msg = raw_input('Fetch No Name. Enter "con" to Continue:')
        while msg:
            if msg == 'con':
                profile['name'] = 'nonnihono---bt7yh--hiu--++lj+++===---noo=-=557;klnbyfyuf'
                break
            else:
                msg = raw_input('Wrong Input. Enter "con" to Continue:')

        res = login(se=s)
    return profile['name']


# 唯一标识
def get_id():
    try:
        id = selector.xpath('//div[@class="profile-overview-content"]/div/@id')[0][7:]
        profile['memberID'] = id
    except:
        profile['memberID'] = ''
    return profile['memberID']


# 资格认证
def get_cert():
    try:
        cert = selector.xpath('//div[@id="background-certifications"]/div/div/hgroup/h4/a/text()')
    except:
        cert = ''
    profile['cert'] = cert
    return profile['cert']


# 出版作品
def get_pub():
    pub = []
    content_field = selector.xpath('//div[starts-with(@id, "publication")]/div')
    for each in content_field:
        # 作品名称
        name = each.xpath('hgroup/h4//span/text()')[0]
        # 出版社名称
        try:
            press = each.xpath('hgroup/h5/span/text()')[0]
        except:
            press = ''
        # 出版日期
        try:
            date = each.xpath('span[@class="publication-date"]/text()')[0]
        except:
            date = ''
        # 作品描述
        try:
            des = each.xpath('p[@class="description summary-field-show-more"]/text()')[0]
        except:
            des = ''

        pub.append({'book_nm': name, 'press': press, 'date': date, 'des': des})
    profile['pub'] = pub
    return profile['pub']


# 获取头像URL
def get_avatar():
    try:
        ava = selector.xpath('//*[@id="top-card"]/div/div[1]/div[1]//@src')[0]
        profile['avatar'] = ava

    except:
        profile['avatar'] = ''

    return profile['avatar']


# 获取外文名
def get_eng_name():
    try:
        eng_nm = selector.xpath('//*[@id="name"]/h1/span/span/span/text()')[0]
        eng_nm = str(eng_nm)[1:-1].decode()
        profile['eng_name'] = eng_nm

    except:
        profile['eng_name'] = ''

    return profile['eng_name']


# 获取职业头衔
def get_title():
    try:
        tt = selector.xpath('//*[@id="headline"]/p/text()')[0]
        profile['title'] = tt

    except:
        profile['title'] = ''

    return profile['title']


# 所在国家/地区
def get_location():
    try:
        loca = selector.xpath('//*[@id="location"]/dl/dd[1]/span/a/text()')[0]
        profile['location'] = loca
    except:
        profile['location'] = ''
    return profile['location']


# 所属行业
def get_industry():
    try:
        indus = selector.xpath('//*[@id="location"]/dl/dd[2]/a/text()')[0]
        profile['industry'] = indus

    except:
        profile['industry'] = ''

    return profile['industry']


# 目前就职 输出列表
def get_curr_company():
    company = selector.xpath('//*[@id="overview-summary-current"]/td/ol/li//a/text()')
    profile['curr_cpn'] = company
    return company


# 曾经就职 输出列表
def get_prev_company():
    company = selector.xpath('//*[@id="overview-summary-past"]/td/ol/li//a/text()')
    profile['prev_cpn'] = company
    return company


# 个人主页URL
def get_url():
    try:
        url = selector.xpath('//*[@id="top-card"]/div/div[2]//ul/li/dl/dd/a/text()')[0]
        profile['per_url'] = url
    except:
        profile['per_url'] = ''
    return profile['per_url']


# 自我简介
def get_smry():
    summary = ''
    try:
        content = selector.xpath('//*[@id="summary-item-view"]/div/p/text()')
        summary = ''.join(content)

    except:
        pass

    profile['summary'] = summary

    return profile['summary']


# 工作经历
def get_exp():
    exp = []
    content_field = selector.xpath('//div[@id="background-experience"]/div/div')
    for each in content_field:
        # 职位头衔
        try:
            title = each.xpath('header/h4/a/text()')[0]
        except:
            title = ''
        # 任职公司名称
        try:
            company = each.xpath('header/h5//text()')[0]
        except:
            company = ''
        # 任职日期
        try:
            date_and_loca = ''
            dt = each.xpath('span[@class="experience-date-locale"]//text()')
            for d in dt:
                date_and_loca += d
        except:
            date_and_loca = ''

        exp.append({'TITLE': title, 'COMPANY': company, 'DATE&LOCA': date_and_loca})
    profile['exp'] = exp
    return profile['exp']


# 语言能力 输出文本
#
# 形式为：
# 语言 语言水平
#
# 例:
# 英语 高级 (无障碍商务沟通)
# 普通话 高级 (无障碍商务沟通)
# 广东话 母语
def get_lan():
    lan = ''
    n = 1
    try:
        info = selector.xpath('//*[@id="languages-view"]//text()')
        for i in info:
            lan += i
            if n % 2:
                lan += ' '
            else:
                lan += '\n'
            n += 1
        lan = lan.strip()

    except:
        pass

    profile['lan'] = lan

    return profile['lan']


# 技能 输出文本
#
# 格式为：
# 技能:评分
#
# 例：
# 企业运营框架:42
# 心态:41
# 沟通:29
def get_skills():
    skills = ''
    try:
        skill_one = selector.xpath('//*[@id="profile-skills"]/ul[1]/li/@data-endorsed-item-name')
        score_one = selector.xpath('//*[@id="profile-skills"]/ul[1]//span/a/span/text()')
        skill_two = selector.xpath('//*[@id="profile-skills"]/ul[2]/li/@data-endorsed-item-name')
        score_two = selector.xpath('//*[@id="profile-skills"]/ul[2]//div/span/a/span/text()')
        for skill, score in zip(skill_one, score_one):
            skills += skill
            skills += ':'
            skills += score
            skills += '\n'

        for skill, score in zip(skill_two, score_two):
            skills += skill
            skills += ':'
            skills += score
            skills += '\n'
        skills = skills.strip()

    except:
        pass

    profile['skills'] = skills

    return profile['skills']


# 兴趣爱好 输出文本
#
# 格式：
# 爱好一,爱好二,爱好三.(或没有句点)
#
# 示例：
# Basketball,Guitar,Reading.
def get_interest():
    inter = ''
    try:
        items = selector.xpath('//*[@id="interests-view"]/ul//a/text()')
        for item in items:
            inter += item
            inter += ','
        inter = inter[:-1]

    except:
        pass

    profile['interest'] = inter

    return profile['interest']


# 荣誉奖项
def get_honor():
    try:
        hon = selector.xpath('//div[@id="background-honors"]/div/div/div/h4/span/text() | //*[@id="honors-additional-item-view"]/div/p/text()')
    except:
        hon = ''
    profile['honor'] = hon
    return profile['honor']


# 志愿者经历 check
def get_volun():
    vo = []
    content_field = selector.xpath('//div[@id="background-volunteering"]//div[@class="experience"]')
    for each in content_field:
        try:
            role = each.xpath('hgroup/h4/span/text()')[0]
        except:
            role = ''

        try:
            org = each.xpath('hgroup/h5//text()')[0]
        except:
            org = ''

        try:
            date = ''
            dt = each.xpath('span[@class="volunteering-date-cause"]/time/text()')
            if len(dt) == 2:
                date = dt[0] + '-' + dt[1]
            else:
                date = dt[0]
        except:
            date = ''

        try:
            area = each.xpath('span/span[@class="locality"]/text()')[0]
        except:
            area = ''
        vo.append({'ROLE': role, 'ORG': org, 'DATE': date, 'AREA': area})
    profile['volun'] = vo
    return profile['volun']


# 参与组织
def get_org():
    try:
        org = selector.xpath('//div[@id="background-organizations"]//hgroup/h4//a/text() | //*[@id="organization-additional-item-view"]/div/p/a/text()')
    except:
        org = ''
    profile['org'] = org
    return profile['org']


# 联系方式
def get_touch():
    touch = []
    # 推特
    try:
        twitter = selector.xpath('//*[@id="twitter-view"]/ul/li/a/text()')[0]
        touch.append({'TYPE': 'twitter', 'USERNAME': twitter})
    except:
        pass

    # 微信
    try:
        wechat = selector.xpath('//*[@id="wechat-view"]/a/text()')[0]
        touch.append({'TYPE': 'WeChat', 'USERNAME': wechat})
    except:
        pass

    # 个人网站
    try:
        website = selector.xpath('//*[@id="website-view"]/ul/li/a/@href')
        touch.append({'TYPE': 'WEBSITE', 'URL': website})
    except:
        pass

    profile['touch'] = touch
    return profile['touch']


# 教育背景
def get_edu():
    education = []
    content_field = selector.xpath('//div[@id="background-education"]//div[starts-with(@class,"education")]')
    for each in content_field:
        # 学习名称
        try:
            school_nm = each.xpath('header/h4/a/text()')[0]
        except:
            school_nm = ''
        # 专业
        try:
            major = each.xpath('header/h5/span/a/text()')
        except:
            major = ''
        # 学位
        try:
            degree = each.xpath('header/h5//span[@class="degree"]/text()')[0]
        except:
            degree = ''
        # 学习期限
        try:
            date = ''
            dt = each.xpath('span[@class="education-date"]/time/text()')
            for d in dt:
                date += d
        except:
            date = ''
        education.append({'SCHOOL': school_nm, 'MAJOR': major, 'DEGREE': degree, 'DATE': date})
    profile['edu'] = education
    return profile['edu']


# 推荐信
def get_endorse():
    endorse = []    # 收到 + 发出
    giv = []        # 发出的推荐信
    get = []        # 收到的推荐信

    giv_field = selector.xpath('//div[@id="endorsements"]//div[@class="endorsements-given"]/ol/li')
    for each in giv_field:
        # 被推荐人姓名
        try:
            name = each.xpath('div/div[@class="endorsement-info"]/hgroup/h5/span/strong/a/text()')[0]
        except:
            name = ''
        # 被推荐人职位头衔
        try:
            title = each.xpath('div/div[@class="endorsement-info"]/hgroup/h6/text()')[0]
        except:
            title = ''
        # 与被推荐人的关系
        try:
            relation_and_date = each.xpath('div/div[@class="endorsement-info"]/span[@class="endorsement-date"]/text()')[0]
        except:
            relation_and_date = ''
        # 推荐信内容
        try:
            content = each.xpath('div/div[@class="endorsement-info"]/blockquote/p/text()')[0]
        except:
            content = ''

        giv.append({'NAME': name, 'TITLE': title, 'RELA&DATE': relation_and_date, 'CONTENT': content})
    endorse.append(giv)

    get_field = selector.xpath('//div[@id="background-experience"]//dd[@class="associated-endorsements "]/ul/li')
    for each in get_field:
        # 推荐人姓名
        try:
            name = each.xpath('hgroup/h5/span/strong/a/text()')[0]
        except:
            name = ''
        # 推荐人职位头衔
        try:
            title = each.xpath('hgroup/h6/text()')[0]
        except:
            title = ''
        # 推荐信内容
        try:
            content = each.xpath('p[@dir="ltr"]/span/text()')[0]
        except:
            content = ''

        get.append({'NAME': name, 'TITLE': title, 'CONTENT': content})
    endorse.append(get)

    profile['endorse'] = endorse
    return profile['endorse']


# 低级账户可见时
def more_pro():
    get_name()          # 姓名
    get_id()            # 唯一标识memberID
    get_eng_name()      # 外文名
    get_title()         # 职位
    get_curr_company()  # 目前就职
    get_prev_company()  # 曾经就职
    get_location()      # 所在地区
    get_industry()      # 所在行业
    get_avatar()        # 头像URL
    get_url()           # 个人主页URL
    get_smry()          # 自我简介
    get_exp()           # 工作经历
    get_edu()           # 教育背景(详细)
    get_skills()        # 技能
    get_endorse()       # 推荐信

    get_lan()           # 语言能力
    get_cert()          # 资格认证
    get_honor()         # 荣誉奖项
    get_volun()         # 志愿者经历
    get_interest()      # 兴趣爱好
    get_pub()           # 出版作品
    get_org()           # 参与组织
    get_touch()


# 仅对高级账户可见时
# 只抓取: 职位、所在地区、所在行业
def less_pro():
    get_title()
    get_location()
    get_industry()


# 检查cookie
def check_cookie():
    try:
        word = selector.xpath('//section[@id="topcard"]/div[2]/a/@class')[0]
        if word == 'signup-button':     # cookie 过期
            return True
        else:
            return False
    except:
        return False


# 延时函数
def interval():
    if n % 20 == 0:
        print 'rigth now:    ' + time.ctime()

        # PROXY = get_proxy()
    s_inter = 53
    if n % s_inter == 0:
        time.sleep(random.uniform(15, 20))

    l_inter = 199
    if n % l_inter == 0:
        print '------------199*' + str(n / 199) + time.ctime()
        time.sleep(300)
        # msg = raw_input('Enter "con" to Continue:')
        # while msg:
        #     if msg == 'con':
        #         break
        #     else:
        #         msg = raw_input('Wrong Input. Enter "con" to Continue:')

    t_inter = random.uniform(2, 5)
    time.sleep(t_inter)


if __name__ == '__main__':
    conn = pymongo.MongoClient('localhost', 27017)
    profile_db = conn.test_3
    profile_info = profile_db.info

    # 创建mail实例，receiver定义一个邮件接收者
    # 使用mail.send(sub='Sub', content='Content')调用邮件发送函数
    # sub--邮件主题，content--邮件正文
    mail = mail163.Mail(receiver='yiergeadmin@163.com')
    with open('zhao_homepages.txt') as fhome:   # 打开主页保存文件并读取
        urls = fhome.readlines()
    urls = deque(urls)
    s = requests.session()
    global res
    res = login(se=s)

    n = 1
    while urls:

        # 重名链接
        if urls[0][:8] == '/pub/dir':
            print '    Found pub dir: ' + urls[0].strip()
            urls.popleft()
            n += 1
        url = 'https://www.linkedin.com' + urls[0].strip() + '/zh-cn'
        print str(n) + '##crawling:' + url
        # try:
        text = s.get(url, cookies=res.cookies).content
        selector = etree.HTML(text)

        # cookie过期
        if check_cookie():  # cookie过期
            now = time.ctime()
            print 'cookie expired at ' + now
            # urls.appendleft(url)
            mail.send('Check Cookie', 'Cookie Might Has Expired.')
            print '                    Mail Sent: Check Cookie'

            while True:
                if raw_input('Cookie Expired. Enter "con" to Continue:') == 'con':
                    break
            print 'trying to get a new cookie'
            res = login(s)
            text = s.get(url, cookies=res.cookies).content
            selector = etree.HTML(text)

        # 该会员不存在
        if not user_exit():
            print '              User Not Exits..' + url
            urls.popleft()
            continue

        profile = {}
        if divide():
            profile['level'] = 'HIGH'  # 设置标识，仅高级账户可见
            # less_pro()
        else:
            profile['level'] = 'LOW'
            more_pro()
            profile_info.insert(profile)
            urls.popleft()
            n += 1

        interval()

        # except:
        #     print 'Wrong:' + url
        #     urls.popleft()



