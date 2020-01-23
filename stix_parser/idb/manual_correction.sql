update PCF set PCF_WIDTH=16 where PCF_NAME="NIX00123";
update PCF set PCF_WIDTH=8 where PCF_NAME="ZZPAD008";
update PCF set PCF_WIDTH=16 where PCF_NAME='ZZPAD016';
update PCF set PCF_WIDTH=24 where PCF_NAME='ZZPAD024';
update PCF set PCF_WIDTH=32 where PCF_NAME='ZZPAD032';
update SW_PARA set SW_DESCR="Pixel 7" where SCOS_NAME='PIX00122';
update SW_PARA set SW_DESCR="Pixel 3" where SCOS_NAME='PIX00123';
update SW_PARA set SW_DESCR="Pixel 11" where SCOS_NAME='PIX00125';
update SW_PARA set SW_DESCR="Pixel 6" where SCOS_NAME='PIX00127';
update SW_PARA set SW_DESCR="Pixel 2" where SCOS_NAME='PIX00130';
update SW_PARA set SW_DESCR="Pixel 10" where SCOS_NAME='PIX00133';
update SW_PARA set SW_DESCR="Pixel 1" where SCOS_NAME='PIX00137';
update SW_PARA set SW_DESCR="Pixel 5" where SCOS_NAME='PIX00140';
update SW_PARA set SW_DESCR="Pixel 9" where SCOS_NAME='PIX00143';
update SW_PARA set SW_DESCR="Pixel 0" where SCOS_NAME='PIX00148';
update SW_PARA set SW_DESCR="Pixel 4" where SCOS_NAME='PIX00151';
update SW_PARA set SW_DESCR="Pixel 8" where SCOS_NAME='PIX00152';
update SW_PARA set SW_DESCR="Guard ring" where SCOS_NAME='PIX00153';


drop table if exists IDB;
create table IDB(
creation_datetime  datetime,
version  varchar(64) not null
);
insert into IDB (creation_datetime, version) values (current_timestamp, '2.26.28');

