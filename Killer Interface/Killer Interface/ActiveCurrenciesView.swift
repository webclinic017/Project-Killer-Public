//
//  ActiveCurrenciesView.swift
//  Killer Interface
//
//  Created by Yush Raj Kapoor on 5/15/22.
//

import Foundation
import UIKit
import SwiftyJSON

class ActiveCurrenciesView: UIViewController, UITableViewDelegate, UITableViewDataSource {
    
    
    @IBOutlet weak var tableView: UITableView!
    
    var currencies:[Coin] = []
    var isActive:[String:Bool] = [:]
    
    
    override func viewDidLoad() {
        super.viewDidLoad()
        
        title = "Active Currencies"
        
        tableView.dataSource = self
        tableView.delegate = self
        
        var activeCurrencies:[Coin] = []
        
        if let allFather = UserDefaults.standard.data(forKey: "entryCurrencies") {
            let coins = try? PropertyListDecoder().decode([Coin].self, from: allFather)
            if let coins = coins {
                activeCurrencies = coins
            }
        }
        
        if let allFather = UserDefaults.standard.data(forKey: "allAvailableCurrencies") {
            let coins = try? PropertyListDecoder().decode([Coin].self, from: allFather)
            if let coins = coins {
                currencies = coins
            }
            for i in currencies {
                if activeCurrencies.contains(where: {$0.ticker == i.ticker}) {
                    isActive[i.ticker] = true
                } else {
                    isActive[i.ticker] = false
                }
            }
            tableView.reloadData()
        }
        
        Task.init() {
            do {
                let coinGeckoData = try await ref.child("coin_gecko_data").getData()
                
                var temp:[Coin] = []
                if let val = coinGeckoData.value as? NSDictionary {
                    for i in val {
                        if let vl = i.value as? [String:Any] {
                            temp.append(Coin(displayName: vl["displayName"] as? String ?? "", geckoID: vl["geckoID"] as? String ?? "", ticker: vl["ticker"] as? String ?? "", marketCap: vl["marketCap"] as? Int ?? 0, geckoImageURL: vl["geckoImageURL"] as? String ?? ""))
                        }
                    }
                }
                temp.sort(by: {$0.displayName < $1.displayName})
                
                let activeCurrencies = try await ref.child("active_currencies").getData()
                
                if let val = activeCurrencies.value as? [String] {
                    for i in temp {
                        if val.contains(i.ticker.uppercased()) {
                            isActive[i.ticker] = true
                        } else {
                            isActive[i.ticker] = false
                        }
                    }
                }
                
                currencies = temp
                UserDefaults.standard.setValue(try! PropertyListEncoder().encode(currencies), forKey: "allAvailableCurrencies")
                DispatchQueue.main.async {
                    self.tableView.reloadData()
                }
            } catch {
                print("Error: \(error)")
            }
            if !currencies.isEmpty {
                await getImages(from: currencies)
            }
            DispatchQueue.main.async {
                self.tableView.reloadData()
            }
        }
    }
    
    
    func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
        return currencies.count
    }
    
    func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
        let cell = tableView.dequeueReusableCell(withIdentifier:"cell", for: indexPath) as! ActiveCurrenciesTableViewCell
        let coin = currencies[indexPath.row]
        cell.coin = coin
        cell.label.text = "\(coin.displayName) (\(coin.ticker.uppercased()))"
        cell.activeSwitch.setOn(isActive[coin.ticker] ?? false, animated: true)
        
        let path = getPath(fileName: coin.ticker + ".png") ?? ""
        cell.imgView.image = UIImage(contentsOfFile: path)
        
        
        
        return cell
    }
    
    func tableView(_ tableView: UITableView, didSelectRowAt indexPath: IndexPath) {
        tableView.deselectRow(at: indexPath, animated: true)
    }
    
}
