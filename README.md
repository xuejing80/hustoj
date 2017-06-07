南京邮电大学程序设计类课程作业平台
======
本系统是基于HUSTOJ二次开发的。特别感谢HUSTOJ的作者和广大贡献者！

[HUSTOJ](https://github.com/zhblue/hustoj/) 是采用GPL的自由软件。

注意：基于本项目源码从事科研、论文、系统开发，"最好"在文中或系统中表明来自于本项目的内容和创意，否则所有贡献者可能会鄙视你和你的项目。使用本项目源码和freeproblemset题库请尊重程序员职业和劳动

PS: GPL保证你可以合法忽略以上注意事项但不能保证你不受鄙视，呵呵。

新用户必看 README 和 FAQ

Ubuntu14.04快速安装指南：

    1、安装Ubuntu Server 14.04 LTS  (本安装尚不支持16.x的Ubuntu系统)
    2、执行如下命令
        sudo apt-get update
        sudo apt-get install subversion
        sudo svn co https://github.com/xuejing80/hustoj/trunk/trunk/install hustoj
        cd hustoj
        sudo bash install-interactive.sh
    3、执行如下命令，修改90,91行的数据库账号和密码,如需配置发送邮件功能，设置131到136行中邮箱账号和密码
        sudo vi /var/www/html/onlineTest/onlineTest/settings.py
        sudo bash install-onlineTest.sh
    4、安装后访问服务器80端口上的web服务JudgeOnline目录
        例如 w3m http://127.0.0.1/test/


安装过程首先会询问您数据库的<b>账号和密码</b>

如果您提前安装了数据库，或使用其他服务提供的数据库服务，您应该<b>已经</b>获得了数据库的账号密码，那么请您确保输入正确。

如果您没有预先mysql服务器，安装安装过程中会自动安装，并触发root账户密码设置操作。这种情况下，第一次询问您数据库账号，请输入<b>root</b>,然后会有<b>三次</b>询问数据库密码的提示，请确保输入<b>完全相同的三次密码</b>，并自行<b>记录下来</b>，以做将来备份迁移时使用。
  
推荐用干净的Ubuntu安装，不推荐使用外挂的LAMP或LNMP打包程序，会与安装脚本冲突。
