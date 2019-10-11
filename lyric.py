import requests
import danmaku
from time import sleep


def get_lyric(_id, write=True, translate=False)->[str]:
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
            if _lyric == '':
                continue
        except ValueError:
            continue
        lyric_time.append(_time.strip('['))
        lyric.append(_lyric)

    if translate:
        translation = []
        translated = raw['tlyric']['lyric']  # 翻译的歌词
        # print(translated)
        lines = translated.split('\n')
        for _ in lines:
            try:
                _time, _lyric = _.split(']')
                if _lyric == '':
                    continue
            except ValueError:
                continue
            translation.append(_lyric)
        return lyric_time, lyric, translation

    return lyric_time, lyric


def lyric_fill(aid, song_id, fill=False, translate=False):
    """
    b站视频歌词自动填充的功能

    :param aid: 视频的编号, 包括前缀的字符串
    :param song_id: 要填词的网易云歌曲编号, 如果网易云没有, 这个方法不能使用
    :param fill: 是否发送弹幕, 默认不发送, 可以先检测歌词是否正确再发送
    :param translate: 是否填充翻译的歌词弹幕
    :return: None
    """
    if translate:
        time, lyric, translation = get_lyric(int(song_id), translate=translate)
    else:
        time, lyric = get_lyric(int(song_id))
    """注意这里一开始number是设为1的, 如果因为中断需要重新进行, 需要调整, 并在下一次使用前改正回来"""

    number = 1
    num_offset = 0
    # 在这里设置字幕的颜色
    color = 0x9966FF   # 原版字幕颜色
    color2 = 0xCC66FF  # 翻译字幕的颜色
    skip = True
    for _ in range(len(time)):
        # 如果因为某些原因导致歌词搬运失败, 比如过于频繁等, 需要重新发送时在这里添加过滤的条件
        # if _+num_offset < number-16:
        #     continue
        if fill:
            if number % 10 == 0:
                sleep(20)
        if lyric[_+num_offset] != '':
            print('第{}条弹幕'.format(number))

            if fill:
                if skip:
                    skip = False
                    dmid = '1'
                else:
                    dmid = danmaku.send(aid, lyric[_+num_offset], video_time=time[_+num_offset], mode=4, color=color)
                sleep(10)
                if dmid == '':
                    print('正在重试...')
                    num_offset -= 1
                    sleep(60)
                    continue
                print(time[_+num_offset], lyric[_+num_offset])
                if translate:
                    while True:
                        dmid = danmaku.send(aid, translation[_+num_offset], video_time=time[_+num_offset],
                                            mode=4, color=color2)
                        sleep(10)
                        if dmid != '':
                            sleep(60)
                            break
                        print('正在重试...')
                    print(translation[_+num_offset])

        number += 1


if __name__ == '__main__':
    time, lyric = get_lyric(850775)
    for _ in range(len(time)):
        print(time[_], lyric[_])
