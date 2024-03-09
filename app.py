from flask import Flask,render_template,request,redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///todo.db"   # to connect with sqllite
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False    #signal emmiting purpose
db = SQLAlchemy(app)

# Creating class to store in database
class Todo(db.Model):
    sno = db.Column(db.Integer,primary_key=True)
    title = db.Column(db.String(200),nullable = False)
    desc = db.Column(db.String(500),nullable = False)
    date_created = db.Column(db.DateTime,default=datetime.utcnow)

# what to print when we want to print object of todo
    def __repr__(self) -> str:
        return f"{self.sno} - {self.title}"


# routing pages
@app.route('/',methods=['GET','POST'])
def hello_world():
    if request.method == 'POST':
        title = (request.form['title'])
        desc = (request.form['desc'])
        todo = Todo(title=title,desc = desc)
        db.session.add(todo)
        db.session.commit()
        
    allTodo = Todo.query.all()
    print(allTodo)
    return render_template('index.html',allTodo = allTodo) #using jinja2 adding all todos in html file so we can display

# todo=Todo(title="Mr",desc="4A5")
with app.app_context():
    db.create_all()
    # t11 = Todo(title="Mr", desc="4A5")
    # db.session.add(t11)
    db.session.commit()
    # todo = Todo.query.filter_by(title="Mr").first()
    # print(todo)

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
        return redirect("/")
    
    todo = Todo.query.filter_by(sno=sno).first()
    return render_template('update.html',todo=todo)

@app.route('/delete/<int:sno>')
def delete(sno):
    todo = Todo.query.filter_by(sno=sno).first()
    db.session.delete(todo)
    db.session.commit()
    return redirect("/")


if __name__=="__main__":
    app.run(debug=True)
