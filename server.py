import socket
from threading import Thread, Lock
import pickle
import json


class Server:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind(('127.0.0.1', 65432))
        self.sock.listen(6)
        self.lock = Lock()
        self.clients = []

        with open('stats.json', 'r') as file:
            self.stats = json.load(file)

        self.listen()

    def listen(self):
        try:
            while True:
                client, address = self.sock.accept()
                with self.lock:
                    self.clients.append(client)
                thread = Thread(target=self.handle_client, args=(client,))
                thread.start()
        except KeyboardInterrupt:
            print("Отключение сервера")
        finally:
            self.sock.close()

    def broadcast(self, message, curr_client, name):
        new_message = name + ': ' + message
        for client in self.clients:
            if client == curr_client:
                continue
            try:
                client.send(pickle.dumps({'msg': new_message}))

                with open('messages.txt', 'a') as file:
                    file.write(new_message + '\n')

            except Exception as e:
                print('socket error: ', e)
                client.close()

    def handle_client(self, client):
        try:
            name = ''
            while True:
                data = client.recv(1024)
                message = pickle.loads(data)

                if not message:
                    continue

                if message.get('name', ''):
                    name = message.get('name')
                    continue

                if message.get('msg') == 'stats':
                    stat = self.stats[name]
                    client.send(pickle.dumps({'stats': stat}))
                    continue

                msg = message.get('msg')

                self.broadcast(msg, client, name)

                with self.lock:
                    self.stats[name] = self.stats.get(name, 0) + 1

                    with open('stats.json', 'w') as file:
                        json.dump(self.stats, file)

        except Exception as e:
            print('client error: ', e)
            client.close()


server = Server()
