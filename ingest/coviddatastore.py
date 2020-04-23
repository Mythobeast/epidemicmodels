
import os
from datetime import datetime

import urllib.parse
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

import ingest.models as models

# from ingest.models import Base, StateData
# from ingest.models import CaseSummaryFile, CasesByCounty, CasesByOnsetdate, CasesByAHD
# from ingest.models import DeathsBySex, DeathsByCounty, PositivityData
# from ingest.models import CumulativeHospByOnsetdate, CumulativeDeathByOnsetdate, CumulativeCasesByOnsetdate
# from ingest.models import CumulativeCasesByReported, CumulativeHospsByReported, CumulativeDeathsByReported


def pop_column(row):
	startquote = row.find('"')
	endquote = row.find('"', startquote + 1)
	return row[startquote+1:endquote], row[endquote+2:]

# Managing inconsistent date format
def extract_date(value):
	try:
		return datetime.strptime(value, '%Y-%m-%d')
	except ValueError:
		pass
	return datetime.strptime(value, '%m/%d/%Y')

def checkfornull(value):
	if value == 'NA' or value == 'N/A':
		return None
	return value

def extract_quoted(input):
	output = []
	thischar = input.pop(0)
	while thischar != '"' and len(input):
		output.append(thischar)
		thischar = input.pop(0)
	return "".join(output)

def split_cvs_string(input):
	input = list(input)
	output = []
	latest = []
	while len(input) > 0:
		onechar = input.pop(0)
		if onechar == '"':
			latest = extract_quoted(input)
			continue
		if onechar == ',':
			output.append("".join(latest))
			latest = []
			continue
		latest.append(onechar)
	output.append("".join(latest).strip())
	return output

def parse_reportfilename(filename):
	fname, extension = filename.split('.')
	if extension != 'csv':
		return None
	covid19, case, summary, reportdate = fname.split('_')
	reportdate = datetime.strptime(reportdate, '%Y-%m-%d')
	return reportdate


def get_sql_url(dbspec):
	if dbspec['ENGINE'] == 'mssql':
		return f"mssql+pyodbc://{dbspec['USER']}:{urllib.parse.quote(dbspec['PASSWORD'])}@{dbspec['DSN']}"
	elif dbspec['ENGINE'] == 'mysql':
		constr = f"mysql+pymysql://{dbspec['USER']}:{urllib.parse.quote(dbspec['PASSWORD'])}@{dbspec['HOST']}/{dbspec['DATABASE']}"
		print(f"Connection string: {constr}")
		return constr
	# sooooo many problems with odbc
#		return f"mysql+pyodbc://{dbspec['USER']}:{urllib.parse.quote(dbspec['PASSWORD'])}@{dbspec['DSN']}"


class CovidDatastore:
	def __init__(self, dbspec):
#		if dbspec['ENGINE'] == 'mssql':
#			classes = dict([(name, cls) for name, cls in models.__dict__.items() if isinstance(cls, type)])
#			for name, classdef in classes.items():
#				if issubclass(classdef, models.Base):
					# if name != 'Base':
					# 	classdef.__table_args__ = {"schema": "coviddata"}
					# 	print(f"adding to {name}, {classdef.__dict__}")
		url = get_sql_url(dbspec)
		print(f"Connecting to {url}")
		self.engine = create_engine(url)
		models.Base.metadata.create_all(self.engine)
		self.DBSession = sessionmaker(bind=self.engine)
		self.session = self.DBSession()
		self.reportdate = None

		self.handlers = dict()
		self.assign_handlers()

	def assign_handlers(self):
		self.handlers['State Data'] = self.insert_state_data
		self.handlers['Case Counts by County'] = self.insert_cases_by_county
		self.handlers['Colorado Case Counts by County'] = self.insert_cases_by_county
		self.handlers['Case Rates Per 100,000 People in Colorado by County'] = self.insert_cases_by_county
		self.handlers['Number of Deaths From COVID-19 in Colorado by Date of Death - By Day'] = self.insert_deaths_by_dateofdeath
		self.handlers['Case Counts by Age Group'] = self.insert_cases_by_agegrp
		self.handlers['COVID-19 in Colorado by Age Group'] = self.insert_cases_by_agegrp
		self.handlers['Case Counts by Sex'] = self.insert_cases_by_sex
		self.handlers['COVID-19 in Colorado by Sex'] = self.insert_cases_by_sex
		self.handlers['Fatal cases by sex'] = self.insert_deaths_by_sex
		self.handlers['Case Counts by Onset Date'] = self.insert_case_counts_by_onset
		self.handlers['Cases of COVID-19 in Colorado by Date of Illness Onset'] = self.insert_case_counts_by_onset
		self.handlers['Case Counts by Reported Date'] = self.insert_case_counts_by_reported
		self.handlers['Cases of COVID-19 in Colorado by Date Reported to the State'] = self.insert_case_counts_by_reported

		self.handlers['Deaths'] = self.insert_deaths_by_county
		self.handlers['Number of Deaths by County'] = self.insert_deaths_by_county
		self.handlers['Case Counts by Age Group, Hospitalizations, and Deaths'] = self.insert_case_counts_by_ahd
		self.handlers['Case Counts by Age Group, Hospitalizations'] = self.insert_case_counts_by_ahd
		self.handlers['Cumulative Number of Cases by Onset Date'] = self.insert_cum_cases_by_onset
		self.handlers['Cumulative Number of Hospitalized Cases of COVID-19 in Colorado by Date of Illness Onset'] = self.insert_cum_cases_by_onset
		self.handlers['Cumulative Number of Cases of COVID-19 in Colorado by Date of Illness Onset'] = self.insert_cum_cases_by_onset
		self.handlers['Cumulative Number of Cases by Reported Date'] = self.insert_cum_cases_by_reported
		self.handlers['Cumulative Number of Cases of COVID-19 in Colorado by Date Reported to the State'] = self.insert_cum_cases_by_reported
		self.handlers['Cumulative Number of Hospitalizations by Onset Date'] = self.insert_cum_hosp_by_onset
		self.handlers['Cumulative Number of Hospitalizations by Reported Date'] = self.insert_cum_hosps_by_reported
		self.handlers['Cumulative Number of Hospitalized Cases of COVID-19 in Colorado by Date Reported to the State'] = self.insert_cum_hosps_by_reported
		self.handlers['Cumulative Number of Deaths by Onset Date'] = self.insert_cum_deaths_by_onset
		self.handlers['Cumulative Number of Deaths From COVID-19 in Colorado by Date of Illness'] = self.insert_cum_deaths_by_onset
		self.handlers['Cumulative Number of Deaths by Reported Date'] = self.insert_cum_deaths_by_reported
		self.handlers['Cumulative Number of Deaths From COVID-19 in Colorado by Date Reported to the State'] = self.insert_cum_deaths_by_reported

		self.handlers['Cumulative Number of Deaths From COVID-19 in Colorado by Date of Death'] = self.insert_cum_deaths_by_reported
		self.handlers['Transmission Type'] = self.insert_transmission_type
		self.handlers['Positivity Data from Clinical Laboratories'] = self.insert_positivity_data
		self.handlers['COVID-19 in Colorado by Race & Ethnicity'] = self.insert_race_and_ethnicity


	def is_loaded(self, filename):
		fileset = self.session.query(models.CaseSummaryFile).filter(models.CaseSummaryFile.filename==filename).first()
		if fileset is None:
			return False
		if fileset.state != 'loaded':
			return False
		return True

	def mark_loaded(self, filename):
		filerecord = self.session.query(models.CaseSummaryFile).filter(models.CaseSummaryFile.filename==filename).first()
		if filerecord is None:
			reportdate = parse_reportfilename(filename)
			if reportdate is None:
				return
			filesize = os.path.getsize(f'data/{filename}')
			filerecord = models.CaseSummaryFile(
					filename = filename,
					size = filesize,
					state = 'loaded',
					released = reportdate)
		else:
			filerecord.state = 'loaded'

		self.session.add(filerecord)
		self.session.commit()


	def load(self, filename):
		fname, extension = filename.split('.')
		if extension != 'csv':
			print(f"Skipping {filename}")
			return
		print(f"Processing {filename}")
		covid19, case, summary, reportdate = fname.split('_')
		self.reportdate = datetime.strptime(reportdate, '%Y-%m-%d')
		with open(f"data/{filename}") as fp:
			for oneline in fp:
				if ",Note," in oneline:
					continue
				self.insert(oneline)
		self.mark_loaded(filename)


	def insert(self, oneline):
		row = split_cvs_string(oneline)
		if row[0] == 'description':
			return
		try:
			self.handlers[row[0]](row)
		except (ValueError, KeyError) as ve:
			print(f"Value error on {oneline}")
			raise ve

	def insert_state_data(self, row):
		_ = row.pop(0)
		_ = row.pop(0)
		key = row.pop(0)
		value = row.pop(0).strip()
		insertable = models.StateData(summaryfiledate=self.reportdate, itemname=key, itemvalue=value)
		self.session.add(insertable)
		self.session.commit()


	def insert_cases_by_county(self, row):
		_ = row.pop(0)
		countyname = row.pop(0)
		key = row.pop(0)
		value = checkfornull(row.pop(0).strip())
		insertable = models.CasesByCounty(
			summaryfiledate=self.reportdate,
			county=countyname,
			itemname=key,
			itemvalue=value)
		self.session.add(insertable)
		self.session.commit()

	def insert_cases_by_agegrp(self, row):
		_ = row.pop(0)
		agegroup = row.pop(0)
		key = row.pop(0)
		value = checkfornull(row.pop(0).strip())
		insertable = models.CasesByAgeGroup(
			summaryfiledate=self.reportdate,
			agegroup=agegroup,
			itemname=key,
			itemvalue=value)
		self.session.add(insertable)
		self.session.commit()

	def insert_cases_by_sex(self, row):
		_ = row.pop(0)
		sex = row.pop(0)
		key = row.pop(0)
		value = row.pop(0).strip()
		insertable = models.CasesBySex(
			summaryfiledate=self.reportdate,
			sex=sex,
			itemname=key,
			itemvalue=value)
		self.session.add(insertable)
		self.session.commit()

	def insert_deaths_by_sex(self, row):
		_ = row.pop(0)
		sex = row.pop(0)
		key = row.pop(0)
		value = checkfornull(row.pop(0).strip())
		insertable = models.DeathsBySex(
			summaryfiledate=self.reportdate,
			sex=sex,
			itemname=key,
			itemvalue=value)
		self.session.add(insertable)
		self.session.commit()

	def insert_case_counts_by_onset(self, row):
		_ = row.pop(0)
		onsetdate = extract_date(row.pop(0))
		key = row.pop(0)
		value = checkfornull(row.pop(0).strip())
		insertable = models.CasesByOnsetdate(
			summaryfiledate=self.reportdate,
			onsetdate=onsetdate,
			itemname=key,
			itemvalue=value)
		self.session.add(insertable)
		self.session.commit()

	def insert_deaths_by_county(self, row):
		_ = row.pop(0)
		county = row.pop(0)
		key = row.pop(0)
		value = row.pop(0).strip()

		insertable = models.DeathsByCounty(
			summaryfiledate=self.reportdate,
			county=county,
			itemname=key,
			itemvalue=value)
		self.session.add(insertable)
		self.session.commit()

	def insert_case_counts_by_ahd(self, row):
		_ = row.pop(0)
		age_and_hosp = row.pop(0)
		cases = row.pop(0)
		if cases != 'Cases':
			raise ValueError("cases is not Cases")
		value = row.pop(0).strip()
		agegroup, hospitalization = age_and_hosp.split(',')
		hospitalization = hospitalization.strip()

		insertable = models.CasesByAHD(
			summaryfiledate=self.reportdate,
			agegroup=agegroup,
			hospitalization=hospitalization,
			itemvalue=value)
		self.session.add(insertable)
		self.session.commit()

	def insert_case_counts_by_reported(self, row):
		_ = row.pop(0)
		reporteddate = extract_date(row.pop(0))
		key = row.pop(0)
		value = checkfornull(row.pop(0).strip())
		insertable = models.CasesByReported(
			summaryfiledate=self.reportdate,
			reporteddate=reporteddate,
			itemname=key,
			itemvalue=value)
		self.session.add(insertable)
		self.session.commit()

	def insert_positivity_data(self, row):
		_ = row.pop(0)
		testdate = extract_date(row.pop(0))
		key = row.pop(0)
		value = checkfornull(row.pop(0).strip())

		insertable = models.PositivityData(
			summaryfiledate=self.reportdate,
			testdate=testdate,
			itemname=key,
			itemvalue=value)
		self.session.add(insertable)
		self.session.commit()

	def insert_cum_cases_by_onset(self, row):
		_ = row.pop(0)
		onsetdate = extract_date(row.pop(0))
		key = row.pop(0)
		value = checkfornull(row.pop(0).strip())
		insertable = models.CumulativeCasesByOnsetdate(
			summaryfiledate=self.reportdate,
			onsetdate=onsetdate,
			itemname=key,
			itemvalue=value)
		self.session.add(insertable)
		self.session.commit()

	def insert_cum_hosp_by_onset(self, row):
		_ = row.pop(0)
		onsetdate = extract_date(row.pop(0))
		key = row.pop(0)
		value = row.pop(0).strip()
		insertable = models.CumulativeHospByOnsetdate(
			summaryfiledate=self.reportdate,
			onsetdate=onsetdate,
			itemname=key,
			itemvalue=value)
		self.session.add(insertable)
		self.session.commit()

	def insert_cum_deaths_by_onset(self, row):
		_ = row.pop(0)
		onsetdate = extract_date(row.pop(0))
		key = row.pop(0)
		value = row.pop(0).strip()
		insertable = models.CumulativeDeathByOnsetdate(
			summaryfiledate=self.reportdate,
			onsetdate=onsetdate,
			itemname=key,
			itemvalue=value)
		self.session.add(insertable)
		self.session.commit()

	def insert_cum_cases_by_reported(self, row):
		_ = row.pop(0)
		reporteddate = extract_date(row.pop(0))
		key = row.pop(0)
		value = row.pop(0).strip()
		insertable = models.CumulativeCasesByReported(
			summaryfiledate=self.reportdate,
			reporteddate=reporteddate,
			itemname=key,
			itemvalue=value)
		self.session.add(insertable)
		self.session.commit()

	def insert_cum_hosps_by_reported(self, row):
		_ = row.pop(0)
		reporteddate = extract_date(row.pop(0))
		key = row.pop(0)
		value = row.pop(0).strip()
		insertable = models.CumulativeHospsByReported(
			summaryfiledate=self.reportdate,
			reporteddate=reporteddate,
			itemname=key,
			itemvalue=value)
		self.session.add(insertable)
		self.session.commit()

	def insert_cum_deaths_by_reported(self, row):
		_ = row.pop(0)
		reporteddate = extract_date(row.pop(0))
		key = row.pop(0)
		value = row.pop(0).strip()
		insertable = models.CumulativeDeathsByReported(
			summaryfiledate=self.reportdate,
			reporteddate=reporteddate,
			itemname=key,
			itemvalue=value)
		self.session.add(insertable)
		self.session.commit()

	def insert_deaths_by_dateofdeath(self, row):
		_ = row.pop(0)
		deathdate = extract_date(row.pop(0))
		key = row.pop(0)
		value = row.pop(0).strip()
		insertable = models.DeathsByDeathDate(
			summaryfiledate=self.reportdate,
			deathdate=deathdate,
			itemname=key,
			itemvalue=value)
		self.session.add(insertable)
		self.session.commit()

	def insert_transmission_type(self, row):
		_ = row.pop(0)
		transtype = row.pop(0)
		measure = row.pop(0)
		value = row.pop(0).strip()
		insertable = models.TransmissionType(
			summaryfiledate=self.reportdate,
			transtype=transtype,
			itemmeasure=measure,
			itemvalue=value)
		self.session.add(insertable)
		self.session.commit()

	def insert_race_and_ethnicity(self, row):
		_ = row.pop(0)
		raceandeth = row.pop(0)
		metric = row.pop(0)
		value = row.pop(0).strip()
		insertable = models.PercentRaceAndEthnicity(
			summaryfiledate=self.reportdate,
			raceeth=raceandeth,
			metric=metric,
			itemvalue=value)
		self.session.add(insertable)
		self.session.commit()

