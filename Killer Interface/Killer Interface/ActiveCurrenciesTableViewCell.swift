//
//  ActiveCurrenciesTableViewCell.swift
//  Killer Interface
//
//  Created by Yush Raj Kapoor on 5/15/22.
//

import UIKit

class ActiveCurrenciesTableViewCell: UITableViewCell {
    
    
    @IBOutlet weak var imgView: UIImageView!
    @IBOutlet weak var label: UILabel!
    @IBOutlet weak var activeSwitch: UISwitch!
    var coin: Coin!
    
    override func awakeFromNib() {
        super.awakeFromNib()
        // Initialization code
    }
    
    override func setSelected(_ selected: Bool, animated: Bool) {
        super.setSelected(selected, animated: animated)
        
        // Configure the view for the selected state
    }
    
    @IBAction func switchChanged(_ sender: Any) {
        if let allFather = UserDefaults.standard.data(forKey: "entryCurrencies") {
            do {
                var coins = try PropertyListDecoder().decode([Coin].self, from: allFather)
                if activeSwitch.isOn {
                    coins.append(coin)
                } else {
                    coins.removeAll(where: {$0.ticker == coin.ticker})
                }
                var symbols: [String] = []
                for i in coins {
                    symbols.append(i.ticker.uppercased())
                }
                ref.child("active_currencies").setValue(symbols)
                UserDefaults.standard.setValue(try! PropertyListEncoder().encode(coins), forKey: "entryCurrencies")
            } catch {
                print("Error: \(error)")
            }
        }
    }
}
