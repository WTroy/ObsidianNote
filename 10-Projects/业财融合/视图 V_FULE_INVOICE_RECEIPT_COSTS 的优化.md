---
title: 视图 V_FULE_INVOICE_RECEIPT_COSTS 的优化
source: 有道云笔记
imported: true
related: ["```json"]
related: ["备份开账存储过程", "航油TODO", "国内油价确认", "油单信息接口", "预提期间归属问题修复的存储过程"]
related: ["近期的SQL脚本", "航油TODO", "FOFAS系统迁移", "预提期间归属问题修复的存储过程", "智慧航油拆分"]
---

全字段的新视图：
CREATE OR REPLACE FORCE VIEW "FOFAS"."V_FULE_INVOICE_RECEIPT_COSTS" (1
"ID", "NAME", "CODE", "MEMO", "VERSION", "CREATETIME", "CREATOR",
"UPDATETIME", "UPDATER",
2
"FLIGHT_DATE", "CARRIER", "FLIGHT_NO", "ORI_ENG", "DES_ENG", "FLIGHT_TYPE",
"DISTANCE",
3
"SEATS", "AC_FAMILY", "TAIL_NO", "ACTUAL_DPT_TIME", "ACTUAL_ARR_TIME",
"AT_BRIDGE",
4
"BRIDGE_TYPE", "BRIDGE_TIME", "BLOCK_ON_TIME", "BLOCK_OFF_TIME",
"FLIGHT_SEAT_DISTANCE",
5
"FLIGHT_PASSENGER_DISTANCE", "FLIGHT_PASSENGER_AMT", "AGENT",
"FLIGHT_LINE_TYPE",
6
"FLT_STATUS", "LEG_ID", "SEAT_QTY_F", "SEAT_QTY_C", "SEAT_QTY_Y",
"PLAN_DEPART_TIME",
7
"PLAN_ARRIVAL_TIME", "LINE_SERIAL", "ORIG_AIRPORT_CD", "DEST_AIRPORT_CD",
"CARRIER_O",
8
"ADULT_QTY", "CHILD_QTY", "INFANT_QTY", "FLT_DT_UTC", "SRV_TYPE",
"LINE_SEAT_QTY_F",
9
"LINE_SEAT_QTY_C", "LINE_SEAT_QTY_Y", "LINE_ADULT_QTY", "LINE_CHILD_QTY",
"LINE_INFANT_QTY",
10
"EST_ARRIVAL_TIME", "EST_DEPART_TIME", "FLTID", "SHEET_ADULTS",
"SHEET_CHILDREN",
11
"SHEET_INFANTS", "TIMESTAMPNUM", "VERSION_DATE", "INVOICE_NO", "RECEIPT_NO",
"RECEIPT_ID",
12
"REFUELED_ID", "TYPE_ID", "TIMESTAMP", "CW_ACTYPE", "FLIGHT_TYPE_CODE",
"SHARE_MONEY",
13
"QTY", "MEASURE_UNIT", "AMOUNT", "CURRENCY", "FUEL_AMOUNT_RMB",
"FUEL_AMOUNT_RATE",
14
"ACCRUEDAMOUNT", "ACCRUEDAMOUNTRMB", "EXCHANGE_RATE", "IF_MATCH", "GL_DATE",
"BATCH_NUM"
15
) AS16
WITH base_union AS (17
SELECT 18
c.*, 19
d.qty, d.measure_unit, d.amount, d.currency,20
d.fuel_amount_rmb, d.fuel_amount_rate, d.fuel_amount as acc_val,21
d.refueling_date as match_date, d.refueling_airport as match_airport22
FROM t_fule_invoice_receipt_costs c23
JOIN t_fuel_invoice_receipt_detail d ON c.receipt_id = d.proxyid AND
c.timestamp = d.timestamp and c.TIMESTAMP > '1704038400'
24
WHERE c.type_id = '1'25
UNION ALL26
SELECT 27
c.*, 28

d.REFUELED, d.MEASURE_UNITS, d.amount, d.currencys,29
d.fuel_amount_rmb, d.fuel_amount_rate, d.amount,30
c.flight_date, c.ori_eng31
FROM t_fule_invoice_receipt_costs c32
JOIN t_flight_fuelinfo_detail d ON c.refueled_id = d.id AND c.timestamp =
d.timestamp and c.TIMESTAMP > '1704038400'
33
WHERE c.type_id = '2'34
UNION ALL35
SELECT 36
c.*, 37
d.QTY_KG, d.MEASURE_UNITS, d.amount, d.currencys,38
d.fuel_amount_rmb, d.fuel_amount_rate, d.amount,39
c.flight_date, c.ori_eng40
FROM t_fule_invoice_receipt_costs c41
JOIN t_type_line_detail d ON c.refueled_id = d.id AND c.timestamp =
d.timestamp and c.TIMESTAMP > '1704038400'
42
WHERE c.type_id IN ('3', '4')43
)44
SELECT 45
U."ID", U."NAME", U."CODE", U."MEMO", U."VERSION", U."CREATETIME",
U."CREATOR", U."UPDATETIME", U."UPDATER",
46
U."FLIGHT_DATE", U."CARRIER", U."FLIGHT_NO", U."ORI_ENG", U."DES_ENG",
U."FLIGHT_TYPE", U."DISTANCE",
47
U."SEATS", U."AC_FAMILY", U."TAIL_NO", U."ACTUAL_DPT_TIME",
U."ACTUAL_ARR_TIME", U."AT_BRIDGE",
48
U."BRIDGE_TYPE", U."BRIDGE_TIME", U."BLOCK_ON_TIME", U."BLOCK_OFF_TIME",
U."FLIGHT_SEAT_DISTANCE",
49
U."FLIGHT_PASSENGER_DISTANCE", U."FLIGHT_PASSENGER_AMT", U."AGENT",
U."FLIGHT_LINE_TYPE",
50
U."FLT_STATUS", U."LEG_ID", U."SEAT_QTY_F", U."SEAT_QTY_C", U."SEAT_QTY_Y",
U."PLAN_DEPART_TIME",
51
U."PLAN_ARRIVAL_TIME", U."LINE_SERIAL", U."ORIG_AIRPORT_CD",
U."DEST_AIRPORT_CD", U."CARRIER_O",
52
U."ADULT_QTY", U."CHILD_QTY", U."INFANT_QTY", U."FLT_DT_UTC", U."SRV_TYPE",
U."LINE_SEAT_QTY_F",
53
U."LINE_SEAT_QTY_C", U."LINE_SEAT_QTY_Y", U."LINE_ADULT_QTY",
U."LINE_CHILD_QTY", U."LINE_INFANT_QTY",
54
U."EST_ARRIVAL_TIME", U."EST_DEPART_TIME", U."FLTID", U."SHEET_ADULTS",
U."SHEET_CHILDREN",
55
U."SHEET_INFANTS", U."TIMESTAMPNUM", U."VERSION_DATE", U."INVOICE_NO",
U."RECEIPT_NO", U."RECEIPT_ID",
56
U."REFUELED_ID", U."TYPE_ID", U."TIMESTAMP", U."CW_ACTYPE",
U."FLIGHT_TYPE_CODE", U."SHARE_MONEY",
57
U.qty, U.measure_unit,58
CASE 59

精简之后的视图（希望让 hash join 数据可以在内存中放下，不要去⾛磁盘 io ）：
WHEN AP.area_code = 'DOME' AND U.TYPE_ID != '1' THEN ROUND(U.amount * (1
+ R.EXCHANGE_RATE), 2)
60
ELSE U.amount 61
END,62
U.currency,63
CASE 64
WHEN AP.area_code = 'DOME' THEN ROUND(U.fuel_amount_rmb * (1 +
R.EXCHANGE_RATE), 2)
65
ELSE U.fuel_amount_rmb 66
END,67
U.fuel_amount_rate, U.acc_val, U.fuel_amount_rmb, R.EXCHANGE_RATE,68
P.IF_MATCH, P.GL_DATE, P.BATCH_NUM69
FROM base_union U70
LEFT JOIN t_fuel_rate_conversion R ON U.match_date BETWEEN R.apply_date AND
R.expiry_date
71
LEFT JOIN t_airport AP ON AP.airport_code3 = U.match_airport72
LEFT JOIN dc_flight_plan P ON P.id = U.id;73
CREATE OR REPLACE FORCE VIEW "FOFAS"."V_FULE_INVOICE_RECEIPT_COSTS" (1
"ID",2
"FLIGHT_DATE", "CARRIER", "FLIGHT_NO", "ORI_ENG", "DES_ENG", "FLIGHT_TYPE",
"TAIL_NO", "PLAN_DEPART_TIME",
3
"PLAN_ARRIVAL_TIME", "INVOICE_NO", "RECEIPT_NO", "RECEIPT_ID", 4
"REFUELED_ID", "TYPE_ID", "TIMESTAMP", "CW_ACTYPE", "FLIGHT_TYPE_CODE",
"SHARE_MONEY",
5
"QTY", "MEASURE_UNIT", "AMOUNT", "CURRENCY", "FUEL_AMOUNT_RMB",
"FUEL_AMOUNT_RATE",
6
"ACCRUEDAMOUNT", "ACCRUEDAMOUNTRMB", "EXCHANGE_RATE", "IF_MATCH", "GL_DATE",
"BATCH_NUM"
7
) AS8
WITH base_union AS (9
SELECT 10
c.ID, c.FLIGHT_DATE, c.CARRIER, c.FLIGHT_NO, c.ORI_ENG, c.DES_ENG,
c.FLIGHT_TYPE, c.TAIL_NO, c.PLAN_DEPART_TIME, c.PLAN_ARRIVAL_TIME, c.INVOICE_NO,
c.RECEIPT_NO, c.RECEIPT_ID, c.REFUELED_ID, c.TYPE_ID, c.TIMESTAMP, c.CW_ACTYPE,
c.FLIGHT_TYPE_CODE, c.SHARE_MONEY,
11
d.qty, d.measure_unit, d.amount, d.currency,12
d.fuel_amount_rmb, d.fuel_amount_rate, d.fuel_amount as acc_val,13
d.refueling_date as match_date, d.refueling_airport as match_airport14
FROM t_fule_invoice_receipt_costs c15
JOIN t_fuel_invoice_receipt_detail d ON c.receipt_id = d.proxyid AND
c.timestamp = d.timestamp and c.TIMESTAMP > '1704038400'
16

WHERE c.type_id = '1'17
UNION ALL18
SELECT 19
c.ID, c.FLIGHT_DATE, c.CARRIER, c.FLIGHT_NO, c.ORI_ENG, c.DES_ENG,
c.FLIGHT_TYPE, c.TAIL_NO, c.PLAN_DEPART_TIME, c.PLAN_ARRIVAL_TIME, c.INVOICE_NO,
c.RECEIPT_NO, c.RECEIPT_ID, c.REFUELED_ID, c.TYPE_ID, c.TIMESTAMP, c.CW_ACTYPE,
c.FLIGHT_TYPE_CODE, c.SHARE_MONEY,
20
d.REFUELED, d.MEASURE_UNITS, d.amount, d.currencys,21
d.fuel_amount_rmb, d.fuel_amount_rate, d.amount,22
c.flight_date, c.ori_eng23
FROM t_fule_invoice_receipt_costs c24
JOIN t_flight_fuelinfo_detail d ON c.refueled_id = d.id AND c.timestamp =
d.timestamp and c.TIMESTAMP > '1704038400'
25
WHERE c.type_id = '2'26
UNION ALL27
SELECT 28
c.ID, c.FLIGHT_DATE, c.CARRIER, c.FLIGHT_NO, c.ORI_ENG, c.DES_ENG,
c.FLIGHT_TYPE, c.TAIL_NO, c.PLAN_DEPART_TIME, c.PLAN_ARRIVAL_TIME, c.INVOICE_NO,
c.RECEIPT_NO, c.RECEIPT_ID, c.REFUELED_ID, c.TYPE_ID, c.TIMESTAMP, c.CW_ACTYPE,
c.FLIGHT_TYPE_CODE, c.SHARE_MONEY,
29
d.QTY_KG, d.MEASURE_UNITS, d.amount, d.currencys,30
d.fuel_amount_rmb, d.fuel_amount_rate, d.amount,31
c.flight_date, c.ori_eng32
FROM t_fule_invoice_receipt_costs c33
JOIN t_type_line_detail d ON c.refueled_id = d.id AND c.timestamp =
d.timestamp and c.TIMESTAMP > '1704038400'
34
WHERE c.type_id IN ('3', '4')35
)36
SELECT 37
U."ID", 38
U."FLIGHT_DATE", U."CARRIER", U."FLIGHT_NO", U."ORI_ENG", U."DES_ENG",
U."FLIGHT_TYPE", U."TAIL_NO", U."PLAN_DEPART_TIME",
39
U."PLAN_ARRIVAL_TIME",U."INVOICE_NO", U."RECEIPT_NO", U."RECEIPT_ID", 40
U."REFUELED_ID", U."TYPE_ID", U."TIMESTAMP", U."CW_ACTYPE",
U."FLIGHT_TYPE_CODE", U."SHARE_MONEY",
41
U.qty, U.measure_unit,42
CASE 43
WHEN AP.area_code = 'DOME' AND U.TYPE_ID != '1' THEN ROUND(U.amount * (1
+ R.EXCHANGE_RATE), 2)
44
ELSE U.amount 45
END,46
U.currency,47
CASE 48
WHEN AP.area_code = 'DOME' THEN ROUND(U.fuel_amount_rmb * (1 +
R.EXCHANGE_RATE), 2)
49

索引：
原始视图：
ELSE U.fuel_amount_rmb 50
END,51
U.fuel_amount_rate, U.acc_val, U.fuel_amount_rmb, R.EXCHANGE_RATE,52
P.IF_MATCH, P.GL_DATE, P.BATCH_NUM53
FROM base_union U54
LEFT JOIN t_fuel_rate_conversion R ON U.match_date BETWEEN R.apply_date AND
R.expiry_date
55
LEFT JOIN t_airport AP ON AP.airport_code3 = U.match_airport56
LEFT JOIN dc_flight_plan P ON P.id = U.id;57
CREATE INDEX IDX_COSTS_FLIGHTINFO ON T_FULE_INVOICE_RECEIPT_COSTS (FLIGHT_DATE,
FLIGHT_NO, ORI_ENG, DES_ENG, TAIL_NO);
1
CREATE INDEX idx_costs_comp ON t_fule_invoice_receipt_costs (type_id, timestamp,
receipt_id);
2
CREATE INDEX idx_costs_comp1 ON t_fule_invoice_receipt_costs (type_id,
timestamp, refueled_id);
3
CREATE INDEX idx_detail_pt ON T_FUEL_INVOICE_RECEIPT_DETAIL (PROXYID, TIMESTAMP);4
CREATE INDEX idx_rate_date ON t_fuel_rate_conversion (apply_date, expiry_date);5
create or replace force view "V_FULE_INVOICE_RECEIPT_COSTS"1
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
2

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
3
from (select c.*,4
d.qty qty,d.measure_unit,5
d.amount, -- 含税⾦额原币6
d.currency,7
case8
when a.area_code = 'DOME' then9
round(d.fuel_amount_rmb * (1 + r.exchange_rate), 2)10
else11
d.fuel_amount_rmb12
end fuel_amount_rmb, -- 含税⾦额⼈⺠币13
d.fuel_amount_rate, -- 币种转换汇率14
d.fuel_amount accruedamount, -- 不含税⾦额原币15
d.fuel_amount_rmb accruedamountrmb, -- 不含税⾦额原币16
R.EXCHANGE_RATE17
from t_fule_invoice_receipt_costs  c,18
t_fuel_invoice_receipt_detail d,19
t_airport                     a,20
t_fuel_rate_conversion        r21
where c.receipt_id = d.proxyid22
and c.type_id = 123
and c.timestamp = d.timestamp24
and a.airport_code3 = d.refueling_airport25
and d.refueling_date between r.apply_date and r.expiry_date26
union all27
select c.*,28
d.REFUELED qty,d.MEASURE_UNITS measure_unit,29
case30
when a.area_code = 'DOME' then31
round(d.amount * (1 + r.exchange_rate), 2)32

else33
d.amount34
end amount,35
d.currencys,36
case37
when a.area_code = 'DOME' then38
round(d.fuel_amount_rmb * (1 + r.exchange_rate), 2)39
else40
d.fuel_amount_rmb41
end fuel_amount_rmb,42
d.fuel_amount_rate,43
d.amount accruedamount, -- 不含税⾦额44
d.fuel_amount_rmb accruedamountrmb, -- 不含税⾦额原币45
R.EXCHANGE_RATE46
from t_fule_invoice_receipt_costs c,47
t_flight_fuelinfo_detail     d,48
t_airport                    a,49
t_fuel_rate_conversion       r50
where c.refueled_id = d.id51
and c.type_id = 252
and a.airport_code3 = c.ori_eng53
--and  d.FUEL_AMOUNT_RMB > 054
and c.timestamp = d.timestamp55
and c.flight_date between r.apply_date and r.expiry_date56
union all57
select c.*,58
d.QTY_KG qty,d.MEASURE_UNITS measure_unit,59
case60
when a.area_code = 'DOME' then61
round(d.amount * (1 + r.exchange_rate), 2)62
else63
d.amount64
end amount,65
d.currencys,66
case67
when a.area_code = 'DOME' then68
round(d.fuel_amount_rmb * (1 + r.exchange_rate), 2)69
else70
d.fuel_amount_rmb71
end fuel_amount_rmb,72
d.fuel_amount_rate,73
d.amount accruedamount, -- 不含税⾦额74

d.fuel_amount_rmb accruedamountrmb, -- 不含税⾦额原币75
R.EXCHANGE_RATE76
from t_fule_invoice_receipt_costs c,77
t_type_line_detail           d,78
t_airport                    a,79
t_fuel_rate_conversion       r80
where c.refueled_id = d.id81
and c.type_id in (3, 4)82
and a.airport_code3 = c.ori_eng83
--AND d.FUEL_AMOUNT_RMB > 084
and c.timestamp = d.timestamp85
and c.flight_date between r.apply_date and r.expiry_date) a,86
/*       (select max(timestamp) tamestamp,87
to_char(flight_date, 'yyyymm') flight_mouth88
from t_fule_invoice_receipt_costs89
group by to_char(flight_date, 'yyyymm')) b,*/90
dc_flight_plan p91
where /*a.timestamp = b.tamestamp92
and to_char(a.flight_date, 'YYYYMM') = b.flight_mouth93
and*/ p.id = a.id94
95



---
## 相关笔记
- [[近期的SQL脚本]]
- [[航油TODO]]
- [[FOFAS系统迁移]]
- [[预提期间归属问题修复的存储过程]]
- [[智慧航油拆分]]