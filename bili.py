import requests
import http
import urllib
import json
import time
import pyquery as pq
import schedule
from user_info import *


# 声明一个CookieJar对象实例来保存cookie
cj = http.cookiejar.CookieJar()
# 利用urllib库中的request的HTTPCookieProcessor对象来创建cookie处理器
cp = urllib.request.HTTPCookieProcessor(cj)
# 使用创建的cookie处理器来创建一个opener
opener = urllib.request.build_opener(cp)
# 使用自定义的opener来模拟浏览器操作
urllib.request.install_opener(opener)


def send_comment(aid, message, write=True) -> str:  # ok
    """通过模拟浏览器请求来完成对指定视频的评论发送,并在本地记录相关信息\n
    aid:视频的av号，纯数字字符串\n
    message:评论的内容，字符串，可以包含转义字符\n
    write：是否在本地文件中记录评论信息"""
    if aid[:2] == 'av':
        aid = aid[2:]
    comment = {
        'oid': aid,
        'type': '1',
        'message': message,
        'plat': '1',
        'jsonp': 'jsonp',
        'csrf': csrf
    }
    # 这个是发评论的接口，只要成功向这个接口发送data即可发送评论
    url = 'https://api.bilibili.com/x/v2/reply/add'
    post_data = urllib.parse.urlencode(comment).encode('utf-8')

    try:
        request = urllib.request.Request(url, headers=headers, data=post_data)
        # 使用自定义opener中的open方法来请求
        response = opener.open(request)
        # 以utf-8的编码来读取response的内容
        raw_data = response.read().decode('utf-8')
        # 转换成json数据（类似于字典）
        raw_data = json.loads(raw_data)
    except urllib.error.URLError as e:
        print(e)
        print('请求失败！')
        exit(1)
    # 从json数据中提取rpid(评论的编号)

    rpid = raw_data['data']['rpid']
    if write:
        # 记录时间
        local_time = time.localtime()
        time_str = '{}'.format(local_time[0])
        for i in range(5):
            time_str += '-' + str(local_time[i + 1]).zfill(2)
        with open('bili-cmt-record.txt', 'ab') as f:
            # 向文件中写入相关信息，一些其他的操作(删除，回复评论)需要用到这些信息
            s = str(rpid)+'\tav'+aid+'\t【'+message+'】\t'+time_str+'\n'
            # 注意中文字符要以utf-8的编码写入，否则打开会变成乱码
            f.write(s.encode('utf-8'))
            print(s)
            print('评论记录成功！')
    print('评论发送成功！')
    return rpid


def del_comment(rpid, aid)->bool:  # ok
    """通过模拟浏览器请求来完成评论的删除，和上面的类似\n
    rpid：评论的编号，不是楼层号，纯数字字符串\n
    aid：视频的av号，纯数字字符串"""
    if aid[:2] == 'av':
        aid = aid[2:]
    url = 'https://api.bilibili.com/x/v2/reply/del'
    comment = {
        'oid': aid,
        'type': '1',
        'rpid': rpid,
        'jsonp': 'jsonp',
        'csrf': csrf
    }
    postdata = urllib.parse.urlencode(comment).encode('utf-8')
    # cj = http.cookiejar.CookieJar()
    # opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    # urllib.request.install_opener(opener)

    try:
        request = urllib.request.Request(url, headers=headers, data=postdata)
        response = opener.open(request)
        raw_data = response.read().decode('utf-8')
        raw_data = json.loads(raw_data)
        message = raw_data['message']
        if message == '0':
            print('评论删除成功！')
        else:
            print(message)
    except urllib.error.URLError as e:
        print(e)
        print('评论删除失败!')
        return False

    return True


def danmaku_report(cid, dmid, referer, reason='10')->bool:  # TODO:有待完善，自动获取cid,dmid
    """利用弹幕编号、dmid等信息举报弹幕\n
    cid：视频弹幕池编号\n
    dmid：弹幕编号\n
    referer:视频播放页地址\n
    reason：举报的理由"""
    url = 'https://api.bilibili.com/x/dm/report/add'
    header = headers.copy()
    header['Referer'] = referer  # 'https://www.bilibili.com/bangumi/play/ep232407'  # 视频url
    data = {
        'cid': cid,  # '49075258',  # 视频弹幕池编号
        'dmid': dmid,  # '3672991774801924',  # 弹幕编号
        'reason': reason,  # 举报理由，如下，随序号递增影响、受理速度下降
        """ 1.违法违规  2.色情低俗
            3.赌博诈骗  4.人身攻击
            5.侵犯隐私  6.垃圾广告
            7.引战        8.剧透
            9.恶意刷屏  10.视频无关"""
        'jsonp': 'jsonp',
        'csrf': csrf
    }
    r = requests.post(url, data=data, headers=header)
    print(r.json()['message'])
    if r.status_code == 200:
        print('弹幕举报成功')
        return True
    else:
        print('弹幕举报失败')
        return False


def ep_2_av(ep, times_=200)->str:  # ok
    """给定视频的ep号，返回对于的av号，用于发送评论等\n
    ep:ep号，开头为ep之后是纯数字的字符串，例如‘ep232536’"""
    url = 'https://www.bilibili.com/bangumi/play/'+ep
    headers_ = headers.copy()
    headers_['Host'] = 'www.bilibili.com'
    headers_['Referer'] = 'https://t.bilibili.com/pages/nav/index'
    headers_['Upgrade - Insecure - Requests'] = '1'
    times = 1
    """如果404则暂停一段时间再继续请求"""
    while True:
        while True:
            response = requests.get(url, headers=headers_)
            if response.status_code == 404:
                print('正在重试...第{}次'.format(times), end='\r')
                if times == times_:
                    return ''
                times += 1
                time.sleep(.5)
            elif response.status_code == 200:
                break
        html = response.text
        doc = pq.PyQuery(html)
        doc = doc('body')
        doc = doc('#bangumi_header .header-info div')('.info-second')('.info-sec-av')
        # 关键是获得一个视频的oid，得到后就可以利用api发送评论了
        oid = doc.text()[2:]  # 这里要去掉前缀的两个字母
        if oid == '':
            """每0.5秒重试一次，频率过高可能会被封ip"""
            print('正在重试...第{}次'.format(times), end='\r')
            times += 1
            time.sleep(.5)
            continue
        else:
            return oid


def auto_reply(ep, message, times):  # ok
    """自动在指定的视频下发送评论\n
    ep:视频的av号或者ep号\n"""
    if ep[:2] == 'ep':
        oid = 'av' + ep_2_av(ep, times)
        if oid == '':
            return
    elif ep[:2] == 'av':
        oid = ep
    else:
        print(ep, '的格式错误！')
        return
    rpid = send_comment(oid, message)
    print('自动评论发送成功！')
    print(rpid)
    return


def auto_action(rpid, referer, oid, action='1')->bool:  # ok
    """自动给评论点赞，\n
    rpid：需要点赞的评论编号\n
    referer：评论页面的url\n
    oid：视频的av号\n
    action: 如果action是'2'就取消点赞"""
    url = 'https://api.bilibili.com/x/v2/reply/action'
    headers_ = headers.copy()
    headers_['Host'] = 'api.bilibili.com'
    headers_['Referer'] = referer
    headers_['Upgrade - Insecure - Requests'] = '1'
    if oid[:2] == 'av':
        oid = oid[2:]
    if action == '1':
        behavior = ''
    else:
        behavior = '取消'
    data = {
        'oid': oid,  # 此处oid与referer中的数字并不总是统一的，所以要单独传入
        'type': '1',  # 不变
        'rpid': rpid,  # 评论编号
        'action': action,  # 点赞, '0' 表示取消点赞
        'jsonp': 'jsonp',
        'csrf': csrf
    }
    # print(referer)
    postdata = urllib.parse.urlencode(data).encode('utf-8')

    try:
        request = urllib.request.Request(url, headers=headers, data=postdata)
        # 这里使用全局的opener
        response = opener.open(request)
        raw_data = response.read().decode('utf-8')
        raw_data = json.loads(raw_data)
        message = raw_data['message']
        if message == '0':
            print('评论' + behavior + '点赞成功！')
        else:
            print(message)
    except urllib.error.URLError as e:
        print(e)
        print('评论'+behavior+'点赞失败!')
        return False

    return True


def get_comment(aid, page=1, write=True)->[str]:
    """获得指定视频的评论
    aid:视频av号
    page：第page页的评论"""
    if aid[:2] == 'av':
        aid = aid[2:]
    url = 'https://api.bilibili.com/x/v2/reply?pn={}&type=1&oid='.format(page)+aid
    req = requests.get(url=url)
    json_ = req.text
    raw_data = json.loads(json_)
    # s = json_.encode('utf-8')

    # acount = raw_data['data']['page']['acount']  # 当前的总评论数，包括楼中楼
    replies = []

    for _ in range(20):
        replies.append(raw_data['data']['replies'][_]['content']['message'])
    if write:
        with open('comment-' + 'av' + aid + '.txt', 'wb') as f:
            for _ in replies:
                f.write((_+'\n').encode('utf-8'))
    return replies


def get_hots(aid, write=True)->[str]:
    """获得视频的热评，\n
    aid：视频的av号"""
    if aid[:2] == 'av':
        aid = aid[2:]
    url = 'https://api.bilibili.com/x/v2/reply?pn=1&type=1&oid='+aid
    req = requests.get(url=url)
    json_ = req.text
    raw_data = json.loads(json_)
    # 以下是热评的部分
    hots = raw_data['data']['hots']
    hots = [_['content']['message'] for _ in hots]
    return hots


def get_cid_av(av)->str:
    """用于获得指定视频的cid，有了cid就可以发弹幕、获得弹幕\n
    av:视频的av号,含前缀\n
    返回cid，纯数字字符串"""
    url = 'https://www.bilibili.com/video/' + av
    response = requests.get(url)
    s = response.text
    # 利用pyquery把cid从html中解析出来
    doc = pq.PyQuery(s)
    doc = doc('body')('#app div')('.player-box')('#arc_toolbar_report div')('#playpage_share div')('.share-popup div')
    doc = doc('.share-address')('ul')('li').items()
    for _ in doc:
        s = str(_('#link2'))
        if s == '':
            continue
        s = s.split('&')[3][8:]
        return s


def get_danmaku_av(av)->[str]:
    """获取原始的弹幕，返回字符串列表"""
    cid = get_cid_av(av)
    comment_url = 'https://comment.bilibili.com/'+cid+'.xml'
    response = requests.get(comment_url)
    response.encoding = 'utf-8'
    text = response.text.split('><')[9:][:-1]
    text = [_[4:-3]for _ in text]
    return text


def get_num_danmaku(av, write=True, name='danmaku.txt')->int:
    """利用cid来获取某个视频的全部弹幕，并写入文件，有待改进，例如记录弹幕的各种属性，目前ok\n
    cid:视频的cid，纯数字字符串
    write：是否将弹幕写入文件
    name：写入的文件名
    最后返回弹幕的总条数，注意是当前的弹幕总数，不是历史总数，因为弹幕池有上限
    """
    cid = get_cid_av(av)  # 获取cid
    text = get_danmaku_av(cid)
    if write:
        with open(name, 'wb') as f:
            for _ in text:
                """以一条弹幕为例：
                3.21500,1,25,16777215,1534147850,0,8e982cdb,3672991774801924"', '从抖音来
                时间(s)，弹幕类型，字号，未知，rnd（未知），颜色，未知，弹幕编号"""
                line = _.split('>')
                # info = line[0].split(',')  # 需要弹幕信息的可以从info中处理获得，暂时注释掉
                # 获得方式如下
                # dmid = info[7][:-1]
                # danmaku = line[1][:-3]+'\n'

                f.write((line[0]+'\t'+line[1]+'\n').encode('utf-8'))
    return len(text)


def first_floor(ep, message, run_time='22:23', max_times=200):
    """为了更加自动的实现在指定时间段的抢楼，使用轻量的schedule实现定时任务\n
    用于实现自动在未来预测的某个视频下抢楼，抢楼是违规行为，\n
    这里仅用于学习，请勿用于非法！
    ep：视频的av号或者ep号\n
    message：评论的内容\n
    run_time：发送的时间，如果失败会重试\n
    max_times：最大尝试次数，默认为200次"""
    second = 0
    # 程序第一次运行到这里会添加一个定时任务，不会立刻运行
    # 这里默认设置为每天的22:59执行auto_reply函数
    schedule.every().day.at(run_time).do(auto_reply, ep, message, max_times)
    while True:
        """这里用一个死循环每隔一秒检查条件是否满足，满足则执行之前添加的定时任务
        这里脚本刚运行时会被挂起，直到本地时间到run_time自动去执行任务"""
        print('\r等待中......已等待{}秒'.format(second), end='')
        schedule.run_pending()
        time.sleep(1)
        second += 1

