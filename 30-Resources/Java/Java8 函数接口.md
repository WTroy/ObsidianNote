---
title: Java8 函数接口
source: 有道云笔记
imported: true
---

Java8 中函数接⼝有很多 , ⼤概有⼏⼗个吧 , 具体究竟是多少我也数不清 , 所以⼀开始看的时候感觉⼀脸懵逼 , 不过其实根本没那
么复杂 , 毕竟不应该也没必要把⼀个东⻄设计的很复杂。
在学习了解之前 , 希望⼤家能记住⼏个单词 , 掌握这⼏个单词 , 什么 3 ， 40 个官⽅的函数接⼝都是⼩问题了 , 不信的话接着往下看
啦。 ok ，那这⼏个单词呢分别是supplier 提供者,consumer 消费者,function 函数,operation 运算符,binary ⼆元（就是数学
⾥⼆元⼀次⽅程那个⼆元 , 代表 2 个的意思） , 双重的
函数接⼝ , 你可以理解为对⼀段⾏为的抽象 , 简单点说可以在⽅法就是将⼀段⾏为作为参数进⾏传递 , 这个⾏为呢 , 可以是⼀段代
码 , 也可以是⼀个⽅法 , 那你可以想象在 java8 之前要将⼀段⽅法作为参数传递只能通过匿名内部类来实现 , ⽽且代码很难看 , 也很⻓ ,
函数接⼝就是对匿名内部类的优化。
虽然类库中的基本函数接⼝特别多 , 但其实总体可以分成四类 , 就好像阿拉伯数字是⽆限多的 , 但总共就 10 个基本数字⼀样 , 理解
了这 4 个 , 其他的就都明⽩了。
function, 顾名思义 , 函数的意思 , 这⾥的函数是指数学上的函数哦 , 你也可以说是严格函数语⾔中的函数 , 例如 haskell ⾥的 , 他接
受⼀个参数 , 返回⼀个值 , 永远都是这样 , 是⼀个恒定的 , 状态不可改变的⽅法。其实想讲函数这个彻底将明⽩可以再开⼀篇博客了 ,
所以这⾥不详细的说了。
上⾯说到 , 函数接⼝是对⾏为的抽象 , 因此我⽅便⼤家理解 , 就⽤ java 中的⽅法作例⼦。
Fcuntion 接⼝是对接受⼀个 T 类型参数 , 返回 R 类型的结果的⽅法的抽象 , 通过调⽤ apply ⽅法执⾏内容。

```java
public class Operation{
/*
```

下⾯这个⽅法接受⼀个 int 类型参数 a, 返回 a+1, 符合我上⾯说的接受⼀个参数 , 返回⼀个值
所以呢这个⽅法就符合 Function 接⼝的定义 , 那要怎么⽤呢 , 继续看例⼦
*/

```java
public static final int addOne(int a){
return a+1;
}
```

JDK8 函数接⼝

```yaml
https://www.cnblogs.com/invoker-/p/7709052.html
```

前⾔
⼏个单词
四⼤基础函数接⼝
Function<T,R> 接⼝

/*
该⽅法第⼆个参数接受⼀个 function 类型的⾏为 , 然后调⽤ apply ，对 a 执⾏这段⾏为
*/

```java
public static int oper(int a, Function<Integer,Integer> action){
return action.apply(a);
}
```

/* 下⾯调⽤这个 oper ⽅法 , 将 addOne ⽅法作为参数传递  */

```
pulic static void main(String[] args){
int x = 1;
int y = oper(x,x -> addOne(x));// 这⾥可以换成⽅法引⽤的写法  int y = oper(x,Operation::addOne)
```

System.out.printf("x= %d, y = %d", x, y); // 打印结果  x=1, y=2

/* 当然你也可以使⽤ lambda 表达式来表示这段⾏为 , 只要保证⼀个参数 , ⼀个返回值就能匹配  */

```yaml
y = oper(x, x -> x + 3 ); // y =
y = oper(x, x -> x * 3 ); // y =
}
}
```

这⾥的箭头指向的位置就是形参 , 可以看到第⼆个箭头的 Lambda 表达式指向了 Funtion 接⼝
Consumer  接⼝翻译过来就是消费者 , 顾名思义，该接⼝对应的⽅法类型为接收⼀个参数，没有返回值，可以通俗的理解成将这个
参数 ' 消费掉了 ' ，⼀般来说使⽤ Consumer 接⼝往往伴随着⼀些期望状态的改变或者事件的发⽣ , 例如最典型的 forEach 就是使⽤的
Consumer 接⼝，虽然没有任何的返回值，但是却向控制台输出了语句。
Consumer 使⽤ accept 对参数执⾏⾏为

```java
public static void main(String[] args) {
Consumer<String> printString = s -> System.out.println(s);
printString.accept("helloWorld!");
```

// 控制台输出  helloWorld!
}
Consumer  接⼝

Supplier  接⼝翻译过来就是提供者 , 和上⾯的消费者相反，该接⼝对应的⽅法类型为不接受参数，但是提供⼀个返回值，通俗的
理解为这种接⼝是⽆私的奉献者，不仅不要参数，还返回⼀个值 , 使⽤ get() ⽅法获得这个返回值

```
Supplier<String> getInstance = () -> "HelloWorld!";
System.out.println(getInstance.get());
```

// 控偶值台输出  HelloWorld
predicate<T,Boolean> 谓语接⼝，顾名思义，中⽂中的 ‘ 是 ʼ 与 ‘ 不是 ʼ 是中⽂语法的谓语，同样的该接⼝对应的⽅法为接收⼀个参
数，返回⼀个 Boolean 类型值，多⽤于判断与过滤，当然你可以把他理解成特殊的 Funcation<T,R> ，但是为了便于区分语义，还
是单独的划了⼀个接⼝，使⽤ test() ⽅法执⾏这段⾏为

```java
public static void main(String[] args) {
Predicate<Integer> predOdd = integer -> integer % 2 == 1;
System.out.println(predOdd.test(5));
```

// 控制台输出  5
}

介绍完正⾯这四种最基本的接⼝，剩余的接⼝就可以很容易的理解了， java8 中定义了⼏⼗种的函数接⼝，但是剩下的接⼝都是
上⾯这⼏种接⼝的变种，⼤多为限制参数类型，数量，下⾯举⼏个例⼦。
类型限制接⼝
数量限制接⼝
Operator 接⼝
下⾯是各种类型的接⼝的示意图，相信只要真正理解了，其实问题并不⼤
Supplier  接⼝
Predicate  接⼝
其他的接⼝
参数类型 , 例如IntPredicate,LongPredicate, DoublePredicate，这⼏个接⼝，都是在基于 Predicate 接⼝的，不同的就
是他们的泛型类型分别变成了 Integer,Long,Double,IntConsumer,LongConsumer, DoubleConsumer⽐如这⼏个 , 对应的就
是Consumer<Integer>,Consumer<Long>,Consumer<Double>, 其余的是⼀样的道理，就不再举例⼦了
返回值类型，和上⾯类似，只是命名的规则上多了⼀个 To, 例如IntToDoubleFunction,IntToLongFunction,  很明显就是对
应的Funtion<Integer,Double>  与Fcuntion<Integer,Long>，其余同理，另外需要注意的是，参数限制与返回值限制的
命名唯⼀不同就是 To, 简单来说 , 前⾯不带 To 的都是参数类型限制 , 带 To 的是返回值类型限制，对于没有参数的函数接⼝，那显
⽽易⻅只可能是对返回值作限制。例如LongFunction<R>就相当于Function<Long,R>  ⽽多了⼀个 To 的
ToLongFunction<T>就相当于Function<T,Long>，也就是对返回值类型作了限制。
有些接⼝需要接受两名参数 , 此类接⼝的所有名字前⾯都是附加上 Bi, 是Binary的缩写，开头也介绍过这个单词了，是⼆元的意
思，例如BiPredicate,BiFcuntion等等 , ⽽由于 java 没有多返回值的设定，所以 Bi 指的都是参数为两个
此类接⼝只有 2 个分别是UnaryOperator<T>  ⼀元操作符接⼝ , 与BinaryOperator<T>⼆元操作符接⼝，这类接⼝属于
Function 接⼝的简写，他们只有⼀个泛型参数，意思是 Funtion 的参数与返回值类型相同 , ⼀般多⽤于操作计算，计算  a + b 的
BiFcuntion 如果限制条件为 Integer 的话  往往要这么写BiFunction<Integer,Integer,Integer>  前 2 个泛型代表参数，最后
⼀个代表返回值，看起来似乎是有点繁重了 , 这个时候就可以⽤BinaryOperator<Integer>来代替了。

Java8 中的 lambda 表达式 , 并不是完全闭包， lambda 表达式对值封闭，不对变量封闭。简单点来说就是局部变量在 lambda 表达式
中如果要使⽤，必须是声明 final 类型或者是隐式的 final 例如

```
int num = 123;
Consumer<Integer> print = () -> System.out.println(num);
```

就是可以的 , 虽然 num 没有被声明为 final ，但从整体来看，他和 final 类型的变量的表现是⼀致的，可如果是这样的代码

```
int num = 123;
num ++;
Consumer<Integer> print = () -> System.out.println(num);
```

则⽆法通过编译器，这就是对值封闭 ( 也就是栈上的变量封闭 )
如果上⽂中的 num 是实例变量或者是静态变量就没有这个限制。
看到这⾥，⾃然⽽然就会有疑问为什么会这样？或者说为什么要这么设计。理由有很多，例如函数的不变性，线程安全等等等，
这⾥我给⼀个简单的说明
关于 lambda 的限制
为什么局部变量会有限制⽽静态变量和全局变量就没有限制，因为局部变量是保存在栈上的，⽽众所周知，栈上的变量都隐
式的表现了它们仅限于它们所在的线程，⽽静态变量与实例变量是保存在静态区与堆中的，⽽这两块区域是线程共享的，所
以访问并没有问题。
现在我们假设如果 lambda 表达式可以局部变量的情况，实例变量存储在堆中，局部变量存储在栈上，⽽ lambda 表达式是在另
外⼀个线程中使⽤的，那么在访问局部变量的时候，因为线程不共享，因此 lambda 可能会在分配该变量的线程将这个变量收
回之后，去访问该变量。所以说， Java 在访问⾃由局部变量时，实际上是在访问它的副本，⽽不是访问原始变量。如果局部
变量仅仅赋值⼀次那就没有什么区别了。
严格保证这种限制会让你的代码变得⽆⽐安全，如果你学习或了解过⼀些经典的函数式语⾔的话，就会知道不变性的重要
性，这也是为什么 stream 流可以⼗分⽅便的改成并⾏流的重要原因之⼀。
总结

本篇介绍了四⼤函数接⼝和他们引申出的各类接⼝，终点是对不同种类⾏为的封装导致了设计出不同的函数接⼝，另外在使⽤函
数接⼝或者 lambda 表达式的时候，要注意 lambda 对值封闭这个特性。
