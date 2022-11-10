import socket
import threading

# Canales donde los clientes se conectaran para chatear entre si
canal1 = []
canal2 = []

# En este bloque de codigo se asignaran la direccion IP del server, su puerto,
# tipo de protocolos utilizados e inicio del servidor. Cuando termine este proceso
# se ejecutara la funcion recibiendo_conexion
try:
    server = '192.168.0.135'
    puerto = 8080
    op_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    op_socket.bind((server, puerto))
    op_socket.listen()
    print("Servidor iniciado y contestando OK")
except BaseException as error:
    print(error)

# Mensajes predeterminados que mostrara en el aplicativo
def mensaje_canales(cliente):
    cliente.send("Selecciona el canal\n".encode())
    cliente.send("1.Canal 1\n".encode())
    cliente.send("2.Canal 2\n".encode())
    cliente.send("Indica el numero del canal al que deseas ingresar\n".encode())
    cliente.send("Nota: si deseas cerrar la sesión ingresa la palabra salir()\n".encode())
    cliente.send("###################################".encode())

# Mensajes predeterminados que mostrara en el aplicativo
def mensaje_chat(cliente, numCanal):
    cliente.send("Chat".encode())
    cliente.send(f"Conectado al canal {numCanal[-1]} correctamente\n".encode())
    cliente.send("Ya puedes chatear con las personas que esten conectados en este canal\n".encode())
    cliente.send("Nota: para salir del chat debes ingresar la palabra chao e iras a la sección para escoger"
                 " canales\n".encode())
    cliente.send("###################################\n".encode())

# Funcion utilizada para enviar alertas
def alertas_mensajes(mensaje, canal, _cliente):
    for cliente in canal:
        cliente.send(mensaje.encode())

# Funcion utilizada para enviar mensajes en el chat
def enviar_mensajes(mensaje, canal, _cliente):
    for cliente in canal:
        if cliente != _cliente:
            cliente.send(mensaje.encode())

# Funcion utilizada para recibir los mensajes enviados por los clientes y realizar el envio
def respuesta_mensaje(cliente, canal, usuario):
    try:
        estado = True

        # Mensaje de bienvenida que muestra los usuarios que se van conectando a la sala
        mensBien = f"El usuario {usuario} se conecto a la sala\n"
        alertas_mensajes(mensBien, canal, cliente)
        if len(canal) == 1:
            mensaje = "Te encuentras solo en la sala\n"
            alertas_mensajes(mensaje, canal, cliente)

        while estado:
            # En este ciclo while se mantendra a la escucha para poder recibir los mensajes
            # y estos ser enviados a los demas clientes
            mensaje = cliente.recv(1024).decode()

            if mensaje == f"{usuario}--> chao":
                mensDes = f"El usuario {usuario} ha salido de la sala"
                enviar_mensajes(mensDes, canal, cliente)
                estado = False
                canal.remove(cliente)
            if mensaje == f"{usuario}--> salir()":
                cliente.send(f"{usuario}--> salir()".encode())
                print(f"el usuario {usuario} se desconecto inesperadamente del servidor")
            enviar_mensajes(mensaje, canal, cliente)
    except BaseException as err:
        canal.remove(cliente)
        print(err)

# Funcion utilizada para seleccionar el canal donde el cliente se desea conectar para poder
# chatear con los demas
def seleccionar_canal(cliente, usuario):
    try:
        estado = True
        while estado:
            # Se generar un mensaje predeterminado con una funcion y se solicita el
            # ingreso de un canal
            mensaje_canales(cliente)
            canalSeleccionado = cliente.recv(1024).decode()

            # Se genera una serie de condiciones para ingresar a uno de los canales
            # tambien para poder salir del chat y por si el usuario trata de ingresar
            # un canal erroneo
            if canalSeleccionado == f"{usuario}--> 1":
                # Se agrega al cliente al canal y envia un mensaje predeterminado al cliente
                # de que ingreso correctamente a la sala de chat
                canal1.append(cliente)
                mensaje_chat(cliente, canalSeleccionado)

                # Se ejecuta la funciona respuesta_mensaje en un hilo para que esta se ejecute
                # en segundo pano y poder realizar la conversación entre los usuarios
                thread_respuesta_mensaje = threading.Thread(target=respuesta_mensaje, args=(cliente, canal1, usuario,))
                thread_respuesta_mensaje.start()
                thread_respuesta_mensaje.join()
            elif canalSeleccionado == f"{usuario}--> 2":
                canal2.append(cliente)
                mensaje_chat(cliente, canalSeleccionado)
                thread_respuesta_mensaje = threading.Thread(target=respuesta_mensaje, args=(cliente, canal1, usuario,))
                thread_respuesta_mensaje.start()
                thread_respuesta_mensaje.join()
            elif canalSeleccionado == f"{usuario}--> salir()":
                estado = False
                cliente.send(f"{usuario}--> salir()".encode())
                print(f"el usuario {usuario} se desconecto inesperadamente del servidor")
            else:
                cliente.send("RESPUESTA: El canal indicado es incorrecto\n".encode())
    except:
        print(f"el usuario {usuario} se desconecto")

# Esta funcion sera la encargada de aceptar la conexión del cliente y poder empezar
# a interactuar con los clientes que se van conectando
def recibiendo_conexion():
    try:
        while True:

            # El servidor acepta la conexión del cliente
            (socketCliente, direccion) = op_socket.accept()

            # Recibe el usuario por parte del cliente
            socketCliente.send("@res".encode())
            usuario = socketCliente.recv(1024).decode('utf-8')

            print(f'Usuario {usuario} conectado')

            # Se crea un mensaje para que este sea enviado al cliente
            mensaje_server = "Esta conectado al server correctamente"
            socketCliente.send(f'{usuario}--> {mensaje_server}\n'.encode())

            # Se crea un hilo para que se ejecute en segundo plano la funcion seleccionar_canal
            # Para que este siempre se mantenga a la escucha y se pueda navegar allí
            thread_seleccionar_canal = threading.Thread(target=seleccionar_canal, args=(socketCliente, usuario,))
            thread_seleccionar_canal.start()

    except BaseException as err:
        print(err)


recibiendo_conexion()
