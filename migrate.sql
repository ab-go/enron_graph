select * into outfile '/var/lib/mysql-files/employeelist.csv'  fields terminated by ',' optionally enclosed by '"' lines terminated by '\n' from employeelist;
select * into outfile '/var/lib/mysql-files/message.csv'  fields terminated by ',' optionally enclosed by '"' lines terminated by '\n' from message;
select * into outfile '/var/lib/mysql-files/recipientinfo.csv'  fields terminated by ',' optionally enclosed by '"' lines terminated by '\n' from recipientinfo;
select * into outfile '/var/lib/mysql-files/referenceinfo.csv'  fields terminated by ',' optionally enclosed by '"' lines terminated by '\n' from referenceinfo;
