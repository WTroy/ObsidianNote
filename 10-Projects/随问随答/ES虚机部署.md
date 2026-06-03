---
title: ES虚机部署
source: 有道云笔记
imported: true
related: ["Docker实战教程", "基础架构相关信息", "ES内存那点事"]
tags: ["服务器", "运维", "部署指南", "部署", "Elasticsearch"]
summary: ES虚拟机部署、插件安装、系统配置及安全设置的操作指南。
---

创建 elasticsearch ⽤户，不能直接 root 启动：

```bash
sudo adduser es;
sudo passwd es; # ⾃⼰记住密码
```

上传安装包并解压：

```xml
tar -xzf elasticsearch-x.x.x-linux-x86_64.tar.gz
unzip elasticsearch-analysis-ik-7.6.2.zip
# 将分词插件移到 es 的插件⽬录中
mv elasticsearch-analysis-ik-7.6.2 $ES_HOME/plugins/ik
# 修改分词器的词库地址：
vi $ES_HOME/plugins/ik/config/IKAnalyzer.cfg.xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE properties SYSTEM "http://java.sun.com/dtd/properties.dtd">
<properties>
<comment>IK Analyzer 扩展配置</comment>
<!-- ⽤户可以在这⾥配置⾃⼰的扩展字典  -->
<!-- <entry key="ext_dict"></entry> -->
<!-- ⽤户可以在这⾥配置⾃⼰的扩展停⽌词字典 -->
<entry key="ext_stopwords"></entry>
<!-- ⽤户可以在这⾥配置远程扩展字典  -->
<entry
key="remote_ext_dict">http://shpaaspub02.ceair.com:11916/api/v1/static/files/term
s.dic</entry>
<!-- ⽤户可以在这⾥配置远程扩展停⽌词字典 -->
<!-- <entry key="remote_ext_stopwords">words_location</entry> -->
</properties>
# 创建同义词⽂件，⽤过备份改进⽅案
vi $ES_HOME/config/analysis/synonym.txt
```

修改配置：

```bash
vi $ES_HOME/config/elasticsearch.yml
network.host: 0.0.0.03
```

```yaml
cluster.initial_master_nodes: ["node-1"]
```

如果启动有报错，⼤概率要修改系统配置：

```bash
sudo vim /etc/sysctl.conf
# 在最后⼀⾏添加：
vm.max_map_count=2621443
sysctl -p
```

启动：

```bash
./bin/elasticsearch &
# 或者：
./bin/elasticsearch -d -p pid
# ⽇志在  $ES_HOME/logs  ⽬录中
pkill -F pid
```

验证：

```bash
curl -X GET "10.73.96.142:9222/?pretty"
curl --request POST \
--url http://10.18.8.203:9200/_analyze \
--header 'content-type: application/json' \
--data '{
"analyzer": "ik_smart", // ik_smart/ik_max_word
"text": " 查询基础运⾏数据 "
}'
```

如果有防⽕墙
启动：  systemctl start firewalld1
查看状态：  systemctl status firewalld 2

停⽌：  systemctl disable firewalld3
禁⽤：  systemctl stop firewalld4

```bash
firewall-cmd --zone=public --add-port=9200/tcp --permanent
```

重新载⼊6

```bash
firewall-cmd --reload
```

如果是 centos6 ⼤概率是 iptables ：9

```bash
iptables -I INPUT -p tcp --dport 9222 -j ACCEPT
```

登录密码
第⼀步、在  elasticsearch.yml 中添加如下配置1

```yaml
# 配置 X-Pack
http.cors.enabled: true
http.cors.allow-origin: "*"
http.cors.allow-headers: Authorization
xpack.security.enabled: true
xpack.security.transport.ssl.enabled: true
```

第⼆步、重启 elasticsearch 服务9
第三步、设置 elasticsearch 密码11

```bash
./bin/elasticsearch-setup-passwords interactive
```

因为需要设置  elastic ， apm_system ， kibana ， kibana_system ， logstash_system ，
beats_system ， remote_monitoring_user 这些⽤户的密码，故这个过程⽐较漫⻓，耐⼼设置；
第四步、验证15
待补充

---
## 相关笔记
- [[Docker实战教程]]
- [[基础架构相关信息]]
- [[ES内存那点事]]
