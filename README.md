南京邮电大学程序设计类课程作业平台
======
本系统是基于HUSTOJ二次开发的。特别感谢HUSTOJ的作者和广大贡献者！

如果这个项目对你有用，请挥动鼠标，右上角给个Star!

Star us, please!

[HUSTOJ](https://github.com/zhblue/hustoj/) 是采用GPL的自由软件。

注意：基于本项目源码从事科研、论文、系统开发，"最好"在文中或系统中表明来自于本项目的内容和创意，否则所有贡献者可能会鄙视你和你的项目。使用本项目源码和freeproblemset题库请尊重程序员职业和劳动。

论文请引用参考文献:

[1] [程序设计类课程在线评测教辅系统的设计与实现](http://kns.cnki.net/KCMS/detail/detail.aspx?dbcode=CJFD&dbname=CJFDLAST2018&filename=JYJS201811028&uid=WEEvREcwSlJHSldRa1FhdkJkVG1BdWpzVXFERGxRcjFqTVRFRTlMNHJqZz0=$9A4hF_YAuvQ5obgVAqNKPCYcEjKensW4IQMovwHtwkF4VYPoHbKxJw!!&v=MDgyODViRzRIOW5Ocm85SGJJUjhlWDFMdXhZUzdEaDFUM3FUcldNMUZyQ1VSTE9mWU9adEZ5emdVYjdOTHpUQmY=)

[2] [基于开放式云平台的开源在线评测系统设计与实现](http://kns.cnki.net/KCMS/detail/detail.aspx?dbcode=CJFQ&dbname=CJFD2012&filename=JSJA2012S3088&uid=WEEvREcwSlJHSldRa1FhdXNXYXJwcFhRL1Z1Q2lKUDFMNGd0TnJVVlh4bz0=$9A4hF_YAuvQ5obgVAqNKPCYcEjKensW4ggI8Fm4gTkoUKaID8j8gFw!!&v=MjgwNTExVDNxVHJXTTFGckNVUkwyZlllWm1GaURsV3IvQUx6N0JiN0c0SDlPdnJJOU5iSVI4ZVgxTHV4WVM3RGg=)

PS: GPL保证你可以合法忽略以上注意事项但不能保证你不受鄙视，呵呵。

Ubuntu14.04快速安装指南：

    1、安装Ubuntu Server 14.04 LTS  (本安装尚不支持16.x的Ubuntu系统)
    2、执行如下命令
        wget https://raw.githubusercontent.com/xuejing80/hustoj/master/trunk/install/install-ubuntu14.04.sh
        sudo bash install-ubuntu14.04.sh
    3、执行如下命令，如需配置发送邮件功能，设置143到146行中邮箱账号和密码，数据库密码应该不需要自己手动修改，脚本中会自动替换，如果有问题再手动修改
        wget https://raw.githubusercontent.com/xuejing80/hustoj/master/trunk/install/install-onlineTest.sh
        sudo vi /home/judge/onlineTest/onlineTest/settings.py
        sudo bash install-onlineTest.sh
    4、安装后访问服务器80端口上的web服务
        例如 w3m http://127.0.0.1/
 
推荐用干净的Ubuntu安装，不推荐使用外挂的LAMP或LNMP打包程序，会与安装脚本冲突。
