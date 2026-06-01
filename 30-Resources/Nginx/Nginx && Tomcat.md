---
title: Nginx && Tomcat
source: 有道云笔记
imported: true
related: ["Nginx centos 离线安装", "Docker安装常见中间件", "SpringBoot学习笔记"]
---

Linux 安装软件的⽅法：
Nginx 编译安装
进⼊ nginx 的安装⽬录： /opt/nginx
第⼀章   Nginx 与 Tomcat 安装，配置以及优化
⼀   Nginx 的安装使⽤
rpm （或 pkg ）安装，类似于 Windows 安装程序，是预编译好的程序
使⽤的是通⽤参数编译，配置参数不是最佳
可控制性不强，⽐如对程序特定组件的定制性安装
通常安装包之间有复杂的依赖关系，操作⽐较复杂
yum （或 apt-get ）安装，改良版的 rpm ，⾃动联⽹下载安装包，⾃动管理依赖关系
编译安装（⽅式在各类 Linux 发⾏版中差异不⼤）
可控性强， config 时可根据当前系统环境优化参数，可定制组件及安装参数
易出错，难度略⾼
检查和安装依赖项
yum -y install gcc pcre pcre-devel zlib zlib-devel openssl openssl-devel1
配置安装选项
./configure --prefix=/opt/nginx // 配置安装⽬录1
2
编译安装：  make && make install

Centos 随机启动：将启动命令添加都下图⽂件中
新增⼀⾏： /opt/nginx/sbin/nginx
⼆   Nginx 的配置

三   Nginx 的优化

Centos 环境变量设置： profile.d ⽂件夹下添加对应的 .sh ⽂件
内存使⽤配置： catalina.sh
最⼤连接数配置： server.xml
四   Tomcat 的安装使⽤
五   Tomcat 的配置与优化
JAVA_OPTS="$JAVA_OPTS -server -Xms1024m -Xmx1024m -XX:PermSize=256m -
XX:MaxPermSize=512m -Djava.awt.headless=true"
1
通过内存设置充分利⽤服务器内存2
-server ： server 模式启动应⽤慢，但是可以极⼤程度提⾼运⾏性能3
-Xms ：最⼩堆内存4
-Xmx ：最⼤堆内存5
Java8 开始， PermSize （永久代）被 MetaspaceSize 代替， MetaspaceSize 共享 head （堆），不会再有
java.lang.OutOfMemoryError:PermGen space, 可以不设置
6
headless=true 适⽤于 linux 系统，与图形操作有关，如⽣产验证码，含义是当前使⽤的是⽆显示器的服务
器，应⽤中如果获取系统显示相关参数会抛出异常
7
8

application.yml
官⽅⽂档的说明为：当所有的请求处理线程都在使⽤时，所能接收的连接请求的队列的最⼤⻓度。当队列已满时，任何
的连接请求都将被拒绝。 accept-count 的默认值为 100 。
详细的来说：当调⽤ HTTP 请求数达到 tomcat 的最⼤线程数时，还有新的 HTTP 请求到来，这时 tomcat 会将该请求放在
等待队列中，这个 acceptCount 就是指能够接受的最⼤等待数，默认 100 。如果等待队列也被放满了，这个时候再来新
的请求就会被 tomcat 拒绝（ connection refused ）。
<Connector port="8080" protocol="org.apache.coyote.http11.Http11NioProtocol"1
connectionTimeout="20000"2
redirectPort="8443" 3
4
maxthreads="500"5
minSpareThreads="100"6
maxSpareThreads="200"7
acceptCount="200"8
enableLookups="false"9
/>10
11
protocol 启动 nio 模式（ tomcat8 默认使⽤的是 nio ）（ apr 模式利⽤系统级异步 io ）12
minProcessors 最⼩空闲连接线程数13
maxProcessors 最⼤连接线程数14
acceptCount 允许的最⼤连接数，应该⼤于等于 maxProcessors15
enableLookups 如果为 true ， request.getRemoteHost 会执⾏ DNS 查找，反向解析 ip 对应域名或主机名16
server:
tomcat:
uri-encoding: UTF-8
# 最⼤⼯作线程数，默认 200, 4 核 8g 内存，线程数经验值 800
# 操作系统做线程之间的切换调度是有系统开销的，所以不是越多越好。
max-threads: 1000
# 等待队列⻓度，默认 100
accept-count: 1000
max-connections: 20000
# 最⼩⼯作空闲线程数，默认 10, 适当增⼤⼀些，以便应对突然增⻓的访问量
min-spare-threads: 100
1
⼀、 accept-count ：最⼤等待数
⼆、 maxThreads ：最⼤线程数

每⼀次 HTTP 请求到达 Web 服务， tomcat 都会创建⼀个线程来处理该请求，那么最⼤线程数决定了 Web 服务容器可以同
时处理多少个请求。 maxThreads 默认 200 ，肯定建议增加。但是，增加线程是有成本的，更多的线程，不仅仅会带来
更多的线程上下⽂切换成本，⽽且意味着带来更多的内存消耗。 JVM 中默认情况下在创建新线程时会分配⼤⼩为 1M 的
线程栈，所以，更多的线程异味着需要更多的内存。线程数的经验值为： 1 核 2g 内存为 200 ，线程数经验值 200 ； 4 核 8g
内存，线程数经验值 800 。
官⽅⽂档的说明为：
这个参数是指在同⼀时间， tomcat 能够接受的最⼤连接数。对于 Java 的阻塞式 BIO ，默认值是 maxthreads 的值；如果
在 BIO 模式使⽤定制的 Executor 执⾏器，默认值将是执⾏器中 maxthreads 的值。对于 Java 新的 NIO 模式，
maxConnections 默认值是 10000 。
对于 windows 上 APR/native IO 模式， maxConnections 默认值为 8192 ，这是出于性能原因，如果配置的值不是 1024 的
倍数， maxConnections 的实际值将减少到 1024 的最⼤倍数。
如果设置为 -1 ，则禁⽤ maxconnections 功能，表示不限制 tomcat 容器的连接数。
maxConnections 和 accept-count 的关系为：当连接数达到最⼤值 maxConnections 后，系统会继续接收连接，但不会
超过 acceptCount 的值。
反向代理⼯作示意图：
负载均衡⼯作示意图：
三、 maxConnections ：最⼤连接数
第⼆章   Nginx+Tomcat 负载均衡配置详解
⼀   负载均衡配置实现

nginx 配置：
nginx upstream 的配置详情：
均衡策略  fair 和 url_hash 是第三⽅提供的负载均衡策略，需要下载相关的包安装才可以使⽤，安装⽅法：

重新执⾏ nginx 的 configure ：
如果时新安装 nginx ，执⾏  make&&make install ，如果是新增第三⽅模块，先执⾏  make 然后按如下步骤：
如果上⾯步骤 make 出现异常：没有名为‘default_port’的成员
执⾏以下命令，然后重来
sed -i 's/default_port/no_port/g' ngx_http_upstream_fair_module.c
⽅案⼀：设置负载均衡策略： ip_hash
⽅案⼆： session 复制
1. Tomcat 配置⽂件中配置集群模式：
./configure --prefix=/opt/nginx --add-module=/root/app/nginx-upstream-fair-master1
⼆   负载均衡时 Session 的处理策略

2. 在应⽤中 web.xml 添加如下配置：（springboot 中怎么实现呢？）
这种⽅案会造成性能下降
⽅案三  tomcat 将 session 放到外部存储
两种⼯作模式：
1. 外部存储的设置，⽐如 redis ，略。
2. Tomcat 的设置：
常⽤的完整配置：
sticky 模式：外部存储只做备份， session 主要存储在服务器上
⾮ sticky 模式： tomcat 不保存 session ， session 放到外部存储

transcoderFactoryClass ：配置第三⽅的序列化类，相关 jar 需要放到 tomcat 的 lib 包下。
三   集群环境中应⽤代码应注意的问题

---
## 相关笔记
- [[Nginx centos 离线安装]]
- [[Docker安装常见中间件]]
- [[SpringBoot学习笔记]]