

from sqlalchemy import Column, Integer, String, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

SCHEMADEF = {"schema": "coviddata"}

class CaseSummaryFile(Base):
	__tablename__ = 'summaryfile'
#	__table_args__ = {"schema": "coviddata"}
	__table_args__ = SCHEMADEF

	id = Column(Integer, nullable=False, unique=True, primary_key=True)
	filename = Column(String(250), nullable=False, unique=True)
	size = Column(Integer, nullable=False)
	state = Column(String(25), nullable=False)
	released = Column(DateTime, nullable=False)

class StateData(Base):
	__tablename__ = 'statedata'
#	__table_args__ = {"schema": "coviddata"}
	__table_args__ = SCHEMADEF

	id = Column(Integer, nullable=False, unique=True, primary_key=True)
	summaryfiledate = Column(DateTime, nullable=False)
	itemname = Column(String(200), nullable=False)
	itemvalue = Column(Float, nullable=False)

class CasesByCounty(Base):
	__tablename__ = 'CasesByCounty'
#	__table_args__ = {"schema": "coviddata"}
	__table_args__ = SCHEMADEF

	id = Column(Integer, nullable=False, unique=True, primary_key=True)
	summaryfiledate = Column(DateTime, nullable=False)
	county = Column(String(200), nullable=False)
	itemname = Column(String(200), nullable=False)
	itemvalue = Column(Float, nullable=True)

class CasesByAgeGroup(Base):
	__tablename__ = 'CasesByAgeGroup'
#	__table_args__ = {"schema": "coviddata"}
	__table_args__ = SCHEMADEF

	id = Column(Integer, nullable=False, unique=True, primary_key=True)
	summaryfiledate = Column(DateTime, nullable=False)
	agegroup = Column(String(200), nullable=False)
	itemname = Column(String(200), nullable=False)
	itemvalue = Column(Float, nullable=True)

class CasesBySex(Base):
	__tablename__ = 'CasesBySex'
#	__table_args__ = {"schema": "coviddata"}
	__table_args__ = SCHEMADEF

	id = Column(Integer, nullable=False, unique=True, primary_key=True)
	summaryfiledate = Column(DateTime, nullable=False)
	sex = Column(String(200), nullable=False)
	itemname = Column(String(200), nullable=False)
	itemvalue = Column(Float, nullable=True)

class DeathsBySex(Base):
	__tablename__ = 'DeathsBySex'
#	__table_args__ = {"schema": "coviddata"}
	__table_args__ = SCHEMADEF

	id = Column(Integer, nullable=False, unique=True, primary_key=True)
	summaryfiledate = Column(DateTime, nullable=False)
	sex = Column(String(200), nullable=False)
	itemname = Column(String(200), nullable=False)
	itemvalue = Column(Float, nullable=True)

class CasesByOnsetdate(Base):
	__tablename__ = 'CasesByOnsetdate'
#	__table_args__ = {"schema": "coviddata"}
	__table_args__ = SCHEMADEF

	id = Column(Integer, nullable=False, unique=True, primary_key=True)
	summaryfiledate = Column(DateTime, nullable=False)
	onsetdate = Column(DateTime, nullable=False)
	itemname = Column(String(200), nullable=False)
	itemvalue = Column(Float, nullable=True)

class CasesByReported(Base):
	__tablename__ = 'CasesByReported'
#	__table_args__ = {"schema": "coviddata"}
	__table_args__ = SCHEMADEF

	id = Column(Integer, nullable=False, unique=True, primary_key=True)
	summaryfiledate = Column(DateTime, nullable=False)
	reporteddate = Column(DateTime, nullable=False)
	itemname = Column(String(200), nullable=False)
	itemvalue = Column(Float, nullable=True)

class DeathsByCounty(Base):
	__tablename__ = 'DeathsByCounty'
#	__table_args__ = {"schema": "coviddata"}
	__table_args__ = SCHEMADEF

	id = Column(Integer, nullable=False, unique=True, primary_key=True)
	summaryfiledate = Column(DateTime, nullable=False)
	county = Column(String(200), nullable=False)
	itemname = Column(String(200), nullable=False)
	itemvalue = Column(Float, nullable=True)

class CasesByAHD(Base):
	__tablename__ = 'CasesByAHD'
#	__table_args__ = {"schema": "coviddata"}
	__table_args__ = SCHEMADEF

	id = Column(Integer, nullable=False, unique=True, primary_key=True)
	summaryfiledate = Column(DateTime, nullable=False)
	agegroup = Column(String(200), nullable=False)
	hospitalization = Column(String(200), nullable=False)
	itemvalue = Column(Float, nullable=True)

class PercentRaceAndEthnicity(Base):
	__tablename__ = 'PercentRaceAndEthnicity'
#	__table_args__ = {"schema": "coviddata"}
	__table_args__ = SCHEMADEF

	id = Column(Integer, nullable=False, unique=True, primary_key=True)
	summaryfiledate = Column(DateTime, nullable=False)
	raceeth = Column(String(200), nullable=False)
	metric = Column(String(200), nullable=False)
	itemvalue = Column(Float, nullable=True)

class PositivityData(Base):
	__tablename__ = 'PositivityData'
#	__table_args__ = {"schema": "coviddata"}
	__table_args__ = SCHEMADEF

	id = Column(Integer, nullable=False, unique=True, primary_key=True)
	summaryfiledate = Column(DateTime, nullable=False)
	testdate = Column(String(200), nullable=False)
	itemname = Column(String(200), nullable=False)
	itemvalue = Column(Float, nullable=True)

class CumulativeCasesByOnsetdate(Base):
	__tablename__ = 'CumulativeCasesByOnsetdate'
#	__table_args__ = {"schema": "coviddata"}
	__table_args__ = SCHEMADEF

	id = Column(Integer, nullable=False, unique=True, primary_key=True)
	summaryfiledate = Column(DateTime, nullable=False)
	onsetdate = Column(String(200), nullable=False)
	itemname = Column(String(200), nullable=False)
	itemvalue = Column(Float, nullable=True)

class CumulativeHospByOnsetdate(Base):
	__tablename__ = 'CumulativeHospByOnsetdate'
#	__table_args__ = {"schema": "coviddata"}
	__table_args__ = SCHEMADEF

	id = Column(Integer, nullable=False, unique=True, primary_key=True)
	summaryfiledate = Column(DateTime, nullable=False)
	onsetdate = Column(String(200), nullable=False)
	itemname = Column(String(200), nullable=False)
	itemvalue = Column(Float, nullable=True)

class CumulativeDeathByOnsetdate(Base):
	__tablename__ = 'CumulativeDeathByOnsetdate'
#	__table_args__ = {"schema": "coviddata"}
	__table_args__ = SCHEMADEF

	id = Column(Integer, nullable=False, unique=True, primary_key=True)
	summaryfiledate = Column(DateTime, nullable=False)
	onsetdate = Column(String(200), nullable=False)
	itemname = Column(String(200), nullable=False)
	itemvalue = Column(Float, nullable=True)

class CumulativeCasesByReported(Base):
	__tablename__ = 'CumulativeCasesByReported'
#	__table_args__ = {"schema": "coviddata"}
	__table_args__ = SCHEMADEF

	id = Column(Integer, nullable=False, unique=True, primary_key=True)
	summaryfiledate = Column(DateTime, nullable=False)
	reporteddate = Column(String(200), nullable=False)
	itemname = Column(String(200), nullable=False)
	itemvalue = Column(Float, nullable=True)

class CumulativeHospsByReported(Base):
	__tablename__ = 'CumulativeHospsByReported'
#	__table_args__ = {"schema": "coviddata"}
	__table_args__ = SCHEMADEF

	id = Column(Integer, nullable=False, unique=True, primary_key=True)
	summaryfiledate = Column(DateTime, nullable=False)
	reporteddate = Column(String(200), nullable=False)
	itemname = Column(String(200), nullable=False)
	itemvalue = Column(Float, nullable=True)

class CumulativeDeathsByReported(Base):
	__tablename__ = 'CumulativeDeathsByReported'
#	__table_args__ = {"schema": "coviddata"}
	__table_args__ = SCHEMADEF

	id = Column(Integer, nullable=False, unique=True, primary_key=True)
	summaryfiledate = Column(DateTime, nullable=False)
	reporteddate = Column(String(200), nullable=False)
	itemname = Column(String(200), nullable=False)
	itemvalue = Column(Float, nullable=True)

class DeathsByDeathDate(Base):
	__tablename__ = 'DeathsByDeathDate'
#	__table_args__ = {"schema": "coviddata"}
	__table_args__ = SCHEMADEF

	id = Column(Integer, nullable=False, unique=True, primary_key=True)
	summaryfiledate = Column(DateTime, nullable=False)
	deathdate = Column(String(200), nullable=False)
	itemname = Column(String(200), nullable=False)
	itemvalue = Column(Float, nullable=True)


class TransmissionType(Base):
	__tablename__ = 'TransmissionType'
#	__table_args__ = {"schema": "coviddata"}
	__table_args__ = SCHEMADEF

	id = Column(Integer, nullable=False, unique=True, primary_key=True)
	summaryfiledate = Column(DateTime, nullable=False)
	transtype = Column(String(200), nullable=False)
	itemmeasure = Column(String(200), nullable=False)
	itemvalue = Column(Float, nullable=True)




