# Sistema de rutas de entrega con grafos, Dijkstra, prioridad y Merge Sort

## 1. Descripcion general

Este proyecto es una aplicacion en Python que simula la gestion de pedidos para
un repartidor. El sistema representa una ciudad como un grafo ponderado, calcula
rutas cortas con el algoritmo de Dijkstra y organiza los pedidos por prioridad o
por precio mayor.

La aplicacion tiene dos formas de uso:

- modo consola, ejecutando `main.py`;
- interfaz grafica simple, ejecutando `gui.py`.

En la interfaz grafica se puede ver el mapa, registrar pedidos, cargar pedidos
desde un archivo `.txt`, ordenar por prioridad, ordenar por precio mayor con
Merge Sort y procesar entregas con la ruta resaltada sobre el mapa.

## 2. Problema que se desea resolver

El problema consiste en organizar y optimizar las entregas de un repartidor en
una ciudad simulada. En una aplicacion de domicilios, no todos los pedidos
tienen la misma urgencia. Por ejemplo, un pedido de comida preparada debe
entregarse antes porque puede enfriarse, mientras que una camiseta puede esperar
mas tiempo sin afectar tanto al cliente.

Ademas, el repartidor debe moverse por una red de calles. Si el sistema no
calcula una buena ruta, puede gastar mas tiempo del necesario y retrasar las
entregas. Por esta razon, el programa combina dos necesidades:

- decidir que pedido atender primero por prioridad o por precio mayor;
- encontrar la ruta mas corta desde la ubicacion actual del repartidor hasta el
  destino del pedido.

## 3. Objetivo de la practica

Desarrollar una aplicacion que simule un sistema de entregas usando estructuras
de datos y algoritmos. La aplicacion busca:

- representar la ciudad como un grafo ponderado;
- usar Dijkstra para calcular rutas de menor costo;
- organizar pedidos mediante una cola de prioridad;
- aplicar Merge Sort para ordenar pedidos por precio mayor;
- respetar el orden de llegada cuando dos pedidos tienen la misma prioridad o el
  mismo precio;
- mostrar visualmente el mapa y las rutas en una interfaz sencilla;
- generar un reporte basico de pedidos entregados y tiempo total recorrido.

## 4. Estructuras de datos principales

### Grafo ponderado

El mapa de la ciudad se representa como un grafo. Los nodos son lugares como la
bodega, barrios, zonas comerciales y 20 clientes distintos. Las aristas son
calles que conectan esos lugares. Cada arista tiene un peso que representa el
tiempo estimado de recorrido en minutos.

Ejemplo:

```text
Bodega -- Centro: 4 minutos
Centro -- Hospital: 5 minutos
Hospital -- Renata: 3 minutos
```

### Algoritmo de Dijkstra

Dijkstra se utiliza para encontrar la ruta mas corta entre dos nodos del grafo.
En este proyecto, la ruta mas corta significa la ruta con menor tiempo total de
recorrido.

### Cola de prioridad

Los pedidos se guardan en una cola de prioridad. El sistema atiende primero los
pedidos mas urgentes. Si dos pedidos tienen la misma prioridad, se atiende
primero el que llego antes.

Las prioridades ya no dependen automaticamente del tipo de producto. El usuario
las escribe al registrar el pedido o en el archivo TXT. Esto permite que un
mismo tipo de producto pueda ser urgente o no segun el caso.

Prioridades usadas:

```text
alta = pedido urgente
media = pedido normal
baja = pedido menos urgente
```

Internamente, la prioridad se maneja asi:

```text
1 = alta
2 = media
3 = baja
```

### Merge Sort por precio

Como funcion adicional, el programa puede ignorar la prioridad y ordenar los
pedidos unicamente por precio. En este modo se usa Merge Sort para organizar los
pedidos de mayor a menor valor. El pedido con mayor precio se entrega primero.
Si dos pedidos tienen el mismo precio, se conserva primero el que llego antes.

### Listas

Se usan listas para guardar el historial de pedidos entregados y para mostrar
los pedidos pendientes en la interfaz. Tambien se usan como entrada para Merge
Sort cuando se ordena por precio.

### Diccionarios

Se usan diccionarios para guardar las conexiones del grafo y para asociar cada
prioridad con su valor numerico.

## 5. Descripcion de la solucion propuesta

La solucion consiste en un simulador de entregas. El programa inicia con un mapa
predefinido de la ciudad. En ese mapa, cada punto importante es un nodo y cada
calle es una arista con un tiempo estimado de recorrido.

El usuario puede registrar pedidos manualmente o cargarlos desde un archivo de
texto. Cada pedido contiene:

- nombre del cliente;
- tipo de pedido;
- prioridad;
- precio total del pedido;
- destino.

Los destinos de pedidos son clientes del mapa. El programa evita que un mismo
lote tenga dos pedidos hacia el mismo destino, para que los pedidos vayan a
personas diferentes.

Cuando el pedido se registra, el sistema toma la prioridad escrita por el
usuario o por el archivo TXT. Tambien registra el precio total del pedido.

Antes de procesar entregas, el usuario decide si quiere usar el criterio de
prioridad o el criterio de precio mayor. Si usa prioridad, los pedidos se
atienden por urgencia y orden de llegada. Si usa precio mayor, el programa aplica
Merge Sort y entrega primero los pedidos de mayor valor.

Cuando el repartidor procesa un pedido, el sistema toma el primer pedido de la
cola, calcula con Dijkstra la ruta mas corta desde la ubicacion actual hasta el
destino, muestra el recorrido y actualiza la ubicacion del repartidor.

Al final, el usuario puede revisar un reporte con los pedidos entregados, las
rutas tomadas y el tiempo total recorrido.

## 6. Interaccion del usuario

En la aplicacion el usuario puede:

- ver el mapa de la ciudad como grafo;
- ver los puntos disponibles;
- registrar pedidos uno por uno;
- ingresar el precio total de cada pedido;
- cargar pedidos desde un archivo `.txt`;
- consultar la cola de pedidos pendientes;
- revisar el orden en que se atenderan los pedidos;
- ordenar los pedidos por precio mayor usando Merge Sort;
- cambiar entre el criterio de prioridad y el criterio de precio;
- calcular una ruta completa de pedidos pendientes desde la bodega;
- procesar el siguiente pedido;
- procesar todos los pedidos pendientes;
- observar la ruta resaltada en la interfaz grafica;
- consultar un reporte final de entregas.

## 7. Estructura del proyecto

```text
Practica_ADA/
|-- city_graph.py        # Grafo ponderado y algoritmo de Dijkstra
|-- orders.py            # Pedido y cola de prioridad
|-- order_file.py        # Lectura de pedidos desde TXT
|-- delivery_app.py      # Aplicacion de consola
|-- delivery_gui.py      # Interfaz grafica con Tkinter
|-- main.py              # Entrada para modo consola
|-- gui.py               # Entrada para interfaz grafica
|-- pedidos_ejemplo.txt  # Archivo de pedidos de ejemplo
|-- pedidos_20_ejemplo.txt # Archivo con 20 pedidos de prueba
|-- README.md
`-- .gitignore
```

## 8. Como ejecutar el programa

### Modo consola

```bash
python main.py
```

En algunos equipos:

```bash
py main.py
```

### Interfaz grafica

```bash
python gui.py
```

En algunos equipos:

```bash
py gui.py
```

## 9. Formato del archivo TXT de pedidos

El archivo debe tener una linea por pedido y separar los campos con punto y
coma:

```text
cliente;tipo_pedido;prioridad;precio;destino
Ana;pizza familiar;alta;45000;Ana
Luis;camiseta;baja;120000;Lucas
Marta;mercado semanal;media;90000;Mariana
```

El archivo puede incluir una fila de encabezado. Tambien se pueden usar lineas
vacias o comentarios que empiecen con `#`.

Cuando se carga un TXT nuevo, el programa reemplaza los pedidos anteriores y
reinicia la simulacion del lote. De esta forma, una lista nueva no se suma a la
lista cargada anteriormente.

El campo `tipo_pedido` es libre. Puede ser cualquier descripcion corta, por
ejemplo `pizza familiar`, `camiseta`, `mercado semanal`, `medicamento` o
`documentos`.

Prioridades validas:

```text
alta
media
baja
```

Tambien se pueden escribir como numeros:

```text
1 = alta
2 = media
3 = baja
```

El campo `precio` debe ser numerico y mayor que cero. Se puede escribir, por
ejemplo, `45000`, `120000` o `35000.50`.

Destinos validos incluidos en el mapa:

```text
Ana
Bruno
Camila
Diego
Elena
Fabio
Gabriela
Hugo
Irene
Julian
Karla
Lucas
Mariana
Nicolas
Olivia
Pablo
Renata
Samuel
Valentina
Zoe
```

El proyecto incluye `pedidos_ejemplo.txt` para una prueba corta y
`pedidos_20_ejemplo.txt` para probar los 20 destinos de clientes.

## 10. Funcionamiento de la interfaz grafica

La interfaz muestra un mapa con nodos y calles. Los numeros sobre las calles son
los tiempos de recorrido. El panel derecho permite registrar pedidos manuales,
escribir libremente el tipo de producto, seleccionar la prioridad, ingresar el
precio del pedido o cargar pedidos desde TXT.

El boton `ORDENAR POR PRECIO` cambia el criterio activo y organiza los pedidos
pendientes con Merge Sort de mayor a menor precio. El boton `Ordenar por
prioridad` vuelve al criterio de urgencia y orden de llegada.

El boton `Calcular ruta de pedidos desde Bodega` no entrega pedidos ni cambia la
ubicacion real del repartidor. Su funcion es planificar el recorrido completo de
los pedidos pendientes segun el criterio activo. Siempre empieza en `Bodega`,
visita los destinos de los pedidos en orden y resalta todo el recorrido en el
mapa.

Colores principales:

- verde: ubicacion actual del repartidor;
- rojo: destinos con pedidos pendientes;
- azul: bodega inicial;
- linea verde: ruta calculada por Dijkstra.

Cuando se procesa un pedido, la ruta mas corta se resalta en el mapa y el
repartidor cambia su ubicacion al destino entregado.

## 11. Ejemplo de simulacion

Supongamos que se cargan estos pedidos:

```text
Ana;pizza familiar;alta;45000;Ana
Luis;camiseta;baja;120000;Lucas
Marta;mercado semanal;media;90000;Mariana
```

Si se usa prioridad, el sistema los ordena asi:

```text
1. Ana - pizza familiar - prioridad alta
2. Marta - mercado semanal - prioridad media
3. Luis - camiseta - prioridad baja
```

Si se usa precio mayor, el sistema aplica Merge Sort y los ordena asi:

```text
1. Luis - camiseta - $120000
2. Marta - mercado semanal - $90000
3. Ana - pizza familiar - $45000
```

Luego calcula la ruta mas corta para cada entrega segun la ubicacion actual del
repartidor.

## 12. Reporte academico del proyecto

### Nombre del proyecto

Sistema de rutas de entrega con grafos, Dijkstra, prioridad y Merge Sort.

### Problema que se desea resolver

El proyecto busca resolver el problema de organizacion y planificacion de
entregas para un repartidor dentro de una ciudad simulada. En un sistema de
domicilios, los pedidos pueden tener diferentes niveles de importancia y tambien
distintos valores economicos. Ademas, el repartidor debe desplazarse por una red
de calles, por lo que no basta con saber que pedido atender primero: tambien es
necesario calcular una ruta eficiente para llegar al destino.

Si los pedidos se atienden sin un criterio claro, pueden generarse retrasos,
rutas innecesariamente largas y un uso poco eficiente del tiempo del repartidor.
Por eso, la aplicacion propone dos formas de organizar los pedidos: por prioridad
o por precio mayor. Despues, para cada entrega, calcula la ruta mas corta usando
el algoritmo de Dijkstra.

### Objetivo de la practica

El objetivo de la practica es desarrollar una aplicacion que aplique estructuras
de datos y algoritmos vistos en clase para simular un problema real de reparto.
La aplicacion busca permitir el registro de pedidos, ordenarlos segun un criterio
seleccionado por el usuario y calcular la ruta mas corta desde la ubicacion
actual del repartidor hasta el destino de cada pedido.

Con este proyecto se busca demostrar el uso de grafos ponderados, Dijkstra,
colas de prioridad, listas y Merge Sort dentro de una misma solucion.

### Estructuras de datos utilizadas

El proyecto utiliza un grafo ponderado para representar el mapa de la ciudad.
Cada nodo representa un lugar, como la bodega, un barrio, una zona comercial o
un cliente. Cada arista representa una calle y su peso indica el tiempo estimado
de recorrido en minutos.

Tambien se utiliza una cola de prioridad para atender pedidos segun urgencia. En
este modo, los pedidos de prioridad alta se entregan primero, luego los de
prioridad media y finalmente los de prioridad baja. Si dos pedidos tienen la
misma prioridad, se respeta el orden de llegada.

Como funcion adicional, se utiliza Merge Sort para ordenar los pedidos por
precio mayor. En este modo, la prioridad no se toma en cuenta para decidir el
orden de entrega; el pedido con mayor precio se atiende primero.

Ademas, se usan listas para guardar pedidos pendientes y entregados, y
diccionarios para almacenar las conexiones del grafo y los valores internos de
las prioridades.

### Descripcion de la solucion propuesta

La aplicacion inicia con un mapa predefinido de ciudad representado como grafo.
El repartidor comienza en la bodega. El usuario puede registrar pedidos desde la
interfaz grafica, desde la consola o mediante un archivo TXT.

Cada pedido contiene cliente, tipo de producto, prioridad, precio y destino. Al
iniciar el programa en consola, el usuario escoge si desea atender los pedidos
por prioridad o por precio mayor. En la interfaz grafica, puede cambiar el
criterio usando los botones `Ordenar por prioridad` y `ORDENAR POR PRECIO`.

Cuando se procesa un pedido, el sistema toma el primer pedido segun el criterio
activo. Luego aplica Dijkstra para encontrar la ruta mas corta desde la ubicacion
actual del repartidor hasta el destino. Finalmente, actualiza la ubicacion del
repartidor y registra la entrega en el reporte final.

### Interaccion del usuario

El usuario puede ejecutar la aplicacion en modo consola o en modo grafico. En
ambos casos puede registrar pedidos, cargar pedidos desde un archivo TXT, elegir
el criterio de ordenamiento, ver pedidos pendientes, procesar entregas y revisar
un reporte final.

En la interfaz grafica, el usuario tambien puede observar visualmente el mapa de
la ciudad. Los nodos representan ubicaciones y las lineas representan calles. Al
procesar una entrega, la ruta calculada por Dijkstra se resalta sobre el mapa.

### Resultados esperados

El resultado esperado es que el sistema organice correctamente los pedidos segun
el criterio elegido. Si se usa prioridad, los pedidos se atienden por urgencia y
orden de llegada. Si se usa precio, Merge Sort organiza los pedidos de mayor a
menor valor.

Tambien se espera que para cada pedido el programa muestre la ruta mas corta, el
tiempo estimado de recorrido y el historial de entregas realizadas.

### Conclusion

El proyecto permite demostrar como diferentes estructuras de datos pueden
trabajar juntas para resolver un problema practico. El grafo modela la ciudad,
Dijkstra permite encontrar rutas eficientes, la cola de prioridad organiza
pedidos urgentes y Merge Sort permite ordenar pedidos por precio. De esta forma,
la aplicacion combina organizacion de datos y optimizacion de rutas en un mismo
sistema.

## 13. Version breve para formulario academico

### Problema

El proyecto busca resolver la organizacion de pedidos de un repartidor,
considerando la prioridad, el precio del pedido y la ruta mas corta para llegar
a su destino.

### Objetivo

Desarrollar una aplicacion que use grafos, Dijkstra, colas de prioridad y Merge
Sort para simular un sistema de entregas eficiente.

### Estructuras de datos

Se utiliza un grafo ponderado para representar la ciudad, una cola de prioridad
para ordenar pedidos por urgencia, Merge Sort para ordenarlos por precio, listas
para guardar historiales y diccionarios para almacenar conexiones y prioridades.

### Solucion

El usuario registra o carga pedidos desde TXT. El sistema pregunta si se desea
ordenar por prioridad o por precio mayor. Luego calcula con Dijkstra la ruta mas
corta desde la ubicacion actual del repartidor hasta el destino del pedido.

### Interaccion

El usuario puede ver el mapa, agregar pedidos con prioridad y precio, cargar
pedidos desde archivo, ordenar por prioridad o precio, procesar entregas y
observar la ruta calculada en una interfaz grafica simple.
