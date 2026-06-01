---
title: Mysql主从+集群
source: 有道云笔记
imported: true
related: ["MySql优化", "MYSQL技术内幕 InnoDB存储引擎", "Mysql事务，事务的隔离级别", "Docker实战教程", "CentOS8卸载与安装MySQL5.7"]
---

binlog 的主从复制实现⽅案图：
前提条件：
Mysql 主从复制
Mysql5.7 安装
Centos8 卸载与安装 MySQL5.7( 完整版 ) - 简书  (jianshu.com)
基于 binlog 主从复制搭建
主从两台主机都安装了 mysql ，并且正常运⾏
字符集：主从机器的字符集全部都设置⼀致
show variables like '%char%';1
修改 mysql 的 my.conf ⽂件2
[mysqld]3
character_set_server=utf84
开启 binlog ：查看 binlog 是否开启
show variables like '%log_bin%';1
my.conf2
[mysqld]3
server-id=101 // 副本节点也需要设置这个选项4
log-bin=mysql-bin5

注意：
主库需要开启 binlog ，从库不是必须的
在主库添加⼀个⽤户 repl 并指定 replication 权限
grant replication slave on *.* TO 'repl'@'%' identified by '123456';1
在主数据库中运⾏  show master status; 记下  file 和  position 字段对应的参数
在从库设置它的 master
change master to master_host='192.168.230.101', master_port=3306,
master_user='repl', master_password='123456', master_log_file='mysql-
bin.000001', master_log_pos=437;
1
// 这⾥的 master_log_file 和 master_log_pos 对应刚才 show master status 记下的参数2
在从库中开启从数据库复制功能： start slave;
在从库中通过  show slave status\G; 来查看⼀些参数

事务的四⼤特性（ ACID ）
此时在主库中创建数据库，表或者插⼊数据，在从库中就会很快能看到
利⽤ binlog ，不影响业务搭建主从
原⼦性（ Atomicity ）
⼀致性（ Consistency ）
隔离型（ Isolation ）
持久性（ Durability ）
事务隔离级别 脏读 不可重复读 幻读
读未提交（ read-
uncommitted ） 是 是 是
不可重复读（ read-
committed ） 否 是 是
可重复读（ repeated-
read ） 否 否 是
串⾏化（ Serializable ） 否 否 否
在之前的基础上，如果备库未运⾏可忽略
在从库上执⾏： stop slave  && reset slave
在主库上执⾏以下命令
mysqldump -h192.168.230.101 -uroot -p123456 --default-character-set=utf8 --
database test --single-transaction --master-date=2>test.sql
1
// single-transaction, 使⽤可重复读隔离级别，保证数据的读⼀致性  innodb 引擎下2
// master-data=1 不注释  change master3
// master-data=2 注释  change master4
查看导出的 test.sql ⽂件内容，获取 binlog 的⽂件和 position 信息

Mysql binlog ⽇志有三种格式：
ROW ：
⽇志中会记录成每⼀⾏数据的修改，然后在 slave 端再对相同的数据进⾏修改。
STATEMENT ：
每⼀条修改数据的 sql 都会被记录到 master 的 bin-log 中。 slave 在复制的时候 sql 进程会解析成和原来 master 端执⾏过的
相同的 sql 来再次执⾏。
MIXED ：
实际上就是两种模式的结合，在 mixed 模式下， mysql 会根据执⾏的每⼀条具体的 sql 语句来区分对待记录的⽇志形式。
也就是说在 statement 和 row 之间选⼀种。新版本中的 statement level 还是和以前⼀样，仅仅记录执⾏的语句。⽽新版
本的 row level 被做了优化，并不是所有的修改都会以 row level 来记录，想遇到表结构变更的时候就会以 statement 模式
来记录，如果 sql 语句确实就是 update 或者 delete 等修改数据的语句，那么还是会记录所有⾏的变化。
现在从库中导⼊ dump ⽂件
其他和上述第六步及以后步骤（注意 binlog 的⽂件信息和 position 位置信息）。
主从复制 binlog 格式
优点： bin-log 中可以不记录执⾏的 sql 语句的上下⽂相关的信息，仅仅只需要记录哪⼀条记录被修改了，修改成什么
样了。所以 row level 的⽇志内容会⾮常清楚的记录下每⼀⾏数据修改的细节
缺点： row level 下，所有的执⾏的语句当记录到⽇志中的时候，都会以每⾏记录的修改记录，这样可能会产⽣⼤量
的⽇志内容，⽐如有⼀条更新语句，更新了很多⾏数据，每⼀⾏的数据都会被记录。因此。 bin-log 的⽇志⽂件会很
⼤。
优点：减少 bin-log ⽇志量，节约 io ，提⾼性能。因为它只需要记录在 master 上执⾏的语句的细节以及执⾏语句时候
的上下⽂信息
缺点：由于他是记录的执⾏语句，所以为了让这些语句在 slave 端也能正确执⾏，那么它还必须记录每条语句在执⾏
的时候的⼀些相关信息，也就是上下⽂信息，以保证所有语句在 slave 端被执⾏时能够得到和在 master 上执⾏时候相
同的结果。另外就是，由于 mysql 发展⽐较快，很多新功能的加⼊，使 mysql 的复制遇到了不⼩的挑战，⾃然复制的
时候设计到越复杂的内容， bug 也就越容易出现。在 statement level 下，⽬前已经发现的就有不少情况会造成 mysql
的复制问题，主要是修改数据的时候使⽤了某些特定的函数或者功能的时候会出现，⽐如 sleep() 在有些版本就不能
正确复制。

查看 binlog ⽂件：
GTID （ Global Transaction ID ），也即是全局事务 ID ，其保证为每⼀个在 master 主上提交的事务在复制集群中可以⽣成
⼀个唯⼀的 ID
基于 GTID 的复制是从 MySql5.6 开始⽀持的⼀种新的复制⽅式，此⽅式与传统基于 binlog ⽇志的⽅式存在很⼤的差异，
在原来的基于⽇志的复制中， slave 从服务器连接到 master 主服务器并告诉主服务器要从哪个⼆进制⽇志的偏移量开始
执⾏增加同步，这是我们如果指定的⽇志偏移量不对，这就可能造成主从数据的不⼀致，⽽基于 GTID 的复制会避免。
在基于 GTID 的复制中，⾸先从服务器会告诉主服务器已经在从服务器执⾏完了哪些事务的 GTID 值，然后主库会把所有
没有在从库上执⾏的事务，发送到从库上进⾏执⾏，并且使⽤ GTID 的复制可以保证同⼀个事务只在指定的从库上执⾏⼀
次，这样可以避免由于偏移量的问题造成数据不⼀致。
GTID=source_id:transaction_id
source_id 就是执⾏事务的主库的 server-uuid 值
server-uuid 值是在 mysql 服务⾸次启动⽣成的保存在数据库的数据⽬录中，在数据⽬录中⼜⼀个 auto.conf ⽂件
主从复制过滤规则
Master 上把 event 时间从⼆进制⽇志中过滤（主服务器配置⽂件⾥设置）
binlog-do-db: 只复制指定的数据库
binlog-ignore-db: 不复制指定的数据库
slave 上时间从中继⽇志中过滤（从服务器配置⽂件⾥设置）
replicate_do_db: 只应⽤指定的数据库，多个数据库就写多⾏
replicate_ingore_db: 只忽略应⽤指定的数据库
replicate_do_table: 只应⽤指定的表
replicate_ignore_table: 只忽略指定的表
replicate_wild_do_table: 使⽤ wild 匹配来复制的指定表，⽐如参数设为 abc.% 表示复制 abc 的所有表
replicate_wild_ignore_table: 使⽤ wild 匹配来不复制的指定表
基于 GTID 技术搭建主从复制
1.
a.
b.
2.
a.
b.
c.
d.
e.
f.

也可以使⽤ sql 命令： show variables like '%uuid%';
事务 ID 则是从 1 开始⾃增的序列，表示这个事务是在主库上执⾏的第⼏个事务。
主库操作：
仍然需要开启 binlog ⽇志。
主库修改配置⽂件 my.cnf
查看 master 状态： show master status;
在线开启的⽅式：
[mysqld]1
server-id=1012
log-bin=mysql-bin3
gtid-mode=ON4
enforce-gtid-consistency=ON5
6
// 查看 gtid 相关配置命令7
show variables like '%gtid%';8
// 设置从库操作账户并赋予权限9
grant replication slave,replication client on *.* TO 'repl'@'%' identified by
'123456';
10
set global enforce_gtid_consistency=ON1
set global gtid_mode=ON2
// 查看配置3
show variables like '%gtid%'4

备库：
开启 GTID
查看 mster 状态： show master status\G;
GTID 不⽤关⼼⽇志的位置， gtid 会⾃⼰去寻找位置进⾏同步。
dump 出主库现存数据：
数据初始化：
数据初始化鄙视必须的，如果初始化了会减少搭建的时间：
[mysqld]1
server-id=1022
gtid-mode=ON3
enforce-gtid-consistency=ON4
5
// 查看配置6
show variables like '%gtid%'7
// 在从库中执⾏如下 sql 语句，设置 master 信息8
change master to master_host='192.168.230.101',
master_user='repl',master_password='123456',master_auto_position=1;
9
// 启动 slave10
start slave;11
12
基于 GTID 不影响⽣产的配置主从
mysqldump -h192.168.230.101 -uroot -p123456 --default-character-set=utf8 --
database fxdb --single-transaction --master-data=2 --triggers --routines --
events > test.sql
1
// 到处主库数据到 test.sql ⽂件。参数可以百度⼀下是啥意思2

从库中：
传统⽅式 binlog ：
GTID ⽅式：
reset slave;1
reset master;// 清空 mysql 中的 gtid_executed2
// 导⼊ dump 数据1
mysql -uroot -p123456 --default-character-set=utf8 < test.sql2
// 更新 master 信息3
change master to master_host='192.168.230.101', master_user='repl',
master_password='123456',master_auto_position=1;
4
// 启动 slave5
start slave;6
在线增加从服务器
mysqldump -h192.168.230.101 -uroot -p123456 --default-character-set=utf8 --
database test --single-transaction --master-data=2 > test.sql;
1
mysql -uroot -p123456 --default-character-set=utf8 < test.sql;2
change master to master_host='192.168.230.101', master_port=3306,
master_user='repl',master_password='123456',master_log_file='mysql-
bin.000003',master_log_pos=1142;
3
start slave;4
mysqldump -h192.168.230.101 -uroot -p123456 --default-character-set=utf8 --
database fxdb --single-transaction --master-data=2 --triggers --routines --
events > test.sql;
1
mysql -uroot -p123456 --default-character-set=utf8 < test.sql;2
change master to master_host='192.168.230.101', master_port=3306,
master_user='repl',master_password='123456',master_auto_position=1;
3
start slave;4

已经开启了主从复制的前提下：
主库：
设置参数如下：  show variables like '%auto%';
从库：
主库：
MYSQL 双主复制
// 开启 binlog1
log-bin=mysql-bin2
// 创建⽤户给主库⽤3
grant replication slave,replication client on *.* TO 'repl'@'%' identified by
'123456';
4
// 设置⾃增主键的起始值和步伐，如下图5
change master to master_host='192.168.230.101', master_port=3306,
master_user='repl',master_password='123456',master_auto_position=1;
1

双主同步如何解决主键冲突：
主键在 mysql 中⼀般都是⾃增主键，如果开启双主复制就会导致主键冲突，为了解决这个问题：
如上：如果主备各⼀台，那备机设置参数： offset=2 ； increment=2
主键冲突：
主键冲突后，会导致 SQL 线程停⽌，但是 I/O 线程不会停⽌。
修复⽅案：
show variables like '%gtid%';
MySQL5.5 及以前的复制：
⼀般主从复制有三个线程且都是但线程：
binlog dump( 主 ) --> IO Thread( 从 ) --> SQL Thread( 从 )
⽽ master 这边是通过并发线程提交，事务通过 LSN 写⼊ binlog ；但是 slave 只有⼀个 IO 线程和 SQL 线程，是但线程，所以
在业务⼤的情况下很容易造成主从延时。
start slave;2
stop slave;1
set gtid_next='faa3fd7d-126e-11e9-b533-000c297967df:1-2:5'; // 上图中是 4 ，所以 next 就
是 5
2
begin;3
commit;4
set gtid_next=automatic;5
start slave;6
多线程复制

如果在 MYSQL5.6 版本开启并⾏复制功能（ slave_parallel_workers > 0 ），那么 sql 线程就变成了 coordinator 线程，
coordinator 线程主要负责以下两部分内容：
Coordinator+worker （多个）
若判断可以并⾏执⾏，那么选择 worker 线程执⾏事务的⼆进制⽇志。
若判断不可以并⾏执⾏，如该操作是 DDL ，亦或者是事务跨 schema 操作，则等待所有的 worker 线程执⾏完成之后，在
执⾏当前的⽇志。
这意味着 coordinator 线程并不是仅将⽇志发送给 worker 线程，⾃⼰也可以回放⽇志，但是所有可以并⾏的操作交付由
worker 线程完成。
上述机制实现的基于 schema 的并⾏复制，存在的问题是：
这样设计的并⾏复制效率并不⾼，如果⽤户实例仅有⼀个库，那么就⽆法实现并⾏回放，甚⾄性能会⽐原来的单线程更
差，⽽单库多表是⽐多库多表更为常⻅的⼀种情形。
MySql5.7 的 MTS （ Enhanced Muti-threadedslaves ）
5.7 引⼊了新的机制来实现并⾏复制，不再有基于库的并⾏复制限制，主要思想就是 slave 服务器的回放与主机是⼀致
的，即 master 服务器上是怎么并⾏执⾏， slave 上就怎样进⾏并⾏回放。
mysql v5.7.2 进⾏了优化，增加了参数 slave_parallel_type ，参数有两个选项：
具体设置：
从库：
开启多线程复制的时候，可能需要更改的配置：
对应关系：
可能还需要开启的参数：
DATABASE ：默认值，基于库的并⾏复制⽅式，该参数表示每个库只能⼀个线程
LOGICAL_CLOCK ：基于组提交的并⾏复制⽅式，基于逻辑时钟，可以在⼀个 database 中并发执⾏ relaylog 事务
show variables like 'slave_parallel%';// 查看多线程复制配置参数1
stop slave;2
set global slave_parrallel_type='LOGICAL_CLOCK';3
set global slave_parallel_workers=2; // ⼀般和服务器 cpu 核数相同或 -14
start slave;5
master_info_repository=TABLE （开启 MTS 功能后，会频繁更新 master.info ，设置为 TABLE 减⼩开销）
relay_log_info_repository=TABLE
⽂件 表 说明
master.info mysql.slave_master_info 记录了⾸次同步 master 的位置
relay-log.info mysql.slave_relay_log_info

relay_log_recovery=ON; slave IO 线程 crash ，如果 relay-log 损坏，则⾃动放弃所有未执⾏的 relay-log ，重新从
master 上获取⽇志，保证 relay-log 的完整性。
slave_preserve_commit_order=ON ( 保证提交的顺序性 ) 。在 slave 上应⽤事务的顺序是⽆序的，和 relay log 中记录
的事务顺序不⼀样，这样数据⼀致性是⽆法保证的，为了保证事务是按照 relay log 中记录的顺序来回放，就需要开启
这个参数。虽然 mysql5.7 添加 MTS 后，虽然 slave 可以并⾏应⽤ relaylog ，但是 commit 部分让然是顺序提交，其中可
能会有等待的情况。
多源复制（多主单从）

MySQL 的三种复制⽅式：
InnoDB commit ：三阶段提交过程：
复制的关键步骤：等待从库响应：
异步复制：
半同步复制和 lossless ⽆损复制
asynchronous 异步复制
fully synchronous 全同步复制
semisynchronous 半同步复制：从 MySQL5.5 开始， MySQL 以插件的形式⽀持半同步复制。
A 阶段： write prepare log -- 写⼊ xid
B 阶段： write binlog
C 阶段： commit log

MySQL 默认的复制是异步的，主库在执⾏万客户端提交的事务后会⽴即将结果返回给客户端，并不关⼼从库是否已经接
受并处理，这样如果主 crash ，此时主上已经提交的事务可能并没有传到从上，如果此时，将从提升为主，可能导致新
主上的数据不完整
原理：在异步复制中， master 写数据到 binlog 且 sync ， slave request binlog 后写⼊ relay-log 并 flush disk
优点：复制的性能最好
缺点： master 挂掉后， slave 可能会丢失数据
全同步复制：
当主库执⾏完⼀个事务，所有的从库都执⾏了该事务才返回给客户端，因为需要等待所有从库执⾏完该事务才能返回，
所以全同步复制的性能必然会受到严重的影响
优点：数据不会丢失
缺点：会阻塞 master session ，性能太差，⾮常依赖⽹络。
传统的半同步复制：
介于异步复制和全同步复制之间，主库在执⾏完客户端提交的事务后不是⽴刻返回给客户端，⽽是等待⾄少⼀个从库接
收到并写到 relay log 中才返回给客户端。相对于异步复制，半同步复制提⾼了数据的安全性，同时它也造成了⼀定程度
的延迟，这个延迟最少是⼀个 TCP/IP 往返的时间。所以半同步复制最好在延迟低的⽹络中使⽤。
优点：丢失数据⻛险低
缺点：会阻塞 master session ，性能差，⾮常依赖⽹络。
由于 master 是在第三阶段提交的最后 commit 阶段完成后才等待，所以 master 的其他 session 是可以看到这个提交事务
的，所以这时候 master 上的数据和 slave 上的数据不⼀致， master crash 后， slave 数据丢失。
增强版的半同步复制（ lossless replication ）

原理：在半同步复制中， master 写数据到 binlog 且 sync ，然后⼀直等到 ack ，当⾄少⼀个 slave request binlog 后写⼊到
relay log 并 flush disk ，就返回 ack （不需要回放完⽇志）
优点：数据零丢失（前提是让其⼀直是 lossless replication ） , 性能好
缺点：会阻塞 master session ，⾮常依赖⽹络
由于 master 是在三阶段提交的第⼆阶段 sync binlog 完成后才等待，所以 master 的其他 session 是看不到这个提交事务
的，所以这时候 master 上的数据和 slave ⼀致， master crash 后， slave 没有丢失数据。
实现主从半同步复制：
半同步复制是依赖插件来实现的。
查看 plugins ：
主库：
查看是否⽀持动态加载的 MySQL 服务器：
查看半同步复制相关的参数：
show plugins;1
或者查询： INFORMATION_SCHEMA.PLUGINS 表2
插件的安装位置⼀般为：3
/usr/lib64/mysql/plugin4
mysql>show variables like '%dynamic%';1
安装半同步复制的插件：2
install plugin rpl_semi_sync_master soname 'semisync_master.so'3

查看半同步复制的状态：
备库：
如上图：1
修改红圈中的两个参数：2
rpl_semi_sync_master_enabled=13
rpl_semi_sync_master_timeout: ⼀个以毫秒为单位的值，⽤于控制主服务器等待来⾃从服务器的确认提
交并恢复到异步复制的时间，超过这个值就是超时。默认是 10000 （ 10 秒）。超时后就从半同步复制返回到异
步复制。
4
rpl_semi_sync_master_yes_tx: 从库成功确认的提交数量。1
先安装备库的插件：1
install plugin rpl_semi_sync_slave soname 'semisync_slave.so';2
修改 my.cnf3

keepalived 是什么：
keepalived 是集群管理中保证集群⾼可⽤的⼀个服务软件，⽤来防⽌单点故障。
keepalived ⼯作原理：
keepalived 是以 VRRP 协议为实现基础的， VRRP 全称 Virtual Router Redundancy Protocol ，即虚拟路哟冗余协议。
虚拟路由冗余协议，可以认为是实现路由器⾼可⽤的协议，即将 N 台提供相同功能的路由器组成⼀个路由器组，这
个组⾥⾯有⼀个 master 和多个 backup ， master 上⾯有⼀个对外提供服务的 VIP （该路由器所在局域⽹内其他机器
的默认路由为该 vip ）， master 会发组播，当 backup 收不到 vrrp 包时就认为 master 宕机了，这是就需要根据 VRRP
的优先级来选举⼀个 backup 当 master 。这样的话就可以保证路由器的⾼可⽤了。
keepalived 主要有三个模块：
rpl_semi_sync_slave_enabled=14
查看状态：5
show global variables like '%rpl_semi%';6
Mysql集群（ keepalive ⾼可⽤， LVS 负载均衡， Mycat 读写分离）
keepalived+Mysql 双主可⽤
core ： keepalived 的核⼼，负责主进程的启动，维护以及全局配置⽂件的加载和解析。
check ：负责健康检查，包括常⻅的各种检查⽅式
vrrp ：实现 VRRP 协议的。

开始安装 keepalived （多台机器都装）：
keepalived 服务的开机启动：
keepalived 配置⽂件：
下载 keepalived ，上传到服务器并解压：1
tar zxvf keepalived-2.0.11.tar.gz2
cd keepalived-2.0.11/3
congigure 并设置安装路径4
./configure --prefix=/usr/local/keepalived5
可能会需要的依赖：6
yum install openssl* libnl-dev*7
make && make install8
cp /usr/local/keepalived/sbin/keepalived /usr/sbin1
systemctl list-unit-files | grep keepalived2
mkdir /etc/keepalived3
cp /usr/local/keepalived/conf/keepalived.conf /etc/keepalived4
systemctl enable keepalived5

LVS(Linux Virtual Server) 即 Linux 虚拟服务器，是⼀个开源负载均衡项⽬，⽬前 LVS 已经被集成到 Linux 内核模块中。
LVS 是四层负载均衡，也就是说建⽴在 OSI 模型的第四层的传输层之上，传输层上有我们熟悉的 TCP/UDP ， LVS ⽀持
TCP/UDP 的负载均衡。
环境准备：
安装  ipvsadm 软件包：
LVS+keepalived+ 双主 mysql 负载均衡
IP
192.168.2.150 VIP
192.168.2.151 LVS01
192.168.2.152 LVS02
192.168.2.153 mysql 主 1
192.168.2.154 mysql 主 2

LVS ⼯作模式分为：
LVS 负载均衡调度算法：
yum install -y ipvsadm*1
LVS 安装完成后，查看当前 LVS 集群：2
ipvsadm -L -n3
NAT 模式
TUN 模式
DR 模式
轮训调度（ Round Robin ，简称 RR ）算法就是按⼀次循坏的⽅式将请求调度到不同的服务器上，该算法最⼤的特点
就是实现简单。轮训算法假设所有的服务器处理请求的能⼒都⼀样的，调度器会将所有的请求平均分配给每个真是
服务器
加权轮训（ Weight Round Robin ，简称 WRR ）算法主要是对轮训算法的⼀种优化与补充， LVS 会考虑每台服务器的
性能，并给没台服务器添加⼀个权值，如果服务器 A 的权值为 1 ，服务器 B 的权值为 2 ，则调度器调度到服务器 B 的请
求会是服务器 A 的两倍。

调度算法分类：
keepalived 配置：
在 mysql 所在服务器中：
增加如下脚本⽂件： realserver.sh
加⼊到开机⾃启动：
realserver.sh
最⼩连接调度（ Least Connections ，简称 LC ）算法是把新的连接请求分配到当前连接数最⼩的服务器。最⼩连接调
度是⼀种动态的调度算法，他通过服务器当前活跃的连接数来估计服务器的情况。调度器需要记录各个服务器已建
⽴连接的数⽬，当⼀个请求被调度到某台服务器，其连接数加 1 ；当连接中断或超时，其连接数 -1
加权最少连接（ Weight LeastConnections 简称 WLC ）算法是最⼩连接调度的超级，各个服务器响应的权值表示其
处理性能。服务器的缺省权值是 1 ，系统管理员可以动态的设置服务器的权值。加权最⼩连接调度在调度新连接是尽
可能使服务器的已建⽴连接数和其权值成正⽐。调度器可以⾃动问询真是服务器的负载情况，并动态的调整其权值
基于局部性的最少连接调度算法 lblc
复杂的基于局部性最少的连接算法 lblcr
⽬标地址散列调度算法 dh
原地址散列调度算法 sh
固定调度算法： rr, wrr, dh, sh
动态调度算法： wlc, lc, lblc, lblcr
vi /etc/rc.d/rc.local1
/opt/realserver.sh start2
chmod +x /etc/rc.d/rc.local3
#!/bin/bash1
# chkconfig: 2345 10 90 2

realserver.sh 中参数的含义：
arp_ignore:
arp 是指请求包和响应包。
# description: lvs+kepalived realserver.sh3
VIP=192.168.236.30 4
. /etc/rc.d/init.d/functions5
case "$1" in 6
start) 7
echo 1 > /proc/sys/net/ipv4/conf/lo/arp_ignore8
echo 2 > /proc/sys/net/ipv4/conf/lo/arp_announce9
echo 1 > /proc/sys/net/ipv4/conf/all/arp_ignore 10
echo 2 > /proc/sys/net/ipv4/conf/all/arp_announce 11
ifconfig lo:0 $VIP broadcast $VIP netmask 255.255.255.255 up 12
/sbin/route add -host $VIP dev lo:0 13
sysctl -p > /dev/null 2>&1 14
echo "realserver start OK" 15
;; 16
stop) 17
echo 0 > /proc/sys/net/ipv4/conf/lo/arp_ignore18
echo 0 > /proc/sys/net/ipv4/conf/lo/arp_announce 19
echo 0 > /proc/sys/net/ipv4/conf/all/arp_ignore 20
echo 0 > /proc/sys/net/ipv4/conf/all/arp_announce 21
ifconfig lo:0 down 22
/sbin/route del $VIP > /dev/null 2>&1 23
echo "realserver stoped" 24
;; 25
*) 26
echo "Usage:$0 {start|stop}" 27
exit 1 28
esac 29
exit 030
0 ：响应任意⽹卡上接收到的对主机 IP 地址的 arp 请求（包括环回⽹卡上的地址），⽽不管该⽬的 IP 是否在接受⽹卡
上。
1 ：只响应⽬的 IP 地址为接收⽹卡上的本地地址的 arp 请求

如上图所示：当 arp_ignore 参数配置为 0 时， eth1 ⽹卡上收到⽬的 IP 为环回⽹卡 IP 的 arp 请求，但是 eth1 也会返回 arp 响
应，把⾃⼰的 mac 地址告诉对端。
如上图所示：当 arp_ignore 参数配置为 1 时， eth1 ⽹卡上收到⽬的 IP 为环回⽹卡 IP 的 arp 请求，发现请求的 IP 不是⾃⼰⽹
卡上的 IP ，不会回 arp 响应。
arp_announce:
当 arp_announce 参数设置为 0 时，系统要发送的 IP 包源地址为 eth1 的地址， IP 包⽬的地址根据路由表查询判断需要从
eth2 ⽹卡发出，这是会先从 eth2 ⽹卡发起⼀个 arp 请求，⽤于获取⽬的 IP 地址的 MAC 地址。该 arp 请求的源 MAC ⾃然是
eth2 ⽹卡的 MAC 地址，但是源 IP 地址会选择 eth1 ⽹卡的地址。
0: 允许使⽤任意⽹卡上的 IP 地址作为 arp 请求的源 IP ，通常就是使⽤数据包的源 IP
1: 尽量避免使⽤不属于该发送⽹卡⼦⽹的本地地址作为发送 arp 请求的源 IP 地址
2: 忽略 IP 数据包的源 IP 地址，选择该发送⽹卡上最合适的本地地址作为 arp 请求的源 IP 地址

当 arp_announce 参数配置为 2 时， eth2 ⽹卡发起 arp 请求时，源 IP 地址会选择 eth2 ⽹卡⾃身的 IP 地址。
arp_ignore 和 arp_announce 参数在 DR 模式下的作⽤：
⾃⼰研究⼀下
实现读写分离的⽅式：
arp_ignore: 因为 DR 模式下，每个真是服务器节点都要在环回⽹卡上绑定虚拟服务 IP 。这时候，如果客户端对于虚拟
服务 IP 的 arp 请求⼴播到了各个真实服务器节点，如果 arp_ignore 参数配置为 0 ，则各个真是服务器节点都会响应该
arp 请求，此时客户端就⽆法正确获取 LVS 节点上正确的虚拟服务 IP 所在⽹卡的 MAC 地址。所以 DR 模式下要求
arp_ignore 参数要求配置为 1
arp_announce: 每个机器或者交换机中都有⼀张 arp 表，该表⽤于存储对端通信节点 IP 地址和 MAC 地址的对应关系。
当收到⼀个未知 IP 地址的 arp 请求，就会在本机的 arp 表中新增对端的 IP 和 mac 记录；当收到⼀个已知 IP 地址（ arp 表
中已有记录的地址）的 arp 请求，则会根据 arp 请求中的源 MAC 刷新⾃⼰的 arp 表。
如果 arp_announce 参数配置为 0 ，则⽹卡在发送 arp 请求时，可能选择的源 IP 地址并不是该⽹卡⾃身的 IP 地址，
这时候收到该 arp 请求的其他节点或者交换机上的 arp 表中记录的该⽹卡 IP 和 MAC 的对应关系就不正确，可能会
引发⼀些未知的⽹络问题，存在安全隐患。
所以 DR 模式下要求 arp_announce 参数要求配置为 2
使⽤ Mycat 实现 Mysql 读写分离
Mycat1.6
程序端实现
主库 从库
insert, update, delete select
mycat 数据库中间件

注意 datahost 节点下⾯的三个属性：
server.xml
balance 负载
balance="0" ，不开启读写分离机制，所有读操作都发送到当前可⽤的 writeHost 上
balance="1" ，全部的 readHost 与 stand by writeHost 参与 select 语句的负载均衡，简单的说，当双主双从模式
（ M1->S1,M2->S2, 并且 M1 和 M2 互为主备），正常情况下， M1,S1,M2,S2 都参与 select 语句的负载均衡。
balance="2" ，所有读操作都随机的在 writeHost ， readHost 上分发
balance="3" ，所有读请求随机发送到 writeHost 下的 readHost 执⾏， writeHost 不负担读压⼒
switchType 切换的模式
switchType="-1", 表示不⾃动切换
switchType="1", 默认值，表示⾃动切换
switchType="2", 基于 Mysql 主从同步的状态决定是否切换，⼼跳语句是  show slave status
switchType="3", 基于 Mysql galary cluster 的切换机制（适合集群），⼼跳语句是  show status like 'wsrep%'
writeType 写模式
writeType="0", 所有的操作发送带配置的第⼀个 writeHost
writeType="1", 随机发送到配置的所有 writeHost
writeType="2", 不执⾏写操作

---
## 相关笔记
- [[MySql优化]]
- [[MYSQL技术内幕 InnoDB存储引擎]]
- [[Mysql事务，事务的隔离级别]]
- [[Docker实战教程]]
- [[CentOS8卸载与安装MySQL5.7]]