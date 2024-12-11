import codecs
import json
import pickle
import sys

input_string = sys.stdin.read()

def unpickle(p):
    return pickle.loads(codecs.decode(bytes(p, "utf-8"), "base64"))

d = {}
for row in json.loads(input_string):
    d[row['key'].lower()] = unpickle(row['value'])

print(json.dumps(d, default=str))
