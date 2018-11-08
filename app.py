#########################################
# Author         : Haibo Zhu             
# Email          : haibo.zhu@hotmail.com 
# created        : 2018-11-05 16:54 
# Last modified  : 2018-11-08 14:51
# Filename       : app.py
# Description    :                       
#########################################
from flask import Flask
from os import path
from flask_sqlalchemy import SQLAlchemy
import random
from db_init import db
import os
'''
from flask_bootstrap import Bootstrap
Bootstrap(app)
sqliteAdminBP = sqliteAdminBlueprint(dbPath = dbPath)
app.register_blueprint(sqliteAdminBP, url_prefix='/sqlite')
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True
'''
class Example(db.Model):
    __tablename__='example'

    id = db.Column(db.Integer, primary_key=True)
    str1 = db.Column(db.String(32))
    str2 = db.Column(db.String(32))
    str3 = db.Column(db.String(32))

    def __init__(self, str1, str2, str3):
      self.str1 = str1
      self.str2 = str2
      self.str3 = str3

    def __repr__(self):
      return "example id:{}, {} {} {}".format(self.id, self.str1, self.str2, self.str3)

    @staticmethod
    def generate(num):
      for i in range(num):
        s1 = random.choice(['2016','2017','2018'])
        s2 = str(random.randint(1,12))
        s3 = str(random.randint(3000,5000))
        e = Example(str1=s1, str2=s2, str3=s3)
        db.session.add(e)
        db.session.commit()

db_path = os.path.abspath('.') + "/example.db"
def create_app():
  app = Flask(__name__)

  from flask_bootstrap import Bootstrap
  Bootstrap(app)

  app.config['WTF_CSRF_SECRET_KEY'] = 'mysecretkey1234567890'
  app.config['SECRET_KEY'] = 'mysecretkey1234567890'
  app.config['DEBUG'] = True
  app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///" + db_path
  app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

  db.init_app(app)

  from flask_sqlite_web.core import sqliteAdminBlueprint
  sqliteAdminBP = sqliteAdminBlueprint(title='Exaqmple',h1='Example',dbPath = db_path)
  app.register_blueprint(sqliteAdminBP, url_prefix='/sqlite')

  return app

def setup_database(app):
  with app.app_context():
    db.create_all()
    Example.generate(100)

if __name__ == '__main__':
  app  = create_app()
  @app.route('/')
  def hello_world():
    return 'Hello flask_sqlite_web!'


  if not os.path.isfile(db_path):
    setup_database(app)
  app.run(host='0.0.0.0', port='5000')
