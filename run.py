from bili import *


if __name__ == '__main__':
    aid = 'av29308501'
    message = '2333333'
    url = 'https://www.bilibili.com/video/'+aid
    """发送评论的部分，测试后记得将评论删除"""
    # rpid = send_comment(aid, message)
    # # 利用rpid删除评论
    # del_comment(rpid, aid)

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
    name = '【东方国人社团-優曇華】首作「墨染散華」试听XFD 【上海TH09】.txt'
    danmaku = get_danmaku_av('av29308501')
    for _ in danmaku:
        print(_)

    """抢楼的部分"""
    # ep = 'ep232370'
    # first_floor(ep, message, run_time='14:15')

