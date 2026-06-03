---
title: Docker 达梦数据库
source: 有道云笔记
imported: true
related: ["Docker的常用命令", "Docker安装常见中间件", "信创平台达梦安装", "Linux 达梦数据库安装", "Docker实战教程"]
tags: ["技术文档", "达梦数据库", "Docker", "部署"]
summary: Docker 环境下达梦数据库的加载与运行命令
---

Docker 达梦数据库（本机）

```bash
docker load -i dm8_20240422_x86_rh6_64_rq_std_8.1.3.100_pack2.tar
docker run --name=dm8_test --env=EXTENT_SIZE=32 --env=LOG_SIZE=1024 --
env=UNICODE_FLAG=1 --env=INSTANCE_NAME=dm8_test --
env=LD_LIBRARY_PATH=/opt/dmdbms/bin --env=CASE_SENSITIVE=0 --
env=SYSDBA_PWD=PswIsTroy123 --env=PAGE_SIZE=16 --env=SYSAUDITOR_PWD=SYSDBA_dm001
--env=LENGTH_IN_CHAR=0 --env=BUFFER=1000 --env=MODE=dmsingle --
env=CHG_PASSWD=dameng777 --env=DM_USER_PWD=dameng777 --env=BLANK_PAD_MODE=0 --
env=LANG=en_US.UTF-8 -p 30236:5236 --restart=always -d
dm8:dm8_20241230_rev255012_x86_rh6_64
```

---
## 相关笔记
- [[Docker的常用命令]]
- [[Docker安装常见中间件]]
- [[信创平台达梦安装]]
- [[Linux 达梦数据库安装]]
- [[Docker实战教程]]
