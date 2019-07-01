from lm_API.HookDict import Command
import random


#TODO: FlexMessage対応
class randBox(object):
    gp=["!","?","#","."]
    
    @Command(gprefix=gp,alt=["サイコロ","ダイス"])
    def dice(self,cl,msg):
        '''サイコロを投げます'''
        cl.addMessage(random.randint(1,6))
        cl.replyMessage()
        
    @Command(gprefix=gp,alt=["コイン","コイントス"])    
    def coin(self,cl,msg):
        '''コインを投げます'''
        if random.randint(1,2) == 1:
            cl.addMessage("表")
        else:
            cl.addMessage("裏")
        cl.replyMessage()
        
    @Command(gprefix=gp,alt=["おみくじ","今日の運勢"])
    def omikuji(self,cl,msg):
        '''おみくじを引きます (何度でも可)'''
        rnd = random.randint(1,100)
        per = {
            56 : "吉",
            81 : "小吉",
            91 : "中吉",
            98 : "大吉",
            101: "凶"
        }
        for k in per.keys():
            if rnd < k:
                result = per[k]
                break
        cl.addMessage("おみくじ結果: "+result)
        cl.replyMessage()
        
    @Command(gprefix=gp,alt=["ガチャ","ガチャガチャ"])
    def gacha(self,cl,msg):
        '''ガチャガチャを回します(1日1回)'''
        #UserDataをとって回してあるかを取る
        rnd = random.randint(1,100)
        per = {
            56 : "N  (5EXP)",
            81 : "R  (10EXP)",
            91 : "HR (15EXP)",
            98 : "SR (20EXP)",
            101: "SSR(30EXP)"
        }
        exp = {
            "N  (5EXP)" :5,
            "R  (10EXP)":10,
            "HR (15EXP)":15,
            "SR (20EXP)":20,
            "SSR(30EXP)":30,
        }
        for k in per.keys():
            if rnd < k:
                result = per[k]
                #経験値をガチャ扱いで入手する
                #self.getEXP(exp[result])
                break
        cl.addMessage("ガチャ結果: "+result)
        cl.replyMessage()
        
    @Command(gprefix=gp,alt=["じゃんけん"],sources=["User"],jankenStat=0)
    def janken(self,cl,msg):
        '''じゃんけんをします (1日1回)'''
        #if not self.getUser(self.userId,"jankened"):
        self.postUser(self.userId,"jankenStat",1)
        cl.addMessage("最初はグー。")
        cl.messages.append({"type":"text","text":"じゃんけん!","quickReply":{"items":[{"type":"action","action":{"type":"message","label":"パー","text":"パー"}},{"type":"action","action":{"type":"message","label":"グー","text":"グー"}},{"type":"action","action":{"type":"message","label":"チョキ","text":"チョキ"}}]}})
        cl.replyMessage()
        
    @Command(gprefix=gp,prefix=False,alt=["guu","choki","paa","グー","チョキ","パー"],sources=["User"],jankenStat=1)
    def _janken_end(self,cl,msg):
        jan = {
            "guu":1,"グー":1,
            "choki":2,"チョキ":2,
            "paa":3,"パー":3
        }
        jan2 ={
            1:"グー",
            2:"チョキ",
            3:"パー"
        }
        uHand = jan[msg["message"]["text"]]
        cHand = random.randint(1,3)
        cl.addMessage("ほいっ!")
        cl.addMessage(jan2[cHand])
        if uHand == cHand:
            #経験値追加(1EXP)
            cl.messages.append({"type":"text","text":"あいこで...","quickReply":{"items":[{"type":"action","action":{"type":"message","label":"パー","text":"パー"}},{"type":"action","action":{"type":"message","label":"グー","text":"グー"}},{"type":"action","action":{"type":"message","label":"チョキ","text":"チョキ"}}]}})
        elif (uHand == 1 and cHand == 2)\
          or (uHand == 2 and cHand == 3)\
          or (uHand == 3 and cHand == 1):
            cl.addMessage("あなたの勝ちですね")
            #経験値追加(10EXP)
            self.postUser(self.userId,"jankenStat",0)
            self.postUser(self.userId,"jankened",True)
        else:
            cl.addMessage("私の勝ちですね!")
            #経験値追加(5EXP)
            self.postUser(self.userId,"jankenStat",0)
            self.postUser(self.userId,"jankened",True)
        cl.replyMessage()