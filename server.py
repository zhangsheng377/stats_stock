from flask import Flask
import datetime
import requests
from threading import Timer

app = Flask(__name__)
app.debug = True


with open("update_ip_url", 'r') as file:
    update_ip_url = file.readline()

def update_ip():
    requests.get(update_ip_url)
    t = Timer(60 * 30, update_ip)
    t.start()


@app.route('/')
def hello_world():
    return 'Hello, World!' + '<br /><br />' + str(datetime.datetime.now())


if __name__ == "__main__":
    t = Timer(0, update_ip)
    t.start()

    app.run(host="0.0.0.0", port=5000)
