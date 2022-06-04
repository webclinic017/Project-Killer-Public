//
//  Account.swift
//  Killer Interface
//
//  Created by Yush Raj Kapoor on 3/15/22.
//

import Foundation


enum Account:String, CaseIterable {
    case one = "one"
    case two = "two"
    case three = "three"
    case four = "four"
    case five = "five"
    case testOne = "testOne"
    case testTwo = "testTwo"
    case testThree = "testThree"
    case testFour = "testFour"
    case testFive = "testFive"
    
    
    func key() -> String {
        let creds:[String:String] = UserDefaults.standard.dictionary(forKey: "credentials") as? [String:String] ?? [:]
        switch self {
        case .one:
            return creds["PHEMEX_API_KEY_1"] ?? ""
        case .two:
            return creds["PHEMEX_API_KEY_2"] ?? ""
        case .three:
            return creds["PHEMEX_API_KEY_3"] ?? ""
        case .four:
            return creds["PHEMEX_API_KEY_4"] ?? ""
        case .five:
            return creds["PHEMEX_API_KEY_5"] ?? ""
        case .testOne:
            return creds["PHEMEX_TESTNET_API_KEY_1"] ?? ""
        case .testTwo:
            return creds["PHEMEX_TESTNET_API_KEY_2"] ?? ""
        case .testThree:
            return creds["PHEMEX_TESTNET_API_KEY_3"] ?? ""
        case .testFour:
            return creds["PHEMEX_TESTNET_API_KEY_4"] ?? ""
        case .testFive:
            return creds["PHEMEX_TESTNET_API_KEY_5"] ?? ""
        }
    }
    
    func secret() -> String {
        let creds:[String:String] = UserDefaults.standard.dictionary(forKey: "credentials") as? [String:String] ?? [:]
        switch self {
        case .one:
            return creds["PHEMEX_API_SECRET_1"] ?? ""
        case .two:
            return creds["PHEMEX_API_SECRET_2"] ?? ""
        case .three:
            return creds["PHEMEX_API_SECRET_3"] ?? ""
        case .four:
            return creds["PHEMEX_API_SECRET_4"] ?? ""
        case .five:
            return creds["PHEMEX_API_SECRET_5"] ?? ""
        case .testOne:
            return creds["PHEMEX_TESTNET_API_SECRET_1"] ?? ""
        case .testTwo:
            return creds["PHEMEX_TESTNET_API_SECRET_2"] ?? ""
        case .testThree:
            return creds["PHEMEX_TESTNET_API_SECRET_3"] ?? ""
        case .testFour:
            return creds["PHEMEX_TESTNET_API_SECRET_4"] ?? ""
        case .testFive:
            return creds["PHEMEX_TESTNET_API_SECRET_5"] ?? ""
        }
    }
    
    func strategy() -> String {
        switch self {
        case .one, .testOne:
            return "strategy_one"
        case .two, .testTwo:
            return "strategy_two"
        case .three, .testThree:
            return "strategy_three"
        case .four, .testFour:
            return "strategy_four"
        case .five, .testFive:
            return "strategy_five"
        }
    }
    
    func strategyName() -> String {
        switch strategy() {
        case "strategy_one":
            return "Classic"
        case "strategy_two":
            return "Scalper"
        case "strategy_three":
            return "Engulfer"
        case "strategy_four":
            return "The Works"
        case "strategy_five":
            return "BB Squeeze"
        default:
            return ""
        }
    }
    
    func isTestnet() -> Bool {
        switch self {
        case .testOne, .testTwo, .testThree, .testFour:
            return true
        default:
            return false
        }
    }
    
    func url() -> String {
        switch isTestnet() {
        case true:
            return "https://testnet-api.phemex.com"
        case false:
            return "https://api.phemex.com"
        }
    }
    
    func name() -> String {
        switch self {
        case .one:
            return "Live 1"
        case .two:
            return "Live 2"
        case .three:
            return "Live 3"
        case .four:
            return "Live 4"
        case .five:
            return "Live 5"
        case .testOne:
            return "Testnet 1"
        case .testTwo:
            return "Testnet 2"
        case .testThree:
            return "Testnet 3"
        case .testFour:
            return "Testnet 4"
        case .testFive:
            return "Testnet 5"
        }
    }
    
    func dataSource() -> String {
        switch self {
        case .one, .testOne:
            return "fifteen_minute_data"
        case .two, .testTwo, .three, .testThree:
            return "five_minute_data"
        case .four, .testFour, .five, .testFive:
            return "one_hour_data"
        }
    }
}
