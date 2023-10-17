from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User, Feedback
from forms import UserForm, Login, Comment
from sqlalchemy.exc import IntegrityError

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///flask_feedback_db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "abc123"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

app.app_context().push()
# ACCESS FLASK WITHIN IPYTHON AND HAVE SESSIONS

connect_db(app)
db.create_all()

toolbar = DebugToolbarExtension(app)

@app.route('/')
def home_page():
    """Home page to view all feedback, if logged in you can edit/delete posts too."""
    all_feedback = Feedback.query.all()
    return render_template('base.html', feedbacks=all_feedback)

@app.route('/register', methods = ['GET','POST'])
def register_new_user():
    """Using WTForms to validate Post then add to database OR rendering the register template if invalid.
    
    Setting session to username if successful. 
    """
    form = UserForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        new_user = User.register(username,password, email,first_name,last_name)

        db.session.add(new_user)
        db.session.commit()
        session['username'] = new_user.username
        flash("New user registered.", 'success')
        return redirect(f'/users/{new_user.username}')

    return render_template('register.html', form =form)

@app.route('/users/<username>')
def view_flask_comments(username):
    """View the logged in user's comments list. """
    if "username" not in session:
        flash("Please login to view content.", 'danger')
        return redirect('/login')

    u = User.query.filter_by(username=username).first()
    return render_template('user_page.html', user=u)

@app.route('/login', methods = ['GET', 'POST'])
def login_user():
    """Directs to the login form with WTForms to validate and direct logic for 'post' or render template for 'get'"""
    form = Login()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        user = User.authenticate(username, password)
        if user:
            session['username'] = user.username
            flash(f'Welcome Back, {user.username}!')
            return redirect(f'/users/{user.username}')
        else:
            form.username.errors = ['Invalid username/password combination.']

    return render_template('login.html', form=form)

@app.route('/logout', methods = ['POST'])
def logout_user():
    """Logs the user out by removing username from the session and sending to the home page. """
    session.pop('username')
    flash("Successfully logged out!", 'success')
    return redirect('/')

@app.route('/users/<username>/feedback/add', methods = ['POST', 'GET'])
def add_feedback_form(username):
    """Creates new feedback using WTForms to 'post'/validate inputs OR render template of feedback form. """
    if "username" not in session:
        flash("Please login to add feedback.", 'danger')
        return redirect('/login')
    if session['username'] == username:
        u = User.query.filter_by(username= username).first()
        form = Comment()
        if form.validate_on_submit():
            title = form.title.data
            content = form.content.data 
            new_feedback = Feedback(title=title, content=content, user_id=u.id)
            db.session.add(new_feedback)
            db.session.commit()
            flash("Your comment was added.", 'success')
            return redirect(f'/users/{u.username}')
    
    return render_template('feedback.html', form=form)

@app.route('/feedback/<int:feedback_id>/update', methods = ['POST', 'GET'])
def update_feedback(feedback_id):
    """ Updates the feedback and populates with current feedback into the form. Again uses WTForms to determine 'post' vs 'get' and validate the incoming data."""
    if 'username' not in session:
        flash("Please login to edit feedback.", 'danger')
        return redirect('/login')
    feedback = Feedback.query.get_or_404(feedback_id)
    form = Comment(obj = feedback)
    if form.validate_on_submit():
        feedback.title = form.title.data
        feedback.content = form.content.data
        db.session.commit()
        flash("Your comment was updated.", 'success')
        return redirect(f'/users/{feedback.user.username}')
    
    return render_template('feedback.html', form=form)


@app.route('/feedback/<feedback_id>/delete', methods = ['POST'])
def delete_feedback(feedback_id):
    """Delete feedback only for the user who created it."""
    if 'username' not in session:
        flash("Please login first!", 'danger')
        return redirect('/login')
    feedback = Feedback.query.get_or_404(feedback_id)
    if feedback.user.username == session['username']:
        db.session.delete(feedback)
        db.session.commit()
        flash('Your feedback was deleted.', 'success')
        return redirect('/')
    
    flash("You don't have permission to delete this feedback.", 'success')
    return redirect('/')

@app.route('/users/<username>/delete', methods = ['post'])
def delete_the_user_cascade_delete_feedback(username):
    """This will remove the user from the database and their associated feedbacks."""
    user = User.query.filter_by(username=username).first()
    if user.username == session['username']:
        db.session.delete(user)
        db.session.commit()
        session.pop('username')
        flash('User deleted', 'success')
        return redirect('/')
    
    flash("You are not authorized to delete this user.", 'danger')
    return redirect('/')
