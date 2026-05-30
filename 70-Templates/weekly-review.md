---
type: weekly-review
week: <% tp.date.now("YYYY") %>-W<% tp.date.now("WW") %>
date: <% tp.date.now("YYYY-MM-DD") %>
tags: [weekly-review]
---

# 周回顾 <% tp.date.now("YYYY") %> 第 <% tp.date.now("WW") %> 周

## 本周完成
- 

## 本周收获


## 未完成 / 下周计划
- [ ] 

## 本周日记回顾
```dataview
LIST
FROM "50-Daily"
WHERE date >= date("<% tp.date.now("YYYY-MM-DD", -7) %>") AND date <= date("<% tp.date.now("YYYY-MM-DD") %>")
SORT date ASC
```
