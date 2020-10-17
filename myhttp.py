#
# The worst Python HTTP library in existance
#

def http_read(conn):
	"""
	Read an HTTP message from a socket
	"""

	msg = bytearray()

	# NOTE: this is a lot of ugly copy-pasted code, but Python has no
	# macros, and I can't think of another implementation of this that
	# is as fast without macros
	while True:
		b = conn.recv(1)
		if len(b) == 0:
			break
		msg += b
		if b != b"\r":
			continue
		b = conn.recv(1)
		if len(b) == 0:
			break
		msg += b
		if b != b"\n":
			continue
		b = conn.recv(1)
		if len(b) == 0:
			break
		msg += b
		if b != b"\r":
			continue
		b = conn.recv(1)
		if len(b) == 0:
			break
		msg += b
		if b != b"\n":
			continue
		break

	return bytes(msg)

