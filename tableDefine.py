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
	""""""
	__tablename__ = "particulars"

	data_id = Column(Integer, primary_key=True)
	national_id = Column(Integer, unique = True, nullable=False)
	full_name = Column(String, nullable=False)
	date_of_birth = Column(Date, nullable=False)
	postal_code = Column(Integer, nullable=False)
	nationality = Column(String, nullable=False)
	gender = Column(String, nullable=False)
		
	
	#----------------------------------------------------------------------
	# This is used to query for creating the entries in the table
	def __init__(self, data_id, national_id, full_name, date_of_birth, postal_code, nationality, gender):
		""""""
		self.data_id = data_id
		self.national_id =national_id
		self.full_name = full_name
		self.date_of_birth = date_of_birth
		self.postal_code = postal_code
		self.nationality = nationality
		self.gender = gender

class Credentials(Base):
    __tablename__ = "credentials"
    user_name = Column(String, nullable=False, primary_key=True)
    password = Column(String,nullable=False)
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
        

# create tables
Base.metadata.create_all(engine)