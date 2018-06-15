from flask import Flask, render_template, flash, url_for, session, logging, request, redirect
from data import Articles
from flask_mysqldb import MySQL
from wtforms import Form, StringField, TextAreaField, PasswordField, validators
from passlib.hash import sha256_crypt
from functools import wraps

app = Flask(__name__)

# Config MySQL
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'xflow123'
app.config['MYSQL_DB'] = 'flask_blog_app'

# By default the db cursor returns touples as a result of query 
# to get dictionary object set DictCursor as cursor class
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# init  MySQL
mysql = MySQL(app)

# Get articles. As there is no db setup for articles just get 
# the articles from a static python file
all_articles = Articles()

# Index page of application
@app.route('/')
def hello_world():
    return render_template('home.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/articles')
def articles():
    return render_template('articles.html', articles = all_articles)

@app.route('/article/<string:id>')
def article(id):
    return render_template('article.html', id = id)

# Helper function for html forms. 
# This allows us to create html forms with server side validations.
# Checkout https://github.com/wtforms/wtforms
class RegisterForm(Form):
    name = StringField('Name', [validators.Length(min=1, max=50)])
    username = StringField('Username', [validators.Length(min=4, max=25)])
    email = StringField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', [
        validators.DataRequired(),
        validators.EqualTo('confirm', message='Passwords do not match.')
    ])
    confirm = PasswordField('Confirm Password')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        name = form.name.data
        email = form.email.data
        username = form.username.data
        password = sha256_crypt.encrypt(str(form.password.data))

        # Create cursor to execute db querys
        cur = mysql.connection.cursor()

        # TODO: Check if username already exists.

        # Insert user data in database
        cur.execute("INSERT INTO users(name, email, username, password) VALUES (%s, %s, %s, %s)", (name, email, username, password))

        # Commit db changes done by the above query
        mysql.connection.commit()

        # Close db connection
        cur.close()

        flash('You are now registered and can log in', 'success')

        return redirect(url_for('login'))
    return render_template('register.html', form=form)

# User login
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method != 'POST':
        return render_template('login.html')

    # Get form data from request
    username = request.form['username']
    password_candidate = request.form['password']

    # Create cursor to execute db querys
    cur = mysql.connection.cursor()

    # Get user data for passed username from db
    result = cur.execute("SELECT * FROM users WHERE username = %s", [ username ])

    if result > 0:
        # We have some results.
        
        # Get the first record from the results. 
        # There should be one record for a username in the db.
        data = cur.fetchone()
        password = data['password']

        # Close db connection
        cur.close()

        # Check if the password in request is valid.
        if sha256_crypt.verify(password_candidate, password):
            # Passed. Set session
            session['logged_in'] = True
            session['username'] = username
            session['userId'] = data['id']

            flash('You are now logged in', 'success')
            return redirect(url_for('dashboard'))
        else:
            # Password did not match
            error = 'Invalid login.'
            return render_template('login.html', error=error)
    else:
        # No users found with passed username
        
        # Close db connection
        cur.close()
        
        error = 'Username not found.'
        return render_template('login.html', error=error)

    return render_template('login.html')

# Decorator to verify that there is a valid login present.
# If someone is trying to access a page which is login protected 
# and there is no valid login present, redirect the user to login page.
# 
# This can be used to restrict pages where login is always 
# required to access the page.
# 
# Check http://flask.pocoo.org/docs/0.12/patterns/viewdecorators/
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthorized, Please login', 'danger')
            return redirect(url_for('login'))
    return wrap

@app.route('/logout')
def logout():
    session.clear()
    flash('You are now logged out', 'success')
    return redirect(url_for('login'))

@app.route('/dashboard')
# Only show dashboard if there is a login present
@is_logged_in
def dashboard():
    return render_template('dashboard.html')

if __name__ == '__main__':
    app.secret_key='mysecret@%!'
    app.run(debug=True)
