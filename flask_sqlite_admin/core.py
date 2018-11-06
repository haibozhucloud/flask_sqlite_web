#########################################
# Author         : Haibo Zhu             
# Email          : haibo.zhu@hotmail.com 
# created        : 2018-11-05 17:40 
# Last modified  : 2018-11-07 03:43
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
   title='Test data',
   h1='Test data',
   baseLayout='flask_sqlite_admin/sqlite_base.html',
   extraRules=[],
   decorator=defaultDecorator):
  """ create routes for admin """

  sqlite = Blueprint(bpName, __name__,template_folder='templates',static_folder='static')

  #@sh.wrapper()
  @sqlite.route('/',methods=['GET', 'POST'])
  @decorator
  def index():
    print("==>flask_sqlite_admin::index tables:{}".format(tables))
    #db = sqlite3.connect(dbPath,timeout=1000)
    #db.isolation_level=None
    sf = sqliteAdminFunctions(global_db,tables=tables,extraRules=extraRules)

    if request.method == 'POST':
      add_form = AddFieldForm()
      if add_form.validate_on_submit():
        print("  ## Add column :")
        print("  ##   table: {}".format(add_form.field_table.data))
        print("  ##   name :{}".format(add_form.field_name.data))
        print("  ##   type :{}".format(add_form.field_type.data))
        print("  ##   default value :{}".format(add_form.field_default.data))
        sf.addCol(add_form.field_name.data,
            add_form.field_type.data,
            add_form.field_table.data)

    res = sf.tableList(tables)
    #db.close()
    if len(res) == 0:
      raise ValueError('No sqlite db and/or tables found at path = %s' % dbPath)
    else:
      #print("  ##res:{}".format(pprint.pformat(res)))
      return render_template('flask_sqlite_admin/sqlite.html',res=res,title=title,h1=h1,baseLayout=baseLayout,bpName=bpName) 

  #@sh.wrapper()
  @sqlite.route('/api',methods=['GET','POST','PUT','DELETE'])
  @decorator
  def api():
    print("==>flask_sqlite_admin::api request.method:{}".format(request.method))
    # create sqliteAdminFunctions object

    '''
    try:
      pass
      #db = sqlite3.connect(dbPath, timeout=1000)
      #db.isolation_level=None
      c = db.execute("select count(id) as c from example" )
    except Exception as e:
      print("  ##exception:{}".format(e))
    '''

    sf = sqliteAdminFunctions(global_db,tables=tables,extraRules=extraRules)
    # GET request
    if request.method == 'GET':
      q = request.args
      try:
        res = sf.tableContents(request.args['table'],request.args['sort'],request.args['dir'],request.args['offset'])
      except Exception as e:
        #db.close()
        return render_template('flask_sqlite_admin/sqlite_ajax.html',table=request.args['table'],error='{}'.format(e))
      #print("  ## GET res:{}".format(pprint.pformat(res)))
      add_form = AddFieldForm()
      print("  ##set add_form.table {}".format(request.args['table']))
      add_form.field_table.default = request.args['table']
      add_form.field_table.data = request.args['table']
      #db.close()
      return render_template('flask_sqlite_admin/sqlite_ajax.html',add_form=add_form,data=res,title=title,h1=h1,baseLayout=baseLayout,bpName=bpName,q=q,qJson=json.dumps(q))
    # POST request
    elif request.method == 'POST':
      try:
        request_data = request.get_json()
        print("  ## POST: command:{}".format(request_data))
        if "command" in request_data and request_data['command'] == 'del_col':
          del_col = request_data['data']
          table = request_data['table']
          print("  ## deleting a column: {} in {}".format(del_col, table ))
          sf.delCol(del_col, table)
          #db.close()
          return jsonify({'status':'success', 'data':table})
        elif "command" in request_data and request_data['command'] == 'save_row':
          sf.saveRow(request_data['row'],request_data['table'],request_data['id'])
          return jsonify({'status':'success', 'data':table})
        elif "command" in request_data and request_data['command'] == 'delete_row':
          pass
        print('  ## POST res:{}'.format(sf.editTables(request.form,request.method)))
        res = {'status':1,'message':sf.editTables(request.form,request.method)}
      except Exception as e:
        print("  ##error:{}".format(e))
        res = {'status':0,'error':'{}'.format(e)}
      #db.close()
      return json.dumps(res)
    elif request.method == 'PUT':
      print("  ## save new row:{}".format(request.get_json()))
    elif request.method == 'DELETE':
      print("  ## save new row:{}".format(request))


  @sqlite.route('/selected', methods=['POST'])
  @decorator
  def selected():
    print("==>selected: {}".format(request.form.get('selected','null')))

    response = make_response()
    return response

  return sqlite
