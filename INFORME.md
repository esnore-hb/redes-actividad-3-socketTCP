# Actividad 3: SocketTCP con Stop & Wait

## Ejecución

Requiere Python 3.11 o superior, sin dependencias externas. En una terminal de Linux, situarse en la raíz del proyecto:

```bash
cd redes-actividad-3-socketTCP
```

Para probar la clase confiable, abrir dos terminales en esa carpeta. En la primera, iniciar el servidor:

```bash
python3 -m test.server
```

En la segunda, ejecutar el cliente:

```bash
python3 -m test.client
```

Las pruebas básicas muestran `Passed` si los mensajes recibidos y el cierre son correctos. Para repetirlas con pérdidas en Linux, activar `netem` antes de iniciar el servidor y el cliente:

```bash
sudo tc qdisc add dev lo root netem loss 20%
```

Ejecutar nuevamente los comandos del servidor y del cliente en sus respectivas terminales y comprobar que los mensajes llegan completos y ambos sockets cierran. Al terminar, desactivar las pérdidas:

```bash
sudo tc qdisc del dev lo root
```

Los programas principales se ejecutan con `python3 servidor.py` y luego `python3 cliente.py localhost 8000 < archivo.txt`. El cliente recibe el host y el puerto como argumentos y lee los bytes del archivo desde la entrada estándar; el servidor imprime su contenido UTF-8. El servidor escucha en localhost, puerto 8000, y el cliente usa el puerto local 8001.

**Limitación de entrega:** esos programas aún son provisionales: transfieren mediante UDP directo y terminan con un datagrama vacío. Falta conectarlos a `send/recv/close/recv_close`. Las pruebas de confiabilidad corresponden a la clase, no a esos programas.

## Flujo y decisiones de diseño

1. `bind` asocia el socket UDP. Si el cliente no hizo bind, `connect` asigna un puerto disponible.
2. `connect/accept` realizan el handshake. El servidor crea otro socket en un puerto disponible para la conexión.
3. `send` transmite primero la longitud en 4 bytes y después bloques de hasta 16 bytes. Espera el ACK de cada segmento; si vence el timeout fijo de 10 ms, lo retransmite.
4. `recv(n)` confirma duplicados sin repetir datos y guarda los excedentes en un buffer para próximas llamadas.
5. El cierre usa FIN → FIN-ACK → ACK. Se permiten tres timeouts; el emisor repite el ACK final tres veces, separadas por un timeout.

El encabezado contiene ACK, SYN y FIN de 1 byte cada uno, más SEQ de 4 bytes, en orden big-endian: 7 bytes de encabezado y hasta 16 de contenido. El buffer UDP es de 23 bytes. La secuencia avanza una unidad por segmento confirmado, no por byte.

### Diagrama del handshake

```text
Cliente: connect()                    Servidor: accept()
   | -------- SYN, seq=x -----------> | socket de escucha
   | <------ SYN-ACK, seq=x+1 -------- | nuevo socket/puerto
   | -------- ACK, seq=x+2 ---------> | nuevo socket
   |          conexión lista         |
```

### Pérdida del último ACK

```text
Cliente: connect()/send()             Servidor: accept()
   | <------ SYN-ACK, seq=x+1 -------- |
   | ---- ACK, seq=x+2 ---- X          | ACK perdido
   |                                  | timeout
   | <------ SYN-ACK, seq=x+1 -------- | retransmisión
   | -------- ACK, seq=x+2 ---------> | conexión lista
```

`send` reconoce el SYN-ACK repetido y reenvía el ACK final. Como alternativa, si llega primero el segmento de longitud con secuencia x+2, `accept` lo considera confirmación y lo guarda para `recv`.

## Pruebas y pendientes

La validación con pérdidas se realizará mediante `netem`, siguiendo los comandos de la sección de ejecución. Queda pendiente ejecutar esta prueba en Linux y registrar sus resultados; aún falta un modo debug que muestre cómo se manejan las pérdidas, solicitado por el enunciado.

También se comprobó un mensaje de 38 bytes mediante exactamente dos llamadas a `recv(19)`: ambas devolvieron 19 bytes y reconstruyeron el original. Así se cubre el caso solicitado de n no múltiplo de 16.

Caso borde: el buffer conserva bytes sobrantes de un segmento cuando n no es múltiplo de 16. El timeout de 10 ms se eligió para pruebas locales; puede causar retransmisiones innecesarias en redes con mayor retardo.

## Declaración de IA

- Se usó la IA para poder saber manipular bytes en Python.
- Se usó IA para ajustar la recepción de argumentos por consola en el cliente.

Se utilizó `sys` porque permite acceder a los argumentos y a la entrada estándar: `sys.argv[1]` obtiene el host, `int(sys.argv[2])` obtiene el puerto y `sys.stdin.buffer.read()` lee los bytes del archivo redirigido con `< archivo.txt`.
