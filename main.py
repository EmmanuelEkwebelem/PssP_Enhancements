from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, abort, session
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import os
import datetime
import uuid

load_dotenv()

db = SQLAlchemy()
app = Flask(__name__)

mysql_username = os.getenv("MYSQL_USERNAME")
mysql_password = os.getenv("MYSQL_PASSWORD")
mysql_host = os.getenv("MYSQL_HOST")

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqldb://' + mysql_username + ':' + mysql_password + '@' + mysql_host + ':3306/patient_portal'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'sdf#$#dfjkhdf0SDJH0df9fd98343fdfu34rf'
db.init_app(app)

class Users(db.Model):
    __tablename__ = 'production_accounts'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    account_type = db.Column(db.String(80), nullable=False)
    mrn = db.Column(db.String(80), unique=True, nullable=False)
    date_created = db.Column(db.DateTime, default=db.func.current_timestamp())
    last_login = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    def __init__(self, username, password, email, account_type, mrn, date_created, last_login):
        self.username = username
        self.password = password
        self.email = email
        self.account_type = account_type
        self.mrn = mrn
        self.date_created = date_created
        self.last_login = last_login
    def to_json(self):
        return {
            'id': self.id,
            'username': self.username,
            'password': self.password,
            'email': self.email,
            'account_type': self.account_type,
            'mrn': self.mrn,
            'date_created': self.date_created,
            'last_login': self.last_login
        }

class Patients(db.Model):
    __tablename__ = 'production_patients'
    id = db.Column(db.Integer, primary_key=True)
    mrn = db.Column(db.String(255))
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    zip_code = db.Column(db.String(255), nullable=True)
    gender = db.Column(db.String(255), nullable=True)
    dob = db.Column(db.String(255), nullable=True)
    gender = db.Column(db.String(255), nullable=True)
    race = db.Column(db.String(255))
    insurance_type = db.Column(db.String(255), nullable=True)
    contact_mobile = db.Column(db.String(255), nullable=True)
    def __init__(self, mrn, first_name, last_name, zip_code, gender, dob, race, insurance_type, contact_mobile):
        self.mrn = mrn
        self.first_name = first_name
        self.last_name = last_name
        self.zip_code = zip_code
        self.gender = gender
        self.dob = dob
        self.race = race
        self.insurance_type = insurance_type
        self.contact_mobile = contact_mobile
    def to_json(self):
        return {
            'id': self.id,
            'mrn': self.mrn,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'zip_code': self.zip_code,
            'gender': self.gender,
            'dob': self.dob,
            'race': self.race,
            'insurance_type': self.insurance_type,
            'contact_mobile': self.contact_mobile, 
        }

class Conditions_patient(db.Model):
    __tablename__ = 'production_patient_conditions'
    id = db.Column(db.Integer, primary_key=True)
    mrn = db.Column(db.String(255), db.ForeignKey('production_patients.mrn'))
    icd10_code = db.Column(db.String(255), db.ForeignKey('production_conditions.icd10_code'))
    def __init__(self, mrn, icd10_code):
        self.mrn = mrn
        self.icd10_code = icd10_code
    def to_json(self):
        return {
            'id': self.id,
            'mrn': self.mrn,
            'icd10_code': self.icd10_code
        }

class Conditions(db.Model):
    __tablename__ = 'production_conditions'

    id = db.Column(db.Integer, primary_key=True)
    icd10_code = db.Column(db.String(255))
    icd10_description = db.Column(db.String(255))

    def __init__(self, icd10_code, icd10_description):
        self.icd10_code = icd10_code
        self.icd10_description = icd10_description

    def to_json(self):
        return {
            'id': self.id,
            'icd10_code': self.icd10_code,
            'icd10_description': self.icd10_description
        }

class Medications_patient(db.Model):
    __tablename__ = 'production_patient_medications'
    id = db.Column(db.Integer, primary_key=True)
    mrn = db.Column(db.String(255), db.ForeignKey('production_patients.mrn'))
    med_ndc = db.Column(db.String(255), db.ForeignKey('production_medications.med_ndc'))
    def __init__(self, mrn, med_ndc):
        self.mrn = mrn
        self.med_ndc = med_ndc
    def to_json(self):
        return {
            'id': self.id,
            'mrn': self.mrn,
            'med_ndc': self.med_ndc
        }
    
class Medications(db.Model):
    __tablename__ = 'production_medications'
    id = db.Column(db.Integer, primary_key=True)
    med_ndc = db.Column(db.String(255))
    med_human_name = db.Column(db.String(255))
    def __init__(self, med_ndc, med_human_name):
        self.med_ndc = med_ndc
        self.med_human_name = med_human_name
    def to_json(self):
        return {
            'id': self.id,
            'med_ndc': self.med_ndc,
            'med_human_name': self.med_human_name
        }

@app.route('/')
def index():
    return render_template('landing.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        username = request.form['username']
        password = request.form['password']
        account = Users.query.filter_by(username=username, password=password).first()
        if account:
            session['loggedin'] = True
            session['id'] = account.id
            session['mrn'] = account.mrn
            session['username'] = account.username
            session['account_type'] = account.account_type
            msg = 'Logged in successfully !'
            account.last_login = datetime.datetime.now()
            db.session.commit()
            if session['account_type'] == 'admin':
                return redirect(url_for('get_gui_patients'))
            elif session['account_type'] == 'patient':
                return redirect(url_for('get_patient_details', mrn=session['mrn']))
            elif session['account_type'] == 'careprovider':
                return redirect(url_for('get_gui_patients'))
        else:
            msg = 'Incorrect username / password !'
    return render_template('/login.html', msg = msg)

@app.route('/register', methods=['GET', 'POST'])
def register():
    msg = ''
    if request.method == 'POST' and 'account_type' in request.form:
        if request.form['account_type'] == 'admin':
            return redirect(url_for('register_admin'))
        elif request.form['account_type'] == 'patient':
            return redirect(url_for('register_patient'))
        elif request.form['account_type'] == 'careprovider':
            return redirect(url_for('register_provider'))
    elif request.method == 'POST':
        msg = 'Please fill out the form!'
    return render_template('register.html', msg=msg)

@app.route('/register/admin', methods=['GET', 'POST'])
def register_admin():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        account_type = 'admin'
        mrn = None
        account = Users.query.filter_by(email=email).first()
        if account:
            msg = 'Account already exists! Please log in'   
        else:
            datecreated = datetime.datetime.now()
            lastlogin = datetime.datetime.now()
            new_user = Users(username, password, email, account_type, mrn, datecreated, lastlogin)
            db.session.add(new_user)
            db.session.commit()
            msg = "You have successfully registered a ADMIN account!"
    elif request.method == 'POST':
        msg = 'Please fill out the form!'
    return render_template('register_admin.html', msg=msg)

@app.route('/register/provider', methods=['GET', 'POST'])
def register_provider():
    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        account_type = 'careprovider'
        mrn = None
        account = Users.query.filter_by(email=email).first()
        if account:
            msg = 'Account already exists! Please log in'   
        else:
            datecreated = datetime.datetime.now()
            lastlogin = datetime.datetime.now()
            new_user = Users(username, password, email, account_type, mrn, datecreated, lastlogin)
            db.session.add(new_user)
            db.session.commit()
            msg = "You have successfully registered a CARE PROVIDER account!"
    elif request.method == 'POST':
        msg = 'Please fill out the form!'
    return render_template('register_provider.html', msg=msg)

@app.route('/register/patient', methods=['GET', 'POST'])
def register_patient():

    db_conditions = Conditions.query.all()
    db_medications = Medications.query.all()

    print('count of conditions loaded: ', len(db_conditions))
    print('count of medications loaded: ', len(db_medications))

    msg = ''
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        
        mrn = str(uuid.uuid4())[:8]
        account_type = 'patient'

        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        first_name = request.form['first_name']
        last_name = request.form['last_name']
        zip_code = request.form['zip_code']
        dob = request.form['dob']
        gender = request.form['gender']
        contact_mobile = request.form['contact_mobile']
        contact_home = request.form['contact_home']

        pt_conditions = request.form.getlist('conditions')
        print('pt_conditions: ', pt_conditions)

        account = Users.query.filter_by(email=email).first()
        patient = Patients.query.filter_by(contact_mobile=contact_mobile).first()
        if account or patient:
            msg = 'Account already exists! Please log in'   
        else:
            datecreated = datetime.datetime.now()
            lastlogin = datetime.datetime.now()
            
            new_user = Users(username, password, email, account_type, mrn, datecreated, lastlogin)
            new_patient = Patients(mrn, first_name, last_name, zip_code, dob, gender, contact_mobile, contact_home)

            db.session.add(new_user)
            db.session.commit()
            db.session.add(new_patient)
            db.session.commit()

            for condition in pt_conditions:
                new_patient_condition = Conditions_patient(mrn, condition)
                db.session.add(new_patient_condition)
                db.session.commit()

            msg = 'You have successfully registered a PATIENT account !'
    elif request.method == 'POST':
        msg = 'Please fill out the form!'
    return render_template('register_patient.html', msg=msg, conditions=db_conditions, medications=db_medications)

@app.route('/account')
def account():
    if 'loggedin' in session:
        account = Users.query.filter_by(id=session['id']).first()
        print('Account details: ', account.to_json())
        return render_template('account.html', account=account)
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   return redirect(url_for('login'))

@app.route('/patients', methods=['GET'])
def get_gui_patients():
    if 'loggedin' in session and session['account_type'] == 'admin':
        returned_Patients = Patients.query.all() 
        return render_template("patient_all.html", patients = returned_Patients)
    elif 'loggedin' in session and session['account_type'] == 'careprovider':
        returned_Patients = Patients.query.all()
        return render_template("patient_all.html", patients = returned_Patients)
    else:
        return redirect(url_for('get_patient_details', mrn=session['mrn']))

@app.route('/insert', methods = ['POST'])
def insert(): 
    if request.method == 'POST':
        mrn = request.form['mrn']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        gender = request.form['gender']
        zip_code = request.form['zip_code']
        new_patient = Patients(mrn, first_name, last_name, gender, zip_code)
        db.session.add(new_patient)
        db.session.commit()
        flash("Patient Inserted Successfully")
        return redirect(url_for('get_gui_patients'))
    else:
        flash("Something went wrong")
        return redirect(url_for('get_gui_patients'))

@app.route('/update', methods = ['GET', 'POST'])
def update(): 
    if request.method == 'POST':
        form_mrn = request.form.get('mrn')
        patient = Patients.query.filter_by(mrn=form_mrn).first()
        patient.first_name = request.form.get('first_name')
        patient.last_name = request.form.get('last_name')
        patient.gender = request.form.get('gender')
        db.session.commit()
        flash("Patient Updated Successfully")
        return redirect(url_for('get_gui_patients'))

@app.route('/delete/<string:mrn>', methods = ['GET', 'POST'])
def delete(mrn): 
    patient = Patients.query.filter_by(mrn=mrn).first()
    print('Found patient: ', patient)
    db.session.delete(patient)
    db.session.commit()
    flash("Patient Deleted Successfully")
    return redirect(url_for('get_gui_patients'))

@app.route('/details/<string:mrn>', methods = ['GET'])
def get_patient_details(mrn):
    patient_details = Patients.query.filter_by(mrn=mrn).first()
    patient_conditions = Conditions_patient.query.filter_by(mrn=mrn).all()
    patient_medications = Medications_patient.query.filter_by(mrn=mrn).all()
    db_conditions = Conditions.query.all()
    db_medications = Medications.query.all()
    print('Number of conditions total loaded: ', len(db_conditions))
    print('Number of medications total loaded: ', len(db_medications))
    return render_template("patient_details.html", patient_details = patient_details, 
        patient_conditions = patient_conditions, patient_medications = patient_medications,
        db_conditions = db_conditions, db_medications = db_medications)

@app.route('/update_conditions', methods = ['GET', 'POST'])
def update_conditions(): 
    if request.method == 'POST':
        form_id = request.form.get('id')
        print('form_id', form_id)
        form_icd10_code = request.form.get('icd10_code')
        print('form_icd10_code', form_icd10_code)
        patient_condition = Conditions_patient.query.filter_by(id=form_id).first()
        print('patient_condition', patient_condition)
        patient_condition.icd10_code = request.form.get('icd10_code')
        db.session.commit()
        flash("Patient Condition Updated Successfully")
        return redirect(url_for('get_patient_details', mrn=patient_condition.mrn))

@app.route('/add_condition', methods = ['GET', 'POST'])
def add_condition(): 
    if request.method == 'POST':
        form_mrn = request.form.get('mrn')
        print('form_mrn', form_mrn)
        form_icd10_code = request.form.get('icd10_code')
        print('form_icd10_code', form_icd10_code)
        new_condition = Conditions_patient(form_mrn, form_icd10_code)
        db.session.add(new_condition)
        db.session.commit()
        flash("Patient Condition Added Successfully")
        return redirect(url_for('get_patient_details', mrn=form_mrn))

@app.route('/delete_condition', methods = ['GET', 'POST'])
def delete_condition():
    if request.method == 'POST':
        form_mrn = request.form.get('mrn')
        form_icd10_code = request.form.get('icd10_code')
        print('form_id', form_mrn)
        print('form_icd10_code', form_icd10_code)
        patient_condition = Conditions_patient.query.filter_by(mrn=form_mrn, icd10_code=form_icd10_code).all()
        print('Found conditions: ', patient_condition)
        for condition in patient_condition:
            db.session.delete(condition)
        db.session.commit()
        flash("Patient Condition Deleted Successfully")
        return redirect(url_for('get_patient_details', mrn=form_mrn))

@app.route('/add_medication', methods = ['GET', 'POST'])
def add_medication(): 
    if request.method == 'POST':
        form_mrn = request.form.get('mrn')
        print('form_mrn', form_mrn)
        form_ndc_code = request.form.get('med_ndc')
        print('form_ndc_code', form_ndc_code)
        new_medication = Medications_patient(form_mrn, form_ndc_code)
        db.session.add(new_medication)
        db.session.commit()
        flash("Patient Medication Added Successfully")
        return redirect(url_for('get_patient_details', mrn=form_mrn))

@app.route("/api/patients/list", methods=["GET"])
def get_patients():
    if 'loggedin' in session and session['account_type'] == 'admin':
        patients = Patients.query.all()
        return jsonify([patient.to_json() for patient in patients])
    else:
        return jsonify({'error': 'Not logged in, please log in first'})

@app.route("/api/patients/<string:mrn>", methods=["GET"])
def get_patient(mrn):
    patient = Patients.query.filter_by(mrn=mrn).first()
    if patient is None:
        abort(404)
    return jsonify(patient.to_json())

@app.route('/api/patient', methods=['POST'])
def create_patient():
    if not request.json:
        abort(400)
    patient = Patients(
        mrn=request.json.get('mrn'),
        first_name=request.json.get('first_name'),
        last_name=request.json.get('last_name')
    )
    db.session.add(patient)
    db.session.commit()
    return jsonify(patient.to_json()), 201

@app.route('/api/patient/<string:mrn>', methods=['PUT'])
def update_patient(mrn):
    if not request.json:
        abort(400)
    patient = Patients.query.filter_by(mrn=mrn).first()
    if patient is None:
        abort(404)
    patient.first_name = request.json.get('first_name', patient.first_name)
    patient.last_name = request.json.get('price', patient.last_name)
    db.session.commit()
    return jsonify(patient.to_json())

@app.route("/api/patient/<string:mrn>", methods=["DELETE"])
def delete_patient(mrn):
    patient = Patients.query.filter_by(mrn=mrn).first()
    if patient is None:
        abort(404)
    db.session.delete(patient)
    db.session.commit()
    return jsonify({'result': True})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)