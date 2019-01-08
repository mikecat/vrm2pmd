import sys
import vrm
import pmd
from math import sqrt
from os import path

if len(sys.argv) < 3:
	sys.stderr.write("Usage: python %s input_file output_file [vertice_drop_start]\n" % sys.argv[0])
	sys.exit(1)

if len(sys.argv) >= 4:
	verticeDropStart = int(sys.argv[3])
else:
	verticeDropStart = 0

vrmData = vrm.Vrm.loadFromFile(sys.argv[1])
pmdData = pmd.Pmd()
verticeByPrimitives = []
verticeByMaterials = [[] for i in range(len(vrmData.materials))]
for mesh in vrmData.meshes:
	for primitive in mesh.primitives:
		vertice = []
		primitiveIndex = len(verticeByPrimitives)
		for vert in primitive.vertice:
			verticeByMaterials[primitive.materialIndex].append((primitiveIndex, len(vertice)))
			pmdVertex = pmd.Vertex()
			pmdVertex.px = vert.position[0]
			pmdVertex.py = vert.position[1]
			pmdVertex.pz = -vert.position[2]
			pmdVertex.nx = vert.normal[0]
			pmdVertex.ny = vert.normal[1]
			pmdVertex.nz = -vert.normal[2]
			pmdVertex.u = vert.texCoord0[0]
			pmdVertex.v = vert.texCoord0[1]
			vertice.append(pmdVertex)
		verticeByPrimitives.append(vertice)
verticeOffset = [0]
for vs in verticeByPrimitives:
	pmdData.vertice.extend(vs)
	verticeOffset.append(len(pmdData.vertice))
pmdData.vertice = pmdData.vertice[verticeDropStart:]
verticeByMaterialsCommitCount = []
verticeDropped = False
for vs in verticeByMaterials:
	triangle = []
	commitCount = 0
	for pi, vi in vs:
		triangle.append(verticeOffset[pi] + vi - verticeDropStart)
		if len(triangle) >= 3:
			if 0 <= triangle[0] and 0 <= triangle[1] and 0 <= triangle[2]:
				if triangle[0] < 0x10000 and triangle[1] < 0x10000 and triangle[2] < 0x10000:
					pmdData.faceVert.append(triangle[2])
					pmdData.faceVert.append(triangle[1])
					pmdData.faceVert.append(triangle[0])
					commitCount += 1
				else:
					verticeDropped = True
			triangle = []
	verticeByMaterialsCommitCount.append(commitCount)
if verticeDropped:
	sys.stderr.write("warning: some triangles are dropped due to face vert index limit\n")
for i in range(len(vrmData.materials)):
	m = vrmData.materials[i]
	pmdMaterial = pmd.Material()
	if m.baseColorFactor is not None:
		pmdMaterial.diffuseColor = pmd.Color(m.baseColorFactor[0], m.baseColorFactor[1], m.baseColorFactor[2])
		if len(m.baseColorFactor) >= 3:
			pmdMaterial.alpha = m.baseColorFactor[3]
	else:
		pmdMaterial.diffuseColor = pmd.Color(1.0, 1.0, 1.0)
	pmdMaterial.faceVertCount = verticeByMaterialsCommitCount[i] * 3
	if m.baseColorTextureIndex is not None:
		pmdMaterial.textureFileName = "%d.png" % m.baseColorTextureIndex
	pmdData.materials.append(pmdMaterial)
b0 = pmd.Bone()
b0.name = "root"
b0.tailIndex = 1
b1 = pmd.Bone()
b1.name = "root_to"
b1.parentIndex = 0
b1.boneType = 7
b1.py = 1.0
pmdData.bones = [b0, b1]
pmdData.saveToFile(sys.argv[2])
dir = path.dirname(sys.argv[2])
for i in range(len(vrmData.textures)):
	t = vrmData.textures[i]
	f = open(path.join(dir, "%d.png" % i), "wb")
	f.write(t.source.getData())
	f.close()
