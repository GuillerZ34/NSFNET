import socket
import threading
import json

class Router:
    def __init__(self, server_host, server_port, router_port):
        self.server_host = server_host
        self.server_port = server_port
        self.router_port = router_port
        self.server_socket = None
        self.node_name = "RouterNode"
        self.hosts = {}
        self.paths = {}
        self.routing_table = {}
        self.routers = {
            "Node WA": 15000,
            "Node CA1": 15001,
            "Node CA2": 15002,
            "Node UT": 15003,
            "Node CO": 15004,
            "Node TX": 15005,
            "Node NE": 15006,
            "Node IL": 15007,
            "Node PA": 15008,
            "Node GA": 15009,
            "Node MI": 15010,
            "Node NY": 15011,
            "Node NJ": 15012,
            "Node DC": 15013
        }
        self.node_to_router = {
            "Host WA" : "Node WA",
            "Host CA1" : "Node CA1",
            "Host CA2" : "Node CA2",
            "Host UT" : "Node UT",
            "Host CO" : "Node CO",
            "Host TX" : "Node TX",
            "Host NE" : "Node NE",
            "Host IL" : "Node IL",
            "Host PA" : "Node PA",
            "Host GA" : "Node GA",
            "Host MI" : "Node MI",
            "Host NY" : "Node NY",
            "Host NJ" : "Node NJ",
            "Host DC" : "Node DC"
            
        }

    def connect_to_server(self):
        try:
            print(f"Connecting to server at {self.server_host}:{self.server_port}...")
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.connect((self.server_host, self.server_port))
            node_info = self.server_socket.recv(1024).decode()
            self.node_name, port = node_info.split(':')
            self.server_port = int(port)
            print(f"Connected to server as {self.node_name} on port {self.server_port}")

            # Receive paths JSON from server
            print("Waiting to receive paths JSON from server...")
            paths_json = b""
            while True:
                data = self.server_socket.recv(1024)
                if b'EOF' in data:
                    paths_json += data.split(b'EOF')[0]
                    break
                paths_json += data

            paths_json_str = paths_json.decode().strip()

            # Debugging output for received JSON string
            print(f"Received paths JSON string: {paths_json_str}")

            try:
                # Split the concatenated JSON strings
                json_objects = paths_json_str.split('}{')
                if len(json_objects) == 2:
                    json_objects[0] += '}'
                    json_objects[1] = '{' + json_objects[1]

                    # Load each JSON object
                    paths1 = json.loads(json_objects[0])
                    paths2 = json.loads(json_objects[1])

                    # Combine the paths (assuming we need to merge them)
                    self.paths = {**paths1, **paths2}

                else:
                    self.paths = json.loads(paths_json_str)

                # Save paths JSON to file
                filename = f"received_{self.node_name}_paths.json"
                with open(filename, "w") as f:
                    f.write(paths_json_str)
                print(f"Saved paths JSON to {filename}")

                # Debugging output for paths
                print("Paths received from server:")
                print(json.dumps(self.paths, indent=2))

                # Populate routing table
                self.populate_routing_table()

            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")

            # Send confirmation to server
            self.server_socket.send("File received".encode())

            # Listen for ACK messages from server
            while True:
                data = self.server_socket.recv(1024).decode()
                if data == "ACK":
                    print("Received ACK message from server. Node is OK.")
                    response = "OK"
                    self.server_socket.send(response.encode())
                else:
                    print(f"Received unexpected message from server: {data}")
                    break
        except ConnectionRefusedError as e:
            print(f"Connection refused: {e}")
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}")

    def populate_routing_table(self):
        for host_name, router_name in self.node_to_router.items():
            if router_name in self.paths:
                path = self.paths[router_name]
                print(f"Adding path for host {host_name} via router {router_name}: {path}")
                if len(path) == 1:
                    # Directly connected or it's the current node
                    next_hop = router_name
                else:
                    # Next hop is the second node in the path
                    next_hop = path[1]
                self.routing_table[host_name] = next_hop
        
        print("Routing table populated:")
        print(json.dumps(self.routing_table, indent=2))

    def forward_message(self, next_router, message):
        try:
            next_router_port = self.routers[next_router]
            print(f"Connecting to next router {next_router} on port {next_router_port}")
            forward_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            forward_socket.connect(("localhost", int(next_router_port)))
            forward_socket.send(message.encode())
            forward_socket.close()
            print(f"Message forwarded to router {next_router}")
        except Exception as e:
            print(f"Failed to forward message to router {next_router}: {e}")

    def process_forward_message(self, message):
        parts = message.split(':', 2)
        if len(parts) == 3 and parts[0] == "forward":
            dest_host = parts[1]
            msg_content = parts[2]
            print(f"Processing forward message to {dest_host} with content: {msg_content}")
            if dest_host in self.hosts:
                print(f"Host {dest_host} is directly connected.")
                self.hosts[dest_host].send(f"Message from {self.node_name}: {msg_content}".encode())
            else:
                next_router_name = self.routing_table.get(dest_host)
                print(f"Next router for host {dest_host}: {next_router_name}")
                if next_router_name:
                    forward_message = f"forward:{dest_host}:{msg_content}"
                    print(f"Forwarding message to next router {next_router_name} for host {dest_host}")
                    self.forward_message(next_router_name, forward_message)
                else:
                    print(f"Host {dest_host} not found in routing paths.")
        else:
            print(f"Invalid forward message format: {message}")

    def host_handler(self, host_socket, host_address):
        print(f"Host connected from {host_address}")

        # Receive and register the host name
        host_name = host_socket.recv(1024).decode()
    
        if host_name.startswith("forward:"):
            print(f"Processing forwarded message: {host_name}")
            self.process_forward_message(host_name)
            host_socket.close()
        else:
            self.hosts[host_name] = host_socket
            print(f"Host registered with name: {host_name}")

            while True:
                try:
                    data = host_socket.recv(1024).decode()
                    if not data:
                        print(f"Connection with host {host_name} closed.")
                        del self.hosts[host_name]
                        break
                    else:
                        print(f"Received message from {host_name}: {data}")
                        if data.startswith("forward:"):
                            self.process_forward_message(data)
                        else:
                            try:
                                message = json.loads(data)
                                dest_host = message.get("dest_host")
                                msg_content = message.get("message")
                                print(f"Message to {dest_host} with content: {msg_content}")
                                if dest_host in self.hosts:
                                    print(f"Sending message directly to host {dest_host}.")
                                    self.hosts[dest_host].send(f"Message from {host_name}: {msg_content}".encode())
                                else:
                                    next_router = self.routing_table.get(dest_host)
                                    print(f"Next router for destination {dest_host}: {next_router}")
                                    if next_router:
                                        forward_message = f"forward:{dest_host}:{msg_content}"
                                        print(f"Forwarding message to router {next_router} for host {dest_host}")
                                        self.forward_message(next_router, forward_message)
                                    else:
                                        print(f"Host {dest_host} not found in routing paths.")
                            except json.JSONDecodeError as e:
                                print(f"Failed to decode message from {host_name}: {data}, error: {e}")
                except ConnectionResetError:
                    print(f"Connection reset by host {host_name}.")
                    del self.hosts[host_name]
                    break
                except Exception as e:
                    print(f"Error handling data from host {host_name}: {e}")
                    break

    def start_router_socket(self):
        try:
            router_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            router_socket.bind(('localhost', self.router_port))
            router_socket.listen(5)
            print(f"Router {self.node_name} listening for hosts on port {self.router_port}...")

            while True:
                host_socket, host_address = router_socket.accept()
                threading.Thread(target=self.host_handler, args=(host_socket, host_address)).start()
        except Exception as e:
            print(f"Error occurred in router socket: {e}")


    def start(self):
        try:
            print(f"Router port: {self.router_port}")
            # Iniciar el servidor del router en un hilo separado
            threading.Thread(target=self.start_router_socket).start()
            self.connect_to_server()
        except Exception as e:
            print(f"Error occurred: {e}")
        finally:
            if self.server_socket:
                self.server_socket.close()
# Ejemplo de uso
if __name__ == "__main__":
    node_name = input("Nombre Router: ")
    server_port = 8888
    router_port = int(input("Puerto Host: "))  # Cambiar el puerto aquí si es necesario
    router1 = Router("localhost", server_port, router_port)
    router1.start()


