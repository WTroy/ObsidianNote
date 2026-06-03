---
title: TABLE
source: 有道云笔记
imported: true
related: ["FOFAS系统迁移", "视图 V_FULE_INVOICE_RECEIPT_COSTS 的优化", "近期的SQL脚本", "数据迁移", "浦东航油虚拟账单确认_国际账单差额审核", "备份开账存储过程"]
---

```yaml
HSS_AP_VENDORS_ALL: 供应商信息表；还有⼀个相关的表： HSS_AP_VENDOR_SITES_ALL
```

账单表： T_FUEL_INVOICE

```sql
# 供应商信息查询
-- HSS_AP_VENDORS_ALL1 零时表
SELECT DISTINCT VENDOR_NUMBER vendor_number, VENDOR_NAME vendor_name
FROM HSS_AP_VENDOR_SITES_ALL S, HSS_AP_VENDORS_ALL A
WHERE S.VENDORS_ID = A.VENDOR_ID
AND S.BUSINESS_TYPE = 108
AND A.bank_account_number is not null
AND ARCHIVE_FLAG = 0
AND A.Supper_Type in('ALL',  'DOME', 'INTL')
--and vendor_number = 'S032493
order by vendor_name;
select * from HSS_AP_VENDORS_ALL1 where vendor_number = 'S063645';
select * from HSS_AP_VENDORS_ALL where vendor_number = 'S063645';
select * from HSS_AP_VENDOR_SITES_ALL1 where VENDORS_ID = '982741';
select * from HSS_AP_VENDOR_SITES_ALL where VENDORS_ID = '982741';
INSERT INTO FOFAS.HSS_AP_VENDORS_ALL (VENDOR_ID, VENDOR_NUMBER, VENDOR_NAME,
TAX_REFERENCE, VENDOR_TYPE, BANK_ACCOUNT_ID, BANK_ACCOUNT_USE_ID,
BANK_ACCOUNT_NUMBER, BANK_ACCOUNT_NAME, BANK_ACCOUNT_DESCRIPTION, CURRENCY_CODE,
BANK_NAME, BANK_CODE, BRANCHES_NAME, SWIFT_CODE, COUNTRY_CODE, PROVINCE, CITY,
BANK_PHONE, BANK_ADDRESS, BANK_POSTAL_CODE, BANK_ZONE_CODE, ACCOUNT_TYPE,
GENERAL_SWIFT_CODE, STREET, BUILDING_NUMBER, DISABLE_DATE, CREATOR, CREATE_TIME,
UPDATER, UPDATE_TIME, PROXYID, ARCHIVE_FLAG, SUPPER_TYPE)
select VENDOR_ID, VENDOR_NUMBER, VENDOR_NAME, TAX_REFERENCE, VENDOR_TYPE,
BANK_ACCOUNT_ID, BANK_ACCOUNT_USE_ID, BANK_ACCOUNT_NUMBER, BANK_ACCOUNT_NAME,
BANK_ACCOUNT_DESCRIPTION, CURRENCY_CODE, BANK_NAME, BANK_CODE, BRANCHES_NAME,
SWIFT_CODE, COUNTRY_CODE, PROVINCE, CITY, BANK_PHONE, BANK_ADDRESS,
BANK_POSTAL_CODE, BANK_ZONE_CODE, ACCOUNT_TYPE, GENERAL_SWIFT_CODE, STREET,
BUILDING_NUMBER, DISABLE_DATE, CREATOR, CREATE_TIME, UPDATER, UPDATE_TIME,
PROXYID, '0', 'INTL' from HSS_AP_VENDORS_ALL
where vendor_number = 'S015042' and bank_account_id = '180487';
INSERT INTO FOFAS.HSS_AP_VENDOR_SITES_ALL (PROXYID, VENDORS_ID, VENDOR_SITE_ID,
SITE_NAME, ADDRESS, ADDRESSEE, PHONE, FAX, POSTAL_CODE, DISABLE_DATE,
BUSINESS_TYPE, ORG_CODE, INTERCOMPANY_CODE, CREATOR, CREATE_TIME, UPDATER,
UPDATE_TIME)
select PROXYID, VENDORS_ID, VENDOR_SITE_ID, SITE_NAME, ADDRESS, ADDRESSEE, PHONE,
FAX, POSTAL_CODE, DISABLE_DATE, BUSINESS_TYPE, ORG_CODE, INTERCOMPANY_CODE,
CREATOR, CREATE_TIME, UPDATER, UPDATE_TIME from HSS_AP_VENDOR_SITES_ALL1 where
VENDORS_ID = '974643';
```

增值税发票表： T_TAX_SPECIAL_INVOICE

```sql
select * from t_fuel_invoice WHERE INVOICE_NO in ('10247336');-- 账单信息
select * from t_fuel_invoice_receipt where invoice_no = '73429850'; -- 账单明细信息
```

invoice_no 和 proxyid 关联

```sql
select * from t_fuel_invoice_surcharge where invoice_no = '73429850';-- 账单附加费信
```

息   invoice_no 和 proxyid 关联

```sql
SELECT * FROM t_fuel_invoice_ap_invoice where source_receipt_id = 'HY-001-202404-168';
SELECT * FROM t_fuel_invoice_ap_detail where ap_invoice_id = '67769' order by
amount for update;
select * from t_fuel_invoice_write_off where ap_invoice_id in ('67769') order by
receipt_amount for update;
select * from t_fuel_invoice_write_off where ap_invoice_id in ('67771') and
flight_id in ('7660659') for update;
SELECT * FROM DC_FLIGHT_PLAN dfp WHERE dfp.ID IN ('7660659');
SELECT
af.proxyid,
af.invoice_no,
af.invoice_date,
af.qty,
af.amount,
af.station_code,
af.invoice_type,
ap.source_receipt_id
FROM
t_fuel_invoice af,
```

t_fuel_invoice_ap_invoice ap --ap 发票表22
WHERE23

```sql
af.ap_invoice_id = ap.proxyid
AND ap.notice_status = '13'
AND af.proxyid = '72643856';
-- 传共享的那张表 :
T_FUEL_INVOICE_AP_INTERFACE
-- 根据共享接⼝要求，按照公司机型航线汇总的数据
-- 总⾦额应该是 ap 发票表⾥⾦额⼀样的
-- ⼀般是航班重复了，导致关联预提的时候重复了
-- 增值税发票查询不到的问题处理：
-- ⼤概率是有的，但是 invoice_id 和发票表⾥的不⼀致 :
-- 处理流程：
-- 发票表⾥真的没有发票或者发票状态是未确认（ is_confirm=0 ），让业务⼈员处理
-- 检查⾦额是否和账单表⼀致
-- 确认发票表的 is_confirm 值是不是为 1
-- 如果以上都符合，则更新发票表的 invoice_id 和账单表的 proxyid ⼀致
SELECT t.proxyid as proxyid,
c.ou_code AS companyCode,
c.company_name companyName,
t.supplier as supplierId,
T.INVOICE_NO AS invoiceNo,
T.INVOICE_CODE AS invoiceCode,
T.INVOICE_DATE AS invoiceDate,
to_char(T.INVOICE_DATE, 'YYYY-MM-DD') AS invoiceDateStr,
T.INVOICE_AMOUNT AS invoiceAmount,
T.TAX_AMOUNT AS taxAmount,
T.TAX_AMOUNT_RATE AS taxAmountRate,
T.NO_TAX_AMOUNT AS noTaxAmount,
T.INVOICE_ID as invoiceId
FROM T_TAX_SPECIAL_INVOICE T ,t_company c
where 1=1  and t.company_code=c.company_name
-- and INVOICE_ID = '73588042'
and invoice_no = '24512000000050006096'
order by  INVOICE_DATE DESC;
SELECT *
FROM T_TAX_SPECIAL_INVOICE T
where 1=
-- and INVOICE_ID = '73588042'
and invoice_no = '24112000000095772626'
order by  INVOICE_DATE DESC;
update T_TAX_SPECIAL_INVOICE SET invoice_id = '74472637' where proxyid = (SELECT
proxyid
FROM T_TAX_SPECIAL_INVOICE T
where invoice_no = '24112000000095772626');
select * from t_fuel_invoice WHERE INVOICE_NO in ('24112000000095772626', ''); --
```

账单信息

t_airport ：  场站信息；  Dc_flight_plan 航班计划表
油价表；汇率表

```sql
-- 如果增值税发票表⾥没有数据，查⼀下电票接⼝⽇志
select * from t_sys_interface_outbound where task_number =
'24462000000008762814' order by request_time desc;
-- 如果江苏公司还没有接⼊电票系统，需要业务的⽼师⾃⼰⼿⼯确认，⼿⼯上传附件
-- 如果增票表没数据，发票表是否确认为 1 ，就把发票表⾥这个是否确认改成 0 ，让徐⽼师重新确认
-- 批量处理
MERGE INTO T_TAX_SPECIAL_INVOICE A
USING t_fuel_invoice B
ON (A.INVOICE_NO = B.INVOICE_NO AND A.INVOICE_NO IN ('25317000002182558538'))
WHEN MATCHED THEN
UPDATE SET A.invoice_id = B.PROXYID;
select * from t_airport;
SELECT a.*, c.R12_TYPE
FROM t_aircraft a,
T_FUEL_ACTYPE_CONTRAST c
WHERE a.ac_type = c.oil_ac_type
AND a.TAIL_NO in ('B659Z','B658S')
ORDER BY a.CREATE_TIME;
select * from Dc_flight_plan;
-- 国际油价
SELECT * FROM t_Fuel_Int_Unit_Price WHERE REFUELING_AIRPORT = 'ICN';
-- 国内油价
SELECT * FROM T_FUEL_DOM_UNIT_PRICE ;
-- 汇率信息
SELECT * FROM T_EXCHANGE_RATE ;  -- 联系彭磊，管控的
SELECT *
FROM T_FUEL_DOM_UNIT_PRICE P, T_FUEL_DOM_PRICE_AIRPORT A
```

航班留存油量表：
航油供应商表： T_FUEL_SUPPLIER
影像系统上传⽂件：

```sql
WHERE P.PROXYID = A.DOM_UNIT_PRICE_ID and to_char(a.apply_date, 'yyyyMMdd') =
'20240801' and p.confirm_status = '0';
SELECT
*
FROM
kb_v_flight_fuelinfo i
WHERE
to_char(i.flight_bj_date, 'yyyymmdd') = '20240523'
--and i.flight_no='5357'
--and carrier = 'MU'
AND i.tail_no = 'B6755'
SELECT * FROM T_DICT_CODE tdc WHERE CODE_NAME in
('serialNumberPath','dmsFileUploadPath');
SELECT PROCESS_STATUS , PAY_NOTICE_TYPE  FROM T_FUEL_INVOICE_AP_INVOICE tfiai
WHERE TFIAI.SOURCE_RECEIPT_ID = 'HY-013-202405-05';
SELECT * FROM T_FUEL_INVOICE_AP_INVOICE tfiai WHERE TFIAI.SOURCE_RECEIPT_ID in
('HY-013-202405-06','HY-013-202405-07','HY-013-202405-08'
,'HY-020-202407-03','HY-020-202407-04','HWHY-020-202407-05'); -- HY-013-202212-054
SELECT * FROM T_FUEL_INVOICE_AP_INVOICE t WHERE TO_CHAR(t.CREATE_TIME  , 'yyyy-MM-dd') = '2024-05-07';
select ap.proxyid,
ap.notice_status noticeStatus,
ap.source_receipt_id sourceReceiptId,
ap.pay_scan panScan,
AP.PROCESS_STATUS processStatus,
AP.INVOICE_FILE invoiceFile,
AP.FILE_PATH filePath
from t_fuel_invoice_ap_invoice ap
where ap.notice_status = '07'
and ap.upload_flag in ('0', '2')
and ap.process_status in ('B', 'C','E') and
```

ap.create_time > sysdate - 45;18

```sql
select f.proxyid,
f.file_name fileName,
f.file_path filePath,
f.state,
f.invoice_id invoiceId,
f.upload_type uploadType
from t_fuel_invoice i, t_fuel_invoice_import_file f
where i.proxyid = f.invoice_id
and f.state =
--and f.upload_flag in ('0', '2','3')
and i.ap_invoice_id = '7018';
SELECT * FROM T_SYS_INTERFACE_OUTBOUND WHERE INTERFACE_NAME = ' 影像附件上传接⼝ '
AND TASK_NUMBER IN ('HY-1018-202408-10','HY-1018-202408-11') ORDER BY
REQUEST_TIME DESC ;
-- 我还可以抢救⼀下 --34
select ap.proxyid,
ap.notice_status noticeStatus,
ap.source_receipt_id sourceReceiptId,
ap.pay_scan panScan,
AP.PROCESS_STATUS processStatus,
AP.INVOICE_FILE invoiceFile,
AP.FILE_PATH filePath
from t_fuel_invoice_ap_invoice ap
where ap.notice_status = '07'
--and ap.upload_flag in ('0', '2')
and ap.process_status in ('B', 'C','E') and
ap.SOURCE_RECEIPT_ID = 'HY-009-202510-04';
update t_fuel_invoice_ap_invoice t set t.upload_flag = '0' where
t.SOURCE_RECEIPT_ID = 'HY-009-202510-04';
select f.proxyid,
f.file_name fileName,
f.file_path filePath,
f.state,
f.invoice_id invoiceId,
f.upload_type uploadType
from t_fuel_invoice i, t_fuel_invoice_import_file f
where i.proxyid = f.invoice_id
```

国际账单导⼊：
账单 FTP 信息：

```sql
and f.state =
and f.upload_flag in ('0', '2','3')
and i.ap_invoice_id = '94052';
update t_fuel_invoice_import_file t set t.UPLOAD_FLAG = '0' where t.STATE = '1'
and t.INVOICE_ID in (select proxyid from t_fuel_invoice where ap_invoice_id =
'94071');
select * from t_fuel_invoice WHERE INVOICE_NO in ('0030006257');
select * from t_fuel_invoice_receipt where invoice_no = '6c0b6acd-d4b5-45e4-9548-99a23498995a';
SELECT * FROM T_FUEL_INVOICE_IMPORT_RECORD WHERE FILE_NAME =
'ChinaEasternAirlines_Invoice_0030006257_20240910033126.495.xml';
SELECT * FROM T_FUEL_IMPORT_INVOICE_LINE WHERE XML_ID = '445f0c81-6395-46d0-8af3-11c9bed60dca'
SELECT * FROM T_FUEL_IMPORT_INVOICE WHERE XML_ID = '445f0c81-6395-46d0-8af3-11c9bed60dca'
SELECT * FROM T_FUEL_IMPORT_INVOICE_DETAIL WHERE XML_ID = '445f0c81-6395-46d0-8af3-11c9bed60dca'
select src,
suffix,
company,
sftp_req_host sftpReqHost,
sftp_req_username sftpReqUsername,
sftp_req_password sftpReqPassword,
job_execute_time_start jobExecuteTimeStart,
job_execute_time_end jobExecuteTimeEnd,
sftp_req_host_port sftpReqHostPort,
is_sftp isSftp,
sftp_proxy_host sftpProxyHost,
sftp_src_local sftpSrcLocal,
is_open isOpen
from t_supplier_bill_job_ftphost
```

航班 ID 异常导致的⼤量为推送数据处理：
浦东账单重复处理：

```sql
UPDATE
t_fuel_input t2
SET3
t.SOFLSEQNR = t.AOCID
WHERE
substr(t.FLIGHTDATE, 0, 10) = '2024-11-14'
AND t.AOCID != ' ⽆ data 项 '
AND t.SOFLSEQNR = '0000'
AND t.ssn = 'CNAF'
select qty, amount from T_FUEL_INVOICE t where t.INVOICE_NO in
('24312000000364620261');
select sum(qty), sum(amount) from T_FUEL_INVOICE_RECEIPT t where
t.INVOICE_NO = (select proxyid from T_FUEL_INVOICE t where t.INVOICE_NO =
'24312000000364620261')
select t.RECEIPT_NO, count(1) from T_FUEL_INVOICE_RECEIPT t where
t.INVOICE_NO = (select proxyid from T_FUEL_INVOICE t where t.INVOICE_NO =
'24312000000377337493') GROUP by t.RECEIPT_NO;
DELETE FROM T_FUEL_INVOICE_RECEIPT a
WHERE a.ROWID > (
SELECT MIN(b.ROWID)
FROM T_FUEL_INVOICE_RECEIPT b
WHERE a.RECEIPT_NO = b.RECEIPT_NO and b.INVOICE_NO = (select proxyid from
T_FUEL_INVOICE t where t.INVOICE_NO = '24312000000377337493')
) and a.INVOICE_NO = (select proxyid from T_FUEL_INVOICE t where t.INVOICE_NO =
'24312000000377337493') ;
UPDATE T_FUEL_INVOICE t
SET t.QTY = t.QTY / 2, t.AMOUNT = t.AMOUNT /
WHERE t.INVOICE_NO in ('24312000000364619349',
'24312000000364620261',
'24312000000364629198',
'24312000000364629217',
'24312000000364630816',
'24312000000377328904',
'24312000000377329274',
'24312000000377330247',
'24312000000377337249',
'24312000000377337493');
-- 更新税费
SELECT t.AMOUNT, t.TAX_AMOUNT, t.NO_TAX_AMOUNT from T_FUEL_INVOICE t where
t.INVOICE_NO in ('24312000000364619349',
'24312000000364620261',
'24312000000364629198',
'24312000000364629217',
'24312000000364630816',
'24312000000377328904',
'24312000000377329274',
'24312000000377330247',
'24312000000377337249',
'24312000000377337493');
UPDATE T_FUEL_INVOICE
SET
TAX_AMOUNT = ROUND(AMOUNT - ROUND(AMOUNT / 1.13, 2), 2),
NO_TAX_AMOUNT = ROUND(AMOUNT / 1.13, 2)
where INVOICE_NO in ('24312000000364619349',
'24312000000364620261',
'24312000000364629198',
'24312000000364629217',
'24312000000364630816',
'24312000000377328904',
'24312000000377329274',
'24312000000377330247',
'24312000000377337249',
'24312000000377337493');
-- 更新增值税发票税费
SELECT t.INVOICE_NO , t.INVOICE_AMOUNT, t.TAX_AMOUNT, t.NO_TAX_AMOUNT from
T_TAX_SPECIAL_INVOICE t where t.INVOICE_NO in ('24312000000364619349',
'24312000000364620261',
'24312000000364629198',
'24312000000364629217',
```

共享接⼝的⽇志记录表：
预提核销检查 sql ：
'24312000000364630816',62
'24312000000377328904',63
'24312000000377329274',64
'24312000000377330247',65
'24312000000377337249',66
'24312000000377337493');67

```sql
UPDATE T_TAX_SPECIAL_INVOICE
SET
TAX_AMOUNT = ROUND(INVOICE_AMOUNT - ROUND(INVOICE_AMOUNT / 1.13, 2), 2),
NO_TAX_AMOUNT = ROUND(INVOICE_AMOUNT / 1.13, 2)
where INVOICE_NO in ('24312000000364619349',
'24312000000364620261',
'24312000000364629198',
'24312000000364629217',
'24312000000364630816',
'24312000000377328904',
'24312000000377329274',
'24312000000377330247',
'24312000000377337249',
'24312000000377337493');
AOP_DCS_AP_REQUEST_LOG
select * from T_FULE_INVOICE_RECEIPT_COSTS
where to_char(flight_date,'YYYY/MM/DD')='2024/10/01'; --17304174032
select * from T_AIRPORT t where t.CNAME like '% 釜⼭ %'; -- PUS
SELECT * FROM T_FUEL_INVOICE_RECEIPT_DETAIL d
WHERE  timestamp='1730417403' and d.proxyid in (
select tt.receipt_id from T_FULE_INVOICE_RECEIPT_COSTS tt where
to_char(timestamp)='1730417403'
and  tt.ori_eng='PUS' and tt.type_id = '1'
);
--yuti112
select Q.* from (
SELECT tt.id,d.fuel_amount,d.currency,d.fuel_amount_rmb,dc.company_code,'1' as
type_id FROM T_FULE_INVOICE_RECEIPT_COSTS tt
inner join t_aircraft dc on dc.tail_no = tt.tail_no and tt.flight_date between
dc.apply_date and dc.expire_date
inner join T_FUEL_INVOICE_RECEIPT_DETAIL d on d.proxyid = tt.receipt_id and
d.timestamp = tt.timestamp
inner join t_aircraft ta on ta.tail_no = tt.tail_no and tt.flight_date between
ta.apply_date and ta.expire_date
where to_char(tt.timestamp)='1730417403'
and  tt.ori_eng='PUS' and tt.type_id = '1'
and ta.company_code != 'FM'
union
SELECT tt.id,d1.amount,d1.currencys,d1.fuel_amount_rmb,dc.company_code,'2' as
type_id FROM T_FULE_INVOICE_RECEIPT_COSTS tt
inner join t_aircraft dc on dc.tail_no = tt.tail_no and tt.flight_date between
dc.apply_date and dc.expire_date
inner join T_FLIGHT_FUELINFO_DETAIL d1 on d1.id = tt.refueled_id and
d1.timestamp = tt.timestamp
inner join t_aircraft ta on ta.tail_no = tt.tail_no and tt.flight_date between
ta.apply_date and ta.expire_date
where to_char(tt.timestamp)='1730417403'
and  tt.ori_eng='PUS' and tt.type_id = '2' and ta.company_code != 'FM'
union
SELECT tt.id,d1.amount,d1.currencys,d1.fuel_amount_rmb,dc.company_code,'3' as
type_id FROM T_FULE_INVOICE_RECEIPT_COSTS tt
inner join t_aircraft dc on dc.tail_no = tt.tail_no and tt.flight_date between
dc.apply_date and dc.expire_date
inner join T_TYPE_LINE_DETAIL d1 on d1.id = tt.refueled_id and d1.timestamp =
tt.timestamp
inner join t_aircraft ta on ta.tail_no = tt.tail_no and tt.flight_date between
ta.apply_date and ta.expire_date
where to_char(tt.timestamp)='1730417403'
and  tt.ori_eng='PUS' and tt.type_id = '3' and ta.company_code != 'FM'
)Q
order by Q.id asc;
--hexiao
select
f.receipt_id,f.flight_id,f.receipt_amount,r.currency,f.accrued_amount,w.fuel_amou
nt,w.currency,f.sub_amount,f.writeoff_amount,w.type_id,w.company_code from
t_fuel_invoice_write_off f
inner join t_fuel_invoice_receipt r on r.proxyid = f.receipt_id
inner join t_fuel_invoice fn on fn.proxyid = r.invoice_no
inner join (
SELECT tt.id,d.fuel_amount,d.currency,d.fuel_amount_rmb,'1'as type_id
,ta.company_code FROM T_FULE_INVOICE_RECEIPT_COSTS tt
inner join T_FUEL_INVOICE_RECEIPT_DETAIL d on d.proxyid = tt.receipt_id and
d.timestamp = tt.timestamp
inner join t_aircraft ta on ta.tail_no = tt.tail_no and tt.flight_date between
ta.apply_date and ta.expire_date
where to_char(tt.timestamp)='1730417403'
and  tt.ori_eng='PUS' and tt.type_id = '1'
and ta.company_code != 'FM'
union
SELECT tt.id,d1.amount,d1.currencys,d1.fuel_amount_rmb,'2' as type_id
,ta.company_code FROM T_FULE_INVOICE_RECEIPT_COSTS tt
inner join T_FLIGHT_FUELINFO_DETAIL d1 on d1.id = tt.refueled_id and
d1.timestamp = tt.timestamp
inner join t_aircraft ta on ta.tail_no = tt.tail_no and tt.flight_date between
ta.apply_date and ta.expire_date
where to_char(tt.timestamp)='1730417403'
and  tt.ori_eng='PUS' and tt.type_id = '2' and ta.company_code != 'FM'
union
SELECT tt.id,d1.amount,d1.currencys,d1.fuel_amount_rmb,'3' as type_id
,ta.company_code FROM T_FULE_INVOICE_RECEIPT_COSTS tt
inner join T_TYPE_LINE_DETAIL d1 on d1.id = tt.refueled_id and d1.timestamp =
tt.timestamp
inner join t_aircraft ta on ta.tail_no = tt.tail_no and tt.flight_date between
ta.apply_date and ta.expire_date
where to_char(tt.timestamp)='1730417403'
and  tt.ori_eng='TAE' and tt.type_id = '3' and ta.company_code != 'FM')W on w.id
= f.flight_id
where f.flight_id in (
select tt.id from T_FULE_INVOICE_RECEIPT_COSTS tt where
to_char(timestamp)='1730417403'
and  tt.ori_eng='PUS'
)
and fn.ap_invoice_id is not null
order by f.flight_id asc;
-- 查询有没有  帐单没付款，但是邦定  预提的
--hexiao
select
f.receipt_id,f.flight_id,f.receipt_amount,r.currency,f.accrued_amount,f.sub_amoun
t,f.writeoff_amount from t_fuel_invoice_write_off f
inner join t_fuel_invoice_receipt r on r.proxyid = f.receipt_id
inner join t_fuel_invoice fn on fn.proxyid = r.invoice_no
where  fn.ap_invoice_id is null
and fn.company = ' 江苏 '
```

⽣成 AP ⻚⾯，根据供应商赋值付款公司：
调共享接⼝⽇志表：
年度平账：预提余额账龄报表
审计预提的数据 sql ：

```sql
and r.refueling_date between to_date('2023/01/01','YYYY/MM/DD') and
to_date('2023/12/01','YYYY/MM/DD')  ;
select p.supplier_id supplierId,
p.ou_code ouCode,
p.airport_code airportCode,
p.currency currency,
p.dept_code deptCode,
p.child_dept_code childDeptCode
from t_fuel_supplier_paycompany p;
select proxyid from T_fuel_SUPPLIER t where t.SUPPLIER_NO = '266';
INSERT INTO FOFAS.T_FUEL_SUPPLIER_PAYCOMPANY (supplier_id, ou_code)
VALUES((select proxyid from T_fuel_SUPPLIER t where t.SUPPLIER_NO = '266'),
'101');
AOP_DCS_AP_REQUEST_LOG
update DC_FLIGHT_PLAN set GL_DATE = SYSDATE, IF_MATCH = '1', memo = '24 年⼿⼯平账 '
where id in (
SELECT t.ID FROM DC_FLIGHT_PLAN t INNER JOIN T_AIRCRAFT t1 on t.TAIL_NO =
t1.TAIL_NO and t.FLIGHT_DATE BETWEEN t1.APPLY_DATE and t1.EXPIRE_DATE
INNER join T_COMPANY t2 on t1.COMPANY_CODE = t2.COMPANY_CODE
where t.FLIGHT_DATE BETWEEN TO_DATE('2024-01-01','yyyy-MM-dd') AND TO_DATE('2024-12-31','yyyy-MM-dd')
and t.IF_MATCH = '0' and t2.COMPANY_NAME = ' 上航 '
)
-- 单号、航班号、发票号、公司、机场、单价、数量、⾦额、货币、国内国际、加油⽇期
-- 优化思路：先筛选核⼼表  tt 的数据，再左关联各明细表，避免重复关联
WITH base_tt AS (
-- 第⼀步：先筛选核⼼表  tt 的数据，只查⼀次
SELECT
tt.receipt_id, tt.timestamp, tt.flight_no, tt.flight_type,
tt.flight_date, tt.refueled_id, tt.type_id,
```

dc.company_code  -- 只关联⼀次  t_aircraft ，去掉冗余的  ta 关联8

```sql
FROM T_FULE_INVOICE_RECEIPT_COSTS tt
INNER JOIN t_aircraft dc
ON dc.tail_no = tt.tail_no
AND tt.flight_date BETWEEN dc.apply_date AND dc.expire_date
WHERE
tt.FLIGHT_DATE BETWEEN to_date('2025-12-01','yyyy-MM-dd') AND
to_date('2025-12-31','yyyy-MM-dd')
AND tt.type_id IN ('1','2','3')  -- 合并  type_id 过滤
)
-- 第⼆步：⽤  UNION ALL 合并各明细表数据，基于已筛选的  base_tt
SELECT
```

d.RECEIPT_NO " 单号 ", 19
bt.flight_no " 航班号 ", 20
ti.INVOICE_NO " 发票号 ", 21
bt.company_code " 公司 ", 22
d.REFUELING_AIRPORT " 机场 ", 23
d.UNIT_PRICE " 单价 ", 24
d.QTY " 数量 ", 25
d.AMOUNT " ⾦额 ", 26
d.CURRENCY " 货币 ", 27
bt.flight_type " 国内国际 ", 28
bt.flight_date " 加油⽇期 "29

```sql
FROM base_tt bt
INNER JOIN T_FUEL_INVOICE_RECEIPT_DETAIL d
ON d.proxyid = bt.receipt_id AND d.timestamp = bt.timestamp
INNER JOIN T_FUEL_INVOICE ti
ON ti.proxyid = d.INVOICE_NO
WHERE bt.type_id = '1' AND d.AMOUNT > 4500035
UNION ALL
SELECT
'' " 单号 ",
```

审计提取数据：
bt.flight_no " 航班号 ", 41
'' " 发票号 ", 42
bt.company_code " 公司 ", 43
d1.DEPTAIRPORT " 机场 ", 44
d1.FUEL_PRICE " 单价 ", 45
d1.REFUELED " 数量 ", 46
d1.AMOUNT " ⾦额 ", 47
d1.CURRENCYS " 货币 ", 48
bt.flight_type " 国内国际 ", 49
bt.flight_date " 加油⽇期 "50

```sql
FROM base_tt bt
INNER JOIN T_FLIGHT_FUELINFO_DETAIL d1
ON d1.id = bt.refueled_id AND d1.timestamp = bt.timestamp
WHERE bt.type_id = '2' AND d1.AMOUNT > 4500054
UNION ALL
SELECT
'' " 单号 ",
```

bt.flight_no " 航班号 ", 60
'' " 发票号 ", 61
bt.company_code " 公司 ", 62
d1.ori_eng " 机场 ", 63
d1.FUEL_PRICE " 单价 ", 64
d1.qty_kg " 数量 ", 65
d1.AMOUNT " ⾦额 ", 66
d1.CURRENCYS " 货币 ", 67
bt.flight_type " 国内国际 ", 68
bt.flight_date " 加油⽇期 "69

```sql
FROM base_tt bt
INNER JOIN T_TYPE_LINE_DETAIL d1
ON d1.id = bt.refueled_id AND d1.timestamp = bt.timestamp
WHERE bt.type_id = '3' AND d1.AMOUNT > 45000;
SELECT t.proxyid, t.company, t.invoice_no, t.refueling_date, t.receipt_no,
t.carrier, t.flight_no, t.tail_no, t.actype, t.fuel_name, t.density, t.qty,
t.measure_unit, t.qty_kg, t.unit_price, t.unit_price_unit,t.amount, t.currency,
```

周总要的数据：
t.remark, t.dept_airport, t.stop_airport, t.arri_airport, t.refueling_airport,
t.weight_unit, t.flight_type from T_FUEL_INVOICE_RECEIPT t where

```sql
t.REFUELING_DATE = TO_DATE('20251103', 'yyyyMMdd') and t.FLIGHT_TYPE = 'DOME'
and t.proxyid = '77974214'
union all
SELECT t.proxyid, t.company, t.invoice_no, t.refueling_date, t.receipt_no,
t.carrier, t.flight_no, t.tail_no, t.actype, t.fuel_name, t.density, t.qty,
t.measure_unit, t.qty_kg, t.unit_price, t.unit_price_unit,t.amount, t.currency,
t.remark, t.dept_airport, t.stop_airport, t.arri_airport, t.refueling_airport,
t.weight_unit, t.flight_type from T_FUEL_INVOICE_RECEIPT t where
t.REFUELING_DATE = TO_DATE('20251227', 'yyyyMMdd') and t.FLIGHT_TYPE = 'INTL'
and t.proxyid = 'fd4853eb-3543-41e4-b397-4f55fc374f3d';
SELECT
```

t.REFUELING_AIRPORT 加油站点 ,2

```
CASE
t.RECEIPT_TYPE
```

```
WHEN '5' THEN ' 维修费 '
WHEN '8' THEN ' ⼿⼯标记（其他） '
```

ELSE ' 正常加油单 '7

```sql
END AS 加油单类型 ,
```

to_char(t.REFUELING_DATE, 'yyyyMM') ⽉份 ,9
sum(t.QTY) 加油量 ,10
sum(t.AMOUNT) ⾦额11

```sql
FROM
T_FUEL_INVOICE_RECEIPT t13
WHERE
t.REFUELING_DATE BETWEEN to_date('20251201', 'yyyyMMdd') AND
to_date('20260331', 'yyyyMMdd')
AND t.REFUELING_AIRPORT IN ('XIY', 'SHA')
AND t.TAIL_NO IN (
SELECT
a.TAIL_NO
FROM
t_aircraft a,
T_FUEL_ACTYPE_CONTRAST c
WHERE
a.ac_type = c.oil_ac_type
AND c.OIL_AC_TYPE IN ('332', '333'))
GROUP BY
t.REFUELING_AIRPORT,
CASE
t.RECEIPT_TYPE
WHEN '5' THEN ' 维修费 '
WHEN '8' THEN ' ⼿⼯标记（其他） '
```

ELSE ' 正常加油单 '32

```sql
END,
to_char(t.REFUELING_DATE, 'yyyyMM')
ORDER BY
t.REFUELING_AIRPORT,
to_char(t.REFUELING_DATE, 'yyyyMM');
```

---
## 相关笔记
- [[FOFAS系统迁移]]
- [[视图 V_FULE_INVOICE_RECEIPT_COSTS 的优化]]
- [[近期的SQL脚本]]
- [[数据迁移]]
- [[浦东航油虚拟账单确认_国际账单差额审核]]
- [[备份开账存储过程]]
