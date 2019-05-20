# enron_graph
A study of the connections at Enron explored as a graph.

This project

- ingests the data from a mysql dump
- loads the data into a graphdb
- adds an API to query the graphd


INSTALLATION PROCESS
-------------------

This project is currently being "docker"-ised. That is, the installation, migration,
et al will all be carried out using docker in the **very near** future. In the meantime,
the following steps are required in order to run this project

1. Install MySQL (server and client) if not installed. This can be done using 
   your preferred package manager or docker, if you so prefer.

2. Download the enron-mysqldump_v5.sql file as specified.
   Untar, gunzip it as necessary based on your source.

3. Create a database enron from this file. 
   On Ubuntu, the command is: sudo mysql enron < enron-mysqldump_v5.sql. 

   You can use your preferred tool/client to do so.

4. Examine the tables to see that the data exists and makes sense. 
   At the very least, check that "Lynn Blair" exists in the employeelist table 
   and "tidwellgreer@bfusa.com" exists in the recipientinfo table.

5. Export the data to csv files using migrate.sql provided. This creates the 
    csv files in the /var/lib/mysql-files folder. This folder depends on the 
   secure_file_priv option in your instance of mysqld. If that option is not the 
   same as /var/lib/mysql-files, you will need to repalce the /var/lib/mysql-files 
   string in migrate.sql folder before running it.

6. Choose a GraphDBMS that is optimal for our purpose. Looking around at various
   options here - (https://db-engines.com/en/ranking/graph+dbms), Neo4j was 
   selected for this.

7. Install Neo4j if you haven't already.

8. Create a model from the tables in sql format to the model from a GraphDB 
   perspective. The model we chose (after some experimenting) had the 
   following types of nodes

   - Employee
   - EmailId

   It has the following types of Relationships

   - HAS:    An employee has EmailIds (One to Many). This is a directed edge.
   - SENT:   An EmailId sent message to another EmailId (Many to Many). 
             Many SENT edges can exist between the same pairs of vertices. 

   NOTE: This model initially had Message nodes and the relationships 
         were 
               EmailId SENT Message (One to Many) and 
               Message RECEIVED_BY EmailId (One to Many). 

         However, since the problem asked for discovering the connections 
         between people, the Message nodes and the RECEIVED_BY edges were removed
         to speed up the search and to keep memory usage low.
         These can be reintroduced if required. 

         Alternatively, additional metadata such as 

            - number of messages
            - first messaged on
            - last messaged on

         can be stored in the SENT edges which keeps the memory footprint low
         but provides potentially important information about the 
         importance of the edge.

9. Create a migration script that loads the data into Neo4j with the specified model.
   This is stored in neo_data_model.txt. Use this, along with the CSV files exported 
   using MySql (Step 5 above), to ingest data into the Neo4j db. Note that Neo4j 
   expects these files to be in the import folder of wherever it is installed/running from.
   Thus, the CSV files will need to be moved/copied there.

10. Install the python modules listed in requirements.txt. This can be done either
    using pip or conda. Please note that the Python version used for this project
    is Python3. You might need to use pip3 for this.

11. Test that the Neo4j import works. There is a db_wrapper.py file in the directory. 
    This can independently test the db access without needing to test the Flask component. 
    Just running the db_wrapper.py using the python interpreter (like so)

    python db_wrapper.py

    on the command line should be fine. It runs the tests when it is invoked as the main script. 
    This was done to keep the project dependencies low at this point. Proper testing using the 
    unittest/nose modules should be done for better guarantees of robustness.

    NOTE: This file needs access to your Neo4j instance's password. It currently gets this via 
    the NEO4J_PASSWORD environment variable. This is neither secure nor desirable in a 
    production system.

12. Create a REST API to expose this data to the clients. This is done using Flask and the neo4j
    python driver that talks to the db to get the data. Running 

    python app.py  

    will start the Flask web server to test this. The port currently in use is 12879, though 
    this can easily be changed.

13. The following queries can be performed on this web server
    a. GET /employees     - Returns all employees
   
    For example, http://localhost:12879/employees
   

    b. GET /employees/<id> - Returns employee with specified EID (if one exists) or returns 404 exception

    For example, http://localhost:12879/employees/143 returns the employee with that EID.
   

    c. GET /path/<firstName>/<lastName>/<emailId> - Returns the path from an employee 
       with the specified first name and last name to the email address specified. It does 
       so as a Node-Edge-(Node-Edge)*-Node that specifies the Node and the Edge leading to the next 
       Node until the final node is reached. 

       Please note that these searches are directional. Thus, it is possible to find a path from Node A to 
       Node B but not one that goes from Node B to Node A. This is because the Edges HAS and SENT (and, in
       the previous/complete model, RECEIVED_BY) are directional.

    For example, http://localhost:12879/path/Lynn/Blair/tidwellgreer@bfusa.com will return a path from 
    Lynn Blair to tidwellgreer@bfusa.com.

    Note: If the Employee table doesn't contain an employee with the specified first name and last name,
    the system tries to look for an email id such as <firstName>.<lastName>@enron.com in order to find a 
    path. Thus, the following query
   
    http://localhost:12879/path/Louis/Soldano/tidwellgreer@bfusa.com will still return a path using this guess.
