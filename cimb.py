# -*- coding: utf-8 -*-
"""
Created on Wed Dec  5 17:20:04 2018

@author: Asus
"""
import random
import uuid
import datetime as dt
import names

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import SingletonThreadPool
from tableDefine import *

engine = create_engine('sqlite:///data.db', echo = True, poolclass=SingletonThreadPool)
Session = sessionmaker(bind = engine)
session = Session()
cimb_credentials_database = session.query(Credentials).all()
cimb_particulars_database = session.query(Particulars).all()


from telegram import ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, RegexHandler, ConversationHandler
import qrcode
import logging
from pyzbar.pyzbar import decode
from pyzbar.pyzbar import ZBarSymbol
from PIL import Image

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

WHICHUSER, BEGINCREATE, SCANFRONTID, SCANBACKID, SCANRESIDENCE, PASSWORD, \
    CHECK, SELECTOR, WITHDRAW, QRWITHDRAW, DEPOSIT, QRDEPOSIT, USERNAME_CREATION, \
    PASSWORD_CREATION = range(14)

start_keyboard =[['Create New Account'],
                 ['Login to Current Account']]
new_keyboard = [['Continue'],
                ['Exit']]
login_keyboard = [['Withdraw','Deposit'],
                  ['Show QR','Check Balance'],
                  ['Exit']]

start_markup = ReplyKeyboardMarkup(start_keyboard, one_time_keyboard = True)
new_markup = ReplyKeyboardMarkup(new_keyboard, one_time_keyboard = True)
login_markup = ReplyKeyboardMarkup(login_keyboard, one_time_keyboard = True)

def start(bot, update):
    update.message.reply_text("Hi, I am Cheryl, how can I help you today?", reply_markup = start_markup)
    return WHICHUSER

def new_account(bot, update):
    update.message.reply_text("Thank you for choosing CIMB.\nWe require several pieces of information from you. This will require a camera-enabled device.\n1) National ID\n2) Proof of Residential Address(Telco, Utility)", reply_markup = new_markup)
    return BEGINCREATE


######################################################################################
def check_credential(user_name_value, password_value, databases):
    for item in databases:
        if item.user_name == user_name_value:
            if item.password == password_value:
                return ('Login Successful', item.particulars_id)
    return ('Invalid Username or Password',0)

def pull_out_name(particulars_id, databases):
    for item in databases:
        if particulars_id == item.data_id:
            return item.full_name
    return

def pull_out_balance(username, databases):
    for item in databases:
        if username == item.user_name:
            return item.acc_balance
    return

######################################################################################
def for_username(bot, update):
    cimb_credentials_database = session.query(Credentials).all()
    cimb_particulars_database = session.query(Particulars).all()
    update.message.reply_text("Welcome to CIMB Login Page!")
    update.message.reply_text("Input Username")
    return PASSWORD

def for_password(bot, update, user_data):
    user_data['username'] = update.message.text
    update.message.reply_text("Input Password")
    return CHECK

def check(bot, update, user_data):
    user_data['password'] = update.message.text
    check_status = check_credential(user_data['username'], user_data['password'], cimb_credentials_database)
    if check_status[1] == False:
        update.message.reply_text("Invalid username or password! Please enter username again.")
        return PASSWORD
    else:
        #Query userdata here
        amount = pull_out_balance(user_data['username'], cimb_credentials_database)
        user_data['balance'] = amount #placeholder (need go query) 
        update.message.reply_text("Login Successful!\n Welcome " + pull_out_name(check_status[1], cimb_particulars_database))
        update.message.reply_text("Account balance: " + str(user_data['balance']))
        update.message.reply_text("What would you like to do?", reply_markup = login_markup)
        return SELECTOR
        
######################################################################################

def received(bot,update):
    file_id = update.message.photo[-1].file_id
    newFile = bot.getFile(file_id)
    newFile.download('residence_' + str(update.message.from_user.id) + '_' + str(update.message.date).replace(':','') + '.jpg')
    update.message.reply_text("Your documents are received successfully.\n\n Processing may take up to two working days.\n\n You will receive a message from us shortly.")
    update.message.reply_text("Your application is successful.")
    ######################################################################################
    # I just mock some data just for trial purpose to insert to database
    session1 = Session()
    startdate = dt.date(1950,1,1)
    nbdays = (dt.date.today()-startdate).days
    d = random.randint(0,nbdays)
    gender = ['M', 'F']
    particulars_data = Particulars(query_max_dataid(cimb_particulars_database)+1, str(uuid.uuid4()), names.get_full_name(), startdate+dt.timedelta(days=d), random.randint(100000,999999), 'Singaporean', gender[random.randint(0,1)] , None)
    session1.add(particulars_data)
    session1.commit()
    update.message.reply_text("Enter your desired username:")
    return USERNAME_CREATION


def creating_username(bot, update, user_data):
    ## Added function to create username
    user_data['username'] = update.message.text
    check_value = check_username_validity(user_data['username'], cimb_credentials_database)
    if check_value == 0:
        update.message.reply_text('Username already taken!')
        update.message.reply_text("Enter your desired username:")
        return USERNAME_CREATION
    update.message.reply_text('Username successfully created!')
    update.message.reply_text('Enter your desired password:')
    return PASSWORD_CREATION

def check_username_validity(username, databases):
    for item in databases:
        if username == item.user_name:
            return 0
    return 1

def creating_password(bot, update, user_data):
    ## Added function to create password
    session3 = Session()
    user_data['password'] = update.message.text
    update.message.reply_text('Password successfully created!')
    credentials_data = Credentials(user_data['username'], user_data['password'], query_max_dataid2(cimb_credentials_database) + 1)
    session3.add(credentials_data)
    session3.commit()
    update.message.reply_text('Type /start to redeploy Cheryl')
    return ConversationHandler.END

def query_max_dataid2(databases):
    # For taking largest id number HAHA
    max_value = 0
    for item in databases:
        if item.particulars_id > max_value:
            max_value = item.particulars_id
    return max_value

def query_max_dataid(databases):
    # For taking largest id number HAHA
    max_value = 0
    for item in databases:
        if item.data_id > max_value:
            max_value = item.data_id
    return max_value


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

def withdraw(bot, update):
    update.message.reply_text("Please enter the amount you wish to withdraw.")
    return WITHDRAW

def withdraw_balance(bot, update, user_data):
    user_data['withdraw'] = float(update.message.text)
    if user_data['balance'] >= user_data['withdraw']:
        update.message.reply_text("Please scan the QR Code of the merchant.")
        return QRWITHDRAW
    else:
        update.message.reply_text("Insufficient Funds! Please enter another amount.")
        return WITHDRAW

def qrcheck_withdraw(bot, update, user_data):
    file_id = update.message.photo[-1].file_id
    newFile = bot.getFile(file_id)
    newFile.download('QR_' + str(update.message.from_user.id) + '_' + str(update.message.date).replace(':','') + '.png')
    user_id = qr_reader('QR_' + str(update.message.from_user.id) + '_' + str(update.message.date).replace(':','') + '.png')
    user_data['balance'] = user_data['balance'] - user_data['withdraw']
    #update database
    update.message.reply_text("Withdrawal was successful from " + user_id[0].data.decode('ascii'))
    update.message.reply_text("What else would you like to do?", reply_markup = login_markup)
    return SELECTOR

def deposit(bot, update):
    update.message.reply_text("Please enter the amount you wish to deposit.")
    return DEPOSIT

def deposit_amount(bot, update, user_data):
    user_data['deposit'] = float(update.message.text)
    update.message.reply_text("Please scan the QR Code of the merchant.")
    return QRDEPOSIT

def qrcheck_deposit(bot, update, user_data):
    file_id = update.message.photo[-1].file_id
    newFile = bot.getFile(file_id)
    newFile.download('QR_' + str(update.message.from_user.id) + '_' + str(update.message.date).replace(':','') + '.png')
    user_id = qr_reader('QR_' + str(update.message.from_user.id) + '_' + str(update.message.date).replace(':','') + '.png')
    #check id somehow
    user_data['balance'] = user_data['balance'] + user_data['deposit']
    #update database
    update.message.reply_text("Deposit was made successfully to " + user_id[0].data.decode('ascii'))
    update.message.reply_text("What else would you like to do?", reply_markup = login_markup)
    return SELECTOR

def showQR(bot, update,user_data):
    img = qrcode.make(user_data['username'])
    img.save(str(update.message.from_user.id) + '_' + str(update.message.date).replace(':','') + '.png')
    bot.send_photo(chat_id=update.message.chat_id, photo = open(str(update.message.from_user.id) + '_' + str(update.message.date).replace(':','') + '.png', 'rb'))
    update.message.reply_text("What else would you like to do?", reply_markup = login_markup)
    return SELECTOR

def check_balance(bot, update, user_data):
    update.message.reply_text('Your current balance is {}'.format(user_data['balance']))
    update.message.reply_text("What else would you like to do?", reply_markup = login_markup)
    return SELECTOR

    
def finish(bot,update):
    update.message.reply_text("See you soon. To begin again, type /start")
    return ConversationHandler.END
    
def invalid(bot,update):
    update.message.reply_text("Invalid input")
    return ConversationHandler.END

def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)
    
def qr_reader(image):
    data = decode(Image.open(image), symbols=[ZBarSymbol.QRCODE])
    return data


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
                    CHECK: [MessageHandler(Filters.text, check, pass_user_data = True)],
                    SELECTOR: [RegexHandler('^Withdraw$', withdraw), RegexHandler('^Deposit$', deposit), \
                               RegexHandler('^Show QR$', showQR, pass_user_data = True), \
                               RegexHandler('^Check Balance$', check_balance, pass_user_data = True), \
                               RegexHandler('^Exit$', finish)],
                    WITHDRAW: [RegexHandler('^\$?(\d*(\d\.?|\.\d{1,2}))$', withdraw_balance, pass_user_data = True)],
                    QRWITHDRAW: [MessageHandler(Filters.photo, qrcheck_withdraw, pass_user_data = True)],
                    DEPOSIT: [RegexHandler('^\$?(\d*(\d\.?|\.\d{1,2}))$', deposit_amount, pass_user_data = True)],
                    QRDEPOSIT: [MessageHandler(Filters.photo, qrcheck_deposit, pass_user_data = True)],
                    USERNAME_CREATION: [MessageHandler(Filters.text, creating_username, pass_user_data = True)],
                    PASSWORD_CREATION: [MessageHandler(Filters.text, creating_password, pass_user_data = True)],
                    },
            fallbacks = [MessageHandler(Filters.text,invalid), CommandHandler('exit', finish)]
            
            )
    
    dp.add_handler(conv_handler)

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()