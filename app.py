import os
from json import dumps
from flask import Flask, g, Response, request, abort
from db_wrapper import get_driver

app = Flask(__name__, static_url_path='/html/')

def get_db():
    if not hasattr(g, 'db'):
        g.db = get_driver()
    return g.db

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'db'):
        pass #g.db.close()


@app.route("/employees")
def get_all_employees():
    db = get_db()
    result = db.get_all_employees()
    return Response(
                dumps(
                    [x for x in result]
                ), 
                mimetype="application/json"
           )

@app.route("/employees/<eid>")
def get_employee(eid):
    db = get_db()

    try:
        result = db.get_employee(int(eid))
        return Response(
                dumps(
                    result
                ), 
                mimetype="application/json"
           )
    except:
        abort(404)

@app.route("/path/<firstName>/<lastName>/<emailId>")
def get_path(firstName, lastName, emailId):
    db = get_db()
    try:
        result = db.get_path_from_emp_to_email(firstName, lastName, emailId)
        return Response(
                dumps(
                    result
                ), 
                mimetype="application/json"
           )
    except Exception as e:
        print(e)
        abort(404)


if __name__ == '__main__':
    app.run(port=12879)
