import requests,json

class Internal(object):
    def isOK(self,resp):
        if resp.status_code == 200: return True
        else: return False
        
    def setReplyToken(self,token):
        self.replyToken = token
        self.replyed = False
        
    def reqPost(self,addr,headers=None,params=None):
        if headers == None: headers = self.post_headers
        if params == None: params = {}
        return requests.post(self.endpoint+addr,headers=headers,data=json.dumps(params))
    
    def reqGet(self,addr,headers=None,params=None):
        if headers == None: headers = self.get_headers
        if params == None: params = {}
        return requests.get(self.endpoint+addr,headers=headers,params=params)
        
    def reqDel(self,addr,headers=None,params=None):
        if headers == None: headers = self.get_headers
        if params == None: params = {}
        return requests.delete(self.endpoint+addr)
    
    def genToken(self,clientId,clientSecret):
        resp = reqPost("/oauth/accesstoken",params={"Content-Type": "application/x-www-form-urlencoded"})
        if isOK(resp): return json.loads(req.text)["access_token"]
        else: raise Exception(req.text)