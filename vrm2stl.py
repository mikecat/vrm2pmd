import sys
import vrm
import stl
from math import sqrt

if len(sys.argv) < 3:
	sys.stderr.write("Usage: python %s input_file output_file\n" % sys.argv[0])
	sys.exit(1)

vrmData = vrm.Vrm.loadFromFile(sys.argv[1])
stlData = stl.Stl()
for mesh in vrmData.meshes:
	for primitive in mesh.primitives:
		triangle = []
		for vert in primitive.vertice:
			triangle.append(vert)
			if len(triangle) >= 3:
				normal = stl.Coord(0.0, 0.0, 0.0)
				coords = []
				for v in triangle:
					p = v.position
					n = v.normal
					coords.append(stl.Coord(p[0], p[1], p[2]))
					normal.x += n[0]
					normal.y += n[1]
					normal.z += n[2]
				l = sqrt(normal.x * normal.x + normal.y * normal.y + normal.z * normal.z)
				if l >= 1e-6:
					normal.x /= l
					normal.y /= l
					normal.z /= l
				stlData.triangles.append(stl.Triangle(normal, coords[0], coords[1], coords[2]))
				triangle = []
stlData.saveToFile(sys.argv[2])
