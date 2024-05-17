import socket
import threading
import json

class Host:

    def __init__(self, host_name, router_port):
        self.host_name = host_name
        self.router_port = router_port
        self.client_socket = None

    def connect(self):
        try:
            print(f"Connecting to router at port {self.router_port}...")
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect(("localhost", self.router_port))
            print(f"Connected to router at port {self.router_port}")
            # Send the host name to the router
            self.client_socket.send(self.host_name.encode())
        except ConnectionRefusedError as e:
            print(f"Connection refused: {e}")

    def send_message(self, dest_host, message):
        try:
            print(f"Sending message to {dest_host}...")
            # Create a JSON formatted message
            msg = json.dumps({"dest_host": dest_host, "message": message})
            self.client_socket.send(msg.encode())
            print("Message sent successfully.")
        except AttributeError:
            print("Please connect to the router first.")
        except Exception as e:
            print(f"Failed to send message: {e}")

    def receive_messages(self):
        while True:
            try:
                message = self.client_socket.recv(1024).decode()
                if message:
                    print(f"\nReceived message: {message}")
                else:
                    print("Connection closed by the router.")
                    break
            except Exception as e:
                print(f"Error receiving message: {e}")
                break

# Ejemplo de uso
if __name__ == "__main__":
    host_name = input("Nombre host: ")
    router_port = int(input("Puerto Router: "))
    
    host = Host(host_name, router_port)
    host.connect()  # Conectarse al router antes de ingresar el mensaje
    
    # Iniciar un hilo para recibir mensajes
    receive_thread = threading.Thread(target=host.receive_messages)
    receive_thread.daemon = True  # Esto permite que el hilo se cierre cuando el programa principal termine
    receive_thread.start()
    
    while True:
        dest_host = input("Enter destination host: ")  # Ingresar el nombre del host de destino
        message = input("Enter message: ")  # Ingresar el mensaje
        host.send_message(dest_host, message)
        
        continue_sending = input("Do you want to send another message? (yes/no): ")
        if continue_sending.lower() != 'yes':
            print("Exiting...")
            break 
