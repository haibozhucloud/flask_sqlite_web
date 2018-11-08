# flask_sqlite_web
SQLite Database Management Blueprint for Flask Applications. 

This package creates a management interface to view/modify sqlite databases in an existing Flask application from only a sqlite file. Somewhat similar to Flask-Admin except nothing is required other than a sqlite file.

## Preparation
### Ubuntu16.04
  virtualenv venv3 --python=/usr/bin/python3
  source venv3/bin/activate
  pip3 install -r requirments.txt

## Usage
  >python app.py

  Access http://<your server net address>:5000/sqlite

## Advanced
This project was inspired and quickly created based on https://github.com/twaldear/flask-sqlite-admin
The new features are:
	Can add a new column on web
	Can delete a new column on web
	Works with Python3, sqlite3 and flask_bootstrap

The other information can reference the origin project flask-sqlite-admin at https://github.com/twaldear/flask-sqlite-admin


## Additional Considerations
### Security
This is not a security heavy interface. There is no CSRF protection on the forms and some string substitution had to be used in generating the queries.

However, the following measures do apply:
* Login can be restricted through the decorator parameter
* Only the tables passed in the blueprint object can be viewed/modified
* Table schemas themselves cannod be modified, added, or deleted - only their contents

### Future development
* Variable rows per page drop down
* Ability to create, edit, modify tables
=======
# flask_sqlite_web
Manage sqlite database by web, including editing/removing/adding columns and rows on web. Works with python3, sqlite3, flask framework. Bases on the project of 'twaldear/flask-sqlite-admin' 
>>>>>>> c87d9a9dfcb34ae940fec124a089f52b3d3da826
