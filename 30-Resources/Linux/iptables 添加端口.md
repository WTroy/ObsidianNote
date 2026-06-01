---
title: iptables 添加端口
source: 有道云笔记
imported: true
---

添加的时候要注意位置，不能添加到拒绝的配置下边
1
[root@ets-test003-10182231 ~]# vi /etc/sysconfig/iptables2
-A INPUT -m state --state NEW -m tcp -p tcp --dport 10000 -j ACCEPT3
[root@ets-test003-10182231 ~]# systemctl restart iptables.service4
[root@ets-test003-10182231 ~]# service iptables restart5
6