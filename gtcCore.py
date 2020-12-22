#! /usr/bin/env python
# -*- coding: utf-8 -*-
from math import sqrt
import sys

class Gcode(object):
	"""Archivo de movimiento de CNC"""
	def __init__(self, archivo):
		super(Gcode, self).__init__()
		self.archivo = archivo
		self.__velocidadActual = 0.0
		self.__X = 0.0
		self.__Y = 0.0
		self.__Z = 0.0
		self.__materialEmpleado = 0.0
		self.__longitudTotal = 0.0
		self.__tiempoTotal = 0.0

	@property
	def __posicionActual(self):
	    '''Devuelve la posicion actual como una tupla'''
	    return [self.__X, self.__Y, self.__Z]
	

	def calcDistLineal(self, final, inicial=None):
		"""Calcula y devuelve la distancia entre los puntos final e inicial.
		Si no se especifica el punto inicial se utiliza la posición actual."""
		
		if inicial == None:
			inicial = self.__posicionActual	

		dist = sqrt( (final[0]-inicial[0])**2 + (final[1]-inicial[1])**2 + (final[2]-inicial[2])**2)

		return dist

	def calcTiempo(self, dist, vel=None):
		"""Calcula y devuelve el tiempo mínimo (en segundos) que tomaría recorrer la distancia pasada, a la velocidad pasada.
		Si no se especifica la velocidad se utiliza la velocidad actual."""
		
		if vel == None:
			vel = self.__velocidadActual

		tpo = dist / vel

		return tpo

	def setPosicion(self, pos):
		"""Establece pos como la posición actual. El parametro pos debe ser tipo (X, Y, Z) donde cada elemento es de tipo float """

		self.__X = pos[0]
		self.__Y = pos[1]
		self.__Z = pos[2]

		return self.__posicionActual

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

	def updateMaterialEmpleado(self, dist):
		"""Actualiza la cantidad de material empleado"""

		self.__materialEmpleado = self.__materialEmpleado + dist

	def getMaterialEmpleado(self):
		"""Devuelve la cantidad total de material"""

		return self.__materialEmpleado

	def parsearLinea(self, linea):
		"""Recibe una linea del archivo y devuelve una 3-upla donde el primer elemento es el comando, el segundo elemento es otra n-upla con los argumentos y el tercer elemento es el comentario.
		Si alguna de las partes no existe entonces el elemento correspondiente a esa parte es una cadena vacía"""

		comando = ''
		parametros = ''
		comentario = ''

		instruccion, sep, comentario = linea.partition(';')

		# Elimino los espacios al principio y al final si los hubiera
		instruccion = instruccion.strip()
		comentario = comentario.strip()

		if instruccion != '':  # Si existe la instruccion (o sea que la linea no es un comentario toda entera)
			instElem = instruccion.split(' ')  # Cada elemento de la instruccion lo pongo como elemento de una lista

			# La lista tiene al menos 1 elemento que es el comando, y si tiene mas son parametros
			comando = instElem[0]
			if len(instElem)>1:
				listParams =  instElem[1:]

				# Parseo los parametros para que queden como diccionario
				parametros = self.parsearParametros(listParams)

		return comando, parametros, comentario

	def parsearGcode(self):
		"""Recorre el archivo línea por línea para encontrar los movimientos y calcular el tiempo y distancia recorrida"""

		arch = open(self.archivo, "r")

		l = 0

		for linea in arch:

			comando, parametros, comentario = self.parsearLinea(linea)
			l = l + 1

			if parametros != '':

				if comando == 'G1':  # Para hacer movimiento
					if 'F' in parametros:  # si hay cambio de velocidad
						self.setVelocidad(parametros['F'])

					# Punto de destino
					destino = self.__posicionActual # inicializo

					# Cargo la posicion nueva
					if 'X' in parametros:  
						destino[0] = parametros['X']
					if 'Y' in parametros:
						destino[1] = parametros['Y']
					if 'Z' in parametros:
						destino[2] = parametros['Z']

					# Calculo la distancia 
					dist = self.calcDistLineal(destino)
					# Sumo a la distancia total
					self.updateLongitudTotal(dist)

					# Calculo el tiempo empleado
					tpo = self.calcTiempo(dist)
					# Sumo al tiempo total
					self.updateTiempoTotal(tpo)


					# Actualizo el material empleado
					if 'E' in parametros:
						self.updateMaterialEmpleado(parametros['E'])

		arch.close()

		print l, " lineas procesadas"
		print "Distancia recorrida [mm]: ", self.getLongitudTotal()
		print "Tiempo empleado [min]: ", self.getTiempoTotal()/60
		print "Material utilizado [mm]: ", self.getMaterialEmpleado()


	def parsearParametros(self, listaParametros):
		"""Devuelve un diccionario con los parámetros y valores"""
		
		param = {}

		for p in listaParametros:
			param[p[0]] = float(p[1:])

		return param

if __name__ == '__main__':
	
	# Para uso como programa
	a = Gcode(sys.argv[1])
	a.parsearGcode()
