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

WHICHUSER, BEGINCREATE, SCANFRONTID, SCANBACKID, SCANRESIDENCE, USERNAME, PASSWORD, CHECK, \
    USERNAME_CREATION, PASSWORD_CREATION = range(10)

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
    if name_data[1] == 0:
        return ConversationHandler.END
    update.message.reply_text(name_data[0])
    update.message.reply_text('Welcome ' + pull_out_name(name_data[1], cimb_particulars_database) + '!')
    return ConversationHandler.END

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

USERNAME_CREATION: [MessageHandler(Filters.text, creating_username, pass_user_data = True)],
                    PASSWORD_CREATION: [MessageHandler(Filters.text, creating_password, pass_user_data = True)],



