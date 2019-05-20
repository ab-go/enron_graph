# enron_graph
A study of the connections at Enron explored as a graph.

This project

- ingests the data from a mysql dump
- loads the data into a graphdb
- adds an API to query the graphdba


PROCESS
-------

The following steps are required in order to run this project

1. Install MySQL (server and client) if not installed. This can be done using your preferred package manager or docker, if you so prefer.

2. Download the enron-mysqldump_v5.sql file as specified. Untar, gunzip it as necessary based on your source.

3. Create a database enron from this file. On Ubuntu, the command is: sudo mysql enron < enron-mysqldump_v5.sql

4. Examine the tables to see that the data exists and makes sense. At the very least, check that "Lynn Blair" exists in the employeelist table and "tidwellgreer@bfusa.com" exists in the recipientinfo table.

5. Export the data to csv files using migrate.sql provided. This creates the csv files in the /var/lib/mysql-files folder.

6. Choose a GraphDBMS that is optimal for our purpose. Looking around at various options here (https://db-engines.com/en/ranking/graph+dbms), Neo4j was selected for this.

7. Install Neo4j if you haven't already.

8. Create a model from the tables in sql format to the model from a GraphDB perspective.

9. Create a migration script that loads the data into Neo4j with the specified model. This is stored in neo_data_model.txt

10. Test that the Neo4j import works.

11. Create a db wrapper that tests whether db access works well. Thus, we can unit test the db access without needing to test the Flask component.

11. Create a REST API to expose this data to the clients. This is done using Flask and the neo4j python driver that talks to the db to get the data.
