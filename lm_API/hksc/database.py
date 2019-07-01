from collections import OrderedDict
import sqlite3
from contextlib import closing
import pickle

class InternalProcess(object):
    def ug_get(self,type,id,var_name):
        if self.dbType == "JSON":
            if id not in self.db[type]:
                self.ug_reset(type,id)
            if var_name not in self.db[type][id]:
                if var_name in self.db[type]["Default"]:
                    self.db[type][id][var_name] = self.db[type]["Default"][var_name]
                else:
                    return None
            return self.db[type][id][var_name]
        else:
            if self.dbType == "SQLite":
                self.conn.execute("PRAGMA TABLE_INFO(%s)"%(type))
                keys = [x[1] for x in self.conn.fetchall()]
            else:
                self.conn.execute("SHOW COLUMNS FROM %s;"%(type))
                keys = [x[0] for x in self.conn.fetchall()]
            if var_name not in keys:
                return None
            self.conn.execute("SELECT %s FROM %s WHERE id='%s'"%(var_name,type,id))
            resp = self.conn.fetchone()[0]
            if resp == "True":
                resp = True
            elif resp == "False":
                resp = False
            return resp
            
    def ug_del(self,type,id):
        try:
            if self.dbType == "JSON":
                if id in self.db[type]:
                    del self.db[type][id]
            else:
                self.conn.execute("DELETE FROM %s WHERE id='%s'"%(type,id))
                self.db.commit()
            return True
        except:
            return False
    
    def ug_post(self,type,id,var_name,data,binary=False):
        if self.dbType == "JSON":
            if id not in self.db[type]:
                self.ug_reset(type,id)
            self.db[type][id][var_name] = data
        else:
            try:
                # Make new User if not there.
                self.conn.execute("SELECT * FROM %s WHERE id='%s'"%(type,id))
                chk = self.conn.fetchone()
                if chk == None:
                    self.ug_reset(type,id)
                # Get Table Keys
                if self.dbType == "SQLite":
                    self.conn.execute("PRAGMA TABLE_INFO(%s)"%(type))
                    keys = [x[1] for x in self.conn.fetchall()]
                else:
                    self.conn.execute("SHOW COLUMNS FROM %s;"%(type))
                    keys = [x[0] for x in self.conn.fetchall()]
                # Make new Column if not there.
                if var_name not in keys:
                    self.ug_makeVar(type,var_name,data)
                # Update Table data
                if binary:
                    data = pickle.dumps(data,pickle.HIGHEST_PROTOCOL)
                    sql = "UPDATE %s SET %s=? WHERE id='%s'"%(type,var_name,id)
                    self.conn.execute(sql,(sqlite3.Binary(data),))
                else:
                    self.log("UPDATE %s SET %s = '%s' WHERE id='%s'"%(type,var_name,data,id))
                    self.conn.execute("UPDATE %s SET %s = '%s' WHERE id='%s'"%(type,var_name,data,id))
                self.db.commit()
            except:
                self.db.rollback()
                raise Exception("post%s failed"%(type))
                
    def ug_default(self,type,id):
        if self.dbType == "JSON":
            self.db[type]["Default"] = self.db[type][id]
        else:
            try:
                if self.dbType == "SQLite":
                    self.conn.execute("PRAGMA table_info(%s);"%(type))
                    table_keys = [k[1] for k in self.conn.fetchall()]
                else:
                    self.conn.execute("SHOW COLUMNS FROM %s;"%(type))
                    table_keys = self.conn.fetchall()
                    table_keys = [k[0] for k in self.conn.fetchall()]
                self.conn.execute("DELETE FROM %s where id='Default'"%(type))
                self.conn.execute("INSERT INTO %s ('id') VALUES ('Default')"%(type))
                self.conn.execute("SELECT * FROM %s where id='%s'"%(type,id))
                default_values = list(self.conn.fetchone())
                for i,k in enumerate(table_keys):
                    if i != 0:
                        self.conn.execute("UPDATE %s SET '%s'='%s' where id='Default'"%(type,k,default_values[i]))
                self.db.commit()
            except:
                self.db.rollback()
                raise Exception("default%s failed"%(type))
                
    def ug_makeVar(self,_type,var_name,data=None,default=False):
        if self.dbType != "JSON":
            pysq = {
                "int":"NUMERIC",
                "float":"NUMERIC",
                "bool":"NUMERIC",
                "dict":"TEXT",
                "OrderedDict":"TEXT",
                "str":"TEXT"
            }
            sqdf = {
                "TEXT":'DummyText',
                "NUMERIC": 0
            }
            dataType = type(data).__name__
            if dataType in pysq:
                if not default:
                    self.conn.execute("ALTER TABLE %s ADD COLUMN %s %s DEFAULT %s"%(_type,var_name,pysq[dataType],sqdf[pysq[dataType]]))
                else:
                    self.conn.execute("ALTER TABLE %s ADD COLUMN %s %s DEFAULT '%s'"%(_type,var_name,pysq[dataType],default))
            else:
                self.conn.execute("ALTER TABLE %s ADD COLUMN %s BLOB;"%(_type,var_name))
            self.db.commit()

    def ug_reset(self,type,id):
        if self.dbType == "JSON":
            if "Default" in self.db[type]:
                self.db[type][id] = self.db[type]["Default"]
            else:
                self.db[type][id] = OrderedDict()
        else:
            self.conn.execute("DELETE FROM %s where id='%s'"%(type,id))
            self.conn.execute("INSERT INTO %s ('id') VALUES ('%s')"%(type,id))
            self.conn.execute("SELECT * FROM %s where id='Default'"%(type))
            default_values = self.conn.fetchone()
            if self.dbType == "SQLite":
                self.conn.execute("PRAGMA table_info(%s);"%(type))
                table_keys = self.conn.fetchall()
            else:
                self.conn.execute("SHOW COLUMNS FROM %s;"%(type))
                table_keys = self.conn.fetchall()
            for i,k in enumerate(table_keys):
                if i != 0:
                    self.conn.execute("UPDATE %s SET '%s'='%s' where id='%s'"%(type,k[1],default_values[i],id))
            self.db.commit()
            
    def ps_list(self,type):
        if self.dbType == "JSON":
            return self.db[type].keys()
        self.conn.execute("SELECT distinct name FROM %s"%(type))
        return [x[0] for x in self.conn.fetchall()]
        
    def ps_get_by_name(self,type,pName):
        if self.dbType == "JSON":
            ret = []
            if pName in self.db[type]:
                ret = self.db[type][pName]
            return ret
        self.conn.execute("SELECT mid_or_gid FROM %s where name='%s'"%(type,pName))
        return [x[0] for x in self.conn.fetchall()]
        
    def ps_get_by_id(self,type,mid_or_gid):
        if self.dbType == "JSON":
            ret = []
            for g in self.db[type]:
                if mid_or_gid in self.db[type][g]:
                    ret.append(g)     
            return ret
        self.conn.execute("SELECT name FROM %s where mid_or_gid='%s'"%(type,mid_or_gid))
        return [x[0] for x in self.conn.fetchall()]
        
    def ps_delete(self,type,dataName):
        if self.dbType == "JSON":
            if permission in self.db[type]:
                del self.db[type][dataName]
        else:
            self.conn.execute("DELETE FROM %s where name='%s'"%(type,dataName))
            self.db.commit()

    def ps_post(self,type,mid_or_gid,data):
        if self.dbType == "JSON":
            for p in self.db[type]:
                if mid_or_gid in self.db[type][p]:
                    self.db[type][p].remove(mid_or_gid)
            for d in data:
                if d not in self.db[type]:
                    self.db[type][d] = []
                self.db[type][d].append(mid_or_gid)
        else:
            try:
                self.conn.execute("DELETE FROM %s where mid_or_gid='%s'"%(type,mid_or_gid))
                for d in data:
                    self.conn.execute("INSERT INTO %s (name,mid_or_gid) VALUES ('%s','%s')"%(type,d,mid_or_gid))
                self.db.commit()
            except:
                self.db.rollback()
                raise Exception("postPermission failed")

class UserDatabase(object):
    def getUser(self,mid,var_name):
        '''Get UserVar from Database'''
        return self.ug_get("VarUser",mid,var_name)
            
    def deleteUser(self,mid):
        '''Delete UserData'''
        return self.ug_del("VarUser",mid)
    
    def postUser(self,mid,var_name,data,binary=False):
        '''Save VarUser to Database'''
        return self.ug_post("VarUser",mid,var_name,data,binary)
                
    def defaultUser(self,mid):
        '''Set specified mid user as default data'''
        return self.ug_default("VarUser",mid)
                
    def makeVarUser(self,var_name,data,default=None):
        '''Make newVar for Database'''
        return self.ug_makeVar("VarUser",var_name,data,default)
        
    def resetUser(self,mid):
        '''Reset VarUser in Database'''
        return self.ug_reset("VarUser",mid)
        
class GroupDatabase(object):
    def getGroup(self,gid,var_name):
        '''Get UserVar from Database'''
        return self.ug_get("VarGroup",gid,var_name)
            
    def deleteGroup(self,gid):
        '''Delete UserData'''
        return self.ug_del("VarGroup",gid)
    
    def postGroup(self,gid,var_name,data,binary=False):
        '''Save VarGroup to Database'''
        return self.ug_post("VarGroup",gid,var_name,data,binary)
                
    def defaultGroup(self,gid):
        '''Set specified gid Group as default data'''
        return self.ug_default("VarGroup",gid)
                
    def makeVarGroup(self,var_name,data,default=None):
        '''Make newVar for Database'''
        return self.ug_makeVar("VarGroup",var_name,data,default)
        
    def resetGroup(self,gid):
        '''Reset VarGroup in Database'''
        return self.ug_reset("VarGroup",gid)
        
class TracerDatabase(object):
    def getPermissionList(self):
        return self.ps_list("Permission")

    def getPermissionById(self,mid_or_gid):
        '''Get Permission by gid/mid'''
        return self.ps_get_by_id("Permission",mid_or_gid)
        
    def getPermissionByName(self,pName):
        '''Get Users by permissionName'''
        return self.ps_get_by_name("Permission",pName)
        
    def deletePermission(self,permissionName):
        '''Delete specified Permission'''
        return self.ps_delete("Permission",permissionName)

    def postPermission(self,mid_or_gid,permission):
        '''Post Permission of user_or_group'''
        return self.ps_post("Permission",mid_or_gid,permission)
        
    def addPermission(self,mid_or_gid,permissions):
        if type(permissions).__name__ != "list":
            permissions = [str(permissions)]
        pms = self.getPermissionById(mid_or_gid)
        pms += permissions
        pms = list(set(pms))
        self.postPermission(mid_or_gid,pms)
        
    def removePermission(self,mid_or_gid,permissions):
        if type(permissions).__name__ != "list":
            permissions = [str(permissions)]
        pms = self.getPermissionById(mid_or_gid)
        pms -= permissions
        pms = list(set(pms))
        self.postPermission(mid_or_gid,pms)
        
    def getScopeList(self):
        return self.ps_list("Scope")
        
    def getScopeById(self,mid_or_gid):
        '''Get ScopeData By gid/mid'''
        return self.ps_get_by_id("Scope",mid_or_gid)
        
    def getScopeByName(self,sName):
        '''Get Users By scopeName'''
        return self.ps_get_by_name("Scope",sName)
            
    def deleteScope(self,scopeName):
        '''Post specified Scope'''
        return self.ps_delete("Scope",scopeName)
        
    def postScope(self,mid_or_gid,scope):
        '''Post Scope of user_or_group'''
        return self.ps_post("Scope",mid_or_gid,scope)
        
class LogDatabase(object):
    def getLog(self,gid_or_mid,start_time,end_time):
        pass
        
    def postLog(self,gid_or_mid,data):
        pass

class Database(InternalProcess,UserDatabase,GroupDatabase,LogDatabase,TracerDatabase):
    def __init__(self,db):
        dbType = type(db).__name__
        #MySQL/SQLite3
        if dbType in ['connection',"Connection"]:
            if dbType == 'Connection':
                self.dbType = "SQLite"
            else:
                self.dbType = "MySQL"
            self.db = db
            self.conn = db.cursor()
        #Json
        elif type(db).__name__ in ['dict','collections.OrderedDict',"NoneType"]:
            self.dbType = "JSON"
            if type(db).__name__ == "NoneType":
                self.generate_db()
            else:
                self.db = db

    def generate_db(self):
        '''Call this if using new database.'''
        if self.dbType == "JSON":
            self.db = {"Permission":{},"Scope":{},"VarGroup":{"Default":{}},"VarUser":{"Default":{}},"Log":{}}
            return
        ct = [
            'CREATE TABLE "Log" ( `ID` INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE, `Time` TEXT, `Source` TEXT, `Message` TEXT )',
            'CREATE TABLE "Permission" ( `ID` INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE, `name` TEXT, `mid_or_gid` TEXT )',
            'CREATE TABLE "Scope" ( `ID` INTEGER NOT NULL UNIQUE, `name` TEXT, `mid_or_gid` TEXT, PRIMARY KEY(`ID`) )',
            'CREATE TABLE "VarGroup" ( `id` TEXT NOT NULL UNIQUE, PRIMARY KEY(`id`) )',
            'CREATE TABLE "VarUser" ( `id` TEXT NOT NULL UNIQUE, PRIMARY KEY(`id`) )',
            "INSERT INTO VarUser('id') VALUES ('Default')",
            "INSERT INTO VarGroup('id') VALUES ('Default')"
        ]
        for c in ct:
            self.conn.execute(c)
        self.db.commit()
        
    def file_import(self,filename):
        if self.dbType == "JSON":
            with open(filename,"r",encoding="utf_8_sig") as f:
                self.db = json.loads(f.read(),object_pairs_hook=OrderedDict)

    def file_export(self,filename="HookData"):
        if self.dbType == "JSON":
            with open(filename,"w",encoding="utf8") as f:
                json.dump(self.db, f, ensure_ascii=False, indent=4,separators=(',', ': '))
        else:
            self.conn.close()
        print("Database Save success")

if __name__ == "__main__":
    test_db = sqlite3.connect("database_test_sqlite2.db")
    dbp = DatabaseProcessor(db=test_db)
    # UserDatabase
    dbp.postUser("MID","Test",10)
    dbp.getUser("MID","Test")
    dbp.defaultUser("MID")
    dbp.resetUser("MID2")
    dbp.deleteUser("MID2")
    # GroupDatabase
    dbp.postGroup("GID","Test",10)
    dbp.getGroup("GID","Test")
    dbp.defaultGroup("GID")
    dbp.resetGroup("GID2")
    dbp.deleteGroup("GID2")
    # TracerDatabase
    dbp.postPermission("my_mid",["Developper","User"])
    dbp.getPermission("my_mid")
    dbp.deletePermission("Developper")
    dbp.postScope("my_mid",["HENTAI"])
    dbp.getScope("HENTAI")
    dbp.deleteScope("HENTAI")
    dbp.file_export()