import os

from flask import Flask, render_template, session, request, redirect, escape, url_for
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

#welcoming page
@app.route("/")
def hello():
	if 'email' in session:
		name = db.execute("SELECT name FROM users WHERE email = :email",{"email": session['email']}).fetchone()
		return render_template("index.html",name=name)
	countries = db.execute("SELECT countrycode,countryname FROM countries").fetchall()
	return render_template("hello.html", countries=countries)
# Registration
@app.route("/registration", methods=["POST"])
def registration():
	name = request.form.get("name")
	lastname = request.form.get("lastname")
	email = request.form.get("email")
	age = request.form.get("age")
	country = request.form.get("country")
	password = request.form.get("password")
	user_info = db.execute("INSERT INTO users(name,lastname,country,age,email,password) VALUES(:name,:lastname,:country,:age,:email,:password)",
	{"name": name,"lastname": lastname,"country": country,"age": age,"email": email,"password": password}	)
	db.commit()
	return render_template("index.html")

# Login
@app.route("/login",methods=["POST", "GET"])
def login():
	if request.method == 'POST':
		session['email'] = request.form['email']
		return redirect(url_for('hello'))
	email_promt = request.form.get("email")
	password_promt = request.form.get("password")
	check_one = db.execute("SELECT email,password FROM users WHERE email = :email AND password = :password", {"email": email_promt,"password": password_promt}).fetchone()	
	if check_one is None:
		no_display = True
		return "Error"
	return render_template("index.html")
# Logout
@app.route('/logout')
def logout():
    # remove the username from the session if it's there
	session.pop('email', None)
	return redirect(url_for('hello'))
#If search doesn't return results
@app.route("/again")
def again():
	if 'email' in session:
		name = db.execute("SELECT name FROM users WHERE email = :email",{"email": session['email']}).fetchone()
		return render_template("search.html",name=name)

# Application Dashboard
@app.route("/dashboard")
def dashboard():
	return render_template("index.html")
# code for Search Engine
@app.route("/search",methods=["GET","POST"])
def search():
	if request.method == "POST":
		search_query = request.form.get("search")
		books = db.execute("SELECT * FROM books WHERE isbn = :search OR title = :search OR author = :search",
			{"search": search_query})
		return render_template("index.html",books=books)	
	error_message = ("It Turns Out there is no such a book. Try Again...")
	return render_template("search.html",error_message=error_message)
# Index page of Books
@app.route("/index",methods=["POST","GET"])
def list():
	if 'email' in session:
		name = db.execute("SELECT name FROM users WHERE email = :email",{"email": session['email']}).fetchone()
		books = db.execute("SELECT * FROM books").fetchall()
		return render_template("list.html",books=books,name=name)