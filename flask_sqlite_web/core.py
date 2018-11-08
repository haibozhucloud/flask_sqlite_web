#########################################
# Author         : Haibo Zhu             
# Email          : haibo.zhu@hotmail.com 
# created        : 2018-11-05 17:40 
# Last modified  : 2018-11-08 14:51
# Filename       : core.py
# Description    :                       
#########################################
#import sys
#reload(sys)
#sys.setdefaultencoding('utf8')

from flask import Blueprint, render_template, flash, request, abort, make_response, jsonify
from .sqliteFunctions import sqliteAdminFunctions, rules
import sqlite3
import json
import types
#from flask_secure_headers.core import Secure_Headers
from functools import wraps
import os.path
import pprint
from flask_wtf import FlaskForm
from wtforms import *
from wtforms.validators import *
from db_init import db as global_db

class AddFieldForm(FlaskForm):
  field_table = HiddenField('Table',)
  field_name = StringField('column name:', validators=[DataRequired()])
  field_type = SelectField(label='column type',validators=[DataRequired('select type')],choices=[("string", "TEXT"),("time", "TIME"),("enum", "TEXT")],default=1)
	#,coerce=int)
  field_default = StringField(u'默认值')
  add_field_submit = SubmitField('OK')

# decorators
'''
sh = Secure_Headers()
sh.update({'CSP':{'default-src':['localhost'],'script-src':['self','code.jquery.com','sha256-0U0JKOeLnVrPAm22MQQtlb5cufdXFDzRS9l-petvH6U=']}})
'''

def defaultDecorator(f):
  @wraps(f)
  def decorated_function(*args, **kwargs):
    return make_response(f(*args, **kwargs))
  return decorated_function

def sqliteAdminBlueprint(
   dbPath,
   bpName='sqliteAdmin',
   tables=[],
   title='标题',
   h1='页标题',
   baseLayout='flask_sqlite_admin/sqlite_base.html',
   extraRules=[],
   decorator=defaultDecorator):
  """ create routes for admin """

  sqlite = Blueprint(bpName, __name__,template_folder='templates',static_folder='static')

  #@sh.wrapper()
  @sqlite.route('/',methods=['GET', 'POST'])
  @decorator
  def index():
    sf = sqliteAdminFunctions(global_db,tables=tables,extraRules=extraRules)

    if request.method == 'POST':
      add_form = AddFieldForm()
      if add_form.validate_on_submit():
        sf.addCol(add_form.field_name.data,
            add_form.field_type.data,
            add_form.field_table.data)

    res = sf.tableList(tables)
    #db.close()
    if len(res) == 0:
      raise ValueError('No sqlite db and/or tables found at path = %s' % dbPath)
    else:
      return render_template('flask_sqlite_admin/sqlite.html',res=res,title=title,h1=h1,baseLayout=baseLayout,bpName=bpName) 


  #@sh.wrapper()
  @sqlite.route('/api',methods=['GET','POST','PUT','DELETE'])
  @decorator
  def api():

    sf = sqliteAdminFunctions(global_db,tables=tables,extraRules=extraRules)

    # GET request
    if request.method == 'GET':
      q = request.args
      try:
        res = sf.tableContents(request.args['table'],request.args['sort'],request.args['dir'],request.args['offset'])
      except Exception as e:
        return render_template('flask_sqlite_admin/sqlite_ajax.html',table=request.args['table'],error='{}'.format(e))
      add_form = AddFieldForm()
      add_form.field_table.default = request.args['table']
      add_form.field_table.data = request.args['table']
      #db.close()
      return render_template('flask_sqlite_admin/sqlite_ajax.html',add_form=add_form,data=res,title=title,h1=h1,baseLayout=baseLayout,bpName=bpName,q=q,qJson=json.dumps(q))

    # POST request
    elif request.method == 'POST':
      try:
        request_data = request.get_json()
        if "command" in request_data:

          # delete column
          if request_data['command'] == 'del_col':
            del_col = request_data['data']
            table = request_data['table']
            sf.delCol(del_col, table)
            res = {'status':1, 'message':'<a href="" class="alert-link">Refresh Page</a>'}

          # save a row
          elif request_data['command'] == 'save_row':
            sf.saveRow(request_data['row'],request_data['table'],request_data['id'])
            res = {'status':1, 'message':'<a href="" class="alert-link">Refresh Page</a>'}

          #delete a row
          elif request_data['command'] == 'del_row':
            table = request_data['table']
            id    = request_data['id']
            sf.delRow(table, id)
            res = {'status':1,'message':'<a href="" class="alert-link">Refresh Page</a>'}
          #create a row
          elif request_data['command'] == 'save_detail':
            table = request_data['table']
            row = request_data['row']
            sf.addRow(table,row)
            res = {'status':1,'message':'<a href="" class="alert-link">Refresh Page</a>'}
      except Exception as e:
        res = {'status':0,'error':'{}'.format(e)}
      return json.dumps(res)



  @sqlite.route('/selected', methods=['POST'])
  @decorator
  def selected():

    response = make_response()
    return response

  return sqlite
