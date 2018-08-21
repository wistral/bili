# coding=utf-8
import requests


def get_lyric(_id, write=False)->[str]:
    """
    获取网易云音乐的歌词

    :param _id: 歌曲的网易云id
    :return: 返回时间和歌词的字符串列表
    """
    # tv: 翻译 kv:
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
    # translated = raw['tlyric']['lyric']  # 翻译歌词
    return lyric_time, lyric
    # for _ in range(len(lyric)):
    #     print(lyric_time[_], lyric[_])


if __name__ == '__main__':
    get_lyric(850775)
