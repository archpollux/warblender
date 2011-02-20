#!BPY
"""
Name: 'Warblender - Blizzard Warcraft III files (.mdx)...'
Blender: 233
Group: 'Import'
Tooltip: "Import a model file from Blizzard's Warcraft III"
"""

import Blender
from mdx import mdx
import wbconv


def loadMDX(filename):
	r = mdx.Reader()
	mdxModel = None
	try:
		mdxModel = r.loadFile(filename)
	except mdx.MDXFileFormatError:
		Blender.Draw.Text("Could not read model file")
		raise
	conv = wbconv.Converter()
	bMeshes = conv.toBlender(filename, mdxModel)
	for m in bMeshes:
		Blender.NMesh.PutRaw(m)

print "Warblender"
Blender.Window.FileSelector(loadMDX, "Import MDX")
