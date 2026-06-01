---
title: Linux 达梦数据库安装
source: 有道云笔记
imported: true
related: ["Docker 达梦数据库", "信创平台达梦安装", "CentOS7 firewalld的基本使用", "Docker安装常见中间件", "init sql"]
tags: ["达梦", "部署指南", "数据库", "Linux运维"]
summary: 在CentOS7系统下安装和配置达梦数据库DM8的详细操作指南。
---

Centos7  下载对应的安装⽂件
在  Linux 、 Solaris 、 AIX 和  HP-UNIX 等系统中，操作系统默认会对程序使⽤资源进⾏限制。如果不取消对应的限制，
则数据库的性能将会受到影响。
永久修改和临时修改。
使⽤  root ⽤户打开  /etc/security/limits.conf  ⽂件进⾏修改，命令如下：
在最后需要添加如下配置：
创建⽤户组1
groupadd dinstall -g 20012
创建⽤户3
useradd  -G dinstall -m -d /home/dmdba -s /bin/bash -u 2001 dmdba4
修改密码(Qwer1234!)5
passwd dmdba   6
修改⽂件打开最⼤数
重启服务器后永久⽣效。
vi /etc/security/limits.conf1
dmdba  soft      nproc      655361
dmdba  hard      nproc      655362
dmdba  soft      nofile     655363
dmdba  hard      nofile     655364
切换到  dmdba ⽤户，查看是否⽣效，命令如下：
su - dmdba1
2

1. 可根据实际需求规划安装⽬录，本示例使⽤默认配置  DM 数据库安装在  /home/dmdba ⽂件夹下。
2. 规划创建实例保存⽬录、归档保存⽬录、备份保存⽬录。
注意使⽤  root ⽤户建⽴⽂件夹，待  dmdba ⽤户建⽴完成后需将⽂件所有者更改为  dmdba ⽤户，否
则⽆法安装到该⽬录下
将新建的路径⽬录权限的⽤户修改为  dmdba ，⽤户组修改为  dinstall 。命令如下：
ulimit -a1
⽬录规划
## 实例保存⽬录1
mkdir -p /dmdata/data 2
## 归档保存⽬录3
mkdir -p /dmdata/arch4
## 备份保存⽬录5
mkdir -p /dmdata/dmbak6
7
修改⽬录权限

给路径下的⽂件设置  755 权限。命令如下：
切换到  root ⽤户，将  DM 数据库的  iso 安装包保存在任意位置，例如  /opt ⽬录下，执⾏如下命令挂载镜像：
初始化数据库：
chown -R dmdba:dinstall /dmdata/data1
chown -R dmdba:dinstall /dmdata/arch2
chown -R dmdba:dinstall /dmdata/dmbak3
4
chmod -R 755 /dmdata/data1
chmod -R 755 /dmdata/arch2
chmod -R 755 /dmdata/dmbak3
挂载镜像
cd  /opt1
mount -o loop dm8_20240116_x86_rh7_64.iso /mnt2
3
如果挂在不了，直接解压 iso ⽂件  上传解压后⽂件并安装。4
./dminit path=/dmdata/data PAGE_SIZE=32 EXTENT_SIZE=32 CASE_SENSITIVE=n
CHARSET=1 DB_NAME=DMTEST INSTANCE_NAME=DBSERVER PORT_NUM=5237
SYSDBA_PWD=Qwer1234! SYSAUDITOR_PWD=Qwer1234!
1




---
## 相关笔记
- [[信创平台达梦安装]]
- [[Docker 达梦数据库]]
- [[init sql]]
- [[Docker安装常见中间件]]
- [[CentOS7 firewalld的基本使用]]