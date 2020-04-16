import urllib.parse
from datetime import datetime, timedelta
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

import ingest.models as models
from utils.hoconfig import HoConfig

ONEDAY = timedelta(1)


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
	config = HoConfig('/etc/dh/epi.conf.example')
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


DATEFORMAT = "%Y-%m-%d"

def dtos(dateval):
	return dateval.strftime(DATEFORMAT)

def stod(strval):
	return datetime.strptime(strval, DATEFORMAT)

def generate_projected_actual():
	config = HoConfig('/etc/dh/epi.conf')
	engine = create_engine(get_sql_url(config.dbservers['LOCAL']))

	models.Base.metadata.create_all(engine)
	DBSession = sessionmaker(bind=engine)
	session = DBSession()

	allrows = session.query(models.CasesByOnsetdate).all()
	allpubs = dict()
	all_onset_dates = set()

	for onerow in allrows:
		pub_date = dtos(onerow.summaryfiledate)
		ons_date = dtos(onerow.onsetdate)
#		print(f"Reading {onerow.summaryfiledate},{onerow.onsetdate}")
		all_onset_dates.add(ons_date)
		if pub_date not in allpubs:
			allpubs[pub_date] = dict()
		allpubs[pub_date][ons_date] = onerow.itemvalue

	all_onset_dates_list = sorted(list(all_onset_dates))
	all_pub_dates_list = sorted(list(allpubs.keys()))
	maxpub = stod(max(all_pub_dates_list))

	reporting_delays = [1.0, 1.0, 1.0, 1.0, 1.0,
	                    1.0, 1.0, 1.0, 1.0, 1.0,
	                    1.0, 1.0, 1.0, 1.0, 1.0,
	                    1.0, 1.0, 1.0, 1.0, 1.0,
	                    1.0, 1.0, 1.0, 1.0, 1.0]

	for datecursor in all_onset_dates_list:
		print(f"Processing {datecursor}")
		this_dt = stod(datecursor)
		from_date = this_dt + ONEDAY
		to_date = from_date + ONEDAY
		from_str = dtos(from_date)
		to_str = dtos(to_date)
		if (from_str in allpubs and datecursor in allpubs[from_str]
				and to_str in allpubs and datecursor in allpubs[to_str]):
			print(f"to: ({to_str}) {allpubs[to_str][datecursor]} from: ({from_str}) {allpubs[from_str][datecursor]}")
		delay = 0
		while delay < len(reporting_delays) and to_date <= maxpub:
			from_str = dtos(from_date)
			to_str = dtos(to_date)

			if (from_str in allpubs and datecursor in allpubs[from_str]
					and to_str in allpubs and datecursor in allpubs[to_str]):
				from_val = float(allpubs[from_str][datecursor])
				to_val = float(allpubs[to_str][datecursor])
				offset = to_val / from_val
				reporting_delays[delay] = reporting_delays[delay] * .8 + offset * .2

			from_date = to_date
			to_date = from_date + ONEDAY
			delay += 1

	print(f"Reporting delays = {reporting_delays}")

	best_numbers = dict()
	last_report = allpubs[max(all_pub_dates_list)]
	for key, value in last_report.items():
		best_numbers[key] = value
	max_report = max(last_report.keys())
	min_report = min(last_report.keys())

	max_report_dt = stod(max_report)
	min_report_dt = stod(min_report)
	datecursor = max_report_dt
	offset_cursor = 0
	while offset_cursor < len(reporting_delays):
		date_to_adjust = dtos(datecursor)
		holder = last_report[date_to_adjust]
		for itr in range(offset_cursor, len(reporting_delays)):
			holder *= reporting_delays[itr]
		best_numbers[date_to_adjust] = holder
		datecursor -= ONEDAY
		offset_cursor += 1

	outfile = open('cum_cases_with_delay.csv', 'w')
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
	accum = 0.0
	outfile.write(f"best final")
	for itr in all_onset_dates_list:
		if itr in best_numbers:
			accum += best_numbers[itr]
		if itr < pub_date:
			outfile.write(f",{accum}")
		else:
			outfile.write(",")

	outfile.close()

if __name__ == '__main__':
	generate_projected_actual()




