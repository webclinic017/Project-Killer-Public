//
//  CurrencyListCell.swift
//  Killer Interface
//
//  Created by Yush Raj Kapoor on 5/12/22.
//

import Foundation
import UIKit

class CurrencyListCell: UICollectionViewCell {


    @IBOutlet weak var image: UIImageView!
    @IBOutlet weak var label: UILabel!
    

    override init(frame: CGRect) {
        super.init(frame: frame)
    }

       required init?(coder: NSCoder) {
           super.init(coder: coder)
           self.isUserInteractionEnabled = true
       }

    func format() {
        let smallWidth = min(UIScreen.main.bounds.width, UIScreen.main.bounds.height)
        let imageSize = (smallWidth - 100) / 3
        image.heightAnchor.constraint(equalToConstant: imageSize).isActive = true
        image.widthAnchor.constraint(equalToConstant: imageSize).isActive = true
    }

       override func awakeFromNib() {
           super.awakeFromNib()
       }
    }
