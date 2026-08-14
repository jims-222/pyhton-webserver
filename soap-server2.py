from flask import Flask
from spyne import Application, rpc, ServiceBase, Iterable, Integer, Unicode
from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication

# 1. Define the service operations
class CalculatorService(ServiceBase):
    @rpc(Integer, Integer, _returns=Integer)
    def add_numbers(ctx, num1, num2):
        """Adds two integers together."""
        return num1 + num2

    @rpc(Unicode, _returns=Unicode)
    def say_hello(ctx, name):
        """Greets the user by name."""
        return f"Hello, {name}!"

# 2. Package the service into a Spyne application
soap_app = Application(
    services=[CalculatorService],
    tns="spyne.examples.calculator",
    in_protocol=Soap11(validator="lxml"),
    out_protocol=Soap11()
)

# 3. Wrap it in a WSGI app wrapper
wsgi_soap_app = WsgiApplication(soap_app)

# 4. Integrate with Flask
app = Flask(__name__)

@app.route("/soap", methods=["POST", "GET"])
def soap_endpoint():
    # Route incoming server requests straight to Spyne
    return wsgi_soap_app

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
