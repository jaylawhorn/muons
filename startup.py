#!/usr/bin/python
import visa
 
""" Program to connect to the scope and return control to the command line. Only run in -i mode! """

test = visa.instrument("USB0::0x1AB1::0x0488::DS1BC130900036::INSTR")
