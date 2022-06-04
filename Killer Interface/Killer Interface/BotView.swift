//
//  BotView.swift
//  Killer Interface
//
//  Created by Yush Raj Kapoor on 2/27/22.
//

import Foundation
import UIKit
import Firebase
import SwiftyJSON

class BotView: UIViewController, UITableViewDelegate, UITableViewDataSource {
    
    var account:Account! {
        didSet {
            Phemex.shared.setAccount(account: account)
        }
    }
    
    var coin:Coin!
    
    @IBOutlet weak var table: UITableView!
    @IBOutlet weak var simpleComplex: UIButton!
    var isItSimple: Complexity! {
        didSet {
            simpleComplex.setTitle(isItSimple.rawValue, for: .normal)
            UserDefaults.standard.setValue(isItSimple.rawValue, forKey: "simpleOrComplex")
            
            updateDataArray()
        }
    }
    
    var runtimes:[DataNode] = [] {
        didSet {
            runtimes.sort(by: {$0.TimeOfDecision > $1.TimeOfDecision})
            updateDataArray()
        }
    }
    var dataArray:[DataNode] = []
    
    
    override func viewDidLoad() {
        super.viewDidLoad()
        title = account.strategyName()
        table.delegate = self
        table.dataSource = self
        
        let simpleOrComplex = UserDefaults.standard.string(forKey: "simpleOrComplex")
        isItSimple = Complexity(rawValue: simpleOrComplex ?? "All")
        
        getRuntimes()
    }
    
    
    func getRuntimes() {
        let name = "\(coin.ticker)_\(account.strategy())_DataNodeCache"
        let savedDataNodes = FileData.shared.decodeDataNode(name: name)
        runtimes.append(contentsOf: savedDataNodes)
        
        let t = Int(runtimes.first?.TimeOfDecision ?? 1646940000.0)
        ref.child(coin.ticker.uppercased() + "/data").child(account.dataSource()).queryOrderedByKey().queryStarting(atValue: String(t)).observeSingleEvent(of: .value) { [self] snapshot in
            
            let json = JSON(snapshot.value ?? [])
            
            var tempData:[Double:DataNode] = [:]
            let savedDataTimes = savedDataNodes.map({$0.TimeOfDecision})
            for i in json {
                if !savedDataTimes.contains(Double(i.0)) {
                    var nodeJSON = i.1
                    nodeJSON["time_of_decision"] = JSON(i.0)
                    let node = DataNode(node: nodeJSON)
                    tempData[node.TimeOfDecision] = node
                }
            }
            
            ref.child(coin.ticker.uppercased() + "/verdicts").child(account.strategy()).getData(completion: { err, snapshot in
                let json = JSON(snapshot.value ?? [])
                for i in json {
                    let value = i.1.string ?? ""
                    let first = tempData[Double(i.0)!]
                    first?.Verdict = DataNode.Verdict(rawValue: value)
                }
                
                runtimes.append(contentsOf: tempData.values)
                FileData.shared.encode(json: try! JSONEncoder().encode(runtimes), name: name)
            })
        }
        
        
    }
    
    func updateDataArray() {
        if isItSimple == .simple {
            dataArray =  runtimes.filter({$0.Verdict?.rawValue ?? "put" != "put"})
        } else {
            dataArray = runtimes
        }
        table.reloadData()
    }
    
    @IBAction func simplePressed(_ sender: Any) {
        if isItSimple == .complex {
            isItSimple = .simple
        } else {
            isItSimple = .complex
        }
    }
    
    func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
        dataArray.count
    }
    
    func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
        let cell = tableView.dequeueReusableCell(withIdentifier:"cell", for: indexPath)
        var content = cell.defaultContentConfiguration()
        let value = dataArray[indexPath.row]
        
        let labelDate = Date(timeIntervalSince1970: TimeInterval(value.TimeOfDecision))
        let dateFormatter = DateFormatter()
        dateFormatter.dateFormat = "MM/dd/YY HH:mm:ss"
        content.text = dateFormatter.string(from: labelDate)
        
        if value.Verdict == .buy {
            content.textProperties.color = .green
        } else if value.Verdict == .sell {
            content.textProperties.color = .red
        }
        
        cell.accessoryType = .disclosureIndicator
        cell.contentConfiguration = content
        return cell
    }
    
    func tableView(_ tableView: UITableView, didSelectRowAt indexPath: IndexPath) {
        tableView.deselectRow(at: indexPath, animated: true)
        let vc = UIStoryboard(name:"Main", bundle:nil).instantiateViewController(identifier: "VerdictView") as! VerdictView
        let data = dataArray[indexPath.row]
        vc.strategy = account.strategy()
        vc.node = data
        vc.data = runtimes
        vc.coin = coin
        
        let labelDate = Date(timeIntervalSince1970: TimeInterval(data.TimeOfDecision))
        let dateFormatter = DateFormatter()
        dateFormatter.dateFormat = "MM/dd/YY HH:mm:ss"
        vc.title = dateFormatter.string(from: labelDate)
        
        navigationController?.pushViewController(vc, animated: true)
    }
    
    enum Complexity:String {
        case simple = "Simple"
        case complex = "All"
    }
    
}
