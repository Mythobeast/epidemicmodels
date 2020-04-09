
from pathlib import Path

from pyhocon import ConfigFactory

from dhutil.dhlog import getlog

CONFIGLIST=dict()

class HoConfig:
	class __HoConfig:
		def __init__(self, filename):
			self.val = ConfigFactory.parse_file(filename)
#			print ("Retrieved: %s" % self.val.get(root))
		def __str__(self):
			return repr(self) + self.val
		def __getattr__(self, name):
			return self.val[name]
		def __getitem__(self, name):
			return self.val[name]

	instance = None

	def __init__(self, filename):
		if filename in CONFIGLIST:
			HoConfig.instance = CONFIGLIST[filename]
		else:
			filechecker = Path(filename)
			if not filechecker.is_file():
				# Create an empty file, log a warning
				open(filename, 'a').close()
				getlog('config').error(f"Configuration file {filename} not found. Expect issues.")

			HoConfig.instance = HoConfig.__HoConfig(filename)
			CONFIGLIST[filename] = HoConfig.instance

	def __getitem__(self, name):
		return self.instance.__getattr__(name)

	def __getattr__(self, name):
		return self.instance.__getattr__(name)


def test():
#	tester = CherConf('../../resources/config.hocon')
#	tester2 = CherConf('../../resources/config.hocon')
#	print ("tester1: %s" % tester.get('objects.Incident.name'))
#	tester.put('objects.Incident.name', "wrongthing")
#	print ("tester1: %s" % tester.get('objects.Incident.name'))
#	print ("tester1: %s" % tester2.get('objects.Incident.name'))

	tester = HoConfig()
	tester2 = HoConfig()
	print ("tester1: %s" % tester.get('objects.Incident.name'))
	tester.put('objects.Incident.name', "wrongthing")
	print ("tester1: %s" % tester.get('objects.Incident.name'))
	print ("tester1: %s" % tester2.get('objects.Incident.name'))

if __name__ == '__main__':
	test()
