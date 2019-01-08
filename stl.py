import struct

class Coord():
	def __init__(self, x, y, z):
		self.x = x
		self.y = y
		self.z = z

class Triangle():
	def __init__(self, normal, c0, c1, c2):
		self.normal = normal
		self.c0 = c0
		self.c1 = c1
		self.c2 = c2

class Stl():
	def __init__(self):
		self.header = b"\x00" * 80
		self.triangles = []

	def saveToFile(self, fileToWrite):
		header = self.header
		if len(header) < 80:
			header += b"\x00" * (80 - len(header))
		else:
			header = header[0:80]
		f = open(fileToWrite, "wb")
		f.write(header)
		f.write(struct.pack("I", len(self.triangles)))
		for t in self.triangles:
			f.write(struct.pack("ffffffffffffxx",
				t.normal.x, t.normal.y, t.normal.z, t.c0.x, t.c0.y, t.c0.z,
				t.c1.x, t.c1.y, t.c1.z, t.c2.x, t.c2.y, t.c2.z))
		f.close()
