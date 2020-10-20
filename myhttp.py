#
# Helper functions for HTTP
#

def urlencode(s):
	"""
	Perform standard URL encoding per RFC 1738
	"""
	rsvd = b"<>#%\"{}|\\^[]`"
	buf = b""
	for ch in s:
		if ch <= 0x20 or ch in rsvd:
			buf += b"%%%02x" %ch
		else:
			buf += bytes([ch])
	return buf

def urldecode(s):
	"""
	Decode a URL encoded string
	"""

	chs = list(s) # Character stack
	dec = b""     # Decoded string

	while len(chs) > 0:
		ch = chs.pop(0)
		if ch == b"%":
			if len(ch) == 0:
				raise ValueError()
			n = bytes([chs.pop(0)])
			if len(ch) == 0:
				raise ValueError()
			n += bytes([chs.pop(0)])
			dec += bytes([int(n, 16)])
		else:
			dec += bytes([ch])

	return dec

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

def http_parse_req(msg):
	"""
	(Not so) standard compliant HTTP request parser, works fine for the
	subset we care about
	"""

	# Request object
	request = lambda: None

	# Split request into lines
	lines = msg.split(b"\r\n")

	# Parse request line
	request.method, request.path, request.version = \
		lines[0].split(b" ", 2)

	# Run the path through the URL decoder
	request.path = urldecode(request.path)

	# Parse headers
	request.headers = {}
	for hdr in lines[1:]:
		if len(hdr) == 0:
			break
		nam, val = hdr.split(b":", 1)
		request.headers[nam.lower()] = val.lstrip()

	return request

def http_parse_resp(msg):
	"""
	Same as the above, except it parses HTTP responses instead
	"""

	# Response object
	response = lambda: None

	# Split response into lines
	lines = msg.split(b"\r\n")

	# Parse status line
	response.version, response.status, response.reason = \
		lines[0].split(b" ", 2)

	# Parse headers
	response.headers = {}
	for hdr in lines[1:]:
		if len(hdr) == 0:
			break
		nam, val = hdr.split(b":", 1)
		response.headers[nam.lower()] = val.lstrip()

	return response
