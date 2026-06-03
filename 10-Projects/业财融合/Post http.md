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
*/ 8
private String getPost(String urlStr, String reqData) { 9

```java
OutputStream out = null;
String respData = "";
try {
URL url = new URL(urlStr);
HttpURLConnection con;
con = (HttpURLConnection) url.openConnection();
con.setDoOutput(true);
con.setDoInput(true);
con.setRequestMethod("POST");
con.setUseCaches(false);
con.setRequestProperty("Content-type", "text/xml;
charset=UTF-8");
con.setRequestProperty("Encoding", "UTF-8");
out = con.getOutputStream();
con.getOutputStream().write(reqData.getBytes());
out.flush();
out.close();
int code = con.getResponseCode();
String tempString = null;
StringBuffer sb1 = new StringBuffer();
if (code == HttpURLConnection.HTTP_OK) {
BufferedReader reader = new BufferedReader(
new
InputStreamReader(con.getInputStream(), "UTF-8"));
while ((tempString = reader.readLine()) != null)
{
sb1.append(tempString);
}
if (null != reader) {
reader.close();
}
```

```java
} else {
BufferedReader reader = new BufferedReader(
new
InputStreamReader(con.getErrorStream(), "UTF-8"));
```

// ⼀次读⼊⼀⾏，直到读⼊ null 为⽂件结束 41

```
while ((tempString = reader.readLine()) != null)
{
sb1.append(tempString);
}
if (null != reader) {
reader.close();
}
}
```

// 响应报⽂ 49

```yaml
respData = sb1.toString();
} catch (Exception e) {
```

logger.error("getPost 执⾏异常 ", e); 52

```java
}
return respData;
}
```

---
## 相关笔记
- [[SpringCloud]]
- [[油单信息接口]]
- [[JAVA并发编程实战]]
- [[SpringBoot学习笔记]]
