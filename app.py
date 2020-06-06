"""
Python Development Techdegree
Project 5 - Build a Learning Journal with Flask

Author: Felix Andrew Sapalaran (felixandrewsapalaran@gmail.com)
---------------------------------------------------------------
"""

from flask import Flask
import models
from views import main_app_views


def main():
    """
    Main creation and running - all in a few lines of code now!
    """
    # Create the main flask app normally
    app = Flask(__name__)
    app.secret_key = 'some random key should be set here...!'
    app.config['USERNAME'] = 'default'
    app.config['PASSWORD'] = 'default'

    # Now we need to initialise the database
    models.add_initial_database_content()
    models.add_default_user_using_app_config(app)
    # This handles adding the login managment!
    models.add_login_manager_to_app(app)
    # And this handles opening and closing the database before and
    # after each request
    models.add_before_after_request_functions(app)

    # Views are now defined as a blueprint and are added
    # to the app by simply registering the entire blueprint
    app.register_blueprint(main_app_views)

    # ... and we're good to go! Time to run the app!
    app.run(debug=True)


if __name__ == '__main__':
    main()
