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
		self.__X = None # 0.0
		self.__Y = None # 0.0
		self.__Z = None # 0.0
		self.__E = 0.0  # Posicion del filamento
		self.__materialEmpleado = 0.0
		self.__retraccion = 0.0  # Si hay una retraccion ,primero hay que compensarla antes de sumar material como empleado
		self.__modoExtrusorRelativo = False  # El eje extrusor tiene coordenadas relativas sin importar el modo de los otros ejes
		self.__modoRelativo = False  # Todos los ejes son relativos. 
		self.__distanciaTotalRecorrida = 0.0
		self.__tiempoTotal = 0.0
		self.__lineasProcesadas = 0
		self.__sistemaMetrico = True  # Establece mm, mm/s y mm/s2 cuando es True. Si es False las unidades son pulg, pulg/s, y pulg/s2

	@property
	def __posicionActual(self):
	    '''Devuelve la posicion actual como una tupla'''
	    return [self.__X, self.__Y, self.__Z]

	def lineasProcesadas(self):
		'''Devuelve la cantidad de lineas procesadas por el parser'''
		return self.__lineasProcesadas
	

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

	def setModoExtrusor(self, relativo):
		''' Define el modo de movimiento del extrusor'''
		self.__modoExtrusorRelativo = relativo
		return relativo

	def setModoPosicionamiento(self, relativo):
		''' Define el modo de movimiento de todos los ejes'''
		self.__modoRelativo = relativo
		return relativo


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

	def updateDistanciaTotal(self, dist):
		"""Aumenta la distancia total la cantidad indicada en dist"""

		self.__distanciaTotalRecorrida = self.__distanciaTotalRecorrida + dist

	def getDistanciaTotal(self):
		"""Devuelve la distancia total calculada"""

		return self.__distanciaTotalRecorrida

	def updateMaterialEmpleado(self, val):
		"""Actualiza la cantidad de material empleado"""

		if not self.__modoExtrusorRelativo:  # Si val no es un valor relativo lo transformo en relativo para el calculo siguiente
			dist = val - self.__E
		else:
			dist = val


		# Siendo dist un valor relativo, continuo 

		self.__E = self.__E + dist      # Posicion del material

		cant = dist + self.__retraccion  # Verifico si salio algo de material por el nozzle

		if cant <= 0:
			self.__retraccion = cant  # Si cantidad es negativo, entonces ese valor es toda la retraccion que tiene el material
		else:
			# Si cantidad es positivo, entonces no hay retraccion y ese valor es el material usado
			self.__retraccion = 0
			self.__materialEmpleado = self.__materialEmpleado + cant

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

			if parametros != '':  # Realizar acciones segun los parametros

				if (comando == 'G1') | (comando == 'G0'):  # Para hacer movimiento
					if 'F' in parametros:  # si hay cambio de velocidad
						self.setVelocidad(parametros['F'])

					# Punto de destino
					destino = self.__posicionActual # inicializo con la pos actual por si alguno de los ejes no hay que modificarlo

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
					self.updateDistanciaTotal(dist)

					# Calculo el tiempo empleado
					tpo = self.calcTiempo(dist)
					# Sumo al tiempo total
					self.updateTiempoTotal(tpo)


					# Actualizo el material empleado
					if 'E' in parametros:
						self.updateMaterialEmpleado(parametros['E'])

				if (comando == 'G4') | (comando == 'M0') | (comando == 'M1'):   # Hace una pausa por un tiempo determinado
					if 'S' in parametros:  # Si estan definidos los segundos, toma importancia este valor sin importar P
						self.updateTiempoTotal(float(parametros['S']))
					elif 'P' in parametros:  # Si solo está P, entonces el valor es en milisegundos
						self.updateTiempoTotal(float(parametros['P'])/1000)

				if comando == 'G28':  # Hace homing
					home = True # bandera para hacer home
					homeCompleto = False # Bandera para home en todos los ejes si o si

					if 'O' in parametros:  # Si la posicion es conocida entonces cancela el homing
						if (self.__X != None) & (self.__Y != None) & (self.__Z != None):
							home = False
						else:
							homeCompleto = True

					if home:
						if (not('X' in parametros) and not('Y' in parametros) and not('Z' in parametros)) | homeCompleto:
							self.__X = 0.0
							self.__Y = 0.0
							self.__Z = 0.0
						else:
							if 'X' in parametros:  
								self.__X = 0.0
							if 'Y' in parametros:
								self.__Y = 0.0
							if 'Z' in parametros:
								self.__Z = 0.0

				if comando == 'G92':  # Establece los ejes al valor indicado

					if 'E' in parametros:
						self.__E == flaot(parametros['E'])
					if 'X' in parametros:
						self.__X == flaot(parametros['X'])
					if 'Y' in parametros:
						self.__Y == flaot(parametros['Y'])
					if 'Z' in parametros:
						self.__Z == flaot(parametros['Z'])
					

			else:  # Realizar acciones cuando no hay parametros

				if comando == 'G20':  # Pone las unidades en pulgadas
					
					self.__sistemaMetrico = False

				if comando == 'G21':  # Pone las unidades en mm

					self.__sistemaMetrico = True

				if comando == 'G28':  # Hace homing completo si o si
					self.__X = 0.0
					self.__Y = 0.0
					self.__Z = 0.0

				if (comando == 'G4') | (comando == 'M400'):  # Termina de hacer los movimientos de la lista de planeados y hace una pausa hasta que el usuario continue
					
					pass  # No hago nada xq el tiempo es indeterminado

				if comando == 'M82':  # Pone solo el extrusor en modo absoluto

					self.__modoExtrusorRelativo = False
					
				if comando == 'M83':  # Pone solo el extrusor en modo relativo
					
					self.__modoExtrusorRelativo = True
					
				if comando == 'G90':  # Pone todos los ejes en modo absoluto (inclusive el extrusor)
					self.__modoExtrusorRelativo = False
					self.__modoRelativo = False

				if comando == 'G91':  # Pone todos los ejes en modo relativo (inclusive el extrusor)
					self.__modoExtrusorRelativo = True
					self.__modoRelativo = True



		arch.close()

		self.__lineasProcesadas = l

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
	print(a.lineasProcesadas(), " lineas procesadas")
	print("Distancia recorrida [mm]: ", a.getDistanciaTotal())
	print("Tiempo empleado [seg]: ", a.getTiempoTotal()*60)
	print("Material utilizado [mm]: ", a.getMaterialEmpleado())
