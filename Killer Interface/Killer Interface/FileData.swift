//
//  FileData.swift
//  Killer Interface
//
//  Created by Yush Raj Kapoor on 3/29/22.
//

import Foundation

class FileData {
    
    static var shared = FileData()
    
    
    func encode(json: Data, name: String) {
        // requires try? JSONEncoder().encode(encodable_data)
        let pathDirectory = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0]
        try? FileManager().createDirectory(at: pathDirectory, withIntermediateDirectories: true)
        let filePath = pathDirectory.appendingPathComponent("\(name).json")
        
        do {
             try json.write(to: filePath)
        } catch {
            print("Failed to write JSON data: \(error.localizedDescription)")
        }
    }

    func decodeDataNode(name: String) -> [DataNode] {
        let path = retrievePath(name: name)
        if let path = path {
            let d = (try? Data(contentsOf: URL(fileURLWithPath: path))) ?? Data()
            let decoded = try! JSONDecoder().decode([DataNode].self, from: d)
            return decoded
        }
        return []
    }

    func existsOnFile(name: String) -> Bool {
        let fileManager = FileManager.default
        let directoryPath = NSSearchPathForDirectoriesInDomains(.documentDirectory, .userDomainMask, true)[0]
        let path = (directoryPath as NSString).appendingPathComponent("\(name).json")
        if fileManager.fileExists(atPath: path) {
            return true
        }
        return false
    }

    func retrievePath(name: String) -> String? {
        let fileManager = FileManager.default
        let directoryPath = NSSearchPathForDirectoriesInDomains(.documentDirectory, .userDomainMask, true)[0]
        let path = (directoryPath as NSString).appendingPathComponent("\(name).json")
        if fileManager.fileExists(atPath: path) {
            return path
        }
        print("File \(name).json does not exist")
        return nil
    }

}
