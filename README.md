# enron_graph
A study of the connections at Enron explored as a graph.

This project

- ingests the data from a mysql dump
- loads the data into a graphdb
- adds an API to query the graphdba


INSTALL
-------

The following steps are required in order to run this project

1. Install MySQL (server and client) if not installed. This can be done using your preferred package manager or docker, if you so prefer.
2. Download the enron-mysqldump_v5.sql file as specified. Untar, gunzip it as necessary based on your source.
3. Create a database enron from this file. On Ubuntu, the command is: sudo mysql enron < enron-mysqldump_v5.sql
4. Examine the tables to see that the data exists and makes sense. At the very least, check that "Lynn Blair" exists in the employeelist table and "tidwellgreer@bfusa.com" exists in the recipientinfo table.
