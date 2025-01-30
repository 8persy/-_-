import socket
from threading import Thread
import pickle


class Client:
    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        name = input('введите имя')
        self.connect()
        self.sock.send(pickle.dumps({'name': name}))

    def send(self):
        while True:
            msg = input()
            try:
                self.sock.send(pickle.dumps({'msg': msg}))
            except Exception as e:
                print('error with send ', e)

    def receive(self):
        try:
            while True:
                data = self.sock.recv(1024)
                message = pickle.loads(data)

                if message.get('stats', ''):
                    print("stats: ", message.get('stats'))
                    continue

                print(message.get('msg', ''))
        except Exception as e:
            print('exception ', e)

    def connect(self):
        self.sock.connect(('127.0.0.1', 65432))

        send_thread = Thread(target=self.send)
        receive_thread = Thread(target=self.receive)

        send_thread.start()
        receive_thread.start()


client = Client()