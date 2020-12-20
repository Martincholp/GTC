[estado]: /estado.md/ "estado del proyecto"

# GTC #
G-code time calc

## Que es GTC? ##

GTC es un script de python que analiza un archivo G-code generado por un slicer (tales como Cura, Simplify3D, Slic3r, etc) y calcula el tiempo que tardaría una impresora 3D en ejecutar la pieza.

## Como funciona? ##

Se puede utilizar la linea de comandos pasando como primer argumento la URL del G-code a analizar y devolverá el tiempo que llevaría su impresión y la distancia recorrida por el extrusor. Cabe aclarar que esta distancia no es la cantidad de filamento a utilizar, ya que también están incluidos los movimientos en vacío.

Otra forma de utilizarlo es como un módulo de python, pudiendo importarlo a nuestro código y mediante las funciones correspondientes cargar el archivo a analizar y obtener el tiempo y distancia.

## Estado del proyecto ##

Con el siguiente enlace se puede consultar el [estado][]
