# NSFNET 
# Sistema de Red - Instalación y Configuración

Este README proporciona instrucciones para la instalación y configuración del sistema de red que incluye un servidor TCP, routers y hosts para el cálculo y comunicación de rutas más cortas entre nodos utilizando los algoritmos de Dijkstra y Bellman-Ford.

## Requisitos Previos
- Python 3.x
- Bibliotecas de Python:
  - `networkx`
  - `matplotlib`

Puedes instalar las bibliotecas necesarias utilizando pip:

```bash
pip install networkx matplotlib
```

## Estructura del Proyecto
El proyecto se organiza en los siguientes archivos:

```
.
├── controlador.py
├── router.py
├── host.py
└── network.py
```

## Instalación

### Clonar el Repositorio
Primero, clona el repositorio en tu máquina local:

```bash
git clone https://github.com/tu_usuario/tu_repositorio.git
cd tu_repositorio
```

### Configuración del Servidor

1. Ejecute el script del controlador:
   ```bash
   python controlador.py
   ```
2. Seleccione el algoritmo de enrutamiento (Dijkstra o Bellman-Ford) cuando se le solicite.

### Configuración de Routers

1. Ejecute el script del router en cada máquina/router:
   ```bash
   python router.py
   ```
2. Ingrese el nombre del router y el puerto del host cuando se le solicite.

### Configuración de Hosts

1. Ejecute el script del host en cada máquina/host:
   ```bash
   python host.py
   ```
2. Ingrese el nombre del host y el puerto del router al que se conectará cuando se le solicite.

## Uso

### En el Servidor
1. Al iniciar el servidor, seleccione el algoritmo de enrutamiento.
2. El servidor calculará las rutas más cortas y las enviará a los routers.

### En los Routers
1. Cada router se conectará al servidor, recibirá las rutas y escuchará conexiones de hosts.
2. Los routers gestionarán la comunicación y el encaminamiento de mensajes entre los hosts.

### En los Hosts
1. Los hosts se conectarán a los routers y podrán enviar y recibir mensajes.
2. Para enviar un mensaje, ingrese el host de destino y el mensaje a enviar.

## Consideraciones y Solución de Problemas
- Asegúrese de que todos los puertos utilizados estén disponibles y no estén bloqueados por firewalls.
- Verifique las conexiones de red entre el servidor, los routers y los hosts.
- Maneje adecuadamente las desconexiones inesperadas para evitar errores en el sistema.

## Autor
Creado por [Tu Nombre]

## Licencia
Este proyecto está licenciado bajo los términos de la Licencia MIT. Consulta el archivo `LICENSE` para más detalles.

---

Siguiendo estos pasos, deberías poder configurar y ejecutar el sistema de red correctamente. Si encuentras algún problema o tienes alguna pregunta, no dudes en abrir un issue en el repositorio del proyecto.
