import sys
import os
import Blender
from mdx import mdx

TEAMCOLOUR = [0, 0, 1]

class Converter:
	def __init__(self):
		pass

	def toBlender(self, filename, model):
		print "Converting model %s to Blender data structures" % (repr(model.MODL.Name))
		bObjects = []

		# textures
		(filepath, dummy) = os.path.split(filename)
		TEXTURES = []
		for texnr in range(model.TEXS.ntexs):
			tex = Blender.Texture.New(model.MODL.Name + "_tex" + str(texnr))
			tex.setType('Image')
			tex.setImageFlags('InterPol', 'UseAlpha', 'MipMap')
			texturefile = model.TEXS.textures[texnr].TexturePath;
			if texturefile!='':
				if os.name!='nt':
					texturefile = texturefile.replace("\\", "/")
				(texturefile, dummy) = os.path.splitext(texturefile)
				texturefile = os.path.join(filepath, texturefile + ".png")
				sys.stderr.write("texture %d: PNG texture file (%s)\n" % (texnr, texturefile))
				try:
					tex.setImage(Blender.Image.Load(texturefile))
				except IOError:
					pass
				TEXTURES.append(tex)
			else:
				sys.stderr.write("texture %d: None\n" % texnr)
				TEXTURES.append(None)


		# materials
		MATERIALS = []
		for matnr in range(model.MTLS.nmtls):
			mat = Blender.Material.New(model.MODL.Name + "_mat" + str(matnr))
			mat.setRGBCol(TEAMCOLOUR)
			mat.setMode('Shadeless', 'ZTransp')
			setTexFace = 1
			for laynr in range(model.MTLS.materials[matnr].LAYS.nlays):
				mapto = 0
				lay = model.MTLS.materials[matnr].LAYS.layers[laynr]
				if lay.FilterMode == 1:
					mapto = mapto | Blender.Texture.MapTo.ALPHA | Blender.Texture.MapTo.COL
				elif lay.FilterMode == 2:
					mapto = mapto | Blender.Texture.MapTo.COL
					setTexFace = 0
				elif lay.FilterMode == 3:
					# set 'texture blending mode' to 'add'
					pass
				elif lay.FilterMode == 4:
					# set 'texture blending mode' to 'add'
					mapto = mapto | Blender.Texture.MapTo.ALPHA
				elif lay.FilterMode == 5:
					# modulate ??					
					pass
				tex = TEXTURES[model.MTLS.materials[matnr].LAYS.layers[laynr].TextureID]
				if tex!=None:
					mat.setTexture(laynr, tex, Blender.Texture.TexCo.UV, mapto)
					# FIXME we also need a way to specify the other kind of ALPHA setting
					# FIXME as well as the DVar option in the MapTo tab of Shading->Material Buttons
			if setTexFace==1:
				mat.setMode('TexFace')
			MATERIALS.append(mat)

		# geosets
		for j in range(len(model.GEOS.geosets)):
			obj = model.GEOS.geosets[j]
			mymesh = Blender.NMesh.New(model.MODL.Name + str(j))
			sys.stderr.write("mesh %d: %d NRMS\n" % (j, obj.NRMS.nvrts))
				
			mymesh.setMaterials([MATERIALS[obj.MaterialID]]);
			mymesh.hasFaceUV(1);

			# vertices
			nrverts = 0
			for k in range(len(obj.VRTX.vertices)):
				vert = obj.VRTX.vertices[k]
				x = vert.x
				y = vert.y
				z = vert.z
				v = Blender.NMesh.Vert(x, y, z)
				#sys.stderr.write("initial normal %d = %s\n" % (k, repr(v.no)))
				v.no[0] = obj.NRMS.vertices[k].x
				v.no[1] = obj.NRMS.vertices[k].y
				v.no[2] = obj.NRMS.vertices[k].z
				#sys.stderr.write("normal %d = %s\n" % (k, repr(v.no)))
				#if HAS_TEX==1:
				#	v.uvco[0] = obj.UVAS.UVBS[0].vertices[k].x;
				#	v.uvco[1] = obj.UVAS.UVBS[0].vertices[k].y;
				mymesh.verts.append(v)
				nrverts += 1
			sys.stderr.write("mesh %d: %d verts\n" % (j, nrverts))
			
			Blender.NMesh.PutRaw(mymesh)
			# vertex groups
			GROUPS = []
			for k in range(len(obj.GNDX.vertexGroups)):
				if obj.GNDX.vertexGroups[k] > len(GROUPS)-1:
					GROUPS.insert(obj.GNDX.vertexGroups[k], [k])
				else:
					GROUPS[obj.GNDX.vertexGroups[k]].append(k)
			for k in range(len(GROUPS)):
				mymesh.addVertGroup('grp' + str(k))
				mymesh.assignVertsToGroup('grp'+str(k), GROUPS[k], 1.0, 'replace')
		
			# faces
			nrfaces = 0
			for i in range(obj.PVTX.nvrts / 3):
				v1 = obj.PVTX.vertices[3 * i]
				v2 = obj.PVTX.vertices[3 * i + 1]
				v3 = obj.PVTX.vertices[3 * i + 2]
				face = Blender.NMesh.Face([mymesh.verts[v1], mymesh.verts[v2], mymesh.verts[v3]])
	
				uv_v1 = (obj.UVAS.UVBS[0].vertices[v1].x, 1-obj.UVAS.UVBS[0].vertices[v1].y);
				uv_v2 = (obj.UVAS.UVBS[0].vertices[v2].x, 1-obj.UVAS.UVBS[0].vertices[v2].y);
				uv_v3 = (obj.UVAS.UVBS[0].vertices[v3].x, 1-obj.UVAS.UVBS[0].vertices[v3].y);
				face.uv = [uv_v1, uv_v2, uv_v3];
				face.mode = face.mode | Blender.NMesh.FaceModes['TEX'];
				#face.transp = Blender.NMesh.FaceTranspModes['ALPHA'];
				#face.image = teximg;
				face.mat = 0;
				mymesh.faces.append(face)
				nrfaces += 1
			sys.stderr.write("mesh %d: %d faces\n" % (j, nrfaces))

			mymesh.update()
			bObjects.append(mymesh)

			# bones
		return bObjects
