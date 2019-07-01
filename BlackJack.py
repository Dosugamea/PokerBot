import random

class BlackJack():
    num_dict = {
        11:"J",
        12:"Q",
        13:"K"
    }
    
    #共通なんだけどなぁ
    def b_makeCards(self):
        return [[m, n] for m in ['♣', '♦', '♥', '♠'] for n in range(1, 14)]
        
    

    #カードを数える(10以上は10として数える)
    def b_cnt_cards(self,cards,SB=False):
        tt = 0
        for card in cards:
            if card[1] < 11: tt += card[1]
            else: tt += 10
        if SB == False: return tt
        else:
            if tt == 21: return "ブラックジャック"
            elif tt > 21: return "%s バスト"%(tt)
            else: return str(tt)
    #カード一覧リセット
    def reset_cards(self):
        self.d_cards = self.draw()
        self.p_cards = self.draw()
        #ディーラーは17以上になるまで引く
        while True:
            if self.cnt_cards("D") < 18: self.d_cards.append(self.draw(1)[0])
            else: break
        
    #カードを引く
    def p_draw(self,yamafuda,cnt=2):
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
    
    #判定 引き分けなら 0 負けなら -1 勝ちなら 1が返る
    def decision(self,pcards,dcards):
        pcnt = self.cnt_cards(pcards)
        dcnt = self.cnt_cards(dcards)
        if pcnt == dcnt or (pcnt > 21 and dcnt > 21): return 0
        if (dcnt > 21 or pcnt > dcnt) and pcnt <= 21: return 1
        else: return -1
    
    #カードを追加する 21以下なら1 それ以外なら -1が返る
    def hit(self):
        self.p_cards.append(self.draw(1)[0])
        if self.cnt_cards("P") < 22: return 1
        else: return -1
    
    #一覧をそれぞれテキストで返す
    def conv_txt(self):
        toret = ["",""]
        for card in self.p_cards:
            if card[1] in self.num_dict: toret[0] += "%s%s "%(card[0],self.num_dict[card[1]])
            else: toret[0] += "%s%s "%(card[0],card[1])
        for card in self.d_cards:
            if card[1] in self.num_dict: toret[1] += "%s%s "%(card[0],self.num_dict[card[1]])
            else: toret[1] += "%s%s "%(card[0],card[1])
        toret = [ret[:len(ret)-1] for ret in toret]
        return toret


#blackjacker = BlackJack()
'''
print("あなたの手札")
print(blackjacker.conv_txt()[0])
while True:
    print("ヒットしますか? y/n")
    yn = input('>>')
    if yn == "y":
        gohit = blackjacker.hit()
        print("あなたの手札")
        print(blackjacker.conv_txt()[0])
        if gohit == -1: break
    elif yn == "n":
        break
print("\nショーダウン\n")
datas = blackjacker.conv_txt()
print("私 [%s] :"%(blackjacker.cnt_cards("D")))
print(datas[1])
print("あなた [%s] :"%(blackjacker.cnt_cards("P")))
print(datas[0])
print("")
print(blackjacker.decision())
'''