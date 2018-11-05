import re
from functools import wraps
import types
import sys
import sqlite3
import pprint
import time

'''
reload(sys)
sys.setdefaultencoding("utf-8")
'''

def execRule(i):
  def do_assignment(to_func):
    to_func.run = i
    return to_func
  return do_assignment

class rules:
  """ base rules applied to all modifications """
  
  def __init__(self,colData,postData,tables,method):
    self.colData = colData
    self.postData = postData
    self.method = method
    self.methods = ['GET','POST','PUT','DELETE']
    self.tables = tables
    if self.colData['name'] in self.postData:
      self.value = self.postData[self.colData['name']]
    else:
      self.value = '0'

  @execRule(1)
  def validTable(self):
    """ check if table is in object """
    if 'table' not in self.postData or self.postData['table'] not in self.tables:
      raise ValueError('invalid table `%s`' % self.postData['table'])
  
  @execRule(2)
  def validAction(self):
    """ check if action is valid """
    if self.method is None:
      raise ValueError('no method in request')
    elif self.method not in self.methods:
      raise ValueError('invalid method `%s`' % self.method)

  @execRule(3)
  def idRequired(self):
    """ check if id parameter passed for edit/delete functions """
    if self.method == 'put' or self.method == 'delete':
      if 'id' not in self.postData:
        raise ValueError('Request must include an id')


  @execRule(4)
  def notNull(self):
    """ check if null value passed for not null columns """
    if self.colData['name'] not in self.postData or self.value=='':
      if self.colData['notNull'] is 1 and self.colData['primaryKey'] is 0:
        raise ValueError('%s field required' % self.colData['name'])    
  
  @execRule(5)
  def integer(self):
    """ check if integer for integer affinity columns """
    if self.colData['dataType'].lower() in ['integer','int','tinyint','smallint','mediumint','bigint','unisgned big int','int2','int8']:
      try:
        int(self.value)
      except Exception as e:
        raise ValueError('Non integer value `%s` for field %s' % (self.value, self.colData['name']) )
  
  @execRule(6)
  def real(self):
    """ check if float for real affinity columns """
    if self.colData['dataType'].lower() in ['real','float','double','double precision']:
      try:
        float(self.value)
      except Exception as e:
        raise ValueError('Non real/float value `%s` for field %s' % (self.value, self.colData['name']) )

class sqliteAdminFunctions:
  """ functions for SQLite3 Admin tool """

  def __init__(self,con,tables=[],extraRules=[]):
    print("==>sqliteAdminFunctions::__init__")
    self.db = con
    self.extraRules = extraRules
    self.tables = self.tableList(tables)
    #c = self.db.execute("select count(?) as c from 'example' ", ['id'])

  def dict_factory(self,cursor, row):
    #print("==>dict_factory ")
    """ function to return sqlite results in dict """
    d = {}
    for idx, col in enumerate(cursor.description):
      try:
        #str(row[idx]).decode('utf-8').encode('utf-8')
        d[col[0]] = row[idx]
      except:
        d[col[0]] = "invalid byte"
    return d

  def tableList(self,tables):
    print("==>tableList")
    if len(tables) > 0:
      return tables
    else:
      print("  ## db execute SELECT name FROM sqlite_master WHERE type = \"table\"")
      c = self.db.execute('SELECT name FROM sqlite_master WHERE type = "table"')
      tables=  c.fetchall()

      if ('sqlite_sequence',) in tables:
        tables.remove(('sqlite_sequence',))
      print("  ## find tables:{}".format(tables))
      return [row[0] for row in tables]

  def tableContents(self,table,sort,dir,offset):
    print("==>tableContents")
    """ create list of tables for admin """
    res = {}
   
    if table in self.tables:
      res['schema'] = self.tableSchemas(table)
      if res['schema'][0]['primaryKey'] == 1:
        res['primaryKey'] = res['schema'][0]['name']
        
        con = self.db
        con.row_factory = self.dict_factory
        print("  ##db execute select count({}) as c from {}".format(res['primaryKey'],table))
        c = self.db.execute('select count(?) as c from %s' % (table),[res['primaryKey']])
        res['count'] = c.fetchone()['c']
        self.db.commit() 
        if sort == '': sort = res['primaryKey']
        print("  ## db execute select * from {} order by {} {} limit {},50".format(table, sort, dir, int(offset)))
        l = self.db.execute('select * from %s order by %s %s limit ?,50' % (table,sort,dir),[int(offset)*50])
        res['contents'] = l.fetchall()
        self.db.commit()
        return res
      else:
        raise ValueError('No primary key for first column in table `%s`' % table)
    else:
      raise ValueError('invalid table `%s`' % table)

  def tableSchemas(self,table):
    """ return table schemas by column """
    print("==>tableSchemas")
    cur = self.db.cursor()
    print("  ## db cursor execute PRAGMA table_info({})".format(table))
    cur.execute('PRAGMA table_info({})'.format(table) )
    sch = cur.fetchall()
    cur.close()
    self.db.commit()
    print(sch)
    return [{'name':row[1],'dataType':row[2],'notNull':row[3],'primaryKey':row[5]} for row in sch]
   
  def tableCols(self, table):
    print("==>tableCols")
    
    cur = self.db.cursor()
    print("  ## db cursor execute PRAGMA table_info({})".format(table))
    cur.execute('PRAGMA table_info({})'.format(table) )
    sch = cur.fetchall()
    cur.close()
    self.db.commit()

    res = []
    for row in sch:
      c = ''
      c += row[1] 
      c += ' ' + row[2]
      if row[5] == 1:
        c += ' PRIMARY KEY AUTOINCREMENT'
      res.append(c)
    print("  ## return columns: {}".format(res))
    return res

  def checkValid(self,q,method):
    print("==>checkValid")
    """ validate admin input """

    if 'table' not in q:
      raise ValueError('no table value provided')
    elif q['table'] not in self.tables:
      raise ValueError('invalid table `%s`' % q['table'])
    else:
      for col in self.tableSchemas(q['table']):

        # iterate through rules
        r = rules(col,q,self.tables,method) # instantiate rules objecy
        if len(self.extraRules)>0: 
          # add extra rules
          for i,x in enumerate(self.extraRules):
            x.run = 7+i
            def add_method(self, method, i):
              setattr(self.__class__, 'extraRule%d' % i, method)
            add_method(r,x,i)
        # perform rule check  
        funcs = sorted(
          [ getattr(r, field) for field in dir(r) if hasattr(getattr(r, field), "run") ],
          key = (lambda field: field.run)
        )
        for func in funcs:
          try:
            func()
          except Exception as e:
            raise

  def editTables(self,q,method):
    print("==>editTables")
    """ edit tables """
    qString = ''
    qParams = []

    # validate input
    self.checkValid(q,method)

    # create copy of request
    q2 = q.copy()
    del q2['table']

    # edit
    ret = ''
    if method == 'PUT':
      del q2['id']
      del q2['primaryKey']

      qString = 'update %s set %s where %s=?' % (q['table'],', '.join("%s=?" %p for p in q2.keys()),q['primaryKey'])
      qParams = [v for k,v in q2.items()]
      qParams.append(q[q['primaryKey']])
    # add
    elif method == 'POST':
      del q2['primaryKey']
 
      qString = 'insert into %s (%s) values (%s)' % (q['table'],','.join(q2.keys()),','.join("?" for p in q2.keys()) )
      qParams = [v for k,v in q2.items()]
      ret = '<a href="" class="alert-link">Refresh Page</a>'
    # delete
    elif method == 'DELETE':
      qString = 'delete from %s where %s=?' % (q['table'],q['primaryKey'])
      qParams = [q['id']]
      ret = 'Row deleted'

    # execute sql
    print("  ##db execute {} {}".format(qString, qParams))
    self.db.execute(qString,qParams)
    self.db.commit()
    return ret

  #检查表中是否已存在列
  def checkColumn(self,col,table):
    print("==>checkColumn")
    sch = self.tableSchemas(table)
    cols = [{'col':row['name']} for row in sch]
    if {'col':col} in cols:
      print(' columns {} exists'.format(pprint.pformat(cols)))
      return True
    return False

  def addCol(self,new_col,new_col_type,table):
    print("==>addCol")

    #增加新字段
    if self.checkColumn(new_col,table):
      print(" The column {} exists!".format(new_col))
      return(0)

    command = "ALTER TABLE {} ADD {} {};".format(table, new_col, new_col_type)
    print("  ## db cursor execute {}".format(command))
    cu = self.db.cursor()

    res = cu.execute(command)
    cu.close()
    self.db.commit()
    print("  ##{}".format(pprint.pformat(self.tableSchemas(table))))

  '''
  #Get columns
  def getColumns(self, table):
    print("==>getColumns")
    sch = self.tableSchemas(table)
    cols = [row['name'] for row in sch]
    return cols
  '''

  def delCol(self, del_col, table):
    print("==>delCol")
    cols = self.tableCols(table)
    deleted = False
    for c in cols:
      if c.find(del_col) == 0:
        cols.remove(c)
        deleted = True
        break
    
    if deleted == False:
      print("The column {} doesn't exists".format(del_col))
      return
    cp_cols= [row.split()[0] for row in cols]
    try:
      db = self.db
      db.close()
      db1 = sqlite3.connect("/mnt/educloud/working/example.db")
      cu = db1.cursor()
      command = "drop table if exists 'temp'"
      print("  ## db execute {}".format(command))
      cu.execute(command)
      db1.commit()

      command = "create table temp({})".format(','.join(cols))
      print("  ##db execute {}".format(command))
      cu.execute(command)
      db1.commit()

      command = "insert into {}({}) select {} from {}".format('temp', ','.join(cp_cols), ','.join(cp_cols), table)
      print("  ##db execute {}".format(command))
      cu.execute(command)
      db1.commit()

      command = "drop table if exists {}".format(table) 
      print("  ##db execute {}".format(command))
      cu.execute(command)
      db1.commit()

      command = "alter table temp rename to {}".format(table)
      print("  ##db execute {}".format(command))
      cu.execute(command)
      db1.commit()

      db1.close()
      self.db = sqlite3.connect("/mnt/educloud/working/example.db")

    except self.db.Error as ex:
      print(ex)
    #print(pprint.pformat(self.tableSchemas(table)))


