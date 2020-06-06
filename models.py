"""
Python Development Techdegree
Project 5 - Build a Learning Journal with Flask
Author: Felix Andrew Sapalaran (felixandrewsapalaran@gmail.com)
---------------------------------------------------------------
"""

import datetime
from peewee import (
    SqliteDatabase,
    Model,
    CharField,
    DateField,
    TextField,
    IntegerField,
)


from flask_login import UserMixin, LoginManager
from werkzeug.security import generate_password_hash, check_password_hash
from slugify import slugify


database = SqliteDatabase(
    'entries.db')  # pylint: disable=invalid-name


class Entry(Model):
    """
    Class to hold our entry information
    """
    title = CharField()
    date = DateField()
    time_spent = IntegerField(null=True)
    learned = TextField(default="")
    resources = TextField(default="")
    tags = TextField(default="")
    slug = CharField(unique=True)

    # Adding the internal class Meta is required for Peewee models
    # pylint: disable=too-few-public-methods,missing-class-docstring
    class Meta:
        database = database

    # Here we over-ride the model saving method
    # so that when an entry is saved, a slug is
    # automatically generated from the title
    def save(self, force_insert=False, only=None):
        # To generate the slug, we use the slugify function
        # from the slugify library
        slug = slugify(self.title)
        # As it's possible to have duplicate titles,
        # but we need unique slugs to identify entries,
        # we need to use the following to make sure that
        # the slug we use is unique!
        if self.id is None:
            ind = 1
            while Entry.get_or_none(slug=slug) is not None:
                slug = "{}-{:08d}".format(slug, ind)
        self.slug = slug
        # Now simply call the normal Model save function
        # - "super()" allows a class to call its parent's
        # function. Otherwise we would have to duplicate
        # rest of that code here!
        super().save()

#
# Basic user model for logging in
#


class User(UserMixin, Model):
    """
    Basic user model just for password protection
    """
    # All we need to is the username and password.
    # usernames shoudl be unique
    username = CharField(unique=True)
    password = CharField()

    def __repr__(self):
        return "%d/%s/%s" % (self.id, self.username, self.password)

    def set_password(self, password):
        """
        Instead of saving a plain-text password (considered bad practice)
        we save a "hashed" password which makes seeing the original
        password impossible
        """
        self.password = generate_password_hash(password)

    def check_password(self, password):
        """
        As we saved a hashed password, we now also have to check
        the given password using a special function, as
        directly comparing the given password to the hased
        value stored in self.password would fail!
        """
        return check_password_hash(self.password, password)

    # Here we over-ride the User saving method
    # so that when an entry is saved, the password is
    # hashed
    def save(self, force_insert=False, only=None):
        self.set_password(self.password)
        super().save()

    # pylint: disable=too-few-public-methods,missing-class-docstring
    class Meta:
        database = database


#
# Now test the database for any issues by attempting to connect!
#

database.connect()

# For testing, we reset the table each time we start

database.drop_tables([Entry, User])

# If that was all fine, we can now create the model tables

database.create_tables([Entry, User])
database.close()


def add_initial_database_content():
    """
    Here we initialise the actual content in the database
    so that it doesn't start out empty
    """

    # We've simply pulled most of this content from the original
    # static web pages
    database.connect()
    Entry.create(
        title="The best day I’ve ever had",
        date=datetime.datetime(2016, 1, 31),
        time_spent=15,
        # pylint: disable=line-too-long
        learned="""Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nunc ut rhoncus felis, vel tincidunt neque.
    Cras egestas ac ipsum in posuere. Fusce suscipit, libero id malesuada placerat, orci velit semper metus, quis pulvinar sem nunc vel augue. In ornare tempor metus, sit amet congue justo porta et. Etiam pretium, sapien non fermentum consequat, <a href="">dolor augue</a> gravida lacus, non accumsan. Vestibulum ut metus eleifend, malesuada nisl at, scelerisque sapien.""",  # noqa: 501
        resources="""Lorem ipsum dolor sit amet
    Cras accumsan cursus ante, non dapibus tempor
    Nunc ut rhoncus felis, vel tincidunt neque
    Ipsum dolor sit amet""",
        tags=' best latin long-day ',
    )
    # Let's do the same with a few more entries
    # which were originally present coded into the HTML!
    Entry.create(
        title="The absolute worst day I’ve ever had",
        date=datetime.datetime(2016, 1, 31),
        tags=' long-day bad ',
    )
    Entry.create(
        title="That time at the mall",
        date=datetime.datetime(2016, 1, 31)
    )
    Entry.create(
        title="Dude, where's my car",
        date=datetime.datetime(2016, 1, 31),
        tags=' bad ',
    )
    database.close()


def add_default_user_using_app_config(app):
    """
    Add a default user for the password protected section
    using the values defined in the
    database.connect()
    """
    User.create(
        username=app.config['USERNAME'],
        password=app.config['PASSWORD'])
    database.close()


def add_login_manager_to_app(app):
    """
    Here we use LoginManager from flask-login to handle the
    complictad login process for us
    """
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = "main_app_views.login"

    @login_manager.user_loader
    def load_user(userid):
        """
        This tells LoginManager how to get a user
        """
        # database.connect()
        user = User.get(int(userid))
        # database.close()
        return user


def add_before_after_request_functions(app):
    """
    This modifies app to add before and after-request hooks,
    such that we don't need to keep opening and closing database
    connections
    """
    @app.before_request
    def before_request():
        """Connect to the database before each request."""
        database.connect()

    @app.after_request
    def after_request(response):
        """Close the database connection after each request."""
        database.close()
        return response
