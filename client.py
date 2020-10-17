#!/usr/bin/python3
import os
import sys
import socket

def cmd_list(conn):
	pass

def cmd_get(conn):
	pass

def cmd_put(conn):
	pass

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

	# Validate port
	try:
		port = int(sys.argv[2])
		if port < 0 or port > 65535:
			raise ValueError()
	except:
		print("Invalid port number", file=sys.stderr)
		exit(1)

	# Setup TCP socket
	conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	conn.connect((sys.argv[1], port))

	# Invalid command handler
	def cmd_invalid(conn):
		print("Invalid command %s" %sys.argv[3])
		exit(1)

	# Call command handler
	cmds.get(sys.argv[3], cmd_invalid)(conn)

	# Close socket
	conn.close()

if __name__ == "__main__":
	main()
