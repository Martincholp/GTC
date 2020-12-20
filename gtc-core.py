#! /usr/bin/env python
# -*- coding: utf-8 -*-

class Gcode(object):
	"""Archivo de movimiento de CNC"""
	def __init__(self, archivo):
		super(Gcode, self).__init__()
		self.archivo = archivo
		self.__velocidadActual = 0
		self.__posicionActual = (0,0)
		self.__longitud = 0

		
		

