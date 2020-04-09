
import csv

from datetime import datetime

import urllib.parse
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from ingest.models import Base, CaseSummaryFile, StateData, CasesByCounty
from ingest.models import DeathsBySex, CasesByOnsetdate, DeathsByCounty, CasesByAHD, PositivityData, CumulativeCasesByOnsetdate
from ingest.models import CumulativeHospByOnsetdate, CumulativeDeathByOnsetdate
from ingest.models import CumulativeCasesByReported, CumulativeHospsByReported, CumulativeDeathsByReported


def pop_column(self, row):
	startquote = row.find('"')
	endquote = row.find('"', startquote + 1)
	return row[startquote+1:endquote], row[endquote+2:]



class CovidDatastore:
	def __init__(self, dbspec):
		if dbspec['ENGINE'] == 'mysql':

		elif dbspec['ENGINE'] == 'mysql':
		sql_url = f"mssql+pyodbc://%s:%s@%s" % (
			dbspec['USER'], urllib.parse.quote(dbspec['PASSWORD']),
			dbspec['DSN'])

		engine = create_engine(
		                "mysql://{dbspec['USER']}:{dbspec['PASSWORD']}@{dbspec['HOST']}/{dbspec['DATABASE']}",
		                isolation_level="READ UNCOMMITTED"
		            )
		self.engine = create_engine(sql_url)

		Base.metadata.create_all(self.engine)
		self.DBSession = sessionmaker(bind=self.engine)
		self.session = self.DBSession()
		self.reportdate = None

		self.handlers = dict()
		self.assign_handlers()

	def assign_handlers(self):
		self.handlers['State Data'] = self.insert_state_data
		self.handlers['Case Counts by County'] = self.insert_cases_by_county
		self.handlers['Case Counts by Age Group'] = self.insert_cases_by_agegrp
		self.handlers['Case Counts by Sex'] = self.insert_cases_by_sex
		self.handlers['Fatal cases by sex'] = self.insert_deaths_by_sex
		self.handlers['Case Counts by Onset Date'] = self.insert_case_counts_by_onset
		self.handlers['Deaths'] = self.insert_deaths_by_county
		self.handlers['"Case Counts by Age Group'] = self.insert_case_counts_by_ahd
		self.handlers['Positivity Data from Clinical Laboratories'] = self.insert_positivity_data
		self.handlers['Cumulative Number of Cases by Onset Date'] = self.insert_cum_cases_by_onset
		self.handlers['Cumulative Number of Hospitalizations by Onset Date'] = self.insert_cum_hosp_by_onset
		self.handlers['Cumulative Number of Deaths by Onset Date'] = self.insert_cum_deaths_by_onset
		self.handlers['Cumulative Number of Cases by Reported Date'] = self.insert_cum_cases_by_reported
		self.handlers['Cumulative Number of Hospitalizations by Reported Date'] = self.insert_cum_hosps_by_reported
		self.handlers['Cumulative Number of Deaths by Reported Date'] = self.insert_cum_deaths_by_reported

	def is_loaded(self, filename):
		fileset = self.session.query(CaseSummaryFile).filter(CaseSummaryFile.filename==filename)
		if len(fileset) == 0:
			return False
		if fileset[0].state != 'loaded':
			return False
		return True

	def load(self, filename):
		fname, extension = filename.split('.')
		covid19, case, summary, reportdate = fname.split('_')
		self.reportdate = datetime.strptime(reportdate, '%Y-%m-%d')
		with open(filename) as fp:
			for oneline in fp:
				parts = oneline.split(',')
				self.insert(parts)

	def insert(self, row):
		if row[0] == 'description' or row[1] == 'Note':
			return
		return self.handlers[row[0]](row)

	def insert_state_data(self, row):
		key, value = row[2:]
		insertable = StateData(summaryfiledate=self.reportdate, itemname=key, itemvalue=value)
		self.session.add(insertable)
		self.session.commit()

	def insert_cases_by_county(self, row):
		countyname, key, value = row[1:]
		if value == 'NA':
			value = None
		insertable = CasesByCounty(
			summaryfiledate=self.reportdate,
			county=countyname,
			itemname=key,
			itemvalue=value)
		self.session.add(insertable)
		self.session.commit()

	def insert_cases_by_agegrp(self, row):
		agegroup, key, value = row[1:]
		if value == 'NA':
			value = None
		insertable = CasesByCounty(
			summaryfiledate=self.reportdate,
			agegroup=agegroup,
			itemname=key,
			itemvalue=value)
		self.session.add(insertable)
		self.session.commit()

	def insert_cases_by_sex(self, row):
		sex, key, value = row[1:]
		if value == 'NA':
			value = None
		insertable = CasesByCounty(
			summaryfiledate=self.reportdate,
			sex=sex,
			itemname=key,
			itemvalue=value)
		self.session.add(insertable)
		self.session.commit()

	def insert_deaths_by_sex(self, row):
		sex, key, value = row[1:]
		if value == 'NA':
			value = None
		insertable = DeathsBySex(
			summaryfiledate=self.reportdate,
			sex=sex,
			itemname=key,
			itemvalue=value)
		self.session.add(insertable)
		self.session.commit()

	def insert_case_counts_by_onset(self, row):
		onsetdate, key, value = row[1:]
		onsetdate = datetime.strptime(onsetdate, '%Y-%m-%d')
		insertable = CasesByOnsetdate(
			summaryfiledate=self.reportdate,
			onsetdate=onsetdate,
			itemname=key,
			itemvalue=value)
		self.session.add(insertable)
		self.session.commit()

	def insert_deaths_by_county(self, row):
		county, key, value = row[1:]
		insertable = DeathsByCounty(
			summaryfiledate=self.reportdate,
			county=county,
			itemname=key,
			itemvalue=value)
		self.session.add(insertable)
		self.session.commit()

	def insert_case_counts_by_ahd(self, row):
		# this row has quotes in the names
		fullrow = ",".join(row)
		_, fullrow = pop_column(fullrow)
		grouping, fullrow = pop_column(fullrow)
		agegroup, hospitalization = grouping.split(',')
		cases, count = fullrow.split(',')
		insertable = CasesByAHD(
			summaryfiledate=self.reportdate,
			agegroup=agegroup,
			hospitalization=hospitalization,
			itemvalue=count)
		self.session.add(insertable)
		self.session.commit()

	def insert_positivity_data(self, row):
		testdate, key, value = row[1:]
		testdate = datetime.strptime(testdate, '%Y-%m-%d')
		if value == 'NA':
			value = None

		insertable = PositivityData(
			summaryfiledate=self.reportdate,
			testdate=testdate,
			itemname=key,
			itemvalue=value)
		self.session.add(insertable)
		self.session.commit()

	def insert_cum_cases_by_onset(self, row):
		onsetdate, key, value = row[1:]
		onsetdate = datetime.strptime(onsetdate, '%Y-%m-%d')
		insertable = CumulativeCasesByOnsetdate(
			summaryfiledate=self.reportdate,
			onsetdate=onsetdate,
			itemname=key,
			itemvalue=value)
		self.session.add(insertable)
		self.session.commit()

	def insert_cum_hosp_by_onset(self, row):
		onsetdate, key, value = row[1:]
		onsetdate = datetime.strptime(onsetdate, '%Y-%m-%d')
		insertable = CumulativeHospByOnsetdate(
			summaryfiledate=self.reportdate,
			onsetdate=onsetdate,
			itemname=key,
			itemvalue=value)
		self.session.add(insertable)
		self.session.commit()

	def insert_cum_deaths_by_onset(self, row):
		onsetdate, key, value = row[1:]
		onsetdate = datetime.strptime(onsetdate, '%Y-%m-%d')
		insertable = CumulativeDeathByOnsetdate(
			summaryfiledate=self.reportdate,
			onsetdate=onsetdate,
			itemname=key,
			itemvalue=value)
		self.session.add(insertable)
		self.session.commit()

	def insert_cum_cases_by_reported(self, row):
		reporteddate, key, value = row[1:]
		reporteddate = datetime.strptime(reporteddate, '%Y-%m-%d')
		insertable = CumulativeCasesByReported(
			summaryfiledate=self.reportdate,
			reporteddate=reporteddate,
			itemname=key,
			itemvalue=value)
		self.session.add(insertable)
		self.session.commit()

	def insert_cum_hosps_by_reported(self, row):
		reporteddate, key, value = row[1:]
		reporteddate = datetime.strptime(reporteddate, '%Y-%m-%d')
		insertable = CumulativeHospsByReported(
			summaryfiledate=self.reportdate,
			reporteddate=reporteddate,
			itemname=key,
			itemvalue=value)
		self.session.add(insertable)
		self.session.commit()

	def insert_cum_deaths_by_reported(self, row):
		reporteddate, key, value = row[1:]
		reporteddate = datetime.strptime(reporteddate, '%Y-%m-%d')
		insertable = CumulativeDeathsByReported(
			summaryfiledate=self.reportdate,
			reporteddate=reporteddate,
			itemname=key,
			itemvalue=value)
		self.session.add(insertable)
		self.session.commit()


