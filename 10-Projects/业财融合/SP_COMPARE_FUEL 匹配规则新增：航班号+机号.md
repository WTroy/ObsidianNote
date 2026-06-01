---
title: SP_COMPARE_FUEL 匹配规则新增：航班号+机号
source: 有道云笔记
imported: true
---

更新后的存储过程：
CREATE OR REPLACE PROCEDURE FOFAS.SP_COMPARE_FUEL (i_PROXYID VARCHAR2, --
i_PROXYID  ⼤发票的  PROXYID
1
i_userid  VARCHAR2) IS2
3
-- 账单变量4
p_amount_INVOICE   NUMBER(14,3);5
p_dept_airport     varchar2(10);6
p_AREA_CODE        varchar2(20);7
p_INVOICE_DATE     date;8
p_SUPPLIER_ID      varchar2(50);9
p_PRICE            NUMBER(16,8);10
p_UNIT_PRICE       NUMBER(16,8);11
p_MEASURE_UNIT     varchar2(10);12
p_QTY_INVOICE      NUMBER(12,3);13
p_CURRENCY_INVOICE varchar2(20);14
p_INVOICE_NO       varchar2(50);15
p_LINE_TYPE     varchar2(50);16
P_COUNTRYTAXFLAG       varchar2(20);17
18
-- 加油单变量19
p_MEASURE_UNIT_recept varchar2(20);20
p_FLIGHT_TYPE_recept  varchar2(20);21
p_recept_date         date;22
p_QTY                 number(14, 2);23
p_QTY_KG              number(14, 2);24
25
-- 附加费计算和（新增变量）26
p_sur_flt_rownum       number(3);27
p_sur_weight_rownum    number(3);28
p_sur_dh_flt_rownum    number(3);29
p_sur_dh_weight_rownum number(3);30
31
-- 附加费变量32
p_SURCHARGE    number(14, 2);33
p_SURCHARGE_DH number(14, 2);34
p_SURCHARGE_DH_Country number(14, 2);35
36
-- 内部附加费37
--p_MEASURE_UNIT_DH varchar2(20);38

--p_CURRENCY_DH     varchar2(20);39
--p_PRICE_DH        number(14, 6);40
41
-- 加油单单位转换42
p_QTY_recept_sum    number(14, 2); -- 经过单位转换后的加油数量43
p_QTY_minus_recept_sum    number(14, 2); -- 经过单位转换后的抽油数量 ( 负数 )44
p_QTY_recept_amount number(14, 3); -- 计算出来内部的总⾦额45
p_QTY_recept        number(14, 2);46
p_flight_num        number(3);47
--p_PRICE_jx          number(16, 8);48
49
p_remarks varchar2(300);50
51
p_CURRENCY_price     varchar2(20);52
P_MEASURE_UNIT_price varchar2(20);53
p_row_count          number(10); -- ⽤于判断是否查询出记录54
55
p_count            number(10);56
p_recept_price_sum number(16, 8);57
v_temp_amount NUMBER(14, 2) := 0;-- 存放附加费计算临时值58
59
60
-- 按取出对应的加油单油量，按航班类型、⽇期、单位汇总61
cursor c_fuel is62
select a.FLIGHT_TYPE,63
a.REFUELING_DATE,64
a.MEASURE_UNIT,65
sum(a.QTY_KG),66
sum(a.QTY)67
from T_FUEL_REFUELING_RECEIPT a68
where a.QTY > 069
-- 王浩 _2026-03-02 ：国际同⼀天，可能存在相同的加油单号：增加航班号和机号的匹配70
and (a.RECEIPT_NO, a.refueling_date, a.flight_no, a.tail_no) in71
(select b.RECEIPT_NO, b.refueling_date, b.flight_no, b.tail_no72
from T_FUEL_INVOICE_RECEIPT b73
where b.INVOICE_NO = i_proxyid74
and b.merge_id is null-- 增加查询条件，查询出未和并的加油单信息75
and b.refueling_date = a.refueling_date)76
group by FLIGHT_TYPE, REFUELING_DATE, MEASURE_UNIT77
78
union all79
-- 增加从  合并备份表中 t_fuel_invoice_receipt_merge 查询出合并前的加油单信息80

select a.FLIGHT_TYPE,81
a.REFUELING_DATE,82
a.MEASURE_UNIT,83
sum(a.QTY_KG),84
sum(a.QTY)85
from T_FUEL_REFUELING_RECEIPT a86
where a.QTY > 087
and (a.RECEIPT_NO, a.refueling_date, a.flight_no, a.tail_no) in88
(select mm.receipt_no,mm.refueling_date, mm.flight_no, mm.tail_no from
t_fuel_invoice_receipt_merge mm
89
where mm.id in (90
select r.merge_id from t_fuel_invoice_receipt r91
where r.invoice_no = i_proxyid92
and r.merge_id is not null-- 增加查询条件，查询出和并的加油单信息93
)94
and mm.refueling_date = a.refueling_date)95
group by FLIGHT_TYPE, REFUELING_DATE, MEASURE_UNIT96
97
union all98
99
select a.FLIGHT_TYPE,100
a.REFUELING_DATE,101
a.MEASURE_UNIT,102
sum(a.QTY_KG),103
sum(a.QTY)104
from T_FUEL_REFUELING_RECEIPT a105
where a.QTY < 0106
and (a.RECEIPT_NO, a.refueling_date, a.flight_no, a.tail_no) in107
(select b.RECEIPT_NO, b.refueling_date, b.flight_no, b.tail_no108
from T_FUEL_INVOICE_RECEIPT b109
where b.INVOICE_NO = i_proxyid110
and b.merge_id is null-- 增加查询条件，查询出未和并的加油单信息111
and b.refueling_date = a.refueling_date)112
group by FLIGHT_TYPE, REFUELING_DATE, MEASURE_UNIT113
114
union all115
-- 增加从  合并备份表中 t_fuel_invoice_receipt_merge 查询出合并前的加油单信息116
select a.FLIGHT_TYPE,117
a.REFUELING_DATE,118
a.MEASURE_UNIT,119
sum(a.QTY_KG),120
sum(a.QTY)121

from T_FUEL_REFUELING_RECEIPT a122
where a.QTY < 0123
and (a.RECEIPT_NO, a.refueling_date, a.flight_no, a.tail_no) in124
(select mm.receipt_no,mm.refueling_date, mm.flight_no, mm.tail_no from
t_fuel_invoice_receipt_merge mm
125
where mm.id in (126
select r.merge_id from t_fuel_invoice_receipt r127
where r.invoice_no = i_proxyid128
and r.merge_id is not null-- 增加查询条件，查询出和并的加油单信息129
)130
and mm.refueling_date = a.refueling_date)131
group by FLIGHT_TYPE, REFUELING_DATE, MEASURE_UNIT;132
133
BEGIN134
135
SELECT AMOUNT,136
STATION_CODE,137
AREA_CODE,138
INVOICE_DATE,139
SUPPLIER_ID,140
UNIT_PRICE,141
MEASURE_UNIT,142
QTY,143
CURRENCY,144
INVOICE_NO,145
COUNTRYTAXFLAG146
INTO P_AMOUNT_INVOICE,147
P_DEPT_AIRPORT,148
P_AREA_CODE,149
P_INVOICE_DATE,150
P_SUPPLIER_ID,151
P_UNIT_PRICE,152
P_MEASURE_UNIT,153
P_QTY_INVOICE,154
P_CURRENCY_INVOICE,155
P_INVOICE_NO,156
P_COUNTRYTAXFLAG157
FROM T_FUEL_INVOICE A, T_AIRPORT B158
WHERE A.PROXYID = I_PROXYID159
AND A.STATION_CODE = B.AIRPORT_CODE3;160
161

/********************************************************************************
*
162
1 、取出对应的加油单的加油量，并把单位转换账单数量单位163
2 、根据供油公司、加油航站、账单⽇期，取出单价，并做单位转换164
3 、  计算内部加油总⾦额165
4 、抽油  油量、抽油架次166

*********************************************************************************
**/
167
p_QTY_recept_sum    := 0;168
p_QTY_minus_recept_sum :=0;169
p_QTY_recept_amount := 0;170
p_recept_price_sum  := 0;171
p_count             := 0;172
p_remarks := '';173
174
/************************************************************************175
判断是不是浦东油料公司的账单，要是浦东油料公司的账单，176
审核的时候不按油单的航班性质取油价，177
账单是外线  就取国际航线油价，内线就取国内航线油价178
*************************************************************************/179
180
p_row_count := 0;181
182
select count(*)183
into p_row_count184
from T_FUEL_INVOICE a, t_fuel_supplier b185
where a.PROXYID = i_PROXYID186
and  a.supplier_id = b.proxyid187
and  b.supplier_no = '010'188
and  a.station_code = 'PVG';189
190
191
if (p_row_count > 0) then192
select LINE_TYPE193
into   p_LINE_TYPE194
from T_FUEL_INVOICE a, t_fuel_supplier b195
where a.PROXYID = i_PROXYID196
and  a.supplier_id = b.proxyid197
and  b.supplier_no = '010'198
and  a.station_code = 'PVG';199
end if;200

201
-- 附加费202
p_SURCHARGE_DH := 0;203
-- 国内税附加费204
p_SURCHARGE_DH_Country := 0;205
p_sur_flt_rownum      :=0;206
p_sur_weight_rownum   :=0;207
p_sur_dh_flt_rownum   :=0;208
p_sur_dh_weight_rownum :=0;209
/***************** 内部  加油  架次
*****************************************************/
210
p_flight_num := 0;211
212
-- 开始循环迭代按航班类型、⽇期、单位汇总的油量数据213
open c_fuel;214
fetch c_fuel215
into p_FLIGHT_TYPE_recept, p_recept_date, p_MEASURE_UNIT_recept, p_QTY_KG,
p_QTY;
216
while (c_fuel%found) loop217
218
p_PRICE     := 0;219
p_row_count := 0;220
221
-- 如果是浦东油料公司，航班性质取账单  内线（ DOME ）、外线（ INTL ）222
if p_LINE_TYPE is not null then223
p_FLIGHT_TYPE_recept := p_LINE_TYPE;224
end if;225
226
227
228
/* 如果是国际、地区航班取出对应的国际单价 , 单位与账单统⼀ */229
if instr('AREA INTL', p_AREA_CODE, 1, 1) > 0 then230
231
-- 如果油单数量单位和账单数量单位都为 LT 或 GA ，则油单数量取 qty232
if instr('LT GA', p_MEASURE_UNIT_recept, 1, 1) > 0 and233
instr('LT GA', p_MEASURE_UNIT, 1, 1) > 0 then234
-- 数量235
p_QTY_recept := p_QTY * EXCHANGE_UNIT(p_MEASURE_UNIT_recept,236
p_MEASURE_UNIT,237
p_recept_date,238
'MEASURE');239
-- 如果油单数量单位为 LT 或 GA ，账单数量单位都为 KG 或 TG ，则油单数量取 qty_KG240
elsif instr('LT GA', p_MEASURE_UNIT_recept, 1, 1) > 0 and241

instr('KG TG', p_MEASURE_UNIT, 1, 1) > 0 then242
p_QTY_recept := p_QTY_KG * EXCHANGE_UNIT('KG',243
p_MEASURE_UNIT,244
p_recept_date,245
'MEASURE');246
247
-- 其他情况取 qty248
else249
p_QTY_recept := p_QTY * EXCHANGE_UNIT(p_MEASURE_UNIT_recept,250
p_MEASURE_UNIT,251
p_recept_date,252
'MEASURE');253
end if;254
255
p_QTY_recept_sum := p_QTY_recept_sum + p_QTY_recept; -- 单位转换后的数量256
257
if p_QTY < 0  then258
p_QTY_minus_recept_sum := p_QTY_minus_recept_sum + p_QTY_recept;  -- 单位
转换后的抽油量（负数）
259
end if;260
261
-- 查询是否存在单价262
select count(*)263
into p_row_count264
from T_FUEL_INT_UNIT_PRICE265
where SUPPLIER_ID = p_SUPPLIER_ID -- 供油公司266
and REFUELING_AIRPORT = p_dept_airport -- 加油航站267
and p_recept_date >= APPLY_DATE -- 账单⽇期268
and p_recept_date <= EXPIRY_DATE;269
270
-- 如果存在单价，则转换单价271
if (p_row_count > 0) then272
select PRICE, CURRENCY, MEASURE_UNIT273
into p_PRICE, p_CURRENCY_price, P_MEASURE_UNIT_price274
from T_FUEL_INT_UNIT_PRICE275
where SUPPLIER_ID = p_SUPPLIER_ID276
and REFUELING_AIRPORT = p_dept_airport277
and p_recept_date >= APPLY_DATE278
and p_recept_date <= EXPIRY_DATE;279
280
p_PRICE := (p_PRICE * EXCHANGE_UNIT(p_CURRENCY_price,281
p_CURRENCY_INVOICE,282

p_recept_date,283
'CURRENCY')) /284
EXCHANGE_UNIT(P_MEASURE_UNIT_price,285
p_MEASURE_UNIT,286
p_recept_date,287
'MEASURE');288
end if;289
290
end if;291
292
293
/* 如果是国内航班取出对应的国内单价 , 单位与账单统⼀ */294
if instr('DOME', p_AREA_CODE, 1, 1) > 0 then295
-- 油量 KG 数296
p_QTY_recept     := p_QTY_KG * EXCHANGE_UNIT('KG',297
p_MEASURE_UNIT,298
p_recept_date,299
'MEASURE');300
p_QTY_recept_sum := p_QTY_recept_sum + p_QTY_recept; -- 单位转换后的数量301
302
if p_QTY < 0  then303
p_QTY_minus_recept_sum := p_QTY_minus_recept_sum + p_QTY_recept;  -- 单位
转换后的抽油量（负数）
304
end if;305
306
-- 查询是否存在单价307
p_row_count := 0;308
309
select count(*)310
into p_row_count311
from T_FUEL_DOM_UNIT_PRICE a312
where a.supplier_id = p_SUPPLIER_ID -- 供油公司313
and FLIGHT_TYPE =
decode(p_FLIGHT_TYPE_recept,'AREA','INTL',p_FLIGHT_TYPE_recept) -- 航班类型
314
and a.apply_date <= p_recept_date -- 账单⽇期315
and a.expiry_date >= p_recept_date316
and p_dept_airport IN -- 加油航站317
(select AIRPORT318
from T_FUEL_DOM_PRICE_AIRPORT319
where DOM_UNIT_PRICE_ID = a.PROXYID320
and APPLY_DATE <= p_recept_date321
and EXPIRY_DATE >= p_recept_date);322
323

-- 如果存在单价，则转换单价324
if (p_row_count > 0) then325
326
-- 国内同⼀个加油公司同⼀个时间段同⼀个单价对于的机场327
select a.PRICE, a.CURRENCY, a.MEASURE_UNIT328
into p_PRICE, p_CURRENCY_price, P_MEASURE_UNIT_price329
from T_FUEL_DOM_UNIT_PRICE a330
where a.supplier_id = p_SUPPLIER_ID331
and FLIGHT_TYPE =
decode(p_FLIGHT_TYPE_recept,'AREA','INTL',p_FLIGHT_TYPE_recept)
332
and a.apply_date <= p_recept_date333
and a.expiry_date >= p_recept_date334
and p_dept_airport IN335
(select AIRPORT336
from T_FUEL_DOM_PRICE_AIRPORT337
where DOM_UNIT_PRICE_ID = a.PROXYID338
and APPLY_DATE <= p_recept_date339
and EXPIRY_DATE >= p_recept_date)340
and rownum = 1;341
342
p_PRICE := (p_PRICE * EXCHANGE_UNIT(p_CURRENCY_price,343
p_CURRENCY_INVOICE,344
p_recept_date,345
'CURRENCY')) /346
EXCHANGE_UNIT(P_MEASURE_UNIT_price,347
p_MEASURE_UNIT,348
p_recept_date,349
'MEASURE');350
end if;351
352
end if;353
354
-- 附加费计算开始355
if p_QTY_recept > 0 then356
--1 加油357
--1.1 、按班次收费的加油附加费358
select count(*)  into p_sur_flt_rownum359
FROM T_FUEL_SURCHARGE A360
WHERE A.SUPPLIER_ID = p_SUPPLIER_ID361
AND A.REFUELING_AIRPORT = p_dept_airport362
AND A.APPLY_DATE <= p_recept_date363
AND A.EXPIRY_DATE >= p_recept_date364

AND A.MEASURE_UNIT = 'FLIGHT'365
AND (A.SUR_KIND <> '1' OR A.SUR_KIND IS NULL);366
if p_sur_flt_rownum>0 then          -- 如果有按班次收的附加费367
-- 查询航班次数368
SELECT COUNT(*)369
INTO p_flight_num370
FROM T_FUEL_REFUELING_RECEIPT371
WHERE QTY > 0 -- 加油372
AND  REFUELING_DATE=p_recept_date373
AND (RECEIPT_NO, REFUELING_DATE) IN374
(SELECT RECEIPT_NO, REFUELING_DATE375
FROM T_FUEL_INVOICE_RECEIPT376
WHERE INVOICE_NO = I_PROXYID377
AND REFUELING_DATE=p_recept_date);378
p_SURCHARGE_DH := p_SURCHARGE_DH + p_flight_num379
*pkg_fuel_surcharge.CALC_ADD_PRICE(p_recept_date,380
p_SUPPLIER_ID,381
p_dept_airport,382
'',383
'FLIGHT',384

p_CURRENCY_INVOICE);
385
end if;386
--1.2 、按重量或体积收费的加油附加费387
select count(*)  into p_sur_weight_rownum388
FROM T_FUEL_SURCHARGE A389
WHERE A.SUPPLIER_ID = p_SUPPLIER_ID390
AND A.REFUELING_AIRPORT = p_dept_airport391
AND A.APPLY_DATE <= p_recept_date392
AND A.EXPIRY_DATE >= p_recept_date393
AND A.MEASURE_UNIT <> 'FLIGHT'394
AND (A.SUR_KIND <> '1' OR A.SUR_KIND IS NULL);395
if p_sur_weight_rownum>0 then          -- 如果有按重量或体积收的附加费396
/***************** 内部  加油  附加费标准  附加费⾦额
*****************************************************/
397
-- 计算  东航认为的附加费     数量单位转换398
p_SURCHARGE_DH := p_SURCHARGE_DH + p_QTY_recept399

*pkg_fuel_surcharge.CALC_ADD_PRICE(p_recept_date,
400

p_SUPPLIER_ID,
401

p_dept_airport,
402

p_MEASURE_UNIT,
403

'WEIGHT',
404

p_CURRENCY_INVOICE);
405
end if;406
end if;407
408
-- 发票有国内税409
if P_COUNTRYTAXFLAG is NULL or P_COUNTRYTAXFLAG <> 'Y' then410
-- 国内税附加费计算开始411
if p_QTY_recept > 0 then412
--1 加油413
--1.1 、按班次收费的加油附加费414
select count(*)  into p_sur_flt_rownum415
FROM T_FUEL_SURCHARGE A416
WHERE A.SUPPLIER_ID = p_SUPPLIER_ID417
AND A.REFUELING_AIRPORT = p_dept_airport418
AND A.APPLY_DATE <= p_recept_date419
AND A.EXPIRY_DATE >= p_recept_date420
AND A.MEASURE_UNIT = 'FLIGHT'421
AND (A.SUR_KIND <> '1' OR A.SUR_KIND IS NULL);422
if p_sur_flt_rownum>0 then          -- 如果有按班次收的附加费423
-- 查询航班次数424
SELECT COUNT(*)425
INTO p_flight_num426
FROM T_FUEL_REFUELING_RECEIPT427
WHERE QTY > 0 -- 加油428
AND  REFUELING_DATE=p_recept_date429
AND (RECEIPT_NO, REFUELING_DATE) IN430
(SELECT RECEIPT_NO, REFUELING_DATE431
FROM T_FUEL_INVOICE_RECEIPT432
WHERE INVOICE_NO = I_PROXYID433
AND REFUELING_DATE=p_recept_date);434
435
-- 国内税436
p_SURCHARGE_DH_Country := p_SURCHARGE_DH_Country + p_flight_num437

*pkg_fuel_surcharge.CALC_ADD_PRICE_TWO(p_recept_date,
438
p_SUPPLIER_ID,439
p_dept_airport,440
'',441

'FLIGHT',442

p_CURRENCY_INVOICE);
443
444
end if;445
--1.2 、按重量或体积收费的加油附加费446
select count(*)  into p_sur_weight_rownum447
FROM T_FUEL_SURCHARGE A448
WHERE A.SUPPLIER_ID = p_SUPPLIER_ID449
AND A.REFUELING_AIRPORT = p_dept_airport450
AND A.APPLY_DATE <= p_recept_date451
AND A.EXPIRY_DATE >= p_recept_date452
AND A.MEASURE_UNIT <> 'FLIGHT'453
AND (A.SUR_KIND <> '1' OR A.SUR_KIND IS NULL);454
if p_sur_weight_rownum>0 then          -- 如果有按重量或体积收的附加费455
/***************** 内部  加油  附加费标准  附加费⾦额
*****************************************************/
456
-- 计算  东航认为的附加费     数量单位转换457
458
-- 国内税459
p_SURCHARGE_DH_Country := p_SURCHARGE_DH_Country + p_QTY_recept460

*pkg_fuel_surcharge.CALC_ADD_PRICE_TWO(p_recept_date,
461

p_SUPPLIER_ID,
462

p_dept_airport,
463

p_MEASURE_UNIT,
464

'WEIGHT',
465

p_CURRENCY_INVOICE);
466
end if;467
end if;468
end if;469
470
471
--2 抽油472
if p_QTY_recept < 0 then473
--2.1 、按班次收费的抽油附加费474
select count(*)  into p_sur_dh_flt_rownum475
FROM T_FUEL_SURCHARGE A476
WHERE A.SUPPLIER_ID = p_SUPPLIER_ID477

AND A.REFUELING_AIRPORT = p_dept_airport478
AND A.APPLY_DATE <= p_recept_date479
AND A.EXPIRY_DATE >= p_recept_date480
AND A.MEASURE_UNIT = 'FLIGHT'481
AND A.SUR_KIND = '1';482
if p_sur_dh_flt_rownum>0 then          -- 如果有按班次收的附加费，且油单数量为正483
-- 查询航班次数484
SELECT COUNT(*)485
INTO p_flight_num486
FROM T_FUEL_REFUELING_RECEIPT487
WHERE QTY < 0 -- 抽油488
AND  REFUELING_DATE=p_recept_date489
AND (RECEIPT_NO, REFUELING_DATE) IN490
(SELECT RECEIPT_NO, REFUELING_DATE491
FROM T_FUEL_INVOICE_RECEIPT492
WHERE INVOICE_NO = I_PROXYID493
AND REFUELING_DATE=p_recept_date);494
v_temp_amount := p_flight_num*pkg_fuel_surcharge.CALC_LESS_PRICE(495
p_recept_date,496
p_SUPPLIER_ID,497
p_dept_airport,498
'',499
'FLIGHT',500
p_CURRENCY_INVOICE);501
p_SURCHARGE_DH := p_SURCHARGE_DH + v_temp_amount;502
end if;503
--2.2 、按重量或体积收费的抽油附加费504
select count(*)  into p_sur_dh_weight_rownum505
FROM T_FUEL_SURCHARGE A506
WHERE A.SUPPLIER_ID = p_SUPPLIER_ID507
AND A.REFUELING_AIRPORT = p_dept_airport508
AND A.APPLY_DATE <= p_recept_date509
AND A.EXPIRY_DATE >= p_recept_date510
AND A.MEASURE_UNIT <> 'FLIGHT'511
AND A.SUR_KIND = '1';512
if p_sur_dh_weight_rownum>0 then          -- 如果有按重量或体积收的附加费513
/***************** 内部  抽油  附加费标准  附加费⾦额
*****************************************************/
514
-- 计算  东航认为的附加费     数量单位转换515
v_temp_amount :=
p_QTY_recept*pkg_fuel_surcharge.CALC_LESS_PRICE(p_recept_date,
516

p_SUPPLIER_ID,
517

p_dept_airport,
518

p_MEASURE_UNIT,
519
'WEIGHT',520

p_CURRENCY_INVOICE);
521
p_SURCHARGE_DH := p_SURCHARGE_DH + abs(v_temp_amount);522
end if;523
end if;524
525
-- 发票有国内税526
if P_COUNTRYTAXFLAG is NULL or P_COUNTRYTAXFLAG <> 'Y' then527
-- 国内税528
--2 抽油529
if p_QTY_recept < 0 then530
--2.1 、按班次收费的抽油附加费531
select count(*)  into p_sur_dh_flt_rownum532
FROM T_FUEL_SURCHARGE A533
WHERE A.SUPPLIER_ID = p_SUPPLIER_ID534
AND A.REFUELING_AIRPORT = p_dept_airport535
AND A.APPLY_DATE <= p_recept_date536
AND A.EXPIRY_DATE >= p_recept_date537
AND A.MEASURE_UNIT = 'FLIGHT'538
AND A.SUR_KIND = '1';539
if p_sur_dh_flt_rownum>0 then          -- 如果有按班次收的附加费，且油单数量为
正
540
-- 查询航班次数541
SELECT COUNT(*)542
INTO p_flight_num543
FROM T_FUEL_REFUELING_RECEIPT544
WHERE QTY < 0 -- 抽油545
AND  REFUELING_DATE=p_recept_date546
AND (RECEIPT_NO, REFUELING_DATE) IN547
(SELECT RECEIPT_NO, REFUELING_DATE548
FROM T_FUEL_INVOICE_RECEIPT549
WHERE INVOICE_NO = I_PROXYID550
AND REFUELING_DATE=p_recept_date);551
v_temp_amount := p_flight_num*pkg_fuel_surcharge.CALC_LESS_PRICE_TWO(552
p_recept_date,553
p_SUPPLIER_ID,554
p_dept_airport,555
'',556

'FLIGHT',557

p_CURRENCY_INVOICE);
558
p_SURCHARGE_DH_Country := p_SURCHARGE_DH_Country + v_temp_amount;559
end if;560
--2.2 、按重量或体积收费的抽油附加费561
select count(*)  into p_sur_dh_weight_rownum562
FROM T_FUEL_SURCHARGE A563
WHERE A.SUPPLIER_ID = p_SUPPLIER_ID564
AND A.REFUELING_AIRPORT = p_dept_airport565
AND A.APPLY_DATE <= p_recept_date566
AND A.EXPIRY_DATE >= p_recept_date567
AND A.MEASURE_UNIT <> 'FLIGHT'568
AND A.SUR_KIND = '1';569
if p_sur_dh_weight_rownum>0 then          -- 如果有按重量或体积收的附加费570
/***************** 内部  抽油  附加费标准  附加费⾦额
*****************************************************/
571
-- 计算  东航认为的附加费     数量单位转换572
v_temp_amount :=
p_QTY_recept*pkg_fuel_surcharge.CALC_LESS_PRICE_TWO(p_recept_date,
573

p_SUPPLIER_ID,
574

p_dept_airport,
575

p_MEASURE_UNIT,
576
'WEIGHT',577

p_CURRENCY_INVOICE);
578
p_SURCHARGE_DH_Country := p_SURCHARGE_DH_Country +
abs(v_temp_amount);
579
end if;580
end if;581
end if;582
583
p_QTY_recept_amount := p_QTY_recept_amount + (p_QTY_recept * p_PRICE); -- 总⾦
额计算
584
p_recept_price_sum  := p_recept_price_sum + p_PRICE;585
p_count             := p_count + 1;586
587
588
fetch c_fuel589
into p_FLIGHT_TYPE_recept, p_recept_date, p_MEASURE_UNIT_recept, p_QTY_KG,
p_QTY;
590
end loop;591

close c_fuel;592
593
594
595
596
597
/***************** 计算加油单单价平均值
*****************************************************/
598
if (p_count > 0) then599
p_PRICE := (p_recept_price_sum / p_count);600
end if;601
602
/***************** 账单附加费总⾦额
*****************************************************/
603
p_row_count := 0;604
select count(*)605
into p_row_count606
from T_FUEL_INVOICE_SURCHARGE607
where INVOICE_NO = i_PROXYID;608
609
if (p_row_count > 0) then610
select sum(AMOUNT * EXCHANGE_UNIT(CURRENCY,611
p_CURRENCY_INVOICE,612
p_INVOICE_DATE,613
'CURRENCY'))614
into p_SURCHARGE615
from T_FUEL_INVOICE_SURCHARGE616
where INVOICE_NO = i_PROXYID;617
end if;618
619
------------------- 审核结果备注 --------------------------620
if p_QTY_INVOICE > p_QTY_recept_sum then621
p_remarks := ' 加油数量差异 ';622
elsif p_SURCHARGE > p_SURCHARGE_DH then623
p_remarks := ' 附加费差异 ';624
elsif p_amount_INVOICE > p_QTY_recept_amount + p_SURCHARGE_DH then625
p_remarks := ' 总⾦额差异 ';626
end if;627
628
629
-- 插⼊国内审核存在差异的数据630
UPDATE T_FUEL_INVOICE A631
SET RECEIPT_QTY      = P_QTY_RECEPT_SUM,632

RECEIPT_PRICE    = P_PRICE,633
SURCHARGE_AMOUNT = P_SURCHARGE,634
RECEIPT_SUCHARGE = P_SURCHARGE_DH - p_SURCHARGE_DH_Country,635
RECEIPT_AMOUNT   = P_QTY_RECEPT_AMOUNT,636
MU_AMOUNT        = P_QTY_RECEPT_AMOUNT + P_SURCHARGE_DH -
p_SURCHARGE_DH_Country,   -- 减掉国内税
637
DIFF_AMOUNT      = P_AMOUNT_INVOICE - P_QTY_RECEPT_AMOUNT -
(P_SURCHARGE_DH - p_SURCHARGE_DH_Country),
638
DIFF_FLAG        = P_REMARKS,639
INVOICE_STATUS   = '01', -- 账单设置为 '01' （已经审核）640
AUDIT_USER       = I_USERID,641
AUDIT_TIME       = SYSDATE,642
MU_TAX_AMOUNT    = (P_QTY_RECEPT_AMOUNT + P_SURCHARGE_DH -
p_SURCHARGE_DH_Country) /(1+EXCHANGE_UNIT(NULL,NULL,a.invoice_date,'RATE'))*
(EXCHANGE_UNIT(NULL,NULL,a.invoice_date,'RATE')), -- 计算税⾦ : 内部总⾦额的 17% （税率这
⾥为固定 17% ，税率变化可在这修改  或增加税率维护表）
643
MU_NO_TAX_AMOUNT = (P_QTY_RECEPT_AMOUNT + P_SURCHARGE_DH -
p_SURCHARGE_DH_Country) /(1+EXCHANGE_UNIT(NULL,NULL,a.invoice_date,'RATE'))*1
644
WHERE PROXYID = I_PROXYID;645
646
647
UPDATE T_FUEL_INVOICE T648
SET DIFF_FLAG = DIFF_FLAG || ',' ||649
(SELECT REMARK650
FROM (SELECT A.INVOICE_NO,651
' ⽆法找到对应的油单： ' || WM_CONCAT(A.RECEIPT_NO)
||
652
'( 油单未录⼊或者未核对 ) 。 ' REMARK653
FROM T_FUEL_INVOICE_RECEIPT A654
LEFT JOIN T_FUEL_REFUELING_RECEIPT B ON
A.RECEIPT_NO =  B.RECEIPT_NO
655
AND
A.REFUELING_DATE =  B.REFUELING_DATE
656
AND
A.FLIGHT_NO = B.FLIGHT_NO
657
AND A.TAIL_NO =
B.TAIL_NO
658
WHERE B.RECEIPT_NO IS NULL659
AND INVOICE_NO = I_PROXYID660
GROUP BY A.INVOICE_NO))661
WHERE T.PROXYID IN (SELECT A.INVOICE_NO662
FROM T_FUEL_INVOICE_RECEIPT A663
LEFT JOIN T_FUEL_REFUELING_RECEIPT B ON A.RECEIPT_NO =
B.RECEIPT_NO
664
AND A.REFUELING_DATE =
B.REFUELING_DATE
665

原始存储过程备份：
AND A.FLIGHT_NO =
B.FLIGHT_NO
666
AND A.TAIL_NO =
B.TAIL_NO
667
WHERE B.RECEIPT_NO IS NULL668
AND INVOICE_NO = I_PROXYID669
GROUP BY A.INVOICE_NO);670
671
-- 插⼊监控数据672
INSERT INTO T_FUEL_INVOICE_HANDLE_RECORD673
(PROXYID, INVOICE_ID, OPERATOR, OPERATE_TIME, STEP)674
VALUES675
(SQ_APPRCAL.NEXTVAL, I_PROXYID, I_USERID, SYSDATE, '01');676
677
COMMIT;678
679
END Sp_Compare_Fuel;680
681
682
CREATE OR REPLACE PROCEDURE FOFAS.SP_COMPARE_FUEL (i_PROXYID VARCHAR2, --
i_PROXYID  ⼤发票的  PROXYID
1
i_userid  VARCHAR2) IS2
3
-- 账单变量4
p_amount_INVOICE   NUMBER(14,3);5
p_dept_airport     varchar2(10);6
p_AREA_CODE        varchar2(20);7
p_INVOICE_DATE     date;8
p_SUPPLIER_ID      varchar2(50);9
p_PRICE            NUMBER(16,8);10
p_UNIT_PRICE       NUMBER(16,8);11
p_MEASURE_UNIT     varchar2(10);12
p_QTY_INVOICE      NUMBER(12,3);13
p_CURRENCY_INVOICE varchar2(20);14
p_INVOICE_NO       varchar2(50);15
p_LINE_TYPE     varchar2(50);16
P_COUNTRYTAXFLAG       varchar2(20);17

18
-- 加油单变量19
p_MEASURE_UNIT_recept varchar2(20);20
p_FLIGHT_TYPE_recept  varchar2(20);21
p_recept_date         date;22
p_QTY                 number(14, 2);23
p_QTY_KG              number(14, 2);24
25
-- 附加费计算和（新增变量）26
p_sur_flt_rownum       number(3);27
p_sur_weight_rownum    number(3);28
p_sur_dh_flt_rownum    number(3);29
p_sur_dh_weight_rownum number(3);30
31
-- 附加费变量32
p_SURCHARGE    number(14, 2);33
p_SURCHARGE_DH number(14, 2);34
p_SURCHARGE_DH_Country number(14, 2);35
36
-- 内部附加费37
--p_MEASURE_UNIT_DH varchar2(20);38
--p_CURRENCY_DH     varchar2(20);39
--p_PRICE_DH        number(14, 6);40
41
-- 加油单单位转换42
p_QTY_recept_sum    number(14, 2); -- 经过单位转换后的加油数量43
p_QTY_minus_recept_sum    number(14, 2); -- 经过单位转换后的抽油数量 ( 负数 )44
p_QTY_recept_amount number(14, 3); -- 计算出来内部的总⾦额45
p_QTY_recept        number(14, 2);46
p_flight_num        number(3);47
--p_PRICE_jx          number(16, 8);48
49
p_remarks varchar2(300);50
51
p_CURRENCY_price     varchar2(20);52
P_MEASURE_UNIT_price varchar2(20);53
p_row_count          number(10); -- ⽤于判断是否查询出记录54
55
p_count            number(10);56
p_recept_price_sum number(16, 8);57
v_temp_amount NUMBER(14, 2) := 0;-- 存放附加费计算临时值58
59

60
-- 按取出对应的加油单油量，按航班类型、⽇期、单位汇总61
cursor c_fuel is62
select a.FLIGHT_TYPE,63
a.REFUELING_DATE,64
a.MEASURE_UNIT,65
sum(a.QTY_KG),66
sum(a.QTY)67
from T_FUEL_REFUELING_RECEIPT a68
where a.QTY > 069
and (a.RECEIPT_NO, a.refueling_date) in70
(select b.RECEIPT_NO, b.refueling_date71
from T_FUEL_INVOICE_RECEIPT b72
where b.INVOICE_NO = i_proxyid73
and b.merge_id is null-- 增加查询条件，查询出未和并的加油单信息74
and b.refueling_date = a.refueling_date)75
group by FLIGHT_TYPE, REFUELING_DATE, MEASURE_UNIT76
77
union all78
-- 增加从  合并备份表中 t_fuel_invoice_receipt_merge 查询出合并前的加油单信息79
select a.FLIGHT_TYPE,80
a.REFUELING_DATE,81
a.MEASURE_UNIT,82
sum(a.QTY_KG),83
sum(a.QTY)84
from T_FUEL_REFUELING_RECEIPT a85
where a.QTY > 086
and (a.RECEIPT_NO, a.refueling_date) in87
(select mm.receipt_no,mm.refueling_date from
t_fuel_invoice_receipt_merge mm
88
where mm.id in (89
select r.merge_id from t_fuel_invoice_receipt r90
where r.invoice_no = i_proxyid91
and r.merge_id is not null-- 增加查询条件，查询出和并的加油单信息92
)93
and mm.refueling_date = a.refueling_date)94
group by FLIGHT_TYPE, REFUELING_DATE, MEASURE_UNIT95
96
union all97
98
select a.FLIGHT_TYPE,99
a.REFUELING_DATE,100

a.MEASURE_UNIT,101
sum(a.QTY_KG),102
sum(a.QTY)103
from T_FUEL_REFUELING_RECEIPT a104
where a.QTY < 0105
and (a.RECEIPT_NO, a.refueling_date) in106
(select b.RECEIPT_NO, b.refueling_date107
from T_FUEL_INVOICE_RECEIPT b108
where b.INVOICE_NO = i_proxyid109
and b.merge_id is null-- 增加查询条件，查询出未和并的加油单信息110
and b.refueling_date = a.refueling_date)111
group by FLIGHT_TYPE, REFUELING_DATE, MEASURE_UNIT112
113
union all114
-- 增加从  合并备份表中 t_fuel_invoice_receipt_merge 查询出合并前的加油单信息115
select a.FLIGHT_TYPE,116
a.REFUELING_DATE,117
a.MEASURE_UNIT,118
sum(a.QTY_KG),119
sum(a.QTY)120
from T_FUEL_REFUELING_RECEIPT a121
where a.QTY < 0122
and (a.RECEIPT_NO, a.refueling_date) in123
(select mm.receipt_no,mm.refueling_date from
t_fuel_invoice_receipt_merge mm
124
where mm.id in (125
select r.merge_id from t_fuel_invoice_receipt r126
where r.invoice_no = i_proxyid127
and r.merge_id is not null-- 增加查询条件，查询出和并的加油单信息128
)129
and mm.refueling_date = a.refueling_date)130
group by FLIGHT_TYPE, REFUELING_DATE, MEASURE_UNIT;131
132
BEGIN133
134
SELECT AMOUNT,135
STATION_CODE,136
AREA_CODE,137
INVOICE_DATE,138
SUPPLIER_ID,139
UNIT_PRICE,140
MEASURE_UNIT,141

QTY,142
CURRENCY,143
INVOICE_NO,144
COUNTRYTAXFLAG145
INTO P_AMOUNT_INVOICE,146
P_DEPT_AIRPORT,147
P_AREA_CODE,148
P_INVOICE_DATE,149
P_SUPPLIER_ID,150
P_UNIT_PRICE,151
P_MEASURE_UNIT,152
P_QTY_INVOICE,153
P_CURRENCY_INVOICE,154
P_INVOICE_NO,155
P_COUNTRYTAXFLAG156
FROM T_FUEL_INVOICE A, T_AIRPORT B157
WHERE A.PROXYID = I_PROXYID158
AND A.STATION_CODE = B.AIRPORT_CODE3;159
160

/********************************************************************************
*
161
1 、取出对应的加油单的加油量，并把单位转换账单数量单位162
2 、根据供油公司、加油航站、账单⽇期，取出单价，并做单位转换163
3 、  计算内部加油总⾦额164
4 、抽油  油量、抽油架次165

*********************************************************************************
**/
166
p_QTY_recept_sum    := 0;167
p_QTY_minus_recept_sum :=0;168
p_QTY_recept_amount := 0;169
p_recept_price_sum  := 0;170
p_count             := 0;171
p_remarks := '';172
173
/************************************************************************174
判断是不是浦东油料公司的账单，要是浦东油料公司的账单，175
审核的时候不按油单的航班性质取油价，176
账单是外线  就取国际航线油价，内线就取国内航线油价177
*************************************************************************/178
179
p_row_count := 0;180

181
select count(*)182
into p_row_count183
from T_FUEL_INVOICE a, t_fuel_supplier b184
where a.PROXYID = i_PROXYID185
and  a.supplier_id = b.proxyid186
and  b.supplier_no = '010'187
and  a.station_code = 'PVG';188
189
190
if (p_row_count > 0) then191
select LINE_TYPE192
into   p_LINE_TYPE193
from T_FUEL_INVOICE a, t_fuel_supplier b194
where a.PROXYID = i_PROXYID195
and  a.supplier_id = b.proxyid196
and  b.supplier_no = '010'197
and  a.station_code = 'PVG';198
end if;199
200
-- 附加费201
p_SURCHARGE_DH := 0;202
-- 国内税附加费203
p_SURCHARGE_DH_Country := 0;204
p_sur_flt_rownum      :=0;205
p_sur_weight_rownum   :=0;206
p_sur_dh_flt_rownum   :=0;207
p_sur_dh_weight_rownum :=0;208
/***************** 内部  加油  架次
*****************************************************/
209
p_flight_num := 0;210
211
-- 开始循环迭代按航班类型、⽇期、单位汇总的油量数据212
open c_fuel;213
fetch c_fuel214
into p_FLIGHT_TYPE_recept, p_recept_date, p_MEASURE_UNIT_recept, p_QTY_KG,
p_QTY;
215
while (c_fuel%found) loop216
217
p_PRICE     := 0;218
p_row_count := 0;219
220
-- 如果是浦东油料公司，航班性质取账单  内线（ DOME ）、外线（ INTL ）221

if p_LINE_TYPE is not null then222
p_FLIGHT_TYPE_recept := p_LINE_TYPE;223
end if;224
225
226
227
/* 如果是国际、地区航班取出对应的国际单价 , 单位与账单统⼀ */228
if instr('AREA INTL', p_AREA_CODE, 1, 1) > 0 then229
230
-- 如果油单数量单位和账单数量单位都为 LT 或 GA ，则油单数量取 qty231
if instr('LT GA', p_MEASURE_UNIT_recept, 1, 1) > 0 and232
instr('LT GA', p_MEASURE_UNIT, 1, 1) > 0 then233
-- 数量234
p_QTY_recept := p_QTY * EXCHANGE_UNIT(p_MEASURE_UNIT_recept,235
p_MEASURE_UNIT,236
p_recept_date,237
'MEASURE');238
-- 如果油单数量单位为 LT 或 GA ，账单数量单位都为 KG 或 TG ，则油单数量取 qty_KG239
elsif instr('LT GA', p_MEASURE_UNIT_recept, 1, 1) > 0 and240
instr('KG TG', p_MEASURE_UNIT, 1, 1) > 0 then241
p_QTY_recept := p_QTY_KG * EXCHANGE_UNIT('KG',242
p_MEASURE_UNIT,243
p_recept_date,244
'MEASURE');245
246
-- 其他情况取 qty247
else248
p_QTY_recept := p_QTY * EXCHANGE_UNIT(p_MEASURE_UNIT_recept,249
p_MEASURE_UNIT,250
p_recept_date,251
'MEASURE');252
end if;253
254
p_QTY_recept_sum := p_QTY_recept_sum + p_QTY_recept; -- 单位转换后的数量255
256
if p_QTY < 0  then257
p_QTY_minus_recept_sum := p_QTY_minus_recept_sum + p_QTY_recept;  -- 单位
转换后的抽油量（负数）
258
end if;259
260
-- 查询是否存在单价261
select count(*)262

into p_row_count263
from T_FUEL_INT_UNIT_PRICE264
where SUPPLIER_ID = p_SUPPLIER_ID -- 供油公司265
and REFUELING_AIRPORT = p_dept_airport -- 加油航站266
and p_recept_date >= APPLY_DATE -- 账单⽇期267
and p_recept_date <= EXPIRY_DATE;268
269
-- 如果存在单价，则转换单价270
if (p_row_count > 0) then271
select PRICE, CURRENCY, MEASURE_UNIT272
into p_PRICE, p_CURRENCY_price, P_MEASURE_UNIT_price273
from T_FUEL_INT_UNIT_PRICE274
where SUPPLIER_ID = p_SUPPLIER_ID275
and REFUELING_AIRPORT = p_dept_airport276
and p_recept_date >= APPLY_DATE277
and p_recept_date <= EXPIRY_DATE;278
279
p_PRICE := (p_PRICE * EXCHANGE_UNIT(p_CURRENCY_price,280
p_CURRENCY_INVOICE,281
p_recept_date,282
'CURRENCY')) /283
EXCHANGE_UNIT(P_MEASURE_UNIT_price,284
p_MEASURE_UNIT,285
p_recept_date,286
'MEASURE');287
end if;288
289
end if;290
291
292
/* 如果是国内航班取出对应的国内单价 , 单位与账单统⼀ */293
if instr('DOME', p_AREA_CODE, 1, 1) > 0 then294
-- 油量 KG 数295
p_QTY_recept     := p_QTY_KG * EXCHANGE_UNIT('KG',296
p_MEASURE_UNIT,297
p_recept_date,298
'MEASURE');299
p_QTY_recept_sum := p_QTY_recept_sum + p_QTY_recept; -- 单位转换后的数量300
301
if p_QTY < 0  then302
p_QTY_minus_recept_sum := p_QTY_minus_recept_sum + p_QTY_recept;  -- 单位
转换后的抽油量（负数）
303

end if;304
305
-- 查询是否存在单价306
p_row_count := 0;307
308
select count(*)309
into p_row_count310
from T_FUEL_DOM_UNIT_PRICE a311
where a.supplier_id = p_SUPPLIER_ID -- 供油公司312
and FLIGHT_TYPE =
decode(p_FLIGHT_TYPE_recept,'AREA','INTL',p_FLIGHT_TYPE_recept) -- 航班类型
313
and a.apply_date <= p_recept_date -- 账单⽇期314
and a.expiry_date >= p_recept_date315
and p_dept_airport IN -- 加油航站316
(select AIRPORT317
from T_FUEL_DOM_PRICE_AIRPORT318
where DOM_UNIT_PRICE_ID = a.PROXYID319
and APPLY_DATE <= p_recept_date320
and EXPIRY_DATE >= p_recept_date);321
322
-- 如果存在单价，则转换单价323
if (p_row_count > 0) then324
325
-- 国内同⼀个加油公司同⼀个时间段同⼀个单价对于的机场326
select a.PRICE, a.CURRENCY, a.MEASURE_UNIT327
into p_PRICE, p_CURRENCY_price, P_MEASURE_UNIT_price328
from T_FUEL_DOM_UNIT_PRICE a329
where a.supplier_id = p_SUPPLIER_ID330
and FLIGHT_TYPE =
decode(p_FLIGHT_TYPE_recept,'AREA','INTL',p_FLIGHT_TYPE_recept)
331
and a.apply_date <= p_recept_date332
and a.expiry_date >= p_recept_date333
and p_dept_airport IN334
(select AIRPORT335
from T_FUEL_DOM_PRICE_AIRPORT336
where DOM_UNIT_PRICE_ID = a.PROXYID337
and APPLY_DATE <= p_recept_date338
and EXPIRY_DATE >= p_recept_date)339
and rownum = 1;340
341
p_PRICE := (p_PRICE * EXCHANGE_UNIT(p_CURRENCY_price,342
p_CURRENCY_INVOICE,343
p_recept_date,344

'CURRENCY')) /345
EXCHANGE_UNIT(P_MEASURE_UNIT_price,346
p_MEASURE_UNIT,347
p_recept_date,348
'MEASURE');349
end if;350
351
end if;352
353
-- 附加费计算开始354
if p_QTY_recept > 0 then355
--1 加油356
--1.1 、按班次收费的加油附加费357
select count(*)  into p_sur_flt_rownum358
FROM T_FUEL_SURCHARGE A359
WHERE A.SUPPLIER_ID = p_SUPPLIER_ID360
AND A.REFUELING_AIRPORT = p_dept_airport361
AND A.APPLY_DATE <= p_recept_date362
AND A.EXPIRY_DATE >= p_recept_date363
AND A.MEASURE_UNIT = 'FLIGHT'364
AND (A.SUR_KIND <> '1' OR A.SUR_KIND IS NULL);365
if p_sur_flt_rownum>0 then          -- 如果有按班次收的附加费366
-- 查询航班次数367
SELECT COUNT(*)368
INTO p_flight_num369
FROM T_FUEL_REFUELING_RECEIPT370
WHERE QTY > 0 -- 加油371
AND  REFUELING_DATE=p_recept_date372
AND (RECEIPT_NO, REFUELING_DATE) IN373
(SELECT RECEIPT_NO, REFUELING_DATE374
FROM T_FUEL_INVOICE_RECEIPT375
WHERE INVOICE_NO = I_PROXYID376
AND REFUELING_DATE=p_recept_date);377
p_SURCHARGE_DH := p_SURCHARGE_DH + p_flight_num378
*pkg_fuel_surcharge.CALC_ADD_PRICE(p_recept_date,379
p_SUPPLIER_ID,380
p_dept_airport,381
'',382
'FLIGHT',383

p_CURRENCY_INVOICE);
384
end if;385

--1.2 、按重量或体积收费的加油附加费386
select count(*)  into p_sur_weight_rownum387
FROM T_FUEL_SURCHARGE A388
WHERE A.SUPPLIER_ID = p_SUPPLIER_ID389
AND A.REFUELING_AIRPORT = p_dept_airport390
AND A.APPLY_DATE <= p_recept_date391
AND A.EXPIRY_DATE >= p_recept_date392
AND A.MEASURE_UNIT <> 'FLIGHT'393
AND (A.SUR_KIND <> '1' OR A.SUR_KIND IS NULL);394
if p_sur_weight_rownum>0 then          -- 如果有按重量或体积收的附加费395
/***************** 内部  加油  附加费标准  附加费⾦额
*****************************************************/
396
-- 计算  东航认为的附加费     数量单位转换397
p_SURCHARGE_DH := p_SURCHARGE_DH + p_QTY_recept398

*pkg_fuel_surcharge.CALC_ADD_PRICE(p_recept_date,
399

p_SUPPLIER_ID,
400

p_dept_airport,
401

p_MEASURE_UNIT,
402

'WEIGHT',
403

p_CURRENCY_INVOICE);
404
end if;405
end if;406
407
-- 发票有国内税408
if P_COUNTRYTAXFLAG is NULL or P_COUNTRYTAXFLAG <> 'Y' then409
-- 国内税附加费计算开始410
if p_QTY_recept > 0 then411
--1 加油412
--1.1 、按班次收费的加油附加费413
select count(*)  into p_sur_flt_rownum414
FROM T_FUEL_SURCHARGE A415
WHERE A.SUPPLIER_ID = p_SUPPLIER_ID416
AND A.REFUELING_AIRPORT = p_dept_airport417
AND A.APPLY_DATE <= p_recept_date418
AND A.EXPIRY_DATE >= p_recept_date419
AND A.MEASURE_UNIT = 'FLIGHT'420
AND (A.SUR_KIND <> '1' OR A.SUR_KIND IS NULL);421
if p_sur_flt_rownum>0 then          -- 如果有按班次收的附加费422

-- 查询航班次数423
SELECT COUNT(*)424
INTO p_flight_num425
FROM T_FUEL_REFUELING_RECEIPT426
WHERE QTY > 0 -- 加油427
AND  REFUELING_DATE=p_recept_date428
AND (RECEIPT_NO, REFUELING_DATE) IN429
(SELECT RECEIPT_NO, REFUELING_DATE430
FROM T_FUEL_INVOICE_RECEIPT431
WHERE INVOICE_NO = I_PROXYID432
AND REFUELING_DATE=p_recept_date);433
434
-- 国内税435
p_SURCHARGE_DH_Country := p_SURCHARGE_DH_Country + p_flight_num436

*pkg_fuel_surcharge.CALC_ADD_PRICE_TWO(p_recept_date,
437
p_SUPPLIER_ID,438
p_dept_airport,439
'',440
'FLIGHT',441

p_CURRENCY_INVOICE);
442
443
end if;444
--1.2 、按重量或体积收费的加油附加费445
select count(*)  into p_sur_weight_rownum446
FROM T_FUEL_SURCHARGE A447
WHERE A.SUPPLIER_ID = p_SUPPLIER_ID448
AND A.REFUELING_AIRPORT = p_dept_airport449
AND A.APPLY_DATE <= p_recept_date450
AND A.EXPIRY_DATE >= p_recept_date451
AND A.MEASURE_UNIT <> 'FLIGHT'452
AND (A.SUR_KIND <> '1' OR A.SUR_KIND IS NULL);453
if p_sur_weight_rownum>0 then          -- 如果有按重量或体积收的附加费454
/***************** 内部  加油  附加费标准  附加费⾦额
*****************************************************/
455
-- 计算  东航认为的附加费     数量单位转换456
457
-- 国内税458
p_SURCHARGE_DH_Country := p_SURCHARGE_DH_Country + p_QTY_recept459

*pkg_fuel_surcharge.CALC_ADD_PRICE_TWO(p_recept_date,
460

p_SUPPLIER_ID,
461

p_dept_airport,
462

p_MEASURE_UNIT,
463

'WEIGHT',
464

p_CURRENCY_INVOICE);
465
end if;466
end if;467
end if;468
469
470
--2 抽油471
if p_QTY_recept < 0 then472
--2.1 、按班次收费的抽油附加费473
select count(*)  into p_sur_dh_flt_rownum474
FROM T_FUEL_SURCHARGE A475
WHERE A.SUPPLIER_ID = p_SUPPLIER_ID476
AND A.REFUELING_AIRPORT = p_dept_airport477
AND A.APPLY_DATE <= p_recept_date478
AND A.EXPIRY_DATE >= p_recept_date479
AND A.MEASURE_UNIT = 'FLIGHT'480
AND A.SUR_KIND = '1';481
if p_sur_dh_flt_rownum>0 then          -- 如果有按班次收的附加费，且油单数量为正482
-- 查询航班次数483
SELECT COUNT(*)484
INTO p_flight_num485
FROM T_FUEL_REFUELING_RECEIPT486
WHERE QTY < 0 -- 抽油487
AND  REFUELING_DATE=p_recept_date488
AND (RECEIPT_NO, REFUELING_DATE) IN489
(SELECT RECEIPT_NO, REFUELING_DATE490
FROM T_FUEL_INVOICE_RECEIPT491
WHERE INVOICE_NO = I_PROXYID492
AND REFUELING_DATE=p_recept_date);493
v_temp_amount := p_flight_num*pkg_fuel_surcharge.CALC_LESS_PRICE(494
p_recept_date,495
p_SUPPLIER_ID,496
p_dept_airport,497
'',498

'FLIGHT',499
p_CURRENCY_INVOICE);500
p_SURCHARGE_DH := p_SURCHARGE_DH + v_temp_amount;501
end if;502
--2.2 、按重量或体积收费的抽油附加费503
select count(*)  into p_sur_dh_weight_rownum504
FROM T_FUEL_SURCHARGE A505
WHERE A.SUPPLIER_ID = p_SUPPLIER_ID506
AND A.REFUELING_AIRPORT = p_dept_airport507
AND A.APPLY_DATE <= p_recept_date508
AND A.EXPIRY_DATE >= p_recept_date509
AND A.MEASURE_UNIT <> 'FLIGHT'510
AND A.SUR_KIND = '1';511
if p_sur_dh_weight_rownum>0 then          -- 如果有按重量或体积收的附加费512
/***************** 内部  抽油  附加费标准  附加费⾦额
*****************************************************/
513
-- 计算  东航认为的附加费     数量单位转换514
v_temp_amount :=
p_QTY_recept*pkg_fuel_surcharge.CALC_LESS_PRICE(p_recept_date,
515

p_SUPPLIER_ID,
516

p_dept_airport,
517

p_MEASURE_UNIT,
518
'WEIGHT',519

p_CURRENCY_INVOICE);
520
p_SURCHARGE_DH := p_SURCHARGE_DH + abs(v_temp_amount);521
end if;522
end if;523
524
-- 发票有国内税525
if P_COUNTRYTAXFLAG is NULL or P_COUNTRYTAXFLAG <> 'Y' then526
-- 国内税527
--2 抽油528
if p_QTY_recept < 0 then529
--2.1 、按班次收费的抽油附加费530
select count(*)  into p_sur_dh_flt_rownum531
FROM T_FUEL_SURCHARGE A532
WHERE A.SUPPLIER_ID = p_SUPPLIER_ID533
AND A.REFUELING_AIRPORT = p_dept_airport534
AND A.APPLY_DATE <= p_recept_date535
AND A.EXPIRY_DATE >= p_recept_date536

AND A.MEASURE_UNIT = 'FLIGHT'537
AND A.SUR_KIND = '1';538
if p_sur_dh_flt_rownum>0 then          -- 如果有按班次收的附加费，且油单数量为
正
539
-- 查询航班次数540
SELECT COUNT(*)541
INTO p_flight_num542
FROM T_FUEL_REFUELING_RECEIPT543
WHERE QTY < 0 -- 抽油544
AND  REFUELING_DATE=p_recept_date545
AND (RECEIPT_NO, REFUELING_DATE) IN546
(SELECT RECEIPT_NO, REFUELING_DATE547
FROM T_FUEL_INVOICE_RECEIPT548
WHERE INVOICE_NO = I_PROXYID549
AND REFUELING_DATE=p_recept_date);550
v_temp_amount := p_flight_num*pkg_fuel_surcharge.CALC_LESS_PRICE_TWO(551
p_recept_date,552
p_SUPPLIER_ID,553
p_dept_airport,554
'',555
'FLIGHT',556

p_CURRENCY_INVOICE);
557
p_SURCHARGE_DH_Country := p_SURCHARGE_DH_Country + v_temp_amount;558
end if;559
--2.2 、按重量或体积收费的抽油附加费560
select count(*)  into p_sur_dh_weight_rownum561
FROM T_FUEL_SURCHARGE A562
WHERE A.SUPPLIER_ID = p_SUPPLIER_ID563
AND A.REFUELING_AIRPORT = p_dept_airport564
AND A.APPLY_DATE <= p_recept_date565
AND A.EXPIRY_DATE >= p_recept_date566
AND A.MEASURE_UNIT <> 'FLIGHT'567
AND A.SUR_KIND = '1';568
if p_sur_dh_weight_rownum>0 then          -- 如果有按重量或体积收的附加费569
/***************** 内部  抽油  附加费标准  附加费⾦额
*****************************************************/
570
-- 计算  东航认为的附加费     数量单位转换571
v_temp_amount :=
p_QTY_recept*pkg_fuel_surcharge.CALC_LESS_PRICE_TWO(p_recept_date,
572

p_SUPPLIER_ID,
573

p_dept_airport,
574

p_MEASURE_UNIT,
575
'WEIGHT',576

p_CURRENCY_INVOICE);
577
p_SURCHARGE_DH_Country := p_SURCHARGE_DH_Country +
abs(v_temp_amount);
578
end if;579
end if;580
end if;581
582
p_QTY_recept_amount := p_QTY_recept_amount + (p_QTY_recept * p_PRICE); -- 总⾦
额计算
583
p_recept_price_sum  := p_recept_price_sum + p_PRICE;584
p_count             := p_count + 1;585
586
587
fetch c_fuel588
into p_FLIGHT_TYPE_recept, p_recept_date, p_MEASURE_UNIT_recept, p_QTY_KG,
p_QTY;
589
end loop;590
close c_fuel;591
592
593
594
595
596
/***************** 计算加油单单价平均值
*****************************************************/
597
if (p_count > 0) then598
p_PRICE := (p_recept_price_sum / p_count);599
end if;600
601
/***************** 账单附加费总⾦额
*****************************************************/
602
p_row_count := 0;603
select count(*)604
into p_row_count605
from T_FUEL_INVOICE_SURCHARGE606
where INVOICE_NO = i_PROXYID;607
608
if (p_row_count > 0) then609
select sum(AMOUNT * EXCHANGE_UNIT(CURRENCY,610
p_CURRENCY_INVOICE,611

p_INVOICE_DATE,612
'CURRENCY'))613
into p_SURCHARGE614
from T_FUEL_INVOICE_SURCHARGE615
where INVOICE_NO = i_PROXYID;616
end if;617
618
------------------- 审核结果备注 --------------------------619
if p_QTY_INVOICE > p_QTY_recept_sum then620
p_remarks := ' 加油数量差异 ';621
elsif p_SURCHARGE > p_SURCHARGE_DH then622
p_remarks := ' 附加费差异 ';623
elsif p_amount_INVOICE > p_QTY_recept_amount + p_SURCHARGE_DH then624
p_remarks := ' 总⾦额差异 ';625
end if;626
627
628
-- 插⼊国内审核存在差异的数据629
UPDATE T_FUEL_INVOICE A630
SET RECEIPT_QTY      = P_QTY_RECEPT_SUM,631
RECEIPT_PRICE    = P_PRICE,632
SURCHARGE_AMOUNT = P_SURCHARGE,633
RECEIPT_SUCHARGE = P_SURCHARGE_DH - p_SURCHARGE_DH_Country,634
RECEIPT_AMOUNT   = P_QTY_RECEPT_AMOUNT,635
MU_AMOUNT        = P_QTY_RECEPT_AMOUNT + P_SURCHARGE_DH -
p_SURCHARGE_DH_Country,   -- 减掉国内税
636
DIFF_AMOUNT      = P_AMOUNT_INVOICE - P_QTY_RECEPT_AMOUNT -
(P_SURCHARGE_DH - p_SURCHARGE_DH_Country),
637
DIFF_FLAG        = P_REMARKS,638
INVOICE_STATUS   = '01', -- 账单设置为 '01' （已经审核）639
AUDIT_USER       = I_USERID,640
AUDIT_TIME       = SYSDATE,641
MU_TAX_AMOUNT    = (P_QTY_RECEPT_AMOUNT + P_SURCHARGE_DH -
p_SURCHARGE_DH_Country) /(1+EXCHANGE_UNIT(NULL,NULL,a.invoice_date,'RATE'))*
(EXCHANGE_UNIT(NULL,NULL,a.invoice_date,'RATE')), -- 计算税⾦ : 内部总⾦额的 17% （税率这
⾥为固定 17% ，税率变化可在这修改  或增加税率维护表）
642
MU_NO_TAX_AMOUNT = (P_QTY_RECEPT_AMOUNT + P_SURCHARGE_DH -
p_SURCHARGE_DH_Country) /(1+EXCHANGE_UNIT(NULL,NULL,a.invoice_date,'RATE'))*1
643
WHERE PROXYID = I_PROXYID;644
645
646
UPDATE T_FUEL_INVOICE T647
SET DIFF_FLAG = DIFF_FLAG || ',' ||648
(SELECT REMARK649

FROM (SELECT A.INVOICE_NO,650
' ⽆法找到对应的油单： ' ||
WM_CONCAT(A.RECEIPT_NO) ||
651
'( 油单未录⼊或者未核对 ) 。 ' REMARK652
FROM T_FUEL_INVOICE_RECEIPT A653
LEFT JOIN T_FUEL_REFUELING_RECEIPT B ON
A.RECEIPT_NO =  B.RECEIPT_NO
654
AND
A.REFUELING_DATE =  B.REFUELING_DATE
655
WHERE B.RECEIPT_NO IS NULL656
AND INVOICE_NO = I_PROXYID657
GROUP BY A.INVOICE_NO))658
WHERE T.PROXYID IN (SELECT A.INVOICE_NO659
FROM T_FUEL_INVOICE_RECEIPT A660
LEFT JOIN T_FUEL_REFUELING_RECEIPT B ON A.RECEIPT_NO =
B.RECEIPT_NO
661
AND A.REFUELING_DATE
=  B.REFUELING_DATE
662
WHERE B.RECEIPT_NO IS NULL663
AND INVOICE_NO = I_PROXYID664
GROUP BY A.INVOICE_NO);665
666
-- 插⼊监控数据667
INSERT INTO T_FUEL_INVOICE_HANDLE_RECORD668
(PROXYID, INVOICE_ID, OPERATOR, OPERATE_TIME, STEP)669
VALUES670
(SQ_APPRCAL.NEXTVAL, I_PROXYID, I_USERID, SYSDATE, '01');671
672
COMMIT;673
674
END Sp_Compare_Fuel;675
676
677