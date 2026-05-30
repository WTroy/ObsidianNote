---
type: dashboard
tags: [dashboard]
---

# 知识库首页

> 快速导航和知识库概览

## 快速入口

| 功能 | 链接 |
|------|------|
| 收件箱 | [[00-Inbox]] |
| 日记 | [[50-Daily]] |
| 内容地图 | [[60-MOC]] |
| 项目 | [[10-Projects]] |

---

## 最近修改的笔记

```dataview
TABLE file.mtime as "修改时间", file.folder as "目录"
FROM ""
WHERE file.name != "Home"
SORT file.mtime DESC
LIMIT 15
```

---

## 正在进行的项目

```dataview
TABLE status as "状态", start_date as "开始日期"
FROM #project
WHERE status = "active"
SORT start_date DESC
```

---

## 正在阅读的书

```dataview
TABLE author as "作者", rating as "评分"
FROM #book-note
WHERE status = "reading"
```

---

## 本周日记

```dataview
LIST
FROM "50-Daily"
WHERE date >= date(today) - dur(7 days)
SORT date DESC
```

---

## 未整理的笔记 (Inbox)

```dataview
TABLE file.ctime as "创建时间"
FROM "00-Inbox"
SORT file.ctime DESC
LIMIT 10
```
