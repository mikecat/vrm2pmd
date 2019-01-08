import struct

class Vertex():
	def __init__(self):
		self.px = self.py = self.pz = 0.0
		self.nx = self.ny = self.nz = 0.0
		self.u = self.v = 0.0
		self.bone0 = self.bone1 = 0
		self.boneWeight = 100
		self.edgeFlag = 1

class Color():
	def __init__(self, r = 0.0, g = 0.0, b = 0.0):
		self.r = r
		self.g = g
		self.b = b

class Material():
	def __init__(self):
		self.diffuseColor = Color()
		self.alpha = 1.0
		self.specularity = 0.0
		self.specularColor = Color()
		self.mirrorColor = Color()
		self.toonIndex = 0
		self.edgeFlag = 0
		self.faceVertCount = 0
		self.textureFileName = ""

class Bone():
	def __init__(self):
		self.name = ""
		self.parentIndex = 0xffff
		self.tailIndex = 0
		self.boneType = 1
		self.ikIndex = 0
		self.px = self.py = self.pz = 0.0

class Pmd():
	def __init__(self):
		self.vertice = []
		self.faceVert = []
		self.materials = []
		self.bones = []

	def saveToFile(self, fileName):
		f = open(fileName, "wb")
		f.write(b"Pmd")
		f.write(struct.pack("f", 1.00))
		f.write(b"x\x00" + b"\xfd" * 18)
		f.write(b"x\x00" + b"\xfd" * 254)
		f.write(struct.pack("I", len(self.vertice)))
		for v in self.vertice:
			f.write(struct.pack("ffffffffHHBB",
				v.px, v.py, v.pz, v.nx, v.ny, v.nz, v.u, v.v,
				v.bone0, v.bone1, v.boneWeight, v.edgeFlag))
		f.write(struct.pack("I", len(self.faceVert)))
		for fv in self.faceVert:
			f.write(struct.pack("H", fv))
		f.write(struct.pack("I", len(self.materials)))
		for m in self.materials:
			f.write(struct.pack("fffffffffffBB",
				m.diffuseColor.r, m.diffuseColor.g, m.diffuseColor.b,
				m.alpha, m.specularity,
				m.specularColor.r, m.specularColor.g, m.specularColor.b,
				m.mirrorColor.r, m.mirrorColor.g, m.mirrorColor.b,
				m.toonIndex, m.edgeFlag))
			f.write(struct.pack("I", m.faceVertCount))
			f.write((m.textureFileName.encode("Shift_JIS") + b"\x00" + b"\xfd" * 20)[0:20])
		f.write(struct.pack("H", len(self.bones)))
		for b in self.bones:
			f.write((b.name.encode("Shift_JIS") + b"\x00" + b"\xfd" * 20)[0:20])
			f.write(struct.pack("HHB", b.parentIndex, b.tailIndex, b.boneType))
			f.write(struct.pack("H", b.ikIndex))
			f.write(struct.pack("fff", b.px, b.py, b.pz))
		# TODO: implement IK list and more
		f.write(struct.pack("H", 0)) # IK
		f.write(struct.pack("H", 0)) # skin
		f.write(struct.pack("H", 0)) # skin disp
		f.write(struct.pack("B", 0)) # bone disp name
		f.write(struct.pack("I", 0)) # bone disp
		f.close()
