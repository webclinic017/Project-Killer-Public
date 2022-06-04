//
//  EntryView.swift
//  Killer Interface
//
//  Created by Yush Raj Kapoor on 5/12/22.
//

import Foundation
import UIKit


class EntryView: UIViewController, UICollectionViewDelegate, UICollectionViewDataSource {
    
    @IBOutlet weak var collectionView: UICollectionView!
    
    private let sectionInsets = UIEdgeInsets.zero
    
    var currencies:[Coin] = []
    
    override func viewDidAppear(_ animated: Bool) {
        super.viewDidAppear(animated)
       loadCache()
    }
    
    override func viewDidLoad() {
        super.viewDidLoad()
        
        collectionView.delegate = self
        collectionView.dataSource = self
        
        loadCache()
        
        Task.init() {
            let coinGeckoData = try await ref.child("coin_gecko_data").getData()
            
            do {
                var tempCoins:[Coin] = []
                if let val = coinGeckoData.value as? NSDictionary {
                    for i in val {
                        if let vl = i.value as? [String:Any] {
                            tempCoins.append(Coin(displayName: vl["displayName"] as? String ?? "", geckoID: vl["geckoID"] as? String ?? "", ticker: vl["ticker"] as? String ?? "", marketCap: vl["marketCap"] as? Int ?? 0, geckoImageURL: vl["geckoImageURL"] as? String ?? ""))
                        }
                    }
                }
                
                let data = try await ref.child("active_currencies").getData()
                if let val = data.value as? [String] {
                    var temp:[Coin] = []
                    for sym in val {
                        temp.append(tempCoins.first(where: {$0.ticker.uppercased() == sym})!)
                    }
                    temp.sort(by: {$0.displayName < $1.displayName})
                    
                    currencies = temp
                    collectionView.reloadData()
                }
                UserDefaults.standard.setValue(try! PropertyListEncoder().encode(currencies), forKey: "entryCurrencies")
            } catch {
                print("Error: \(error)")
            }
            if !currencies.isEmpty {
                await getImages(from: currencies)
            }
            DispatchQueue.main.async {
                self.collectionView.reloadData()
            }
        }
    }
    
    
    func loadCache() {
        if let allFather = UserDefaults.standard.data(forKey: "entryCurrencies") {
            let coins = try? PropertyListDecoder().decode([Coin].self, from: allFather)
            if let coins = coins {
                currencies = coins
            }
            collectionView.reloadData()
        }
    }
    
    func collectionView(_ collectionView: UICollectionView, numberOfItemsInSection section: Int) -> Int {
        currencies.count
    }
    
    func collectionView(_ collectionView: UICollectionView, cellForItemAt indexPath: IndexPath) -> UICollectionViewCell {
        let cell = collectionView.dequeueReusableCell(withReuseIdentifier:"cell", for: indexPath) as! CurrencyListCell
        cell.format()
        
        let coin = currencies[indexPath.row]
        cell.label.text = coin.displayName
        let path = getPath(fileName: coin.ticker + ".png") ?? ""
        
        cell.image.image = UIImage(contentsOfFile: path)
        
        return cell
    }
    
    func collectionView(_ collectionView: UICollectionView, layout collectionViewLayout: UICollectionViewLayout, insetForSectionAt section: Int) -> UIEdgeInsets {
        return sectionInsets
    }
    
    func collectionView(_ collectionView: UICollectionView, layout collectionViewLayout: UICollectionViewLayout, minimumLineSpacingForSectionAt section: Int) -> CGFloat {
        return sectionInsets.left
    }
    
    func collectionView(_ collectionView: UICollectionView, didSelectItemAt indexPath: IndexPath) {
        collectionView.deselectItem(at: indexPath, animated: true)
        let coin = currencies[indexPath.row]
        
        UserDefaults.standard.set(try! PropertyListEncoder().encode(coin), forKey: "relevantCoin")
        performSegue(withIdentifier: "Doorway", sender: self)
    }
    
}
