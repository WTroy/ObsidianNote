---
title: Thread的中断机制(interrupt)
source: 有道云笔记
imported: true
---

中断线程
线程的 thread.interrupt() ⽅法是中断线程，将会设置该线程的中断状态位，即设置为 true ，中断的结果线程是死亡、还
是等待新的任务或是继续运⾏⾄下⼀步，就取决于这个程序本身。线程会不时地检测这个中断标示位，以判断线程是否
应该被中断（中断标示值是否为 true ）。它并不像 stop ⽅法那样会中断⼀个正在运⾏的线程。
判断线程是否被中断
判断某个线程是否已被发送过中断请求，请使⽤ Thread.currentThread().isInterrupted() ⽅法（因为它将线程中断标示
位设置为 true 后，不会⽴刻清除中断标示位，即不会将中断标设置为 false ），⽽不要使⽤ thread.interrupted() （该⽅法
调⽤后会将中断标示位清除，即重新设置为 false ）⽅法来判断，下⾯是线程在循环中时的中断⽅式：
while(!Thread.currentThread().isInterrupted() && more work to do){
do more work
}
如何中断线程
如果⼀个线程处于了阻塞状态（如线程调⽤了 thread.sleep 、 thread.join 、 thread.wait 、 1.5 中的 condition.await 、以及
可中断的通道上的  I/O 操作⽅法后可进⼊阻塞状态），则在线程在检查中断标示时如果发现中断标示为 true ，则会在这
些阻塞⽅法（ sleep 、 join 、 wait 、 1.5 中的 condition.await 及可中断的通道上的  I/O 操作⽅法）调⽤处抛出
InterruptedException 异常，并且在抛出异常后⽴即将线程的中断标示位清除，即重新设置为 false 。抛出异常是为了线
程从阻塞状态醒过来，并在结束线程前让程序员有⾜够的时间来处理中断请求。
需要注意的事， synchronized 在获锁的过程中是不能被中断的，意思是说如果产⽣了死锁，则不可能被中断（请参考后
⾯的测试例⼦）。与 synchronized 功能相似的 reentrantLock.lock() ⽅法也是⼀样，它也不可中断的，即如果发⽣死
锁，那么 reentrantLock.lock() ⽅法⽆法终⽌，如果调⽤时被阻塞，则它⼀直阻塞到它获取到锁为⽌。但是如果调⽤带
超时的 tryLock ⽅法 reentrantLock.tryLock(long timeout, TimeUnit unit) ，那么如果线程在等待时被中断，将抛出⼀个
InterruptedException 异常，这是⼀个⾮常有⽤的特性，因为它允许程序打破死锁。你也可以调⽤
reentrantLock.lockInterruptibly() ⽅法，它就相当于⼀个超时设为⽆限的 tryLock ⽅法。
没有任何语⾔⽅⾯的需求⼀个被中断的线程应该终⽌。中断⼀个线程只是为了引起该线程的注意，被中断线程可以决定
如何应对中断。某些线程⾮常重要，以⾄于它们应该不理会中断，⽽是在处理完抛出的异常之后继续执⾏，但是更普遍
的情况是，⼀个线程将把中断看作⼀个终⽌请求，这种线程的 run ⽅法遵循如下形式：
public void run() {
try {
...
/*
* 不管循环⾥是否调⽤过线程阻塞的⽅法如 sleep 、 join 、 wait ，这⾥还是需要加上
* !Thread.currentThread().isInterrupted() 条件，虽然抛出异常后退出了循环，显
* 得⽤阻塞的情况下是多余的，但如果调⽤了阻塞⽅法但没有阻塞时，这样会更安全、更及时。
*/
while (!Thread.currentThread().isInterrupted()&& more work to do) {
do more work
}
} catch (InterruptedException e) {
// 线程在 wait 或 sleep 期间被中断了
} finally {
// 线程结束前做⼀些清理⼯作

}
}
上⾯是 while 循环在 try 块⾥，如果 try 在 while 循环⾥时，因该在 catch 块⾥重新设置⼀下中断标示，因为抛出
InterruptedException 异常后，中断标示位会⾃动清除，此时应该这样：
public void run() {
while (!Thread.currentThread().isInterrupted()&& more work to do) {
try {
...
sleep(delay);
} catch (InterruptedException e) {
Thread.currentThread().interrupt();// 重新设置中断标示
}
}
}
底层中断异常处理⽅式
另外不要在你的底层代码⾥捕获 InterruptedException 异常后不处理，会处理不当，如下：
void mySubTask(){
...
try{
sleep(delay);
}catch(InterruptedException e){}// 不要这样做
...
}
如果你不知道抛 InterruptedException 异常后如何处理，那么你有如下好的建议处理⽅式：
1 、在 catch ⼦句中，调⽤ Thread.currentThread.interrupt() 来设置中断状态（因为抛出异常后中断标示会被清除），让
外界通过判断 Thread.currentThread().isInterrupted() 标示来决定是否终⽌线程还是继续下去，应该这样做：
void mySubTask() {
...
try {
sleep(delay);
} catch (InterruptedException e) {
Thread.currentThread().interrupt();
}
...
}
2 、或者，更好的做法就是，不使⽤ try 来捕获这样的异常，让⽅法直接抛出：
void mySubTask() throws InterruptedException {
...
sleep(delay);
...
}
中断应⽤
使⽤中断信号量中断⾮阻塞状态的线程
中断线程最好的，最受推荐的⽅式是，使⽤共享变量（ shared variable ）发出信号，告诉线程必须停⽌正在运⾏的任
务。线程必须周期性的核查这⼀变量，然后有秩序地中⽌任务。 Example2 描述了这⼀⽅式：
class Example2 extends Thread {
volatile boolean stop = false;// 线程中断信号量

public static void main(String args[]) throws Exception {
Example2 thread = new Example2();
System.out.println("Starting thread...");
thread.start();
Thread.sleep(3000);
System.out.println("Asking thread to stop...");
// 设置中断信号量
thread.stop = true;
Thread.sleep(3000);
System.out.println("Stopping application...");
}
public void run() {
// 每隔⼀秒检测⼀下中断信号量
while (!stop) {
System.out.println("Thread is running...");
long time = System.currentTimeMillis();
/*
* 使⽤ while 循环模拟  sleep ⽅法，这⾥不要使⽤ sleep ，否则在阻塞时会  抛
* InterruptedException 异常⽽退出循环，这样 while 检测 stop 条件就不会执⾏，
* 失去了意义。
*/
while ((System.currentTimeMillis() - time < 1000)) {}
}
System.out.println("Thread exiting under request...");
}
}
使⽤ thread.interrupt() 中断⾮阻塞状态线程
虽然 Example2 该⽅法要求⼀些编码，但并不难实现。同时，它给予线程机会进⾏必要的清理⼯作。这⾥需注意⼀点的
是需将共享变量定义成 volatile 类型或将对它的⼀切访问封⼊同步的块 / ⽅法（ synchronized blocks/methods ）中。上
⾯是中断⼀个⾮阻塞状态的线程的常⻅做法，但对⾮检测 isInterrupted() 条件会更简洁 :
class Example2 extends Thread {
public static void main(String args[]) throws Exception {
Example2 thread = new Example2();
System.out.println("Starting thread...");
thread.start();
Thread.sleep(3000);
System.out.println("Asking thread to stop...");
// 发出中断请求
thread.interrupt();
Thread.sleep(3000);
System.out.println("Stopping application...");
}
public void run() {
// 每隔⼀秒检测是否设置了中断标示
while (!Thread.currentThread().isInterrupted()) {
System.out.println("Thread is running...");

long time = System.currentTimeMillis();
// 使⽤ while 循环模拟  sleep
while ((System.currentTimeMillis() - time < 1000) ) {
}
}
System.out.println("Thread exiting under request...");
}
}
到⽬前为⽌⼀切顺利！但是，当线程等待某些事件发⽣⽽被阻塞，⼜会发⽣什么？当然，如果线程被阻塞，它便不能核
查共享变量，也就不能停⽌。这在许多情况下会发⽣，例如调⽤ Object.wait() 、 ServerSocket.accept() 和
DatagramSocket.receive() 时，这⾥仅举出⼀些。
他们都可能永久的阻塞线程。即使发⽣超时，在超时期满之前持续等待也是不可⾏和不适当的，所以，要使⽤某种机制
使得线程更早地退出被阻塞的状态。下⾯就来看⼀下中断阻塞线程技术。
使⽤ thread.interrupt() 中断阻塞状态线程
Thread.interrupt() ⽅法不会中断⼀个正在运⾏的线程。这⼀⽅法实际上完成的是，设置线程的中断标示位，在线程受到
阻塞的地⽅（如调⽤ sleep 、 wait 、 join 等地⽅）抛出⼀个异常 InterruptedException ，并且中断状态也将被清除，这样
线程就得以退出阻塞的状态。下⾯是具体实现：
class Example3 extends Thread {
public static void main(String args[]) throws Exception {
Example3 thread = new Example3();
System.out.println("Starting thread...");
thread.start();
Thread.sleep(3000);
System.out.println("Asking thread to stop...");
thread.interrupt();// 等中断信号量设置后再调⽤
Thread.sleep(3000);
System.out.println("Stopping application...");
}
public void run() {
while (!Thread.currentThread().isInterrupted()) {
System.out.println("Thread running...");
try {
/*
* 如果线程阻塞，将不会去检查中断信号量 stop 变量，所  以 thread.interrupt()
* 会使阻塞线程从阻塞的地⽅抛出异常，让阻塞线程从阻塞状态逃离出来，并
* 进⾏异常块进⾏  相应的处理
*/
Thread.sleep(1000);// 线程阻塞，如果线程收到中断操作信号将抛出异常
} catch (InterruptedException e) {
System.out.println("Thread interrupted...");
/*
* 如果线程在调⽤  Object.wait() ⽅法，或者该类的  join() 、 sleep() ⽅法
* 过程中受阻，则其中断状态将被清除
*/
System.out.println(this.isInterrupted());// false

// 中不中断由⾃⼰决定，如果需要真真中断线程，则需要重新设置中断位，如果
// 不需要，则不⽤调⽤
Thread.currentThread().interrupt();
}
}
System.out.println("Thread exiting under request...");
}
}
⼀旦 Example3 中的 Thread.interrupt() 被调⽤，线程便收到⼀个异常，于是逃离了阻塞状态并确定应该停⽌。上⾯我们
还可以使⽤共享信号量来替换 !Thread.currentThread().isInterrupted() 条件，但不如它简洁。
死锁状态线程⽆法被中断
Example4试着去中断处于死锁状态的两个线程，但这两个线都没有收到任何中断信号（抛出异常），所以 interrupt() ⽅
法是不能中断死锁线程的，因为锁定的位置根本⽆法抛出异常：
class Example4 extends Thread {
public static void main(String args[]) throws Exception {
final Object lock1 = new Object();
final Object lock2 = new Object();
Thread thread1 = new Thread() {
public void run() {
deathLock(lock1, lock2);
}
};
Thread thread2 = new Thread() {
public void run() {
// 注意，这⾥在交换了⼀下位置
deathLock(lock2, lock1);
}
};
System.out.println("Starting thread...");
thread1.start();
thread2.start();
Thread.sleep(3000);
System.out.println("Interrupting thread...");
thread1.interrupt();
thread2.interrupt();
Thread.sleep(3000);
System.out.println("Stopping application...");
}
static void deathLock(Object lock1, Object lock2) {
try {
synchronized (lock1) {
Thread.sleep(10);// 不会在这⾥死掉
synchronized (lock2) {// 会锁在这⾥，虽然阻塞了，但不会抛异常
System.out.println(Thread.currentThread());
}
}
} catch (InterruptedException e) {
e.printStackTrace();

System.exit(1);
}
}
}
中断 I/O 操作
然⽽，如果线程在 I/O 操作进⾏时被阻塞，⼜会如何？ I/O 操作可以阻塞线程⼀段相当⻓的时间，特别是牵扯到⽹络应⽤
时。例如，服务器可能需要等待⼀个请求（ request ），⼜或者，⼀个⽹络应⽤程序可能要等待远端主机的响应。
实现此 InterruptibleChannel 接⼝的通道是可中断的：如果某个线程在可中断通道上因调⽤某个阻塞的  I/O 操作（常⻅的
操作⼀般有这些： serverSocketChannel. accept() 、 socketChannel.connect 、 socketChannel.open 、
socketChannel.read 、 socketChannel.write 、 fileChannel.read 、 fileChannel.write ）⽽进⼊阻塞状态，⽽另⼀个线程
⼜调⽤了该阻塞线程的  interrupt ⽅法，这将导致该通道被关闭，并且已阻塞线程接将会收到
ClosedByInterruptException ，并且设置已阻塞线程的中断状态。另外，如果已设置某个线程的中断状态并且它在通道
上调⽤某个阻塞的  I/O 操作，则该通道将关闭并且该线程⽴即接收到  ClosedByInterruptException ；并仍然设置其中断
状态。如果情况是这样，其代码的逻辑和第三个例⼦中的是⼀样的，只是异常不同⽽已。
如果你正使⽤通道（ channels ）（这是在 Java 1.4 中引⼊的新的 I/O API ），那么被阻塞的线程将收到⼀个
ClosedByInterruptException 异常。但是，你可能正使⽤ Java1.0 之前就存在的传统的 I/O ，⽽且要求更多的⼯作。既然
这样， Thread.interrupt() 将不起作⽤，因为线程将不会退出被阻塞状态。 Example5 描述了这⼀⾏为。尽管 interrupt()
被调⽤，线程也不会退出被阻塞状态，⽐如 ServerSocket 的 accept ⽅法根本不抛出异常。
很幸运，Java 平台为这种情形提供了⼀项解决⽅案，即调⽤阻塞该线程的套接字的 close() ⽅法。在这种情形下，如果线
程被 I/O 操作阻塞，当调⽤该套接字的 close ⽅法时，该线程在调⽤ accept 地⽅法将接收到⼀个 SocketException
（ SocketException 为 IOException 的⼦异常）异常，这与使⽤ interrupt() ⽅法引起⼀个 InterruptedException 异常被抛
出⾮常相似，（注，如果是流因读写阻塞后，调⽤流的 close ⽅法也会被阻塞，根本不能调⽤，更不会抛 IOExcepiton ，
此种情况下怎样中断？我想可以转换为通道来操作流可以解决，⽐如⽂件通道）。下⾯是具体实现：
class Example6 extends Thread {
volatile ServerSocket socket;
public static void main(String args[]) throws Exception {
Example6 thread = new Example6();
System.out.println("Starting thread...");
thread.start();
Thread.sleep(3000);
System.out.println("Asking thread to stop...");
Thread.currentThread().interrupt();// 再调⽤ interrupt ⽅法
thread.socket.close();// 再调⽤ close ⽅法
try {
Thread.sleep(3000);
} catch (InterruptedException e) {
}
System.out.println("Stopping application...");
}
public void run() {
try {

socket = new ServerSocket(8888);
} catch (IOException e) {
System.out.println("Could not create the socket...");
return;
}
while (!Thread.currentThread().isInterrupted()) {
System.out.println("Waiting for connection...");
try {
socket.accept();
} catch (IOException e) {
System.out.println("accept() failed or interrupted...");
Thread.currentThread().interrupt();// 重新设置中断标示位
}
}
System.out.println("Thread exiting under request...");
}
}
---
---
⼀、没有任何语⾔⽅⾯的需求⼀个被中断的线程应该终⽌。中断⼀个线程只是为了引起该线程的注意，被中断线程可以
决定如何应对中断。
⼆、对于处于 sleep ， join 等操作的线程，如果被调⽤ interrupt() 后，会抛出 InterruptedException ，然后线程的中断标
志位会由 true 重置为 false ，因为线程为了处理异常已经重新处于就绪状态。
三、不可中断的操作，包括进⼊ synchronized 段以及 Lock.lock() ， inputSteam.read() 等，调⽤ interrupt() 对于这⼏个
问题⽆效，因为它们都不抛出中断异常。如果拿不到资源，它们会⽆限期阻塞下去。
对于 Lock.lock() ，可以改⽤ Lock.lockInterruptibly() ，可被中断的加锁操作，它可以抛出中断异常。等同于等待时间⽆
限⻓的 Lock.tryLock(long time, TimeUnit unit) 。
对于 inputStream 等资源，有些 ( 实现了 interruptibleChannel 接⼝ ) 可以通过 close() ⽅法将资源关闭，对应的阻塞也会被
放开。

⾸先，看看 Thread 类⾥的⼏个⽅法：
上⾯列出了与中断有关的⼏个⽅法及其⾏为，可以看到 interrupt 是中断线程。如果不了解 Java 的中断机制，这样的⼀种
解释极容易造成误解，认为调⽤了线程的 interrupt ⽅法就⼀定会中断线程。
其实， Java 的中断是⼀种协作机制。也就是说调⽤线程对象的 interrupt ⽅法并不⼀定就中断了正在运⾏的线程，它只是
要求线程⾃⼰在合适的时机中断⾃⼰。每个线程都有⼀个 boolean 的中断状态（这个状态不在 Thread 的属性上），
interrupt ⽅法仅仅只是将该状态置为 true 。
⽐如对正常运⾏的线程调⽤ interrupt() 并不能终⽌他，只是改变了 interrupt 标示符。
public static boolean interrupted 测试当前线程是否已经中断。线程的中断状态  由
该⽅法清除。换句话说，如果连续两次调⽤该⽅
法，则第⼆次调⽤将返回  false 。
public boolean isInterrupted() 测试线程是否已经中断。线程的中断状态  不受该
⽅法的影响。
public void interrupt() 中断线程。

⼀般说来，如果⼀个⽅法声明抛出 InterruptedException ，表示该⽅法是可中断的 , ⽐如 wait,sleep,join ，也就是说可中
断⽅法会对 interrupt 调⽤做出响应（例如 sleep 响应 interrupt 的操作包括清除中断状态，抛出 InterruptedException ） ,
异常都是由可中断⽅法⾃⼰抛出来的，并不是直接由 interrupt ⽅法直接引起的。
Object.wait, Thread.sleep ⽅法，会不断的轮询监听  interrupted 标志位，发现其设置为 true 后，会停⽌阻塞并抛出
InterruptedException 异常。
---
---
看了以上的说明，对 java 中断的使⽤肯定是会了，但我想知道的是阻塞了的线程是如何通过 interuppt ⽅法完成停⽌阻
塞并抛出 interruptedException 的，这就要看 Thread 中 native 的 interuppt0 ⽅法了。
第⼀步学习 Java 的 JNI 调⽤ Native ⽅法。
第⼆步下载 openjdk 的源代码，找到⽬录结构⾥的 openjdk-src\jdk\src\share\native\java\lang\Thread.c ⽂件。
#include "jni.h"
#include "jvm.h"
#include "java_lang_Thread.h"
#define THD "Ljava/lang/Thread;"
#define OBJ "Ljava/lang/Object;"
#define STE "Ljava/lang/StackTraceElement;"
#define ARRAY_LENGTH(a) (sizeof(a)/sizeof(a[0]))
static JNINativeMethod methods[] = {
{"start0",           "()V",        (void *)&JVM_StartThread},
{"stop0",            "(" OBJ ")V", (void *)&JVM_StopThread},
{"isAlive",          "()Z",        (void *)&JVM_IsThreadAlive},
{"suspend0",         "()V",        (void *)&JVM_SuspendThread},
{"resume0",          "()V",        (void *)&JVM_ResumeThread},
{"setPriority0",     "(I)V",       (void *)&JVM_SetThreadPriority},
{"yield",            "()V",        (void *)&JVM_Yield},
{"sleep",            "(J)V",       (void *)&JVM_Sleep},
{"currentThread",    "()" THD,     (void *)&JVM_CurrentThread},
{"countStackFrames", "()I",        (void *)&JVM_CountStackFrames},
{"interrupt0",       "()V",        (void *)&JVM_Interrupt},
{"isInterrupted",    "(Z)Z",       (void *)&JVM_IsInterrupted},
{"holdsLock",        "(" OBJ ")Z", (void *)&JVM_HoldsLock},
{"getThreads",        "()[" THD,   (void *)&JVM_GetAllThreads},
{"dumpThreads",      "([" THD ")[[" STE, (void *)&JVM_DumpThreads},
};
#undef THD
#undef OBJ
#undef STE
JNIEXPORT void JNICALL
Java_java_lang_Thread_registerNatives(JNIEnv *env, jclass cls)
{

(*env)->RegisterNatives(env, cls, methods, ARRAY_LENGTH(methods));
}
暂时还看不太懂，先去学习⼀下 C 的⼀些基础。
未完待续 ...