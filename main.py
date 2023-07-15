import os
import json
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
from urllib.parse import parse_qs, urlparse
import socketserver
import threading


# Клас для обробки HTTP запитів
class RequestHandler(BaseHTTPRequestHandler):
    def set_headers(self, status):
        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def serve_file(self, filename):
        file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
        if os.path.exists(file_path):
            self.set_headers(200)
            with open(file_path, 'rb') as file:
                self.wfile.write(file.read())
        else:
            self.set_headers(404)
            with open('error.html', 'rb') as file:
                self.wfile.write(file.read())

    def handle_post(self, data):
        username = data.get('username', [''])[0]
        message = data.get('message', [''])[0]
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        message_data = {'username': username, 'message': message}

        storage_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'storage')
        os.makedirs(storage_folder, exist_ok=True)
        file_path = os.path.join(storage_folder, 'data.json')

        # Зчитуємо вміст файлу data.json, якщо він існує
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                try:
                    messages = json.load(file)
                except json.JSONDecodeError:
                    messages = {}
        else:
            messages = {}

        # Додаємо нове повідомлення до словника
        messages[current_time] = message_data

        # Записуємо оновлений словник у файл data.json
        with open(file_path, 'w') as file:
            json.dump(messages, file, indent=4)  # Збереження з відступами

        self.set_headers(200)
        self.wfile.write(b'Message submitted')

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = parse_qs(post_data.decode('utf-8'))
        self.handle_post(data)

    def do_GET(self):
        parsed_url = urlparse(self.path)
        query_params = parse_qs(parsed_url.query)

        if parsed_url.path == '/':
            self.serve_file('index.html')
        elif parsed_url.path == '/message' or parsed_url.path == '/message.html':
            self.serve_file('message.html')
        else:
            self.serve_file(parsed_url.path[1:])


class ThreadingHTTPServer(ThreadingMixIn, HTTPServer):
    pass


if __name__ == '__main__':
    server_address = ('', 3000)
    http_server = ThreadingHTTPServer(server_address, RequestHandler)
    print('Starting HTTP server on port 3000...')
    http_server_thread = threading.Thread(target=http_server.serve_forever)
    http_server_thread.start()

    storage_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'storage')
    os.makedirs(storage_folder, exist_ok=True)
    file_path = os.path.join(storage_folder, 'data.json')


    class SocketServer(socketserver.ThreadingMixIn, socketserver.UDPServer):
        def handle(self, data, address):
            message_data = json.loads(data.decode('utf-8'))


    socket_server = SocketServer(('localhost', 5000), SocketServer)
    print('Starting Socket server on port 5000...')
    socket_server.serve_forever()
