from flask import Flask, render_template, request, redirect, session, url_for
import bcrypt
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from zxcvbn import zxcvbn
from pytz import timezone

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///todo.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = "SECRETKEY"
db = SQLAlchemy(app)


class Todo(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    desc = db.Column(db.String(500), nullable=True)
    date_created = db.Column(db.DateTime, default=datetime.now(timezone('Asia/Kolkata')))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref=db.backref('todos', lazy=True))


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.now(timezone('Asia/Kolkata')))
    role = db.Column(db.String(30), default='default')


@app.route('/home', methods=['GET', 'POST'])
def home():
    if 'username' in session:
        user = User.query.filter_by(username=session["username"]).first()

        if request.method == 'POST':
            title = request.form.get('title')
            desc = request.form.get('desc')

            if not title:
                return render_template('index.html', allTodo=user.todos, error="Title is required")

            new_todo = Todo(title=title, desc=desc, user_id=user.id)
            db.session.add(new_todo)
            db.session.commit()

        user_todos = user.todos
        # Convert time zone for each todo item
        for todo in user_todos:
            todo.date_created = todo.date_created.astimezone(timezone('Asia/Kolkata'))
        return render_template('index.html', allTodo=user_todos)
    else:
        return redirect('/signin')


@app.route('/show')
def show():
    if 'username' in session:
        user = User.query.filter_by(username=session["username"]).first()
        user_todos = user.todos
        return render_template('show.html', allTodo=user_todos)
    else:
        return redirect('/signin')


@app.route('/update/<int:sno>', methods=['GET', 'POST'])
def update(sno):
    if 'username' in session:
        user = User.query.filter_by(username=session["username"]).first()
        todo = Todo.query.filter_by(sno=sno, user_id=user.id).first()

        if not todo:
            return "Unauthorized to access this todo."

        if request.method == 'POST':
            title = request.form['title']
            desc = request.form['desc']
            todo.title = title
            todo.desc = desc
            db.session.commit()
            return redirect("/home")

        return render_template('update.html', todo=todo)
    else:
        return redirect('/signin')


@app.route('/delete/<int:sno>')
def delete(sno):
    if 'username' in session:
        user = User.query.filter_by(username=session["username"]).first()
        todo = Todo.query.filter_by(sno=sno, user_id=user.id).first()

        if not todo:
            return "Unauthorized to delete this todo."

        db.session.delete(todo)
        db.session.commit()
        return redirect("/home")
    else:
        return redirect('/signin')


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
            hashPassword = bcrypt.hashpw(ipassword.encode('utf-8'), bcrypt.gensalt())
            new_user = User(username=iusername, password=hashPassword)
            db.session.add(new_user)
            db.session.commit()
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
            return redirect('/home')
        if not user:
            return render_template('signin.html', msg="User does not exist.")
        if user and not bcrypt.checkpw(password.encode('utf-8'), user.password):
            return render_template('signin.html', msg="Incorrect Password")

    return render_template('signin.html')


@app.route('/logout')
def logout():
    session.pop('username')
    return redirect('/signin')

if __name__ == "__main__":
    with app.app_context():
        try:
            db.create_all()
            print("Database tables created successfully.")
        except Exception as e:
            print("An error occurred while creating database tables:", e)

    app.run(debug=True)
