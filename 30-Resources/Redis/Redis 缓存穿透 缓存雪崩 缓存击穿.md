---
title: Redis 缓存穿透 缓存雪崩 缓存击穿
source: 有道云笔记
imported: true
related: ["Redis项目实战与分布式集群", "Redis的高并发和快速原因", "SpringCloud", "事务：隔离级别，不生效场景", "视图 V_FULE_INVOICE_RECEIPT_COSTS 的优化"]
---

缓存穿透：
现象：
查询⼀个不存在的数据，由于缓存不命中，将去查询数据库，但是数据库也⽆此记录，我们没有将这个空值 null 写⼊缓
存，这将导致这个你不存在的数据每次都需要查询数据库，失去了缓存的意义。
⻛险：
利⽤不存在的数据进⾏攻击，数据库压⼒增⼤，最终导致奔溃
解决：
null 结果缓存，并加⼊短暂过期时间
缓存雪崩：
现象：
缓存雪崩是指我们设置缓存的 key 采⽤了相同的过期时间，导致缓存在某⼀个时刻同时失效，请求全部转发到 DB ， DB 瞬
时压⼒过⼤
解决：
原有的失效的时间基础上增加⼀个随机值，⽐如 1-5 分钟随机值。
缓存击穿：
现象：
对于⼀个热点数据，在某⼀时间点有超⾼的访问量；如果在⼤量访问的时候正好这个 key 失效了，那么所有查询这个 key
的⽤户都会访问 DB
解决：
加锁：⼤量并发只让⼀个去查，其他⼈等候，查到以后释放锁，其他⼈获取锁先查缓存，就会有数据，不会去 DB
单实例 redis 情境下的 redis 命令分布式实现⽅式：
public class SingleLock {1
@Autowired2
private RedisTemplate<String, String> redisTemplate;3
public Boolean testLock() throws InterruptedException {5
// 占⽤分布式锁，去 redis 占坑6

```
String value = UUID.randomUUID().toString();
```

// 设置过期时间必须和加锁是同步的，保证原⼦性8

```
Boolean lock = redisTemplate.opsForValue().setIfAbsent("lock", value, 1,
TimeUnit.MINUTES);
if (lock) {
```

// 执⾏业务逻辑11
TimeUnit.SECONDS.sleep(30);12
// 删锁也要保证原⼦性，利⽤ Lua 脚本实现13

```java
String unLockStr = "if redis.call(\"get\",KEYS[1]) == ARGV[1] then
return redis.call(\"del\",KEYS[1]) else return 0 end";
Long unLock = redisTemplate.execute(new DefaultRedisScript<>
(unLockStr, Long.class), Collections.singletonList("lock"), value);
return true;
}else {
```

// 加锁失败后重试；可以加⼀个短暂的休眠时间18
return testLock();19

```
}
}
}
```

---
## 相关笔记
- [[Redis项目实战与分布式集群]]
- [[Redis的高并发和快速原因]]
- [[SpringCloud]]
- [[事务：隔离级别，不生效场景]]
- [[视图 V_FULE_INVOICE_RECEIPT_COSTS 的优化]]
