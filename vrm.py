import json
import struct

class Buffer():
	def __init__(self, info, defaultData):
		self.byteLength = info["byteLength"]
		if "uri" in info:
			self.uri = info["uri"]
			self.data = None
		else:
			self.uri = None
			self.data = defaultData

	def read(self, offset, length):
		if self.data is None:
			raise Exception("unsuppoted buffer type")
		if offset < 0 or self.byteLength < offset + length:
			#raise Exception("out-of-bounds buffer read")
			print("warning: out-of-bounds buffer read?")
		return self.data[offset:offset+length]

class BufferView():
	def __init__(self, info, buffers):
		self.buffer = buffers[info["buffer"]]
		self.byteOffset = info["byteOffset"]
		self.byteLength = info["byteLength"]
		if "byteStride" in info:
			self.byteStride = info["byteStride"]
		else:
			self.byteStride = None

	def read(self, offset, length):
		if offset < 0 or self.byteLength < offset + length:
			raise Exception("out-of-bound bufferView read")
		readOffset = self.byteOffset + offset
		return self.buffer.read(readOffset, length)

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

	def __init__(self, info, bufferViews):
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
			raise Exception("out-of-range accessor get")
		return struct.unpack(self.unpackStr,
			self.bufferView.read(self.stride * index, self.elementSize))

class Image():
	def __init__(self, info, bufferViews):
		if "uri" in info:
			self.uri = info["uri"]
		else:
			self.uri = None
		if "bufferView" in info:
			self.bufferView = bufferViews[info["bufferView"]]
			self.mimeType = info["mimeType"]
		else:
			self.bufferView = None
			self.mimeType = None
		if self.uri is not None and self.bufferView is not None:
			raise Exception("both uri and bufferView is provided for image")

	def getData(self):
		if self.uri is not None:
			raise Exception("uri image is not supported")
		else:
			return self.bufferView.read(0, self.bufferView.byteLength)

class Sampler():
	def __init__(self, info):
		self.info = info

class Texture():
	def __init__(self, info, samplers, images):
		self.sampler = samplers[info["sampler"]]
		self.source = images[info["source"]]

class Material():
	def __init__(self, info, textures):
		self.name = info["name"]
		pmr = info["pbrMetallicRoughness"]
		if "baseColorFactor" in pmr:
			self.baseColorFactor = pmr["baseColorFactor"]
		else:
			self.baseColorFactor = None
		if "baseColorTexture" in pmr:
			self.baseColorTextureIndex = pmr["baseColorTexture"]["index"]
			self.baseColorTexture = textures[pmr["baseColorTexture"]["index"]]
			self.baseColorTextureCoord =  textures[pmr["baseColorTexture"]["texCoord"]]
		else:
			self.baseColorTextureIndex = None
			self.baseColorTexture = None
			self.baseColorTextureCoord = None
		self.metallicFactor = pmr["metallicFactor"]
		self.roughnessFactor = pmr["roughnessFactor"]

class Vertex():
	FLOAT = 1
	UNSIGNED_BYTE = 2
	UNSIGNED_SHORT = 3

	def __init__(self):
		self.index = None
		self.position = None
		self.normal = None
		self.tangent = None
		self.texCoord0 = self.texCoord0Type = None
		self.texCoord1 = self.texCoord1Type = None
		self.color0 = self.color0Type = None
		self.joints0 = self.joints0Type = None
		self.weights0 = self.weights0Type = None
		pass

class Primitive():
	TYPES = {
		5126 : Vertex.FLOAT,
		5121 : Vertex.UNSIGNED_BYTE,
		5123 : Vertex.UNSIGNED_SHORT
	}

	def __init__(self, info, accessors, materials):
		indices = accessors[info["indices"]]
		def readAttribute(name):
			if name in info["attributes"]:
				return accessors[info["attributes"][name]]
			else:
				return None
		positions = readAttribute("POSITION")
		normals = readAttribute("NORMAL")
		tangents = readAttribute("TANGENT")
		texCoord0s = readAttribute("TEXCOORD_0")
		texCoord1s = readAttribute("TEXCOORD_1")
		color0s = readAttribute("COLOR_0")
		joints0s = readAttribute("JOINTS_0")
		weights0s = readAttribute("WEIGHTS_0")

		self.materialIndex = info["material"]
		self.material = materials[self.materialIndex]
		self.vertice = []
		for i in range(indices.count):
			idx = indices.get(i)[0]
			vert = Vertex()
			vert.index = idx
			if positions  is not None:
				vert.position      = positions.get(idx)
			if normals    is not None:
				vert.normal        = normals.get(idx)
			if tangents   is not None:
				vert.tangent       = tangents.get(idx)
			if texCoord0s is not None:
				vert.texCoord0     = texCoord0s.get(idx)
				vert.texCoord0Type = Primitive.TYPES[texCoord0s.componentType]
			if texCoord1s is not None:
				vert.texCoord1     = texCoord1s.get(idx)
				vert.texCoord1Type = Primitive.TYPES[texCoord1s.componentType]
			if color0s    is not None:
				vert.color0        = color0s.get(idx)
				vert.color0Type    = Primitive.TYPES[color0s.componentType]
			if joints0s   is not None:
				vert.joints0       = joints0s.get(idx)
				vert.joints0Type   = Primitive.TYPES[joints0s.componentType]
			if weights0s  is not None:
				vert.weights0      = weights0s.get(idx)
				vert.weights0Type  = Primitive.TYPES[weights0s.componentType]
			self.vertice.append(vert)

class Mesh():
	def __init__(self, info, accessors, materials):
		self.name = info["name"]
		self.primitives = [Primitive(p, accessors, materials) for p in info["primitives"]]

class Vrm():
	def __init__(self):
		pass

	@staticmethod
	def loadFromFile(fileName):
		vrmFile = open(fileName, "rb")
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
		defaultData = vrmData[binOffset:]

		buffers = [Buffer(b, defaultData) for b in jsonData["buffers"]]
		bufferViews = [BufferView(bv, buffers) for bv in jsonData["bufferViews"]]
		accessors = [Accessor(info, bufferViews) for info in jsonData["accessors"]]
		images = [Image(i, bufferViews) for i in jsonData["images"]]
		samplers = [Sampler(s) for s in jsonData["samplers"]]
		textures = [Texture(t, samplers, images) for t in jsonData["textures"]]
		materials = [Material(m, textures) for m in jsonData["materials"]]
		meshes = [Mesh(m, accessors, materials) for m in jsonData["meshes"]]

		vrm = Vrm()
		vrm.json = jsonData
		vrm.bin = defaultData
		vrm.buffers = buffers
		vrm.bufferViews = bufferViews
		vrm.acccssors = accessors
		vrm.meshes = meshes
		vrm.images = images
		vrm.samplers = samplers
		vrm.textures = textures
		vrm.materials = materials
		return vrm
