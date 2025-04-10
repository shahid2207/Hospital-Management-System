from ast import Param
from flask import Flask,render_template,request,session,redirect,url_for,flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from flask_login import UserMixin
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import login_user,logout_user,login_manager,LoginManager
from flask_login import login_required,current_user
from flask_mail import Mail
import json



local_server= True
app = Flask(__name__)
app.secret_key='mayank'


# this is for getting unique user access
login_manager=LoginManager(app)
login_manager.login_view='login'

# SMTP MAIL SERVER SETTINGS

app.config.update(
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT='465',
    MAIL_USE_SSL=True,
    MAIL_USERNAME="sayhamali4@gmail.com",
    MAIL_PASSWORD="jfhwzsxjnxdbbbkg"
)
mail = Mail(app)


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))



app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:9615@localhost/hmdbms'

db=SQLAlchemy(app)



class Test(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    name=db.Column(db.String(100))
    email=db.Column(db.String(100))

class User(UserMixin,db.Model):
    id=db.Column(db.Integer,primary_key=True)
    username=db.Column(db.String(50))
    usertype=db.Column(db.String(50))
    email=db.Column(db.String(50),unique=True)
    password=db.Column(db.String(1000))

class Patients(db.Model):
    pid=db.Column(db.Integer,primary_key=True)
    email=db.Column(db.String(50))
    name=db.Column(db.String(50))
    gender=db.Column(db.String(50))
    slot=db.Column(db.String(50))
    disease=db.Column(db.String(50))
    time=db.Column(db.String(50),nullable=False)
    date=db.Column(db.String(50),nullable=False)
    dept=db.Column(db.String(50))
    number=db.Column(db.String(50))

class Doctors(db.Model):
    did=db.Column(db.Integer,primary_key=True)
    email=db.Column(db.String(50))
    doctorname=db.Column(db.String(50))
    dept=db.Column(db.String(50))

class Trigr(db.Model):
    tid=db.Column(db.Integer,primary_key=True)
    pid=db.Column(db.Integer)
    email=db.Column(db.String(50))
    name=db.Column(db.String(50))
    action=db.Column(db.String(50))
    timestamp=db.Column(db.String(50))





@app.route('/')
def index():
    return render_template('index.html')
    



@app.route('/doctors', methods=['POST', 'GET'])
def doctors():
    if request.method == "POST":
        email = request.form.get('email')
        doctorname = request.form.get('doctorname')
        dept = request.form.get('dept')

        # Using parameterized SQL to avoid SQL injection
        sql = text("INSERT INTO doctors (email, doctorname, dept) VALUES (:email, :doctorname, :dept)")
        db.session.execute(sql, {
            'email': email,
            'doctorname': doctorname,
            'dept': dept
        })
        db.session.commit()

        flash("Information is Stored", "primary")

    return render_template('doctor.html')



@app.route('/patients', methods=['POST', 'GET'])
@login_required
def patient():
    # Get doctor list using session
    doct = db.session.execute(text("SELECT * FROM doctors")).fetchall()

    if request.method == "POST":
        email = request.form.get('email')
        name = request.form.get('name')
        gender = request.form.get('gender')
        slot = request.form.get('slot')
        disease = request.form.get('disease')
        time = request.form.get('time')
        date = request.form.get('date')
        dept = request.form.get('dept')
        number = request.form.get('number')
        subject = "HOSPITAL MANAGEMENT SYSTEM"

        # Insert patient using SQLAlchemy 2.0 syntax
        sql = text("INSERT INTO patients (email, name, gender, slot, disease, time, date, dept, number) VALUES (:email, :name, :gender, :slot, :disease, :time, :date, :dept, :number)")
        db.session.execute(sql, {
            "email": email,
            "name": name,
            "gender": gender,
            "slot": slot,
            "disease": disease,
            "time": time,
            "date": date,
            "dept": dept,
            "number": number
        })
        db.session.commit()

        mail.send_message(subject,
                          sender=app.config['MAIL_USERNAME'],
                          recipients=[email],
                          body=f"YOUR BOOKING IS CONFIRMED.\n\nDetails:\nName: {name}\nSlot: {slot}")

        flash("Booking Confirmed", "info")

    return render_template('patient.html', doct=doct)


@app.route('/bookings')
@login_required
def bookings(): 
    em = current_user.email
    if current_user.usertype == "Doctor":
        query = db.session.execute(text("SELECT * FROM patients")).fetchall()
    else:
        query = db.session.execute(text("SELECT * FROM patients WHERE email = :email"), {"email": em}).fetchall()

    return render_template('booking.html', query=query)
    

@app.route("/edit/<string:pid>", methods=['POST', 'GET'])
@login_required
def edit(pid):
    posts = Patients.query.filter_by(pid=pid).first()

    if request.method == "POST":
        email = request.form.get('email')
        name = request.form.get('name')
        gender = request.form.get('gender')
        slot = request.form.get('slot')
        disease = request.form.get('disease')
        time = request.form.get('time')
        date = request.form.get('date')
        dept = request.form.get('dept')
        number = request.form.get('number')

        sql = text("""UPDATE patients SET email = :email, name = :name, gender = :gender, slot = :slot,
                      disease = :disease, time = :time, date = :date, dept = :dept, number = :number 
                      WHERE pid = :pid""")

        db.session.execute(sql, {
            "email": email,
            "name": name,
            "gender": gender,
            "slot": slot,
            "disease": disease,
            "time": time,
            "date": date,
            "dept": dept,
            "number": number,
            "pid": pid
        })
        db.session.commit()
        flash("Slot Updated", "success")
        return redirect('/bookings')
    
    return render_template('edit.html', posts=posts)



@app.route("/delete/<string:pid>", methods=['POST', 'GET'])
@login_required
def delete(pid):
    sql = text("DELETE FROM patients WHERE pid = :pid")
    db.session.execute(sql, {'pid': pid})
    db.session.commit()

    flash("Slot Deleted Successfully", "danger")
    return redirect('/bookings')






@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == "POST":
        username = request.form.get('username')
        usertype = request.form.get('usertype')
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            flash("Email Already Exists", "warning")
            return render_template('signup.html')

        encpassword = generate_password_hash(password)

        # Correct SQLAlchemy 2.0+ approach using db.session.execute
        sql = text("INSERT INTO user (username, usertype, email, password) VALUES (:username, :usertype, :email, :password)")
        db.session.execute(sql, {
            "username": username,
            "usertype": usertype,
            "email": email,
            "password": encpassword
        })
        db.session.commit()

        flash("Signup Success. Please Login", "success")
        return render_template('login.html')

    return render_template('signup.html')

@app.route('/login',methods=['POST','GET'])
def login():
    if request.method == "POST":
        email=request.form.get('email')
        password=request.form.get('password')
        user=User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password,password):
            login_user(user)
            flash("Login Success","primary")
            return redirect(url_for('index'))
        else:
            flash("invalid credentials","danger")
            return render_template('login.html')    





    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logout SuccessFul","warning")
    return redirect(url_for('login'))



@app.route('/test')
def test():
    try:
        Test.query.all()
        return 'My database is Connected'
    except Exception as e:
        return f'My db is not Connected: {str(e)}'
    

@app.route('/details')
@login_required
def details():
    sql = text("SELECT * FROM trigr")
    posts = db.session.execute(sql).fetchall()
    return render_template('trigers.html', posts=posts)

@app.route('/search', methods=['POST', 'GET'])
@login_required
def search():
    if request.method == "POST":
        query_text = request.form.get('search')

        # Search for a doctor by name or department
        doctor = Doctors.query.filter(
            (Doctors.dept.ilike(f'%{query_text}%')) | 
            (Doctors.doctorname.ilike(f'%{query_text}%'))
        ).first()

        if doctor:
            flash("Doctor is Available", "info")
        else:
            flash("Doctor is Not Available", "danger")

    return render_template('index.html')





app.run(debug=True)    

