---
title: Post http
source: 有道云笔记
imported: true
related: ["SpringCloud", "油单信息接口", "JAVA并发编程实战", "SpringBoot学习笔记"]
tags: ["工具类", "HTTP请求", "Java", "代码片段"]
summary: 一个Java实现的通用POST HTTP请求工具方法
---

Post http
/**1
* http 请求包装⽅法，⽅法类型 POST2
* 可以考虑⼯具类3
* 4
* @param urlStr5
* @param reqData6
* @return7
*/ 8
private String getPost(String urlStr, String reqData) { 9
OutputStream out = null; 10
String respData = ""; 11
try { 12
URL url = new URL(urlStr); 13
HttpURLConnection con; 14
con = (HttpURLConnection) url.openConnection(); 15
con.setDoOutput(true); 16
con.setDoInput(true); 17
con.setRequestMethod("POST"); 18
con.setUseCaches(false); 19
con.setRequestProperty("Content-type", "text/xml;
charset=UTF-8");
20
con.setRequestProperty("Encoding", "UTF-8"); 21
out = con.getOutputStream(); 22
con.getOutputStream().write(reqData.getBytes()); 23
out.flush(); 24
out.close(); 25
int code = con.getResponseCode(); 26
String tempString = null; 27
StringBuffer sb1 = new StringBuffer(); 28
if (code == HttpURLConnection.HTTP_OK) { 29
BufferedReader reader = new BufferedReader( 30
new
InputStreamReader(con.getInputStream(), "UTF-8"));
31
while ((tempString = reader.readLine()) != null)
{
32
sb1.append(tempString); 33
} 34
if (null != reader) { 35
reader.close(); 36
} 37

} else { 38
BufferedReader reader = new BufferedReader( 39
new
InputStreamReader(con.getErrorStream(), "UTF-8"));
40
// ⼀次读⼊⼀⾏，直到读⼊ null 为⽂件结束 41
while ((tempString = reader.readLine()) != null)
{
42
sb1.append(tempString); 43
} 44
if (null != reader) { 45
reader.close(); 46
} 47
} 48
// 响应报⽂ 49
respData = sb1.toString(); 50
} catch (Exception e) { 51
logger.error("getPost 执⾏异常 ", e); 52
} 53
return respData; 54
}55


---
## 相关笔记
- [[SpringBoot学习笔记]]