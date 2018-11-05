#########################################
# Author         : Haibo Zhu             
# Email          : haibo.zhu@hotmail.com 
# created        : 2018-11-05 16:54 
# Last modified  : 2018-11-05 16:55
# Filename       : app.py
# Description    :                       
#########################################
from flask import Flask
from flask_sqlite_admin.core import sqliteAdminBlueprint
from os import path
from flask_sqlalchemy import SQLAlchemy
import random
from flask_bootstrap import Bootstrap

dbPath = path.abspath('.') + "/example.db"

sqliteAdminBP = sqliteAdminBlueprint(dbPath = dbPath)

app = Flask(__name__)
Bootstrap(app)
app.register_blueprint(sqliteAdminBP, url_prefix='/sqlite')

app.config['SECRET_KEY'] = 'hard to guess'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + dbPath
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True

db = SQLAlchemy(app)

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


@app.route('/')
def hello_world():
  return 'Hello Flask!'

if __name__ == '__main__':
  app.run(host='0.0.0.0', port='5000')
