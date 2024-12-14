import os
from dotenv import load_dotenv
from flask import Flask,render_template,url_for,redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine,text
from flask_login import LoginManager,UserMixin,login_user,login_required,logout_user,current_user
from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField
from wtforms.validators import InputRequired,Length,ValidationError
from flask_bcrypt import Bcrypt
import pymysql
import urllib.parse

load_dotenv()

password = urllib.parse.quote_plus('nitin@2024')
engine = create_engine(f'mysql+pymysql://root:{password}@localhost')

with engine.connect() as connection:
    connection.execute(text("CREATE DATABASE IF NOT EXISTS users"))

app = Flask(__name__)

bcrypt = Bcrypt(app)

app.config['SECRET_KEY'] = 'secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://root:{password}@localhost:3306/users'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
   return User.query.get(int(user_id))

db = SQLAlchemy(app)

class User(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)

class RegisterForm(FlaskForm):
    username = StringField(validators=(InputRequired(),Length(min=4, max=20)),render_kw={"placeholder":"Username"})
    password = PasswordField(validators=(InputRequired(),Length(min=4, max=20)),render_kw={"placeholder":"Password"})
    submit = SubmitField('Register')

    def validate_username(self,username):
       existing_user_name = User.query.filter_by(username=username.data).first()
       if existing_user_name:
          raise ValidationError('That username already exists. Please choose another one.')
       
class LoginForm(FlaskForm):
    username = StringField(validators=(InputRequired(),Length(min=4, max=20)),render_kw={"placeholder":"Username"})
    password = PasswordField(validators=(InputRequired(),Length(min=4, max=20)),render_kw={"placeholder":"Password"})
    submit = SubmitField('Login')

@app.route('/')
def home():
  return render_template('home.html')

@app.route('/login',methods=['GET','POST'])
def login():
  form = LoginForm()
  if form.validate_on_submit():
     user = User.query.filter_by(username=form.username.data).first()
     if user:
        if bcrypt.check_password_hash(user.password,form.password.data):
           login_user(user)
           return redirect(url_for('dashboard'))
  return render_template('login.html',form=form)

@app.route('/dashboard',methods=['GET','POST'])
@login_required
def dashboard():
  return render_template('dashboard.html')

@app.route('/logout',methods=['GET','POST'])
@login_required
def logout():
   logout_user()
   return redirect(url_for('login'))

@app.route('/register',methods=['GET','POST'])
def register():
  form = RegisterForm()
  if form.validate_on_submit():
     hashed_password = bcrypt.generate_password_hash(form.password.data)
     new_user = User(username=form.username.data,password=hashed_password)
     db.session.add(new_user)
     db.session.commit()
     return redirect(url_for('login'))
    
  return render_template('register.html',form=form)




if __name__ == '__main__':
  with app.app_context():
        db.create_all() 
  app.run(debug=True)
  