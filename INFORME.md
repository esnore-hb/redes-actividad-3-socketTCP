# Informe

## Decisiones de diseño

### Conexión del cliente sin un `bind()` previo

Decidimos asignar un puerto local con `bind(("", 0))` si el cliente llama a
`connect()` sin un `bind()` previo, como muestra el ejemplo del punto 4. Lanzar
una excepción impediría ejecutar ese ejemplo. Si ya existe un `bind()`, se conserva.

## Declaración de IA

- Se usó la IA para poder saber manipular bytes en Python
