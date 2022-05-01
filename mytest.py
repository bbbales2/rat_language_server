import json
import logging
import re
import sys
import threading
import time
import jsonrpcserver
import jsonrpcclient

logging.basicConfig(filename="mytest.log", encoding="utf-8", level=logging.DEBUG, filemode = "w")

def read_json_rpc():
	content_length = None
	content_type = None

	while True:
		#logging.debug("Waiting for new message in")
		line = sys.stdin.readline().strip()
		#logging.debug("Got new message!")
		if len(line) == 0:
			break
		cmd, string_value = line.split(":")

		if cmd == "Content-Length":
			content_length = int(string_value)
		elif cmd == "Content-Type":
			content_type = string_value
		else:
			raise Exception("Unrecognized command!")

	if content_length is None:
		raise Exception("Content length never set!")

	return sys.stdin.read(content_length)

def write_json_rpc(string_obj):
	output_string = f"Content-Length:{len(string_obj)}\r\n\r\n{string_obj}"
	logging.debug(f"Writing out message: {repr(output_string)}")
	sys.stdout.write(output_string)
	sys.stdout.flush()

@jsonrpcserver.method
def initialize(processId, rootUri, capabilities, **kwargs):
	return jsonrpcserver.Success({
		"capabilities": {
			"textDocumentSync": 1,
			# Tell the client that this server supports code completion.
			# "completionProvider": {
			#	"resolveProvider": True
			# }
		}
	})

def publishDiagnostics(uri, diagnostics):
	message_out = jsonrpcclient.notification_json(
		"textDocument/publishDiagnostics",
		params = {
			"uri" : uri,
			"diagnostics" : diagnostics
		}
	)
	write_json_rpc(message_out)

versions = {}
text = {}

def validateDocument(uri : str):
	diagnostics = []
	for line_number, line in enumerate(text[uri].split("\n")):
		for match in re.finditer("match[a-z]*", line.strip()):
			diagnostics.append({
				"range" : {
					"start" : { "line" : line_number, "character" : match.start()},
					"end" : { "line" : line_number, "character" : match.end()}
				},
				"message" : match.string[match.start():match.end()]
			})
	publishDiagnostics(uri, diagnostics)

@jsonrpcserver.method(name = "textDocument/didOpen")
def didOpen(textDocument):
	uri : str = textDocument["uri"]
	versions[uri] = textDocument["version"]
	text[uri] = textDocument["text"]

	validateDocument(uri)

	return jsonrpcserver.Success()

@jsonrpcserver.method(name = "textDocument/didChange")
def didChange(textDocument, contentChanges):
	uri : str = textDocument["uri"]
	version : int = textDocument["version"]
	if versions[uri] < version:
		if len(contentChanges) != 1:
			raise Exception("There should be exactly one change. textDocumentSync should be for full document only, not incremental")
		text[uri] = contentChanges[0]["text"]

		validateDocument(uri)

	return jsonrpcserver.Success()

@jsonrpcserver.method(name = "textDocument/didClose")
def didClose(textDocument):
	uri : str = textDocument["uri"]
	del versions[uri]
	del text[uri]

	return jsonrpcserver.Success()

process = False
while True:
	message_in = read_json_rpc()
	logging.debug(f"Reading in message: {message_in}")
	message_out = jsonrpcserver.dispatch(message_in)
	if message_out:
		write_json_rpc(message_out)
	else:
		logging.debug("No response to notification necessary")
