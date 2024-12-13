import os
from dotenv import load_dotenv
from flask import Flask,render_template,url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine,text
from flask_login import LoginManager,UserMixin
import pymysql
import urllib.parse

load_dotenv()

password = urllib.parse.quote_plus('nitin@2024')
engine = create_engine(f'mysql+pymysql://root:{password}@localhost')

with engine.connect() as connection:
    connection.execute(text("CREATE DATABASE IF NOT EXISTS users"))

app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://root:{password}@localhost:3306/users'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model,UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(80), nullable=False)

    

@app.route('/')
def home():
  return render_template('home.html')

@app.route('/login')
def login():
  return render_template('login.html')

@app.route('/register')
def register():
  return render_template('register.html')




if __name__ == '__main__':
  with app.app_context():
        db.create_all() 
  app.run(debug=True)
  