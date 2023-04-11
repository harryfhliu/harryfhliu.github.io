---
layout:     post
title:      让ChatGPT加持你的word
subtitle:
date:       2023-04-11
author:     沐杰
header-img: img/post-bg-geothermal.jpg
catalog: true
tags:
    - word
    - AI
    - ChatGPT
---

# 让ChatGPT加持你的word

3月16日，微软展示了搭载copilot的Microsoft 365让人眼前一亮，在AI的强力加持下，办公软件的工作效率竟然可以发挥到如此程度。

不过office的copilot还没正式发布，即便发布了也不是每个人都会订阅Microsoft 365，因此如果能通过插件工具将ChatGPT整合到自己的办公软件里也可以一定程度的解渴。

今天发现了一个wordGPT的word插件，可以在一定程度上帮助一二。

位置在这里[https://github.com/filippofinke/WordGPT](https://github.com/filippofinke/WordGPT)

MacOS的安装方式如下：

先关闭word；

在终端输入如下代码：
```
cd ~/Library/Containers/com.microsoft.Word/Data/Documents/wef
wget https://word-gpt-filippofinke.vercel.app/manifest.xml -O wordgpt.xml
```

如果没有wef这个文件夹，就先mkdir创建之；

启动word。

启动后在”插入“-”加载项“里面点一下wordGPT，在”开始“页面就出现这个边栏助手了，一定程度上可以辅助写作。

大概是这个样子，工具栏右边多个了白色的机器人：
![标题](https://raw.githubusercontent.com/harryfhliu/picbed/master/img/202304112048033.png)

第一次使用的时候需要填入你openai账号的api哦。