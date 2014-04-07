#!/usr/bin/python
import visa
 
""" Program to return control to the scope keyboard """

test = visa.instrument("USB0::0x1AB1::0x0488::DS1BC130900036::INSTR")
test.write(":KEY:LOCK DISABLE")
test.close()
