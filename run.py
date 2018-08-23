# coding=utf-8
import reply
import danmaku
from lyric import lyric_fill
from time import sleep


if __name__ == '__main__':
    aid = 'av360061/?p=112'
    message = '23333'
    """以下是发送评论的部分，测试后记得将评论删除"""
    # 获得某视频的评论
    # rp = reply.get_comment(aid, write=False)
    # for _ in rp:
    #     print(_)

    # 发送评论,获得rpid
    # rpid = reply.send_comment(aid, message)
    # 利用rpid删除评论
    # reply.del_comment(rpid, aid)

    # # 自动定时评论
    # auto_reply(aid, message, '10:53')
    # # 自动点赞
    # auto_action('997646401', url, aid[2:])

    # # 获取视频第一页的评论
    # c = get_comment(aid, 1)
    # for _ in c:
    #     print(_)
    # hots = get_hots(aid)  # 获取热评

    """以下是弹幕的部分"""
    # for _ in range(5):
    #     print(danmaku.get_cid('ep'+str(232170+_)))
    # 在某个视频1p的第20秒发弹幕
    # dmid = danmaku.send(aid, message, video_time='03:10.020', mode=1, color=16646914)
    # print(dmid)
    # 撤回弹幕,每天每个账号只有5次机会
    # danmaku.recall(aid, dmid)
    # 获得某个视频1p的弹幕总数，其他以此类推
    # print(danmaku.get_num(aid))
    # # 获得弹幕发送者的uid及其空间地址
    # dmids, dm, user = danmaku.get_danmaku(aid, user=True)
    # for _ in user:
    #     user_space = danmaku.get_sender(_)
    #     print('https://space.bilibili.com/{}/#/'.format(user_space))
    # 利用弹幕的dmid来举报弹幕
    # dmid = '4040153822658562'
    # danmaku.report(aid, dmid)

    # 获得弹幕数量
    # print(danmaku.get_num(aid))
    # 获得弹幕
    # dmid, dm = danmaku.get_danmaku(aid)
    # 按要求举报弹幕
    # danmaku.clear(aid, dmid, dm)
    # for _ in range(len(dm)):
    #     print(dmid[_], dm[_])
    # 获得弹幕发送者
    # print(danmaku.get_sender())
    dm = danmaku.get_danmaku_info(aid)
    for _ in dm:
        print(_)
    """抢楼的部分"""
    # ep = 'ep232372'
    # first_floor(ep, message, run_time='14:43')

    """补充歌词的部分"""

    # lyric_fill(aid, 29848674, fill=True, translate=True)
    # print(lyric)

