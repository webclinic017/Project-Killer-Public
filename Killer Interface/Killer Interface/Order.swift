//
//  Order.swift
//  Killer Interface
//
//  Created by Yush Raj Kapoor on 3/16/22.
//

import Foundation
import SwiftyJSON
import CoreText

class Order {
    var time: Double!
    var price: Double!
    var side: Side!
    var status: Status!
    var type: OrderType!
    var takeProfitPrice: Double!
    var stopLossPrice: Double!
    var pnl: Double!
    var orderID: String!
    var symbol: String!
    
    init(time: Double, price: Double, side: Side, status: Status, type: OrderType, takeProfitPrice: Double, stopLossPrice: Double, pnl: Double, orderID: String, symbol: String) {
        self.time = time
        self.price = price
        self.side = side
        self.status = status
        self.type = type
        self.takeProfitPrice = takeProfitPrice
        self.stopLossPrice = stopLossPrice
        self.pnl = pnl
        self.orderID = orderID
        self.symbol = symbol
    }
    
    init(order: JSON, feeRate:Double=0.00075, decimals:Int=2) {
        self.time = Double((order["transactTimeNs"].int ?? 0) / 1000000000)
        self.price = Double(order["priceEp"].int ?? 0) / 10000
        self.side = Order.Side(rawValue: order["side"].string ?? "")!
        self.status = Order.Status(rawValue: order["ordStatus"].string!) ?? Order.Status(rawValue: "Unknown")
        self.type = Order.OrderType(rawValue: order["orderType"].string!) ?? Order.OrderType(rawValue: "Unknown")
        self.takeProfitPrice = Double(order["takeProfitEp"].int ?? 0) / 10000
        self.stopLossPrice = Double(order["stopLossEp"].int ?? 0) / 10000
        self.orderID = String(order["orderID"].string ?? "")
        let val = Double(order["cumValueEv"].double ?? 0.0) / 100000000
        self.pnl = (Double(order["closedPnlEv"].double ?? 0.0) / 10000) - (val * self.price * feeRate)
        self.symbol = String(order["symbol"].string ?? "")
        formatDecimals(decimals: decimals)
    }
    
    func formatDecimals(decimals: Int) {
        
    }
    
    func findClosestTime(times:[Double]) -> Double {
        var trackTime = 0.0
        
        var arr = times.sorted()
        
        while true {
            if arr.count == 1 {
                trackTime = arr[0]
                break
            }
            
            let first = arr.first!
            let last = arr.last!
            
            let tempArr = arr.split()
            
            if abs(self.time - first) <= abs(self.time - last) {
                arr = tempArr[0]
            } else {
                arr = tempArr[1]
            }
        }
        return trackTime
    }
    
    enum OrderType: String {
        case market = "Market"
        case stopLoss = "Stop"
        case takeProfit = "MarketIfTouched"
        case unknown = "Unknown"
    }

    enum Side: String {
        case buy = "Buy"
        case sell = "Sell"
    }

    enum Status: String {
        case new = "New"
        case partial_fill = "PartiallyFilled"
        case fill = "Filled"
        case canceled = "Canceled"
        case rejected = "Rejected"
        case triggered = "Triggered"
        case untriggered = "Untriggered"
        case deactivated = "Deactivated"
        case unknown = "Unknown"
    }
}



extension Array {
    func split() -> [[Element]] {
        let ct = self.count
        let half = ct / 2
        let leftSplit = self[0 ..< half]
        let rightSplit = self[half ..< ct]
        return [Array(leftSplit), Array(rightSplit)]
    }
}
