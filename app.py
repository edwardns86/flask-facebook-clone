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


followers = db.Table('followers',
    db.Column('follower_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('followed_id', db.Integer, db.ForeignKey('users.id'))
)
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    email = db.Column(db.String(255), nullable = False , unique = True)
    password = db.Column(db.String(300), nullable = False) 
    name = db.Column(db.String(100), nullable = False , unique = True)
    avatar_url = db.Column(db.String, server_default="https://cdn0.iconfinder.com/data/icons/hr-business-and-finance/100/face_human_blank_user_avatar_mannequin_dummy-512.png"
    )
    followed = db.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=db.backref('followers', lazy='dynamic'), lazy='dynamic')

    def generate_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def follow(self, user):
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        return self.followed.filter(
            followers.c.followed_id == user.id).count() > 0

    def followed_posts(self):
        followed = Post.query.join(
            followers, (followers.c.followed_id == Post.user_id)).filter(
                followers.c.follower_id == self.id)
        own = Post.query.filter_by(user_id=self.id)
        return followed.union(own).order_by(Post.timestamp.desc())

class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String, nullable=False)
    image_url = db.Column(db.String)
    user_id = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.now()) 
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())


class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.String, nullable=False)
    image_url = db.Column(db.String)
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
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    posts = Post.query.all()
    posts = Post.query.order_by(Post.created_at.desc()).all()
    
    if request.args.get('filter') == 'oldest':
        posts = Post.query.order_by(Post.created_at.asc()).all()
        
    if request.args.get('filter') == 'yours':
        posts = Post.query.filter(Post.user_id == current_user.id).order_by(Post.created_at.desc()).all()

    if request.args.get('filter') == 'popular':
        pass
        # post = Post.query.order_by(post.count_comments).desc().all() doesn't work refrencing post within its own function

    for post in posts: 
        user = User.query.get(post.user_id)
        post.username = user.name
        post.avatar_url = user.avatar_url
        post.count_comments = Comment.query.filter_by(post_id = post.id).count()
    return render_template('views/index.html', posts = posts)

@app.route('/logout')
@login_required  
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/login', methods=[ 'GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('root'))
    if request.method == "POST":
        user = User.query.filter_by(email = request.form["email"]).first()
        if not user: 
            flash("Your email is not registered",'warning')
            return redirect(url_for('register'))
        if user.check_password(request.form["password"]):   
            login_user(user)
            flash("Welcome back Ed missed you!", "success")
            return redirect(url_for('root'))
        flash('Incorrect password, please try to login again', 'warning')
    return render_template("views/login.html")

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
                        email=request.form['email'],
                        avatar_url = request.form['avatar_url']
                        )
        new_user.generate_password(request.form['password'])  
        db.session.add(new_user) # then we add new user to our session
        db.session.commit() # then we commit to our database (kind of like save to db)
        login_user(new_user) # then we log this user into our system
        flash('Successfully create an account and logged in', 'success')
        return redirect(url_for('root')) # and redirect user to our root
    return render_template('views/register.html') 


@app.route('/post', methods= ['POST'])
@login_required 
def create_post():
    if request.method == 'POST':
        new_post = Post(
            body = request.form['body'],
            image_url = request.form['image_url'],
            user_id = current_user.id
        )
        db.session.add(new_post)
        db.session.commit()
        flash('Thank you for posting on edbook the smallest social network in the world', 'success')
        return redirect(url_for('root'))
    return redirect(url_for('root')) 

@app.route('/posts/<id>')
@login_required
def view_post(id):

    post = Post.query.get(id)
    user = User.query.get(post.user_id)
    post.username = user.name
    post.avatar_url = user.avatar_url
    comments = Comment.query.filter_by(post_id = post.id).all()
    post.count_comments = Comment.query.filter_by(post_id = post.id).count()
    for comment in comments: 
        user = User.query.get(comment.user_id)
        comment.username = user.name
        comment.avatar_url = user.avatar_url
        
    return render_template('views/post-view.html', post = post , comments = comments ) 

@app.route('/posts/<id>', methods= ['POST'])
@login_required
def edit_post(id):
    post = Post.query.get(id)
    if request.method == 'POST':
        post.body = request.form['body']
        post.image_url = request.form['image_url']
        db.session.commit()
        flash('Thank you for editing your post on edbook the smallest social network in the world', 'success')
        return redirect(url_for('view_post', id=id))  

@app.route('/posts/<id>/delete', methods=['POST'])
@login_required 
def delete_post(id):
    if request.method == 'POST':
        post = Post.query.get(id) 
        user = User.query.get(post.user_id)
        comments = Comment.query.filter_by(post_id = post.id).all() 
        if not post:
            flash("The post you are looking for doesn't exist")
            return redirect(url_for('root'))
        db.session.delete(post)
        db.session.commit()
        flash('We have deleted your post from edbook', 'success')
        return redirect(url_for('root'))
    return "404 error"    

@app.route('/posts/<id>/comments', methods= ['POST'])
@login_required
def create_comment(id):
    if request.method == 'POST':
        comment = Comment(
        user_id = current_user.id , 
        post_id = id,
        body = request.form['body'],
        image_url = request.form['image_url'] 
        )
        db.session.add(comment)
        db.session.commit()
        flash('Thank you for commenting on edbook the smallest social network in the world', 'success')
        return redirect(url_for('view_post', id=id))


@app.route('/comments/<id>/edit', methods= ['POST'])
@login_required
def edit_comment(id):
    comment = Comment.query.get(id)
    if request.method == 'POST':
        comment.body = request.form['body']
        comment.image_url = request.form['image_url']
        db.session.commit()
        flash('Thank you for editing your comment on edbook the smallest social network in the world', 'success')
        return redirect(url_for('root'))  


@app.route('/comments/<id>/delete', methods = ['POST'])
@login_required
def delete_comment(id):
    if request.method == 'POST':
        comment = Comment.query.get(id)
        user = User.query.get(comment.user_id)
        if not comment:
            flash("The comment you are looking for doesn't exist")
            return redirect(url_for('root'))
        db.session.delete(comment)
        db.session.commit()
        flash('We have deleted your comment from edbook', 'success')
        return redirect(url_for('root'))  

@app.route('/follow/<name>')
@login_required
def follow(name):
    user = User.query.filter_by(name=name).first()
    if user is None:
        flash('User {} not found.'.format(name))
        return redirect(url_for('root'))
    if user == current_user:
        flash('You cannot follow yourself!')
        return redirect(url_for('root', name=name))
    current_user.follow(user)
    db.session.commit()
    flash('You are following {}!'.format(name))
    return redirect(url_for('root', name=name))

@app.route('/unfollow/<name>')
@login_required
def unfollow(name):
    user = User.query.filter_by(name=name).first()
    if user is None:
        flash('User {} not found.'.format(name))
        return redirect(url_for('root'))
    if user == current_user:
        flash('You cannot unfollow yourself!')
        return redirect(url_for('root', name=name))
    current_user.unfollow(user)
    db.session.commit()
    flash('You are not following {}.'.format(name))
    return redirect(url_for('root', name=name))



if __name__ == "__main__":
    app.run(debug = True)
