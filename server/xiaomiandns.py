import socket
import threading
import dns.resolver
import dns.message
import dns.rdataclass
import dns.rdatatype
import dns.flags
import dns.rcode
import dns.rrset
import time
import sqlite3
import re
import base64
from cryptography.hazmat.primitives.asymmetric import rsa, padding
from cryptography.hazmat.primitives import serialization, hashes



class DNSServer:
    def __init__(self, hostname, port, db_file):
        self.hostname = hostname
        self.port = port
        self.db_file = db_file

    def run(self):
        self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.udp_socket.bind((self.hostname, self.port))
        self.tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_socket.bind((self.hostname, self.port))
        self.tcp_socket.listen(1)
        print(f"DNS server running on {self.hostname}:{self.port}")
        for i in range(3):
            udp_thread = threading.Thread(target=self.handle_udp_request)
            udp_thread.start()
            tcp_thread = threading.Thread(target=self.handle_tcp_request)
            tcp_thread.start()

    def handle_udp_request(self):
        data, address = self.udp_socket.recvfrom(1024)
        response = self.handle_request(data)
        self.udp_socket.sendto(response, address)
        udp_thread = threading.Thread(target=self.handle_udp_request)
        udp_thread.start()

    def handle_tcp_request(self):
        connection, address = self.tcp_socket.accept()
        data = connection.recv(1024)
        response = self.handle_request(data)
        connection.send(response)
        connection.close()
        tcp_thread = threading.Thread(target=self.handle_tcp_request)
        tcp_thread.start()

    def handle_request(self, data):
        conn = sqlite3.connect(self.db_file)
        cur = conn.cursor()
        question = dns.message.from_wire(data)
        response = self.build_response(question, cur)
        return response

    def build_response(self, question, dbcursor, rcode=dns.rcode.NOERROR, answer=None):
        # Create a new DNS message object
        response = dns.message.Message()

        # Set the message header fields
        response.id = question.id
        response.flags = dns.flags.QR | dns.flags.RA

        # Add the question to the message
        response.question = question.question

        name = question.question[0].name
        # search domain in database
        dbcursor.execute(
            "SELECT ip FROM xiaomiandns WHERE domain = ? AND nodetype = client", (str(name)[:-1],))
        result = dbcursor.fetchone()

        # Create a new RRset for the answer
        if result is not None:
            answer = dns.rrset.RRset(name, dns.rdataclass.IN, dns.rdatatype.A)
            rdata = dns.rdata.from_text(
                dns.rdataclass.IN, dns.rdatatype.A, result[0])
            answer.add(rdata)
            response.answer.append(answer)
            # Set the response code
            response.set_rcode(rcode)
        else:
            response.set_rcode(dns.rcode.NXDOMAIN)
        return response.to_wire()


class DNSAPI:
    # usage: use POST method
    #        /add
    #        data: domian=xxxx&ip=xx.xx.xx.xx&pubkey=xxxxx&nodetype=xxxx
    #        /delete
    #        data: domian=xxxx&ip=xx.xx.xx.xx&prikey=xxxxx&nodetype=xxxx

    def __init__(self, hostname, port, db_file):
        self.hostname = hostname
        self.port = port
        self.db_file = db_file

    def run(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 绑定 IP 地址和端口号
        server_socket.bind((self.hostname, self.port))
        # 监听连接
        server_socket.listen(5)
        print(f"API server running on {self.hostname}:{self.port}")
        while True:
            # 接受连接
            conn, addr = server_socket.accept()
            # 处理请求
            t = threading.Thread(target=self.handle_tcp_request, args=(conn,))
            t.start()

    def handle_tcp_request(self, conn):
        request = conn.recv(1024).decode('utf-8')
        response = self.handle_http_request(request)
        conn.send(response)
        conn.close()

    def handle_http_request(self, request):
        request_line, headers = request.split('\r\n\r\n', 2)
        method, url, version = request_line.split(' ', 2)

        if method == 'GET':
            response = self.handle_get_request(url)
        elif method == 'POST':
            data = request.split('\r\n')[-1]
            response = self.handle_post_request(url, data)
        else:
            response = self.handle_error_request()

        return response

    def handle_get_request(self, url):

        # check url start with /add
        # if re.match(r'^/add\?', url):
        #     status_code = self.add_data(url[5:])
        #     if status_code == 200:
        #         reason_phrase = 'Add data successful'
        #     else:
        #         reason_phrase = 'Add data unsuccessful'
        # # check url start with /delete
        # elif re.match(r'^/delete\?', url):
        #     status_code = self.delete_data(url[9:])
        #     if status_code == 200:
        #         reason_phrase = 'Delete data successful'
        #     else:
        #         reason_phrase = 'Delete data unsuccessful'
        # else:
        #     status_code = 400
        #     reason_phrase = 'unsupport api'

        response = 'HTTP/1.1 {} {}\r\n'.format(status_code, reason_phrase)
        return response.encode("utf-8")

    def handle_post_request(self, url, data):
        # 处理 POST 请求，data 是 POST 方法提交的数据

        # check url start with /add
        if re.match(r'^/add\?', url):
            status_code = self.add_data(data)
            if status_code == 200:
                reason_phrase = 'Add data successful'
            else:
                reason_phrase = 'Add data unsuccessful'
        # check url start with /delete
        elif re.match(r'^/delete\?', url):
            status_code = self.delete_data(data)
            if status_code == 200:
                reason_phrase = 'Delete data successful'
            else:
                reason_phrase = 'Delete data unsuccessful'
        else:
            status_code = 400
            reason_phrase = 'unsupport api'

        response = 'HTTP/1.1 {} {}\r\n'.format(status_code, reason_phrase)
        return response.encode("utf-8")

    def handle_error_request(self, request):
        status_code = 400
        reason_phrase = "unsupport method"
        headers = {
            'Content-Type': 'text/html',
            'Connection': 'close',
        }
        response = 'HTTP/1.1 {} {}\r\n'.format(status_code, reason_phrase)
        return response.encode("utf-8")

    def add_data(self, data):

        # parse and check validation
        domain, ip, pubkey, nodetype = self.parse_data(data)

        if not self.check_data(domain,ip,nodetype):
            return 400

        # connect db
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()

        # Check if the data already exists
        c.execute(
            "SELECT * FROM xiaomiandns WHERE domain = ? OR ip = ? OR pubkey = ? OR nodetype = ?", (domain, ip, pubkey, nodetype))
        existing_data = c.fetchall()

        cursor.close()
        conn.close()

        if existing_data:
            return 400
        else:
            # Insert the new data
            c.execute(
                "INSERT INTO xiaomiandns (domain,ip,pubkey,nodetype,timestamp) VALUES (?,?,?,?,DATETIME('now'))", (domain, ip, pubkey, nodetype))
            return 200

    def delete_data(self, data):

        # parse and check validation
        domain, ip, private_key_base64, nodetype = self.parse_data(data)
        
        if not self.check_data(domain, ip ,nodetype):
            return 400

        # connect db
        conn = sqlite3.connect(self.db_file)
        c = conn.cursor()
        c.execute(
            "SELECT pubkey FROM xiaomiandns WHERE domain = ? AND ip = ? AND nodetype = ?", (domain, ip, nodetype))
        public_key_base64 = c.fetchone()
        cursor.close()
        conn.close()

        if public_key_base64 != None:
            public_key_base64 = public_key_base64[0]
        else:
            return 400

        private_key_bytes = base64.b64decode(
            private_key_base64).decode("utf-8")

        private_key = serialization.load_pem_private_key(
            private_key_bytes,
            password=None
        )
        
        gen_public_key = private_key.public_key()
        gen_public_key_bytes = gen_public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )
        gen_public_key_base64 = base64.b64encode(gen_public_key_bytes).decode('utf-8')
        
        if gen_public_key_base64 == public_key_base64:
            conn = sqlite3.connect(self.db_file)
            c = conn.cursor()
            c.execute(
                "DELETE FROM xiaomiandns WHERE domain = ? AND ip = ? AND nodetype = ?", (domain, ip, nodetype))
            cursor.close()
            conn.close()
            return 200
        else:
            return 400

    def parse_data(self, data):

        domain = re.search(r'domain=([^&]+)', data)
        ip = re.search(r'ip=([^&]+)', data)
        pubkey = re.search(r'pubkey=([^&]+)', data)
        privkey = re.search(r'privkey=([^&]+)', data)
        nodetype = re.search(r'nodetype=([^]+)', data)

        if domain and ip and nodetype:
            domain = domain.group(1)
            ip = ip.group(1)
            nodetype = nodetype.group(1)
            if bool(pubkey) != bool(privkey):
                if pubkey:
                    key = pubkey.group(1)
                else:
                    key = privkey.group(1)
        return domain, ip, key, nodetype

    def check_data(self, domain, ip, nodetype):

        # check domain
        pattern = r'^[a-z0-9]{16}\.xiaomian$'

        if re.match(pattern, domain):
            return True
        else:
            return False

        # check ip
        pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
        if re.match(pattern, ip):
            octets = ip.split('.')
            if all(int(octet) < 256 for octet in octets):
                return True
        return False

        # check nodetype
        if nodetype in {"server", "client", "node"}:
            return True
        else:
            return False


if __name__ == '__main__':
    with open('serverconf.yaml', 'r') as f:
        config = yaml.safe_load(f)
    db_file = config['database']['db_file']
    DNS_port = config['DNS']['port']
    DNS_listen_host = config['DNS']['listen_host']
    API_port = config['API']['port']
    API_listen_host = config['API']['listen_host']

    
        
        
        
        
        
        
        
        
        
    # start dns server
    server = DNSServer(API_listen_host, DNS_port, db_file)
    server.run()

    # start dns api server
    APIserver = DNSAPI(API_listen_host, API_port, db_file)
    APIserver.run()
    
