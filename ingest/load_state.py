

from os import listdir
from os.path import isfile, join

from ingest.coviddatastore import CovidDatastore
from utils.hoconfig import HoConfig


def main():
	config = HoConfig('/etc/dh/epi.conf')
	datastore = CovidDatastore(config.dbservers['TEST'])
	filelist = [f for f in listdir('data') if isfile(join('data', f))]
	for filename in filelist:
		if not datastore.is_loaded(filename):
			try:
				datastore.load(filename)
			except Exception as exp:
				print(f"Error when processing file {filename}")
				raise exp



if __name__ == '__main__':
	main()
