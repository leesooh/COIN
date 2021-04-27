import time
import pyupbit
import datetime
import requests

access = "your-access"
secret = "your-secret"
myToken = "xoxb-your-token"

def post_message(token, channel, text):
    """슬랙 메시지 전송"""
    response = requests.post("https://slack.com/api/chat.postMessage",
        headers={"Authorization": "Bearer "+token},
        data={"channel": channel,"text": text}
    )

def get_k(ticker):
    """최적의 K값 구하기"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=20)
    noise = []
    for i in range(20):
        noise.append( 1 - abs(df.iloc[i]['open'] - df.iloc[i]['close'])\
             / (df.iloc[i]['high'] - df.iloc[i]['low']) )
       # print("noise{} = {}".format(i,noise[i]))
    avg = sum(noise,0.0) / len(noise)
    #print("avg = ",avg)
    return avg


def get_target_price(ticker, k):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=2)
    target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    return target_price

def get_start_time(ticker):
    """시작 시간 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    start_time = df.index[0]
    return start_time

def get_ma15(ticker):
    """15일 이동 평균선 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=15)
    ma15 = df['close'].rolling(15).mean().iloc[-1]
    return ma15

def get_balance(coin):
    """잔고 조회"""
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == coin:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0

def get_current_price(ticker):
    """현재가 조회"""
    return pyupbit.get_orderbook(tickers=ticker)[0]["orderbook_units"][0]["ask_price"]

# 로그인
upbit = pyupbit.Upbit(access, secret)
print("autotrade start")
# 시작 메세지 슬랙 전송
post_message(myToken,"#stock", "autotrade start")
k = get_k("KRW-XRP")

while True:
    try:
        now = datetime.datetime.now()
        start_time = get_start_time("KRW-XRP")
        end_time = start_time + datetime.timedelta(days=1)
        

        if start_time + datetime.timedelta(seconds=11)< now + datetime.timedelta(hours=9) < end_time - datetime.timedelta(seconds=10):
            target_price = get_target_price("KRW-XRP", k)
            #ma15 = get_ma15("KRW-XRP")
            current_price = get_current_price("KRW-XRP")
            if target_price < current_price : #and ma15 < current_price:
                krw = get_balance("KRW")
                if krw > 5000:
                    buy_result = upbit.buy_market_order("KRW-XRP", krw*0.9995)
                    post_message(myToken,"#stock", "XRP buy : " +str(buy_result))
        elif start_time < now + datetime.timedelta(hours=9) < start_time + datetime.timedelta(seconds=10):
            k = get_k("KRW-XRP")
            post_message(myToken,"#stock", "* New k : " +str(k))
            target_price = get_target_price("KRW-XRP", k)
            post_message(myToken,"#stock", "* target Price : " +str(target_price))
        else:
            btc = get_balance("XRP")
            if btc > 0.00008:
                sell_result = upbit.sell_market_order("KRW-XRP", btc*0.9995)
                post_message(myToken,"#stock", "XRP sell : " +str(sell_result))
        time.sleep(1)
    except Exception as e:
        print(e)
        post_message(myToken,"#stock", e)
        time.sleep(1)