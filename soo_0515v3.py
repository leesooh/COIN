import time
import pyupbit
import datetime
import requests

access = ""
secret = ""
myToken = ""

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
        #print("noise{} = {}".format(i,noise[i]))
    avg = sum(noise,0.0) / len(noise)
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

def get_balance(ticker):
    """잔고 조회"""
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0

def get_current_price(ticker):
    """현재가 조회"""
    return pyupbit.get_orderbook(tickers=ticker)[0]["orderbook_units"][0]["ask_price"]

def print_info_to_slack(ticker1,ticker2):
    """k값, target price 조회"""
    df = pyupbit.get_ohlcv(ticker2, interval="day", count=1)
    open_price = int(df.iloc[0]['open'])
    #print("open :" + str(open_price))
    #post_message(myToken,"#stock", "* start({}) : ".format(ticker1) + str(open_price))
    k = get_k(ticker2) # find new k
    ma15_0 = get_ma15(ticker2)
    #post_message(myToken,"#stock", "* K({}) : ".format(ticker1) + str(k))
    target_price = get_target_price(ticker2, k)
    target_percent = (target_price - float(open_price)) / float(open_price) * 100
    print(target_percent)
    post_message(myToken,"#stock", "* Target({}) : {:d}({:.2f}%), ma15 : {}".format(ticker1,int(target_price),target_percent,int(ma15_0)))

def sell_coin(ticker1, ticker2):
    bal = get_balance(ticker1)
    if bal == None:
        bal = 0
    #print("sell {} bal : ".format(ticker1), bal)
    if bal > 0.00008:
        sell_result = upbit.sell_market_order(ticker2, bal * 0.9995)
        post_message(myToken,"#stock", "{} sell : ".format(ticker1) + str(sell_result))

# 로그인
upbit = pyupbit.Upbit(access, secret)
print("autotrade start")
# 시작 메세지 슬랙 전송
post_message(myToken,"#stock", "autotrade start")
# 초기 거래를 위한 생성 변수

k_XRP = get_k("KRW-XRP")
target_price_XRP = get_target_price("KRW-XRP", k_XRP)
ma15_XRP = get_ma15("KRW-XRP")
k_ADA = get_k("KRW-ADA")
target_price_ADA = get_target_price("KRW-ADA", k_ADA)
ma15_ADA = get_ma15("KRW-ADA")
k_ETC = get_k("KRW-ETC")
target_price_ETC = get_target_price("KRW-ETC", k_ETC)
ma15_ETC = get_ma15("KRW-ETC")
#print("xrp_ma" , ma15_XRP)
#print("Xrp_target" , target_price_XRP)
print_info_to_slack("ETC","KRW-ETC")
print_info_to_slack("XRP","KRW-XRP")
#print_info_to_slack("BTC","KRW-BTC")
print_info_to_slack("ETH","KRW-ETH")
print_info_to_slack("ADA","KRW-ADA")

#print("2")
while True:
    try:
        #time
        now = datetime.datetime.now() + datetime.timedelta(hours=9)
        start_time = get_start_time("KRW-XRP")
        end_time = start_time + datetime.timedelta(days=1)
       

        #  XRP,ADA BUY
        if start_time + datetime.timedelta(seconds=10) <= now < end_time - datetime.timedelta(seconds=10) :
            current_price_XRP = get_current_price("KRW-XRP") # 현재가 조회
            current_price_ADA = get_current_price("KRW-ADA") # 현재가 조회
            current_price_ETC = get_current_price("KRW-ETC") # 현재가 조회
            #print("c_xrp" , current_price_XRP)
            #print("3")
            if target_price_ADA < current_price_ADA and ma15_ADA < current_price_ADA:
                #print("4")
                krw = get_balance("KRW")
                if krw == None:
                    krw = 0
                if krw > 5000:
                    buy_result = upbit.buy_market_order("KRW-ADA", krw*0.9995)
                    post_message(myToken,"#stock", "ADA buy : " + str(buy_result))

            if target_price_XRP < current_price_XRP and ma15_XRP < current_price_XRP:
                #print("5")
                krw = get_balance("KRW")
                if krw == None:
                    krw = 0
                if krw > 5000:
                    buy_result = upbit.buy_market_order("KRW-XRP", krw*0.9995)
                    post_message(myToken,"#stock", "XRP buy : " + str(buy_result))

            if target_price_ETC < current_price_ETC and ma15_ETC < current_price_ETC:
                #print("5")
                krw = get_balance("KRW")
                if krw == None:
                    krw = 0
                if krw > 5000:
                    buy_result = upbit.buy_market_order("KRW-ETC", krw*0.9995)
                    post_message(myToken,"#stock", "ETC buy : " + str(buy_result))

        elif start_time + datetime.timedelta(seconds=1) <= now  < start_time + datetime.timedelta(seconds=10): ## info print to slack
            k_XRP = get_k("KRW-XRP") # find new k_XRP
            target_price_XRP = get_target_price("KRW-XRP", k_XRP)
            ma15_XRP = get_ma15("KRW-XRP")
            k_ADA = get_k("KRW-ADA") # find new k_ADA
            target_price_ADA = get_target_price("KRW-ADA", k_ADA)
            ma15_ADA = get_ma15("KRW-ADA")
            k_ETC = get_k("KRW-ETC")
            target_price_ETC = get_target_price("KRW-ADA", k_ETC)
            ma15_ETC = get_ma15("KRW-ETC")
            print_info_to_slack("XRP","KRW-XRP")
            #print_info_to_slack("BTC","KRW-BTC")
            print_info_to_slack("ETC","KRW-ETC")
            print_info_to_slack("ETH","KRW-ETH")
            print_info_to_slack("ADA","KRW-ADA")
        else:
            sell_coin("XRP","KRW-XRP")
            sell_coin("ADA","KRW-ADA")
            sell_coin("ETC","KRW-ETC")
            sell_coin("ETH","KRW-ETH")
            
        time.sleep(1)
    except Exception as e:
        print(e)
        post_message(myToken,"#stock", e)
        time.sleep(1)