//
//  Endpoints.swift
//  Killer Interface
//
//  Created by Yush Raj Kapoor on 3/15/22.
//

import Foundation
import SwiftyJSON

class Endpoints {
    static var shared = Endpoints()
    
    private func conditionalOrder(symbol: String) -> String {
        return symbol == "BTCUSD" ? "u\(symbol)":symbol
    }
    
    
    func getAllOrders(for symbol: String) async -> JSON {
        let formatted_symbol = conditionalOrder(symbol: symbol)
        let endpoint = "/exchange/order/list"
        let params:[String: Any] = [
            "symbol": formatted_symbol,
            "start": 1600000000000,
            "end": Int(Date().timeIntervalSince1970 * 1000),
            "limit": 200
        ]
        let result = await Phemex.shared.sendRequest(request: endpoint, parameters: JSON(params))
        return handleResultCode(result: result)
    }
    
    func getOrderBy(orderIDs ids: [String], symbol: String) async -> JSON {
        let formatted_symbol = conditionalOrder(symbol: symbol)
        let endpoint = "/exchange/order"
        let params:[String: Any] = [
            "symbol": formatted_symbol,
            "orderID": ids.joined(separator: ",")
        ]
        let result = await Phemex.shared.sendRequest(request: endpoint, parameters: JSON(params))
        return handleResultCode(result: result)
    }
    
    func getAccountPositions() async -> JSON {
        let endpoint = "/accounts/accountPositions"
        let params:[String:Any] = [
            "currency": "USD"
        ]
        let result = await Phemex.shared.sendRequest(request: endpoint, parameters: JSON(params))
        return handleResultCode(result: result)
    }
    
    func get24hData(symbol: String) async -> JSON {
        let formatted_symbol = conditionalOrder(symbol: symbol)
        let endpoint = "/md/ticker/24hr"
        let params:[String:Any] = [
            "symbol": formatted_symbol
        ]
        return await Phemex.shared.sendRequest(request: endpoint, parameters: JSON(params))
    }
    
    func getExecutedTrades(symbol:String, startTime:Int, endTime:Int) async -> JSON {
        let formatted_symbol = conditionalOrder(symbol: symbol)
        let endpoint = "/exchange/order/trade"
        let params:[String:Any] = [
            "symbol": formatted_symbol,
            "start": startTime,
            "end": endTime
        ]
        return await Phemex.shared.sendRequest(request: endpoint, parameters: JSON(params))
    }
    
    func getPriceData(symbol: String, resolution: String, from: TimeInterval, to: TimeInterval) async -> JSON {
        let formatted_symbol = conditionalOrder(symbol: symbol)
        let baseURL = "https://finnhub.io/api/v1"
        let endpoint = "/crypto/candle"
        let creds:[String:String] = UserDefaults.standard.dictionary(forKey: "credentials") as? [String:String] ?? [:]
        let params:[String:Any] = [
            "symbol": formatted_symbol,
            "resolution": resolution,
            "from": Int(from),
            "to": Int(to),
            "format": "json",
            "token": creds["FINNHUB_API_KEY1"] ?? ""
        ]
        
        var queryItems:[URLQueryItem] = []
        for i in params {
            let item = URLQueryItem(name: i.key, value: "\(i.value)")
            queryItems.append(item)
        }
        
        var urlComps = URLComponents(string: baseURL + endpoint)!
        urlComps.queryItems = queryItems
        let url = urlComps.url!
        let request = URLRequest(url: url)
        
        do {
            let (data, _) = try await URLSession.shared.data(for: request)
            let json = try! JSONDecoder().decode(JSON.self, from: data)
            return json
        } catch {
            print("Error: \(error)")
        }
        
        return JSON()
    }
    
    
    private func handleResultCode(result: JSON) -> JSON {
        let okCodes = [0, 10002, 11074]
        print(result)
        if result.contains(where: {$0.0 == "code"}) && okCodes.contains(result["code"].int!) {
            return result["data"]
        }
        return JSON()
    }
}
