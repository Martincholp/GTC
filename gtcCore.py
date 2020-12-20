#! /usr/bin/env python
# -*- coding: utf-8 -*-
from math import sqrt

class Gcode(object):
	"""Archivo de movimiento de CNC"""
	def __init__(self, archivo):
		super(Gcode, self).__init__()
		self.archivo = archivo
		self.__velocidadActual = 0
		self.__posicionActual = (0,0)
		self.__longitudTotal = 0
		self.__tiempoTotal = 0

	def calcDistLineal(self, final, inicial=None):
		"""Calcula y devuelve la distancia entre los puntos final e inicial.
		Si no se especifica el punto inicial se utiliza la posición actual."""
		
		if inicial == None:
			inicial = self.__posicionActual	

		dist = sqrt( (final[0]-inicial[0])**2 + (final[1]-inicial[1])**2)

		return dist

	def calcTiempo(self, dist, vel=None):
		"""Calcula y devuelve el tiempo mínimo (en segundos) que tomaría recorrer la distancia pasada, a la velocidad pasada.
		Si no se especifica la velocidad se utiliza la velocidad actual."""
		
		if vel == None:
			vel = self.__velocidadActual

		tpo = dist / vel

		return tpo

	def setPosicion(self, pos):
		"""Establece pos como la posición actual"""

		self.__posicionActual = pos

		return pos

	def setVelocidad(self, vel):
		"""Establece vel como la velocidad actual"""

		self.__velocidadActual = vel

		return vel

	def updateTiempoTotal(self, tpo):
		"""Aumenta en el tiempo total la cantidad de segundo indicada en tpo"""

		self.__tiempoTotal = self.__tiempoTotal + tpo

	def getTiempoTotal(self):
		"""Devuelve el tiempo total calculado"""

		return self.__tiempoTotal

	def updateLongitudTotal(self, dist):
		"""Aumenta la longitud total la cantidad indicada en dist"""

		self.__longitudTotal = self.__longitudTotal + dist

	def getLongitudTotal(self):
		"""Devuelve la longitud total calculada"""

		return self.__longitudTotal