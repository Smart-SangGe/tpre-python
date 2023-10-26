import argparse
import requests
import json


def send_post_request(ip_addr, message_name):
    url = f"http://localhost:8002/request_message"
    data = {"dest_ip": ip_addr, "message_name": message_name}
    response = requests.post(url, json=data)
    return response.text


def get_pk(ip_addr):
    url = f"http://" + ip_addr + ":8002/get_pk"
    response = requests.get(url, timeout=1)
    print(response.text)
    json_pk = json.loads(response.text)
    payload = {"pkx": json_pk["pkx"], "pky": json_pk["pky"], "ip": ip_addr}
    response = requests.post("http://localhost:8002/recieve_pk", json=payload)

    return response.text



def main():
    parser = argparse.ArgumentParser(description="Send POST request to a specified IP.")
    parser.add_argument("ip_addr", help="IP address to send request to.")
    parser.add_argument("message_name", help="Message name to send.")

    args = parser.parse_args()
    
    response = get_pk(args.ip_addr)
    print(response)
    
    response = send_post_request(args.ip_addr, args.message_name)
    
    print(response)


if __name__ == "__main__":
    main()
