//
//  global.swift
//  Killer Interface
//
//  Created by Yush Raj Kapoor on 3/29/22.
//

import Foundation

func getImages(from currencies:[Coin]) async {
    for coin in currencies {
        let imageDataFromURL = NSData(contentsOf: URL(string: coin.geckoImageURL)!) ?? NSData()
        let documentsDirectory = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0]
        let fileURL = documentsDirectory.appendingPathComponent(coin.ticker + ".png")
        do {
            try imageDataFromURL.write(to: fileURL)
        } catch {
            print("error saving file:", error)
        }
    }
}


func getPath(fileName: String) -> String? {
    let fileManager = FileManager.default
    let path = (getDirectoryPath() as NSString).appendingPathComponent(fileName)
    if !fileManager.fileExists(atPath: path) {
        return nil
    } else {
        return path
    }
}


func getDirectoryPath() -> String {
    let paths = NSSearchPathForDirectoriesInDomains(.documentDirectory, .userDomainMask, true)
    let documentsDirectory = paths[0]
    return documentsDirectory
}
