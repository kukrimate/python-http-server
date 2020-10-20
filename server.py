#!/usr/bin/python3
import os
import sys
import socket
from myhttp import *

# Helper functions for sending HTTP responses
def http_200(conn, data):
	conn.send(b"HTTP/1.0 200 OK\r\n")
	conn.send(b"Content-Length: %d\r\n\r\n" %len(data))
	conn.send(data)

def http_400(conn, data):
	conn.send(b"HTTP/1.0 400 Bad Requst\r\n")
	conn.send(b"Content-Length: %d\r\n\r\n" %len(data))
	conn.send(data)

def http_403(conn, data):
	conn.send(b"HTTP/1.0 403 Forbidden\r\n")
	conn.send(b"Content-Length: %d\r\n\r\n" %len(data))
	conn.send(data)

def http_404(conn, data):
	conn.send(b"HTTP/1.0 404 Not Found\r\n")
	conn.send(b"Content-Length: %d\r\n\r\n" %len(data))
	conn.send(data)

def http_get(conn, req):
	if req.path == b"/": # User wants dir listing
		listing = "\n".join(os.listdir()) + "\n"
		http_200(conn, listing.encode())
	else:		     # User wants file
		filepath = "." + req.path.decode()
		if "/" in filepath:
			http_403(conn, b"No path traversal today :)\n")
			return
		if os.path.isfile(filepath):
			with open(filepath, "rb") as file:
				http_200(conn, file.read())
		else:
			http_404(conn, b"File not found\n")

def http_put(conn, req):
	filepath = "." + req.path.decode()
	filesize = int(req.headers[b"content-length"])

	if "/" in filepath:
		http_403(conn, b"No path traversal today :)")
		return

	if os.path.exists(filepath):
		http_403(conn, b"Sorry, no overwrites allowed\n")
		return

	data = recieve_max(conn, filesize)
	with open(filepath, "wb") as file:
		file.write(data)

	http_200(conn, b"File uploaded\n")

handlers = {
	b"GET": http_get,
	b"PUT": http_put,
}

def handle_connection(conn):
	"""
	Handles an incoming connection, takes the socket file descriptor as an
	argument
	"""

	try:
		req = http_parse_req(http_read(conn))
		handlers[req.method](conn, req)
	except:
		try:
		# Ignore nested exceptions, as we dont care if the 400
		# reaches the client or not
			http_400(conn, b"Invalid request\n")
		except:
			pass

def main():
	"""
	Entry point of the server
	"""

	# Make sure we got enough arguments
	if len(sys.argv) < 2:
		print("Usage: %s <port number>" %sys.argv[0], file=sys.stderr)
		exit(1)

	# Validate port number
	try:
		port = int(sys.argv[1])
		if port < 1 or port > 65535:
			raise ValueError()
	except ValueError:
		print("Invalid port")
		exit(1)

	server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	server.bind(("", port))
	server.listen(10)

	# Catch SIGINT so we can exit cleanly
	try:
		while True:
			conn, addr = server.accept()

			# Fork a child process to handle an incoming connection
			pid = os.fork()

			if pid == 0:
				# We are in the child process

				# Print client address
				print("Connection from: %s" %str(addr))

				# Handle the connection
				handle_connection(conn)

				# Close the file descriptor and exit
				conn.close()
				exit(0)
			else:
				# We are in the parent process

				# Clost the file descriptor as the
				# child handles the connection
				conn.close()

				# Continue to handle new connections
				continue

	except KeyboardInterrupt:
		# Close the server socket and exit
		server.close()
		exit(0)

if __name__ == "__main__":
	main()
