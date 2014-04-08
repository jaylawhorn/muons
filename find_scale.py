#!/usr/bin/python
import math
import numpy
import array
import matplotlib.pyplot as plot
import visa
from time import sleep

def scopewrite(str):
    scope.write(str)
    sleep(.2) 

def scopereadout(n):
    scopewrite(":WAV:POIN:MODE RAW")
    scopewrite(":ACQ:MEMD LONG")
    scopewrite(":WAV:DATA? CHAN"+str(n))
    rawdata = scope.read()
    if rawdata!='':
        data = numpy.frombuffer(rawdata, 'B')
        data = data[range(data.size-1202, data.size,2)]
        data = data * -1 + 255
        return math.fsum(data)/data.size
    else: return -1


# Initialize our scope
print visa.get_instruments_list()
scope = visa.instrument("USB0::0x1AB1::0x0488::DS1BC130900036::INSTR")

scopewrite(':ACQ:MEMD LONG') # Long memory type
scopewrite(':CHAN1:COUP DC') # DC coupling
scopewrite(':CHAN2:COUP DC') # DC coupling
scopewrite(':CHAN3:COUP DC') # DC coupling
scopewrite(':CHAN1:DISP ON') 
scopewrite(':CHAN2:DISP ON') 
scopewrite(':CHAN3:DISP ON') 
scopewrite(':CHAN1:SCAL 5') 
scopewrite(':CHAN1:OFFS 20') 
scopewrite(':CHAN2:SCAL 5')
scopewrite(':CHAN2:OFFS 0')  
scopewrite(':CHAN3:SCAL 5')
scopewrite(':CHAN3:OFFS -15')  
scopewrite(':TIM:SCAL .000002') # 2microsec
#scopewrite(":TRIG:EDGE:SOUR CHAN1")
#scopewrite(':TRIG:EDGE:SWE SING') # Single trigger
#scopewrite(':TRIG:EDGE:COUP DC') # DC trigger coupling
#scopewrite(':TRIG:EDGE:SLOP NEG') # Trigger on negative edge
#scopewrite(':TRIG:EDGE:LEV 2.5') # Trigger at 2.5 volts

#scopewrite(":RUN")
sleep(1)

#sample_rate = scope.ask_for_values(':ACQ:SAMP?')[0]

n = 0; # Number of coincidence events

while (n<1):
	# Wait until the scope is triggered:
	scopewrite(":TRIG:STAT?")
	status = scope.read();
	#if not status=="T'D":
		#print 'Not triggered!'
		#continue
	n = n+1 # Increment the event counter
	
	# Stop data acquisition so that we can take all the data at the same instant
	scopewrite(":STOP")

        val1=scopereadout(1)
        val2=scopereadout(2)
        val3=scopereadout(3)
        val4=scopereadout(4)

        print val1, val2, val3, val4

        print "val2 = ", val2, " = 0 " 
        print "(val1-val2) = ", (val1-val2), " = (20-0)"
        print 20/(val1-val2), "*( x - ", val2, ")"
        print
        print "val1 = ", 20/(val1-val2)*(val1-val2)
        print "val2 = ", 20/(val1-val2)*(val2-val2)

        '''
	# Now, generate a time axis.  The scope display range is 0-600, with 300 being
	# time zero.
	time = numpy.arange(-300.0/50*timescale, 300.0/50*timescale, timescale/50.0)
	
	# Open a file and record the data
	print 'Saving a coincidence event...'
	f = open('event_' + str(n),'w')
	for x in range(len(time)):
		f.write(str(time[x]) + '\t' + str(data1[x]) + '\t' + str(data2[x]) + '\t' + str(data3[x]) + '\t' + str(data4[x]) + '\n')
	f.close()
	'''	

	# Start data acquisition again
	scopewrite(":RUN")
	# Wait to allow the scope to recover
	sleep(2)

# Put the scope back in local mode and close the handle to the scope
scopewrite(":KEY:FORC")
scopewrite(":KEY:LOCK DISABLE")
scope.close()
