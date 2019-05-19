-- several elements of the data pipeline are being carried out here
-- there are some things mysql is good at

-- fix data
-- clean up spaces and extra  dots in email columns
update employeelist set Email_id = replace(Email_id, ' . ', '.');
update employeelist set Email2 = replace(Email2, ' . ', '.');
update employeelist set Email3 = replace(Email3, ' . ', '.');
update employeelist set Email4 = replace(Email4, ' . ', '.');

update employeelist set Email_id = replace(Email_id, '..', '.');
update employeelist set Email2 = replace(Email2, '..', '.');
update employeelist set Email3 = replace(Email3, '..', '.');
update employeelist set Email4 = replace(Email4, '..', '.');

-- do this for the message sender table as well
update message set sender = replace(sender, '..', '.');

-- and the recipient table
update recipientinfo set rvalue = replace(rvalue, ' . ', '.')
update recipientinfo set rvalue = replace(rvalue, '..', '.');

-- process the pipeline
-- set up new tables and data that will lead to a cleaner model
create table email (address varchar(127) not null);

insert into email (select Email_id from employeelist where Email_id not like '');
insert into email (select Email2 from employeelist where Email2 not like '');
insert into email (select Email3 from employeelist where Email3 not like '');
insert into email (select Email4 from employeelist where Email4 not like '');

insert into email (select sender from message);
insert into email (select rvalue from recipientinfo);

-- create a new table with distinct email ids and employee ids
-- get  a table that is going to give us all the links between the employees and their email addresses
create table email_employee (address varchar(127) unique not null, id int(10) unique primary key auto_increment, eid int(10) default null);
insert into email_employee (select distinct address, null, null from email);

update email_employee
inner join employeelist 
on employeelist.Email_id = email_employee.address
set email_employee.eid = employeelist.eid;

update email_employee
inner join employeelist 
on employeelist.Email2 = email_employee.address
set email_employee.eid = employeelist.eid
where employeelist.Email2 not like '';

update email_employee
inner join employeelist 
on employeelist.Email3 = email_employee.address
set email_employee.eid = employeelist.eid
where employeelist.Email3 not like '';

update email_employee
inner join employeelist 
on employeelist.Email4 = email_employee.address
set email_employee.eid = employeelist.eid
where employeelist.Email4 not like '';

-- process the message and recipient info tables so that we can eliminate the need for exporting two tables and save us a lot of links.

create table message_brief (sender int(10) not null,
			    mid int(10) primary key not null,
			    date datetime,
			    message_id varchar(127),
			    subject text);

insert into message_brief
select ee_m.id, m.mid, m.date, m.message_id, m.subject
from message m
inner join email_employee ee_m on m.sender = ee_m.address;

create table recipientinfo_brief (receiver int(10) not null, 
rid int(10) primary key not null,
mid int(10) not null,
rtype varchar(4) default null
);

insert into recipientinfo_brief
select ee_r.id, r.rid, r.mid, r.rtype
from recipientinfo r
inner join email_employee ee_r on r.rvalue = ee_r.address;

-- merge the two above to form a table that will allow us to create a direct relationship between
-- the sender email and the receiver email id.
-- this means we can shorten the graph considerably by removing all message nodes

create table sent_brief (sender int(10),
mid int(10),
receiver int(10) not null,
date datetime,
message_id varchar(127),
subject text,
rtype varchar(4) default null
);

insert into sent_brief
select m.sender, m.mid, r.receiver, m.date, m.message_id, m.subject, r.rtype 
from recipientinfo_brief r
inner join message_brief m on r.mid = m.mid;

-- just a single link instead of all the links
create table emailed (sender int(10), receiver int(10));
insert into emailed select distinct sender, receiver from sent_brief;

-- export data that can be ingested into neo4j
-- export the employeelist
select 'eid', 'firstName', 'lastName', 'status'
union all
select eid, firstName, lastName, status
from employeelist
into outfile '/var/lib/mysql-files/employees.csv'  fields terminated by ',' optionally enclosed by '"' lines terminated by '\n';

-- export the email_employee table that ties together email ids and employees
select 'id', 'address', 'eid'
union all
select id, address, eid
from email_employee
into outfile '/var/lib/mysql-files/email_employee.csv'  fields terminated by ',' optionally enclosed by '"' lines terminated by '\n';

-- export the message brief table, we might use it
select 'mid', 'sender', 'date', 'message_id', 'subject'
union all
select mid, sender, date, message_id, subject
from message_brief
into outfile '/var/lib/mysql-files/message_brief.csv'  fields terminated by ',' optionally enclosed by '"' lines terminated by '\n';

-- export the recipient_brief table, we might use it
select 'rid', 'mid', 'receiver', 'rtype'
union all
select rid, mid, receiver, rtype
from recipientinfo_brief
into outfile '/var/lib/mysql-files/recipientinfo_brief.csv'  fields terminated by ',' optionally enclosed by '"' lines terminated by '\n';

-- export the sent_brief table, we might use it
select 'mid', 'sender', 'date', 'message_id', 'subject', 'receiver', 'rtype'
union all
select mid, sender, date, message_id, subject, receiver, rtype
from sent_brief
into outfile '/var/lib/mysql-files/sent_brief.csv' fields terminated by ',' optionally enclosed by '"' lines terminated by '\n';


select 'sender', 'receiver'
union all
select sender, receiver
from emailed
into outfile '/var/lib/mysql-files/emailed.csv' fields terminated by ',' optionally enclosed by '"' lines terminated by '\n';

