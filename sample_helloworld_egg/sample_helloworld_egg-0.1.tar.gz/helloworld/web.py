import sys
from helloworld.hello import Hello
from flask import Flask

app = Flask(__name__)
greeter = None

@app.route("/")
def hello():
    return greeter.message

def main():
    message = ' '.join(sys.argv[1:])
    if not message:
        print("Please input some sort of message")
    else:
        global greeter
        greeter = Hello(message)
        app.run()
