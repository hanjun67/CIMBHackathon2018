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

WHICHUSER, BEGINCREATE, SCANFRONTID, SCANBACKID, SCANRESIDENCE, USERNAME, PASSWORD, CHECK = range(8)

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


######################################################################################
# For Database query
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from tableDefine import *

engine = create_engine('sqlite:///data.db', echo = True)
Session = sessionmaker(bind = engine)
session = Session()
cimb_credentials_database = session.query(Credentials).all()
cimb_particulars_database = session.query(Particulars).all()
def check_credential(user_name_value, password_value, databases):
    for item in databases:
        if item.user_name == user_name_value:
            if item.password == password_value:
                return ('Login Successful', item.particulars_id)
    return 'Invalid Username or Password'

def pull_out_name(particulars_id, databases):
    for item in databases:
        if particulars_id == item.data_id:
            return item.full_name
    return

######################################################################################

def for_username(bot, update):
    update.message.reply_text("Welcome to CIMB Login Page!")
    update.message.reply_text("Input Username")
    return PASSWORD

def for_password(bot, update, user_data):
    user_data['username'] = update.message.text
    update.message.reply_text("Input Password")
    return CHECK

def check(bot, update, user_data):
    user_data['password'] = update.message.text
    name_data = check_credential(user_data['username'], user_data['password'], cimb_credentials_database)
    update.message.reply_text(name_data[0])
    update.message.reply_text('Welcome ' + pull_out_name(name_data[1], cimb_particulars_database) + '!')
    return ConversationHandler.END

def scanFrontID(bot, update):
    update.message.reply_text("Please send a picture of the front of your National ID")
    return SCANFRONTID

def scanBackID(bot, update):
    file_id = update.message.photo[-1].file_id
    newFile = bot.getFile(file_id)
    newFile.download('frontID_' + str(update.message.from_user.id) + '_' + str(update.message.date).replace(':','') + '.jpg')
    update.message.reply_text("Please send a picture of the back of your National ID")
    return SCANBACKID

def scanResidence(bot, update):
    file_id = update.message.photo[-1].file_id
    newFile = bot.getFile(file_id)
    newFile.download('backID_' + str(update.message.from_user.id) + '_' + str(update.message.date).replace(':','') + '.jpg')
    update.message.reply_text("Please send a picture of the proof of residence")
    return SCANRESIDENCE

def received(bot,update):
    file_id = update.message.photo[-1].file_id
    newFile = bot.getFile(file_id)
    newFile.download('residence_' + str(update.message.from_user.id) + '_' + str(update.message.date).replace(':','') + '.jpg')
    update.message.reply_text("Your documents are received successfully.\n\n Processing may take up to two working days.\n\n You will receive a message from us shortly.")
    return ConversationHandler.END
    
def finish(bot,update):
    update.message.reply_text("Bye motherfucker")
    return ConversationHandler.END
    
def invalid(bot,update):
    update.message.reply_text("Invalid input")
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
                    WHICHUSER: [RegexHandler('^Create New Account$', new_account), RegexHandler('^Login to Current Account$', for_username)],
                    BEGINCREATE: [RegexHandler('^Continue$', scanFrontID), RegexHandler('^Exit$', finish)],
                    SCANFRONTID: [MessageHandler(Filters.photo, scanBackID)],
                    SCANBACKID: [MessageHandler(Filters.photo, scanResidence)],
                    SCANRESIDENCE: [MessageHandler(Filters.photo, received)],
                    PASSWORD: [MessageHandler(Filters.text, for_password, pass_user_data = True)],
                    CHECK: [MessageHandler(Filters.text, check, pass_user_data = True)]
                    },
            fallbacks = [MessageHandler(Filters.text,invalid)]
            
            )
    
    dp.add_handler(conv_handler)

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()