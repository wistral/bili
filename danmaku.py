# coding=utf-8
import requests
from random import *
import json
import time
import pyquery as pq
from user_info import *
from reply import ep_2_av, get_time


__all__ = ['get_cid_av', 'get_cid_ep', 'report', 'recall',
           'get_danmaku_info', 'get_num', 'send', 'clear']


def get_cid_av(av)->str:
    """
    用于获得指定视频的cid，有了cid就可以发弹幕、获得弹幕
    目前只能获得普通视频的cid，暂不能获得番剧的cid

    :param av: 视频的av号,含前缀
    :return cid: 纯数字字符串"""
    # 判断是否为多p的av
    MULTI_PAGE = ('?' in av)
    url = 'https://www.bilibili.com/video/' + av
    response = requests.get(url)
    s = response.text
    # 利用pyquery把含有cid的部分从html中提取出来
    doc = pq.PyQuery(s)
    if MULTI_PAGE:
        doc = doc('head')('script')
        s = doc.text()

        def find_n_str(long, short, n):
            """由于cid在s中多次出现，因此需要一个多次匹配的函数"""
            pivot = 0
            position = 0
            for _ in range(n):
                long = long[pivot:]
                pivot = long.index(short) + 1
                position += pivot
            return position - 1

        p = int(av.split('=')[-1])
        pos = find_n_str(s, 'cid', p+2)+5
        s = s[pos:pos+9].split(',')[0]
        return s
    else:
        """下面是原版的，不用修改"""
        doc = doc('body')('#app div')('div')('.player-box')('#arc_toolbar_report div')('#playpage_share div')('.share-popup div')
        # assert doc.text() == ''
        doc = doc('.share-address')('ul')('li')
        doc = doc.items()
        for _ in doc:
            s = str(_('#link2'))
            if s == '':
                continue
            s = s.split('&')[3][8:]
            return s


def get_cid_ep(ep):  # OK
    """ep:视频的ep号，包括前缀"""
    # return '49808781'
    url = 'https://www.bilibili.com/bangumi/play/'+ep
    response = requests.get(url)
    s = response.text
    doc = pq.PyQuery(s)
    doc = doc('script')
    left = doc.text().find('cid')+5
    cid = doc.text()[left:left+10]
    cid = cid.split(',')[0]
    # print(cid)
    return cid


def recall(av, dmid):
    """
    弹幕撤回的功能, 撤回务必在发弹幕后过几秒, 否则间隔过短无法立即撤回. 每天也只有5次撤回的机会, 所以并没有什么用orz

    :param av: 视频番号
    :param dmid: 弹幕的dmid
    :return:
    """
    url = 'https://api.bilibili.com/x/dm/recall'
    cid = get_cid(av)
    if av[:2] == 'av':
        referer = 'https://www.bilibili.com/video/'+av
    else:
        referer = 'https://www.bilibili.com/bangumi/play/' + av
    headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Content-Length': '84',  # todo:
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Cookie': cookies,
        'Host': 'api.bilibili.com',
        'Origin': 'https://www.bilibili.com',
        'Pragma': 'no-cache',
        'Referer': referer,
        'User-Agent': USER_AGENT
    }
    data = {
        'cid': cid,
        'dmid': dmid,
        'jsonp': 'jsonp',
        'csrf': csrf
    }
    response = requests.post(url, headers=headers, data=data)
    text = response.text
    if response.status_code != 200:
        print('弹幕撤回失败, 请求错误！状态码：', response.status_code)
    message = json.loads(text)['message']
    print(message)


def report(aid, dmid, reason='10')->str:
    """利用弹幕编号、dmid等信息举报弹幕

    :param aid: 视频番号，av号或者ep号
    :param dmid: 弹幕编号
    :param reason: 举报的理由
    :return: 举报成功则返回返回码,否则返回None"""
    url = 'https://api.bilibili.com/x/dm/report/add'

    if aid[:2] == 'av':
        cid = get_cid_av(aid)
        referer = 'https://www.bilibili.com/video/'+aid
        aid = aid[2:]
        aid = aid.split('/')[0]
    else:
        cid = get_cid_ep(aid)
        referer = 'https://www.bilibili.com/bangumi/play/' + aid
        aid = ep_2_av(aid)
        # print(aid, 'is ambiguous!')
    if aid == '':
        return ''

    headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Content-Length': '103',  # todo:
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Cookie': cookies,
        'Host': 'api.bilibili.com',
        'Origin': 'https://www.bilibili.com',
        'Pragma': 'no-cache',
        'Referer': referer,
        'User-Agent': USER_AGENT
    }

    data = {
        'cid': cid,  # '49075258',  # 视频弹幕池编号
        'dmid': dmid,  # '3672991774801924',  # 弹幕编号
        'reason': reason,  # 举报理由，如下，随序号递增影响、受理速度下降
        'content': '',
        #     1.违法违规  2.色情低俗
        #     3.赌博诈骗  4.人身攻击
        #     5.侵犯隐私  6.垃圾广告
        #     7.引战        8.剧透
        #     9.恶意刷屏  10.视频无关
        'jsonp': 'jsonp',
        'csrf': csrf
    }
    r = requests.post(url=url, data=data, headers=headers)
    message = r.json()['message']
    code = r.json()['code']

    if code == '0':
        print('弹幕举报成功')
    else:
        print('弹幕举报失败', message)
    return code


def get_raw_danmaku(av):
    """
    获取原始的弹幕，返回字符串列表

    :param av: 视频番号
    :return: 原始弹幕字符串列表
    """
    cid = get_cid(av)
    comment_url = 'https://comment.bilibili.com/'+cid+'.xml'
    response = requests.get(comment_url)
    response.encoding = 'utf-8'
    text = response.text.split('><')[9:][:-1]
    text = [_[4:-3]for _ in text]
    return text


def get_danmaku_info(av, write=False, name=None, user=False)->[str]:
    """
    获得处理后的弹幕, 可以提取弹幕的信息

    :param av: 视频的番号
    :param write: 是否将弹幕信息写入文件
    :param name: 写入的文件名称
    :param user: 是否获取用户信息
    :return text: dmid, 弹幕内容, [用户信息]"""

    text = get_raw_danmaku(av)

    dmids = []
    users = []
    danmaku = []

    for _ in text:
        a, b = _.split('>')
        danmaku.append(b)
        info = a.strip('"').split(',')
        dmids.append(info[-1])
        if user:
            users.append(info[-2])

    text = danmaku
    if write:
        if name is None:
            name = 'danmaku-'+av+'.txt'
        with open(name, 'wb') as f:
            for _ in text:
                """以一条弹幕为例：
                3.21500,1,25,16777215,1534147850,0,8e982cdb,3672991774801924"', '从抖音来
                时间(s)，弹幕类型，字号，弹幕颜色，rnd，未知，用户id加密，弹幕编号"""
                """弹幕出现时间,模式,字体大小,颜色,发送时间戳,弹幕池,用户Hash,数据库ID"""
                line = _.split('>')
                # info = line[0].split(',')  # 需要弹幕信息的可以从info中处理获得，暂时注释掉
                # 获得方式如下
                # dmid = info[7][:-1]
                # danmaku = line[1][:-3]+'\n'

                f.write((line[0]+'\t'+line[1]+'\n').encode('utf-8'))

    if user:
        return dmids, danmaku, users
    return dmids, danmaku


def get_cid(av):
    """
    获取视频cid的通用接口

    :param av: 视频的av, ep, ss号
    :return: 视频的cid
    """
    if av[:2] == 'av':
        return get_cid_av(av)
    else:
        return get_cid_ep(av)


def get_num(av, write=False, name=None)->int:  # OK
    """利用cid来获取某个视频的全部弹幕，并写入文件，有待改进，例如记录弹幕的各种属性

    :param av: 视频的cid，纯数字字符串
    :param write: 是否将弹幕写入文件
    :param name: 写入的文件名
    :return int: 最后返回弹幕的总条数，注意是当前的弹幕总数，
    不是历史总数，因为弹幕池有上限
    """
    text = get_danmaku_info(av, write=write, name=name)
    return len(text[1])


def get_timestamp():
    """
    获取时间戳的函数

    :return: 时间戳的字符串, 16位字符
    """
    s = str(time.time())
    s = s.replace('.', '')[:-1]
    return s


def time_convert(vt)->str:
    """
    转换时间成毫秒字符串

    :param vt: 接受纯数字(单位秒)转成毫秒, 或者'56:28'这种视频X分钟X秒的转换
    :return:
    """
    if type(vt) == float or type(vt) == int:
        return str((float(vt) + randint(2, 100)))
    if type(vt) == str:
        if ':' in vt:
            minute, second = vt.split(':')
            if '.' in second:
                second = second.split('.')
                return str((int(minute)*60+int(second[0]))*1000+int(second[1]))
            else:
                return str((int(minute)*60+int(second))*1000)
        else:
            return str(int((float(vt))*1000)+randint(2, 100))


def send(aid, msg, video_time=1, color=16777215, mode=1)->str:  # OK
    """发送弹幕，目前已实现分p视频的弹幕

    :param aid: 视频的av号或者ep号
    :param msg: 弹幕的内容
    :param video_time: 弹幕在视频中所处的时间，秒为单位，接受*13:30*这种类型的时间
    :param color: 弹幕的颜色，是16进制颜色对应的十进制的值
    :param mode: 弹幕的类型,如滚动弹幕,顶端弹幕,高级弹幕等
    :return str: 弹幕的编号"""
    url = 'https://api.bilibili.com/x/v2/dm/post'
    video_number = aid
    if aid[:2] == 'av':
        oid = get_cid_av(aid)
        referer = 'https://www.bilibili.com/video/'+aid
        aid = aid[2:]
        aid = aid.split('/')[0]
    else:
        oid = get_cid_ep(aid)
        referer = 'https://www.bilibili.com/bangumi/play/' + aid
        aid = ep_2_av(aid)[2:]
        print(aid, 'is ambiguous!')

    assert aid != ''

    headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Content-Length': '300',  # todo:该参数的作用不明
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Cookie': cookies,
        'Host': 'api.bilibili.com',
        'Origin': 'https://www.bilibili.com',
        'Pragma': 'no-cache',
        'Referer': referer,
        'User-Agent': USER_AGENT
    }

    video_time = time_convert(video_time)

    rnd = get_timestamp()  # 获取时间戳
    data = {'type': '1',  # 弹幕类型，还有高级弹幕等
            'oid': oid,  # 弹幕池编号？  51452487
            'msg': msg,
            'aid': aid,  # 视频av号
            'progress': video_time,  # 弹幕出现在视频的多少毫秒
            'color': str(color),  # 弹幕颜色，默认为白色，对应16进制的0xffffff
            'fontsize': '25',  # 字体大小，大25，小18
            'pool': '0',
            # 弹幕类型
            #   1. 普通弹幕
            #   4. 底端弹幕
            #   5. 顶部弹幕
            #
            'mode': str(mode),
            'rnd': rnd,
            'plat': '1',
            'csrf': csrf
            }
    response = requests.post(url=url, headers=headers, data=data)
    text = response.text
    # print(text)
    if response.status_code != 200:
        print('请求错误！状态码：', response.status_code)
    dmid = json.loads(text)
    if dmid['message'] == '0':
        print('弹幕发送成功！')
        try:
            dmid = dmid['data']['dmid']
        except KeyError:
            print('error!')
            return ''

        info = [str(dmid), str(video_number), '['+msg+']', get_time()]
        with open('bili-dmk-record.txt', 'a') as f:
            f.write('\t'.join(info)+'\n')
    else:
        print(dmid['message'])
        return ''
    # 返回弹幕的id，便于后续的处理
    return str(dmid)


def clear(aid, dmids, danmaku):
    """
    按照一定的规则批量举报违规弹幕的方法

    :param aid: 视频号
    :param dmids: 大量弹幕的id
    :param danmaku: 大量弹幕的dmid
    :return: None
    """
    ban = 'VIP,强者,强使遇,強者,钞,会员'.split(',')
    ero = '五毛本,可本,有本,出本,事后,媚药,爱莉'.split(',')
    ad = ['资源']
    report_info = {}
    for _ in range(len(danmaku)):
        for x in ban:
            if x in danmaku[_]:
                report_info[danmaku[_]] = dmids[_]

    for _ in report_info.keys():
        print('举报弹幕', _, report_info[_])
        code = report(aid, report_info[_])
        print(code)
        time.sleep(3)


def get_sender(hash_name='8e982cdb')->int:
    """利用弹幕中的用户加密的信息和解密api获取用户的uid"""
    api = 'http://biliquery.typcn.com/api/user/hash/'+hash_name
    res = requests.get(api)
    user_id = res.json()['data'][0]['id']
    return int(user_id)  # 6933261

