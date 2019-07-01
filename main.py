from bottle import template,error,HTTPResponse
from bottle import route,run,response,request,static_file
import randBox,Casino,Poker
from lm_API import *
import sqlite3,requests

conn_db = sqlite3.connect("LINE_BOT.db", check_same_thread=False)
cl = LINE(channelAccessToken="TOKEN")
pcl = LinePay("CHANNEL_ID","CHANNEL_SECRET","REDIRECT_URL")
tracer = HooksTracer(cl,db=conn_db,prefix=["!","?","#","."])

class Operations(object):
    @tracer.Before("Operation")
    def set_Token(self,cl,op):
        if "replyToken" in op:
            self.cl.setReplyToken(op["replyToken"])

    @tracer.After("Command")
    def __add_exp(self,cl,msg):
        user = msg["source"]["userId"]
        msg_text = msg["message"]["text"]
        if any([msg_text.startswith(x) for x in self.maybe_cmds]):
            exp = self.getUser(user,"EXP")
            self.postUser(user,"EXP",exp+1)
            
    @tracer.Operation("join")
    def got_join(self,cl,msg):
        self.cl.addMessage("グループに招待いただきありがとうございます!\n私はトーク回数に応じてレベルを表示することができます\nコマンド一覧を確認するためには 「ヘルプ」といってください")
        self.cl.replyMessage()
    @tracer.Operation("message")
    def got_message(self,cl,msg):
        self.trace(msg,"Content")
    @tracer.Operation("follow")
    def got_follow(self,cl,msg):
        print("FOLLOW")
        self.cl.addMessage("友達登録いただきありがとうございます!\n下部のメニューからコマンドを確認できます!\nまたはその辺のマニュアルをご覧ください!")
        self.resetUser(msg["source"]["userId"])
        self.cl.replyMessage()
    @tracer.Operation("postback")
    def got_postback(self,cl,msg):
        print("POSTBACK")
        print(msg)
    @tracer.Operation("unfollow")
    def got_unfollow(self,cl,msg):
        print("UNFOLLOW")
        
class Contents(object):
    @tracer.Content("text")
    def got_text(self,cl,msg):
        self.trace(msg,"Command")
    @tracer.Content("image")
    def got_image(self,cl,msg):
        self.cl.addMessage("画像検索は今はできないんです、すみません > <")
        self.cl.replyMessage()
    @tracer.Content("video")
    def got_video(self,cl,msg):
        self.cl.addMessage("いい動画ですね!")
        self.cl.replyMessage()
    @tracer.Content("audio")
    def got_audio(self,cl,msg):
        self.cl.addMessage("いい音楽ですね!")
        self.cl.replyMessage()
    @tracer.Content("file")
    def got_file(self,cl,msg):
        self.cl.addMessage("ラブレターですか? 受け取れないです、ごめんなさい> <")
        self.cl.replyMessage()
    @tracer.Content("location")
    def got_location(self,cl,msg):
        self.cl.addMessage("今、あなたの後ろに居るよ")
        self.cl.replyMessage()
    @tracer.Content("sticker")
    def got_sticker(self,cl,msg):
        cl.addSticker(1,2)
        cl.replyMessage()

class Commands(object):
    @tracer.Command(alt=["ハロー","こんにちは","こん"],prefix=False)
    def hi(self,cl,msg):
        '''生存を確認します'''
        cl.addMessage("こんにちは!")
        cl.replyMessage()
        
    @tracer.Command()
    def help(self,cl,msg):
        '''このヘルプを表示します'''
        cl.addMessage(self.genHelp())
        cl.replyMessage()
        
    @tracer.Command()
    def Botについて(self,cl,msg):
        cl.addMessage()
        
    @tracer.Command()
    def ランダム(self,cl,msg):
        '''ランダムコマンド一覧を表示します'''
        cl.messages.append({"type":"text","text":"現在これらのランダムコマンドが実装されています","quickReply":{"items":[{"type":"action","action":{"type":"message","label":"サイコロ","text":"!dice"}},{"type":"action","action":{"type":"message","label":"コイン","text":"!coin"}},{"type":"action","action":{"type":"message","label":"おみくじ","text":"!omikuji"}},{"type":"action","action":{"type":"message","label":"ガチャ","text":"!gacha"}},{"type":"action","action":{"type":"message","label":"じゃんけん","text":"!janken"}}]}})
        cl.replyMessage()
        
    @tracer.Command()
    def ユーザー情報(self,cl,msg):
        '''ユーザー情報を表示します'''
        credit = self.getUser(msg["source"]["userId"],"Credit")
        exp = self.getUser(msg["source"]["userId"],"EXP")
        nick =self.getUser(msg["source"]["userId"],"Nickname")
        cl.addMessage("[あなたのユーザー情報]\nニックネーム:\n%s\nEXP:\n%s\nクレジット:\n%s"%(nick,exp,credit))
        cl.replyMessage()
        
    @tracer.Command(prefix=False)
    def Init(self,cl,msg):
        #self.postUser(msg["source"]["userId"],"atCasino",0)
        #self.postUser(msg["source"]["userId"],"atBet",0)
        #self.postUser(msg["source"]["userId"],"casinoStep",0)
        #self.postUser(msg["source"]["userId"],"casinoStep",0)
        #self.postUser(msg["source"]["userId"],"jankenStat",0)
        #self.postUser(msg["source"]["userId"],"jankened",0)
        #self.postUser(msg["source"]["userId"],"pCards","DummyText")
        #self.postUser(msg["source"]["userId"],"mCards","DummyText")
        #self.postUser(msg["source"]["userId"],"EXP",0)
        cl.addMessage("OK")
        cl.replyMessage()
        
    @tracer.Command()
    def EXPランキング(self,cl,msg):
        datas = self.conn.execute("SELECT (SELECT count(*) FROM VarUser as p1 WHERE p1.EXP > p.EXP) + 1 as rank,p.Nickname,p.EXP FROM VarUser as p ORDER BY rank;")
        tls = ["%s位 %s\n%s\n"%(d[0],d[1],d[2]) for d in datas]
        cl.addMessage("\n".join(tls))
        cl.replyMessage()
        

tracer.addClass(Operations())
tracer.addClass(Contents())
tracer.addClass(Commands())
tracer.addClass(randBox.randBox())
tracer.addClass(Casino.Casino())
tracer.addClass(Poker.Poker())
tracer.pcl = pcl
tracer.startup()

@route('/',method='GET')
def ret():
    return "HELLO WORLD!"

@route('/callback',method='POST')
def bot():
    data = request.json
    for d in data["events"]:
        tracer.trace(d,"Operation")
    return "OK"
    
@route('/confirm_pay',method="GET")
def recieve_pay():
    transaction_info = pcl.confirm(request.query['transactionId'])
    credit = tracer.getUser(transaction_info["userId"],"Credit")
    tracer.postUser(transaction_info["userId"],"Credit",credit+1204)
    cl.addMessage("ご購入ありがとうございます!\n1204クレジットが追加されました。")
    cl.sendMessage(transaction_info["userId"])
    return "購入が完了しました"
 
if __name__ == "__main__":
    run(host="localhost", port=8080,reload=False)