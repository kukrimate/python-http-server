#!/usr/bin/python3
import os
import sys
import socket
from myhttp import *

def http_request(conn, method, path, data):
	conn.send(b"%s %s HTTP/1.0\r\n" %(method, urlencode(path)))
	if len(data) > 0:
		conn.send(b"Content-Length: %d\r\n" %len(data))
	conn.send(b"\r\n")
	conn.send(data)

def http_get_content(conn, resp):
	clen = int(resp.headers[b"content-length"])
	return recieve_max(conn, clen)

def cmd_list(conn):
	# Send GET /
	http_request(conn, b"GET", b"/", b"")

	# Read response
	response = http_parse_resp(http_read(conn))
	content = http_get_content(conn, response)

	if response.status != b"200":
		print("Server Error %s: %s"
			%(response.status.decode(),
			content.decode().strip()),
			file=sys.stderr)
	else:
		print(content.decode(), end="")


def cmd_get(conn):
	if len(sys.argv) < 5:
		print("Usage: %s server port get filename" \
			%sys.argv[0], file=sys.stderr)
		exit(1)

	filename = sys.argv[4]

	# Send GET /filename
	http_request(conn, b"GET", ("/" + filename).encode(), b"")

	# Read response
	response = http_parse_resp(http_read(conn))
	content = http_get_content(conn, response)

	if response.status != b"200":
		print("Server Error %s: %s"
			%(response.status.decode(),
			content.decode().strip()),
			file=sys.stderr)
	else:
		with open(filename, "wb") as file:
			file.write(content)


def cmd_put(conn):
	if len(sys.argv) < 5:
		print("Usage: %s server port put filename" \
			%sys.argv[0], file=sys.stderr)
		exit(1)

	filename = sys.argv[4]

	# Read file data
	with open(filename, "rb") as file:
		data = file.read()

	# Send PUT /filename
	http_request(conn, b"PUT", ("/" + filename).encode(), data)

	# Read response
	response = http_parse_resp(http_read(conn))
	content = http_get_content(conn, response)

	if response.status != b"200":
		print("Server Error %s: %s"
			%(response.status.decode(),
			content.decode().strip()),
			file=sys.stderr)


cmds = {
	"list": cmd_list,
	"get":  cmd_get,
	"put":  cmd_put,
}

def main():
	if len(sys.argv) < 4:
		print("Usage: %s server port list|get|put" \
			%sys.argv[0], file=sys.stderr)
		exit(1)

	server = sys.argv[1]
	port   = sys.argv[2]
	cmd    = sys.argv[3]

	# Validate port
	try:
		port = int(port)
		if port < 0 or port > 65535:
			raise ValueError()
	except:
		print("Invalid port number", file=sys.stderr)
		exit(1)

	# Validate command
	if cmd not in cmds:
		print("Invalid command %s" %cmd, file=sys.stderr)
		exit(1)

	# Setup TCP socket
	conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	conn.connect((server, port))

	# Call command handler
	cmds[cmd](conn)

	# Close socket
	conn.close()

if __name__ == "__main__":
	main()
