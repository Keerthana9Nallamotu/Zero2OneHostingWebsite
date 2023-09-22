from flask import Flask, render_template, session, redirect, url_for, request
from datetime import datetime, timedelta
from dateutil import parser
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, exc, text
import sqlalchemy
import os

app = Flask(__name__)


SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY

# # db = create_engine('mysql+pymysql://root:Clever9SQL#Password@127.0.0.1:3306/zero2onewebsite')
db = create_engine("postgresql://default:n8GrzpUYN5Wi@ep-curly-water-29976642.us-east-1.postgres.vercel-storage.com:5432/verceldb")

@app.route('/', methods = ['GET', 'POST'])
def home():
    session['loggedin'] = False
    return render_template('index.html')

@app.route('/dashboard.html', methods = ['GET', 'POST'])
def dashboard():
    return render_template('dashboard.html')

@app.route('/login.html', methods = ['GET', 'POST'])
def login():
    if session and session["loggedin"]:
        return redirect(url_for('dashboard'))
    msg = ''

    today_date = datetime.now()
    print(f"log today's date: {today_date}")

    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:

        email = request.form['email']
        password = request.form['password']

        print('Attempted email: ' + email + ' | Attempted pass: ' + password)

        with db.connect() as conn:
             
            select_statement = "SELECT email_address, activation_date FROM users WHERE email_address = %s AND user_password = %s"
            results = conn.execute(select_statement, (email, password))

            for account in results:
                print('DB Results:',account)
                if account:
                    print('parse: ', parser.parse(account['activation_date']))

                    session['loggedin'] = True
                    # session['id'] = account['username']
                    session['email_address'] = account['email_address']
                       
                    return redirect(url_for('dashboard'))
                else:
                    msg = 'Incorrect username/password!'
                    return render_template('login.html', msg=msg)
                    
    return render_template('login.html', msg=msg)


@app.route('/register.html', methods = ['GET', 'POST'])
def register():
    if session and session["loggedin"]:
        return redirect(url_for('dashboard'))
    
    msg = ''

    today_date = datetime.now()
    print(f"reg today's date: {today_date}")

    if request.method == 'POST' and 'email' in request.form and 'password' in request.form and 'firstname' in request.form and 'lastname' in request.form and 'role' in request.form:

        print("Entered inside conditional")
        email = request.form['email']
        password = request.form['password']
        passwordrep = request.form['password-rep']
        firstname = request.form['firstname']
        lastname = request.form['lastname']
        role_type = request.form['role']

        if password!=passwordrep:
            msg = "Passwords don't match!"
            print(f"pass: {password} | passrep: {passwordrep}")
            return render_template('login.html', msg=msg)
        
        print(f"pass: {password} | passrep: {passwordrep}")

        with db.connect() as conn:

            select_statement = "SELECT * FROM users WHERE email_address = :email"
            values = {'email': email}
            results = conn.execute(text(select_statement), values)

            print(results)

            insert_statement = "INSERT INTO users(email_address, user_password, first_name, last_name, activation_date, role_id, team_id) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            conn.execute(insert_statement, (email, password, firstname, lastname, today_date, role_type, email))

            session['loggedin'] = True
            # session['id'] = username
            session['email_address'] = email
            print(email)
                            
            return redirect(url_for('dashboard'))
                    
    return render_template('register.html', msg='')



@app.route('/our_team.html', methods = ['GET', 'POST'])
def team():
    return render_template('our_team.html')

@app.route('/team_demo.html', methods = ['GET', 'POST'])
def team_demo():
    return render_template('team_demo.html')

@app.route('/software_director.html', methods = ['GET', 'POST'])
def software_director():
    return render_template('software_director.html')

@app.route('/incubator.html', methods = ['GET', 'POST'])
def incubator():
    return render_template('incubator.html')

@app.route('/president.html', methods = ['GET', 'POST'])
def president():
    return render_template('president.html')

@app.route('/vice_president.html', methods = ['GET', 'POST'])
def vice_president():
    return render_template('vice_president.html')

@app.route('/vice_president2.html', methods = ['GET', 'POST'])
def vice_president2():
    return render_template('vice_president2.html')

@app.route('/community_director.html', methods = ['GET', 'POST'])
def community_director():
    return render_template('community_director.html')

@app.route('/outreach_director.html', methods = ['GET', 'POST'])
def outreach_director():
    return render_template('outreach_director.html')

@app.route('/marketing_director.html', methods = ['GET', 'POST'])
def marketing_director():
    return render_template('marketing_director.html')

@app.route('/contact.html', methods = ['GET', 'POST'])
def contact():
    return render_template('contact.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port='5000')





 