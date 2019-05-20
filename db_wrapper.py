"""
    Provide a db wrapper to get information from the db.
    This way, we can change our backend without changing the app code.
"""
import os
from neo4j import GraphDatabase as GraphDB, basic_auth

default_password = os.getenv("NEO4J_PASSWORD")
driver = None


def try_and_get(api, *params):
    try:
        result = api(*params)
    except:
        result = None
    finally:
        return result
    
def serialize(_type, result):
    fields = {
        'employee': {'eid', 'firstName', 'lastName', 'status'},
        'email'   : {'address'},
    }

    return {
        k: result[k] for k in fields[_type]
    }

def serialize_node(node):
    n_dict = dict(node.items())
    n_dict['type'] = [x for x in node.labels][0]
    return n_dict

def serialize_relationship(r):
    r_dict = dict(r.items())
    r_dict['TYPE'] = type(r).__name__
    return r_dict

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
            self.is_closed = False

    def _run(self, query, params=None, **kw_params):
        return self._driver.session().run(query, params, **kw_params)

    def __del__(self):
        self.close()

    def close(self):
        if self.is_closed:
            return
        self._driver.close()
        self.is_closed=True

    ## Employee related API
    def get_all_employees(self):
        q = "MATCH (emp: Employee) return emp"
        ret = self._run(q)
        results = [rd['emp'] for rd in ret.data()]
        return [serialize_node(r) for r in results]

    def get_employee(self, _id):
        q = "MATCH (emp:Employee {eid:{id}} ) return emp"
        params = {"id": _id}
        results = self._run(q, params)
        return serialize_node(results.data()[0]['emp'])
    
    def get_employee_by_name(self, firstName, lastName):
        q = "MATCH (emp:Employee {firstName:{firstName}, lastName:{lastName}} ) return emp"
        params = {"firstName": firstName, "lastName":lastName}
        result = self._run(q, params).data()[0]['emp']
        return serialize_node(result)
    
    ## Email Id related APIs
    def get_email_id(self, email_id):
        q = "match(em: EmailId {address:{address}}) return em"
        params = {'address':email_id}
        result = self._run(q, params)
        return serialize_node(result.data()[0]['em'])

    def get_potential_email_id(self, firstName, lastName):
        return '{}.{}@enron.com'.format(firstName.lower(), lastName.lower())

    ## Path tracking
    ## Don't use APOC - the results seem to be weird
    #def get_apoc_path_from_email_to_email(self, fromAddress, emailId):
    #    from_ = try_and_get(self.get_email_id, fromAddress)
    #    if not from_:
    #        raise KeyError("from address: {} not found".format(fromAddress))

    #    to  = try_and_get(self.get_email_id, emailId)
    #    if not to:
    #        raise KeyError("emailId: {} not found".format(emailId))

    #    q = "match (startNode:EmailId {address:{fromAddress}}), (endNode:EmailId {address:{emailId}}) call apoc.algo.dijkstra(startNode, endNode, 'SENT', 'weight') yield path as path, weight as weight return apoc.path.elements(path) limit 1"
    #    params = {'fromAddress': fromAddress, 'emailId':emailId}
    #    results = self._run(q, params)
    #    return [rd for rd in results.data()][0]['apoc.path.elements(path)']

    #def get_apoc_path_from_emp_to_email(self, firstName, lastName, emailId):
    #    ## check to see if the employee exists
    #    emp = try_and_get(self.get_employee_by_name, firstName, lastName)
    #    if not emp:
    #        return self.get_email_path(self.get_potential_email_id(firstName, lastName), emailId)

    #    to  = try_and_get(self.get_email_id, emailId)
    #    if not to:
    #        raise KeyError("emailId: {} not found".format(emailId))

    #    q = "match (startNode:Employee {firstName:{firstName}, lastName:{lastName}}), (endNode:EmailId {address:{emailId}}) call apoc.algo.dijkstra(startNode, endNode, 'HAS|SENT', 'weight') yield path as path return apoc.path.elements(path) limit 1"
    #    params = {'firstName':firstName, 'lastName':lastName, 'emailId':emailId}

    #    results = self._run(q, params)
    #    return [rd for rd in results.data()][0]['apoc.path.elements(path)']
    
    def get_path_from_email_to_email(self, fromAddress, emailId):
        from_ = try_and_get(self.get_email_id, fromAddress)
        if not from_:
            raise KeyError("from address: {} not found".format(fromAddress))

        to  = try_and_get(self.get_email_id, emailId)
        if not to:
            raise KeyError("emailId: {} not found".format(emailId))

        q = "match (startNode:EmailId {address:{fromAddress}}), (endNode:EmailId {address:{emailId}}), p=shortestPath((startNode)-[*..1000]->(endNode)) return p"
        params = {'fromAddress': fromAddress, 'emailId':emailId}
        ret = self._run(q, params)
        g = ret.graph()
        result = []
        for n,r in zip(g.nodes, g.relationships):
            result.append(serialize_node(n))
            result.append(serialize_relationship(r))
        result.append(to)
        return result

    def get_path_from_emp_to_email(self, firstName, lastName, emailId):
        ## check to see if the employee exists
        emp = try_and_get(self.get_employee_by_name, firstName, lastName)
        if not emp:
            return self.get_email_path(self.get_potential_email_id(firstName, lastName), emailId)

        to  = try_and_get(self.get_email_id, emailId)
        if not to:
            raise KeyError("emailId: {} not found".format(emailId))

        q = "match (startNode:Employee {firstName:{firstName}, lastName:{lastName}}), (endNode:EmailId {address:{emailId}}), p=shortestPath((startNode)-[*..1000]->(endNode)) return p"
        params = {'firstName':firstName, 'lastName':lastName, 'emailId':emailId}
        ret = self._run(q, params)
        g = ret.graph()
        result = []
        for n,r in zip(g.nodes, g.relationships):
            result.append(serialize_node(n))
            result.append(serialize_relationship(r))
        result.append(to)
        return result


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

    result = try_and_get(driver.get_email_id, 'tidwellgreer@bfusa.com')
    assert result

    result = try_and_get(driver.get_email_id, 'tidwellgreerzzzz@bfusa.com')
    assert not result
    
    result = try_and_get(driver.get_employee_by_name, 'Roy', 'Armitage')
    assert not result

    result = try_and_get(driver.get_potential_email_id, 'Roy', 'Armitage')
    assert result

    path = driver.get_apoc_path_from_emp_to_email('Lynn', 'Blair', 'fran.fagan@enron.com')
    assert len(path) == 5

    ## this shortens the path by 2
    path = driver.get_path_from_email_to_email(driver.get_potential_email_id('Lynn', 'Blair'), 'fran.fagan@enron.com')
    assert len(path) == 3

    p = driver.get_path_from_emp_to_email('Lynn', 'Blair', 'tidwellgreer@bfusa.com')
    assert len(p) == 9

    ## TODO: this is ugly. see if we can manage this as a context manager
    del driver 



