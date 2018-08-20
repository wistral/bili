# coding=utf-8
import requests
from random import *
import json
import pyquery as pq
from user_info import *
from reply import ep_2_av


__all__ = ['get_cid_av', 'danmaku_report', 'get_danmaku_av', 'get_num_danmaku', 'send_danmaku']


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


def get_cid_ep(ep):  # TODO 有问题，不可用！ 49808781
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


def danmaku_report(av, dmid, reason='10')->bool:  # TODO:有待完善，自动获取cid,dmid
    """利用弹幕编号、dmid等信息举报弹幕

    :param av: 视频番号，av号或者ep号
    :param dmid: 弹幕编号
    :param reason: 举报的理由"""
    url = 'https://api.bilibili.com/x/dm/report/add'

    if av[:2] == 'av':
        referer = 'https://www.bilibili.com/video/'+av
        cid = get_cid_av(av)
    elif av[:2] == 'ep':
        referer = 'https://www.bilibili.com/bangumi/play/'+av
        cid = get_cid_ep(av)[2:]
    else:
        print(av, 'cannot be recognized!')
        return False
    header = headers.copy()
    header['Referer'] = referer  # 'https://www.bilibili.com/bangumi/play/ep232407'  # 视频url
    data = {
        'cid': cid,  # '49075258',  # 视频弹幕池编号
        'dmid': dmid,  # '3672991774801924',  # 弹幕编号
        'reason': reason,  # 举报理由，如下，随序号递增影响、受理速度下降
        #     1.违法违规  2.色情低俗
        #     3.赌博诈骗  4.人身攻击
        #     5.侵犯隐私  6.垃圾广告
        #     7.引战        8.剧透
        #     9.恶意刷屏  10.视频无关
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


def get_danmaku_av(av)->[str]:
    """获取原始的弹幕，返回字符串列表

    :param av: 视频的番号
    :return text: 弹幕列表"""
    cid = get_cid_av(av)
    comment_url = 'https://comment.bilibili.com/'+cid+'.xml'
    response = requests.get(comment_url)
    response.encoding = 'utf-8'
    text = response.text.split('><')[9:][:-1]
    text = [_[4:-3]for _ in text]
    return text


def get_num_danmaku(av, write=False, name='danmaku.txt')->int:  # OK
    """利用cid来获取某个视频的全部弹幕，并写入文件，有待改进，例如记录弹幕的各种属性

    :param av: 视频的cid，纯数字字符串
    :param write: 是否将弹幕写入文件
    :param name: 写入的文件名
    :return int: 最后返回弹幕的总条数，注意是当前的弹幕总数，
    不是历史总数，因为弹幕池有上限
    """
    text = get_danmaku_av(av)
    if write:
        with open(name, 'wb') as f:
            for _ in text:
                """以一条弹幕为例：
                3.21500,1,25,16777215,1534147850,0,8e982cdb,3672991774801924"', '从抖音来
                时间(s)，弹幕类型，字号，弹幕颜色，rnd，未知，未知，弹幕编号"""
                line = _.split('>')
                # info = line[0].split(',')  # 需要弹幕信息的可以从info中处理获得，暂时注释掉
                # 获得方式如下
                # dmid = info[7][:-1]
                # danmaku = line[1][:-3]+'\n'

                f.write((line[0]+'\t'+line[1]+'\n').encode('utf-8'))
    return len(text)


def send_danmaku(aid, msg, video_time=1, color='16777215'):  # OK
    """发送弹幕，目前已实现分p视频的弹幕

    :param aid: 视频的av号或者ep号
    :param msg: 弹幕的内容
    :param video_time: 弹幕在视频中所处的时间，秒为单位，接受*13:30*这种类型的时间
    :param color: 弹幕的颜色，是16进制颜色对应的十进制的值
    :return str: 弹幕的编号"""
    url = 'https://api.bilibili.com/x/v2/dm/post'
    if aid[:2] == 'av':
        oid = get_cid_av(aid)
        referer = 'https://www.bilibili.com/video/'+aid
        aid = aid[2:]
        aid = aid.split('/')[0]
    elif aid[:2] == 'ep':
        oid = '51464722'
        # oid = get_cid_ep(aid)
        referer = 'https://www.bilibili.com/bangumi/play/'+aid
        aid = ep_2_av(aid)[2:]
    else:
        print(aid, 'is ambiguous!')
        return
    if aid == '':
        return
    headers = {
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Content-Length': '300',  # todo:
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Cookie': cookies,
        'Host': 'api.bilibili.com',
        'Origin': 'https://www.bilibili.com',
        'Pragma': 'no-cache',
        'Referer': referer,
        'User-Agent': USER_AGENT
    }

    def time_convert(vt):
        """转换时间成毫秒"""
        if type(video_time) == float or type(video_time) == int:
            return str(int((float(vt) + random()) * 1000))
        if type(video_time) == str:
            if ':' in vt:
                minute, second = vt.split(':')
                return str((int(minute)*60+int(second))*1000)
            else:
                return str(int((float(vt)+random())*1000))
    video_time = time_convert(video_time)
    """rnd似乎是一个随机数字字符串，用来标记用户的，单独一次播放的rnd是不变的"""
    rnd = '153468103050{:04d}'.format(randint(0, 9999))  # 生成rnd
    data = {'type': '1',  # 弹幕类型，还有高级弹幕等
            'oid': oid,  # 弹幕池编号？  51452487
            'msg': msg,
            'aid': aid,  # 视频av号
            'progress': video_time,  # 弹幕出现在视频的多少毫秒
            'color': color,  # 弹幕颜色，默认为白色，对应16进制的0xffffff TODO:改变弹幕颜色未实现
            'fontsize': '25',  # 字体大小，大25，小18
            'pool': '0',
            # 弹幕类型
            # """ 1. 普通弹幕
            #     5. 顶部弹幕rnd"""
            'mode': '1',
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
    else:
        print(dmid['message'])
    try:
        dmid = dmid['data']['dmid']
    except KeyError:
        print('error!')
        return
    # 返回弹幕的id，便于后续的处理
    return dmid

