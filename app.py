from flask import Flask, render_template, request, flash, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_required, login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask (__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite3'
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.secret_key = "Secret"

login_manager = LoginManager(app)

db = SQLAlchemy(app) 

class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    email = db.Column(db.String(255), nullable = False , unique = True)
    password = db.Column(db.String(300), nullable = False) 
    name = db.Column(db.String(100), nullable = True)


    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now()) 
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())

class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String, nullable=False)
    user_id = db.Column(db.Integer, nullable=False)
    post_id = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now()) 
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())


db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.route('/') 
def root():
    return render_template('views/index.html')

@app.route('/register', methods=['POST','GET'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('root'))
    if request.method == 'POST':  
        check_email = User.query.filter_by(email=request.form['email']).first() 
        if check_email:  
            flash('Email already taken', 'warning')
            return redirect(url_for('register')) 
        
        new_user = User(name=request.form['name'],  
                        email=request.form['email'])
        new_user.generate_password(request.form['password'])  # raw password will be hashed using the generate_password method
        db.session.add(new_user) # then we add new user to our session
        db.session.commit() # then we commit to our database (kind of like save to db)
        login_user(new_user) # then we log this user into our system
        flash('Successfully create an account and logged in', 'success')
        return redirect(url_for('root')) # and redirect user to our root
    return render_template('views/register.html') 

if __name__ == "__main__":
    app.run(debug = True)
