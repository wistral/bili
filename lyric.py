import requests
import danmaku
from time import sleep


def get_lyric(_id, write=True)->[str]:
    """
    获取网易云音乐的歌词

    :param _id: 歌曲的网易云id
    :param write: 是否将歌词写入本地文件
    :return: 返回时间和歌词的字符串列表
    """
    # 网易云获取歌词的接口
    api = 'http://music.163.com/api/song/lyric?'+'id='+str(_id)+'&lv=1&kv=1&tv=-1'
    res = requests.get(api)
    raw = res.json()

    raw_lyric = raw['lrc']['lyric']

    if write:
        with open('lyric-{}.txt'.format(_id), 'wb') as f:
            f.write(str(raw_lyric).encode('utf-8'))

    lyric_time = []
    lyric = []
    lines = raw_lyric.split('\n')
    for _ in lines:
        try:
            _time, _lyric = _.split(']')
        except ValueError:
            continue
        lyric_time.append(_time.strip('['))
        lyric.append(_lyric)
    # translated = raw['tlyric']['lyric']  # 翻译的歌词
    # for _ in range(len(lyric)):
    #     print(lyric_time[_], lyric[_])
    return lyric_time, lyric


def lyric_fill(aid, song_id, fill=False):
    """
    b站视频歌词自动填充的功能

    :param aid: 视频的编号, 包括前缀的字符串
    :param song_id: 要填词的网易云歌曲编号, 如果网易云没有, 这个方法不能使用
    :param fill: 是否发送弹幕, 默认不发送, 可以先检测歌词是否正确再发送
    :return: None
    """
    time, lyric = get_lyric(int(song_id))
    number = 1
    for _ in range(len(time)):
        # 如果因为某些原因导致歌词搬运失败, 比如过于频繁等, 需要重新发送时在这里添加过滤的条件
        # if _ < 13 or _ > 26:
        #     continue
        if lyric[_] != '':
            print('第{}条弹幕'.format(number), time[_], lyric[_])
            if fill:
                danmaku.send(aid, lyric[_], video_time=time[_], mode=4, color=16646914)
                sleep(10)
            number += 1


if __name__ == '__main__':
    time, lyric = get_lyric(850775)
    for _ in range(len(time)):
        print(time[_], lyric[_])
