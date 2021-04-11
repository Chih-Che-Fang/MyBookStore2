#Logger class is used to store testing log in output folder
class Logger():
	#Constructor of Logger
	def __init__(self, log_file):
		self.log_file = log_file

	#Log executed transaction or request
	#input: log message
	#output: None
	def log(self, msg):
		print(msg)
		f = open(self.log_file, 'a')
		f.write(msg)
		f.write('\n')
		f.close()