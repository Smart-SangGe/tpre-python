import argparse
import requests


def send_post_request(ip_addr, message_name):
    url = f"http://localhost:8002/request_message"
    data = {"dest_ip": ip_addr, "message_name": message_name}
    response = requests.post(url, json=data)
    return response.text


def main():
    parser = argparse.ArgumentParser(description="Send POST request to a specified IP.")
    parser.add_argument("ip_addr", help="IP address to send request to.")
    parser.add_argument("message_name", help="Message name to send.")

    args = parser.parse_args()
    response = send_post_request(args.ip_addr, args.message_name)
    print(response)


if __name__ == "__main__":
    main()
