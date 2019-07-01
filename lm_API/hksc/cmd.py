from functools import wraps
import traceback,json

class CmdHooks(object):
    def Operation(self,type):
        def __wrapper(func):
            func.Operation = True
            @wraps(func)
            def __check(self, *args):
                if args[0].op["type"] == type:
                    func(args[0],args[0].cl,args[1])
                    return True
            return __check
        return __wrapper
        
    def Content(self,type,sources=["User","Group"],permissions=["ALL"],**d_kwargs):
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
        
    def Command(self,alt=[],sources=["User","Group"],permissions=["ALL"],prefix=True,inpart=False,ignoreCase=False, **dkwargs):
        def __wrapper(func):
            func.Command     = True
            func.alt         = alt
            func.sources     = sources
            func.permissions = permissions
            func.prefix      = prefix
            func.inpart      = inpart
            func.ignoreCase  = ignoreCase
            if prefix and ignoreCase:
                cmds = [p+func.__name__.lower().replace("_"," ") for p in self.prefix]
                cmds += [c for in_p in [[p+a.lower().replace("_"," ") for p in self.prefix] for a in alt] for c in in_p]
            elif prefix:
                cmds = [p+func.__name__.replace("_"," ") for p in self.prefix]
                cmds += [c for in_p in [[p+a.replace("_"," ") for p in self.prefix] for a in alt] for c in in_p]
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
        
    def Before(self,type):
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

    def After(self,type):
        def __wrapper(func):
            func.type = type
            func.After = True
            @wraps(func)
            def __af(self, *args, **kwargs):
                func(args[0],args[0].cl,args[1])
            return __af
        return __wrapper
        
class Cmd(CmdHooks):
    def cmd_startup(self):
        # Make Cmd List
        self.maybe_cmds = []
        for c in self.mfuncs:
            # Add function name
            if c.prefix and c.ignoreCase:
                self.maybe_cmds.append([k+c.__name__.lower().replace("_"," ") for k in self.prefix])
            elif c.prefix:
                self.maybe_cmds.append([k+c.__name__.replace("_"," ") for k in self.prefix])
            elif c.ignoreCase:
                self.maybe_cmds.append([c.__name__.lower().replace("_"," ")])
            else:
                self.maybe_cmds.append([c.__name__.replace("_"," ")])
            # Add alt name
            for a in c.alt:
                if c.prefix and c.ignoreCase:
                    self.maybe_cmds.append([k+a.lower().replace("_"," ") for k in self.prefix])
                elif c.prefix:
                    self.maybe_cmds.append([k+a.replace("_"," ") for k in self.prefix])
                elif c.ignoreCase:
                    self.maybe_cmds.append([a.lower().replace("_"," ")])
                else:
                    self.maybe_cmds.append([a.replace("_"," ")])
        self.maybe_cmds  = [c for in_p in self.maybe_cmds for c in in_p]
            
    def isCommand(self,data):
        # Check IsCommand
        if data["text"]         in self.maybe_cmds\
        or data["text"].lower() in self.maybe_cmds\
        or any([data["text"].startswith(c) for c in self.maybe_cmds])\
        or any([data["text"].lower().startswith(c) for c in self.maybe_cmds]):
            return True
        else:
            if self.getPrefix(data["text"]) != "":
                self.error(self.msg,"NotCommand")
        return False
            
    def scopeCheck(self,msg,sources):
        '''Check Scope (For Content/Command)'''
        #From Group
        if msg["source"]["type"] == "group":
            # If accept AllGroup or mid in sources
            if "Group" in sources or msg["source"]["groupId"] in sources:
                return True
            # If groupType registered
            chk_ls = [g for g in self.getScopeList() if g in sources]
            if chk_ls != []:
                if [g for g in chk_ls if msg["source"]["groupId"] in self.getScopeByName(g)] != []:
                    return True
        #From 1-1
        elif msg["source"]["type"] == "user":
            # If accept from ALL or mid in sources
            if "User" in sources or msg["source"]["userId"] in sources:
                return True
            # If userType registered
            chk_ls = [u for u in self.getScopeList() if u in sources]
            if chk_ls != []:
                if [u for u in chk_ls if msg["source"]["userId"] in self.getScopeByName(u)] != []:
                    return True
        return False
        
    def permissionCheck(self,msg,permissions):
        '''Check Permission (For Content/Command)'''
        if permissions in [[],["ALL"]]:
            return True
        elif [p for p in permissions if msg["source"]["userId"] in self.getPermissionByName(p)] != []:
            return True
        return False
        
    def userDataCheck(self,msg,**kwargs):
        '''Check UserDatas'''
        #print("CheckingUserData")
        print(kwargs,msg)
        for k in kwargs:
            # a=1
            if type(kwargs[k]).__name__ == "int":
                if self.getUser(msg["source"]["userId"],k) != kwargs[k]:
                    return False
            # a=">1"
            elif ">" in kwargs[k]:
                if self.getUser(msg["source"]["userId"],k) < int(kwargs[k][1:]):
                    print("FAILED")
                    return False
            elif "<" in kwargs[k]:
                if self.getUser(msg["source"]["userId"],k) > int(kwargs[k][1:]):
                    return False
            # a=">=1"
            elif ">=" in kwargs[k]:
                if self.getUser(msg["source"]["userId"],k) <= int(kwargs[k][2:]):
                    return False
            elif "<=" in kwargs[k]:
                if self.getUser(msg["source"]["userId"],k) >= int(kwargs[k][2:]):
                    return False
            # a="1"
            else:
                if self.getUser(msg["source"]["userId"],k) != int(kwargs[k][1:]):
                    return False
            #TODO: ADD String check
        return True
        
    def groupDataCheck(self,msg,**kwargs):
        '''Check GroupDatas'''
        for k in kwargs:
            # a=1
            if type(kwargs[k]).__name__ == "int":
                if self.getGroup(msg["source"]["groupId"],k) != kwargs[k]:
                    return False
            # a=">1"
            elif ">" in kwargs[k]:
                if self.getGroup(msg["source"]["groupId"],k) < int(kwargs[k][1:]):
                    return False
            elif "<" in kwargs[k]:
                if self.getGroup(msg["source"]["groupId"],k) > int(kwargs[k][1:]):
                    return False
            # a=">=1"
            elif ">=" in kwargs[k]:
                if self.getGroup(msg["source"]["groupId"],k) <= int(kwargs[k][2:]):
                    return False
            elif "<=" in kwargs[k]:
                if self.getGroup(msg["source"]["groupId"],k) >= int(kwargs[k][2:]):
                    return False
            # a="1"
            else:
                if self.getGroup(msg["source"]["groupId"],k) != int(kwargs[k]):
                    return False
            #TODO: ADD String check
        return True
        
    def messageCheck(self,msg,funcName,alt,sources,permissions,prefix,inpart,ignoreCase,cmds,**kwargs):
        '''Check Message (For Command)'''
        # Convert Case (DON'T change msg.text directly)
        if ignoreCase:
            msg_text = msg["message"]["text"].lower()
        else:
            msg_text = msg["message"]["text"]
        # Check IsCallThisFunction
        if inpart:
            if not any([msg_text.startswith(c) for c in cmds]):
                return False
        else:
            if msg_text not in cmds:
                return False
        print("CallingMe: %s"%(msg_text))
        # Check Scope
        if not self.scopeCheck(msg,sources):
            self.error(msg,"OutOfScope",sources)
            return "break"
        print("ScopeOK")
        # Check Permission
        if not self.permissionCheck(msg,permissions):
            self.error(msg,"NoPermission",permissions)
            return "break"
        print("PermissionOK")
        # Check User/Group data
        if "groupData" in kwargs:
            if not self.groupDataCheck(msg,**kwargs):
                return False
        else:
            if not self.userDataCheck(msg,**kwargs):
                return False
        print("UserDataOK")
        # Do Function
        return True
