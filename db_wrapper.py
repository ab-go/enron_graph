"""
    Provide a db wrapper to get information from the db.
    This way, we can change our backend without changing the app code.
"""
import os
from neo4j import GraphDatabase as GraphDB, basic_auth

default_password = os.getenv("NEO4J_PASSWORD")
driver = None

class DbWrapper:
    """
        class to wrap db access.
    """
    def __init__(self, hostname='localhost', user='neo4j', password='test'):
            ## create a driver to the db
            self._driver = GraphDB.driver(
                                'bolt://{}'.format(hostname),
                                auth=basic_auth(user, password)
                           )

            ## blank out the password
            password=None

    def _run(self, query, params=None, **kw_params):
        """
        """
        return self._driver.session().run(query, params, **kw_params)

    def __del__(self):
        self._driver.close()

    ## Employee related API
    def get_all_employees(self):
        q = "MATCH (emp: Employee) return emp"
        results = self._run(q)
        return [rd['emp'] for rd in results.data()]

    def get_employee(self, _id):
        q = "MATCH (emp:Employee {eid:{id}} ) return emp"
        params = {"id": _id}
        results = self._run(q, params)
        return results.data()[0]['emp']
    
    def get_employee_by_name(self, firstName, lastName):
        q = "MATCH (emp:Employee {firstName:{firstName}, lastName:{lastName}} ) return emp"
        params = {"firstName": firstName, "lastName":lastName}
        return self._run(q, params).data()[0]['emp']
    
    ## Messages related APIs

    ## Recipient related APIs
    def get_all_recipients(self):
        q = "MATCH (rec: Recipient) return rec"
        results = self._run(q)
        return [rd['rec'] for rd in results.data()]

    ## Path tracking
    def get_path_from(self, firstName, lastName, emailId):
        #q = "match (startNode:Employee {firstName:{firstName}}, lastName:{lastName}}), (endNode:Message {id:{mid}}) call apoc.algo.dijkstra(startNode, endNode, 'SENT', 'd') yield path as path, weight as weight return path"
        #params = {'firstName': firstName, 'lastName':lastName, 'mid':mid}
        #q = "match (startNode:Employee {firstName:'Lynn', lastName:'Blair'}), (endNode:Recipient {emailId:'fran.fagan@enron.com'}) call apoc.algo.dijkstra(startNode, endNode, 'SENT|SENT_TO', 'd') yield path as path, weight as weight return path"
        q = "match (startNode:Employee {firstName:{firstName}, lastName:{lastName}}), (endNode:EmailId {address:{emailId}}) call apoc.algo.dijkstra(startNode, endNode, 'HAS|SENT', 'weight') yield path as path return apoc.path.elements(path) limit 1"
        params = {'firstName':firstName, 'lastName':lastName, 'emailId':emailId}
        results = self._run(q, params)
        return [rd for rd in results.data()][0]['apoc.path.elements(path)']

def get_driver(host='localhost', user='neo4j', password=None):
    global driver, default_password
    if driver is None:
        if password is None:
            password = default_password
        driver = DbWrapper(host, user, password)
    return driver

if __name__ == '__main__':
    driver = get_driver()
    result = driver.get_employee(43)
    assert result['firstName'] == 'Larry'
    assert result['lastName'] == 'Campbell'

    result = driver.get_all_employees()
    assert len(result) == 149
    result = driver.get_employee_by_name('Larry', 'Campbell')
    assert result['eid'] == 43

    path = driver.get_path_from('Lynn', 'Blair', 'fran.fagan@enron.com')
    #assert len(path) == 9
    #print(path)

    path = driver.get_path_from('Lynn', 'Blair', 'tidwellgreer@bfusa.com')
    print(len(path), path)

    ## TODO: this is ugly. see if we can manage this as a context manager
    del driver 



