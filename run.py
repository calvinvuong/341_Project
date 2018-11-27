import configparser
from flask import Flask, render_template, request, session
import mysql.connector
import random

# Read configuration from file.
config = configparser.ConfigParser()
config.read('config.ini')

# Set up application server.
app = Flask(__name__)
#set secret key
app.secret_key = 'df934_f8s9f#450sdfcn'

# Create a function for fetching data from the database.
def sql_query(sql):
    db = mysql.connector.connect(**config['mysql.connector'])
    cursor = db.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    cursor.close()
    db.close()
    return result


def sql_execute(sql):
    db = mysql.connector.connect(**config['mysql.connector'])
    cursor = db.cursor()
    cursor.execute(sql)
    db.commit()
    cursor.close()
    db.close()

# For this example you can select a handler function by
# uncommenting one of the @app.route decorators.

#@app.route('/')
def basic_response():
    return "It works!" #example

@app.route('/')
def template_response():
    return render_template('landing.html', name = random.randint(0,4))

@app.route('/register_customer.html', methods=['GET', 'POST'])
def customer_register():
    print(request.form)
    # check no duplicate username
    sql_string = "select username from customer"
    existing_usernames = sql_query(sql_string)

    for a in existing_usernames:
        if request.form["username"] in a[0]:
            # return to landing page, taken username
            return render_template('landing.html', success="Username already taken.");
        
    sql_string = "insert into customer (name, credit_card_num, street_address, city, state, username, password) values ('%s', %s, '%s', '%s', '%s', '%s', '%s')" % (request.form["name"], request.form["credit_card_num"], request.form["street_address"], request.form["city"], request.form["state"], request.form["username"], request.form["password"])

    sql_execute(sql_string)
    return render_template('landing.html', success="Success. Account created.")

@app.route('/register_employee.html', methods=['GET', 'POST'])
def employee_register():
    print(request.form)
    # check no duplicate username
    sql_string = "select username from employee"
    existing_usernames = sql_query(sql_string)

    for a in existing_usernames:
        if request.form["username"] in a[0]:
            # return to landing page, taken username
            return render_template('landing.html', success="Username already taken.")

    sql_string = "insert into employee (name, position, username, password) values ('%s', '%s', '%s', '%s')" %(request.form["name"], request.form["position"], request.form["username"], request.form["password"])

    sql_execute(sql_string)
    return render_template('landing.html', success='Success. Account created.')

@app.route('/login.html', methods=['GET', 'POST'])
def login():
    # validate credentials
    sql_string = "select username from %s where username='%s' and password='%s'" %(request.form["role"], request.form["username"], request.form["password"])
    exists = sql_query(sql_string)
    if len(exists) == 0: #invalid combo
        session.clear()
        return render_template('landing.html', success="Invalid username or password.")
    else:
        session.clear()
        session["username"] = request.form["username"]
        session["role"] = request.form["role"]
        sql_string = "select id, name from %s where username='%s'" %(request.form["role"], request.form["username"])
        name_id = sql_query(sql_string);
        session["id"] = name_id[0][0];
        session["name"] = name_id[0][1];
        
        if request.form["role"] == "customer":
            return render_template('customer_dashboard.html', name=session["name"])#name=request.form["name"])
        elif request.form["role"] == "employee":
            return render_template('employee_dashboard.html', name=session["name"])#name=request.form["name"])

@app.route('/logout.html', methods=['GET', 'POST'])
def logout():
    session.clear()
    return render_template('landing.html', success='Successfully logged out.')
    
#@app.route('/', methods=['GET', 'POST'])
def template_response_with_data():
    print(request.form)
    if "buy-book" in request.form:
        book_id = int(request.form["buy-book"])
        sql = "delete from book where id={book_id}".format(book_id=book_id)
        sql_execute(sql)
    template_data = {}
    sql = "select id, title from book order by title"
    books = sql_query(sql)
    template_data['books'] = books
    return render_template('home-w-data.html', template_data=template_data)

if __name__ == '__main__':
    app.run(**config['app'])
