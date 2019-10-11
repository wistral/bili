# 目前bili中文件及相关函数介绍
### 1. user_info.py
储存必要的信息, 例如:
 - cookies
 - csrf(跨站请求伪造验证)
 - headers其他信息可以自行修改（如果你知道自己要干什么的话）

 **这些信息可以从浏览器评论时抓包获取
 （这里浏览器推荐chrome，可以完成同样功能的其他浏览器也可）
 以下是某次评论抓包的部分headers和data**
 ![](assets/markdown-img-paste-2018081521582033.png)
## **这里只大致的描述功能, 具体使用方法参见代码内文档注释**
### 2. reply.py
关于评论的功能
 - #### send_comment : fa♂评论
 - #### del_comment : 删评论
 - #### ep_2_av : 将ep视频号转成av视频号
 - #### auto_reply : 比较智能地发评论
 - #### auto_action : 自动给评论点赞
 - #### get_comment : 获得视频的评论(不含热评)
 - #### get_hots : 获得视频的热评
 - #### first_floor : 自动抢一楼

### 3. danmaku.py
关于弹幕的功能
- #### get_cid_av : 获取av视频的弹幕池编号
- #### get_cid_ep : 获取ep视频的弹幕池编号
- #### get_cid : 将前两个方法结合成通用的方法
- #### report : 举报弹幕
- #### get_danmaku : 获得某视频的弹幕
- #### recall : 撤回弹幕
- ### send : 发送弹幕
- #### clear : 按照一定的规则举报违规弹幕(未完成)

### 4. lyric.py
关于补充歌词的功能
- #### get_lyric : 获取歌词
- #### lyric_fill : 补充歌词
### 5. run.py
要运行的脚本写在这个文件, 调用其他的脚本中的功能
当然也可以写在别的地方, 写在统一的地方便于更改查看
### 6. bili-cmt-record.txt
记录发送的评论的信息
### 7. bili-dmk-record.txt
记录发送的评论的信息
