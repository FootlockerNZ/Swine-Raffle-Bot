import time
import sys
import threading
import colorama

lock = threading.Lock()
colorama.init()


class logger:
	def __init__(self):
		self.colours = {
			"error" 		: "[91m",
			"success" 		: "[92m",
			"info" 			: "[96m",
			"debug" 		: "[95m",
			"yellow" 		: "[93m",
			"lightpurple" 	: "[94m",
			"lightgray" 	: "[97m",
			"clear"			: "[00m"
		}

	def log(self, message="", color="", shown=True, showtime=True, nocolor=""):
		currentTime = time.strftime("%H:%M:%S")
		try:
			colourString = self.colours[color]
		except:
			colourString = ""
		if showtime:
			timestring = "[%s] " % currentTime
		else:
			timestring = ""

		messageString = str(message) + self.colours['clear']
		noColourString = str(message)

		store = "[SWINE RAFFLES] "

		if nocolor:
			messageString += ": %s" % nocolor 
			noColourString += ": %s" % nocolor 
        
		finalString = timestring+colourString+store+str(messageString)+"\n"

		with lock:
			sys.stdout.write(finalString)
			sys.stdout.flush()
        