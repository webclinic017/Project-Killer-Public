//
//  KillerView.swift
//  Killer Interface
//
//  Created by Yush Raj Kapoor on 2/26/22.
//

import Foundation
import UIKit
import SwiftyJSON

class KillerView: UIViewController, UITableViewDelegate, UITableViewDataSource {
    
    @IBOutlet weak var tableView: UITableView!
    
    var accounts:[Account]!
    
    var coin:Coin?
    
    override func viewDidLoad() {
        super.viewDidLoad()
        if let storedRelevantCoin = UserDefaults.standard.data(forKey: "relevantCoin") {
            let relevantCoin = try? PropertyListDecoder().decode(Coin.self, from: storedRelevantCoin)
            if let relevantCoin = relevantCoin {
                coin = relevantCoin
            }
        }
        
        tableView.delegate = self
        tableView.dataSource = self
        
        getNames()
    }
    
    func getNames() {
        accounts = [Account.one, Account.two, Account.three, Account.four, Account.five]
        if Mock {
            accounts = [Account.testOne, Account.testTwo, Account.testThree, Account.testFour, Account.testFive]
        }
        
        self.tableView.reloadData()
    }
    
    func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
        return accounts.count
    }
    
    func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
        let cell = tableView.dequeueReusableCell(withIdentifier:"cell", for: indexPath)
        var content = cell.defaultContentConfiguration()
        content.text = accounts.sorted(by: {$0.strategyName() < $1.strategyName()})[indexPath.row].strategyName()
        
        cell.accessoryType = .disclosureIndicator
        cell.contentConfiguration = content
        return cell
    }
    
    func tableView(_ tableView: UITableView, didSelectRowAt indexPath: IndexPath) {
        tableView.deselectRow(at: indexPath, animated: true)
        let vc = UIStoryboard(name:"Main", bundle:nil).instantiateViewController(identifier: "BotView") as! BotView
        vc.account = accounts.sorted(by: {$0.strategyName() < $1.strategyName()})[indexPath.row]
        vc.coin = coin
        navigationController?.pushViewController(vc, animated: true)
    }
}
