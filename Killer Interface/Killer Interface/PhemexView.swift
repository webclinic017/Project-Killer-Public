//
//  PhemexView.swift
//  Killer Interface
//
//  Created by Yush Raj Kapoor on 2/26/22.
//

import Foundation
import UIKit
import SwiftyJSON
import Charts

class PhemexView: UIViewController, UIPickerViewDelegate, UIPickerViewDataSource, UITextFieldDelegate, ChartViewDelegate {
    
    @IBOutlet weak var priceSegmentedControl: UISegmentedControl!
    @IBOutlet weak var pnlSegmentedControl: UISegmentedControl!
    @IBOutlet weak var priceChart: LineChartView!
    @IBOutlet weak var pnlChart: LineChartView!
    @IBOutlet weak var account: UIButton!
    @IBOutlet weak var activityIndicator1: UIActivityIndicatorView!
    @IBOutlet weak var activityIndicator2: UIActivityIndicatorView!
    @IBOutlet weak var polaritySwitch: UISwitch!
    
    var coin:Coin?
    
    var relevantAccount:Account! {
        didSet {
            account.setTitle(relevantAccount.name(), for: .normal)
            UserDefaults.standard.set(relevantAccount.rawValue, forKey: "account")
            ref.removeAllObservers()
            updatePolarity()
        }
    }
    var selectedIndex:Int = 0 {
        didSet {
            priceSegmentedControl.selectedSegmentIndex = selectedIndex
            pnlSegmentedControl.selectedSegmentIndex = selectedIndex
            updateData()
        }
    }
    @IBOutlet weak var priceLabel: UILabel!
    var price:String = "Price" {
        didSet {
            DispatchQueue.main.async { [self] in
                priceLabel.text = "Price: $" + price
            }
        }
    }
    var loading:Bool = false {
        didSet {
            if loading {
                activityIndicator1.startAnimating()
                activityIndicator2.startAnimating()
            } else {
                activityIndicator1.stopAnimating()
                activityIndicator2.stopAnimating()
            }
        }
    }
    
    @IBOutlet weak var dontRemove: UITextField!
    let accountTypes = Account.allCases
    
    var priceTimer:Timer?
    var graphTimer:Timer?
    var queryingPrice = false
    
    var first = true
    
    
    override func viewDidLoad() {
        super.viewDidLoad()
        if let storedRelevantCoin = UserDefaults.standard.data(forKey: "relevantCoin") {
            let relevantCoin = try? PropertyListDecoder().decode(Coin.self, from: storedRelevantCoin)
            if let relevantCoin = relevantCoin {
                coin = relevantCoin
            }
        }
        title = coin?.displayName
        
        let name = UserDefaults.standard.string(forKey: "account")
        let account = Account(rawValue: name ?? "one")
        relevantAccount = account
        activityIndicator1.hidesWhenStopped = true
        activityIndicator2.hidesWhenStopped = true
        
        setUpPickerView()
        Phemex.shared.setAccount(account: relevantAccount)
        
        selectorsChanged(ind: priceSegmentedControl.selectedSegmentIndex)
        
        priceTimer = Timer.scheduledTimer(timeInterval: 1, target: self, selector: #selector(updatePrice), userInfo: nil, repeats: true)
        graphTimer = Timer.scheduledTimer(timeInterval: 60, target: self, selector: #selector(updateData), userInfo: nil, repeats: true)
        
        updatePolarity()
        
        Task.init() {
            await queryAndSetPrice()
        }
    }
    
    
    func loadCache(index: Int) {
        if let phemexData = UserDefaults.standard.array(forKey: "PhemexViewData\(coin?.geckoID ?? "")\(relevantAccount.name())\(index)") as? [[[Double]]] {
            var chartData:[[ChartDataEntry]] = []
            for i in phemexData {
                chartData.append(convertTripleDataArray(entries: i))
            }
            setCharts(dataPoints: chartData, indexSnapshot: index)
        }
    }
    
    @objc func updateData() {
        let indexSnapshot = selectedIndex
        loadCache(index: indexSnapshot)
        Task.init() {
            DispatchQueue.main.async {
                self.loading = true
            }
            
            let segmentedControlConversion:[Double] = [1, 7, 30, 365]
            let binSize:[Double] = [5, 15, 60, 1440]
            let periodStringConversion:[String] = ["5", "15", "60", "D"]
            var orders:JSON!
            while orders == nil {
                do {
                    orders = JSON(rawValue: (try await ref.child((coin?.ticker ?? "").uppercased() + "/orders/" + relevantAccount.strategy()).getData().value)!) ?? JSON()
                } catch {
                    print(error)
                }
            }
            
            let now = Date().timeIntervalSince1970
            let days_ago = segmentedControlConversion[selectedIndex] * 24 * 60 * 60
            let delta = now - days_ago
            var priceData = JSON()
            var loop_timeout = 10
            while priceData.contains(where: {$0.0 == "s"}) || priceData["s"] != "ok" {
                if loop_timeout <= 0 {break}
                let curr = JSON(rawValue: (try await ref.child("currency_coin_pairs/" + (coin?.ticker ?? "").uppercased()).getData().value)!) ?? JSON()
                priceData = await Endpoints.shared.getPriceData(symbol: "BINANCE:\((coin?.ticker ?? "").uppercased())\(curr)", resolution: periodStringConversion[selectedIndex], from: delta, to: now)
                loop_timeout -= 1
            }
            
            let genesis:Double = 1576800000
            let day:Double = 60*60*24 //86400 seconds
            
            var startTime = genesis
            let endTime = Date().timeIntervalSince1970
            if selectedIndex != 4 {
                startTime = endTime - (day * segmentedControlConversion[selectedIndex])
            }
            
            var formattedOrders:[Order] = orders.map({Order(order: $0.1)})
            formattedOrders = formattedOrders.filter({$0.symbol == (coin?.ticker ?? "").uppercased() + "USD"})
            
            formattedOrders.sort(by: {$0.time < $1.time})
            
            let priorOrders = formattedOrders.filter({$0.time < startTime})
            let currentOrders = formattedOrders.filter({$0.time >= startTime})
            
            let numberOfDataPoints = Int((endTime - startTime) / (60*binSize[selectedIndex]))
            
            var dataTimes:[Double] = []
            var tallyTime = startTime
            for _ in 0...numberOfDataPoints {
                dataTimes.append(tallyTime)
                tallyTime += (60*binSize[selectedIndex])
            }
            
            var orderPoints:[Double:Double] = currentOrders.reduce(into: [Double:Double]()) {
                $0[$1.findClosestTime(times: dataTimes)] = 0.0
            }
            
            for i in currentOrders {
                let bin = i.findClosestTime(times: dataTimes)
                orderPoints[bin]! += i.pnl
            }
            
            var tallyPNL:Double = 0
            for i in priorOrders {
                tallyPNL += i.pnl
            }
            
            var pnlPoints:[ChartDataEntry] = []
            for i in dataTimes {
                if let relevantOrderPoint = orderPoints.first(where: {$0.key == i}) {
                    tallyPNL += relevantOrderPoint.value
                }
                pnlPoints.append(ChartDataEntry(x: i, y: tallyPNL))
            }
            
            pnlPoints = pnlPoints.filter({$0.x > startTime})
            pnlPoints.sort(by: {$0.x < $1.y})
            
            var pricePoints:[ChartDataEntry] = []
            let allTime = priceData["t"]
            let allClose = priceData["c"]
            for (i,_) in allTime.enumerated() {
                pricePoints.append(ChartDataEntry(x: allTime[i].double!, y: allClose[i].double!))
            }
            
            setCharts(dataPoints: [pricePoints, pnlPoints], indexSnapshot: indexSnapshot)
        }
    }
    
    func setCharts(dataPoints:[[ChartDataEntry]], indexSnapshot: Int) {
        let charts = [priceChart!, pnlChart!]
        for (i, chart) in charts.enumerated() {
            
            getData(chart: chart, dataPoints: dataPoints[i])
            
            Task.init() {
                chart.delegate = self
                chart.setViewPortOffsets(left: 0, top: 20, right: 0, bottom: 20)
                chart.backgroundColor = .secondarySystemBackground
                chart.isUserInteractionEnabled = false
                
                chart.xAxis.enabled = false
                let yAxis = chart.leftAxis
                yAxis.labelFont = yAxis.labelFont.withSize(12)
                yAxis.labelTextColor = .label
                yAxis.labelPosition = .insideChart
                yAxis.axisLineColor = .label
                
                chart.legend.enabled = false
                chart.rightAxis.enabled = false
                chart.leftAxis.enabled = true
                
                chart.layer.cornerRadius = 15
                chart.layer.masksToBounds = true
            }
        }
        first = false
        loading = false
        var convertedData:[[[Double]]] = []
        for i in dataPoints {
            let converted = convertChartDataEntry(entries: i)
            convertedData.append(converted)
        }
        UserDefaults.standard.setValue(convertedData, forKey: "PhemexViewData\(coin?.geckoID ?? "")\(relevantAccount.name())\(indexSnapshot)")
    }
    
    func getData(chart: LineChartView, dataPoints:[ChartDataEntry]) {
        let set = LineChartDataSet(entries: dataPoints, label: (coin?.ticker ?? "").uppercased())
        set.mode = LineChartDataSet.Mode.linear
        
        set.drawCirclesEnabled = false
        set.lineWidth = 2
        
        let chartSet = LineChartData(dataSet: set)
        
        chartSet.setValueFont(UIFont(name: "HelveticaNeue-Light", size: 9)!)
        chartSet.setDrawValues(false)
        
        DispatchQueue.main.async { [self] in
            chart.data = chartSet
            
            if first {
                chart.animate(xAxisDuration: 0.75)
            } else {
                chart.animate(xAxisDuration: 0.0)
            }
        }
    }
    
    @objc func updatePrice() {
        let forceUpdate = UserDefaults.standard.bool(forKey: "forceUpdate")
        if forceUpdate {
            UserDefaults.standard.setValue(false, forKey: "forceUpdate")
            updateData()
        }
        Task.init() {
            if !queryingPrice {
                await queryAndSetPrice()
            }
        }
    }
    
    @objc func queryAndSetPrice() async {
        queryingPrice = true
        let data = await Endpoints.shared.get24hData(symbol: (coin?.ticker ?? "").uppercased() + "USD")["result"]
        queryingPrice = false
        if let markPrice = data["markPrice"].int {
            let marketPrice = Double(markPrice) / 10000.0
            price = String(marketPrice)
        }
    }
    
    func updatePolarity() {
        ref.child("bots/\(relevantAccount.strategy())/polarity").observe(.value) { [self] snapshot in
            if let snap = snapshot.value as? Bool {
                print("Change in Polarity Detected (value: \(snap))")
                polaritySwitch.setOn(snap, animated: true)
            }
        }
    }
    
    func setUpPickerView() {
        let picker = UIPickerView()
        picker.translatesAutoresizingMaskIntoConstraints = false
        picker.delegate = self
        picker.dataSource = self
        picker.backgroundColor = .secondarySystemBackground
        
        let toolBar = UIToolbar()
        toolBar.sizeToFit()
        let space = UIBarButtonItem(barButtonSystemItem: .flexibleSpace, target: nil, action: nil)
        let button = UIBarButtonItem(title: "Done", style: .done, target: self, action: #selector(self.action))
        toolBar.backgroundColor = .secondarySystemBackground
        toolBar.isTranslucent = false
        toolBar.setItems([space, button], animated: false)
        toolBar.isUserInteractionEnabled = true
        dontRemove.inputView = picker
        dontRemove.inputAccessoryView = toolBar
    }
    
    func convertChartDataEntry(entries: [ChartDataEntry]) -> [[Double]] {
        var toReturn:[[Double]] = []
        for entry in entries {
            toReturn.append([entry.x, entry.y])
        }
        return toReturn
    }
    
    func convertTripleDataArray(entries: [[Double]]) -> [ChartDataEntry] {
        var toReturn:[ChartDataEntry] = []
        for entry in entries {
            toReturn.append(ChartDataEntry(x: entry[0], y: entry[1]))
        }
        return toReturn
    }
    
    @IBAction func accountTypeChange(_ sender: Any) {
        dontRemove.becomeFirstResponder()
    }
    
    func selectorsChanged(ind: Int) {
        selectedIndex = ind
    }
    
    @IBAction func priceSelectorChanged(_ sender: Any) {
        selectorsChanged(ind: priceSegmentedControl.selectedSegmentIndex)
    }
    
    @IBAction func pnlSelectorChanged(_ sender: Any) {
        selectorsChanged(ind: pnlSegmentedControl.selectedSegmentIndex)
    }
    
    @IBAction func polarityChanged(_ sender: Any) {
        let alertController = UIAlertController(title: "Wait!", message: "Are you sure you want to change the polarity of \(relevantAccount.strategyName()) algorithm? All future decisions will be made opposite.", preferredStyle: .alert)
        let yes = UIAlertAction(title: "Yes", style: .default, handler: { [self] action in
            ref.child("bots/\(relevantAccount.strategy())/polarity").setValue(polaritySwitch.isOn)
        })
        let no = UIAlertAction(title: "No", style: .cancel, handler: nil)
        
        alertController.addAction(yes)
        alertController.addAction(no)
        present(alertController, animated: true, completion: nil)
    }
    
    @objc func action() {
        view.endEditing(true)
    }
    
    func numberOfComponents(in pickerView: UIPickerView) -> Int {
        return 1
    }
    
    func pickerView(_ pickerView: UIPickerView, numberOfRowsInComponent component: Int) -> Int {
        return accountTypes.count
    }
    
    func pickerView(_ pickerView: UIPickerView, titleForRow row: Int, forComponent component: Int) -> String? {
        return accountTypes[row].name()
    }
    
    func pickerView(_ pickerView: UIPickerView, didSelectRow row: Int, inComponent component: Int) {
        relevantAccount = accountTypes[row]
        Phemex.shared.setAccount(account: relevantAccount)
        first = true
        updateData()
    }
    
}
