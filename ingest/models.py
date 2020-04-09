


import os
import socket
import time
import urllib.parse
from datetime import datetime, timedelta
from sqlalchemy import Column, Integer, String, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine
from sqlalchemy import or_
from sqlalchemy.orm import sessionmaker



Base = declarative_base()

class CaseSummaryFile(Base):
	__tablename__ = 'summaryfile'

	filename = Column(String(250), nullable=False, unique=True)
	size = Column(Integer, nullable=False)
	state = Column(String(25), nullable=False)
	released = Column(DateTime, nullable=False)

class StateData(Base):
	__tablename__ = 'statedata'

	summaryfiledate = Column(DateTime, nullable=False)
	itemname = Column(String(50), nullable=False)
	itemvalue = Column(Float, nullable=False)


class CasesByCounty(Base):
	__tablename__ = 'CasesByCounty'

	summaryfiledate = Column(DateTime, nullable=False)
	county = Column(String(50), nullable=False)
	itemname = Column(String(50), nullable=False)
	itemvalue = Column(Float, nullable=True)


class CasesByAgeGroup(Base):
	__tablename__ = 'CasesByAgeGroup'

	summaryfiledate = Column(DateTime, nullable=False)
	agegroup = Column(String(50), nullable=False)
	itemname = Column(String(50), nullable=False)
	itemvalue = Column(Float, nullable=True)


class CasesBySex(Base):
	__tablename__ = 'CasesBySex'

	summaryfiledate = Column(DateTime, nullable=False)
	sex = Column(String(50), nullable=False)
	itemname = Column(String(50), nullable=False)
	itemvalue = Column(Float, nullable=True)

class DeathsBySex(Base):
	__tablename__ = 'DeathsBySex'

	summaryfiledate = Column(DateTime, nullable=False)
	sex = Column(String(50), nullable=False)
	itemname = Column(String(50), nullable=False)
	itemvalue = Column(Float, nullable=True)

class CasesByOnsetdate(Base):
	__tablename__ = 'CasesByOnsetdate'

	summaryfiledate = Column(DateTime, nullable=False)
	onsetdate = Column(DateTime(50), nullable=False)
	itemname = Column(String(50), nullable=False)
	itemvalue = Column(Float, nullable=True)

class DeathsByCounty(Base):
	__tablename__ = 'DeathsByCounty'

	summaryfiledate = Column(DateTime, nullable=False)
	county = Column(String(50), nullable=False)
	itemname = Column(String(50), nullable=False)
	itemvalue = Column(Float, nullable=True)

class CasesByAHD(Base):
	__tablename__ = 'DeathsByCounty'

	summaryfiledate = Column(DateTime, nullable=False)
	agegroup = Column(String(50), nullable=False)
	hospitalization = Column(String(50), nullable=False)
	itemvalue = Column(Float, nullable=True)

class PositivityData(Base):
	__tablename__ = 'PositivityData'

	summaryfiledate = Column(DateTime, nullable=False)
	testdate = Column(String(50), nullable=False)
	itemname = Column(String(50), nullable=False)
	itemvalue = Column(Float, nullable=True)


class CumulativeCasesByOnsetdate(Base):
	__tablename__ = 'CumulativeCasesByOnsetdate'

	summaryfiledate = Column(DateTime, nullable=False)
	onsetdate = Column(String(50), nullable=False)
	itemname = Column(String(50), nullable=False)
	itemvalue = Column(Float, nullable=True)

class CumulativeHospByOnsetdate(Base):
	__tablename__ = 'CumulativeHospByOnsetdate'

	summaryfiledate = Column(DateTime, nullable=False)
	onsetdate = Column(String(50), nullable=False)
	itemname = Column(String(50), nullable=False)
	itemvalue = Column(Float, nullable=True)

class CumulativeDeathByOnsetdate(Base):
	__tablename__ = 'CumulativeDeathByOnsetdate'

	summaryfiledate = Column(DateTime, nullable=False)
	onsetdate = Column(String(50), nullable=False)
	itemname = Column(String(50), nullable=False)
	itemvalue = Column(Float, nullable=True)

class CumulativeCasesByReported(Base):
	__tablename__ = 'CumulativeCasesByReported'

	summaryfiledate = Column(DateTime, nullable=False)
	reporteddate = Column(String(50), nullable=False)
	itemname = Column(String(50), nullable=False)
	itemvalue = Column(Float, nullable=True)

class CumulativeHospsByReported(Base):
	__tablename__ = 'CumulativeHospsByReported'

	summaryfiledate = Column(DateTime, nullable=False)
	reporteddate = Column(String(50), nullable=False)
	itemname = Column(String(50), nullable=False)
	itemvalue = Column(Float, nullable=True)

class CumulativeDeathsByReported(Base):
	__tablename__ = 'CumulativeDeathsByReported'

	summaryfiledate = Column(DateTime, nullable=False)
	reporteddate = Column(String(50), nullable=False)
	itemname = Column(String(50), nullable=False)
	itemvalue = Column(Float, nullable=True)





