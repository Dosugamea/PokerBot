import json

class Config(object):
    def __init__(self):
        self.lang = "JA"
        self.ERROR_MESSAGES = {
            "EN":{
                "NotCommand"     : "<CmdName> is not command.\nCheck command spelling and try again.",
                "OutOfScope"     : "<CmdName> can not use in <WrongScope>.\nIt is useable in <TargetScope>.",
                "NoPermission"   : "You don't have permission to do it.\nPermission: <TargetPermission> is needed.",
                "NoTicket"       : "You don't have enough tickets to do it.\n<TargetTicket> x<NeedCount> are needed.",
                "UseTicket"      : "You used <TargetTicket> x<NeedCount>.\nRemaining Tickets: <NewCount>"
            },
            "JA":{
                "NotCommand"     : "<CmdName>というコマンドは存在しません",
                "OutOfScope"     : "<CmdName>は<WrongScope>では使用できません。\n<TargetScope>でのみ使用できます",
                "NoPermission"   : "あなたは<CmdName>を実行する権限がありません。\n権限<TargetPermission>が必要です",
                "NoTicket"       : "所持チケットが足りません。このコマンドには<TargetTicket> x<NeedCount>が必要です。",
                "UseTicket"      : "<TargetTicket>チケットを<NeedCount>枚消費しました\n<OldCount>枚→<NewCount>枚"
            }
        }

class Utility(Config):
    def __init__(self):
        Config.__init__(self)
        
    def genHelp(self,list=False,prefixNum=0):
        '''Make help by functions'''
        # Make CmdList
        ls  = [[x.__name__.replace("_"," "),x.__doc__,x.prefix] for x in self.mfuncs]
        ls  = [l for l in ls if l[1] != None]
        # Put Prefix
        ls2 = [[self.prefix[prefixNum]+l[0],l[1]] if l[2] else [l[0],l[1]] for l in ls]
        # Return List/Text
        if list:
            return ls2
        else:
            txt =  "[Command List]\n"
            txt += "\n".join(["%s : %s"%(l[0],l[1]) for l in ls2])
            return txt
        
    def getArg(self,cmd_names,msg_text,ignoreCase,splitKey=" "):
        #This can't use with mention by whitespace in displayName.
        if ignoreCase:
            msg_text = msg_text.lower()
        for c in cmd_names:
            if c in msg_text:
                s = msg_text.find(c)
                if s != -1:
                    arg = msg_text[len(c)+s+1:].split(splitKey)
                    if arg not in [[''],[]]:
                        arg = [a for a in arg if a[0] != "@"]
                    return arg
        return []

    def getMention(self,contentMetadata):
        ret = []
        if "MENTION" in contentMetadata:
            ms = json.loads(contentMetadata["MENTION"])
            for m in ms["MENTIONEES"]:
                ret.append(m["M"])
        return ret
        
    def getPrefix(self,msg_text):
        for x in self.prefix:
            if msg_text.startswith(x):
                return x
        return ""
        
    def error(self,msg,type,data=None):
        print(self.msg)
        errMsg = self.ERROR_MESSAGES[self.lang][type]
        errMsg = errMsg.replace("<CmdName>",msg["text"])
        if type == "OutOfScope":
            if msg.toType == 0:
                errMsg = errMsg.replace("<WrongScope>","1-1")
            elif msg.toType == 2:
                errMsg = errMsg.replace("<WrongScope>","Group")
            errMsg = errMsg.replace("<TargetScope>",str(data))
        elif type == "NoPermission":
            #errMsg = errMsg.replace("<WrongPermission>" ,str(self.getPermissionById(self.msg["source"]["userId"])))
            errMsg = errMsg.replace("<TargetPermission>"," or ".join(data))
        elif type == "NoTicket":
            errMsg = errMsg.replace("<TargetTicket>",str(data[0]))
            errMsg = errMsg.replace("<NeedCount>"   ,str(data[1]))
        elif type == "UseTicket":
            errMsg = errMsg.replace("<TargetTicket>",str(data[0]))
            errMsg = errMsg.replace("<NeedCount>"   ,str(data[1]))
            errMsg = errMsg.replace("<OldCount>"    ,str(data[2]))
            errMsg = errMsg.replace("<NewCount>"    ,str(data[3]))
        self.cl.addMessage(errMsg)
        self.cl.replyMessage()
