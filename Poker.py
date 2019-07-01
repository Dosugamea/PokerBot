from lm_API.HookDict import Command,Before
import random,pickle

class Poker(object):
    gp=["!","?","#","."]

    def __init__(self):
        self.p_display_dict = {
            "11":"J",
            "12":"Q",
            "13":"K"
        }
        self.p_id_dict = {
            "ノーペア": 0,
            "ワンペア": 1,
            "ツーペア": 2,
            "スリーカード": 3,
            "ストレート": 4,
            "フラッシュ": 5,
            "フルハウス": 6,
            "フォーカード": 7,
            "ストレートフラッシュ": 8,
            "ロイヤルストレートフラッシュ": 9
        }

    def p_makeCards(poker,self):
        return [[n, m] for m in ['♣', '♦', '♥', '♠'] for n in range(1, 14)]
        
    #カードを引く
    def p_draw(poker,self,yamafuda,cnt):
        cards = []
        if len(yamafuda) != 0:
            for i in range(cnt):
                c = random.choice(yamafuda)
                cards.append(c)
                yamafuda.remove(c)
            cards.sort(reverse=True)
            return yamafuda,cards
        else:
            return False,False
        
    #カード一覧表示
    def p_printCards(poker,self,cards):
        text = ""
        for l in cards:
            if l[0] in [11,12,13]: 
                text += "%s%s "%(l[1],poker.p_display_dict[str(l[0])])
            else:
                text += "%s%s "%(l[1],l[0])
        return text
        
    #カードを入れ替える
    def p_change(poker,self,id_text,yamafuda,cards):
        for i in id_text:
            if i in ["1","2","3","4","5"]:
                yamafuda,dr = self.p_draw(yamafuda,1)
                if dr != False:
                        cards.pop(int(i)-1)
                        cards.insert(int(i)-1,dr[0])
        return yamafuda,cards
        
    #カード結果表示
    def p_printYaku(poker,self,cards):
        cards.sort(reverse=True)
        return list(self.p_check_cards(cards).keys())[0]
        
    def all_in(poker,self,list,chk):
        for c in chk:
            if c not in list:
                return False
        return True
        
    #勝敗確認
    def p_check_win(poker,self,d_cards,p_cards):
        d_res = self.p_check_cards(d_cards)
        print(d_res)
        p_res = self.p_check_cards(p_cards)
        print(p_res)
        d_res_id = list(d_res.keys())[0]
        p_res_id = list(p_res.keys())[0]
        
        if poker.p_id_dict[d_res_id] > poker.p_id_dict[p_res_id]:
            return -1
        elif poker.p_id_dict[d_res_id] < poker.p_id_dict[p_res_id]:
            return 1
        else:
            if d_res_id == -1 and p_res_id == -1: return 0
            elif list(d_res.values())[0] > list(p_res.values())[0]: return -1
            elif list(d_res.values())[0] < list(p_res.values())[0]: return 1
            else: return 0

    #カード確認本体
    def p_check_cards(poker,self,cards):
        o_card = {}
        flash = 0
        straight = 1
        o_card_type = cards[0][1]
        o_card_num = o_card_ret = cards[0][0]
        for n_card in cards:
            #カード番号ごとの枚数辞書作成
            if n_card[0] not in o_card: o_card[n_card[0]] = 1
            else: o_card[n_card[0]] += 1
            #フラッシュかどうかのcntを増やしていく
            if o_card_type == n_card[1]: flash += 1
            #ストレートかどうかのcntを増やしていく
            if o_card_num - 1 == n_card[0]:
                o_card_num -= 1
                straight += 1
        #ストレート/ フラッシュなら ここで投げる
        if flash == 5 and self.all_in(o_card,[10,11,12,13,1]): return {"ロイヤルストレートフラッシュ": -1} 
        elif flash == 5 and straight == 5: return {"ストレートフラッシュ": o_card_ret}
        elif flash == 5: return {"フラッシュ": -1}
        elif straight == 5: return {"ストレート": o_card_ret}
        to_ret = {}
        #その他の確認
        for card in o_card:
            if o_card[card] == 4: return {"フォーカード":card}
            elif o_card[card] == 3: to_ret["スリーカード"] = card
            elif o_card[card] == 2:
                if "ワンペア" not in to_ret: to_ret["ワンペア"] = card
                else: to_ret["ペア2"] = card
        #フルハウスとツーペアはここで整形
        if self.all_in(to_ret,["ワンペア","スリーカード"]): return {"フルハウス":to_ret["ワンペア"]+to_ret["スリーカード"]}
        elif self.all_in(to_ret,["ワンペア","ペア2"]): return {"ツーペア":to_ret["ワンペア"]+to_ret["ペア2"]}
        elif to_ret != {}: return to_ret
        else: return {"ノーペア":-1}

    @Command(gprefix=gp,alt=["ポーカー"],atCasino=0,atBet=0)
    def p_cmd_poker(self,cl,msg):
        '''ポーカーを開始します'''
        #カジノゲーム共通
        self.kakeGuide(msg)
        if self.getUser(self.userId,"Credit") >= 100:
            self.postUser(self.userId,"atCasino",1)
        #フィールド初期化
        yamafuda = self.p_makeCards()
        yamafuda,pCards = self.p_draw(yamafuda,5)
        yamafuda,mCards = self.p_draw(yamafuda,5)
        self.postUser(self.userId,"yamafuda",yamafuda,True)
        self.postUser(self.userId,"pCards",pCards,True)
        self.postUser(self.userId,"mCards",mCards,True)
        cl.replyMessage()
    
    #ステップ1 手札を配る
    def p_guide(poker,self,_from):
        mls = []
        mls.append("[あなたの手札]")
        mls.append(self.p_printCards(pickle.loads(self.getUser(_from,"pCards"))))
        mls.append("")
        mls.append("カードを交換しますか?")
        mls.append(" 左から 1 2 3 4 5の番号で指定できます")
        mls.append(" 全て交換は 全交換")
        mls.append(" 交換しない場合は 交換しない")
        mls.append(" 降りる場合は 降りる")
        mls.append("と言ってください")
        self.cl.messages.append({"type":"text","text":"\n".join(mls),"quickReply":{"items":[{"type":"action","action":{"type":"message","label":"全交換","text":"全交換"}},{"type":"action","action":{"type":"message","label":"交換しない","text":"交換しない"}},{"type":"action","action":{"type":"message","label":"降りる","text":"降りる"}}]}})
        self.cl.replyMessage()
        
    #ステップ1.5 入力受付部
    @Command(gprefix=gp,alt=["全交換","降りる","1","2","3","4","5"],prefix=False,inpart=True,atBet=0,atCasino=1,casinoStep=1)
    def p_cmd_irekae(self,cl,msg):
        msg_text = msg["message"]["text"]
        _from = msg["source"]["userId"]
        if msg_text == "降りる":
            self.p_fall(_from)
        else:
            yamafuda = pickle.loads(self.getUser(_from,"yamafuda"))
            pCards = pickle.loads(self.getUser(_from,"pCards"))
            mCards = pickle.loads(self.getUser(_from,"mCards"))
            if msg_text == "全交換":
                msg_text = "12345"
            else:
                if len(msg_text) > 5:
                    msg_text = msg_text[:6]
            yamafuda,pCards = self.p_change(msg_text,yamafuda,pCards)
            self.p_showdown(_from,pCards,mCards)
        
    #ステップ2-0 ショーダウンした場合
    def p_showdown(poker,self,_from,pCards,mCards):
        bet = self.getUser(_from,"Bet")
        credit = self.getUser(_from,"Credit")
        mls = [
            "ショーダウン",
            "",
            "[あなたの手札]",
            self.p_printCards(pCards),
            self.p_printYaku(pCards),
            "[わたしの手札]",
            self.p_printCards(mCards),
            self.p_printYaku(mCards)
        ]
        self.cl.addMessage("\n".join(mls))
        result = self.p_check_win(mCards,pCards)
        #勝ち
        if result == 1:
            mls = [
                "あなたの勝ちです > <",
                "%s×2"%(bet),
                "=%sクレジット獲得"%(bet*2)
            ]
            self.cl.addMessage("\n".join(mls))
            self.postUser(_from,"Credit",credit+bet+bet)
        #負け
        elif result == -1:
            mls = [
                "わたしの勝ちですね",
                "%sクレジットは私が頂きます!"%(bet)
            ]
            self.cl.addMessage("\n".join(mls))
        #引き分け
        else:
            mls = [
                "引き分けですね",
                "%sクレジットはお返しします"%(bet)
            ]
            self.cl.addMessage("\n".join(mls))
            self.postUser(_from,"Credit",credit+bet)
        self.postUser(_from,"casinoStep",0)
        self.postUser(_from,"atCasino",0)
        self.postUser(_from,"Bet",0)
        self.cl.replyMessage()

    #ステップ2-1 降りた場合
    def p_fall(poker,self,_from):
        bet = self.getUser(_from,"Bet")
        credit = self.getUser(_from,"Credit")
        pCards = pickle.loads(self.getUser(_from,"pCards"))
        mCards = pickle.loads(self.getUser(_from,"mCards"))
        mls = [
            "結果は",
            "[あなたの手札]",
            self.p_printCards(pCards),
            self.p_printYaku(pCards),
            "[わたしの手札]",
            self.p_printCards(mCards),
            self.p_printYaku(mCards),
            "でした"
        ]
        self.cl.addMessage("\n".join(mls))
        self.postUser(_from,"casinoStep",0)
        self.postUser(_from,"atCasino",0)
        self.postUser(_from,"Bet",0)
        self.postUser(_from,"Credit",int(credit+(bet*0.75)))
        self.cl.replyMessage()
