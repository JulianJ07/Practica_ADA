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
bodega, barrios, zonas comerciales y clientes. Las aristas son calles que
conectan esos lugares. Cada arista tiene un peso que representa el tiempo
estimado de recorrido en minutos.

Ejemplo:

```text
Bodega -- Centro: 4 minutos
Centro -- Hospital: 5 minutos
Hospital -- Cliente Ana: 4 minutos
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
- calcular una ruta entre dos puntos;
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
Ana;pizza familiar;alta;45000;Cliente Ana
Luis;camiseta;baja;120000;Cliente Luis
Marta;mercado semanal;media;90000;Cliente Marta
```

El archivo puede incluir una fila de encabezado. Tambien se pueden usar lineas
vacias o comentarios que empiecen con `#`.

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
Barrio Norte
Barrio Sur
Bodega
Centro
Cliente Ana
Cliente Luis
Cliente Marta
Hospital
Parque
Universidad
Zona Comercial
```

El proyecto incluye el archivo `pedidos_ejemplo.txt` para probar la carga.

## 10. Funcionamiento de la interfaz grafica

La interfaz muestra un mapa con nodos y calles. Los numeros sobre las calles son
los tiempos de recorrido. El panel derecho permite registrar pedidos manuales,
escribir libremente el tipo de producto, seleccionar la prioridad, ingresar el
precio del pedido o cargar pedidos desde TXT.

El boton `ORDENAR POR PRECIO` cambia el criterio activo y organiza los pedidos
pendientes con Merge Sort de mayor a menor precio. El boton `Ordenar por
prioridad` vuelve al criterio de urgencia y orden de llegada.

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
Ana;pizza familiar;alta;45000;Cliente Ana
Luis;camiseta;baja;120000;Cliente Luis
Marta;mercado semanal;media;90000;Cliente Marta
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

## 12. Version breve para formulario academico

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
