---
title: ES虚机部署
source: 有道云笔记
imported: true
related: ["Docker实战教程", "基础架构相关信息", "ES内存那点事"]
tags: ["服务器", "运维", "部署指南", "部署", "Elasticsearch"]
summary: ES虚拟机部署、插件安装、系统配置及安全设置的操作指南。
---

创建 elasticsearch ⽤户，不能直接 root 启动：
sudo adduser es;1
sudo passwd es; # ⾃⼰记住密码2
上传安装包并解压：
tar -xzf elasticsearch-x.x.x-linux-x86_64.tar.gz1
unzip elasticsearch-analysis-ik-7.6.2.zip2
# 将分词插件移到 es 的插件⽬录中3
mv elasticsearch-analysis-ik-7.6.2 $ES_HOME/plugins/ik4
# 修改分词器的词库地址：5
vi $ES_HOME/plugins/ik/config/IKAnalyzer.cfg.xml6
<?xml version="1.0" encoding="UTF-8"?>7
<!DOCTYPE properties SYSTEM "http://java.sun.com/dtd/properties.dtd">8
<properties>9
<comment>IK Analyzer 扩展配置</comment>10
<!-- ⽤户可以在这⾥配置⾃⼰的扩展字典  -->11
<!-- <entry key="ext_dict"></entry> -->12
<!-- ⽤户可以在这⾥配置⾃⼰的扩展停⽌词字典 -->13
<entry key="ext_stopwords"></entry>14
<!-- ⽤户可以在这⾥配置远程扩展字典  -->15
<entry
key="remote_ext_dict">http://shpaaspub02.ceair.com:11916/api/v1/static/files/term
s.dic</entry>
16
<!-- ⽤户可以在这⾥配置远程扩展停⽌词字典 -->17
<!-- <entry key="remote_ext_stopwords">words_location</entry> -->18
</properties>19
20
# 创建同义词⽂件，⽤过备份改进⽅案21
vi $ES_HOME/config/analysis/synonym.txt22
修改配置：
vi $ES_HOME/config/elasticsearch.yml1
2
network.host: 0.0.0.03
1.
2.
3.

cluster.initial_master_nodes: ["node-1"]4
如果启动有报错，⼤概率要修改系统配置：
sudo vim /etc/sysctl.conf1
# 在最后⼀⾏添加：2
vm.max_map_count=2621443
4
sysctl -p5
启动：
./bin/elasticsearch &1
2
# 或者：3
./bin/elasticsearch -d -p pid4
# ⽇志在  $ES_HOME/logs  ⽬录中5
pkill -F pid6
验证：
curl -X GET "10.73.96.142:9222/?pretty"1
2
curl --request POST \3
--url http://10.18.8.203:9200/_analyze \4
--header 'content-type: application/json' \5
--data '{  6
"analyzer": "ik_smart", // ik_smart/ik_max_word7
"text": " 查询基础运⾏数据 "  8
}'9
如果有防⽕墙
启动：  systemctl start firewalld1
查看状态：  systemctl status firewalld 2
4.
5.
6.
7.

停⽌：  systemctl disable firewalld3
禁⽤：  systemctl stop firewalld4
firewall-cmd --zone=public --add-port=9200/tcp --permanent5
重新载⼊6
firewall-cmd --reload7
8
如果是 centos6 ⼤概率是 iptables ：9
iptables -I INPUT -p tcp --dport 9222 -j ACCEPT10
登录密码
第⼀步、在  elasticsearch.yml 中添加如下配置1
# 配置 X-Pack2
http.cors.enabled: true3
http.cors.allow-origin: "*"4
http.cors.allow-headers: Authorization5
xpack.security.enabled: true6
xpack.security.transport.ssl.enabled: true7
8
第⼆步、重启 elasticsearch 服务9
10
第三步、设置 elasticsearch 密码11
./bin/elasticsearch-setup-passwords interactive12
因为需要设置  elastic ， apm_system ， kibana ， kibana_system ， logstash_system ，
beats_system ， remote_monitoring_user 这些⽤户的密码，故这个过程⽐较漫⻓，耐⼼设置；
13
14
第四步、验证15
待补充
8.
9.

---
## 相关笔记
- [[ES内存那点事]]