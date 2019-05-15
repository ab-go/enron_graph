select 'eid', 'firstName', 'lastName', 'Email_id', 'Email2', 'Email3', 'EMail4', 'folder', 'status'
union all
select eid, firstName, lastName, Email_id, Email2, Email3, EMail4, folder, status
from employeelist
into outfile '/var/lib/mysql-files/employeelist.csv'  fields terminated by ',' optionally enclosed by '"' lines terminated by '\n';

select 'mid', 'sender', 'date', 'message_id', 'subject', 'folder'
union all
select mid, sender, date, message_id, subject, folder
from message
into outfile '/var/lib/mysql-files/message.csv'  fields terminated by ',' optionally enclosed by '"' lines terminated by '\n';

select 'rid', 'mid', 'rtype', 'rvalue', 'dater'
union all
select rid, mid, rtype, rvalue, dater
from recipientinfo
into outfile '/var/lib/mysql-files/recipientinfo.csv'  fields terminated by ',' optionally enclosed by '"' lines terminated by '\n';

select 'rfid', 'mid', 'reference'
union all
select rfid, mid, reference
from referenceinfo
into outfile '/var/lib/mysql-files/referenceinfo.csv'  fields terminated by ',' optionally enclosed by '"' lines terminated by '\n';
