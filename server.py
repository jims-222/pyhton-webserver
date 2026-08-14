from http.server import HTTPServer, BaseHTTPRequestHandler
import os
import socketserver
import threading
import time
import xml.etree.ElementTree as ET

# 1. Create a Multi-Threaded HTTP Server class for Python 3.6.8
class ThreadingHTTPServer(socketserver.ThreadingMixIn, HTTPServer):
    """This class allows the server to handle each HTTP request in a new thread."""
    daemon_threads = True  # Ensures threads die when the main program exits

class SOAPRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        """Serves the static WSDL contract file when ?wsdl is requested."""
        if self.path.endswith("?wsdl") or self.path.endswith(".wsdl"):
            if os.path.exists("calculator.wsdl"):
                self.send_response(200)
                self.send_header("Content-Type", "text/xml; charset=utf-8")
                self.end_headers()
                with open("calculator.wsdl", "rb") as f:
                    self.wfile.write(f.read())
            else:
                self.send_error(404, "WSDL file layout not found on server.")
        else:
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(b"SOAP Server Running. Target /?wsdl for contract.")

    def do_POST(self):
        """Processes incoming XML SOAP requests."""
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)

        try:
            root = ET.fromstring(post_data)

            num1_element = root.find('.//{http://example.com}num1')
            num2_element = root.find('.//{http://example.com}num2')

            if num1_element is not None and num2_element is not None:
                val1 = int(num1_element.text)
                val2 = int(num2_element.text)

                sum_result = val1 + val2

                response_xml = (
                    f'<?xml version="1.0" encoding="UTF-8"?>\n'
                    f'<soapenv:Envelope xmlns:soapenv="http://xmlsoap.org" '
                    f'xmlns:calc="http://example.com">\n'
                    f'   <soapenv:Header/>\n'
                    f'   <soapenv:Body>\n'
                    f'      <calc:add_numbersResponse>\n'
                    f'         <calc:result>{sum_result}</calc:result>\n'
                    f'      </calc:add_numbersResponse>\n'
                    f'   </soapenv:Body>\n'
                    f'</soapenv:Envelope>'
                ).encode('utf-8')

                self.send_response(200)
                self.send_header("Content-Type", "text/xml; charset=utf-8")
                self.send_header("Content-Length", str(len(response_xml)))
                self.end_headers()
                self.wfile.write(response_xml)
            else:
                self.send_soap_fault("Client", "Missing expected num1 or num2 payload items.")

        except Exception as e:
            self.send_soap_fault("Server", f"Internal parsing validation error: {str(e)}")

    def send_soap_fault(self, fault_code, fault_string):
        fault_xml = (
            f'<?xml version="1.0" encoding="UTF-8"?>\n'
            f'<soapenv:Envelope xmlns:soapenv="http://xmlsoap.org">\n'
            f'   <soapenv:Body>\n'
            f'      <soapenv:Fault>\n'
            f'         <faultcode>soapenv:{fault_code}</faultcode>\n'
            f'         <faultstring>{fault_string}</faultstring>\n'
            f'      </soapenv:Fault>\n'
            f'   </soapenv:Body>\n'
            f'</soapenv:Envelope>'
        ).encode('utf-8')

        self.send_response(500)
        self.send_header("Content-Type", "text/xml; charset=utf-8")
        self.send_header("Content-Length", str(len(fault_xml)))
        self.end_headers()
        self.wfile.write(fault_xml)

# 2. Background Scheduler Job
def scheduler_job():
    """Prints 'hello' every 5 minutes (300 seconds)."""
    interval = 30  # 300 seconds
    print("Background scheduler thread started successfully.")
    while True:
        time.sleep(interval)
        print(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] hello")

def run(server_class=ThreadingHTTPServer, handler_class=SOAPRequestHandler, port=8000):
    # 3. Start the background scheduler thread
    # Setting daemon=True ensures this thread terminates instantly when the main server exits.
    bg_thread = threading.Thread(target=scheduler_job, daemon=True)
    bg_thread.start()

    # 4. Start the network listener
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f"Multi-threaded Standard Lib SOAP Server listening on port {port}...")
    print(f"WSDL exposed at: http://localhost:{port}/?wsdl")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down server...")
        httpd.server_close()

if __name__ == '__main__':
    run()
