# lambda_function.py

import json

credentials = {
    "ALPACA_API_KEY": "{(,p&u7<r:{)|.|,433:",
    "ALPACA_API_SECRET": "8l7|5}c6o!q9DcwFwJ0jm'V9H1\,VWTyM}R=[WGI",
    "PAPER_1_KEY": ",(%6\"$060=u(1/7300&#",
    "PAPER_1_SECRET": "sZ@k-xpxoHEi%(L:F+LTMsVvP51Vt'>>[-|\>R'\"",
    "FIREBASE_MESSAGING_KEY": ",-./4fJ`d;-08H:3,^D_J1Zd}4SHH!]iTow`*_c&__\"Nj+-n^Q4\"U<1SZ/*.Yz3q:2dJbi>Dcw}BALqElXuBoY0vJ)V3t87Pgyz*$&~.le:-ne8t/2U-D{Y>7?7~>|)~DQ$B1I6-)(Cx4w5wSz;LE1OV",
    "FINNHUB_API_KEY1": "?sPMTpCDHvOKJX}MM$~V",
    "FINNHUB_API_KEY2": "?sLNvHKDHvOLX{TPN{aV",
    "FINNHUB_API_KEY3": "?tRIDsSDHvOvXS^`Z^ZV",
    "PHEMEX_API_KEY_1": "a]]dbbij_;<h=dlr@pi@tusnFvGMv!K||N}\"",
    "PHEMEX_API_SECRET_1": "7EG:Fc:bN.M6BlQau^knSN:Zpeacnx*X/h!n~1n$5U^RmRk-|V{0#kYDzsw:{&$e.PvL(!5I+WnL.\8]>S,xBTEVGB<",
    "PHEMEX_API_KEY_2": "-]3^_h35_;dlldlAlBi@oGunFIKHI|#N#PQ'",
    "PHEMEX_API_SECRET_2": "Me*^bNSPPD?NimgoKU9\":9@WCn:'Gt%yuY]lPq}(n2/*mwfT|VzZukZ6y8)={&%<#C~L(11F7!nI/9,v4=<_6.1U<2H",
    "PHEMEX_API_KEY_3": "2a0dfc8f_d;ikdlooBiuqvqnEKxyxw|{$$S#",
    "PHEMEX_API_SECRET_3": "#Zce<*fIKtle^mB3XwV6iL$=W#y*UH#x#ZiF0,{oe1\"Nxt&V|3jWtCYExp%9{&$N$-,L2G,n*!nJ.))M?=4b6>8{GXZ",
    "PHEMEX_API_KEY_4": ".[3cae6a_ef8idliomiAwqqnxu|L~}\"QMRT~",
    "PHEMEX_API_SECRET_4": "BVLXIa[Ac.AjLJ48tpS^YXlr{QDZ{ZcU'\"1Hlcg$!Lv8md.=}0s0tkY_&Hw;{&%=/C(L(!,V*WmX06J[>P4a81<fGE<",
    "PHEMEX_API_KEY_5": "13c5178g_i:eidlnomivqtGnEGtzv}}~}Q|U",
    "PHEMEX_API_SECRET_5": "]nA-a[[\'jPrtAzXzvsujMV<~\\sxRC\'Zk~g//2d(,O,&8x<c1pho3u{Z6z\"~G{&%<#f0L2.)G+GnJ;O0w3`KR6>WV:X<",
    "PHEMEX_TESTNET_API_KEY_1": "._e4be49_6:l<dlp>livpDtnyszz|}y$M&|U",
    "PHEMEX_TESTNET_API_SECRET_1": ",k:AY-C?hr*uxLd;Ss:}qApq?a^QWT'wHsmpc/F`'%*Smt*T|3~ZtkY\&^vG{&$g/xBL(.Bo*WmX.64s>`)U8>8d:2R",
    "PHEMEX_TESTNET_API_KEY_2": "\\0c`^c6i_dkl=dlp@qi@ADHntGyJIL\"Q}O|(",
    "PHEMEX_TESTNET_API_SECRET_2": "5=6Hobc\(5ue,W9V\ZW[=qV=wbne!+CU'0n2!(sNH4+*m,',rkj@\"3Z7&\"vH{&$b#{~L(1%E6Gmq.r1P2P5T6>N{:2Z",
    "PHEMEX_TESTNET_API_KEY_3": "/1b5^fh6_89<9dl=?liAnGDnxwzKywK\"|$S~",
    "PHEMEX_TESTNET_API_SECRET_3": "L$_W(^b>mKI2vk2pm;_tXjRc[NRA`bjwi\JNG${{zn'*mgo,}h.ZtkZ9x%vG{&%=/@~L2G(n6Wms.\,v>:<`8A<|;BR",
    "PHEMEX_TESTNET_API_KEY_4": "c\\0]dhf7_f9<kdlj@liAFqtnFIzvK{}!}{%&",
    "PHEMEX_TESTNET_API_SECRET_4": "4,@Ng*<TASJW4H6O3czPJx$;C@qoEzwx%`_og%2lp/V(xtn>|033\"3Y_x^vI{&%<.PvL2D%H6WmZ;LJ^2-,a7>-V<E<",
    "PHEMEX_TESTNET_API_KEY_5": "1b^a2gi4_i<fmdlAjnivrBrnHt{J|}L{\"%QR",
    "PHEMEX_TESTNET_API_SECRET_5": "Bcg&V0[cpVOEPUm;jmV|M]tr\"tTtnaS*tb}b~P0om^*:xRfR|{vZ\"{Y_x^%:{&$g#-,L210l,1nM:6Fv>`=SBW5X<E4",
}


def lambda_handler(event, context):
    if "queryStringParameters" in event and "keys" in event["queryStringParameters"]:
        keys = json.loads(event["queryStringParameters"]["keys"])
        return_values = {}

        for val in keys:
            if val in credentials:
                key = credentials[val]
                return_values[val] = key
            else:
                print(f"{val} NOT FOUND IN CREDENTIALS")

        return {
            'statusCode': 200,
            'body': json.dumps(return_values)
        }

    return {
        'statusCode': 400,
        'body': json.dumps("wrong format")
    }
