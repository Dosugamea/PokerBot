from concurrent.futures import ThreadPoolExecutor
from .hksc.database import Database
from .hksc.cmd      import Cmd
from .hksc.schedule import Schedule
from .hksc.ticket   import Ticket
from .hksc.utility  import Utility
from datetime import datetime
import inspect,traceback,types,glob

class HooksTracer(Utility,Database,Cmd,Schedule,Ticket):
    def __init__(self,cl,db=None,prefix=["?"],maxThreads=50):
        Database.__init__(self,db)
        Utility.__init__(self)
        self.cl     = cl
        self.pool   = ThreadPoolExecutor(maxThreads)
        self.prefix = prefix
        self.ofuncs = []
        self.obfunc = []
        self.oafunc = []
        self.cfuncs = []
        self.cbfunc = []
        self.cafunc = []
        self.mfuncs = []
        self.mbfunc = []
        self.mafunc = []
        self.sfuncs = []
        
    def startup(self):
        '''Startup this hook'''
        self.log("Initialize Hook...")
        self.cmd_startup()
        self.log("Initialize Schedule...")
        self.sc_startup()
        self.pool.submit(self.scheduler)
        self.log("Start Trace")
        
    def trace_thread(self,data,type):
        '''Call functions in tracer'''
        if type == "Command":
            self.msg = data["message"]
            #print("CheckIsCommand")
            if not self.isCommand(data["message"]): return
            #print("IsCommand OK")
            bfunc    = self.mbfunc
            afunc    = self.mafunc
            read     = self.mfuncs
        elif type == "Content":
            self.msg = data
            bfunc    = self.cbfunc
            afunc    = self.cafunc
            read     = self.cfuncs
        elif type == "Operation":
            self.op  = data
            bfunc    = self.obfunc
            afunc    = self.oafunc
            read     = self.ofuncs
        #print("Before Functions")
        for b in bfunc:
            if b(self,data): break
        #print("Main Functions")
        for func in read:
            try:
                if func(self,data): break
            except Exception as e:
                self.log("[%s] "%(type)+traceback.format_exc())
        #print("After Functions")
        for a in afunc:
            if a(self,data): break
        
    def trace(self,data,type):
        self.pool.submit(self.trace_thread,data,type)
            
    def log(self,text):
        '''Mini Logger'''
        #TODO: Save log to database
        print("[{}] {}".format(str(datetime.now()), text))
    
    def addFunc(self,_func,type,at):
        '''Add Function to HookTracer'''
        if type in ["Operation",0]:
            self.ofuncs.append(func)
        elif type in ["Content",1]:
            self.cfuncs.append(func)
        elif type in ["Command",2]:
            self.mfuncs.append(func)
        elif type in ["Schedule",3]:
            self.sfuncs.append(func)
        elif type in ["Native",4]:
            exec("self."+func.__name__+" = types.MethodType(func, self)")
        elif type in ["Before",5]:
            if at in ["Operation",0]:
                self.obfunc.append(func)
            elif at in ["Content",1]:
                self.cbfunc.append(func)
            elif at in ["Command",2]:
                self.mbfunc.append(func)
        elif type in ["After",6]:
            if at in ["Operation",0]:
                self.oafunc.append(func)
            elif at in ["Content",1]:
                self.cafunc.append(func)
            elif at in ["Command",2]:
                self.mafunc.append(func)
        else:
            raise TypeError("Func type parameter is invalid")
        
    def addClass(self,_class=None,folder=None):
        '''Add Class to HookTracer'''
        if folder == None:
            for func in [x[1] for x in inspect.getmembers(_class, predicate=inspect.ismethod)]:
                if hasattr(func, 'Operation'):
                    self.ofuncs.append(func)
                elif hasattr(func, 'Content'):
                    self.cfuncs.append(func)
                elif hasattr(func, 'Command'):
                    self.mfuncs.append(func)
                elif hasattr(func, 'Schedule'):
                    self.sfuncs.append(func)
                elif hasattr(func, 'Before'):
                    if func.type in ["Operation",0]:
                        self.obfunc.append(func)
                    elif func.type in ["Content",1]:
                        self.cbfunc.append(func)
                    elif func.type in ["Command",2]:
                        self.mbfunc.append(func)
                elif hasattr(func, 'After'):
                    if func.type in ["Operation",0]:
                        self.oafunc.append(func)
                    elif func.type in ["Content",1]:
                        self.cafunc.append(func)
                    elif func.type in ["Command",2]:
                        self.mafunc.append(func)
                else:
                    exec("self."+func.__name__+" = types.MethodType(func, self)")
        else:
            files = glob.glob('%s/*.py'%(folder))
            for f in files:
                if "HookDict" not in f:
                    with open(f) as c:
                        exec(c.read())
                    exec("self.addClass(%s(),5)"%(f.replace(".py","").replace(folder+"\\","")))
