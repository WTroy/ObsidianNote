---
title: TABLE
source: 有道云笔记
imported: true
related: ["FOFAS系统迁移", "视图 V_FULE_INVOICE_RECEIPT_COSTS 的优化", "近期的SQL脚本", "数据迁移", "浦东航油虚拟账单确认_国际账单差额审核"]
related: ["FOFAS系统迁移", "视图 V_FULE_INVOICE_RECEIPT_COSTS 的优化", "近期的SQL脚本", "数据迁移", "备份开账存储过程"]
---

HSS_AP_VENDORS_ALL: 供应商信息表；还有⼀个相关的表： HSS_AP_VENDOR_SITES_ALL
账单表： T_FUEL_INVOICE
# 供应商信息查询1
-- HSS_AP_VENDORS_ALL1 零时表2
SELECT DISTINCT VENDOR_NUMBER vendor_number, VENDOR_NAME vendor_name3
FROM HSS_AP_VENDOR_SITES_ALL S, HSS_AP_VENDORS_ALL A4
WHERE S.VENDORS_ID = A.VENDOR_ID5
AND S.BUSINESS_TYPE = 108 6
AND A.bank_account_number is not null 7
AND ARCHIVE_FLAG = 0 8
AND A.Supper_Type in('ALL',  'DOME', 'INTL')9
--and vendor_number = 'S032493 10
order by vendor_name;11
12
select * from HSS_AP_VENDORS_ALL1 where vendor_number = 'S063645'; 13
select * from HSS_AP_VENDORS_ALL where vendor_number = 'S063645'; 14
select * from HSS_AP_VENDOR_SITES_ALL1 where VENDORS_ID = '982741'; 15
select * from HSS_AP_VENDOR_SITES_ALL where VENDORS_ID = '982741';16
17
INSERT INTO FOFAS.HSS_AP_VENDORS_ALL (VENDOR_ID, VENDOR_NUMBER, VENDOR_NAME,
TAX_REFERENCE, VENDOR_TYPE, BANK_ACCOUNT_ID, BANK_ACCOUNT_USE_ID,
BANK_ACCOUNT_NUMBER, BANK_ACCOUNT_NAME, BANK_ACCOUNT_DESCRIPTION, CURRENCY_CODE,
BANK_NAME, BANK_CODE, BRANCHES_NAME, SWIFT_CODE, COUNTRY_CODE, PROVINCE, CITY,
BANK_PHONE, BANK_ADDRESS, BANK_POSTAL_CODE, BANK_ZONE_CODE, ACCOUNT_TYPE,
GENERAL_SWIFT_CODE, STREET, BUILDING_NUMBER, DISABLE_DATE, CREATOR, CREATE_TIME,
UPDATER, UPDATE_TIME, PROXYID, ARCHIVE_FLAG, SUPPER_TYPE)
18
select VENDOR_ID, VENDOR_NUMBER, VENDOR_NAME, TAX_REFERENCE, VENDOR_TYPE,
BANK_ACCOUNT_ID, BANK_ACCOUNT_USE_ID, BANK_ACCOUNT_NUMBER, BANK_ACCOUNT_NAME,
BANK_ACCOUNT_DESCRIPTION, CURRENCY_CODE, BANK_NAME, BANK_CODE, BRANCHES_NAME,
SWIFT_CODE, COUNTRY_CODE, PROVINCE, CITY, BANK_PHONE, BANK_ADDRESS,
BANK_POSTAL_CODE, BANK_ZONE_CODE, ACCOUNT_TYPE, GENERAL_SWIFT_CODE, STREET,
BUILDING_NUMBER, DISABLE_DATE, CREATOR, CREATE_TIME, UPDATER, UPDATE_TIME,
PROXYID, '0', 'INTL' from HSS_AP_VENDORS_ALL1
19
where vendor_number = 'S015042' and bank_account_id = '180487';20
21
INSERT INTO FOFAS.HSS_AP_VENDOR_SITES_ALL (PROXYID, VENDORS_ID, VENDOR_SITE_ID,
SITE_NAME, ADDRESS, ADDRESSEE, PHONE, FAX, POSTAL_CODE, DISABLE_DATE,
BUSINESS_TYPE, ORG_CODE, INTERCOMPANY_CODE, CREATOR, CREATE_TIME, UPDATER,
UPDATE_TIME)
22
select PROXYID, VENDORS_ID, VENDOR_SITE_ID, SITE_NAME, ADDRESS, ADDRESSEE, PHONE,
FAX, POSTAL_CODE, DISABLE_DATE, BUSINESS_TYPE, ORG_CODE, INTERCOMPANY_CODE,
CREATOR, CREATE_TIME, UPDATER, UPDATE_TIME from HSS_AP_VENDOR_SITES_ALL1 where
VENDORS_ID = '974643';
23
24

增值税发票表： T_TAX_SPECIAL_INVOICE
select * from t_fuel_invoice WHERE INVOICE_NO in ('10247336');-- 账单信息 1
select * from t_fuel_invoice_receipt where invoice_no = '73429850'; -- 账单明细信息
invoice_no 和 proxyid 关联
2
select * from t_fuel_invoice_surcharge where invoice_no = '73429850';-- 账单附加费信
息   invoice_no 和 proxyid 关联
3
4
SELECT * FROM t_fuel_invoice_ap_invoice where source_receipt_id = 'HY-001-202404-
168';
5
SELECT * FROM t_fuel_invoice_ap_detail where ap_invoice_id = '67769' order by
amount for update;
6
select * from t_fuel_invoice_write_off where ap_invoice_id in ('67769') order by
receipt_amount for update;
7
select * from t_fuel_invoice_write_off where ap_invoice_id in ('67771') and
flight_id in ('7660659') for update;
8
SELECT * FROM DC_FLIGHT_PLAN dfp WHERE dfp.ID IN ('7660659');9
10
SELECT11
af.proxyid,12
af.invoice_no,13
af.invoice_date,14
af.qty,15
af.amount,16
af.station_code,17
af.invoice_type,18
ap.source_receipt_id19
FROM20
t_fuel_invoice af,21
t_fuel_invoice_ap_invoice ap --ap 发票表22
WHERE23
af.ap_invoice_id = ap.proxyid24
AND ap.notice_status = '13'25
AND af.proxyid = '72643856';26
27
-- 传共享的那张表 :28
T_FUEL_INVOICE_AP_INTERFACE29
-- 根据共享接⼝要求，按照公司机型航线汇总的数据30
-- 总⾦额应该是 ap 发票表⾥⾦额⼀样的31
-- ⼀般是航班重复了，导致关联预提的时候重复了32
33

-- 增值税发票查询不到的问题处理：1
-- ⼤概率是有的，但是 invoice_id 和发票表⾥的不⼀致 :2
-- 处理流程：3
-- 发票表⾥真的没有发票或者发票状态是未确认（ is_confirm=0 ），让业务⼈员处理4
-- 检查⾦额是否和账单表⼀致5
-- 确认发票表的 is_confirm 值是不是为 1 6
-- 如果以上都符合，则更新发票表的 invoice_id 和账单表的 proxyid ⼀致7
SELECT t.proxyid as proxyid,8
c.ou_code AS companyCode,9
c.company_name companyName,10
t.supplier as supplierId,11
T.INVOICE_NO AS invoiceNo,12
T.INVOICE_CODE AS invoiceCode,13
T.INVOICE_DATE AS invoiceDate,14
to_char(T.INVOICE_DATE, 'YYYY-MM-DD') AS invoiceDateStr,15
T.INVOICE_AMOUNT AS invoiceAmount,16
T.TAX_AMOUNT AS taxAmount,17
T.TAX_AMOUNT_RATE AS taxAmountRate,18
T.NO_TAX_AMOUNT AS noTaxAmount,19
T.INVOICE_ID as invoiceId20
FROM T_TAX_SPECIAL_INVOICE T ,t_company c21
where 1=1  and t.company_code=c.company_name22
-- and INVOICE_ID = '73588042'23
and invoice_no = '24512000000050006096'24
order by  INVOICE_DATE DESC;25
26
SELECT *27
FROM T_TAX_SPECIAL_INVOICE T28
where 1=129
-- and INVOICE_ID = '73588042'30
and invoice_no = '24112000000095772626'31
order by  INVOICE_DATE DESC;32
33
update T_TAX_SPECIAL_INVOICE SET invoice_id = '74472637' where proxyid = (SELECT
proxyid
34
FROM T_TAX_SPECIAL_INVOICE T35
where invoice_no = '24112000000095772626');36
37
select * from t_fuel_invoice WHERE INVOICE_NO in ('24112000000095772626', ''); --
账单信息
38
39

t_airport ：  场站信息；  Dc_flight_plan 航班计划表
油价表；汇率表
-- 如果增值税发票表⾥没有数据，查⼀下电票接⼝⽇志40
select * from t_sys_interface_outbound where task_number =
'24462000000008762814' order by request_time desc;
41
-- 如果江苏公司还没有接⼊电票系统，需要业务的⽼师⾃⼰⼿⼯确认，⼿⼯上传附件42
-- 如果增票表没数据，发票表是否确认为 1 ，就把发票表⾥这个是否确认改成 0 ，让徐⽼师重新确认43
44
-- 批量处理45
MERGE INTO T_TAX_SPECIAL_INVOICE A46
USING t_fuel_invoice B47
ON (A.INVOICE_NO = B.INVOICE_NO AND A.INVOICE_NO IN ('25317000002182558538'))48
WHEN MATCHED THEN49
UPDATE SET A.invoice_id = B.PROXYID;50
select * from t_airport;1
SELECT a.*, c.R12_TYPE2
FROM t_aircraft a,3
T_FUEL_ACTYPE_CONTRAST c4
WHERE a.ac_type = c.oil_ac_type5
AND a.TAIL_NO in ('B659Z','B658S')6
ORDER BY a.CREATE_TIME;7
8
select * from Dc_flight_plan;9
10
-- 国际油价1
SELECT * FROM t_Fuel_Int_Unit_Price WHERE REFUELING_AIRPORT = 'ICN';2
-- 国内油价3
SELECT * FROM T_FUEL_DOM_UNIT_PRICE ;4
-- 汇率信息5
SELECT * FROM T_EXCHANGE_RATE ;  -- 联系彭磊，管控的6
7
SELECT *8
FROM T_FUEL_DOM_UNIT_PRICE P, T_FUEL_DOM_PRICE_AIRPORT A9

航班留存油量表：
航油供应商表： T_FUEL_SUPPLIER
影像系统上传⽂件：
WHERE P.PROXYID = A.DOM_UNIT_PRICE_ID and to_char(a.apply_date, 'yyyyMMdd') =
'20240801' and p.confirm_status = '0';
10
SELECT1
*2
FROM3
kb_v_flight_fuelinfo i4
WHERE5
to_char(i.flight_bj_date, 'yyyymmdd') = '20240523'6
--and i.flight_no='5357' 7
--and carrier = 'MU'8
AND i.tail_no = 'B6755'9
SELECT * FROM T_DICT_CODE tdc WHERE CODE_NAME in
('serialNumberPath','dmsFileUploadPath');
1
SELECT PROCESS_STATUS , PAY_NOTICE_TYPE  FROM T_FUEL_INVOICE_AP_INVOICE tfiai
WHERE TFIAI.SOURCE_RECEIPT_ID = 'HY-013-202405-05';
2
SELECT * FROM T_FUEL_INVOICE_AP_INVOICE tfiai WHERE TFIAI.SOURCE_RECEIPT_ID in
('HY-013-202405-06','HY-013-202405-07','HY-013-202405-08'
3
,'HY-020-202407-03','HY-020-202407-04','HWHY-020-202407-05'); -- HY-013-202212-054
SELECT * FROM T_FUEL_INVOICE_AP_INVOICE t WHERE TO_CHAR(t.CREATE_TIME  , 'yyyy-
MM-dd') = '2024-05-07';
5
6
select ap.proxyid,7
ap.notice_status noticeStatus,8
ap.source_receipt_id sourceReceiptId,9
ap.pay_scan panScan,10
AP.PROCESS_STATUS processStatus,11
AP.INVOICE_FILE invoiceFile,12
AP.FILE_PATH filePath13
from t_fuel_invoice_ap_invoice ap14
where ap.notice_status = '07'15
and ap.upload_flag in ('0', '2')16
and ap.process_status in ('B', 'C','E') and17

ap.create_time > sysdate - 45;18
19
select f.proxyid,20
f.file_name fileName,21
f.file_path filePath,22
f.state,23
f.invoice_id invoiceId,24
f.upload_type uploadType25
from t_fuel_invoice i, t_fuel_invoice_import_file f26
where i.proxyid = f.invoice_id27
and f.state = 128
--and f.upload_flag in ('0', '2','3')29
and i.ap_invoice_id = '7018';30
31
SELECT * FROM T_SYS_INTERFACE_OUTBOUND WHERE INTERFACE_NAME = ' 影像附件上传接⼝ '
AND TASK_NUMBER IN ('HY-1018-202408-10','HY-1018-202408-11') ORDER BY
REQUEST_TIME DESC ;
32
33
-- 我还可以抢救⼀下 --34
select ap.proxyid,35
ap.notice_status noticeStatus,36
ap.source_receipt_id sourceReceiptId,37
ap.pay_scan panScan,38
AP.PROCESS_STATUS processStatus,39
AP.INVOICE_FILE invoiceFile,40
AP.FILE_PATH filePath41
from t_fuel_invoice_ap_invoice ap42
where ap.notice_status = '07'43
--and ap.upload_flag in ('0', '2')44
and ap.process_status in ('B', 'C','E') and45
ap.SOURCE_RECEIPT_ID = 'HY-009-202510-04';46
47
update t_fuel_invoice_ap_invoice t set t.upload_flag = '0' where
t.SOURCE_RECEIPT_ID = 'HY-009-202510-04';
48
49
select f.proxyid,50
f.file_name fileName,51
f.file_path filePath,52
f.state,53
f.invoice_id invoiceId,54
f.upload_type uploadType55
from t_fuel_invoice i, t_fuel_invoice_import_file f56
where i.proxyid = f.invoice_id57

国际账单导⼊：
账单 FTP 信息：
and f.state = 158
and f.upload_flag in ('0', '2','3')59
and i.ap_invoice_id = '94052';60
61
update t_fuel_invoice_import_file t set t.UPLOAD_FLAG = '0' where t.STATE = '1'
and t.INVOICE_ID in (select proxyid from t_fuel_invoice where ap_invoice_id =
'94071');
62
select * from t_fuel_invoice WHERE INVOICE_NO in ('0030006257');1
select * from t_fuel_invoice_receipt where invoice_no = '6c0b6acd-d4b5-45e4-9548-
99a23498995a';
2
3
SELECT * FROM T_FUEL_INVOICE_IMPORT_RECORD WHERE FILE_NAME =
'ChinaEasternAirlines_Invoice_0030006257_20240910033126.495.xml';
4
SELECT * FROM T_FUEL_IMPORT_INVOICE_LINE WHERE XML_ID = '445f0c81-6395-46d0-8af3-
11c9bed60dca'
5
SELECT * FROM T_FUEL_IMPORT_INVOICE WHERE XML_ID = '445f0c81-6395-46d0-8af3-
11c9bed60dca'
6
SELECT * FROM T_FUEL_IMPORT_INVOICE_DETAIL WHERE XML_ID = '445f0c81-6395-46d0-
8af3-11c9bed60dca'
7
select src,1
suffix,2
company,3
sftp_req_host sftpReqHost,4
sftp_req_username sftpReqUsername,5
sftp_req_password sftpReqPassword,6
job_execute_time_start jobExecuteTimeStart,7
job_execute_time_end jobExecuteTimeEnd,8
sftp_req_host_port sftpReqHostPort,9
is_sftp isSftp,10
sftp_proxy_host sftpProxyHost,11
sftp_src_local sftpSrcLocal,12
is_open isOpen13
from t_supplier_bill_job_ftphost14

航班 ID 异常导致的⼤量为推送数据处理：
浦东账单重复处理：
UPDATE1
t_fuel_input t2
SET3
t.SOFLSEQNR = t.AOCID4
WHERE5
substr(t.FLIGHTDATE, 0, 10) = '2024-11-14'6
AND t.AOCID != ' ⽆ data 项 '7
AND t.SOFLSEQNR = '0000'8
AND t.ssn = 'CNAF'9
select qty, amount from T_FUEL_INVOICE t where t.INVOICE_NO in
('24312000000364620261');
1
2
select sum(qty), sum(amount) from T_FUEL_INVOICE_RECEIPT t where 3
t.INVOICE_NO = (select proxyid from T_FUEL_INVOICE t where t.INVOICE_NO =
'24312000000364620261')
4
5
select t.RECEIPT_NO, count(1) from T_FUEL_INVOICE_RECEIPT t where 6
t.INVOICE_NO = (select proxyid from T_FUEL_INVOICE t where t.INVOICE_NO =
'24312000000377337493') GROUP by t.RECEIPT_NO;
7
8
DELETE FROM T_FUEL_INVOICE_RECEIPT a9
WHERE a.ROWID > (10
SELECT MIN(b.ROWID)11
FROM T_FUEL_INVOICE_RECEIPT b12
WHERE a.RECEIPT_NO = b.RECEIPT_NO and b.INVOICE_NO = (select proxyid from
T_FUEL_INVOICE t where t.INVOICE_NO = '24312000000377337493')
13
) and a.INVOICE_NO = (select proxyid from T_FUEL_INVOICE t where t.INVOICE_NO =
'24312000000377337493') ;
14
15
UPDATE T_FUEL_INVOICE t16
SET t.QTY = t.QTY / 2, t.AMOUNT = t.AMOUNT / 217
WHERE t.INVOICE_NO in ('24312000000364619349',18
'24312000000364620261',19
'24312000000364629198',20

'24312000000364629217',21
'24312000000364630816',22
'24312000000377328904',23
'24312000000377329274',24
'24312000000377330247',25
'24312000000377337249',26
'24312000000377337493');27
28
-- 更新税费29
SELECT t.AMOUNT, t.TAX_AMOUNT, t.NO_TAX_AMOUNT from T_FUEL_INVOICE t where
t.INVOICE_NO in ('24312000000364619349',
30
'24312000000364620261',31
'24312000000364629198',32
'24312000000364629217',33
'24312000000364630816',34
'24312000000377328904',35
'24312000000377329274',36
'24312000000377330247',37
'24312000000377337249',38
'24312000000377337493');39
40
41
UPDATE T_FUEL_INVOICE42
SET 43
TAX_AMOUNT = ROUND(AMOUNT - ROUND(AMOUNT / 1.13, 2), 2),44
NO_TAX_AMOUNT = ROUND(AMOUNT / 1.13, 2)45
where INVOICE_NO in ('24312000000364619349',46
'24312000000364620261',47
'24312000000364629198',48
'24312000000364629217',49
'24312000000364630816',50
'24312000000377328904',51
'24312000000377329274',52
'24312000000377330247',53
'24312000000377337249',54
'24312000000377337493');55
56
-- 更新增值税发票税费57
SELECT t.INVOICE_NO , t.INVOICE_AMOUNT, t.TAX_AMOUNT, t.NO_TAX_AMOUNT from
T_TAX_SPECIAL_INVOICE t where t.INVOICE_NO in ('24312000000364619349',
58
'24312000000364620261',59
'24312000000364629198',60
'24312000000364629217',61

共享接⼝的⽇志记录表：
预提核销检查 sql ：
'24312000000364630816',62
'24312000000377328904',63
'24312000000377329274',64
'24312000000377330247',65
'24312000000377337249',66
'24312000000377337493');67
68
UPDATE T_TAX_SPECIAL_INVOICE69
SET 70
TAX_AMOUNT = ROUND(INVOICE_AMOUNT - ROUND(INVOICE_AMOUNT / 1.13, 2), 2),71
NO_TAX_AMOUNT = ROUND(INVOICE_AMOUNT / 1.13, 2)72
where INVOICE_NO in ('24312000000364619349',73
'24312000000364620261',74
'24312000000364629198',75
'24312000000364629217',76
'24312000000364630816',77
'24312000000377328904',78
'24312000000377329274',79
'24312000000377330247',80
'24312000000377337249',81
'24312000000377337493');82
AOP_DCS_AP_REQUEST_LOG1
select * from T_FULE_INVOICE_RECEIPT_COSTS1
where to_char(flight_date,'YYYY/MM/DD')='2024/10/01'; --17304174032
3
select * from T_AIRPORT t where t.CNAME like '% 釜⼭ %'; -- PUS4
5
SELECT * FROM T_FUEL_INVOICE_RECEIPT_DETAIL d6
WHERE  timestamp='1730417403' and d.proxyid in (7
select tt.receipt_id from T_FULE_INVOICE_RECEIPT_COSTS tt where
to_char(timestamp)='1730417403'
8
and  tt.ori_eng='PUS' and tt.type_id = '1'9
);10

11
--yuti112
select Q.* from (13
SELECT tt.id,d.fuel_amount,d.currency,d.fuel_amount_rmb,dc.company_code,'1' as
type_id FROM T_FULE_INVOICE_RECEIPT_COSTS tt
14
inner join t_aircraft dc on dc.tail_no = tt.tail_no and tt.flight_date between
dc.apply_date and dc.expire_date
15
inner join T_FUEL_INVOICE_RECEIPT_DETAIL d on d.proxyid = tt.receipt_id and
d.timestamp = tt.timestamp
16
inner join t_aircraft ta on ta.tail_no = tt.tail_no and tt.flight_date between
ta.apply_date and ta.expire_date
17
where to_char(tt.timestamp)='1730417403'18
and  tt.ori_eng='PUS' and tt.type_id = '1'19
and ta.company_code != 'FM'20
union21
SELECT tt.id,d1.amount,d1.currencys,d1.fuel_amount_rmb,dc.company_code,'2' as
type_id FROM T_FULE_INVOICE_RECEIPT_COSTS tt
22
inner join t_aircraft dc on dc.tail_no = tt.tail_no and tt.flight_date between
dc.apply_date and dc.expire_date
23
inner join T_FLIGHT_FUELINFO_DETAIL d1 on d1.id = tt.refueled_id and
d1.timestamp = tt.timestamp
24
inner join t_aircraft ta on ta.tail_no = tt.tail_no and tt.flight_date between
ta.apply_date and ta.expire_date
25
where to_char(tt.timestamp)='1730417403'26
and  tt.ori_eng='PUS' and tt.type_id = '2' and ta.company_code != 'FM'27
union28
SELECT tt.id,d1.amount,d1.currencys,d1.fuel_amount_rmb,dc.company_code,'3' as
type_id FROM T_FULE_INVOICE_RECEIPT_COSTS tt
29
inner join t_aircraft dc on dc.tail_no = tt.tail_no and tt.flight_date between
dc.apply_date and dc.expire_date
30
inner join T_TYPE_LINE_DETAIL d1 on d1.id = tt.refueled_id and d1.timestamp =
tt.timestamp
31
inner join t_aircraft ta on ta.tail_no = tt.tail_no and tt.flight_date between
ta.apply_date and ta.expire_date
32
where to_char(tt.timestamp)='1730417403'33
and  tt.ori_eng='PUS' and tt.type_id = '3' and ta.company_code != 'FM'34
)Q35
order by Q.id asc;36
37
--hexiao38
select
f.receipt_id,f.flight_id,f.receipt_amount,r.currency,f.accrued_amount,w.fuel_amou
nt,w.currency,f.sub_amount,f.writeoff_amount,w.type_id,w.company_code from
t_fuel_invoice_write_off f
39
inner join t_fuel_invoice_receipt r on r.proxyid = f.receipt_id40
inner join t_fuel_invoice fn on fn.proxyid = r.invoice_no41

inner join (42
SELECT tt.id,d.fuel_amount,d.currency,d.fuel_amount_rmb,'1'as type_id
,ta.company_code FROM T_FULE_INVOICE_RECEIPT_COSTS tt
43
inner join T_FUEL_INVOICE_RECEIPT_DETAIL d on d.proxyid = tt.receipt_id and
d.timestamp = tt.timestamp
44
inner join t_aircraft ta on ta.tail_no = tt.tail_no and tt.flight_date between
ta.apply_date and ta.expire_date
45
where to_char(tt.timestamp)='1730417403'46
and  tt.ori_eng='PUS' and tt.type_id = '1'47
and ta.company_code != 'FM'48
union49
SELECT tt.id,d1.amount,d1.currencys,d1.fuel_amount_rmb,'2' as type_id
,ta.company_code FROM T_FULE_INVOICE_RECEIPT_COSTS tt
50
inner join T_FLIGHT_FUELINFO_DETAIL d1 on d1.id = tt.refueled_id and
d1.timestamp = tt.timestamp
51
inner join t_aircraft ta on ta.tail_no = tt.tail_no and tt.flight_date between
ta.apply_date and ta.expire_date
52
where to_char(tt.timestamp)='1730417403'53
and  tt.ori_eng='PUS' and tt.type_id = '2' and ta.company_code != 'FM'54
union55
SELECT tt.id,d1.amount,d1.currencys,d1.fuel_amount_rmb,'3' as type_id
,ta.company_code FROM T_FULE_INVOICE_RECEIPT_COSTS tt
56
inner join T_TYPE_LINE_DETAIL d1 on d1.id = tt.refueled_id and d1.timestamp =
tt.timestamp
57
inner join t_aircraft ta on ta.tail_no = tt.tail_no and tt.flight_date between
ta.apply_date and ta.expire_date
58
where to_char(tt.timestamp)='1730417403'59
and  tt.ori_eng='TAE' and tt.type_id = '3' and ta.company_code != 'FM')W on w.id
= f.flight_id
60
where f.flight_id in (61
select tt.id from T_FULE_INVOICE_RECEIPT_COSTS tt where
to_char(timestamp)='1730417403'
62
and  tt.ori_eng='PUS'63
)64
and fn.ap_invoice_id is not null65
order by f.flight_id asc;66
67
-- 查询有没有  帐单没付款，但是邦定  预提的68
--hexiao69
select
f.receipt_id,f.flight_id,f.receipt_amount,r.currency,f.accrued_amount,f.sub_amoun
t,f.writeoff_amount from t_fuel_invoice_write_off f
70
inner join t_fuel_invoice_receipt r on r.proxyid = f.receipt_id71
inner join t_fuel_invoice fn on fn.proxyid = r.invoice_no72
where  fn.ap_invoice_id is null73
and fn.company = ' 江苏 '74

⽣成 AP ⻚⾯，根据供应商赋值付款公司：
调共享接⼝⽇志表：
年度平账：预提余额账龄报表
审计预提的数据 sql ：
and r.refueling_date between to_date('2023/01/01','YYYY/MM/DD') and
to_date('2023/12/01','YYYY/MM/DD')  ;
75
76
select p.supplier_id supplierId,1
p.ou_code ouCode,2
p.airport_code airportCode,3
p.currency currency,4
p.dept_code deptCode,5
p.child_dept_code childDeptCode6
from t_fuel_supplier_paycompany p;7
8
select proxyid from T_fuel_SUPPLIER t where t.SUPPLIER_NO = '266';9
10
INSERT INTO FOFAS.T_FUEL_SUPPLIER_PAYCOMPANY (supplier_id, ou_code) 11
VALUES((select proxyid from T_fuel_SUPPLIER t where t.SUPPLIER_NO = '266'),
'101');
12
AOP_DCS_AP_REQUEST_LOG1
update DC_FLIGHT_PLAN set GL_DATE = SYSDATE, IF_MATCH = '1', memo = '24 年⼿⼯平账 '
where id in (
1
SELECT t.ID FROM DC_FLIGHT_PLAN t INNER JOIN T_AIRCRAFT t1 on t.TAIL_NO =
t1.TAIL_NO and t.FLIGHT_DATE BETWEEN t1.APPLY_DATE and t1.EXPIRE_DATE
2
INNER join T_COMPANY t2 on t1.COMPANY_CODE = t2.COMPANY_CODE3
where t.FLIGHT_DATE BETWEEN TO_DATE('2024-01-01','yyyy-MM-dd') AND TO_DATE('2024-
12-31','yyyy-MM-dd')
4
and t.IF_MATCH = '0' and t2.COMPANY_NAME = ' 上航 '5
)6

-- 单号、航班号、发票号、公司、机场、单价、数量、⾦额、货币、国内国际、加油⽇期1
-- 优化思路：先筛选核⼼表  tt 的数据，再左关联各明细表，避免重复关联2
WITH base_tt AS (3
-- 第⼀步：先筛选核⼼表  tt 的数据，只查⼀次4
SELECT 5
tt.receipt_id, tt.timestamp, tt.flight_no, tt.flight_type, 6
tt.flight_date, tt.refueled_id, tt.type_id,7
dc.company_code  -- 只关联⼀次  t_aircraft ，去掉冗余的  ta 关联8
FROM T_FULE_INVOICE_RECEIPT_COSTS tt9
INNER JOIN t_aircraft dc 10
ON dc.tail_no = tt.tail_no 11
AND tt.flight_date BETWEEN dc.apply_date AND dc.expire_date12
WHERE 13
tt.FLIGHT_DATE BETWEEN to_date('2025-12-01','yyyy-MM-dd') AND
to_date('2025-12-31','yyyy-MM-dd')
14
AND tt.type_id IN ('1','2','3')  -- 合并  type_id 过滤15
)16
-- 第⼆步：⽤  UNION ALL 合并各明细表数据，基于已筛选的  base_tt17
SELECT 18
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
FROM base_tt bt30
INNER JOIN T_FUEL_INVOICE_RECEIPT_DETAIL d 31
ON d.proxyid = bt.receipt_id AND d.timestamp = bt.timestamp32
INNER JOIN T_FUEL_INVOICE ti 33
ON ti.proxyid = d.INVOICE_NO34
WHERE bt.type_id = '1' AND d.AMOUNT > 4500035
36
UNION ALL37
38
SELECT 39
'' " 单号 ", 40

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
FROM base_tt bt51
INNER JOIN T_FLIGHT_FUELINFO_DETAIL d1 52
ON d1.id = bt.refueled_id AND d1.timestamp = bt.timestamp53
WHERE bt.type_id = '2' AND d1.AMOUNT > 4500054
55
UNION ALL56
57
SELECT 58
'' " 单号 ", 59
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
FROM base_tt bt70
INNER JOIN T_TYPE_LINE_DETAIL d1 71
ON d1.id = bt.refueled_id AND d1.timestamp = bt.timestamp72
WHERE bt.type_id = '3' AND d1.AMOUNT > 45000;73
SELECT t.proxyid, t.company, t.invoice_no, t.refueling_date, t.receipt_no,
t.carrier, t.flight_no, t.tail_no, t.actype, t.fuel_name, t.density, t.qty,
t.measure_unit, t.qty_kg, t.unit_price, t.unit_price_unit,t.amount, t.currency,
1

周总要的数据：
t.remark, t.dept_airport, t.stop_airport, t.arri_airport, t.refueling_airport,
t.weight_unit, t.flight_type from T_FUEL_INVOICE_RECEIPT t where
t.REFUELING_DATE = TO_DATE('20251103', 'yyyyMMdd') and t.FLIGHT_TYPE = 'DOME'
and t.proxyid = '77974214'
2
union all 3
SELECT t.proxyid, t.company, t.invoice_no, t.refueling_date, t.receipt_no,
t.carrier, t.flight_no, t.tail_no, t.actype, t.fuel_name, t.density, t.qty,
t.measure_unit, t.qty_kg, t.unit_price, t.unit_price_unit,t.amount, t.currency,
4
t.remark, t.dept_airport, t.stop_airport, t.arri_airport, t.refueling_airport,
t.weight_unit, t.flight_type from T_FUEL_INVOICE_RECEIPT t where
t.REFUELING_DATE = TO_DATE('20251227', 'yyyyMMdd') and t.FLIGHT_TYPE = 'INTL'
and t.proxyid = 'fd4853eb-3543-41e4-b397-4f55fc374f3d';
5
SELECT1
t.REFUELING_AIRPORT 加油站点 ,2
CASE3
t.RECEIPT_TYPE4
WHEN '5' THEN ' 维修费 '5
WHEN '8' THEN ' ⼿⼯标记（其他） '6
ELSE ' 正常加油单 '7
END AS 加油单类型 ,8
to_char(t.REFUELING_DATE, 'yyyyMM') ⽉份 ,9
sum(t.QTY) 加油量 ,10
sum(t.AMOUNT) ⾦额11
FROM12
T_FUEL_INVOICE_RECEIPT t13
WHERE14
t.REFUELING_DATE BETWEEN to_date('20251201', 'yyyyMMdd') AND
to_date('20260331', 'yyyyMMdd')
15
AND t.REFUELING_AIRPORT IN ('XIY', 'SHA')16
AND t.TAIL_NO IN (17
SELECT18
a.TAIL_NO19
FROM20
t_aircraft a,21
T_FUEL_ACTYPE_CONTRAST c22
WHERE23
a.ac_type = c.oil_ac_type24
AND c.OIL_AC_TYPE IN ('332', '333'))25
GROUP BY26
t.REFUELING_AIRPORT,27

CASE28
t.RECEIPT_TYPE29
WHEN '5' THEN ' 维修费 '30
WHEN '8' THEN ' ⼿⼯标记（其他） '31
ELSE ' 正常加油单 '32
END,33
to_char(t.REFUELING_DATE, 'yyyyMM')34
ORDER BY35
t.REFUELING_AIRPORT,36
to_char(t.REFUELING_DATE, 'yyyyMM');37


---
## 相关笔记
- [[FOFAS系统迁移]]
- [[视图 V_FULE_INVOICE_RECEIPT_COSTS 的优化]]
- [[近期的SQL脚本]]
- [[数据迁移]]
- [[备份开账存储过程]]