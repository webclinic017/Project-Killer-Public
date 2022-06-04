//
//  VerdictView.swift
//  Killer Interface
//
//  Created by Yush Raj Kapoor on 3/12/22.
//

import Foundation
import UIKit
import Charts
import SwiftyJSON
import XCTest

class VerdictView: UIViewController, ChartViewDelegate {
    
    @IBOutlet weak var primaryChart: LineChartView!
    @IBOutlet weak var secondaryChart: LineChartView!
    @IBOutlet weak var tertiaryChart: LineChartView!
    @IBOutlet weak var quaternaryChart: LineChartView!
    @IBOutlet weak var verdict: UILabel!
    @IBOutlet weak var positiveVerdictStack: UIStackView!
    @IBOutlet weak var entryPrice: UILabel!
    @IBOutlet weak var takeProfit: UILabel!
    @IBOutlet weak var stopLoss: UILabel!
    @IBOutlet weak var orderStatus: UILabel!
    @IBOutlet weak var filledStack: UIStackView!
    @IBOutlet weak var exitPrice: UILabel!
    @IBOutlet weak var timeOfExit: UILabel!
    @IBOutlet weak var pnl: UILabel!
    @IBOutlet weak var segmentedControl: UISegmentedControl!
    @IBOutlet weak var statusStack: UIStackView!
    var strategy:String!
    var node:DataNode!
    var data:[DataNode]!
    
    var primaryChartData:[String:[ChartDataEntry]] = [:]
    var secondaryChartData:[String:[ChartDataEntry]] = [:]
    var tertiaryChartData:[String:[ChartDataEntry]] = [:]
    var quaternaryChartData:[String:[ChartDataEntry]] = [:]
    
    var coin:Coin!
    
    
    override func viewDidLoad() {
        super.viewDidLoad()
        
        positiveVerdictStack.isHidden = false
        statusStack.isHidden = false
        filledStack.isHidden = true
        let verd = node.Verdict
        verdict.text = verd?.rawValue.capitalized
        if verd == .buy {
            verdict.textColor = .green
        } else if verd == .sell {
            verdict.textColor = .red
        } else {
            statusStack.isHidden = true
            positiveVerdictStack.isHidden = true
        }
        
        handlePositiveVerdict()
        grabData()
    }
    
    func getVerdictIds() async -> JSON {
        do {
            let data = try await ref.child(coin.ticker.uppercased() + "/bots/\(strategy!)/verdict_ids").getData()
            return JSON(data.value ?? [])
        } catch {
            print("error")
        }
        return JSON()
    }
    
    func handlePositiveVerdict() {
        Task.init() {
            let ids = await getVerdictIds()
            
            var relevantIds:[String] = []
            for id in ids {
                if (Double(id.0)! - 20) < node.TimeOfDecision! && node.TimeOfDecision < (Double(id.0)! + 20) {
                    relevantIds = id.1.dictionaryObject?.map({$0.value as! String}) ?? []
                }
            }
            
            var allOrders:[Order] = []
            let orders = await Endpoints.shared.getOrderBy(orderIDs: relevantIds, symbol: coin.ticker.uppercased() + "USD")
            for order in orders {
                let newOrder = Order(order: order.1, feeRate: 0.0015)
                allOrders.append(newOrder)
            }
            
            if !allOrders.isEmpty {
                var TPOrder:Order?
                var SLOrder:Order?
                
                if let marketOrder = allOrders.first(where: {$0.type == .market}) {
                    let executedPrice = await getExecutedPrice(order: marketOrder)
                    marketOrder.price = executedPrice
                    entryPrice.text = "$" + String(marketOrder.price)
                    takeProfit.text = "$" + String(marketOrder.takeProfitPrice)
                    stopLoss.text = "$" + String(marketOrder.stopLossPrice)
                }
                if let takeProfitOrder = allOrders.first(where: {$0.type == .takeProfit}) {
                    if takeProfitOrder.status == .fill {
                        let executedPrice = await getExecutedPrice(order: takeProfitOrder)
                        takeProfitOrder.price = executedPrice
                        fillDetailStack(filledOrder: takeProfitOrder)
                    }
                    TPOrder = takeProfitOrder
                }
                if let stopLossOrder = allOrders.first(where: {$0.type == .stopLoss}) {
                    if stopLossOrder.status == .fill {
                        let executedPrice = await getExecutedPrice(order: stopLossOrder)
                        stopLossOrder.price = executedPrice
                        fillDetailStack(filledOrder: stopLossOrder)
                    }
                    SLOrder = stopLossOrder
                }
                
                if TPOrder?.status == .rejected && SLOrder?.status == .rejected {
                    orderStatus.text = Order.Status.fill.rawValue
                } else if filledStack.isHidden {
                    orderStatus.text = Order.Status.untriggered.rawValue
                }
            }
        }
    }
    
    func fillDetailStack(filledOrder: Order) {
        filledStack.isHidden = false
        orderStatus.text = filledOrder.status.rawValue
        pnl.text = "$" + String(filledOrder.pnl.toString())
        exitPrice.text = "$" + String(filledOrder.price)
        let dateFormatter = DateFormatter()
        dateFormatter.dateFormat = "yyyy-MM-dd HH:mm:ss"
        let formattedDate = dateFormatter.string(from: Date(timeIntervalSince1970: filledOrder.time))
        timeOfExit.text = formattedDate
    }
    
    func getExecutedPrice(order: Order) async -> Double {
        let executedTrades = await Endpoints.shared.getExecutedTrades(symbol: coin.ticker.uppercased() + "USD", startTime: Int(order.time-43200)*1000, endTime: Int(order.time+43200)*1000)["data"]["rows"]
        for i in executedTrades {
            let trade = i.1
            if trade["orderID"].string == order.orderID {
                return Double(trade["execPriceEp"].int! / 10000)
            }
        }
        return 0
    }
    
    func grabData() {
        let time = node.TimeOfDecision!
        let timeTravel = time - 86400
        
        var relevantNodes:[DataNode] = []
        
        for i in data {
            let newTime = i.TimeOfDecision
            if newTime! >= timeTravel && newTime! <= time {
               // i.TimeOfDecision = Double(newTime!)
                relevantNodes.append(i)
            }
        }
        
        switch strategy {
        case "strategy_one":
            strategyOne(relevantNodes: relevantNodes)
            break
        case "strategy_two":
            strategyTwo(relevantNodes: relevantNodes)
            break
        case "strategy_three":
            strategyThree(relevantNodes: relevantNodes)
            break
        case "strategy_four":
            strategyFour(relevantNodes: relevantNodes)
        case "strategy_five":
            strategyFive(relevantNodes: relevantNodes)
        default:
            break
        }
    }
    
    func strategyOne(relevantNodes:[DataNode]) {
        var priceValues:[ChartDataEntry] = []
        var rsiValues:[ChartDataEntry] = []
        var macdValues:[ChartDataEntry] = []
        var signalValues:[ChartDataEntry] = []
        var kValues:[ChartDataEntry] = []
        var dValues:[ChartDataEntry] = []
        for i in relevantNodes {
            priceValues.append(ChartDataEntry(x: i.TimeOfDecision, y: Double(i.Price)))
            rsiValues.append(ChartDataEntry(x: i.TimeOfDecision, y: Double(i.RSI)))
            macdValues.append(ChartDataEntry(x: i.TimeOfDecision, y: Double(i.MACD)))
            signalValues.append(ChartDataEntry(x: i.TimeOfDecision, y: Double(i.Signal)))
            kValues.append(ChartDataEntry(x: i.TimeOfDecision, y: Double(i.KData)))
            dValues.append(ChartDataEntry(x: i.TimeOfDecision, y: Double(i.DData)))
        }
        primaryChartData["Price"] = priceValues.reversed()
        secondaryChartData["RSI"] = rsiValues.reversed()
        secondaryChartData["Bands 50"] = horizontalLineAt(value: 50, chartData: rsiValues.reversed())
        secondaryChartData["Bounds 0"] = horizontalLineAt(value: 0, chartData: rsiValues.reversed())
        secondaryChartData["Bounds 100"] = horizontalLineAt(value: 100, chartData: rsiValues.reversed())
        tertiaryChartData["MACD"] = macdValues.reversed()
        tertiaryChartData["Signal"] = signalValues.reversed()
        quaternaryChartData["KData"] = kValues.reversed()
        quaternaryChartData["DData"] = dValues.reversed()
        quaternaryChartData["Bands 70"] = horizontalLineAt(value: 80, chartData: kValues.reversed())
        quaternaryChartData["Bands 30"] = horizontalLineAt(value: 20, chartData: kValues.reversed())
        quaternaryChartData["Bounds 0"] = horizontalLineAt(value: 0, chartData: kValues.reversed())
        quaternaryChartData["Bounds 100"] = horizontalLineAt(value: 100, chartData: kValues.reversed())
        
        setCharts()
    }
    
    func strategyTwo(relevantNodes:[DataNode]) {
        var ema25Values:[ChartDataEntry] = []
        var ema50Values:[ChartDataEntry] = []
        var ema100Values:[ChartDataEntry] = []
        var priceValues:[ChartDataEntry] = []
        
        for i in relevantNodes {
            ema25Values.append(ChartDataEntry(x: i.TimeOfDecision, y: Double(i.EMA25)))
            ema50Values.append(ChartDataEntry(x: i.TimeOfDecision, y: Double(i.EMA50)))
            ema100Values.append(ChartDataEntry(x: i.TimeOfDecision, y: Double(i.EMA100)))
            priceValues.append(ChartDataEntry(x: i.TimeOfDecision, y: Double(i.Price)))
        }
        primaryChartData["Price"] = priceValues.reversed()
        primaryChartData["EMA25"] = ema25Values.reversed()
        primaryChartData["EMA50"] = ema50Values.reversed()
        primaryChartData["EMA100"] = ema100Values.reversed()
        
        setCharts()
    }
    
    func strategyThree(relevantNodes:[DataNode]) {
        var ema200Values:[ChartDataEntry] = []
        var priceValues:[ChartDataEntry] = []
        var bullishEngulfingPatterns:[ChartDataEntry] = []
        var bearishEngulfingPatterns:[ChartDataEntry] = []
        var rsiValues:[ChartDataEntry] = []
        var stdValues:[ChartDataEntry] = []
        
        for i in relevantNodes {
            ema200Values.append(ChartDataEntry(x: i.TimeOfDecision, y: Double(i.EMA200)))
            priceValues.append(ChartDataEntry(x: i.TimeOfDecision, y: Double(i.Price)))
            rsiValues.append(ChartDataEntry(x: i.TimeOfDecision, y: Double(i.RSI)))
            if i.Engulfing == "Bullish" {
                bullishEngulfingPatterns.append(ChartDataEntry(x: i.TimeOfDecision, y: Double(i.Price)))
            } else if i.Engulfing == "Bearish" {
                bearishEngulfingPatterns.append(ChartDataEntry(x: i.TimeOfDecision, y: Double(i.Price)))
            }
            stdValues.append(ChartDataEntry(x: i.TimeOfDecision, y: Double(i.STD ?? 0.0)/Double(i.Price)))
        }
 
        bullishEngulfingPatterns.remove(at: 0)
        bearishEngulfingPatterns.remove(at: 0)
        if !bullishEngulfingPatterns.contains(where: { $0.x == priceValues.first!.x}) && !bearishEngulfingPatterns.contains(where: { $0.x == priceValues.first!.x}) {
            bullishEngulfingPatterns.insert(ChartDataEntry(x: priceValues.first!.x, y: priceValues.first!.y), at: 0)
            bearishEngulfingPatterns.insert(ChartDataEntry(x: priceValues.first!.x, y: priceValues.first!.y), at: 0)
        }
        
        primaryChartData["Price"] = priceValues.reversed()
        primaryChartData["EMA200"] = ema200Values.reversed()
        primaryChartData["Bull"] = bullishEngulfingPatterns.reversed()
        primaryChartData["Bear"] = bearishEngulfingPatterns.reversed()
        secondaryChartData["RSI"] = rsiValues.reversed()
        secondaryChartData["Bands 50"] = horizontalLineAt(value: 50, chartData: rsiValues.reversed())
        secondaryChartData["Bounds 0"] = horizontalLineAt(value: 0, chartData: rsiValues.reversed())
        secondaryChartData["Bounds 100"] = horizontalLineAt(value: 100, chartData: rsiValues.reversed())
        tertiaryChartData["Standard Deviation"] = stdValues.reversed()
        
        setCharts()
    }
    
    func strategyFour(relevantNodes:[DataNode]) {
        var sTrend10Values:[ChartDataEntry] = []
        var sTrend11Values:[ChartDataEntry] = []
        var sTrend12Values:[ChartDataEntry] = []
        var kValues:[ChartDataEntry] = []
        var dValues:[ChartDataEntry] = []
        var tsvValues:[ChartDataEntry] = []
        var ema200Values:[ChartDataEntry] = []
        var priceValues:[ChartDataEntry] = []
        
        for i in relevantNodes {
            sTrend10Values.append(ChartDataEntry(x: i.TimeOfDecision, y: Double(i.Supertrend10.value)))
            sTrend11Values.append(ChartDataEntry(x: i.TimeOfDecision, y: Double(i.Supertrend11.value)))
            sTrend12Values.append(ChartDataEntry(x: i.TimeOfDecision, y: Double(i.Supertrend12.value)))
            
            dValues.append(ChartDataEntry(x: i.TimeOfDecision, y: Double(i.DData)))
            kValues.append(ChartDataEntry(x: i.TimeOfDecision, y: Double(i.KData)))
            tsvValues.append(ChartDataEntry(x: i.TimeOfDecision, y: Double(i.TSV)))
            ema200Values.append(ChartDataEntry(x: i.TimeOfDecision, y: Double(i.EMA200)))
            priceValues.append(ChartDataEntry(x: i.TimeOfDecision, y: Double(i.Price)))
        }
        
        primaryChartData["Price"] = priceValues.reversed()
        primaryChartData["EMA200"] = ema200Values.reversed()
        primaryChartData["Supertrend 10" + ((relevantNodes.first?.Supertrend10.direction ?? 0) > 0 ? "green":"red")] = sTrend10Values.reversed()
        primaryChartData["Supertrend 11" + ((relevantNodes.first?.Supertrend11.direction ?? 0) > 0 ? "green":"red")] = sTrend11Values.reversed()
        primaryChartData["Supertrend 12" + ((relevantNodes.first?.Supertrend12.direction ?? 0) > 0 ? "green":"red")] = sTrend12Values.reversed()
        secondaryChartData["TSV"] = tsvValues.reversed()
        secondaryChartData["Bounds -10"] = horizontalLineAt(value: -10, chartData: tsvValues.reversed())
        secondaryChartData["Bounds 10"] = horizontalLineAt(value: 10, chartData: tsvValues.reversed())
        tertiaryChartData["KData"] = kValues.reversed()
        tertiaryChartData["DData"] = dValues.reversed()
        tertiaryChartData["Bounds 0"] = horizontalLineAt(value: 0, chartData: kValues.reversed())
        tertiaryChartData["Bounds 100"] = horizontalLineAt(value: 100, chartData: kValues.reversed())
        tertiaryChartData["Bands 20"] = horizontalLineAt(value: 20, chartData: kValues.reversed())
        tertiaryChartData["Bands 80"] = horizontalLineAt(value: 80, chartData: kValues.reversed())
        
        setCharts()
    }
    
    func strategyFive(relevantNodes:[DataNode]) {
        var bBandsUpper:[ChartDataEntry] = []
        var bBandsMiddle:[ChartDataEntry] = []
        var bBandsLower:[ChartDataEntry] = []
        var priceValues:[ChartDataEntry] = []
        
        for i in relevantNodes {
            bBandsUpper.append(ChartDataEntry(x: i.TimeOfDecision, y: Double(i.Bollinger_Upper)))
            bBandsMiddle.append(ChartDataEntry(x: i.TimeOfDecision, y: Double(i.Bollinger_Middle)))
            bBandsLower.append(ChartDataEntry(x: i.TimeOfDecision, y: Double(i.Bollinger_Lower)))
            priceValues.append(ChartDataEntry(x: i.TimeOfDecision, y: Double(i.Price)))
        }
        
        primaryChartData["Price"] = priceValues.reversed()
        primaryChartData["Upper Bollinger"] = bBandsUpper.reversed()
        primaryChartData["Middle Bollinger"] = bBandsMiddle.reversed()
        primaryChartData["Lower Bollinger"] = bBandsLower.reversed()
        
        setCharts()
    }
    
    func setCharts() {
        let charts = [primaryChart, secondaryChart, tertiaryChart, quaternaryChart]
        let chartData = [primaryChartData, secondaryChartData, tertiaryChartData, quaternaryChartData]
        
        for (index, _) in charts.enumerated() {
            let relevantData = chartData[index]
            let relevantChart = charts[index]!
            if relevantData.isEmpty {
                relevantChart.isHidden = true
                continue
            } else {
                relevantChart.isHidden = false
            }
            
            getData(chart: relevantChart, newData: relevantData)
            
            relevantChart.delegate = self
            relevantChart.setViewPortOffsets(left: 0, top: 20, right: 0, bottom: 20)
            relevantChart.backgroundColor = .secondarySystemBackground
            relevantChart.isUserInteractionEnabled = false
            
            relevantChart.xAxis.enabled = false
            
            let yAxis = relevantChart.leftAxis
            yAxis.labelFont = yAxis.labelFont.withSize(12)
            yAxis.labelTextColor = .label
            yAxis.labelPosition = .insideChart
            yAxis.axisLineColor = .label
            
            relevantChart.rightAxis.enabled = false
            relevantChart.leftAxis.enabled = true
            
            var legendEntries = relevantChart.legend.entries
            
            for i in legendEntries {
                let blacklist = ["Bear", "Bull", "Bands", "Bounds"]
                for j in blacklist {
                    if i.label?.contains(j) ?? false {
                        let ind = legendEntries.firstIndex(of: i) ?? -1
                        if ind != -1 {
                            legendEntries.remove(at: ind)
                            relevantChart.legend.setCustom(entries: legendEntries)
                        }
                    }
                }
            }
            relevantChart.legend.enabled = true
            
            relevantChart.layer.cornerRadius = 15
            relevantChart.layer.masksToBounds = true
        }
    }
    
    func getData(chart: LineChartView, newData: [String:[ChartDataEntry]]) {
        let index = segmentedControl.selectedSegmentIndex
        
        let timeTravelIndex:[Int:Double] = [0:3600, 1:86400]
        let entries = newData
        
        let timeString = node.Time ?? ""
        let dateFormatter = DateFormatter()
        dateFormatter.locale = Locale(identifier: "en_US_POSIX")
        dateFormatter.dateFormat = "yyyy-MM-dd'T'HH:mm:ssZ"
        let time = dateFormatter.date(from: timeString)?.timeIntervalSince1970
        let timeTravel = time! - timeTravelIndex[index]!
        
        var dataSets:[ChartDataSetProtocol] = []
        
        for i in entries.keys {
            let dataSet = entries[i]
            let newSet = dataSet!.filter({$0.x >= timeTravel})
            
            let set = LineChartDataSet(entries: newSet, label: i)
            set.mode = LineChartDataSet.Mode.cubicBezier
            set.drawCirclesEnabled = false
            set.lineWidth = 1
            
            let changeColor:[String: NSUIColor] = ["Bear": .clear, "Bull": .clear, "Bands": .label, "Bounds": .clear, "Price": .link, "KData":.cyan, "DData": .magenta, "RSI": .cyan, "Signal": .magenta, "MACD": .cyan, "EMA25": .cyan, "EMA50": .magenta, "EMA100": .orange, "EMA200": .cyan]
            let circleColor:[String: NSUIColor] = ["Bear": .red, "Bull": .green]
            for j in changeColor.keys {
                if i.contains(j) {
                    set.colors = [changeColor[j]!]
                }
            }
            for j in circleColor.keys {
                if i.contains(j) {
                    set.circleColors = [circleColor[j]!]
                    set.drawCirclesEnabled = true
                    set.circleRadius = 3
                    //set.circleHoleRadius = 2
                    set.circleHoleColor = .clear
                }
            }
            if i.contains("green") {
                set.colors = [.green]
                set.label!.removeLast(5)
            }
            if i.contains("red") {
                set.colors = [.red]
                set.label!.removeLast(3)
            }
            
            dataSets.append(set)
        }
        
        dataSets.sort(by: {$0.label! < $1.label!})
        
        let chartSet = LineChartData(dataSets: dataSets)
        
        chartSet.setValueFont(UIFont(name: "HelveticaNeue-Light", size: 9)!)
        chartSet.setDrawValues(false)
        
        chart.data = chartSet
        
        chart.animate(xAxisDuration: 0.75)
    }
    
    func horizontalLineAt(value:Double, chartData: [ChartDataEntry]) -> [ChartDataEntry] {
        var toReturn:[ChartDataEntry] = []
        for i in chartData {
            toReturn.append(ChartDataEntry(x: i.x, y: value))
        }
        return toReturn
    }
    
    
    @IBAction func segmentChanged(_ sender: Any) {
        setCharts()
    }
    
}

extension Double {
    func toString(decimal: Int = 9) -> String {
        let value = decimal < 0 ? 0 : decimal
        var string = String(format: "%.\(value)f", self)

        while string.last == "0" || string.last == "." {
            if string.last == "." { string = String(string.dropLast()); break}
            string = String(string.dropLast())
        }
        return string
    }
}
