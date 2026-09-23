# redes-actividad-3-socketTCP

Modelo simplificado de Protocolo de Transporte TCP implementado en Python

## Setup

Hacer un ambiente de Python. No debería ser necesario porque todo lo usado aquí
es con librerias estándar, pero igual para asegurarse.

```bash
# Linux
python -m venv .venv
source
```

## Organización de las carpetas

```py
.
├── cliente.py
├── servidor.py
├── socket_tcp/             # Módulo principal
│   ├── ejemplo-UDP-puro/   # Ejemplo transferencia de archivos
│   └── model.py            # Clases que implementa nuestro SocketTCP
└── test/
```

## Ejecución

### Programa principal

```bash
python -m servidor

python -m cliente
```

### Con pérdidas

Para activar las pérdidas:

```bash
sudo tc qdisc add dev lo root netem loss [% de pérdida] delay [tiempo de delay]
```

Para desactivarlas:

```bash
sudo tc qdisc del dev lo root netem
```
