# coding=utf-8
import reply
import danmaku


if __name__ == '__main__':
    aid = 'av29870567/?p=1'
    message = '空耳厉害了'
    # url = 'https://www.bilibili.com/video/'+aid
    """以下是发送评论的部分，测试后记得将评论删除"""
    # 获得某视频的评论
    # rp = reply.get_comment(aid, write=False)
    # for _ in rp:
    #     print(_)

    # 发送评论,获得rpid
    # rpid = reply.send_comment(aid, message)
    # 利用rpid删除评论
    # reply.del_comment('1011954064', aid)

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
    # 在某个视频1p的第10秒发弹幕
    # danmaku.send_danmaku(aid, message, video_time=20)

    # 获得某个视频1p的弹幕总数，其他以此类推
    # print(danmaku.get_num_danmaku(aid))

    # 利用弹幕的dmid来举报弹幕
    # dmid = '4000680698183682'
    # danmaku.danmaku_report(aid, dmid)

    # 获得弹幕
    # danmaku = danmaku.get_danmaku_av(aid)
    # for _ in danmaku:
    #     print(_)

    """抢楼的部分"""
    # ep = 'ep232372'
    # first_floor(ep, message, run_time='14:43')

