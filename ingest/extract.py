import urllib.parse
from datetime import datetime
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

import ingest.models as models
from utils.hoconfig import HoConfig


def get_sql_url(dbspec):
	if dbspec['ENGINE'] == 'mssql':
		return f"mssql+pyodbc://{dbspec['USER']}:{urllib.parse.quote(dbspec['PASSWORD'])}@{dbspec['DSN']}"
	elif dbspec['ENGINE'] == 'mysql':
		constr = f"mysql+pymysql://{dbspec['USER']}:{urllib.parse.quote(dbspec['PASSWORD'])}@{dbspec['HOST']}/{dbspec['DATABASE']}"
		print(f"Connection string: {constr}")
		return constr
	# sooooo many problems with odbc
#		return f"mysql+pyodbc://{dbspec['USER']}:{urllib.parse.quote(dbspec['PASSWORD'])}@{dbspec['DSN']}"


def extract_case_counts_by_reported():
	config = HoConfig('/etc/dh/epi.conf')
	engine = create_engine(get_sql_url(config.dbservers['LOCAL']))

	models.Base.metadata.create_all(engine)
	DBSession = sessionmaker(bind=engine)
	session = DBSession()

	allrows = session.query(models.CasesByOnsetdate).all()
	allpubs = dict()
	all_onset_dates = set()

	for onerow in allrows:
		pub_date = onerow.summaryfiledate.strftime("%Y-%m-%d")
		ons_date = onerow.onsetdate.strftime("%Y-%m-%d")
#		print(f"Reading {onerow.summaryfiledate},{onerow.onsetdate}")
		all_onset_dates.add(ons_date)
		if pub_date not in allpubs:
			allpubs[pub_date] = dict()
		allpubs[pub_date][ons_date] = onerow.itemvalue

	all_onset_dates_list = sorted(list(all_onset_dates))
	all_pub_dates_list = sorted(list(allpubs.keys()))

	outfile = open('cum_cases_by_reported_by_published.csv', 'w')
	outfile.write("publisheddate")

	for itr in all_onset_dates_list:
		outfile.write(f",{itr}")
	outfile.write("\n")

	for pub_date in all_pub_dates_list:
		accum = 0.0
		outfile.write(f"{pub_date}")
		onsetvals = allpubs[pub_date]
		for itr in all_onset_dates_list:
			if itr in onsetvals:
				accum += onsetvals[itr]
			if itr < pub_date:
				outfile.write(f",{accum}")
			else:
				outfile.write(",")

		outfile.write("\n")
	outfile.close()

if __name__ == '__main__':
	extract_case_counts_by_reported()




