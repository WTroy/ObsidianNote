---
title: CentOS7 firewalld的基本使用
source: 有道云笔记
imported: true
---

1 、 firewalld 的基本使⽤
启动：  systemctl start firewalld
查看状态：  systemctl status firewalld
停⽌：  systemctl disable firewalld
禁⽤：  systemctl stop firewalld
2.systemctl 是 CentOS7 的服务管理⼯具中主要的⼯具，它融合之前 service 和 chkconfig 的功能于⼀体。
启动⼀个服务： systemctl start firewalld.service
关闭⼀个服务： systemctl stop firewalld.service
重启⼀个服务： systemctl restart firewalld.service
显示⼀个服务的状态： systemctl status firewalld.service
在开机时启⽤⼀个服务： systemctl enable firewalld.service
在开机时禁⽤⼀个服务： systemctl disable firewalld.service
查看服务是否开机启动： systemctl is-enabled firewalld.service
查看已启动的服务列表： systemctl list-unit-files|grep enabled
查看启动失败的服务列表： systemctl --failed
3. 配置 firewalld-cmd
查看版本：  firewall-cmd --version
查看帮助：  firewall-cmd --help
显示状态：  firewall-cmd --state
查看所有打开的端⼝：  firewall-cmd --zone=public --list-ports
更新防⽕墙规则：  firewall-cmd --reload
查看区域信息 :  firewall-cmd --get-active-zones
查看指定接⼝所属区域：  firewall-cmd --get-zone-of-interface=eth0
拒绝所有包： firewall-cmd --panic-on
取消拒绝状态：  firewall-cmd --panic-off
查看是否拒绝：  firewall-cmd --query-panic
那怎么开启⼀个端⼝呢
添加
firewall-cmd --zone=public --add-port=80/tcp --permanent     （ --permanent 永久⽣效，没有此参数重启后失效）
firewall-cmd --zone=public --add-port=6379/tcp --permanent
重新载⼊
firewall-cmd --reload
查看
firewall-cmd --zone= public --query-port=80/tcp
删除
firewall-cmd --zone= public --remove-port=80/tcp --permanent
# 查看当前 zones
# firewall-cmd --get-active-zones
# 显示当前开放端⼝

# firewall-cmd --zone=public --list-ports
下⾯来说⼀下 :  zone   这个参数是做什么的
zone 的概念：硬件防⽕墙默认⼀般有三个区， firewall 引⼊这⼀概念系统默认存在以下区域：
drop ：默认丢弃所有包
block ：拒绝所有外部连接，允许内部发起的连接
public ：指定外部连接可以进⼊
external ：这个不太明⽩，功能上和上⾯相同，允许指定的外部连接
dmz ：和硬件防⽕墙⼀样，受限制的公共连接可以进⼊
work ：⼯作区，概念和 workgoup ⼀样，也是指定的外部连接允许
home ：类似家庭组
internal ：信任所有连接
将 80 端⼝的流量转发⾄ 8080：
1 、⾸先要明⽩， firewall-cmd 是 Centos7 系统的⽹络防⽕墙，既然是防⽕墙它就有能⼒确定外⾯想访问内部端⼝的权
限，我之前在阿⾥云 Centos7.3 上安装了 mysql ，它的内部端⼝号是 3306, 但是我⽤ sql 的图形化界⾯⼯具通过公⽹ IP 始终
连接不了，后来找到了原因，就是系统打开了 firewall 之后没有开放 3306 端⼝的外界访问权限 , 所以这点⾮常重要，需要
⽤ :firewall-cmd --zone=public --list-ports 查看当前 linux 系统开放的端⼝号，也可以⽤ netstat -tunlp 查看当前 linux 系
统正在监听的端⼝号，就知道⾃⼰想要的 liunx 系统端⼝号是否已经打开。没有开放的，但是⾃⼰⼜需要⽤到的，那就⻢
上⽤ :firewall-cmd --permanent --zone=public --add-port=8080/tcp 开放端⼝，其中数字就是你想要开放的端⼝号，
--permanent 参数表示永久的意思，这样就不必每次启动防⽕墙的时候配置， tcp 代表你要开放的端⼝号的⽹络协议，
也可以是 udp 的。
2 、接来下就是允许防⽕墙伪装 ip : firewall-cmd --add-masquerade --permanent 这⼀步必须做。
3 、将 80 端⼝的流量转发⾄ 8080: firewall-cmd --add-forward-port=port=80:proto=tcp:toport=8080 --permanent
4. 最后别忘了  firewall-cmd --reload  使最新的防⽕墙设置规则⽣效。