# -*- coding: utf-8 -*-
"""
Created on Fri Dec  7 16:18:24 2018

@author: User
"""

import qrcode
def createqr(text):
    img = qrcode.make(text)
    path = 'qrcode.png'
    img.save(path)