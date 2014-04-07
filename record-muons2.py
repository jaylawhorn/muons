#!/usr/bin/python
import numpy
import matplotlib.pyplot as plot
import visa
from time import sleep
 
""" Record coincidence events from the PMTs using an external coincidence trigger connected to the scope """
 
# Initialize our scope
print visa.get_instruments_list()
test = visa.instrument("USB0::0x1AB1::0x0488::DS1BC130900036::INSTR")

# Get scale and offset parameters
test.write(":CHAN1:SCAL?")
voltscale = float(test.read())
test.write(":CHAN1:OFFS?")
voltoffset = float(test.read())
test.write(":TIM:SCAL?")
timescale = float(test.read())
test.write(":TIM:OFFS?")
timeoffset = float(test.read())

#
# Set up triggering parameters
# Add this in once we examine the coincidence unit
#
 
n = 0; # Number of coincidence events

while True:
	# Wait until the scope is triggered:
	test.write(":TRIG:STAT?")
	status = test.read();
	if not status=="T'D":
		#print 'Not triggered!'
		continue
	n = n+1 # Increment the event counter
	
	# Stop data acquisition so that we can take all the data at the same instant
	test.write(":STOP")
	
	# Grab the raw data
	test.write(":WAV:POIN:MODE NOR")
	test.write(":WAV:DATA? CHAN1")
	rawdata1 = test.read()
#	print "channel 1"
#	print rawdata1

	test.write(":WAV:DATA? CHAN2")
	rawdata2 = test.read()
#	print "channel 2"
#	print rawdata2

	# Process the data into numerical form
	data1 = numpy.frombuffer(rawdata1, 'B')
	data2 = numpy.frombuffer(rawdata2, 'B')

	# Every other data point is a blank value -- clear these out
	data1 = data1[range(data1.size-1202,data1.size,2)]
	data2 = data2[range(data2.size-1202,data2.size,2)]

	# Walk through the data, and map it to actual voltages
	# First invert the data (ya rly)
	data1 = data1 * -1 + 255
	data2 = data2 * -1 + 255
	
	# NOTE: these scale factors are not working for me--are you sure they're right? -SLE
	
	# Now, we know from experimentation that the scope display range is actually
	# 30-229.  So shift by 130 - the voltage offset in counts, then scale to
	# get the actual voltage.
	data1 = (data1 - 130.0 - voltoffset/voltscale*25) / 25 * voltscale
	data2 = (data2 - 130.0 - voltoffset/voltscale*25) / 25 * voltscale
	
	# Now, generate a time axis.  The scope display range is 0-600, with 300 being
	# time zero.
	time = numpy.arange(-300.0/50*timescale, 300.0/50*timescale, timescale/50.0)
	
	# Open a file and record the data
	print 'Saving a coincidence event...'
	f = open('event_' + str(n),'w')
	for x in range(len(time)):
		f.write(str(time[x]) + '\t' + str(data1[x]) + '\t' + str(data2[x]) + '\n')
	f.close()
	
	# Start data acquisition again
	test.write(":RUN")
	# Wait to allow the scope to recover
	sleep(2)

# Put the scope back in local mode and close the handle to the scope
test.write(":KEY:FORC")
test.write(":KEY:LOCK DISABLE")
test.close()
