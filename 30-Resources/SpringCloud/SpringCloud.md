---
title: SpringCloud
source: 有道云笔记
imported: true
---

本次学习案例：⽤户佩戴健康设备，将健康情况上传到云端服务，云端服务⼈员提供对应的异常情况相应：
案例驱动（ SpringHealth ）：
学习 demo 极度简化了业务逻辑，梳理出三个微服务以供演示：
完整的 SpringHealth 服务列表：
代码⼯程之间的依赖关系图：
基础篇： SpringHealth 案例驱动

SpringCloud Alibaba 环境准备
Mysql 数据库准备：
视频服务数据库  video 表
CREATE TABLE `vedio` (1
`id` int(11) NOT NULL AUTO_INCREMENT,2
`title` varchar(524) DEFAULT NULL COMMENT ' 视频标题 ',3
`summary` varchar(1024) DEFAULT NULL COMMENT ' 概述 ',4
`cover_img` varchar(524) DEFAULT NULL COMMENT ' 封⾯图 ',5
`price` int(11) DEFAULT NULL COMMENT ' 价格，分 ',6
`create_time` datetime DEFAULT NULL COMMENT ' 创建时间 ',7
`point` double(10,2) DEFAULT '8.70' COMMENT ' 评分：默认 8.70 ，最⾼ 10 分 ',8
PRIMARY KEY (`id`)9
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb410
⽤户服务数据库 user 表
CREATE TABLE `user` (1
`id` int(11) NOT NULL AUTO_INCREMENT,2
`phone` varchar(32) DEFAULT NULL COMMENT ' ⼿机号 ',3
`pwd` varchar(128) DEFAULT NULL COMMENT ' 密码 ',4
`sex` int(2) DEFAULT NULL COMMENT ' 性别 ',5
`img` varchar(128) DEFAULT NULL COMMENT ' 头像 ',6
`create_time` datetime DEFAULT NULL COMMENT ' 创建时间 ',7
`role` int(11) DEFAULT NULL COMMENT '1 是普通⽤户； 2 是管理员 ',8

`username` varchar(128) DEFAULT NULL COMMENT ' ⽤户名 ',9
`wechat` varchar(128) DEFAULT NULL COMMENT ' 微信号 ',10
PRIMARY KEY (`id`)11
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb412
订单服务数据库 video_order 表
CREATE TABLE `vedio_order` (1
`id` int(11) NOT NULL AUTO_INCREMENT,2
`out_trade_no` varchar(64) DEFAULT NULL COMMENT ' 订单唯⼀标识 ',3
`state` int(11) DEFAULT NULL COMMENT '0 表示未⽀付， 1 表示已⽀付 ',4
`total_fee` int(11) DEFAULT NULL COMMENT ' ⽀付⾦额，单位分 ',5
`vedio_id` int(11) DEFAULT NULL COMMENT ' 视频主键 ',6
`vedio_title` varchar(256) DEFAULT NULL COMMENT ' 视频标题 ',7
`vedio_image` varchar(256) DEFAULT NULL COMMENT ' 视频图⽚ ',8
`create_time` datetime DEFAULT NULL COMMENT ' 创建时间 ',9
`user_id` int(11) DEFAULT NULL COMMENT ' ⽤户 id',10
PRIMARY KEY (`id`)11
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb412