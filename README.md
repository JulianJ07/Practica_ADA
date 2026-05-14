# Simulador de desembarco de pasajeros

## 1. Descripcion general

Este proyecto es una aplicacion de consola desarrollada en Python que simula el
desembarco de pasajeros en terminales aeroportuarias de diferentes capacidades.
El programa recibe datos ingresados por el usuario, compara varias estrategias
de asignacion de aviones, recomienda una configuracion basada en un algoritmo
greedy y ejecuta una simulacion por ticks hasta que todos los pasajeros han
desembarcado.

El proyecto esta orientado a una practica academica de estructuras de datos,
programacion orientada a objetos, simulacion y algoritmos heuristicos.

## 2. Problema que se desea resolver

En un aeropuerto, el desembarco de pasajeros puede generar congestiones y
demoras cuando los aviones no son distribuidos correctamente entre las
terminales disponibles. Si una terminal recibe demasiados aviones o si no se
tiene en cuenta su capacidad de procesamiento, el tiempo total del proceso puede
aumentar y los recursos pueden usarse de forma ineficiente.

El problema consiste en simular y mejorar la asignacion de aviones a terminales
con distintas capacidades. Cada terminal puede desembarcar una cantidad
determinada de pasajeros por tick. Por esta razon, el programa busca reducir el
tiempo total de desembarco y evitar que una sola terminal quede sobrecargada.

## 3. Objetivo de la practica

Desarrollar una aplicacion en Python que permita simular el desembarco de
pasajeros en terminales aeroportuarias de distintos tamanos y capacidades, con
el fin de comparar configuraciones y encontrar una distribucion eficiente de
aviones.

La aplicacion busca reducir tiempos de espera, mejorar el uso de los recursos
disponibles y mostrar de forma clara como una estrategia greedy puede apoyar la
toma de decisiones en un problema de asignacion.

## 4. Estructura del proyecto

```text
EstructuraDatos2/
|-- counter.py
|-- plane.py
|-- terminal.py
|-- README.md
`-- reports/              # Se crea automaticamente si se exportan resultados
```

## 5. Archivos principales

### plane.py

Define la clase `Plane`, que representa un avion. Cada avion tiene:

- identificador;
- cantidad inicial de pasajeros;
- cantidad de pasajeros restantes durante la simulacion.

Tambien incluye metodos para desembarcar pasajeros, reiniciar el estado del
avion y consultar si el avion ya termino su proceso.

### terminal.py

Define la clase `Terminal`, que representa una terminal aeroportuaria. Cada
terminal tiene:

- identificador;
- capacidad de procesamiento por tick;
- lista de aviones asignados;
- indice del avion que se esta atendiendo.

Tambien define `TickResult`, una estructura que resume lo que ocurre en una
terminal durante un tick de simulacion.

### counter.py

Es el archivo principal del programa. Se encarga de:

- solicitar los datos al usuario;
- crear los aviones y terminales;
- comparar estrategias de asignacion;
- seleccionar la configuracion greedy como recomendacion principal;
- ejecutar la simulacion manual o automatica;
- calcular estadisticas finales;
- exportar resultados en archivos `.txt` y `.csv`.

## 6. Estrategias de asignacion comparadas

El programa compara varias formas de distribuir los aviones entre las
terminales. Esto permite demostrar que la estrategia greedy puede mejorar frente
a asignaciones mas simples.

### FIFO simple

Asigna los aviones en el mismo orden en que fueron ingresados, alternando entre
las terminales disponibles. Es una estrategia sencilla que sirve como punto de
comparacion, pero no intenta optimizar el tiempo total.

### Aleatorio

Asigna cada avion a una terminal elegida al azar. El programa usa una semilla
fija para que el resultado sea reproducible. Esta estrategia permite comparar
el greedy contra una distribucion sin criterio de optimizacion.

### Greedy

Ordena los aviones de mayor a menor cantidad de pasajeros. Luego asigna cada
avion a la terminal donde genere el menor tiempo acumulado estimado. Es la
estrategia recomendada por el programa.

### Fuerza bruta

Prueba todas las asignaciones posibles y encuentra la mejor configuracion para
casos pequenos. Esta estrategia se usa como referencia exacta, pero no se
ejecuta en casos grandes porque el numero de combinaciones crece muy rapido.

## 7. Limitacion principal del algoritmo greedy

La principal limitacion del proyecto es que el algoritmo greedy encuentra una
solucion aproximada, no necesariamente la mejor de todas. Esto ocurre porque el
greedy toma decisiones paso a paso con la informacion disponible en ese momento,
pero no analiza todas las combinaciones posibles.

Esta limitacion no invalida la solucion. Al contrario, permite explicar que el
greedy es una alternativa practica, rapida y facil de implementar para obtener
buenas soluciones en problemas donde revisar todas las posibilidades puede ser
costoso.

Para evidenciar esta limitacion, el programa compara el resultado greedy con
FIFO simple, asignacion aleatoria y fuerza bruta en casos pequenos.

## 8. Funcionamiento general

El usuario ingresa:

- numero de terminales;
- capacidad de procesamiento de cada terminal;
- numero de aviones;
- cantidad de pasajeros de cada avion;
- modo de simulacion: manual o automatico;
- decision de exportar o no los resultados.

Despues de recibir los datos, el sistema calcula los tiempos estimados de las
estrategias de asignacion. Luego muestra una tabla comparativa y presenta la
configuracion recomendada por el algoritmo greedy.

Finalmente, se ejecuta la simulacion por ticks. En cada tick, cada terminal
atiende el avion que tiene activo y desembarca tantos pasajeros como permita su
capacidad. Cuando un avion termina, la terminal pasa al siguiente avion asignado
en el tick posterior.

## 9. Estadisticas finales

Al terminar la simulacion, el programa muestra un resumen con:

- tiempo total del proceso;
- total de pasajeros procesados;
- promedio general de pasajeros desembarcados por tick;
- terminal mas usada;
- terminal menos usada;
- cantidad de aviones asignados por terminal;
- total de pasajeros procesados por terminal;
- ticks de trabajo por terminal;
- promedio de pasajeros por tick para cada terminal.

Estas estadisticas ayudan a analizar si la asignacion fue equilibrada y si los
recursos se aprovecharon correctamente.

## 10. Exportacion de resultados

Al finalizar, el programa pregunta si se desean exportar los resultados. Si el
usuario responde que si, se crea automaticamente una carpeta llamada `reports`
y se generan dos archivos:

- un archivo `.txt` con el reporte general de la simulacion;
- un archivo `.csv` con el registro detallado de cada tick.

El archivo TXT es util para anexar evidencia en la entrega academica. El CSV
puede abrirse en Excel, Google Sheets u otra herramienta para analizar los datos
en forma de tabla.

## 11. Requisitos

Para ejecutar el proyecto se necesita:

- Python 3.10 o superior;
- una terminal o consola de comandos.

El proyecto no requiere librerias externas.

## 12. Como ejecutar el programa

Desde la carpeta del proyecto:

```bash
python counter.py
```

En algunos equipos tambien puede usarse:

```bash
py counter.py
```

O:

```bash
python3 counter.py
```

## 13. Ejemplo de uso

Ejemplo de datos de entrada:

```text
Ingrese el numero de terminales: 2
Ingrese la capacidad de procesamiento de la terminal T1: 30
Ingrese la capacidad de procesamiento de la terminal T2: 50
Ingrese el numero de aviones: 3
Ingrese la cantidad de pasajeros del avion A1: 120
Ingrese la cantidad de pasajeros del avion A2: 80
Ingrese la cantidad de pasajeros del avion A3: 60
Seleccione el modo de simulacion (manual/automatico): automatico
Desea exportar los resultados a TXT y CSV? (s/n): s
```

El programa mostrara:

- una comparacion de estrategias;
- la configuracion recomendada por greedy;
- el avance de la simulacion tick por tick;
- estadisticas finales;
- rutas de los archivos exportados, si el usuario decide generarlos.

## 14. Reporte del trabajo

### Problema trabajado

El proyecto aborda la distribucion eficiente de aviones entre terminales
aeroportuarias con distintas capacidades. La finalidad es disminuir congestiones
y reducir el tiempo total requerido para desembarcar a todos los pasajeros.

### Solucion implementada

Se implemento una aplicacion de consola basada en programacion orientada a
objetos. Los aviones y terminales se modelan mediante clases independientes, lo
que permite separar responsabilidades y mantener el codigo organizado.

La asignacion recomendada se realiza con una heuristica greedy. Primero se
ordenan los aviones de mayor a menor cantidad de pasajeros. Luego, cada avion se
ubica en la terminal que produzca el menor tiempo acumulado estimado.

### Mejoras agregadas

Se agregaron comparaciones contra FIFO simple, asignacion aleatoria y fuerza
bruta limitada a casos pequenos. Tambien se incorporaron estadisticas finales y
exportacion de resultados en archivos TXT y CSV.

Estas mejoras permiten justificar mejor el comportamiento del algoritmo greedy,
analizar el uso de cada terminal y dejar evidencia del resultado de la
simulacion.

### Simulacion

La simulacion avanza por ticks. En cada tick, cada terminal desembarca una
cantidad de pasajeros igual o menor a su capacidad. Si un avion termina de
desembarcar, la terminal continua con el siguiente avion de su lista en el tick
posterior. El programa termina cuando no queda ningun avion con pasajeros
pendientes.

### Resultados esperados

El resultado esperado es una distribucion mas equilibrada de los aviones entre
las terminales. Esto permite observar una reduccion del tiempo total frente a
estrategias simples, como FIFO o asignacion aleatoria.

### Posibles mejoras futuras

- Agregar una interfaz grafica sencilla.
- Permitir que el usuario cree una asignacion manual para compararla.
- Generar graficas a partir del archivo CSV.
- Permitir cargar datos desde un archivo externo.
- Comparar mas algoritmos de optimizacion.

## 15. Version breve para formulario academico

### Problema

El proyecto resuelve el problema de congestion y demora en el desembarco de
pasajeros cuando los aviones no se distribuyen adecuadamente entre terminales de
distintas capacidades.

### Objetivo

Simular el desembarco de pasajeros y encontrar una distribucion eficiente de
aviones que reduzca los tiempos de espera y mejore el uso de las terminales.

### Solucion

El programa recibe los datos de terminales y aviones, compara varias estrategias
de asignacion, recomienda una solucion greedy y ejecuta una simulacion por ticks
hasta completar el desembarco.

### Limitacion

El greedy ofrece una solucion aproximada. No garantiza siempre la mejor solucion,
porque no evalua todas las combinaciones posibles. Para evidenciarlo, el
programa compara greedy con FIFO, aleatorio y fuerza bruta en casos pequenos.

### Interaccion

El usuario ingresa terminales, capacidades, aviones, pasajeros y modo de
simulacion. Luego visualiza la comparacion de estrategias, la configuracion
recomendada, el avance por ticks, las estadisticas finales y, si lo desea,
exporta los resultados a TXT y CSV.
