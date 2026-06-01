---
title: Java变长参数
source: 有道云笔记
imported: true
related: ["栈帧(Stack Frame)"]
---

在  Java 5 中提供了变⻓参数，允许在调⽤⽅法时传⼊不定⻓度的参数。变⻓参数是  Java 的⼀个语法糖，本质上还是基
于数组的实现：
public class test{
public static void test(String...args){
// 本质上还是基于数组的实现：
for(String arg : args) {// 当作数组⽤ foreach 遍历
System.out.println(arg);
}
}
public static void main(String[] args) {
test("aa", "bb", "cc");
}
}
使⽤规则：
问：找出下⾯程序存在的问题并只允许修改调⽤相关代码将其修复好？
public class Demo {
public void print(String str, Integer... args) {}
public void print(String str, String... args) {}
}
// 调⽤
Demo demo = new Demo();
demo.print("hello");
demo.print("hello", null);
答：上⾯代码直接编译报错，因为调⽤处对于两个⽅法都能匹配，编译器不知道选哪个，所以报错了，故别让  null 值和空值威胁到变⻓
⽅法调⽤，对于上⾯调⽤部分来说修改如下即可运⾏：
Demo demo = new Demo();
String[] strs = null;
demo.print("hello", strs);
问：分别说说下⾯程序注释⾏有问题吗，为什么？
class Base {
void print(String... args) {
System.out.println("Base print.");
}
}
class Sub extends Base {
@Override
void print(String[] args) {
System.out.println("Sub print.");
⼀个⽅法只可以有⼀个变⻓参数
边⻓参数的位置必须是最后⼀个

}
}
Base base = new Sub();
base.print("hello");    //1
Sub sub = new Sub();
sub.print("hello");    //2
答：注释  1 能编译通过且打印为  Sub print. ，因为 base 引⽤变量把⼦类对象  sub 做了向上转型，形参列表是由⽗类决定的，当然
能通过。 **** 编译看左边，运⾏看右边。【当⽗类引⽤变量指向⼦类对象的时候，会将⼦类对象向上转型】
注释  2 编译报错为传递的参数 String 类型与⽅法需要的  String[] 类型不匹配，因为这时编译器看到⼦类覆写了⽗类的  print ⽅
法，所以会使⽤⼦类重新定义的  print ⽅法，尽管参数列表不匹配也不会再去⽗类匹配（
因为找到了就不再找了），故有了类型不匹配的编译错误。 --------- 【针对⼦类重写了⽗类⽅法，⽤⼦类变量指向⼦类对象时调⽤的情
况，先确定⽅法，再匹配参数】
**** 先确定该引⽤变量指向哪⼀个对象，其次看调⽤⽅法，之后再匹配参数列表，看是否回编译通过。
这段代码要特别注意上⾯⼦类重写⽗类的  print 是成⽴的，因为⽗类  Base 的  print ⽅法的  args 变⻓参数在编译成字节码后的表
现是⼀个  String 数组类型的形参，⽽⼦类重写时正是  String[] 类型，
所以⾃然就是重写⽽不是重载，故加上  @Override 也没有问题的。
使⽤场景：在不确定⽅法需要处理的对象的数量时可以使⽤可变⻓参数，会使得⽅法调⽤更简单

---
## 相关笔记
- [[栈帧(Stack Frame)]]