# This script is to define the table for SQL
from sqlalchemy import *
from sqlalchemy import create_engine, ForeignKey
from sqlalchemy import Column, Date, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, backref

# Change the .db to the name that you wanted if needed.
engine = create_engine('sqlite:///data.db', echo=True)
Base = declarative_base()

########################################################################
class Particulars(Base):
	__tablename__ = "particulars"

	data_id = Column(Integer, primary_key=True)
	national_id = Column(Integer, unique = True, nullable=False)
	full_name = Column(String, nullable=False)
	date_of_birth = Column(Date, nullable=False)
	postal_code = Column(Integer, nullable=False)
	nationality = Column(String, nullable=False)
	gender = Column(String, nullable=False)
	chat_id = Column(Integer, nullable=True)
	
	#----------------------------------------------------------------------
	# This is used to query for creating the entries in the table
	def __init__(self, data_id, national_id, full_name, date_of_birth, postal_code, nationality, gender, chat_id):
		self.data_id = data_id
		self.national_id =national_id
		self.full_name = full_name
		self.date_of_birth = date_of_birth
		self.postal_code = postal_code
		self.nationality = nationality
		self.gender = gender
		self.chat_id = chat_id

class Credentials(Base):
    __tablename__ = "credentials"

    user_name = Column(String, nullable=False, primary_key=True)
    password = Column(String,nullable=False)
    acc_balance = Column(Float, nullable=False, default=0)
    particulars_id = Column(Integer, ForeignKey('particulars.data_id'))
    # Use cascade='delete,all' to propagate the deletion of a credentials onto its particulars
    particulars = relationship(
        Particulars, 
        backref=backref('credential',
            uselist = True,
            cascade = 'delete, all'
        )
    )

    def __init__(self, user_name, password, particulars_id):
        self.user_name = user_name
        self.password = password
        self.particulars_id = particulars_id
        
class Transactions(Base):
	__tablename__ = "transactions"

	transaction_id = Column(Integer, primary_key=True)
	debit_user_name = Column(Integer, ForeignKey('credentials.user_name'), nullable = False)
	credit_user_name = Column(Integer, ForeignKey('credentials.user_name'), nullable = False)
	amount = Column(Float, nullable=False)
	description = Column(String)
	debit_user = relationship(Credentials, foreign_keys = [debit_user_name])
	credit_user = relationship(Credentials, foreign_keys = [credit_user_name])

	def __init__(self, transaction_id, debit_user_name, credit_user_name, amount, description):
		self.transaction_id = transaction_id
		self.debit_user_name = debit_user_name
		self.credit_user_name = credit_user_name
		self.amount = amount
		self.description = description


# create tables
Base.metadata.create_all(engine)