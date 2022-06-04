//
//  credentials.swift
//  Killer Interface
//
//  Created by Yush Raj Kapoor on 3/15/22.
//

import Foundation
import SwiftyJSON

var keys_ = ["FINNHUB_API_KEY1", "FINNHUB_API_KEY2", "PHEMEX_API_KEY_1", "PHEMEX_API_SECRET_1", "PHEMEX_API_KEY_2", "PHEMEX_API_SECRET_2", "PHEMEX_API_KEY_3", "PHEMEX_API_SECRET_3", "PHEMEX_API_KEY_4", "PHEMEX_API_SECRET_4", "PHEMEX_API_KEY_5", "PHEMEX_API_SECRET_5", "PHEMEX_TESTNET_API_KEY_1", "PHEMEX_TESTNET_API_SECRET_1", "PHEMEX_TESTNET_API_KEY_2", "PHEMEX_TESTNET_API_SECRET_2", "PHEMEX_TESTNET_API_KEY_3", "PHEMEX_TESTNET_API_SECRET_3", "PHEMEX_TESTNET_API_KEY_4", "PHEMEX_TESTNET_API_SECRET_4", "PHEMEX_TESTNET_API_KEY_5", "PHEMEX_TESTNET_API_SECRET_5"]

func decodeCredentials() async {
    do {
        let baseURLString = try await ref.child("Obfuscation/url").getData().value as? String ?? ""
        
        try! await ref.child("Obfuscation/access").setValue(true)
        let endpoint = "/Decode"
        let tm = Int(Date().timeIntervalSince1970)
        try! await ref.child("Obfuscation/time").setValue(tm)
        
        let params:[String:Any] = [
            "keys": keys_,
            "passkey": "!!@#$#it'snotjustforbreakfastN@@nBr3@d&Butt3rCh!ck3n",
            "time": tm
        ]
        
        var queryItems:[URLQueryItem] = []
        for i in params {
            let item = URLQueryItem(name: i.key, value: "\(i.value)")
            queryItems.append(item)
        }
        
        var urlComps = URLComponents(string: baseURLString + endpoint)!
        urlComps.queryItems = queryItems
        let url = urlComps.url!
        let request = URLRequest(url: url)
        
        do {
            let (data, _) = try await URLSession.shared.data(for: request)
            let dict = try JSONDecoder().decode([String:String].self, from: data)
            var abort = false
            for i in keys_ {
                if !dict.keys.contains(i) {
                    abort = true
                }
            }
            if !abort {
                print("credentials updated")
                UserDefaults.standard.setValue(dict, forKey: "credentials")
            }
        } catch {
            print("Error: \(error)")
        }
    } catch {
        print("error")
    }
}



