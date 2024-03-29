from flask import Flask,render_template,request,redirect, session,url_for
import bcrypt
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from zxcvbn import zxcvbn   
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///todo.db"   # to connect with sqllite
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False    #signal emmiting purpose
db = SQLAlchemy(app)

app.secret_key = "SECRETKEY"

# Creating class to store in database
class Todo(db.Model):
    sno = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(200),nullable = False)
    desc = db.Column(db.String(500),nullable = False)
    date_created = db.Column(db.DateTime,default=datetime.utcnow)
    username = db.Column(db.String(100), db.ForeignKey('user.username'))
    user = db.relationship('User', backref=db.backref('todos', lazy=True))

# what to print when we want to print object of todo
    def __repr__(self) -> str:
        return f"{self.sno} - {self.title}"
    

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(30), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    role = db.Column(db.String(30), default='default')

    def __repr__(self) -> str:
        return f"{self.username} is Registered"


# routing pages
@app.route('/home',methods=['GET','POST'])
def hello_world():
    if(session["username"]):
        user = Todo.query.filter_by(username = session["username"]).first()

    if request.method == 'POST':
        title = (request.form['title'])
        desc = (request.form['desc'])
        todo = Todo(title=title,desc = desc, username = session["username"])
        db.session.add(todo)
        db.session.commit()
        
    allTodo = Todo.query.filter_by(username = session["username"]).all()
    print(allTodo)
    return render_template('index.html',allTodo = allTodo) #using jinja2 adding all todos in html file so we can display

# to create db file 
with app.app_context():
    db.create_all()
    db.session.commit()

@app.route('/show')
def show():
    allTodo = Todo.query.all()
    print(allTodo)
    return 'Here we can see all data'

@app.route('/update/<int:sno>',methods=['GET','POST'])
def update(sno):
    if request.method=='POST':
        title = (request.form['title'])
        desc = (request.form['desc'])
        todo = Todo.query.filter_by(sno=sno).first()
        todo.title = title
        todo.desc = desc
        db.session.add(todo)
        db.session.commit()
        return redirect("/home")
    
    todo = Todo.query.filter_by(sno=sno).first()
    return render_template('update.html',todo=todo)

@app.route('/delete/<int:sno>')
def delete(sno):
    todo = Todo.query.filter_by(sno=sno).first()
    db.session.delete(todo)
    db.session.commit()
    return redirect("/home")


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        iusername = request.form.get("username")
        ipassword = request.form.get("password")
        icpassword = request.form.get("cpassword")
        user = User.query.filter_by(username=iusername).first()
        if user:
            return render_template('signup.html', msg="User already exists")
        if zxcvbn(ipassword)["score"] < 2:
            return render_template('signup.html', msg=f"{zxcvbn(ipassword)['feedback']['warning']}")
        if ipassword == icpassword:
            # Generating hashed Password
            # salt = bcrypt.gensalt()
            hashPassword = bcrypt.hashpw(ipassword.encode('utf-8'), bcrypt.gensalt())

            user = User(username=iusername,
                        password=hashPassword)
            db.session.add(user)
            db.session.commit()
            # alldata = Table.query.all()
            # print(alldata)
            print(user)
            return redirect(url_for('signin'))
        else:
            return render_template('signup.html', msg="Password does not match.")
    return render_template('signup.html')

@app.route('/', methods=["GET", "POST"])
@app.route('/signin', methods=["GET", "POST"])
def signin():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.checkpw(password.encode('utf-8'), user.password):
            session['username'] = user.username
            session['role'] = user.role
            session['theme'] = ''
            # return redirect('/dashboard')
            return redirect('/home')
        if not user:
            return render_template('signin.html', msg="User does not exists.")
        if user and user.password != password:
            return render_template('signin.html', msg="Incorrect Password")

    return render_template('signin.html')

@app.route('/logout')
def logout():
    session.pop('username') # terminate session
    return redirect('/signin')

if __name__=="__main__":
    app.run(debug=True)
