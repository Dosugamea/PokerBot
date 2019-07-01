class RichMenu(object):
    def getRichMenu(self,rmid):
        resp = self.reqGet("/bot/richmenu/%s"%(rmid))
        if self.isOK(resp): return json.loads(resp.text)
        else: raise Exception(resp.text)

    def createRichMenu(self,rm):
        resp = self.reqPost("/bot/richmenu",params=rm)
        if self.isOK(resp): return json.loads(resp.text)["richMenuId"]
        else: raise Exception(resp.text)
        
    def deleteRichMenu(self,rmid):
        pass
    
    def getRichMenuIdOfUser(self,mid):
        resp = self.reqGet("/bot/user/%s/richmenu"%(mid))
        if self.isOK(resp): return json.loads(resp.text)["richMenuId"]
        else: raise Exception(resp.text)
        
    def linkRichMenuToUser(self,mid,rmid):
        resp = self.reqPost("/bot/user/%s/richmenu/%s"%(mid,rmid),headers=self.get_headers)
        if self.isOK(resp): return True
        else: raise Exception(resp.text)
        
    def unlinkRichMenuToUser(self,mid):
        pass