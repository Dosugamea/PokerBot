import json

class Message(object):
    def replyMessage(self):
        if len(self.messages) == 0:
            raise Exception("Messages aren't specified.")
        if self.replyed:
            raise Exception("Reply token isn't specified.")
        self.replyed = True
        resp = self.reqPost("/bot/message/reply",params={"replyToken":self.replyToken,"messages": self.messages})
        self.messages = []
        if self.isOK(resp): return True
        else: print(resp.text)
        
    def sendMessage(self,to):
        if len(self.messages) == 0:
            raise Exception("Messages aren't specified.")
        resp = self.reqPost("/bot/message/push",params={"to":to,"messages": self.messages})
        self.messages = []
        if self.isOK(resp): return True
        else: print(resp.text)
        
    def chk_msg_len(self):
        if len(self.messages) > 4:
            raise Exception("You have to replyMessage before add.\n(Message Length is over than 5.)")
    
    def addMessage(self,text):
        self.chk_msg_len()
        self.messages.append({
            "type":"text",
            "text":text
        })
        
    def addSticker(self,packageId,stickerId):
        self.chk_msg_len()
        self.messages.append({
            "type":"sticker",
            "packageId":str(packageId),
            "stickerId":str(stickerId)
        })
        
    def addImage(self,original_url,preview_url):
        self.chk_msg_len()
        self.messages.append({
            "type":"image",
            "originalContentUrl": original_url,
            "previewImageUrl": preview_url
        })
        
    def addVideo(self,original_url,preview_url):
        self.chk_msg_len()
        self.messages.append({
            "type":"video",
            "originalContentUrl": original_url,
            "previewImageUrl": preview_url
        })
        
    def addAudio(self,original_url,duration):
        self.chk_msg_len()
        self.messages.append({
            "type":"audio",
            "originalContentUrl": original_url,
            "duration": duration
        })

    def addLocation(self,title,subtitle,latitude,longitude):
        self.chk_msg_len()
        self.messages.append({
            "type":"location",
            "title": title,
            "address": subtitle,
            "latitude": latitude,
            "longitude": longitude
        })
        
    def addImageMap(self,imagemap):
        pass
        
    def addTemplate(self,template,altText="テンプレートメッセージ"):
        self.chk_msg_len()
        self.messages.append({
            "type":"template",
            "altText": altText,
            "template": template
        })
        
    def addFlex(self,flex,altText="フレックスメッセージ"):
        self.chk_msg_len()
        self.messages.append({
            "type":"flex",
            "altText": altText,
            "contents": flex
        })