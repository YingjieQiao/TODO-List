from flask import Flask, render_template, url_for, request, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.config['SECRET_KEY'] = 'password'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    time_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    content = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"Task('{self.title}', '{self.time_posted}')"


class TaskForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    content = TextAreaField("Content", validators=[DataRequired()])
    submit = SubmitField("Create")


@app.route("/")
@app.route("/home")
def home():
    tasks = Task.query.order_by(Task.time_posted.desc())
    return render_template("home.html", tasks=tasks)


@app.route('/task/new', methods=["GET", "POST"])
def new_task():
    form = TaskForm()
    if form.validate_on_submit():
        task = Task(title=form.title.data, content=form.content.data)
        db.session.add(task)
        db.session.commit()
        flash('Your post has been created!', 'success')
        return redirect(url_for('home'))
    return render_template('create_task.html', title='New Task',
                           form=form, legend='New Task')


@app.route('/task/<int:task_id>', methods=['GET', 'POST'])
def task(task_id):
    task = Task.query.get_or_404(task_id)
    return render_template("task.html", title=task.title, task=task)


@app.route("/task/<int:task_id>/update", methods=['GET', 'POST'])
def update_task(task_id):
    task = Task.query.get_or_404(task_id)
    form = TaskForm()
    if form.validate_on_submit():
        task.title = form.title.data
        task.content = form.content.data
        db.session.commit()
        flash('Your task has been updated!', 'success')
        return redirect(url_for('task', task_id=task.id))
    elif request.method == 'GET':
        form.title.data = task.title
        form.content.data = task.content
    return render_template('create_task.html', title='Update task',
                           form=form, legend='Update task')


@app.route("/task/<int:task_id>/delete", methods=['POST'])
def delete_task(task_id):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    flash('Your task has been deleted!', 'success')
    return redirect(url_for('home'))


if __name__ == '__main__':
    app.run(debug=True)
