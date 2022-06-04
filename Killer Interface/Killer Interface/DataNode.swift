//
//  DataNode.swift
//  Killer Interface
//
//  Created by Yush Raj Kapoor on 2/27/22.
//

import Foundation
import SwiftyJSON

class DataNode: Codable {
    var DData:Float!
    var KData:Float!
    var SMA9:Float!
    var SMA12:Float!
    var SMA26:Float!
    var EMA25:Float!
    var EMA50:Float!
    var EMA100:Float!
    var EMA200:Float!
    var MACD:Float!
    var Signal:Float!
    var RSI:Float!
    var Price:Float!
    var Engulfing:String!
    var Time:String!
    var TimeOfDecision:Double!
    var STD:Double!
    var Verdict:Verdict?
    var TSV:Float!
    var Supertrend10:_InternalData
    var Supertrend11:_InternalData
    var Supertrend12:_InternalData
    var Bollinger_Upper:Float!
    var Bollinger_Middle:Float!
    var Bollinger_Lower:Float!
    
    
    
    init(DData:Float, KData:Float, SMA9:Float, SMA12:Float, SMA26:Float, EMA25:Float, EMA50:Float, EMA100:Float, EMA200:Float, MACD:Float, Signal:Float, RSI:Float, Price:Float, Engulfing:String, TSV:Float, Supertrend10:(Int, Float)!, Supertrend11:(Int, Float)!, Supertrend12:(Int, Float)!, Time:String, TimeOfDecision:Double, STD:Double, Bollinger_Upper:Float, Bollinger_Middle:Float, Bollinger_Lower:Float) {
        self.DData = DData
        self.KData = KData
        self.SMA9 = SMA9
        self.SMA12 = SMA12
        self.SMA26 = SMA26
        self.EMA25 = EMA25
        self.EMA50 = EMA50
        self.EMA100 = EMA100
        self.EMA200 = EMA200
        self.MACD = MACD
        self.Signal = Signal
        self.RSI = RSI
        self.Price = Price
        self.Engulfing = Engulfing
        self.TSV = TSV
        self.Supertrend10 = _InternalData(direction: Supertrend10.0, value: Supertrend10.1)
        self.Supertrend11 = _InternalData(direction: Supertrend11.0, value: Supertrend11.1)
        self.Supertrend12 = _InternalData(direction: Supertrend12.0, value: Supertrend12.1)
        self.Time = Time
        self.TimeOfDecision = TimeOfDecision
        self.STD = STD
        self.Bollinger_Upper = Bollinger_Upper
        self.Bollinger_Middle = Bollinger_Middle
        self.Bollinger_Lower = Bollinger_Lower
    }
    
    init(node: JSON) {
        self.DData = node["d_data"].float
        self.KData = node["k_data"].float
        self.SMA9 = node["sma9"].float
        self.SMA12 = node["sma12"].float
        self.SMA26 = node["sma26"].float
        self.EMA25 = node["ema25"].float
        self.EMA50 = node["ema50"].float
        self.EMA100 = node["ema100"].float
        self.EMA200 = node["ema200"].float
        self.MACD = node["macd"].float
        self.Signal = node["signal"].float
        self.RSI = node["rsi"].float
        self.Price = node["price"].float
        self.Engulfing = node["engulfing"].string
        self.TSV = node["tsv"].float
        self.Supertrend10 = _InternalData(direction: node["supertrend_direction10"].int ?? 0, value: node["supertrend_value10"].float ?? 0.0)
        self.Supertrend11 = _InternalData(direction: node["supertrend_direction11"].int ?? 0, value: node["supertrend_value11"].float ?? 0.0)
        self.Supertrend12 = _InternalData(direction: node["supertrend_direction12"].int ?? 0, value: node["supertrend_value12"].float ?? 0.0)
        self.Time = node["time"].string
        self.TimeOfDecision = Double(node["time_of_decision"].string!)!
        self.STD = Double(node["std"].float ?? 0.0)
        self.Bollinger_Upper = node["bollinger_high"].float
        self.Bollinger_Middle = node["bollinger_middle"].float
        self.Bollinger_Lower = node["bollinger_low"].float
    }
    
    struct _InternalData: Codable {
          let direction: Int
          let value: Float
       }
    
    enum Verdict:String, Codable {
        case put = "put"
        case buy = "long"
        case sell = "short"
    }
    

}

