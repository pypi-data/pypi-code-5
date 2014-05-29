#!python2.5
""" Python 2.5 will not run the server using "py -2.5 -m adodbapi.server" but will run it this way"""
import adodbapi.server
adodbapi.server.serve()
