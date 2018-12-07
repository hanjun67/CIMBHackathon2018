# -*- coding: utf-8 -*-
"""
Created on Fri Dec  7 15:58:46 2018

@author: User
"""

import urllib.request
token = '703554781:AAH_RUj6ss6lG_a-PG6sISy0suBgpeA4yhc'
chatid = '-243593722'
text = 'Your documents have been approved! Type /signup to continue.'
urllib.request.urlopen('https://api.telegram.org/bot' + token + '/sendMessage?chat_id=' + chatid + '&text=' + text)