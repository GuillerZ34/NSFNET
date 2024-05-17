import json
import socket
import threading
from network import Network
import networkx as nx
import time

def compute_all_shortest_paths_dijkstra(network):
    all_paths = dict(nx.all_pairs_dijkstra_path(network.graph))
    for source, destinations in all_paths.items():
        for destination, path in destinations.items():
            print(f"Shortest path from {source} to {destination}: {path}")
    return all_paths

def compute_all_shortest_paths_bellman_ford(network):
    all_paths = dict(nx.all_pairs_bellman_ford_path(network.graph))
    for source, destinations in all_paths.items():
        for destination, path in destinations.items():
            print(f"Shortest path from {source} to {destination}: {path}")
    return all_paths

class TCPServer:
    def __init__(self, host, port, algorithm_choice):
        self.host = host
        self.port = port
        self.server_socket = None
        self.client_count = 0
        self.network = None
        self.node_paths = None
        self.client_sockets = {}
        self.node_names_to_ids = {}  # Diccionario para mapear nombres de nodo a identificadores de nodo
        self.should_stop = threading.Event()  # Evento para indicar si se debe detener el servidor
        self.ack_thread = None  # Hilo para enviar ACK cada 20 segundos
        self.lock = threading.Lock()  # Bloqueo para evitar llamadas simultáneas a send_updated_paths
        self.algorithm_choice = algorithm_choice  # Algoritmo elegido

        self.create_network()

    def start(self):
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            print(f"Server listening on {self.host}:{self.port}...")
            self.ack_thread = threading.Thread(target=self.send_ack_loop)
            self.ack_thread.start()  # Iniciar hilo para enviar ACK cada 20 segundos
            while not self.should_stop.is_set():
                client_socket, client_address = self.server_socket.accept()
                print(f"Connection established with {client_address}")
                self.client_count += 1
                if self.client_count > len(self.node_names_to_ids):
                    print("No more available nodes.")
                    continue
                node_name = f"{list(self.node_names_to_ids.keys())[self.client_count - 1]}"
                port = 12000 + self.client_count
                client_socket.send(f"{node_name}:{port}".encode())
                self.client_sockets[node_name] = client_socket
                client_handler_thread = threading.Thread(
                    target=self.handle_client, args=(client_socket, node_name)
                )
                client_handler_thread.start()
        except Exception as e:
            print(f"Error starting server: {e}")


    def create_network(self):
        self.network = Network()
        self.network.add_node(1, 'Node WA')
        self.node_names_to_ids['Node WA'] = 1  # Guardar la correspondencia de nombre a ID
        self.network.add_node(2, 'Node CA1')
        self.node_names_to_ids['Node CA1'] = 2
        self.network.add_node(3, 'Node CA2')
        self.node_names_to_ids['Node CA2'] = 3
        self.network.add_node(4, 'Node UT')
        self.node_names_to_ids['Node UT'] = 4
        self.network.add_node(5, 'Node CO')
        self.node_names_to_ids['Node CO'] = 5
        self.network.add_node(6, 'Node TX')
        self.node_names_to_ids['Node TX'] = 6
        self.network.add_node(7, 'Node NE')
        self.node_names_to_ids['Node NE'] = 7
        self.network.add_node(8, 'Node IL')
        self.node_names_to_ids['Node IL'] = 8
        self.network.add_node(9, 'Node PA')
        self.node_names_to_ids['Node PA'] = 9
        self.network.add_node(10, 'Node GA')
        self.node_names_to_ids['Node GA'] = 10
        self.network.add_node(11, 'Node MI')
        self.node_names_to_ids['Node MI'] = 11
        self.network.add_node(12, 'Node NY')
        self.node_names_to_ids['Node NY'] = 12
        self.network.add_node(13, 'Node NJ')
        self.node_names_to_ids['Node NJ'] = 13
        self.network.add_node(14, 'Node DC')
        self.node_names_to_ids['Node DC'] = 14
        self.network.add_link(1, 2, 1/2100)
        self.network.add_link(2, 3, 1/1200)
        self.network.add_link(1, 3, 1/3000)
        self.network.add_link(2, 4, 1/1500)
        self.network.add_link(3, 6, 1/3600)
        self.network.add_link(1, 8, 1/4800)
        self.network.add_link(4, 5, 1/1200)
        self.network.add_link(4, 11, 1/3900)
        self.network.add_link(5, 6, 1/2400)
        self.network.add_link(5, 7, 1/1200)
        self.network.add_link(7, 8, 1/1500)
        self.network.add_link(7, 10, 1/2700)
        self.network.add_link(6, 14, 1/3600)
        self.network.add_link(6, 10, 1/2100)
        self.network.add_link(8, 9, 1/1500)
        self.network.add_link(10, 9, 1/1500)
        self.network.add_link(9, 13, 1/600)
        self.network.add_link(9, 12, 1/600)
        self.network.add_link(11, 12, 1/1200)
        self.network.add_link(11, 13, 1/1500)
        self.network.add_link(14, 13, 1/300)
        self.network.add_link(14, 12, 1/600)
        

        self.network.visualize_network()
        if self.algorithm_choice == "dijkstra":
            self.node_paths = compute_all_shortest_paths_dijkstra(self.network)
        elif self.algorithm_choice == "bellman-ford":
            self.node_paths = compute_all_shortest_paths_bellman_ford(self.network)
        else:
            print("Invalid choice. Using Dijkstra by default.")
            self.node_paths = compute_all_shortest_paths_dijkstra(self.network)
        self.save_paths_to_json()  # Llama al método para guardar las rutas

    def save_paths_to_json(self):
        for node, node_paths in self.node_paths.items():
            filename = f"{node}_paths.json"
            with open(filename, "w") as f:
                json.dump(node_paths, f, indent=4)
            print(f"Saved paths for {node} to {filename}")

    def send_ack_loop(self):
        try:
            while not self.should_stop.is_set():
                time.sleep(20)  # Cambiar a 20 segundos
                for client_name, client_socket in self.client_sockets.items():
                    try:
                        client_socket.send("ACK".encode())
                        print(f"Sent ACK message to {client_name}")
                    except Exception as e:
                        print(f"Error sending ACK message to {client_name}: {e}")
                        # Manejar cualquier excepción al enviar el ACK
                        # Esto podría deberse a que el nodo ya no está disponible
                        self.handle_node_failure(client_name)
        except Exception as e:
            print(f"Error sending ACK message: {e}")

    def handle_client(self, client_socket, node_name):
        try:
            paths_json = self.node_paths[node_name]
            client_socket.send(json.dumps(paths_json).encode())
            print(f"Sent paths JSON to {node_name}")

            filename = f"{node_name}_paths.json"
            self.send_file(client_socket, filename)

            # Wait for confirmation from client
            confirmation = client_socket.recv(1024).decode()

            while not self.should_stop.is_set():
                try:
                    data = client_socket.recv(1024).decode()
                    if not data:
                        print(f"Connection with {node_name} closed unexpectedly.")
                        client_socket.send("NO".encode())  # Enviar respuesta "NO" al cliente
                        self.handle_node_failure(node_name)
                        break
                    print(
                        f"Received data from {node_name} ({client_socket.getpeername()}): {data}"
                    )

                    print(f"Received ACK message from {node_name}.")
                    if data == "NO":  # Si la respuesta es "NO"
                        print(f"Node {node_name} responded 'NO'. Removing node...")
                        self.handle_node_failure(node_name)
                except ConnectionResetError:
                    print(f"Connection with {node_name} reset by peer.")
                    client_socket.send("NO".encode())  # Enviar respuesta "NO" al cliente
                    self.handle_node_failure(node_name)
                    break
        except Exception as e:
            print(f"Error handling client: {e}")
        finally:
            client_socket.close()
            del self.client_sockets[node_name]

    def send_file(self, client_socket, filename):
        with open(filename, 'rb') as f:
            while True:
                data = f.read(1024)
                if not data:
                    break
                client_socket.send(data)
            client_socket.send(b'EOF')
            print(f"Sent file {filename} to client")
        f.close()

    def handle_node_failure(self, node_name):
        print(f"Node {node_name} did not respond to ACK. Removing node...")
        node_id = self.node_names_to_ids.get(node_name)
        if node_id is not None:
            self.network.remove_node(node_id)  # Eliminar el nodo de la red
            self.network.visualize_network()
            try:
                self.client_sockets[node_name].close()  # Cerrar el socket del cliente
            except Exception as e:
                print(f"Error closing socket for {node_name}: {e}")
            del self.client_sockets[node_name]  # Eliminar el socket del diccionario
            print("Computing new paths...")
            self.node_paths = compute_all_shortest_paths_dijkstra(self.network)  # Recalcular rutas
            print("New paths computed.")
            self.send_updated_paths()  # Llama a la función para enviar las nuevas rutas
            self.print_updated_paths()  # Imprimir las nuevas rutas después de eliminar el nodo
        else:
            print(f"Node {node_name} not found in the network.")

    def print_updated_paths(self):
        print("Updated paths after removing node:")
        for source, destinations in self.node_paths.items():
            for destination, path in destinations.items():
                print(f"Shortest path from {source} to {destination}: {path}")

    def send_updated_paths(self):
        # Enviar las nuevas rutas actualizadas
        for client_name, client_socket in self.client_sockets.items():
            if client_name in self.node_paths:
                paths_json = self.node_paths[client_name]
                client_socket.send(json.dumps(paths_json).encode())
                print(f"Sent updated paths JSON to {client_name}")
                self.save_paths_to_json()  # Actualiza el archivo JSON después de enviar las rutas
            else:
                print(f"Node {client_name} not found in the network.")

# Ejemplo de uso
if __name__ == "__main__":
    algorithm_choice = input("Choose the algorithm to compute shortest paths (Dijkstra/Bellman-Ford): ").strip().lower()
    server = TCPServer("localhost", 8888, algorithm_choice)
    server.start()
