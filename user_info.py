
"""在本地文件user_info里添加或修改必要的信息，例如cookies、csrf、headers"""


# 以下信息请自行补充，并定时更新
cookies = ''
csrf = ''

headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Encoding': 'deflate, br',  # gzip,
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Connection': 'keep-alive',
        'Cookie': cookies,
        'Host': 'api.bilibili.com',
        'Origin': 'https://www.bilibili.com',
        # 'Referer': 'https://www.bilibili.com/video/av'+aid,
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                      '(KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36'
    }

__author__ = 'Wistral'