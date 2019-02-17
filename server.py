from flask import Flask, render_template, redirect, request, session, flash
from mysqlconnection import connectToMySQL
import re
from flask_bcrypt import Bcrypt

EMAIL_REGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
app = Flask(__name__)
app.secret_key= "IAMGROOT"
bcrypt = Bcrypt(app)

# displays the login/reg page
@app.route('/')
def index():

	return render_template('index.html')

@app.route('/books')
def books():
	#query for left-define variable for html for loop-left
	data={
		"user_id" : session['user_id']
	}
	query="SELECT name FROM users WHERE id = (%(user_id)s);"
	mysql=connectToMySQL("beltrevDB")
	user=mysql.query_db(query, data)
	
	#query for left-define variable for html for loop-left
	mysql=connectToMySQL("beltrevDB")
	left_revs=mysql.query_db("SELECT books.author, books.title, books.creator_id, reviews.rating, reviews.content, users.name, reviews.reviewer_id, reviews.created_at FROM reviews LEFT JOIN books ON reviews.book_id=books.id LEFT JOIN users ON reviews.reviewer_id= users.id ORDER BY created_at ASC LIMIT 0,3;")
	
	
	
	#query for right-define variable for html for loop-right which gets all the books with reviews
	mysql=connectToMySQL("beltrevDB")
	right_titles=mysql.query_db("SELECT title FROM books LEFT JOIN reviews ON reviews.book_id = books.id")
	
	
	return render_template('booksmain.html', user=user[0], reviews= left_revs, titles= right_titles )

# here a user will be able to add a book and review
@app.route('/books/add')
def addBookRev():
	mysql=connectToMySQL("beltrevDB")
	all_authors= mysql.query_db("SELECT author FROM books LEFT JOIN reviews ON reviews.book_id = books.id;")
	return render_template('add.html', authors=all_authors)

@app.route('/add', methods=['POST'])
def add():
	mysql=connectToMySQL("beltrevDB")
	data={
		"creator_id": session['user_id'],
		"title": request.form['title'],
		"author": request.form['newauthor'],
	}
	query="INSERT INTO books(creator_id, title, author, created_at, updated_at) VALUES(%(creator_id)s,%(title)s,%(author)s,NOW(),NOW());"
	books=mysql.query_db(query,data)

	
	mysql=connectToMySQL("beltrevDB")
	data={
		"user_id": session['user_id'],
		"rating": request.form['rating'],
		"content": request.form['content'],
		"book_id": books
	}
	query="INSERT INTO reviews(reviewer_id, book_id, rating, content, created_at, updated_at) VALUES(%(user_id)s, %(book_id)s, %(rating)s, %(content)s, NOW(), NOW());"
	reviews= mysql.query_db(query, data)
	return redirect('/books/add')

# @app.route('/books/<int:books_id>')
# def bookId():
# 	mysql=connectToMySQL("beltrevDB")
# 	query="SELECT * FROM "
# 	return render_template('bookid.html')

# @app.route('/users/<int:user_id>')
# def use(user_id):
# 	return render_template('user.html')

@app.route('/register', methods=["POST"])
def register():
		#validate
	error = False
	if len(request.form['name']) < 3:
		flash("Name must be 3 or more characters")
		error = True
	if len(request.form['alias']) < 3:
		flash("Alias must be 3 or more characters")
		error = True
	if len(request.form['password']) < 8:
		flash("Password must be 8 or more characters")
		error = True
	if request.form['password'] != request.form['c_password']: 
		flash("Password must match!")
		error = True
	if not request.form['name'].isalpha():
		flash("NO BOTS ALLOWED")
		error = True
	if not request.form['alias'].isalpha():
		flash("NO BOTS ALLOWED-alias")
		error = True
	if not EMAIL_REGEX.match(request.form["email"]):
		flash("No BOT emails")
		error = True
	# email nonexistent
	data = {
		"email": request.form["email"]
	}
	query = "SELECT * FROM users WHERE email = %(email)s;"

	mysql = connectToMySQL('beltrevDB')
	matching_email_users= mysql.query_db(query, data)
	if len(matching_email_users) > 0:
		flash("Identity theft is not a joke")
		error = True
	if error:
		return redirect('/')

	data = {
		"name" : request.form['name'],
		"alias"  : request.form['alias'],
		"email"      : request.form['email'],
		"password"   : bcrypt.generate_password_hash(request.form['password'])
	}
	query = "INSERT INTO users (name, alias, email, password, created_at, updated_at) VALUES (%(name)s, %(alias)s, %(email)s, %(password)s, NOW(), NOW());"
	mysql = connectToMySQL('beltrevDB')
	user_id = mysql.query_db(query, data)
	print(user_id)
	session['user_id'] = user_id
	return redirect('/')

@app.route('/login', methods=['POST'])
def login():
    data = {
        "email" : request.form['email']
    }
    query = "SELECT * FROM users WHERE email = %(email)s"
    mysql = connectToMySQL('beltrevDB')
    matching_email_users = mysql.query_db(query,data)
    if len(matching_email_users) == 0:
        flash("Invalid Credentials")
        print("bad email")
        return redirect('/')
    user = matching_email_users[0]
    if bcrypt.check_password_hash(user['password'], request.form['password']):
        session['user_id'] = user['id']
        return redirect('/books')
    flash("Invalid Credentials")
    print("bad pw")
    return redirect('/')

# logs the user out/clears session
@app.route('/logout')
def logout():
	session.clear()
	return redirect('/')
	

if __name__ == "__main__":
    app.run(debug=True)