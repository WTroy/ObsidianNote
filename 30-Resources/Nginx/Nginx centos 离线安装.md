---
title: Nginx centos 离线安装
source: 有道云笔记
imported: true
---

1. 安装 gcc
⽅式 1 ：从 centos7 的系统安装镜像中提取：解压镜像⽂件，进⼊ "Packages" ⽬录，取出如下图所示 rpm 包
⽅式 2 ：访问镜像⽹站获取：   ，然后将其上传
从⾥⾯ packages 找出来，这些是从⽹上整理出来的（ 15 个⽂件不要漏掉！！）
解压 gcc.zip ，编译安装

```
[root@CDH-143 soft]# unzip gcc.zip
[root@CDH-143 soft]# cd gcc
[root@CDH-143 soft]# rpm -Uvh *.rpm --nodeps --force
```

查看 gcc 版本，出现以下信息，表示安装成功

```
[boco@CDH-143 spark_job_monitor]$ gcc --version
gcc (GCC) 4.8.5 20150623 (Red Hat 4.8.5-4)
Copyright (C) 2015 Free Software Foundation, Inc.
This is free software; see the source for copying conditions. There is NO
warranty; not even for MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
[root@CDH-143 redis]#
```

2. pcre 安装
执⾏如下命令：

```bash
tar -zxvf pcre-8.42.tar.gz
cd pcre-8.42/
./configure
make
make install
```

3. zlib 安装
执⾏如下命令：

```bash
tar -zxvf zlib-1.2.11.tar.gz
cd zlib-1.2.11/
./configure
make
make install
```

4. openssl 安装
执⾏如下命令：

```bash
tar -zxvf openssl-1.1.0h.tar.gz
http://mirrors.aliyun.com/centos/7/os/x86_64/Packages/
```

```bash
cd openssl-1.1.0h/
./config
make
make install
```

5. nginx 安装
执⾏如下命令：

```bash
tar -zxvf nginx-1.14.0.tar.gz
cd nginx-1.14.0/
./configure --prefix=/usr/local/nginx --with-http_ssl_module --with-pcre=../pcre-8.42 --with-zlib=../zlib-1.2.11 --with-
openssl=../openssl-1.1.0h
make
make install
```

测试 nginx 是否安装成功
nginx 启动

```bash
cd /usr/local/nginx/sbin
./nginx
```

浏览器访问如： IP
如果能正常显示 nginx ⾸⻚，则表示安装成功
6. 如果启动报错： error while loading shared libraries: libpcre.so.0
⾸先确定 pcre 已经安装，
如果没有安装要⾸先安装⼀下：如上步骤 2 。
查看 libpcre ⽂件是否存在：进⼊ /lib64 ⽬录

```bash
ls -ld libpcre.so.*
```

如图，需要创建软连接，要仔细看报错，⽤报错中缺少的 lib 的名称指向这个 libpcre.so.1.2.0 ，也可能是 libpcre.so.*.* 这种形式
创建软连接：
ln -s /lib64/libpcre.so.1.2.0 /lib64/libpcre.so.0
之后可以看到这个软连接，
现在进⼊ nginx ⽬录下，执⾏ ./sbin/nginx  已经没有报错了。

```yaml
http://
```
