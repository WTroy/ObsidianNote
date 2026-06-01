---
title: RabbitMQ
source: 有道云笔记
imported: true
related: ["Kafka", "SpringCloud", "超时未确认加油单提醒记录保存"]
---

RabbitMQ 架构图：
⽣产者和消费者都是通过⻓连接连接到 MQ ，然后通过信道通信。
⽣产者发送的消息包括消息头和消息体，消息头中包含路由键，再通过 Exchange 的类型来保证保存到哪个队列中，消
息体中则是真正想要发送的数据。

Exchange 交换机  总结：
direct 类型：根据路由键完全匹配
fanout 类型：⼴播，全发
topic 类型：类似正则匹配，匹配成功后再加⼊队列
headers ：  不重要
VHost 虚拟主机：
类似于数据隔离，不同的环境可以使⽤不同的虚拟主机。⽐如： dev/prod
RabbitMQ 消息确认机制 - 可靠抵达
保证消息不丢失，可靠抵达。可以使⽤事务消息，但是性能会下降 250 倍，为此引⼊确认机制。
⽣产者 Publisher ：
confirmCallBack：确认模式：消息到达服务器之时的回调
spring.rabbitmq.publisher-confirms=true SpringBoot 这个配置已经过时，不推荐使⽤这个回调  没意思
1. 在创建 connectionFactory 的时候设置 Publisher Confirms(true) 选项，开启 confirmsCallback
2. CorrelationData ：⽤来表示当前信息的唯⼀性
3. 消息只要被 broker 接收到就会执⾏ confirmsCallback ，如果是 cluster 模式。需要所有 broker 接收到 confirmsCallback
4. 被 broker 接收到的消息只表示 message 到达服务器，并不能保证消息⼀定会被投递到⽬标 queue ⾥，所以需要⽤到接
下来的 returnCallback

returnCallback：未投递到 queue 退回模式
spring.rabbitmq.publisher-returns=true
spring.rabbitmq.template.mandatory=true
1. 有些场景我们需要保证消息被正确的投递到 queue 中，这时就会需要使⽤ return 退回模式
2. 未能成功投递到 queue ⾥时将会调⽤ returnCallback ，可以记录下详细的投递数据，定期巡查或⾃动纠错都需要这些
数据
消费者 Consumer ：
ack 机制：
消费者获取到消息，成功处理，可以回复 ACK 给 Broker ： basic.ack ⽤于肯定确认， broker 将移除此消息； basic.nack ⽤
于否定意图，可以指定是否丢弃此消息，可以批量处理； basic.reject ⽤于否定意图，同上，但是不能批量处理。
1. 默认⾃动 ack ，消息被消费者收到， broker 就会从 queue 中移除
2. queue ⽆消费者，消息仍然会被存储，知道被消费者消费
3. 因为默认会⾃动 ack ，我们可以开启⼿动 ack ，保证每个消息都被处理
3.1 消息处理成功， ack() ，接受下⼀个消息，此消息会被移除
3.2 消息处理失败： nack()/reject() ，重新发送给其他⼈处理，或者容错处理之后再 ack
3.3 消息⼀致没有 ack/nack ⽅法， broker 会认为此消息正在被处理，不会投递给别⼈；此时客户端断开，消息不会被
broker 移除，⽽是投递给别⼈
RabbitMQ 延时队列（实现定时任务）：
场景：未付款账单，超过⼀定时间后，系统⾃动取消订单并释放占⽤物品。
常⽤的解决⽅案： spring 的 schedule 定时任务轮训数据库
缺点：消耗内存，增加数据库压⼒，存在较⼤的时间误差
解决： rabbitmq 的消息 TTL 和死信 Exchange 结合
消息的 TTL （ Time To Live ）：
1. 消息的 TTL 就是消息的存活时间
2. RabbitMQ 可以对队列和消息分别设置 TTL
2.1 对队列设置就是队列中所有的消息从进队开始计时；也可以对每个消息来设置 TTL ，超过这个时间，我们就认为消
息死了，称之为死信
2.2 如果队列设置了，消息也设置了，那么就会取最⼩值
Dead Letter Exchange （ DLX ）：
1. ⼀个消息如果满⾜如下条件，就会进⼊死信路由，记住这⾥是路由⽽不是队列，⼀个路由可以对应很多队列。
2. 什么是死信？
2.1 ⼀个消息被 Consumer 拒收了，并且 reject ⽅法的参数⾥ requeue 是 false ，也就是说不会被再次放在队列中，来让其
他消费者使⽤。 (basic.nack/basic.reject) requeue=false
2.2 上⾯的消息 TTL 到了，消息过期了
2.3 队列的⻓度满了，排在前边的消息就会被丢掉或者放到死信路由
3. DLX 其实就是⼀种普通的 Exchange ，和创建其他 Exchange 没有什么两样。只是在某⼀个延时队列中的消息过期后会
⾃动触发转发消息，转发到这个路由上⽽已。
4. 我们可以控制消息在⼀段时间后变成死信，⼜可以让死信被路由到某⼀个指定的交换机，结合⼆者就可以实现⼀个延
时队列。

业务场景：提交订单之后等待⽀付的过程

---
## 相关笔记
- [[Kafka]]
- [[SpringCloud]]
- [[超时未确认加油单提醒记录保存]]