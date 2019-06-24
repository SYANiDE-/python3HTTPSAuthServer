#!/usr/bin/env python3

from http.server import HTTPServer, SimpleHTTPRequestHandler
import ssl, os, sys, argparse, base64

NARGS = len(sys.argv)
ARGS = {}
tempfiles = []

def Get_Args():
	AO = argparse.ArgumentParser(description="Python HTTPS Auth Server")
	AO.add_argument("-i", "--ip", help="Bind IP (Default all interfaces 0.0.0.0)", type=str, default="0.0.0.0")
	AO.add_argument("-p", "--port", help="Bind port, default 8443", type=int, default=8443)
	AO.add_argument("-a", "--auth", help="HTTP BASIC auth  [username:password]", type=str, default=None)
	AO.add_argument("-s", "--https", help="Use HTTPS", action="store_true")
	AO.add_argument("-c", "--cert", help="If you brought your own CERT, then by all means... [fullpath]", type=str, default=None)
	AO.add_argument("-k", "--privatekey", help="If you brought your own PRIVATE_KEY, then by all means... [fullpath]", type=str, default=None)
	AP, AP_garbage = AO.parse_known_args()
	ARGS = vars(AP)
	if (ARGS['cert'] and not ARGS['privatekey']) or (ARGS['privatekey'] and not ARGS['cert']):
		print("[!] You can BYOC only when providing BOTH a certfile and matching private key! Else NEITHER, and generate a self-signed automatically")
		sys.exit()
	return ARGS	


def gencert():
	## We're just going to generate self-signed certs... 
	# https://www.linux.org/threads/creating-a-self-signed-certificate-with-python.9038/
	# https://markusholtermann.eu/2016/09/ssl-all-the-things-in-python/
	from OpenSSL import crypto, SSL
	from pprint import pprint
	from time import gmtime, mktime
	from os.path import exists, join
	from random import choice, randint
	from string import ascii_letters
	import tempfile, pathlib, os.path
	CN = "SSLS"
	k = crypto.PKey()
	k.generate_key(crypto.TYPE_RSA, 4096)
	cert = crypto.X509()
	cert.get_subject().C = "".join([choice(ascii_letters[:26]) for i in range(2)])
	cert.get_subject().ST = "".join([choice(ascii_letters[:26]) for i in range(2)])
	cert.get_subject().L = "".join([choice(ascii_letters[:26]) for i in range(0, randint(2,32))])
	cert.get_subject().O = "".join([choice(ascii_letters[:26]) for i in range(0, randint(2,32))])
	cert.get_subject().OU = "".join([choice(ascii_letters[:26]) for i in range(0, randint(2,32))])
	cert.get_subject().CN = CN
	cert.set_serial_number(randint(1000,9999))
	cert.gmtime_adj_notBefore(0)
	cert.gmtime_adj_notAfter(604800)  # 7 days...
	cert.set_issuer(cert.get_subject())
	cert.set_pubkey(k)
	cert.sign(k, 'sha256')
	CERT_FILE = "%s.crt" % CN
	PEM_FILE = "%s.pem" % CN
	PUBKEY_FILE = "%s.pub" % CN
	dirpath = tempfile.gettempdir()
	cert_dir = dirpath + os.path.sep
	C_F = join(cert_dir, CERT_FILE)
	K_F = join(cert_dir, PEM_FILE)
	P_F = join(cert_dir, PUBKEY_FILE)
	global tempfiles
	tempfiles.append(C_F)
	tempfiles.append(K_F)
	tempfiles.append(P_F)
	print("[#] Generating disposible, one-time-use, self-signed cert files in:  %s" % cert_dir)
	print("[.]%s\n[.]%s\n[.]%s" % (C_F, K_F, P_F))
	open(C_F, 'wt').write((crypto.dump_certificate(crypto.FILETYPE_PEM, cert)).decode("utf-8"))
	open(K_F, 'wt').write((crypto.dump_privatekey(crypto.FILETYPE_PEM, pkey=k)).decode("utf-8"))
	open(P_F, 'wt').write((crypto.dump_publickey(crypto.FILETYPE_PEM, pkey=k)).decode("utf-8"))
	return C_F, K_F, P_F


class AuthHandler(SimpleHTTPRequestHandler):
	## Based on https://gist.github.com/fxsjy/5465353 ,  just refactored, 'sall 
	''' Main class to present webpages and authentication. '''
	def do_HEAD(self):
		print("send header")
		self.send_response(200)
		self.send_header('Content-type', 'text/html')
		self.end_headers()

	def do_AUTHHEAD(self):
		print("send header")
		self.send_response(401)
		self.send_header('WWW-Authenticate', 'Basic realm=\"PROD\"')
		self.send_header('Content-type', 'text/html')
		self.end_headers()

	def do_GET(self):
		global ARGS
		key = base64.b64encode(bytes(ARGS['auth'].encode("utf-8")))
		''' Present frontpage with user authentication. '''
		if self.headers.get('Authorization') == None:
			self.do_AUTHHEAD()
			self.wfile.write(bytes('no auth header received'.encode("utf-8")))
			pass
		elif self.headers.get('Authorization') == 'Basic '+key.decode('utf-8'):
			SimpleHTTPRequestHandler.do_GET(self)
			pass
		else:
			self.do_AUTHHEAD()
			self.wfile.write(bytes(self.headers.get('Authorization').encode("utf-8")))
			self.wfile.write(bytes('not authenticated'.encode("utf-8")))
			pass


def build_server(ARGS):
	# httpd = HTTPServer((ARGS.ip, ARGS.port), SimpleHTTPRequestHandler)
	if not ARGS['auth'] == None:
		httpd = HTTPServer((ARGS['ip'], ARGS['port']), AuthHandler)
	else:
		httpd = HTTPServer((ARGS['ip'], ARGS['port']), SimpleHTTPRequestHandler)
	if ARGS['https']:
		if ARGS['cert'] and ARGS['privatekey']:
			CERT = ARGS['cert']
			PEM = ARGS['privatekey']
		else:
			global tempfiles
			CERT, PEM, PUBKEY = gencert()
		httpd.socket = ssl.wrap_socket (httpd.socket, certfile=CERT, keyfile=PEM, server_side=True)
	try:
		print("[#] Now serving HTTP%s on %s:%s %s" % (
			"S" if ARGS['https'] else "", 
			ARGS['ip'],
			ARGS['port'],
			"with AUTH "+ARGS['auth'] if ARGS['auth'] else ""
		))
		print("[#] Ctrl+C to stop server\n")
		httpd.serve_forever()
	except TypeError:
		pass
	except KeyboardInterrupt:
		if len(tempfiles) > 0:
			for item in tempfiles:
				os.remove(item)
		sys.exit()
	


def main():
	global ARGS
	ARGS = Get_Args()
	build_server(ARGS)
	sys.exit()


if __name__=="__main__":
	main()
