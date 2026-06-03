---
title: pdf下载
source: 有道云笔记
imported: true
related: ["pdf下载", "航油TODO", "油单信息接口", "超时未确认加油单提醒记录保存", "开发笔记", "备份input数据"]
---

/**1
* 下载 PDF2
* 根据新增字段  EFS ：储存的是 pdf ⽂件的 base64 编码数据3
* 根据 base64 解码为 pdf ⽂件4
* 命名规则是：加油单号 .pdf5
*6
* @param event7
* @throws Exception8
*/9
public void onClick$btnDownload(Event event) throws Exception{10

```
FuelInput tmp = (FuelInput) listboxDS.getSelectedItem().getValue();
String billNo = tmp.getRefuelBillNo();
String efs = tmp.getEfs();
if(efs == null || "".equals(efs)){
```

Messagebox.show(" 当前所选数据没有相关的⽂档信息 !");15
return;16
}17
// 当前⽂件不需要存档，所以不使⽤相关的⽂件路径18
// String

```java
fileuploadpath=WebUtils.getApplicationParameter(Constants.APPLICATION_FILE_UPLOAD
_PATH);
File file=new File(billNo + ".pdf");
```

// tomcat 临时⽬录下如果存在相同⽂件名的⽂件，删除，创建最新⽂件21
if(file.exists())file.delete();22
file.createNewFile();23
byte[] decodedBytes = Base64.decodeBase64(efs);25

```java
FileOutputStream fos = new FileOutputStream(file);
fos.write(decodedBytes);
fos.close();
Filedownload.save(file, null);
}
```

---
## 相关笔记
- [[pdf下载]]
- [[航油TODO]]
- [[油单信息接口]]
- [[超时未确认加油单提醒记录保存]]
- [[开发笔记]]
- [[备份input数据]]
