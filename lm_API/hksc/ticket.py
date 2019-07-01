from functools import wraps
import inspect

class TicketHooks(object):
    def Ticket(self,name,cnt):
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
        
class Ticket(TicketHooks):
    def checkGroupTicket(self,msg,name,cnt):
        tickets = self.getGroup(msg.to,name)
        if tickets == None:
            self.error(msg,"NoTicket",[name,cnt])
            return False
        if tickets >= cnt:
            self.error(msg,"UseTicket",[name,cnt,tickets,tickets-cnt])
            tickets -= cnt
            self.postGroup(msg.to,name,tickets)
            return True
        else:
            self.error(msg,"NoTicket",[name,cnt])

    def checkTicket(self,msg,name,cnt):
        tickets = self.getUser(msg._from,name)
        if tickets == None:
            self.error(msg,"NoTicket",[name,cnt])
            return False
        if tickets >= cnt:
            self.error(msg,"UseTicket",[name,cnt,tickets,tickets-cnt])
            tickets -= cnt
            self.postUser(msg._from,name,tickets)
            return True
        else:
            self.error(msg,"NoTicket",[name,cnt])
