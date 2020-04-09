

from os import listdir
from os.path import isfile, join

from ingest.coviddatastore import CovidDatastore
from utils.hoconfig import HoConfig


def main():
	config = HoConfig('/etc/dh/epi.conf')
	datastore = CovidDatastore(config.dbservers['LOCAL'])
	filelist = [f for f in listdir('data') if isfile(join('data', f))]
	for filename in filelist:
		if not datastore.is_loaded(filename):
			datastore.load(filename)



if __name__ == '__main__':
	main()
