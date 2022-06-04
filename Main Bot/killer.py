# killer.py
# Copyright Yush Raj Kapoor
# Created 02/08/2022

import time
import json
from GeneralStrategy import (validate_order, has_existing_order, upload_data, Mock, api, log_potential_order)
import StrategyOne
import StrategyTwo
import StrategyThree
import StrategyFour
import StrategyFive
from Verdict import Verdict
import firebase as ref
import Account

Mock = Mock
Ticker = "BTCUSD"
fraction_to_use = 0.1
do_not_log = False


def perform_action_with(action, account, current_time, ticker):
    strategy = account.strategy()

    prevent = True
    if action != Verdict.put:
        print(f"ACTION -> {action.value.upper()}")
        prevent = validate_order(action, current_time, account, fraction_to_use, Ticker)

    if prevent:
        ref.update_firebase(ticker + "/verdicts/" + strategy + "/" + current_time, Verdict.put.value)
        print(f"\t{account.strategy()} -> No Action Required")
        return

    ref.update_firebase(ticker + "/verdicts/" + strategy + "/" + current_time, action.value)


def five_minute_data(ticker, relevant_data, current_time):
    upload_data(path=ticker + "/data/five_minute_data/" + current_time, data=relevant_data)
    print("Data Collection Complete - Engine Starting")

    strat_two = StrategyTwo.StrategyTwo(relevant_data, ticker)
    acct = strat_two.account()
    api.update_client(acct, Mock)
    if not requires_abort(acct, ticker):
        action_two = strat_two.decide
        perform_action_with(action_two, acct, current_time, ticker)

    strat_three = StrategyThree.StrategyThree(relevant_data, ticker)
    acct = strat_three.account()
    api.update_client(acct, Mock)
    if not requires_abort(acct, ticker):
        action_three = strat_three.decide
        perform_action_with(action_three, acct, current_time, ticker)


def fifteen_minute_data(ticker, relevant_data, current_time):
    upload_data(path=ticker + "/data/fifteen_minute_data/" + current_time, data=relevant_data)
    print("Data Collection Complete - Engine Starting")

    strat_one = StrategyOne.StrategyOne(relevant_data, ticker)
    acct = strat_one.account()
    api.update_client(acct, Mock)
    if not requires_abort(acct, ticker):
        action_one = strat_one.decide
        perform_action_with(action_one, acct, current_time, ticker)


def one_hour_data(ticker, relevant_data, current_time):
    upload_data(path=ticker + "/data/one_hour_data/" + current_time, data=relevant_data)
    print("Data Collection Complete - Engine Starting")

    strat_four = StrategyFour.StrategyFour(relevant_data, current_time, ticker)
    acct = strat_four.account()
    api.update_client(acct, Mock)
    if not requires_abort(acct, ticker):
        action_four = strat_four.decide
        perform_action_with(action_four, acct, current_time, ticker)

    strat_five = StrategyFive.StrategyFive(relevant_data, current_time, ticker)
    acct = strat_five.account()
    api.update_client(acct, Mock)
    if not requires_abort(acct, ticker):
        action_five = strat_five.decide
        perform_action_with(action_five, acct, current_time, ticker)


def requires_abort(account, ticker):
    exists = has_existing_order(account, f"{ticker}USD")
    if exists:
        print(f"\t{account.strategy()} -> No Action Required")
        return True
    return False


def start(interval, data):
    short_ticker = Ticker.replace("USD", "")
    print(short_ticker + ": " + interval + " MINUTE DATA ACTIVE")

    current_time = str(int(time.time()))
    strategies = []
    if interval == "5":
        five_minute_data(short_ticker, data, current_time)
        strategies = [StrategyTwo, StrategyThree]
    elif interval == "15":
        fifteen_minute_data(short_ticker, data, current_time)
        strategies = [StrategyOne]
    elif interval == "60":
        one_hour_data(short_ticker, data, current_time)
        strategies = [StrategyFour]

    if do_not_log:
        for strategy in strategies:
            account = strategy.account()
            strat = account.strategy()
            ref.delete_data(short_ticker + "/data/" + account.data() + "/" + current_time)
            ref.delete_data(short_ticker + "/verdicts/" + strat + "/" + current_time)
            ref.delete_data(short_ticker + "/bots/" + strat + "/verdict_ids/" + current_time)

    for strategy in strategies:
        account = strategy.account()
        strat = account.strategy()
        log_potential_order(short_ticker, do_not_log, strat)

    print("Script Completed. Fuck you.")


def validate(event):
    active_currencies = ref.get_data("active_currencies").json()

    if "Records" in event:
        sub_records = event["Records"]
        if type(sub_records) == list:
            records = sub_records[0]
            if "body" in records:
                params = json.loads(records["body"])
                if "symbol" not in params:
                    return {'statusCode': 405, 'body': json.dumps("Validation Error: 'symbol' parameter not found")}
                else:
                    sym = params["symbol"]
                    if sym not in active_currencies:
                        return {'statusCode': 405, 'body': json.dumps("Validation Error: Value for 'symbol' is invalid")}
                if "data_interval" not in params:
                    return {'statusCode': 405,
                            'body': json.dumps("Validation Error: 'data_interval' parameter not found")}
            else:
                return {'statusCode': 405, 'body': json.dumps("Validation Error: key 'body' does not exist")}
        else:
            return {'statusCode': 405, 'body': json.dumps("Validation Error: key 'Records' should be of list type")}
    elif "rawQueryString" in event:
        return None
    else:
        return {'statusCode': 405, 'body': json.dumps("Validation Error: key 'Records' does not exist")}


def lambda_handler(event, context):
    global Ticker
    print("Starting Killer Ignition")

    validation = validate(event)
    if validation is None:
        print("Validation Complete")
        json_obj = None
        if "queryStringParameters" in event:
            event["queryStringParameters"]["data"] = json.loads(event["queryStringParameters"]["data"])
            json_obj = event["queryStringParameters"]
        else:
            json_obj = json.loads(event['Records'][0]['body'])
        Ticker = json_obj["symbol"] + "USD"
        if "do_not_log" in json_obj:
            global do_not_log
            do_not_log = True
        interval = json_obj["data_interval"]
        data = json_obj["data"]
        start(interval, data)
        return {'statusCode': 200, 'body': json.dumps("Hello World!")}
    else:
        print(validation["body"])
        return validation


if __name__ == '__main__':
    avax_evt = {
        "Records": [{
            "body": '{"do_not_log": "True", "symbol": "AVAX", "data_interval": "5", "data": {"Time": [1652958900, 1652959200, 1652959500, 1652959800, 1652960100, 1652960400, 1652960700, 1652961000, 1652961300, 1652961600, 1652961900, 1652962200, 1652962500, 1652962800, 1652963100, 1652963400, 1652963700, 1652964000, 1652964300, 1652964600, 1652964900, 1652965200, 1652965500, 1652965800, 1652966100], "Ema25": [28.160792960215886, 28.172270424814666, 28.185941930598155, 28.187023320552143, 28.22879075743275, 28.263499160707156, 28.310153071421993, 28.357064373620304, 28.42729019103413, 28.472114022493045, 28.50272063614743, 28.554819048751476, 28.579063737309056, 28.613751142131438, 28.65961643889056, 28.68041517436052, 28.683460160948172, 28.7008863024137, 28.720818125304955, 28.739985961819958, 28.76921781091073, 28.802354902379136, 28.83294298681151, 28.89810121859524, 28.95747804793407], "Ema50": [28.454301725842686, 28.44864283463317, 28.444774488176968, 28.435175488640617, 28.44673723418412, 28.45588479362788, 28.472124605642474, 28.48968834659767, 28.520288803593843, 28.53949316423722, 28.552454216620077, 28.577063855183997, 28.588551547137566, 28.605863251171385, 28.62955488838035, 28.641337049620336, 28.644421871203853, 28.654836699784095, 28.666803888027857, 28.67869393163461, 28.696000051962663, 28.715764755807264, 28.734754373226586, 28.771822829178486, 28.80704546332835], "Ema100": [28.897534260382663, 28.885899918592905, 28.87528803901681, 28.861915998640235, 28.85930380064736, 28.85575323033751, 28.85603534458825, 28.857301971428086, 28.865474209617627, 28.86833610645688, 28.86836905484387, 28.874539964648942, 28.874450064358864, 28.877530261104233, 28.88411382029029, 28.885022457512264, 28.881754686076377, 28.88231399922338, 28.883852335872422, 28.88555823021158, 28.89020064149452, 28.896335282257006, 28.90234844498459, 28.917747485677964, 28.93264357507048], "Ema200": [29.59605130131603, 29.583254770954678, 29.570983579203887, 29.557341951550118, 29.54910969332574, 29.54046183568071, 29.53379057363414, 29.52768320474226, 29.525119192754776, 29.519993628647764, 29.513526030352764, 29.510207363384083, 29.50383714086285, 29.49912234344133, 29.496245504203106, 29.490611220579197, 29.4829434472401, 29.47724251741682, 29.47209582570123, 29.467099847336048, 29.46364611751181, 29.461022773058957, 29.458425531535983, 29.46063025261523, 29.462713533683733], "RSI": [42.53569859775125, 47.053314863049714, 47.7091845097095, 45.516514435210965, 53.36927478177994, 52.62718575685984, 55.088140396109196, 55.715956373554334, 59.79572785307775, 55.833129032082184, 53.84075865904541, 57.33667277695012, 53.16132944118235, 54.918487154696564, 56.80886070922437, 53.20955626986032, 50.710610278126644, 52.79088946608302, 53.32845452961821, 53.4384202156566, 55.08463122489398, 55.94609146077547, 55.94609146077547, 60.797758122040904, 60.653441953662416], "Open": [28.05, 28.05, 28.3, 28.35, 28.2, 28.72, 28.68, 28.87, 28.93, 29.27, 29, 28.86, 29.17, 28.88, 29.02, 29.2, 28.93, 28.74, 28.91, 28.95, 28.97, 29.11, 29.2, 29.2, 29.67], "Close": [28.05, 28.31, 28.35, 28.2, 28.73, 28.68, 28.87, 28.92, 29.27, 29.01, 28.87, 29.18, 28.87, 29.03, 29.21, 28.93, 28.72, 28.91, 28.96, 28.97, 29.12, 29.2, 29.2, 29.68, 29.67], "Low": [27.89, 28.05, 28.25, 28.14, 28.18, 28.58, 28.59, 28.76, 28.93, 28.93, 28.73, 28.8, 28.86, 28.85, 29.01, 28.88, 28.68, 28.73, 28.84, 28.89, 28.97, 29.11, 29.18, 29.2, 29.48], "High": [28.11, 28.44, 28.44, 28.38, 28.75, 28.92, 28.91, 28.99, 29.42, 29.4, 29, 29.36, 29.21, 29.1, 29.38, 29.28, 28.96, 28.94, 29.06, 29.03, 29.19, 29.24, 29.26, 29.79, 29.71], "Engulfing": ["None", "None", "None", "Bearish", "Bullish", "None", "Bullish", "None", "None", "None", "None", "Bullish", "None", "None", "None", "None", "None", "None", "None", "None", "None", "None", "None", "None", "None"], "Std": [0.16475756415144852, 0.18484326595009012, 0.20307661088902407, 0.20750744723841247, 0.26327710717966796, 0.24756839436843664, 0.29888804916576867, 0.34182204096921254, 0.41887145606181264, 0.4383316271781663, 0.4413914063803406, 0.4469118702610808, 0.40724550470070914, 0.37447105552846394, 0.33683726138799813, 0.3035359384555462, 0.2693633111739887, 0.18155010206677918, 0.1709009738332706, 0.15084378062705256, 0.1516158390056195, 0.15885061058595507, 0.15122212757446038, 0.2337475392125527, 0.27727183472123373], "Price": [28.05, 28.31, 28.35, 28.2, 28.73, 28.68, 28.87, 28.92, 29.27, 29.01, 28.87, 29.18, 28.87, 29.03, 29.21, 28.93, 28.72, 28.91, 28.96, 28.97, 29.12, 29.2, 29.2, 29.68, 29.67], "Volume": [12254.79, 51992.08, 19326.11, 23004.56, 22053.53, 46375.97, 17768.88, 21047.29, 55855.5, 37097.54, 16370.78, 26019.29, 19770.39, 19114.39, 21726.44, 14435.5, 17966.34, 10274.88, 7937.05, 7511.48, 17394.51, 6354.41, 6506.38, 74441.14, 10649.73]}}'
        }]
    }
    btc_evt = {
        "Records": [{
            "body": '{"do_not_log": "True", "symbol": "BTC", "data_interval": "5", "data": {"Time": [1652959800, 1652960100, 1652960400, 1652960700, 1652961000, 1652961300, 1652961600, 1652961900, 1652962200, 1652962500, 1652962800, 1652963100, 1652963400, 1652963700, 1652964000, 1652964300, 1652964600, 1652964900, 1652965200, 1652965500, 1652965800, 1652966100, 1652966400, 1652966700, 1652967000], "Ema25": [29110.2789029383, 29127.292833481508, 29144.619538598316, 29166.84418947537, 29183.879251823422, 29205.602386298546, 29221.974510429427, 29235.289548088702, 29251.564198235727, 29262.660798371442, 29277.230736958256, 29295.85991103839, 29304.616840958515, 29309.631699346326, 29318.547722473533, 29326.450974590956, 29337.083976545502, 29346.93213219585, 29357.87504510386, 29371.07465701895, 29393.098914171343, 29410.08899769663, 29423.22061325843, 29436.30518146932, 29454.504782894757], "Ema50": [29086.529652703888, 29096.13476436256, 29106.189871642462, 29119.027131578052, 29129.586851908327, 29142.790504774668, 29153.600288901154, 29163.069689336404, 29174.198721127133, 29182.88975167117, 29193.44583984093, 29206.22874808246, 29214.208012863543, 29220.310051574776, 29228.358284846356, 29235.924234460224, 29244.89504879512, 29253.530929234526, 29262.772461421406, 29273.23118842449, 29288.296239858824, 29301.06775986436, 29312.037651634386, 29323.06833196245, 29336.787220905102], "Ema100": [29081.93675749625, 29086.877811803253, 29092.138449193288, 29098.898875941934, 29104.62959126982, 29111.7909855021, 29117.863243214928, 29123.352485923544, 29129.758575311196, 29135.02711837434, 29141.305195238212, 29148.792419094883, 29153.958905845477, 29158.233184937646, 29163.526389196308, 29168.630619113213, 29174.49298309117, 29180.247775505206, 29186.365443316983, 29193.15959295427, 29202.352274281908, 29210.503120335732, 29217.835731814233, 29225.271063857515, 29234.135003187068], "Ema200": [29063.621430919487, 29066.28649130835, 29069.134784927173, 29072.76070746521, 29075.900401918294, 29079.78477602856, 29083.154479749668, 29086.258116767087, 29089.846195207218, 29092.890710677795, 29096.464633954634, 29100.673045557076, 29103.74794062616, 29106.395324301524, 29109.57089321395, 29112.67257586854, 29116.175137302685, 29119.647125986245, 29123.32416950877, 29127.365421553463, 29132.639297955917, 29137.42865817526, 29141.840313317796, 29146.332648508665, 29151.57212464291], "RSI": [56.26880318387636, 60.196403506250334, 60.90297282763583, 63.485842127891914, 61.146145110700154, 63.54754466073598, 61.14328544408688, 59.99341760838962, 61.65085197855266, 59.146513319561834, 60.95902477813009, 62.997153546419476, 57.89104847865962, 56.174254328442494, 57.979703219693015, 57.791419227169726, 59.194401395673786, 59.20833604024118, 60.00157014806177, 61.30681411605663, 65.06167684808808, 62.91264354787824, 61.30833702744066, 61.69072695990274, 64.03375772984177], "Open": [29280.4, 29227.64, 29336.26, 29347.91, 29436.11, 29388.3, 29481.41, 29418.3, 29393.11, 29449.63, 29393.99, 29451.28, 29514.75, 29409.83, 29366.01, 29424.17, 29420.87, 29457.92, 29465.12, 29490.29, 29524.21, 29657.39, 29612.93, 29578.53, 29595.75], "Close": [29222.82, 29331.46, 29352.54, 29433.54, 29388.3, 29466.28, 29418.44, 29395.07, 29446.86, 29395.82, 29452.07, 29519.41, 29409.7, 29369.81, 29425.54, 29421.29, 29464.68, 29465.11, 29489.19, 29529.47, 29657.39, 29613.97, 29580.8, 29593.32, 29672.9], "Low": [29207.58, 29217.66, 29309.17, 29318.18, 29338.7, 29386.64, 29407.31, 29345.62, 29380.14, 29342.8, 29386.35, 29450.9, 29322.54, 29365.37, 29365.38, 29383.19, 29405.93, 29457.92, 29465.12, 29487.9, 29524.21, 29594.36, 29580.8, 29544.78, 29560.57], "High": [29303.72, 29333.33, 29379.99, 29458.09, 29440.26, 29500, 29499.63, 29429.2, 29489.93, 29453.51, 29494.61, 29799.99, 29550.75, 29743.99, 29441.78, 29439.46, 29507.45, 29651.53, 29504.08, 29546.1, 29716.41, 29713.16, 29645.15, 29647.34, 29690.46], "Engulfing": ["Bearish", "Bullish", "None", "None", "None", "Bullish", "None", "None", "Bullish", "None", "Bullish", "None", "Bearish", "None", "Bullish", "None", "Bullish", "None", "None", "None", "None", "None", "None", "None", "None"], "Std": [97.41515268166178, 102.8877291779687, 89.09129070614017, 100.49217917202328, 105.68174386988521, 119.03029278304824, 124.30698815157383, 124.32503447083094, 121.75902214024175, 105.22162306513258, 90.59573746140651, 86.68643554625831, 78.24199021970428, 70.46586962808121, 48.68538129329127, 42.39369041953921, 38.90434110249003, 40.081261578148045, 40.81590856252235, 47.127781848971345, 73.45284897507072, 81.41218899563395, 85.52388848547919, 85.91607716175264, 96.21072679010642], "Price": [29222.82, 29331.46, 29352.54, 29433.54, 29388.3, 29466.28, 29418.44, 29395.07, 29446.86, 29395.82, 29452.07, 29519.41, 29409.7, 29369.81, 29425.54, 29421.29, 29464.68, 29465.11, 29489.19, 29529.47, 29657.39, 29613.97, 29580.8, 29593.32, 29672.9], "Volume": [7.51799, 11.46385, 13.53909, 17.094, 13.24454, 48.84518, 13.77569, 10.50224, 18.94116, 24.42607, 15.91087, 92.02855, 50.50585, 53.45349, 13.21187, 8.82331, 16.04399, 38.2104, 3.02396, 10.27112, 45.63727, 43.09536, 14.79942, 35.68518, 57.84105]}}'
        }]
    }
    avax_60_evt = {
        "Records": [{
            "body": '{"do_not_log": "True", "symbol": "AVAX", "data_interval": "60", "data": {"Time": [1653595200], "Ema200": [29.275509385961353], "RSI": [30.244682262191795], "K_Data": [41.21558406843086], "D_Data": [40.6943030346858], "Open": [24.08], "Close": [24.24], "High": [24.6], "Low": [24], "Volume": [170274.71], "TSV": [-654628.8562000002], "Supertrend_Direction10": [-1.0], "Supertrend_Direction11": [1.0], "Supertrend_Direction12": [1.0], "Supertrend_Value10": [25.07171689140498], "Supertrend_Value11": [23.440558559695788], "Supertrend_Value12": [22.55575254108532], "Price": [24.2917], "Bollinger_Low": [22.910344286584838], "Bollinger_Middle": [25.35], "Bollinger_High": [27.789655713415165], "Bollinger_Validation": ["False"]}}'
        }]
    }

    lambda_handler(avax_evt, None)


