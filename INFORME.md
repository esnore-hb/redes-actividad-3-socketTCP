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

## Declaración de IA

- Se usó la IA para poder saber manipular bytes en Python
