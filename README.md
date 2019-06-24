# python3HTTPSAuthServer
It's SimpleHTTPServer, with python3 facial hair!
Supports:
  - HTTP Basic AUTH   [username:pass]
  - HTTPS encryption
  - Self-generates self-signed certificate, or you can bring your own


usage: python3HTTPSAuthServer.py [-h] [-i IP] [-p PORT] [-a AUTH] [-s]  
                                 [-c CERT] [-k PRIVATEKEY]  
  
Python HTTPS Auth Server  
  
optional arguments:    
-h, --help            show this help message and exit  
-i IP, --ip IP        Bind IP (Default all interfaces 0.0.0.0)  
-p PORT, --port PORT  Bind port, default 8443  
-a AUTH, --auth AUTH  HTTP BASIC auth [username:password]  
-s, --https           Use HTTPS  
-c CERT, --cert CERT  If you brought your own CERT, then by all means...  
                       [fullpath]   -k PRIVATEKEY, --privatekey PRIVATEKEY  
                       If you brought your own PRIVATE_KEY, then by all  
                       means... [fullpath]  
  
  






