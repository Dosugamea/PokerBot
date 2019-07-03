from lm_API.HookDict import Command,Before
import uuid

class Casino(object):
    gp=["!","?","#","."]

    @Before("Command")
    def _set_userId(self,cl,msg):
        self.userId  = msg["source"]["userId"]
        self.userTxt = msg["message"]["text"]
        
    @Command(gprefix=gp)
    def 所持クレジット(self,cl,msg):
        credit = self.getUser(msg["source"]["userId"],"Credit")
        cl.addMessage("現在あなたは%sクレジット所有しています"%(credit))
        cl.replyMessage()
        
    @Command(gprefix=gp)
    def クレジット購入(self,cl,msg):
        credit = self.getUser(msg["source"]["userId"],"Credit")
        if credit <= 1000:
            data = {'productImageUrl':'https://example.com'}
            transaction_info = self.pcl.reserve("Casino Credit",'1204','JPY',uuid.uuid4().hex,msg["source"]["userId"],**data)
            cl.addMessage("購入リンクを発行しました\nこちらから購入をお願いします\n"+transaction_info["info"]["paymentUrl"]["web"])
        else:
            cl.addMessage("クレジットが1000未満のときのみ購入できます")
        cl.replyMessage()

    @Command(gprefix=gp,inpart=True)
    def ニックネーム_(self,cl,msg):
        txt = msg["message"]["text"]
        pre = self.getPrefix(txt)
        nick = txt.replace(pre+"ニックネーム ","")
        self.postUser(msg["source"]["userId"],"Nickname",nick)
        cl.addMessage("ニックネームを%sに変更しました"%(nick))
        cl.replyMessage()
        
    @Command(gprefix=gp)
    def クレジットランキング(self,cl,msg):
        datas = self.conn.execute("SELECT (SELECT count(*) FROM VarUser as p1 WHERE p1.Credit > p.Credit) + 1 as rank,p.Nickname,p.Credit FROM VarUser as p ORDER BY rank LIMIT 10;")
        tls = ["%s位 %s\n%s\n"%(d[0],d[1],d[2]) for d in datas]
        cl.addMessage("\n".join(tls))
        cl.replyMessage()
        
    @Command(gprefix=gp)
    def ランキング(self,cl,msg):
        cl.messages.append({"type":"text","text":"現在これらのランキングが実装されています\n\n・クレジットランキング\n クレジット所有数ランキングを表示します\n・EXPランキング\n コマンドを送った回数ランキングを表示します","quickReply":{"items":[{"type":"action","action":{"type":"message","label":"クレジットランキング","text":"!クレジットランキング"}},{"type":"action","action":{"type":"message","label":"EXPランキング","text":"!EXPランキング"}}]}})
        cl.replyMessage()
        
    #掛金設定ガイド(各ゲームの開始時に呼ぶ)
    def kakeGuide(casino,self,msg):
        _from = msg["source"]["userId"]
        credit= self.getUser(_from,"Credit")
        #掛金設定画面(共通)
        if credit >= 100:
            self.cl.messages.append({"type":"text","text":"いくらかけますか?\n最低100クレジット\n(全額,半分,n%%,数字 で指定)\n\n現在の所持クレジット: %s"%(credit),"quickReply":{"items":[{"type":"action","action":{"type":"message","label":"全額","text":"全額"}},{"type":"action","action":{"type":"message","label":"半分","text":"半分"}}]}})
            self.postUser(_from,"atBet",1)
        else:
            self.cl.addMessage("所持クレジットが足りません。\n100クレジット以上が必要です。\n必要な場合は「クレジット購入」と送ってください")
        
    #メッセージから金額を取りだす
    def getBet(casino,self,msg):
        msg_text = msg["message"]["text"]
        _from = msg["source"]["userId"]
        if msg_text in ["全額","全部","オール","オールイン"]:
            return self.getUser(_from,"Credit")
        elif msg_text in ["半額","半分","ハーフ","HALF"]:
            return self.getUser(_from,"Credit") // 2
        elif "％" in msg_text or "%" in msg_text:
            try:
                if "%" in cv:
                    cv = float(msg_text[:msg_text.find("%")])
                else:
                    cv = float(msg_text[:msg_text.find("％")])
                return int(self.getUser(_from,"Credit")*(cv/100))
            except:
                return None
        else:
            return int(msg_text)
        return None
    
    #掛金設定
    @Command(gprefix=gp,alt=["オールイン","半分","ハーフ","オールイン","全部","全額","オール","1","2","3","4","5","6","7","8","9"],prefix=False,inpart=True,atCasino=">0",atBet=1,casinoStep=0)
    def cmd_bet(self,cl,msg):
        credit = self.getBet(msg)
        if credit != None:
            if credit >= 100:
                nokori = self.getUser(self.userId,"Credit")-credit
                self.postUser(self.userId,"atBet",0)
                self.postUser(self.userId,"Bet",credit)
                self.postUser(self.userId,"casinoStep",1)
                self.postUser(self.userId,"Credit",nokori)
                cl.addMessage("%s クレジットを賭けます"%(credit))
                #各カジノゲームの初回メッセージを出す
                ctype = self.getUser(self.userId,"atCasino")
                #ポーカー
                if ctype == 1:
                    self.p_guide(self.userId)
                #ブラックジャック
                elif ctype == 2:
                    self.b_guide(self.userId)
            else:
                cl.addMessage("100クレジット以下にはできません")
                cl.replyMessage()
        else:
            cl.addMessage("入力が正しくありません")
            cl.replyMessage()
