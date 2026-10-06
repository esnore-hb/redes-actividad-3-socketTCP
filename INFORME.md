# Informe

## Decisiones de diseño

### Conexión del cliente sin un `bind()` previo

Decidimos asignar un puerto local con `bind(("", 0))` si el cliente llama a
`connect()` sin un `bind()` previo, como muestra el ejemplo del punto 4. Lanzar
una excepción impediría ejecutar ese ejemplo. Si ya existe un `bind()`, se conserva.

### Manejo simple de archivos

Asumimos archivos dentro del proyecto y ejecución desde su raíz. El cliente lee
el archivo elegido con `input()` y el servidor solo imprime su contenido, sin
crear archivos. Decodificamos al final para evitar cortar caracteres entre paquetes.

### Stop & Wait

Decidimos usar un timeout de 10 ms, secuencias que avanzan de 1 en 1 y ACK con
la misma secuencia del segmento. `send()` parte de la secuencia guardada, envía
la longitud en 4 bytes y luego bloques de hasta 16 bytes, retransmitiendo si vence
el timeout. `recv()` confirma duplicados sin repetir datos y conserva los bytes
que exceden `buff_size` para la siguiente llamada.

## Declaración de IA

- Se usó la IA para poder saber manipular bytes en Python
