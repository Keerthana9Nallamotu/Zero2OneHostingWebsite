from flask import Flask, render_template, session, redirect, url_for, request
from flask_bcrypt import Bcrypt
from datetime import datetime, timedelta
from dateutil import parser
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, exc, text
import sqlalchemy
import os
from flask_session import Session

app = Flask(__name__)

SECRET_KEY = os.urandom(32)
app.config['SECRET_KEY'] = SECRET_KEY

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

bcrypt = Bcrypt(app)



# db = create_engine('mysql+pymysql://root:password@127.0.0.1:3306/zero2onewebsite')

db = create_engine("postgresql://default:n8GrzpUYN5Wi@ep-curly-water-29976642.us-east-1.postgres.vercel-storage.com:5432/verceldb", isolation_level="AUTOCOMMIT")


# session['loggedin'] = False
# session['email_address'] = ""
# session['ATTENDANCE_SUBMITTED'] = False
# session['ASSIGNMENT_SUBMITTED'] = False
# session['ASSIGNMENT_LINK'] = ""

#TODO: REPLACE HARDCODING
WEEK_NUM = 1
CORRECT_WEEKLY_CODE = "Siebel"

@app.route('/', methods = ['GET', 'POST'])
def home():
    # #TODO: REPLACE WITH LISTS
    # session['ATTENDANCE_SUBMITTED'] = False
    # session['ASSIGNMENT_SUBMITTED'] = False

    # session['loggedin'] = False
    return render_template('index.html')

@app.route('/dashboard.html', methods = ['GET', 'POST'])
def dashboard():
    # TODO REDIRECT TO LOGIN IF SESSION = FALSE

    if not session or (session and session.get("email_address")==""):
        # if not session:
        print("Not logged in")
        return redirect(url_for('login'))

    if request.method == 'POST' and 'code' in request.form and 'workshop_num' in request.form:
        code = request.form['code']
        workshop_num = request.form['workshop_num']

        if code != CORRECT_WEEKLY_CODE:
            msg = "Incorrect Code Inputted - Please Try Again"
            #TODO ERROR HANDLING
            return render_template('dashboard.html', msg=msg)
        
        with db.connect() as conn:

            #TODO MAKE WORKSHOP NUMBER A VAR
            update_statement = "UPDATE attendance SET Workshop_1 = :update_num WHERE email_address = :email_address;"
            values = {'update_num': "1", 'email_address': session['email_address']}
            
            print(f"UPDATE: {update_statement}")
            conn.execute(text(update_statement), values)

            session['ATTENDANCE_SUBMITTED'] = True

            return render_template('dashboard.html', msg="", week_num = WEEK_NUM, att_sub = session['ATTENDANCE_SUBMITTED'], assign_sub = session['ASSIGNMENT_SUBMITTED'], assign_link = session['ASSIGNMENT_LINK'])
        
    elif request.method == 'POST' and 'worksheet_link' in request.form:
        worksheet_link = request.form['worksheet_link']
        
        with db.connect() as conn:
            update_statement = "UPDATE assignments SET Workshop_1 = :worksheet_link WHERE email_address = :email_address;"
            values = {'worksheet_link': worksheet_link,'email_address': session['email_address']}
            conn.execute(text(update_statement), values)

            session['ASSIGNMENT_SUBMITTED'] = True
            session['ASSIGNMENT_LINK'] = worksheet_link

            return render_template('dashboard.html', msg="", week_num = WEEK_NUM, att_sub = session['ATTENDANCE_SUBMITTED'], assign_sub = session['ASSIGNMENT_SUBMITTED'], assign_link = session['ASSIGNMENT_LINK'])

    print(session.get("email_address"))
    return render_template('dashboard.html', msg="", week_num = WEEK_NUM, att_sub = session['ATTENDANCE_SUBMITTED'], assign_sub = session['ASSIGNMENT_SUBMITTED'], assign_link = session['ASSIGNMENT_LINK'])

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
             
            select_statement = "SELECT email_address, activation_date, User_password FROM users WHERE email_address = :email_address"
            values = {'email_address': email}

            results = conn.execute(text(select_statement), values)

            for account in results:
                print('DB Results:',account[0])
                print('HASHED: ', str(bcrypt.generate_password_hash(password))[1:])
                if account:
                    print(account)
                    if bcrypt.check_password_hash(account[2], password):
                        print('parse: ', parser.parse(account[1]))

                        session['loggedin'] = True
                        # session['id'] = account['username']
                        session['email_address'] = account[0]

                        #TODO: REPLACE WITH LISTS
                        session['ATTENDANCE_SUBMITTED'] = False
                        session['ASSIGNMENT_SUBMITTED'] = False
                        session['ASSIGNMENT_LINK'] = ""
                        
                        return redirect(url_for('dashboard'))
                else:
                    msg = 'Incorrect username/password!'
                    print(msg)
                    return render_template('login.html', msg=msg)
    else:
        print("Not entering funct")          
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

        print(email)
        print(password)
        print(passwordrep)
        print(firstname)
        print(lastname)
        print(role_type)

        if password!=passwordrep:
            msg = "Passwords don't match!"
            print(f"pass: {password} | passrep: {passwordrep}")
            return render_template('register.html', msg=msg)
        
        print(f"pass: {password} | passrep: {passwordrep}")

        with db.connect() as conn:

            select_statement = "SELECT * FROM users WHERE email_address = :email"
            values1 = {'email': email}
            results = conn.execute(text(select_statement), values1)

            print(results)

            for account in results:
                msg = "Email already registered!"
                return render_template('register.html', msg=msg)

            insert_statement = "INSERT INTO users(email_address, user_password, first_name, last_name, activation_date, role_id, team_id) VALUES (:email_address, :user_password, :first_name, :last_name, :activation_date, :role_id, :team_id)"
            values2 = {'email_address': email, 'user_password': bcrypt.generate_password_hash(password).decode('utf-8'), 'first_name': firstname, 'last_name': lastname, 'activation_date': today_date, 'role_id': role_type, 'team_id': email}

            conn.execute(text(insert_statement).execution_options(autocommit=True), values2)

            insert_statement2 = "INSERT INTO attendance(email_address, Workshop_1, Workshop_2, Workshop_3, Workshop_4, Workshop_5, Workshop_6, Workshop_7, Workshop_8) VALUES (:email_address, :Workshop_1, :Workshop_2, :Workshop_3, :Workshop_4, :Workshop_5, :Workshop_6, :Workshop_7, :Workshop_8)"
            values3 = {'email_address': email, 'Workshop_1': '0', 'Workshop_2': '0', 'Workshop_3': '0', 'Workshop_4': '0', 'Workshop_5': '0', 'Workshop_6': '0', 'Workshop_7': '0', 'Workshop_8': '0'}
            conn.execute(text(insert_statement2).execution_options(autocommit=True), values3)

            insert_statement3 = "INSERT INTO assignments(email_address, Workshop_1, Workshop_2, Workshop_3, Workshop_4, Workshop_5, Workshop_6, Workshop_7, Workshop_8) VALUES (:email_address, :Workshop_1, :Workshop_2, :Workshop_3, :Workshop_4, :Workshop_5, :Workshop_6, :Workshop_7, :Workshop_8)"
            values4 = {'email_address': email, 'Workshop_1': "", 'Workshop_2': "", 'Workshop_3': "", 'Workshop_4': "", 'Workshop_5': "", 'Workshop_6': "", 'Workshop_7': "", 'Workshop_8': ""}
            conn.execute(text(insert_statement3).execution_options(autocommit=True), values4)

            session['loggedin'] = True
            # session['id'] = username
            session['email_address'] = email

            #TODO: REPLACE WITH LISTS
            session['ATTENDANCE_SUBMITTED'] = False
            session['ASSIGNMENT_SUBMITTED'] = False
            session['ASSIGNMENT_LINK'] = ""

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

