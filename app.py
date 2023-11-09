from flask import Flask, render_template,request,redirect,url_for
import pymysql
import datetime
from flask_mail import Mail, Message

app= Flask(__name__)

# Creating a connection object.
host = '127.0.0.1'
user = 'root'
password = 'admin'
port = 3306
database = 'sys'
# Establishing the connection 
connection = pymysql.connect(host=host, port=port, user=user, password=password, database=database)

# Email server setting configuration
# configuration of mail 
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'kaushikacc2007@gmail.com'
app.config['MAIL_PASSWORD'] = 'myfirstpassword'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app) 
   

@app.route("/")
def home():
    return render_template('index.html')

@app.route("/book",methods = ['GET','POST'])
def book():
    if request.method == 'GET':        
        email_value = request.args.get('email')
        return render_template('book.html',email = email_value)
    if request.method == 'POST':  
        name = request.form['name']
        age = request.form['age']
        gender = request.form['gender']
        phone = request.form['phone']
        email = request.form['email']
        doctor = request.form['doctor']
        date = request.form['date']
        time = request.form['time']
        cursor = connection.cursor()
        cursor.execute(''' INSERT INTO sys.patient_profile VALUES(%s,%s,%s,%s,%s,%s,%s,%s)''',(name,age,gender,phone,email,doctor,date,time))    
        connection.commit()
        #msg = Message(subject="Appointment details",sender = app.config.get("MAIL_USERNAME"), recipients= [email], body= "Your appointment has been booked with doctor "+ doctor + " at "+ date +" "+time)
        #mail.send(msg)
        return render_template('book.html', msg = "Patient booking done successfully. Email sent to your email Id.", email = email)
    

@app.route("/login",methods = ['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    if request.method == 'POST':
        user_type = request.form['user_type']
        user = request.form['email']
        pwd = request.form['pass']
        print("user ",user,'pwd...',pwd)
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM sys.user_info WHERE email = % s AND conf_passwd = % s', (user, pwd, ))   
        account = cursor.fetchone()
        cursor.close()
        print(account)
        if account and account[2] == user and account[3] == pwd: 
            if user_type == 'Doctor':                    
                return redirect(url_for('doctor_dashboard', email = user))
            else:                    
                return redirect(url_for('dashboard', email = user))
        else:
            return render_template('login.html', msg = "Incorrect username / password !")

@app.route("/register",methods = ['GET','POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')
    if request.method == 'POST':
        first = request.form['first']
        last = request.form['last']
        email = request.form['email']
        conpwd = request.form['conpwd']
        print("print values :",first,last,email,conpwd)
        cursor = connection.cursor()
        cursor.execute('SELECT * FROM sys.user_info WHERE email = % s', (email, ))   
        account = cursor.fetchone()
        if account:
            msg = 'Account already exists !'
        else:
            cursor.execute(''' INSERT INTO sys.user_info VALUES(%s,%s,%s,%s)''',(first,last,email,conpwd))    
            connection.commit()
            msg = " User created, please login !"
        cursor.close()    	
        return render_template('register.html', msg = msg)

@app.route("/doctors")
def doctors():
    return render_template('doctors.html')

@app.route("/dashboard")
def dashboard():
    email_value = request.args.get('email')    
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM sys.patient_profile WHERE email = % s', (email_value, ))   	
    if cursor.rowcount == 0:
        cursor.execute('SELECT * FROM sys.user_info WHERE email = % s', (email_value, ))
        result = cursor.fetchone()
        #(patient_name, age, gender, phone_number, email) = (result[0],'None','None','None',result[2])   
        account = (result[0],'None','None','None',result[2])            
    else:
        account = cursor.fetchone()
    cursor.execute('SELECT doctor_name,date,time FROM sys.patient_profile WHERE email = % s AND date < % s', (email_value,datetime.date.today(), ))   
    prev_bookings = cursor.fetchall()
    cursor.execute('SELECT doctor_name,date,time FROM sys.patient_profile WHERE email = % s AND date > % s', (email_value,datetime.date.today(), ))   
    fut_bookings = cursor.fetchall()
    cursor.close()
    print(account)
    if account:    	
        return render_template('dashboard.html', account = account, prev_bookings = prev_bookings, future_bookings = fut_bookings)
    else:
        return render_template('dashboard.html')

@app.route("/doctor_dashboard")
def doctor_dashboard():
    email_value = request.args.get('email')    
    cursor = connection.cursor()    
    cursor.execute('SELECT first_name,last_name FROM sys.user_info WHERE email = % s', (email_value, ))   
    doc_name = cursor.fetchone()
    cursor.execute('SELECT patient_name,date,time FROM sys.patient_profile WHERE doctor_name = % s AND date > % s', (doc_name[0]+' '+doc_name[1],datetime.date.today(), ))   
    fut_bookings = cursor.fetchall()
    cursor.close()
    return render_template('doctor_dashboard.html', future_bookings = fut_bookings)
    
@app.route("/cancel",methods = ['GET','POST'])
def cancel():
    email_value = request.args.get('email')
    cursor = connection.cursor()
    cursor.execute('DELETE FROM sys.patient_profile WHERE email = % s AND date > % s', (email_value,datetime.date(2023, 11, 7), )) 
    connection.commit()
    cursor.close()
    return redirect(url_for('dashboard', email = email_value))

if __name__ == '__main__':
    app.run(debug=True)

