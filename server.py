from flask import Flask, request, render_template, jsonify
from flask_socketio import SocketIO, emit
import mysql.connector
import smtplib
import db_credentials
import random

server = smtplib.SMTP_SSL("smtp.gmail.com" , 465)
server.login("pratic61@gmail.com" , "unsj eqwo kgok wqvs")

print("SMTP Connected!")

try:

    db = mysql.connector.connect(user = db_credentials.db_username , password = db_credentials.db_password , host = 'localhost' , port = 3306 , database = 'USER_DATA')
    print("Connection to the db is successful")

except Exception as e:
    print(e) 

app = Flask(__name__)
socket = SocketIO(app)

@app.route('/1234link')
def index():
    return render_template('index.html')

@app.route('/1234link/success')
def success():
    return render_template('success.html')

@app.route('/1234link/login')
def login():
    return render_template('login.html')

@app.route('/1234link/signup')
def signup():
    return render_template('signup.html')

@app.route('/1234link/signup_handle' , methods=['POST'])
def signup_handle():
    cursor = db.cursor(buffered = True)

    cursor.execute('select * from USER order by id desc;')
    last_id = cursor.fetchone()

    if last_id == None:
        id = 0
    else:
        id = int(last_id[0]) + 1

    data = request.get_json()
    
    fname = data['first_name']
    lname = data['last_name']
    age = data['age']
    user = data['user_name']
    password = data['password']
    email = data['email']

    try:
        cursor.execute("INSERT INTO USER (id , first_name , last_name , age , user_name , password_u , email) VALUES ('{}' , '{}' , '{}' , '{}' , '{}' , '{}' , '{}');".format(id , fname , lname , age , user , password , email))
        db.commit()
        cursor.close()
        return jsonify(result = True)
    except Exception as e:
        print(e)
        
        if "Duplicate entry" in str(e) and "USER.email" in str(e):
            cursor.close()
            return jsonify(result = "-12")
        elif "Duplicate entry" in str(e) and "USER.user_name" in str(e):
            cursor.close()
            return jsonify(result = "-11")
  
    #print(user_name)
    #print(password)
  
    #return jsonify(result = user_name)

@app.route('/1234link/login_handle' , methods=['POST'])
def login_handle():
    global is_auth_complete
    is_auth_complete = False
    cursor = db.cursor(buffered = True)
   
    data = request.get_json()
    global user_name 
    user = data['user_name']
    password = data['password']

    cursor.execute("select user_name , password_u from USER where user_name = '{}'".format(user))

    password_db = cursor.fetchone()

    if password_db == None:
        cursor.close()
        return jsonify(result = "-1")
    
    elif password_db[1] != password:
        cursor.close()
        return jsonify(result = "-2")
    
    else:
        global code
        user_name = user
        cursor.execute("select email from USER where user_name = '{}'".format(user))
        email = cursor.fetchone()[0]
        #print(email)
        code = random.randint(0 , 9999)

        mssg = "Subject: Authenticate with the OTP\n\nThe OTP is: {}".format(code)

        #print(mssg)

        server.sendmail(from_addr = "pratic61@gmail.com" , to_addrs = email , msg = mssg)
        print("Mail Sent....")
        cursor.close()
        return jsonify(result = user)


    #print(user_name)
    #print(password)
    #return f"{user_name}"

@app.route('/1234link/login_response_handle' , methods=['GET'])
def response_handle():
    if is_auth_complete == True:
    #print(user_name)
        return jsonify(result = user_name)
    else:
        
        return jsonify(result = "-1")

@app.route('/1234link/auth')
def render_auth():
    #print(user_name)
    return render_template('authenticate.html')

@app.route('/1234link/auth_handle' , methods = ['POST'])
def auth_handle():
    inp_code = int(request.get_json()['code'])
    if inp_code == code:
        print(inp_code == code)
        del globals()['code']
        globals()['is_auth_complete'] = True
        return jsonify(result = True)
    else:
        del globals()['code']
        del globals()['user_name']
        return jsonify(result = False)


@app.route('/1234link/logout_handle' , methods=['GET'])
def logout_handle():
    #print(user_name)
    del globals()['is_auth_complete']
    del globals()['user_name']
    return jsonify(result = "")

@app.route('/1234link/chat')
def client_chat():
    #print(user_name)
    #print(is_auth_complete)
    try:
        if user_name and is_auth_complete:
            return render_template('client.html')
        else:
            return render_template("not_logged_in.html")
    except Exception as e:
        return render_template("not_logged_in.html")
    
@app.route('/1234link/old_mssgs_handle' , methods = ['GET'])
def retrieve_old_mssgs():
    cursor = db.cursor()
    cursor.execute("(select * from USER_MSSGS order by id desc LIMIT 1000) order by id asc")

    result = cursor.fetchall()

    if result == []:
        cursor.close()
        return jsonify(result = None)
    else:
        cursor.close()
        return jsonify(result = result)
    
@app.route('/1234link/mssgs_store_handle' , methods = ['POST'])
def store_MSSGS():
    try:
        cursor = db.cursor(buffered = True)
        cursor.execute('select id from USER_MSSGS order by id desc')
        result = cursor.fetchone()
        data = request.get_json()
        if result != None:
            id = int(result[0]) + 1
        else:
            id = 0

        print(data['MSSG'])
        cursor.execute("INSERT INTO USER_MSSGS (id , user_name , message) VALUES ('{}' , '{}' , '{}')".format(id , data['user_name'] , data['MSSG']))
        cursor.close()
        db.commit()
        return jsonify(result = True)
    
    except Exception as e:
        return jsonify(result = False)

@socket.on('connect')
def connect():
    print("[CLIENT CONNECTED]:", request.sid)

@socket.on('disconnect')
def disconn():
    print("[CLIENT DISCONNECTED]:", request.sid)

@socket.on('notify')
def notify(user):
    emit('notify', user, broadcast=True, skip_sid=request.sid)

@socket.on('data')
def emitback(data):
    emit('returndata', data, broadcast=True)

    #print(__name__)

if __name__ == "__main__":
    socket.run(app , host = '0.0.0.0' , debug = True)
    
    

