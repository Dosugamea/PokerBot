import json

class Other(object):
    def getContent(self,msg_id):
        resp = self.reqGet("/bot/message/%s/content"%(msg_id))
        if self.isOK(resp): return resp.content
        else: raise Exception(resp.text)
    
    def getProfile(self,mid):
        resp = self.reqGet("/bot/profile/%s"%(mid))
        if self.isOK(resp): return json.loads(resp.text)
        else: raise Exception(resp.text)
        
    def leaveGroup(self,gid):
        resp = self.reqPost("/bot/group/%s/leave"%(gid),headers=self.get_headers)
        if self.isOK(resp): return True
        else: raise Exception(resp.text)
    
    def leaveRoom(self,roomid):
        resp = self.reqPost("/bot/room/%s/leave"%(roomid),headers=self.get_headers)
        if self.isOK(resp): return True
        else: raise Exception(resp.text)