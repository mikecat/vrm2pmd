import sys
import json
import struct

if len(sys.argv) < 3:
	sys.stderr.write("Usage: python %s input_file output_file\n" % sys.argv[0])
	sys.exit(1)

vrmFile = open(sys.argv[1], "rb")
vrmData = vrmFile.read()
vrmFile.close()

if vrmData[0:8] != b"glTF\x02\x00\x00\x00":
	raise Exception("unexpected header")

if vrmData[0x10:0x14] != b"JSON":
	raise Exception("not JSON")

jsonSize = struct.unpack("I", vrmData[12:16])[0]
jsonData = json.JSONDecoder().decode(vrmData[0x14:0x14+jsonSize].decode("UTF-8"))

if vrmData[0x14+jsonSize+4:0x14+jsonSize+8] != b"BIN\0":
	raise Exception("not BIN")
binOffset = 0x14+jsonSize+8

bufferData = jsonData["buffers"]

class BufferView():
	def __init__(self, info):
		self.buffer = info["buffer"]
		self.byteOffset = info["byteOffset"]
		self.byteLength = info["byteLength"]
		if "byteStride" in info:
			self.byteStride = info["byteStride"]
		else:
			self.byteStride = None
		if "uri" in bufferData[self.buffer]:
			self.uri = bufferData[self.buffer]["uri"]
		else:
			self.uri = None
	def read(self, offset, length):
		if self.uri is None:
			if offset + length > self.byteLength or offset < 0:
				raise Exception("out-of-bound read")
			readOffset = binOffset + self.byteOffset + offset
			return vrmData[readOffset:readOffset+length]
		else:
			raise Exception("uri reading not supported")

bufferViews = [BufferView(bv) for bv in jsonData["bufferViews"]]

class Accessor():
	COMPONENT_TYPES = {
		5120 : (1, "b"),
		5121 : (1, "B"),
		5122 : (2, "h"),
		5123 : (2, "H"),
		5125 : (4, "I"),
		5126 : (4, "f")
	}
	TYPES = {
		"SCALAR" : 1,
		"VEC2" : 2,
		"VEC3" : 3,
		"VEC4" : 4,
		"MAT2" : 4,
		"MAT3" : 9,
		"MAT4" : 16
	}

	def __init__(self, info):
		self.bufferView = bufferViews[info["bufferView"]]
		self.byteOffset = info["byteOffset"]
		self.componentType = info["componentType"]
		self.count = info["count"]
		self.typeName = info["type"]
		self.elementSize = Accessor.COMPONENT_TYPES[self.componentType][0] * \
			Accessor.TYPES[self.typeName]
		self.stride = self.bufferView.byteStride
		if self.stride is None:
			self.stride = self.elementSize
		self.unpackStr = Accessor.COMPONENT_TYPES[self.componentType][1] * \
			Accessor.TYPES[self.typeName]

	def get(self, index):
		if index < 0 or self.count <= index:
			raise Exception("out-of-range get")
		return struct.unpack(self.unpackStr,
			self.bufferView.read(self.stride * index, self.elementSize))

accessors = [Accessor(info) for info in jsonData["accessors"]]

triangles = []

for m in jsonData["meshes"]:
	for p in m["primitives"]:
		indices = accessors[p["indices"]]
		positions = accessors[p["attributes"]["POSITION"]]
		normals = accessors[p["attributes"]["NORMAL"]]
		for i in range(0, indices.count, 3):
			tx, ty, tz = (0., 0., 0.)
			t = []
			for j in range(3):
				idx = indices.get(i + j)[0]
				p = positions.get(idx)
				n = normals.get(idx)
				tx += n[0]
				ty += n[1]
				tz += n[2]
				t.extend([p[0], p[1], p[2]])
			triangles.append(tuple([tx / 3, ty / 3, tz / 3] + t))

of = open(sys.argv[2], "wb")
of.write(b"x" * 80)
of.write(struct.pack("I", len(triangles)))
for t in triangles:
	of.write(struct.pack("ffffffffffffxx",
		t[0], t[1], t[2], t[3], t[4], t[5], t[6], t[7], t[8], t[9], t[10], t[11]))
