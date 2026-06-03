---
title: 视图 V_FULE_INVOICE_RECEIPT_COSTS 的优化
source: 有道云笔记
imported: true
related: ["```json", "备份开账存储过程", "航油TODO", "国内油价确认", "油单信息接口", "预提期间归属问题修复的存储过程", "近期的SQL脚本", "FOFAS系统迁移", "智慧航油拆分"]
---

全字段的新视图：

```sql
CREATE OR REPLACE FORCE VIEW "FOFAS"."V_FULE_INVOICE_RECEIPT_COSTS" (
"ID", "NAME", "CODE", "MEMO", "VERSION", "CREATETIME", "CREATOR",
"UPDATETIME", "UPDATER",
"FLIGHT_DATE", "CARRIER", "FLIGHT_NO", "ORI_ENG", "DES_ENG", "FLIGHT_TYPE",
"DISTANCE",
"SEATS", "AC_FAMILY", "TAIL_NO", "ACTUAL_DPT_TIME", "ACTUAL_ARR_TIME",
"AT_BRIDGE",
"BRIDGE_TYPE", "BRIDGE_TIME", "BLOCK_ON_TIME", "BLOCK_OFF_TIME",
"FLIGHT_SEAT_DISTANCE",
"FLIGHT_PASSENGER_DISTANCE", "FLIGHT_PASSENGER_AMT", "AGENT",
"FLIGHT_LINE_TYPE",
"FLT_STATUS", "LEG_ID", "SEAT_QTY_F", "SEAT_QTY_C", "SEAT_QTY_Y",
"PLAN_DEPART_TIME",
"PLAN_ARRIVAL_TIME", "LINE_SERIAL", "ORIG_AIRPORT_CD", "DEST_AIRPORT_CD",
"CARRIER_O",
"ADULT_QTY", "CHILD_QTY", "INFANT_QTY", "FLT_DT_UTC", "SRV_TYPE",
"LINE_SEAT_QTY_F",
"LINE_SEAT_QTY_C", "LINE_SEAT_QTY_Y", "LINE_ADULT_QTY", "LINE_CHILD_QTY",
"LINE_INFANT_QTY",
"EST_ARRIVAL_TIME", "EST_DEPART_TIME", "FLTID", "SHEET_ADULTS",
"SHEET_CHILDREN",
"SHEET_INFANTS", "TIMESTAMPNUM", "VERSION_DATE", "INVOICE_NO", "RECEIPT_NO",
"RECEIPT_ID",
"REFUELED_ID", "TYPE_ID", "TIMESTAMP", "CW_ACTYPE", "FLIGHT_TYPE_CODE",
"SHARE_MONEY",
"QTY", "MEASURE_UNIT", "AMOUNT", "CURRENCY", "FUEL_AMOUNT_RMB",
"FUEL_AMOUNT_RATE",
"ACCRUEDAMOUNT", "ACCRUEDAMOUNTRMB", "EXCHANGE_RATE", "IF_MATCH", "GL_DATE",
"BATCH_NUM"
) AS
WITH base_union AS (
SELECT
c.*,
d.qty, d.measure_unit, d.amount, d.currency,
d.fuel_amount_rmb, d.fuel_amount_rate, d.fuel_amount as acc_val,
d.refueling_date as match_date, d.refueling_airport as match_airport
FROM t_fule_invoice_receipt_costs c
JOIN t_fuel_invoice_receipt_detail d ON c.receipt_id = d.proxyid AND
c.timestamp = d.timestamp and c.TIMESTAMP > '1704038400'
WHERE c.type_id = '1'
UNION ALL
SELECT
c.*,
```

d.REFUELED, d.MEASURE_UNITS, d.amount, d.currencys,29
d.fuel_amount_rmb, d.fuel_amount_rate, d.amount,30
c.flight_date, c.ori_eng31

```sql
FROM t_fule_invoice_receipt_costs c
JOIN t_flight_fuelinfo_detail d ON c.refueled_id = d.id AND c.timestamp =
d.timestamp and c.TIMESTAMP > '1704038400'
WHERE c.type_id = '2'
UNION ALL
SELECT
c.*,
d.QTY_KG, d.MEASURE_UNITS, d.amount, d.currencys,
d.fuel_amount_rmb, d.fuel_amount_rate, d.amount,
c.flight_date, c.ori_eng
FROM t_fule_invoice_receipt_costs c
JOIN t_type_line_detail d ON c.refueled_id = d.id AND c.timestamp =
d.timestamp and c.TIMESTAMP > '1704038400'
WHERE c.type_id IN ('3', '4')
)
SELECT
U."ID", U."NAME", U."CODE", U."MEMO", U."VERSION", U."CREATETIME",
U."CREATOR", U."UPDATETIME", U."UPDATER",
U."FLIGHT_DATE", U."CARRIER", U."FLIGHT_NO", U."ORI_ENG", U."DES_ENG",
U."FLIGHT_TYPE", U."DISTANCE",
U."SEATS", U."AC_FAMILY", U."TAIL_NO", U."ACTUAL_DPT_TIME",
U."ACTUAL_ARR_TIME", U."AT_BRIDGE",
U."BRIDGE_TYPE", U."BRIDGE_TIME", U."BLOCK_ON_TIME", U."BLOCK_OFF_TIME",
U."FLIGHT_SEAT_DISTANCE",
U."FLIGHT_PASSENGER_DISTANCE", U."FLIGHT_PASSENGER_AMT", U."AGENT",
U."FLIGHT_LINE_TYPE",
U."FLT_STATUS", U."LEG_ID", U."SEAT_QTY_F", U."SEAT_QTY_C", U."SEAT_QTY_Y",
U."PLAN_DEPART_TIME",
U."PLAN_ARRIVAL_TIME", U."LINE_SERIAL", U."ORIG_AIRPORT_CD",
U."DEST_AIRPORT_CD", U."CARRIER_O",
U."ADULT_QTY", U."CHILD_QTY", U."INFANT_QTY", U."FLT_DT_UTC", U."SRV_TYPE",
U."LINE_SEAT_QTY_F",
U."LINE_SEAT_QTY_C", U."LINE_SEAT_QTY_Y", U."LINE_ADULT_QTY",
U."LINE_CHILD_QTY", U."LINE_INFANT_QTY",
U."EST_ARRIVAL_TIME", U."EST_DEPART_TIME", U."FLTID", U."SHEET_ADULTS",
U."SHEET_CHILDREN",
U."SHEET_INFANTS", U."TIMESTAMPNUM", U."VERSION_DATE", U."INVOICE_NO",
U."RECEIPT_NO", U."RECEIPT_ID",
U."REFUELED_ID", U."TYPE_ID", U."TIMESTAMP", U."CW_ACTYPE",
U."FLIGHT_TYPE_CODE", U."SHARE_MONEY",
U.qty, U.measure_unit,
CASE
```

精简之后的视图（希望让 hash join 数据可以在内存中放下，不要去⾛磁盘 io ）：
WHEN AP.area_code = 'DOME' AND U.TYPE_ID != '1' THEN ROUND(U.amount * (1

```sql
+ R.EXCHANGE_RATE), 2)
ELSE U.amount
END,
U.currency,
CASE
WHEN AP.area_code = 'DOME' THEN ROUND(U.fuel_amount_rmb * (1 +
R.EXCHANGE_RATE), 2)
ELSE U.fuel_amount_rmb
END,
U.fuel_amount_rate, U.acc_val, U.fuel_amount_rmb, R.EXCHANGE_RATE,
P.IF_MATCH, P.GL_DATE, P.BATCH_NUM
FROM base_union U
LEFT JOIN t_fuel_rate_conversion R ON U.match_date BETWEEN R.apply_date AND
R.expiry_date
LEFT JOIN t_airport AP ON AP.airport_code3 = U.match_airport
LEFT JOIN dc_flight_plan P ON P.id = U.id;
CREATE OR REPLACE FORCE VIEW "FOFAS"."V_FULE_INVOICE_RECEIPT_COSTS" (
"ID",
"FLIGHT_DATE", "CARRIER", "FLIGHT_NO", "ORI_ENG", "DES_ENG", "FLIGHT_TYPE",
"TAIL_NO", "PLAN_DEPART_TIME",
"PLAN_ARRIVAL_TIME", "INVOICE_NO", "RECEIPT_NO", "RECEIPT_ID",
"REFUELED_ID", "TYPE_ID", "TIMESTAMP", "CW_ACTYPE", "FLIGHT_TYPE_CODE",
"SHARE_MONEY",
"QTY", "MEASURE_UNIT", "AMOUNT", "CURRENCY", "FUEL_AMOUNT_RMB",
"FUEL_AMOUNT_RATE",
"ACCRUEDAMOUNT", "ACCRUEDAMOUNTRMB", "EXCHANGE_RATE", "IF_MATCH", "GL_DATE",
"BATCH_NUM"
) AS
WITH base_union AS (
SELECT
c.ID, c.FLIGHT_DATE, c.CARRIER, c.FLIGHT_NO, c.ORI_ENG, c.DES_ENG,
c.FLIGHT_TYPE, c.TAIL_NO, c.PLAN_DEPART_TIME, c.PLAN_ARRIVAL_TIME, c.INVOICE_NO,
c.RECEIPT_NO, c.RECEIPT_ID, c.REFUELED_ID, c.TYPE_ID, c.TIMESTAMP, c.CW_ACTYPE,
c.FLIGHT_TYPE_CODE, c.SHARE_MONEY,
d.qty, d.measure_unit, d.amount, d.currency,
d.fuel_amount_rmb, d.fuel_amount_rate, d.fuel_amount as acc_val,
d.refueling_date as match_date, d.refueling_airport as match_airport
FROM t_fule_invoice_receipt_costs c
JOIN t_fuel_invoice_receipt_detail d ON c.receipt_id = d.proxyid AND
c.timestamp = d.timestamp and c.TIMESTAMP > '1704038400'
WHERE c.type_id = '1'
UNION ALL
SELECT
c.ID, c.FLIGHT_DATE, c.CARRIER, c.FLIGHT_NO, c.ORI_ENG, c.DES_ENG,
c.FLIGHT_TYPE, c.TAIL_NO, c.PLAN_DEPART_TIME, c.PLAN_ARRIVAL_TIME, c.INVOICE_NO,
c.RECEIPT_NO, c.RECEIPT_ID, c.REFUELED_ID, c.TYPE_ID, c.TIMESTAMP, c.CW_ACTYPE,
c.FLIGHT_TYPE_CODE, c.SHARE_MONEY,
d.REFUELED, d.MEASURE_UNITS, d.amount, d.currencys,
d.fuel_amount_rmb, d.fuel_amount_rate, d.amount,
c.flight_date, c.ori_eng
FROM t_fule_invoice_receipt_costs c
JOIN t_flight_fuelinfo_detail d ON c.refueled_id = d.id AND c.timestamp =
d.timestamp and c.TIMESTAMP > '1704038400'
WHERE c.type_id = '2'
UNION ALL
SELECT
c.ID, c.FLIGHT_DATE, c.CARRIER, c.FLIGHT_NO, c.ORI_ENG, c.DES_ENG,
c.FLIGHT_TYPE, c.TAIL_NO, c.PLAN_DEPART_TIME, c.PLAN_ARRIVAL_TIME, c.INVOICE_NO,
c.RECEIPT_NO, c.RECEIPT_ID, c.REFUELED_ID, c.TYPE_ID, c.TIMESTAMP, c.CW_ACTYPE,
c.FLIGHT_TYPE_CODE, c.SHARE_MONEY,
d.QTY_KG, d.MEASURE_UNITS, d.amount, d.currencys,
d.fuel_amount_rmb, d.fuel_amount_rate, d.amount,
c.flight_date, c.ori_eng
FROM t_fule_invoice_receipt_costs c
JOIN t_type_line_detail d ON c.refueled_id = d.id AND c.timestamp =
d.timestamp and c.TIMESTAMP > '1704038400'
WHERE c.type_id IN ('3', '4')
)
SELECT
U."ID",
U."FLIGHT_DATE", U."CARRIER", U."FLIGHT_NO", U."ORI_ENG", U."DES_ENG",
U."FLIGHT_TYPE", U."TAIL_NO", U."PLAN_DEPART_TIME",
U."PLAN_ARRIVAL_TIME",U."INVOICE_NO", U."RECEIPT_NO", U."RECEIPT_ID",
U."REFUELED_ID", U."TYPE_ID", U."TIMESTAMP", U."CW_ACTYPE",
U."FLIGHT_TYPE_CODE", U."SHARE_MONEY",
U.qty, U.measure_unit,
CASE
WHEN AP.area_code = 'DOME' AND U.TYPE_ID != '1' THEN ROUND(U.amount * (
+ R.EXCHANGE_RATE), 2)
ELSE U.amount
END,
U.currency,
CASE
WHEN AP.area_code = 'DOME' THEN ROUND(U.fuel_amount_rmb * (1 +
R.EXCHANGE_RATE), 2)
```

索引：
原始视图：
ELSE U.fuel_amount_rmb 50

```sql
END,
U.fuel_amount_rate, U.acc_val, U.fuel_amount_rmb, R.EXCHANGE_RATE,
P.IF_MATCH, P.GL_DATE, P.BATCH_NUM
FROM base_union U
LEFT JOIN t_fuel_rate_conversion R ON U.match_date BETWEEN R.apply_date AND
R.expiry_date
LEFT JOIN t_airport AP ON AP.airport_code3 = U.match_airport
LEFT JOIN dc_flight_plan P ON P.id = U.id;
CREATE INDEX IDX_COSTS_FLIGHTINFO ON T_FULE_INVOICE_RECEIPT_COSTS (FLIGHT_DATE,
FLIGHT_NO, ORI_ENG, DES_ENG, TAIL_NO);
CREATE INDEX idx_costs_comp ON t_fule_invoice_receipt_costs (type_id, timestamp,
receipt_id);
CREATE INDEX idx_costs_comp1 ON t_fule_invoice_receipt_costs (type_id,
timestamp, refueled_id);
CREATE INDEX idx_detail_pt ON T_FUEL_INVOICE_RECEIPT_DETAIL (PROXYID, TIMESTAMP);
CREATE INDEX idx_rate_date ON t_fuel_rate_conversion (apply_date, expiry_date);
create or replace force view "V_FULE_INVOICE_RECEIPT_COSTS"
("ID","NAME","CODE","MEMO","VERSION","CREATETIME","CREATOR","UPDATETIME","UPDATER
","FLIGHT_DATE","CARRIER","FLIGHT_NO","ORI_ENG","DES_ENG","FLIGHT_TYPE","DISTANCE
","SEATS","AC_FAMILY","TAIL_NO","ACTUAL_DPT_TIME","ACTUAL_ARR_TIME","AT_BRIDGE","
BRIDGE_TYPE","BRIDGE_TIME","BLOCK_ON_TIME","BLOCK_OFF_TIME","FLIGHT_SEAT_DISTANCE
","FLIGHT_PASSENGER_DISTANCE","FLIGHT_PASSENGER_AMT","AGENT","FLIGHT_LINE_TYPE","
FLT_STATUS","LEG_ID","SEAT_QTY_F","SEAT_QTY_C","SEAT_QTY_Y","PLAN_DEPART_TIME","P
LAN_ARRIVAL_TIME","LINE_SERIAL","ORIG_AIRPORT_CD","DEST_AIRPORT_CD","CARRIER_O","
ADULT_QTY","CHILD_QTY","INFANT_QTY","FLT_DT_UTC","SRV_TYPE","LINE_SEAT_QTY_F","LI
NE_SEAT_QTY_C","LINE_SEAT_QTY_Y","LINE_ADULT_QTY","LINE_CHILD_QTY","LINE_INFANT_Q
TY","EST_ARRIVAL_TIME","EST_DEPART_TIME","FLTID","SHEET_ADULTS","SHEET_CHILDREN",
"SHEET_INFANTS","TIMESTAMPNUM","VERSION_DATE","INVOICE_NO","RECEIPT_NO","RECEIPT_
ID","REFUELED_ID","TYPE_ID","TIMESTAMP","CW_ACTYPE","FLIGHT_TYPE_CODE","SHARE_MON
EY","QTY","MEASURE_UNIT","AMOUNT","CURRENCY","FUEL_AMOUNT_RMB","FUEL_AMOUNT_RATE"
,"ACCRUEDAMOUNT","ACCRUEDAMOUNTRMB","EXCHANGE_RATE","IF_MATCH","GL_DATE","BATCH_N
UM")
```

as select
a."ID",a."NAME",a."CODE",a."MEMO",a."VERSION",a."CREATETIME",a."CREATOR",a."UPDAT
ETIME",a."UPDATER",a."FLIGHT_DATE",a."CARRIER",a."FLIGHT_NO",a."ORI_ENG",a."DES_E
NG",a."FLIGHT_TYPE",a."DISTANCE",a."SEATS",a."AC_FAMILY",a."TAIL_NO",a."ACTUAL_DP
T_TIME",a."ACTUAL_ARR_TIME",a."AT_BRIDGE",a."BRIDGE_TYPE",a."BRIDGE_TIME",a."BLOC
K_ON_TIME",a."BLOCK_OFF_TIME",a."FLIGHT_SEAT_DISTANCE",a."FLIGHT_PASSENGER_DISTAN
CE",a."FLIGHT_PASSENGER_AMT",a."AGENT",a."FLIGHT_LINE_TYPE",a."FLT_STATUS",a."LEG
_ID",a."SEAT_QTY_F",a."SEAT_QTY_C",a."SEAT_QTY_Y",a."PLAN_DEPART_TIME",a."PLAN_AR
RIVAL_TIME",a."LINE_SERIAL",a."ORIG_AIRPORT_CD",a."DEST_AIRPORT_CD",a."CARRIER_O"
,a."ADULT_QTY",a."CHILD_QTY",a."INFANT_QTY",a."FLT_DT_UTC",a."SRV_TYPE",a."LINE_S
EAT_QTY_F",a."LINE_SEAT_QTY_C",a."LINE_SEAT_QTY_Y",a."LINE_ADULT_QTY",a."LINE_CHI
LD_QTY",a."LINE_INFANT_QTY",a."EST_ARRIVAL_TIME",a."EST_DEPART_TIME",a."FLTID",a.
"SHEET_ADULTS",a."SHEET_CHILDREN",a."SHEET_INFANTS",a."TIMESTAMPNUM",a."VERSION_D
ATE",a."INVOICE_NO",a."RECEIPT_NO",a."RECEIPT_ID",a."REFUELED_ID",a."TYPE_ID",a."
TIMESTAMP",a."CW_ACTYPE",a."FLIGHT_TYPE_CODE",a."SHARE_MONEY",a."QTY",a."MEASURE_
UNIT",a."AMOUNT",a."CURRENCY",a."FUEL_AMOUNT_RMB",a."FUEL_AMOUNT_RATE",a."ACCRUED
AMOUNT",a."ACCRUEDAMOUNTRMB",a."EXCHANGE_RATE", p.if_match,p.gl_date,p.batch_num

```sql
from (select c.*,
d.qty qty,d.measure_unit,
```

d.amount, -- 含税⾦额原币6
d.currency,7

```
case
when a.area_code = 'DOME' then
round(d.fuel_amount_rmb * (1 + r.exchange_rate), 2)
else
d.fuel_amount_rmb
```

```sql
end fuel_amount_rmb, -- 含税⾦额⼈⺠币
```

d.fuel_amount_rate, -- 币种转换汇率14
d.fuel_amount accruedamount, -- 不含税⾦额原币15
d.fuel_amount_rmb accruedamountrmb, -- 不含税⾦额原币16
R.EXCHANGE_RATE17

```sql
from t_fule_invoice_receipt_costs  c,
t_fuel_invoice_receipt_detail d,
t_airport                     a,
t_fuel_rate_conversion        r
where c.receipt_id = d.proxyid
and c.type_id =
and c.timestamp = d.timestamp
and a.airport_code3 = d.refueling_airport
and d.refueling_date between r.apply_date and r.expiry_date
union all
select c.*,
d.REFUELED qty,d.MEASURE_UNITS measure_unit,
case
when a.area_code = 'DOME' then
round(d.amount * (1 + r.exchange_rate), 2)
else
d.amount
end amount,
d.currencys,
case
when a.area_code = 'DOME' then
round(d.fuel_amount_rmb * (1 + r.exchange_rate), 2)
else
d.fuel_amount_rmb
end fuel_amount_rmb,
d.fuel_amount_rate,
```

d.amount accruedamount, -- 不含税⾦额44
d.fuel_amount_rmb accruedamountrmb, -- 不含税⾦额原币45
R.EXCHANGE_RATE46

```sql
from t_fule_invoice_receipt_costs c,
t_flight_fuelinfo_detail     d,
t_airport                    a,
t_fuel_rate_conversion       r
where c.refueled_id = d.id
and c.type_id =
and a.airport_code3 = c.ori_eng
--and  d.FUEL_AMOUNT_RMB > 054
and c.timestamp = d.timestamp
and c.flight_date between r.apply_date and r.expiry_date
union all
select c.*,
d.QTY_KG qty,d.MEASURE_UNITS measure_unit,
case
when a.area_code = 'DOME' then
round(d.amount * (1 + r.exchange_rate), 2)
else
d.amount
end amount,
d.currencys,
case
when a.area_code = 'DOME' then
round(d.fuel_amount_rmb * (1 + r.exchange_rate), 2)
else
d.fuel_amount_rmb
end fuel_amount_rmb,
d.fuel_amount_rate,
```

d.amount accruedamount, -- 不含税⾦额74

d.fuel_amount_rmb accruedamountrmb, -- 不含税⾦额原币75
R.EXCHANGE_RATE76

```sql
from t_fule_invoice_receipt_costs c,
t_type_line_detail           d,
t_airport                    a,
t_fuel_rate_conversion       r
where c.refueled_id = d.id
and c.type_id in (3, 4)
and a.airport_code3 = c.ori_eng
--AND d.FUEL_AMOUNT_RMB > 084
and c.timestamp = d.timestamp
and c.flight_date between r.apply_date and r.expiry_date) a,
/*       (select max(timestamp) tamestamp,
to_char(flight_date, 'yyyymm') flight_mouth
from t_fule_invoice_receipt_costs
group by to_char(flight_date, 'yyyymm')) b,*/
dc_flight_plan p
where /*a.timestamp = b.tamestamp
and to_char(a.flight_date, 'YYYYMM') = b.flight_mouth
and*/ p.id = a.id
```

---
## 相关笔记
- [[```json]]
- [[备份开账存储过程]]
- [[航油TODO]]
- [[国内油价确认]]
- [[油单信息接口]]
- [[预提期间归属问题修复的存储过程]]
- [[近期的SQL脚本]]
- [[FOFAS系统迁移]]
- [[智慧航油拆分]]
