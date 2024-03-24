from flask import Flask, request, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Feedback
from forms import UserForm, LoginForm, FeedbackForm

app=Flask(__name__)
app.app_context().push()
app.config["SQLALCHEMY_DATABASE_URI"]="postgresql:///user_feedback"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]= False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] ="abcd"
app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False

connect_db(app)
db.create_all()

toolbar = DebugToolbarExtension(app)

@app.route('/')
def home_page():
    return redirect('/register')

@app.route('/register',methods=["GET","POST"])
def register_user():
    form = UserForm()
    if form.validate_on_submit():
        username=form.username.data
        password=form.password.data
        email=form.email.data
        first_name=form.first_name.data
        last_name=form.last_name.data
        new_user=User.register(username,password,email,first_name,last_name)
        db.session.add(new_user)
        db.session.commit()
        session['username']=new_user.username
        return redirect(f"/user/{new_user.username}")
    return render_template('register.html',form=form)

@app.route('/login',methods=["GET","POST"])
def login_user():
    form= LoginForm()
    if form.validate_on_submit():
        username=form.username.data
        password=form.password.data
        user = User.authenticate(username,password)
        if user:
            flash(f"Welcome {user.username}!!")
            session['username']=user.username
            return redirect(f"/users/{user.username}")
        else:
            form.username.errors = ['Invalid username/password']
    return render_template('login.html',form=form)

@app.route('/users/<username>')
def secret_page(username):
    if 'username' not in session:
        flash('login first to see your account..')
        return redirect('/login')
    user = User.query.get(username)
    form=FeedbackForm()
    return render_template('user.html',user=user,form=form)

@app.route('/logout')
def logout_user():
    session.pop('username')
    return redirect('/login')

@app.route('/users/<username>/delete',methods=["POST"])
def delete_user(username):
    if 'username' not in session:
        return redirect('/login')
    user = User.query.get(username)
    all_user_feedbacks=user.feedback
    for user_feedback in all_user_feedbacks:
        db.session.delete(user_feedback)
    db.session.commit()
    db.session.delete(user)
    db.session.commit()
    session.pop('username')
    return redirect('/')

@app.route('/users/<username>/feedback/new',methods=["GET","POST"])
def new_feedback(username):
    if "username" not in session or username != session['username']:
        flash('To add feedback, login first!!')
        return redirect('/login')
    form = FeedbackForm()
    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        new_feedback=Feedback(title=title,content=content,username=username)
        db.session.add(new_feedback)
        db.session.commit()
        flash('Feedback Created!!')
        return redirect(f"/users/{username}")
    else:
        return render_template('new_feedback.html',form=form)
    
@app.route('/feedback/<feedback_id>/update',methods=["GET","POST"])
def update_user_feedback(feedback_id):
    feedback = Feedback.query.get_or_404(feedback_id)
    if "username" not in session or feedback.username != session['username']:
        flash('login first!!')
        return redirect('/login')
    form=FeedbackForm(obj=feedback)
    if form.validate_on_submit():
        feedback.title = form.title.data
        feedback.content = form.content.data
        
        db.session.commit()
        flash('Feedback updated')
        return redirect(f"/users/{feedback.username}")
    else:
        return render_template('edit_feedback.html',form=form,feedback=feedback)
    
@app.route('/feedback/<feedback_id>/delete',methods=["POST"])
def delete_feedback(feedback_id):
    feedback = Feedback.query.get_or_404(feedback_id)
    if "username" not in session or feedback.username != session['username']:
        flash('login first!!')
        return redirect('/login')
    else:
        db.session.delete(feedback)
        db.session.commit()
        return redirect(f"/users/{feedback.username}")

        


    






