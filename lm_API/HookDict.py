from functools import wraps
import traceback

def Operation(type):
    def __wrapper(func):
        func.Operation = True
        @wraps(func)
        def __check(self, *args):
            if args[0].op["type"] == type:
                func(args[0],args[0].cl,args[1])
                return True
        return __check
    return __wrapper
    
def Content(type,sources=["User","Group"],permissions=["ALL"],**d_kwargs):
    def __wrapper(func):
        func.Content     = True
        func.sources     = sources
        func.permissions = permissions
        @wraps(func)
        def __check(self, *args):
            if args[0].msg['message']['type'] == type:
                if not args[0].scopeCheck(args[0].msg,sources):
                    return True
                if not args[0].permissionCheck(args[0].msg,permissions):
                    return True
                if args[0].userDataCheck(args[0].msg,**d_kwargs):
                    func(args[0],args[0].cl,args[1])
                    return True
        return __check
    return __wrapper
    
def Command(gprefix=[],alt=[],sources=["User","Group"],permissions=["ALL"],prefix=True,inpart=False,ignoreCase=False, **dkwargs):
    def __wrapper(func):
        func.Command     = True
        func.alt         = alt
        func.sources     = sources
        func.permissions = permissions
        func.prefix      = prefix
        func.inpart      = inpart
        func.ignoreCase  = ignoreCase
        if prefix and ignoreCase:
            cmds = [p+func.__name__.lower().replace("_"," ") for p in gprefix]
            cmds += [c for in_p in [[p+a.lower().replace("_"," ") for p in gprefix] for a in alt] for c in in_p]
        elif prefix:
            cmds = [p+func.__name__.replace("_"," ") for p in gprefix]
            cmds += [c for in_p in [[p+a.replace("_"," ") for p in gprefix] for a in alt] for c in in_p]
        elif ignoreCase:
            cmds = [func.__name__.lower().replace("_"," ")]
            cmds += [a.lower().replace("_"," ") for a in alt]
        else:
            cmds = [func.__name__.replace("_"," ")]
            cmds += [a.replace("_"," ") for a in alt]
        func.cmds = cmds
        @wraps(func)
        def __check(self, *args, **kwargs):
            chk = args[0].messageCheck(args[1],func.__name__,alt,sources,permissions,prefix,inpart,ignoreCase,func.cmds,**dkwargs)
            if chk == True:
                try:
                    #I DON'T KNOW WHY, BUT THIS WORKS
                    if len(args) == 2:
                        func(args[0],args[0].cl,args[1])
                    else:
                        func(args[0],args[0].cl,args[2])
                    return True
                except:
                    args[0].log("[Command] "+traceback.format_exc())
            elif chk == "break":
                return True
        return __check
    return __wrapper
    
def Before(type):
    '''
     type:
        0: Operation
        1: Content
        2: Command
    '''
    def __wrapper(func):
        func.type = type
        func.Before = True
        @wraps(func)
        def __bf(self, *args, **kwargs):
            func(args[0],args[0].cl,args[1])
        return __bf
    return __wrapper

def After(type):
    def __wrapper(func):
        func.type = type
        func.After = True
        @wraps(func)
        def __af(self, *args, **kwargs):
            func(args[0],args[0].cl,args[1])
        return __af
    return __wrapper
    
def Ticket(name,cnt):
    def __wrapper(func):
        func.Ticket = True
        func.name = name
        func.cnt = cnt
        @wraps(func)
        def __check(self, *args, **kwargs):
            #Check is it calling this
            if func.inpart:
                if not any([args[1].text.startswith(c) for c in func.cmds]):
                    return False
            else:
                if args[1].text not in func.cmds:
                    return False
            if args[0].checkTicket(args[0].msg,name,cnt):
                #I DON'T KNOW WHY, BUT THIS WORKS
                func(args[0],args[0],args[0].cl,args[1])
                return True
        return __check
    return __wrapper
    
def Minutely(self):
    def __wrapper(func):
        func.Schedule = True
        func.minutely = True
        @wraps(func)
        def __sc(self, *args, **kwargs):
            func(args[0],args[0].cl)
        return __sc
    return __wrapper
   
def Hourly(self):
    def __wrapper(func):
        func.Schedule = True
        func.hourly = True
        @wraps(func)
        def __sc(self, *args, **kwargs):
            func(args[0],args[0].cl)
        return __sc
    return __wrapper
   
def Daily(self):
    def __wrapper(func):
        func.Schedule = True
        func.daily = True
        @wraps(func)
        def __sc(self, *args, **kwargs):
            func(args[0],args[0].cl)
        return __sc
    return __wrapper
    
def Weekly(self):
    def __wrapper(func):
        func.Schedule = True
        func.weekly = True
        @wraps(func)
        def __sc(self, *args, **kwargs):
            func(args[0],args[0].cl)
        return __sc
    return __wrapper
    
def Monthly(self):
    def __wrapper(func):
        func.Schedule = True
        func.monthly = True
        @wraps(func)
        def __sc(self, *args, **kwargs):
            func(args[0])
        return __sc
    return __wrapper