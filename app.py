from flask import Flask,request, session,render_template,jsonify, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI']= 'sqlite:///db.sqlite3'
app.config['SECRET_KEY'] = 'thisissceritkey'

db = SQLAlchemy(app)

class Myadmin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    admin_id = db.Column(db.Integer, db.ForeignKey('myadmin.id'))
    isAdmin = db.Column(db.Boolean, default=False)

class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    data = db.relationship('Data', backref='company', lazy=True)


class Data(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    mobile = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(100), nullable=False)

admin = Admin(app, name="Dashboard") 
my_admin = False
# define model view for Compay
class CompanyModelView(ModelView):
    def is_accessible(self):
        if session.get('is_admin'):
            return True
        else:
            return False
        
# define User Model View
class UserModelView(ModelView):
    def is_accessible(self):
        if session.get('is_admin'):
            return True
        else:
            return False

# define Data Model View
class DataModeView(ModelView):
    if not my_admin:
        can_delete = False
        can_edit = False



admin.add_view(CompanyModelView(Company, db.session)) 
admin.add_view(DataModeView(Data, db.session,category='Team')) 
admin.add_view(UserModelView(User,db.session, category='Team'))
    

@app.route('/')
def index():
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    return "This is flask app"

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        admin = Myadmin.query.filter_by(username=username, password=password).first()
        
        if admin:
            
            session['user_id'] = admin.id
            session['logged_in'] = True  
            session['is_admin'] = True
        
            return redirect(url_for('index'))

        else:
            user = User.query.filter_by(username=username, password=password).first()
            if user:
                print('this is user section')
                session['user_id'] = user.id
                session['logged_in'] = True  
                session['is_admin'] = False
                print("sessin =>", session.get('is_admin'))
                
                return redirect(url_for('index'))
            return render_template('login',mess="invalid credintials!")
    if request.method == 'GET':
        return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    # return redirect(url_for('login'))
    return redirect(url_for('login'))


@app.route('/register', methods=['POST'])
def register():
    name = request.json.get('username')
    password = request.json.get('password')
    admin = request.json.get('isAdmin')

    try:
        user = User(username=name, password=password)
        if admin:
            adminUser = Myadmin(username=name, password=password)
            db.session.add(adminUser)
            user.admin = adminUser
        
        db.session.add(user)
        db.session.commit()
        return jsonify({'message':'User created Successfuly!'})

    except Exception as e:
        db.session.rollback
        return jsonify({'error':"Failed to create user!", 'message':str(e)}),500


if __name__ == '__main__':
    app.run()