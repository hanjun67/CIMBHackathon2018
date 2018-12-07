# -*- coding: utf-8 -*-
"""
Created on Wed Dec  5 17:20:04 2018

@author: Asus
"""
from telegram import ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, RegexHandler, ConversationHandler

import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

WHICHUSER, BEGINCREATE, SCANFRONTID, SCANBACKID, SCANRESIDENCE = range(5)

start_keyboard =[['Create New Account'],
                 ['Login to Current Account']]
new_keyboard = [['Continue'],
                ['Exit']]

start_markup = ReplyKeyboardMarkup(start_keyboard, one_time_keyboard = True)
new_markup = ReplyKeyboardMarkup(new_keyboard, one_time_keyboard = True)

def start(bot, update):
    update.message.reply_text("Hi, I am Cheryl, how can I help you today?", reply_markup = start_markup)
    return WHICHUSER

def new_account(bot, update):
    update.message.reply_text("Thank you for choosing CIMB.\nWe require several pieces of information from you. This will require a camera-enabled device.\n1) National ID\n2) Proof of Residential Address(Telco, Utility)", reply_markup = new_markup)
    return BEGINCREATE

def login(bot, update):
    update.message.reply_text("fuck off")
    return ConversationHandler.END

def scanFrontID(bot, update):
    update.message.reply_text("Please send a picture of the front of your National ID")
    return SCANFRONTID

def scanBackID(bot, update):
    update.message.reply_text("Please send a picture of the back of your National ID")
    return SCANBACKID

def scanResidence(bot, update):
    update.message.reply_text("Please send a picture of the proof of residence")
    return SCANRESIDENCE
    
def finish(bot,update):
    update.message.reply_text("Bye motherfucker")
    return ConversationHandler.END
    
def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)

def main():
    updater = Updater("703554781:AAH_RUj6ss6lG_a-PG6sISy0suBgpeA4yhc")
    
    dp = updater.dispatcher
    
    conv_handler = ConversationHandler(
            entry_points = [CommandHandler('start',start)],
            states = {
                    WHICHUSER: [RegexHandler('^Create New Account$', new_account), RegexHandler('^Login to Current Account$', login)],
                    BEGINCREATE: [RegexHandler('^Continue$', scanFrontID), RegexHandler('^Exit$', finish)],
                    SCANFRONTID: [MessageHandler(Filters.photo, scanBackID)],
                    SCANBACKID: [MessageHandler(Filters.photo, scanResidence)],
                    SCANRESIDENCE: [MessageHandler(Filters.photo, finish)]
                    },
            fallbacks = [RegexHandler('^Finish$', finish, pass_user_data=True)]
            
            )
    
    dp.add_handler(conv_handler)

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()