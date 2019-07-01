from .Internal import Internal
from .Message import Message
from .RichMenu import RichMenu
from .Other import Other

class MessagingClient(Internal,Message,RichMenu,Other):
    def __init__(self,channelAccessToken=None,clientId=None,clientSecret=None):
        if (channelAccessToken == None and clientId == None and clientSecret == None) or channelAccessToken == None:
            raise ValueError("Need channelAccessToken, or clientId and clientSecret.")
        if clientId and clientSecret:
            self.channelAccessToken = self.genToken(clientId,clientSecret)
        else:
            self.channelAccessToken = channelAccessToken
        self.endpoint = "https://api.line.me/v2"
        #self.endpoint = "http://localhost:8080"
        self.post_headers = {
            "Authorization": "Bearer %s"%(channelAccessToken),
            "Content-Type": "application/json"
        }
        self.get_headers = {
            "Authorization": "Bearer %s"%(channelAccessToken)
        }
        self.messages = []
        self.replyToken = None
        self.replyed = False
    
    