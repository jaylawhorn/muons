#!/usr/bin/python
import numpy
import matplotlib.pyplot as plot
 
import visa
 
""" Example program to plot the Y-T data from Channel 1 """
 
# Initialize our scope
print visa.get_instruments_list()
test = visa.instrument("USB0::0x1AB1::0x0488::DS1BC130900036::INSTR")

# Stop data acquisition
test.write(":STOP")

# Grab the raw data
test.write(":WAV:POIN:MODE NOR")
test.write(":WAV:DATA? CHAN1")
rawdata1 = test.read()
print "channel 1"
print rawdata1

test.write(":WAV:DATA? CHAN2")
rawdata2 = test.read()
print "channel 2"
print rawdata2

# Process the data into numerical form
data1 = numpy.frombuffer(rawdata1, 'B')
data2 = numpy.frombuffer(rawdata2, 'B')

# Every other data point is a blank value -- clear these out
data1 = data1[range(data1.size-1202,data1.size,2)]
data2 = data2[range(data2.size-1202,data2.size,2)]

#print data1
#print data2
#print 

# Get the voltage scale
test.write(":CHAN1:SCAL?")
voltscale = float(test.read())
 
# And the voltage offset
test.write(":CHAN1:OFFS?")
voltoffset = float(test.read())
 
# Walk through the data, and map it to actual voltages
# First invert the data (ya rly)
data1 = data1 * -1 + 255
data2 = data2 * -1 + 255
 
# Now, we know from experimentation that the scope display range is actually
# 30-229.  So shift by 130 - the voltage offset in counts, then scale to
# get the actual voltage.
data1 = (data1 - 130.0 - voltoffset/voltscale*25) / 25 * voltscale
#print
#print data1

data2 = (data2 - 130.0 - voltoffset/voltscale*25) / 25 * voltscale
#print
#print data2

# Get the timescale
test.write(":TIM:SCAL?")
timescale = float(test.read())
 
# Get the timescale offset
test.write(":TIM:OFFS?")
timeoffset = float(test.read())
 
# Now, generate a time axis.  The scope display range is 0-600, with 300 being
# time zero.
time = numpy.arange(-300.0/50*timescale, 300.0/50*timescale, timescale/50.0)
#time = numpy.arange(1,data2.size+1)

print time.size, data1.size
print time.size, data2.size
 
# If we generated too many points due to overflow, crop the length of time.
if (time.size > data1.size):
    time = time[0:600:1]
 
# See if we should use a different time axis
if (time[599] < 1e-3):
    time = time * 1e6
    tUnit = "uS"
elif (time[599] < 1):
    time = time * 1e3
    tUnit = "mS"
else:
    tUnit = "S"

# Plot the data
plot.plot(time, data1, 'b.-')
plot.title("Oscilloscope Channel 1")
plot.ylabel("Voltage (V)")
plot.xlabel("Time (" + tUnit + ")")
#plot.xlim(time[0], time[599])
plot.show()

# Start data acquisition again, and put the scope back in local mode
test.write(":RUN")
test.write(":KEY:FORC")
test.write(":KEY:LOCK DISABLE")
test.close()
