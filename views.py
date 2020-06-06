"""
Python Development Techdegree
Project 5 - Build a Learning Journal with Flask
Author: Felix Andrew Sapalaran (felixandrewsapalaran@gmail.com)
---------------------------------------------------------------
"""

import datetime
from flask import (
    Blueprint,
    render_template,
    redirect,
    request,
    flash,
    url_for,
)


from flask_login import (
    login_required,
    login_user,
    logout_user,
    current_user,
)
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired
from werkzeug.urls import url_parse
import models


class LoginForm(FlaskForm):
    """
    Here we use the WTF form functionality to create a login form
    object which can be used for form validation etc
    """
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember_me = BooleanField('Remember Me')
    submit = SubmitField('Sign In')


main_app_views = Blueprint(
    'main_app_views', __name__, template_folder='templates')


@main_app_views.route('/')
@main_app_views.route('/entries')
def index():
    """
    The index view is supposed to return a list of all
    entries
    """
    entries = models.Entry.select()
    tagname = request.args.get('tag', '')
    if tagname:
        entries = entries.where(models.Entry.tags.contains(tagname))
    return render_template("index.html", entries=entries)


@main_app_views.route('/login', methods=['post', 'get'])
def login():
    """
    Perform logout and return to the index
    """
    # Flask-login provides a global `current_user`
    # object which we can check to see if we're logged in
    if current_user.is_authenticated:
        return redirect(url_for('main_app_views.index'))

    # If we're not logged in, we create a login form object
    # using the LoginForm we defined above
    form = LoginForm()

    # Now the following handles the POST section - if the form
    # has been posted correctly, we will enter this block
    if form.validate_on_submit():
        user = models.User.get_or_none(username=form.username.data)
        # If the user wasn't found or the password didn't match
        # we retry the login
        if user is None or not user.check_password(form.password.data):
            # `flash` is a method build-in to Flask to allow
            # messages to be incorporated into the html templates
            # to show messages to the user, such as the one below!
            flash('Invalid username or password')
            # We simply redirect the user back to this same login page
            return redirect(url_for('main_app_views.login'))
        # If the user was found and the password matched
        # we get here and log the user in
        login_user(user, remember=form.remember_me.data)
        # The following is a nice way to automatically
        # continue on to the originally requested page, if
        # we got redirected here because a protected page
        # was requested but the user was not logged in
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main_app_views.index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)


@main_app_views.route('/logout')
def logout():
    """
    If we logout, we simply return to the index page,
    after using flask-login's `logout_user` function
    to register that the user is no longer logged in
    """
    if not current_user.is_authenticated:
        return redirect(url_for('main_app_views.index'))
    logout_user()
    return redirect(url_for('main_app_views.index'))


@main_app_views.route('/entries/new', methods=['GET', 'POST'])
@login_required
def new_view():
    """
    The new view returns a page allowing a new entry to be
    created
    """
    if request.method == 'POST':
        # Now we get the "posted" inputs from the webpage
        # and add them back into the entry
        entry = models.Entry(
            title=request.form['title'],
            date=datetime.datetime.fromisoformat(
                request.form['date']),
            time_spent=request.form['time_spent'],
            learned=request.form['learned'],
            resources=request.form['resources'],
            tags=request.form['tags']
        )
        entry.save()
        return redirect('/entries/{}'.format(entry.slug))
    return render_template("new.html")


@main_app_views.route('/entries/<slug>')
def detail_view(slug):
    """
    The entry detail view returns a page showing the specified
    entry
    """
    entry = models.Entry.get(slug=slug)
    return render_template("detail.html", entry=entry)


@main_app_views.route('/entries/<slug>/edit', methods=['GET', 'POST'])
@login_required
def edit_view(slug):
    """
    The edit view returns a page allowing an existing entry to be
    modified, or if the request is "posted", ammends the entry
    """
    entry = models.Entry.get(slug=slug)
    if request.method == 'POST':
        # Now we get the "posted" inputs from the webpage
        # and add them back into the entry
        entry.title = request.form['title']
        entry.date = datetime.datetime.fromisoformat(
            request.form['date'])
        entry.time_spent = request.form['time_spent']
        entry.learned = request.form['learned']
        entry.resources = request.form['resources']
        entry.tags = request.form['tags']
        entry.save()
        return redirect('/entries/{}'.format(entry.slug))
    return render_template("edit.html", entry=entry)


@main_app_views.route('/entries/<slug>/delete')
@login_required
def delete_view(slug):
    """
    The delete view doesn't return its own page
    as it corresponds to removing an item from the database;
    instead we will return to the index page once the delete
    operation is complete
    """
    # Open the database and delete the item
    entry = models.Entry.get(slug=slug)
    entry.delete_instance()

    # And now we can return to the index page!
    return redirect('/')
