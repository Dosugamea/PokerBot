import requests
import json
import shelve

class LinePay(object):
    DEFAULT_ENDPOINT = 'https://sandbox-api-pay.line.me/'
    VERSION = 'v2'

    def __init__(self, channel_id, channel_secret, redirect_url):
        self.channel_id = channel_id
        self.channel_secret = channel_secret
        self.redirect_url = redirect_url
        self.headers = {
            'Content-Type': 'application/json',
            'X-LINE-ChannelId':self.channel_id,
            'X-LINE-ChannelSecret':self.channel_secret
        }

    def reserve(self, product_name, amount, currency, order_id, user_id=None, **kwargs):
        url = '{}{}/payments/request'.format(self.DEFAULT_ENDPOINT, self.VERSION)
        data = {**
                {
                    'productName':product_name,
                    'amount':amount,
                    'currency':currency,
                    'confirmUrl':'https://{}'.format(self.redirect_url),
                    'orderId':order_id,
                },
                **kwargs}
        resp = requests.post(url,headers=self.headers, data=json.dumps(data))
        resp = json.loads(resp.text)
        if int(resp['returnCode']) == 0:
            #Save to database (shelve for prototyping)
            with open('payments_data.json',"r",encoding="utf8") as f:
                store = json.loads(f.read())
            with open('payments_data.json',"w",encoding="utf8") as f:
                store["T"+str(resp['info']['transactionId'])] = {
                    'productName': product_name,
                    'amount': amount,
                    'currency': currency,
                    'userId': user_id
                }
                f.write(json.dumps(store))
        return resp

    def confirm(self, transaction_id):
        transaction_info = {}
        with open('payments_data.json','r',encoding="utf8") as f:
            store = json.loads(f.read())
            if "T"+str(transaction_id) in store:
                transaction_info = store["T"+str(transaction_id)]
            else:
                return {"Code":404}
        url = '{}{}/{}/confirm'.format(self.DEFAULT_ENDPOINT, self.VERSION, transaction_id)
        data = {
                'amount':transaction_info['amount'],
                'currency':transaction_info['currency'],
                }
        response = requests.post(url, headers=self.headers, data=json.dumps(data))
        return transaction_info