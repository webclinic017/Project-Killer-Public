//
//  SettingsView.swift
//  Killer Interface
//
//  Created by Yush Raj Kapoor on 5/15/22.
//

import Foundation
import UIKit


class SettingsView: UIViewController, UITableViewDelegate, UITableViewDataSource {
    
    @IBOutlet weak var tableView: UITableView!
    
    let settings = ["Active Currencies"]
    let vcName = ["ActiveCurrenciesView"]
    
    override func viewDidLoad() {
        super.viewDidLoad()
        tableView.delegate = self
        tableView.dataSource = self
        
    }
    
    
    func tableView(_ tableView: UITableView, numberOfRowsInSection section: Int) -> Int {
        settings.count
    }
    
    func tableView(_ tableView: UITableView, cellForRowAt indexPath: IndexPath) -> UITableViewCell {
        let cell = tableView.dequeueReusableCell(withIdentifier:"cell", for: indexPath)
        var content = cell.defaultContentConfiguration()
        content.text = settings[indexPath.row]
        
        cell.accessoryType = .disclosureIndicator
        cell.contentConfiguration = content
        return cell
    }
    
    func tableView(_ tableView: UITableView, didSelectRowAt indexPath: IndexPath) {
        tableView.deselectRow(at: indexPath, animated: true)
        let vc = UIStoryboard(name:"Main", bundle:nil).instantiateViewController(identifier: vcName[indexPath.row])
        navigationController?.pushViewController(vc, animated: true)
    }
    
}
