import socket
import threading
import sys
from os import system

# Se realiza la asignacón del nombre del usuario, direccion IP del host y puerto
# Tambien se realiza la conexión al servidor
try:
    usuario = input('Indica tu nombre de usuario: ')
    host = input('Indica la direccion IP del servidor: ')
    puerto = int(input('Indica el puerto: '))
    op_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    op_socket.connect((host, puerto))
except BaseException as err:
    print(err)
    sys.exit()


# Esta funcion se mantendra a la escucha para poder mostrar los mensajes enviados a traves del servidor
def recibir_mensaje():
    try:
        estado = True
        while estado:
            
            message = op_socket.recv(1024).decode('utf-8')

            # Condiciones utilizadas para cerrar la funcion correctamente, limpiar pantalla,
            # mostrar el usuario o solo mostrar los datos en pantalla al cliente
            if message == "@res":
                op_socket.send(usuario.encode())
            elif message == f"{usuario}--> salir()":
                estado = False
                op_socket.close()
            elif(message == "RESPUESTA: El canal indicado es incorrecto\n" or message == "Selecciona el canal\n"
                 or message == "Chat"):
                system('cls')
                print(message)
            else:
                print(message)
    except:
        # Se crea esta excepción para cerrar el chat de manera correcta si ocurre un error
        print("Cerrando procesos de lectura")
        print("Si cuentas con problemas para salir ingresa la palabra salir() para cerrar sesion")
        
# Esta funcion se mantendra a la escucha para poder envias los mensajes a traves del servidor
def escribir_mensaje():
    try:
        estado = True
        while estado:
            mensaje = f"{usuario}--> {input()}"

            # Condición es utilizada para cerrar la funcion de manera correcta
            if mensaje == f"{usuario}--> salir()":
                estado = False
                op_socket.close()
           
            op_socket.send(mensaje.encode())
    except:
        # Se crea esta excepción para cerrar el chat de manera correcta si ocurre un error
        try:
            op_socket.send(f"{usuario}--> salir()".encode())
        except:
            print("Cerrando procesos de escritura")
        

# Se crea un hilo para que la función recibir_mensaje se ejecute en segundo plano
recibir_thread = threading.Thread(target=escribir_mensaje)
recibir_thread.start()

# Se crea un hilo para que la función escribir_mensaje se ejecute en segundo plano
escribir_thread = threading.Thread(target=recibir_mensaje)
escribir_thread.start()
