import requests
import time
import datetime
from concurrent.futures import ThreadPoolExecutor

def send_post(number: int):
    url = "http://192.168.4.1"  # Target URL
    data = f"number={number}"  # Payload for POST request
    try:
        response = requests.post(url, data=data)
    except requests.exceptions.ConnectionError as e:
        pass
    except requests.exceptions.RequestException as e:
        print(f"Error occurred: {repr(e)}")
    except KeyboardInterrupt:
        print("Script interrupted by user.")

    # Print the response status and message
    print(f"{datetime.datetime.now().time()} Sent: {data}")


def send_post_requests():
    with ThreadPoolExecutor(max_workers=10) as executor:
        res = list(executor.map(send_post, range(1, 1000)))


if __name__ == "__main__":
    send_post_requests()
