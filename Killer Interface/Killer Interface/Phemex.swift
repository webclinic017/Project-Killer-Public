//
//  Phemex.swift
//  Killer Interface
//
//  Created by Yush Raj Kapoor on 3/15/22.
//

import Foundation
import Crypto
import SwiftyJSON
import CommonCrypto

class Phemex {
    static var shared = Phemex()
    
    var account: Account = Account.one
    
    func setAccount(account: Account) {
        self.account = account
    }
    
    func sendRequest(request: String, parameters:JSON? = nil) async -> JSON {
        var queryItems:[URLQueryItem] = []
        for i in parameters ?? JSON() {
            let item = URLQueryItem(name: i.0, value: "\(i.1)")
            queryItems.append(item)
        }
        
        let headers = createHeaders(request: request, payload: queryItems)
        var urlComps = URLComponents(string: self.account.url() + request)!
        urlComps.queryItems = queryItems
        let url = urlComps.url!
        var request = URLRequest(url: url)
        request.allHTTPHeaderFields = headers
        
        do {
            let (data, _) = try await URLSession.shared.data(for: request)
            let json = try JSONDecoder().decode(JSON.self, from: data)
            return json
        } catch {
            print("Error: \(error)")
        }
        
        return JSON()
    }
    
    func createHeaders(request: String, payload: [URLQueryItem]) -> [String: String] {
        let expiration = String(Int(Date().timeIntervalSince1970) + 60)
        var queryString = ""
        for i in payload {
            let key = i.name
            let value = String(i.value!)
            queryString += key + "=" + value + "&"
        }
        if queryString != "" {
            queryString.removeLast()
        }
        let payloadb64 = (request + queryString + expiration)
        
        var tempReq = URLRequest(url: URL(string: "google.com")!)
        tempReq.addValue("application/json", forHTTPHeaderField: "Content-Type")
        tempReq.addValue(payloadb64.hmac(algorithm: CryptoAlgorithm.SHA256, key: self.account.secret()), forHTTPHeaderField: "x-phemex-request-signature")
        tempReq.addValue(expiration, forHTTPHeaderField: "x-phemex-request-expiry")
        tempReq.addValue(self.account.key(), forHTTPHeaderField: "x-phemex-access-token")
        
        return tempReq.allHTTPHeaderFields ?? [:]
    }
    
    
}

extension JSON {
    // serialize the json into a standard JSON string
    func serialize() -> String {
        let s0: String = self.rawString() ?? ""
        let s1: String = s0.replacingOccurrences(of: "\\/", with: "/")
        return s1
    }
}

extension String {
    func toBase64()->String{
        let data = self.data(using: .utf8)
        return data!.base64EncodedString()
    }
}
