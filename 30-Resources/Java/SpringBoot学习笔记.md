---
title: SpringBoot学习笔记
source: 有道云笔记
imported: true
related: ["SpringCloud", "Docker实战教程", "Kubernetes", "Jenkins持续集成实战"]
---

1. SpringBoot 的⾃动化配置：
在向应⽤程序加⼊ Spring Boot 时，有个名为spring-boot-autoconfigure的 JAR ⽂件，其中包含了  很多配置类。每个配
置类都在应⽤程序的 Classpath ⾥，都有机会为应⽤程序的配置添砖加瓦。
2. 条件化配置：
所有这些配置如此与众不同，原因在于它们利⽤了 Spring 的条件化配置，这是 Spring 4.0 引⼊  的新特性。条件化配置允
许配置存在于应⽤程序中，但在满⾜某些特定条件之前都忽略这个配置。在 Spring ⾥可以很⽅便地编写你⾃⼰的条件，
你所要做的就是实现 Condition 接⼝，覆盖它  的 matches() ⽅法。
3. ⾃定义配置：显示配置进⾏覆盖  / 使⽤属性进⾏精细化配置
1. 覆盖⾃动配置很简单，就当⾃动配置不存在，直接显式地写⼀段配置。这段显式配置的形式  不限， Spring ⽀持的 XML
和 Groovy 形式配置都可以。在编写显式配置时，我们会专注于 Java 形式的配置。在 Spring Security 的场景下，这意味
着写  ⼀个扩展了 WebSecurityConfigurerAdapter 的配置类。@ConditionalOnMissingBean 注解是覆盖⾃动配置的关键
2. Spring Boot 应⽤程序有多种设置途径。 Spring Boot 能从多种属性源获得属性，包括如下⼏处：
条件化注释 配置⽣效条件
@ConditionalOnBean 配置了某个特定的 bean
@ConditionalOnMissingBean 没有配置特定的 bean
@ConditionalOnClass Classpath 中有指定的类
@ConditionalOnMissingClass Classpath 中没有指定的类
@ConditionalOnExpression 给定的 Spring Expression Language(SpEL) 表达式
计算结果为 true
@ConditionalOnJava Java 的版本匹配特定值或者⼀个范围值
@ConditionalOnJndi 参数中给定的 JNDI 位置必须存在⼀个，如果没有
给参数，则要有 JNDI InitialContext
@ConditionalOnProperty 指定的配置属性要有⼀个明确的值
@ConditionalOnResource Classpath ⾥有指定的资源
@ConditionalOnWebApplication 这是⼀个 Web 应⽤程序
@ConditionalOnNotWebApplicatio 这不是⼀个 Web 应⽤程序
命令⾏参数

```bash
java:comp/env ⾥的 JNDI 属性
```

JVM 系统属性
操作系统环境变量
随机⽣成的带 random.* 前缀的属性 ( 在设置其他属性时，可以引⽤它们，⽐如 ${random. long})
应⽤程序以外的 application.properties 或者 appliaction.yml ⽂件
打包在应⽤程序内的 application.properties 或者 appliaction.yml ⽂件
通过 @PropertySource 标注的属性源

这个列表按照优先级排序，也就是说，任何在⾼优先级属性源⾥设置的属性都会覆盖低优先级的相同属性。例如，命令
⾏参数会覆盖其他属性源⾥的属性。
application.properties 和 application.yml ⽂件能放在以下四个位置：
同样，这个列表按照优先级排序。
4. 揭秘  Actuator 的端点
Spring Boot Actuator 的关键特性是在应⽤程序⾥提供众多 Web 端点，通过它们了解应⽤程序  运⾏时的内部状况。有了
Actuator ，你可以知道 Bean 在 Spring 应⽤程序上下⽂⾥是如何组装在⼀  起的，掌握应⽤程序可以获取的环境属性信
息，获取运⾏时度量信息的快照 ......
Actuator 提供了 13 个端点，具体如下所示：
默认属性
外置，在相对于应⽤程序运⾏⽬录的 /config ⼦⽬录⾥。
外置，在应⽤程序运⾏的⽬录⾥。
内置，在 config 包内。
内置，在 Classpath 根⽬录。

HTTP ⽅法 路径 描述
GET /autoconfig
提供了⼀份⾃动配置报告，记录
哪些⾃动配置条件通过了，哪些
没通过
GET /configprops 描述配置属性 ( 包含默认值 ) 如何
注⼊ Bean
GET /beans 描述应⽤程序上下⽂⾥全部的
Bean ，以及它们的关系
GET /dump 获取线程活动的快照
GET /env 获取全部环境属性
GET /env/{name} 根据名称获取特定的环境属性值
GET /health
报告应⽤程序的健康指标，这些
值由 HealthIndicator 的实现类提
供
GET /info 获取应⽤程序的定制信息，这些
信息由 info 打头的属性提供
GET /mappings
描述全部的 URI 路径，以及它们
和控制器 ( 包含 Actuator 端点 ) 的
映射关系
GET /metrics 报告各种应⽤程序度量信息，⽐
如内存⽤量和 HTTP 请求计数
GET /metrics/{name} 报告指定名称的应⽤程序度量值
POST /shutdown
关闭应⽤程序，要求
endpoints.shutdown.enabled 设
置为 true
GET /trace 提供基本的 HTTP 请求跟踪信息
( 时间戳、 HTTP 头等 )

---
## 相关笔记
- [[SpringCloud]]
- [[Docker实战教程]]
- [[Kubernetes]]
- [[Jenkins持续集成实战]]
