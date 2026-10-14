"""F-SDA32CB photo-based review model, mm; dimensions not supplied are provisional."""
from pathlib import Path
import cadquery as cq
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle, PathPatch
from matplotlib.path import Path as MPath
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
out=Path(__file__).resolve().parent
BASE=44; THICKNESS=4; EAR_OUTSIDE=28; GAP=15; EAR_DEPTH=20; HOLE=10; AXIS_Z=22; HEIGHT=32; ROOT_RADIUS=2
EAR_THICKNESS=(EAR_OUTSIDE-GAP)/2
base=cq.Workplane('XY').rect(BASE,BASE).extrude(THICKNESS).edges('|Z').fillet(2)
part=base
for x in [-EAR_OUTSIDE/2,GAP/2]:
 ear=(cq.Workplane('YZ',origin=(x,0,0)).moveTo(-10,THICKNESS).lineTo(10,THICKNESS).lineTo(10,AXIS_Z)
      .threePointArc((0,HEIGHT),(-10,AXIS_Z)).close().extrude(EAR_THICKNESS))
 part=part.union(ear)
# Radius at four ear-to-plate root edges; does not add a raised cross.
edges=[]
for e in part.val().Edges():
 b=e.BoundingBox()
 if abs(b.zmin-THICKNESS)<1e-6 and abs(b.zmax-THICKNESS)<1e-6 and abs(e.Length()-EAR_DEPTH)<1e-6:
  edges.append(e)
assert len(edges)==4, len(edges)
part=part.newObject(edges).fillet(ROOT_RADIUS)
hole=cq.Solid.makeCylinder(HOLE/2,40,cq.Vector(-20,0,AXIS_Z),cq.Vector(1,0,0))
part=part.cut(hole)
solid=part.val(); assert solid.isValid() and len(part.solids().vals())==1
cq.exporters.export(part,str(out/'32cb_flat.step'))
cq.exporters.export(part,str(out/'32cb_flat.stl'),tolerance=.03,angularTolerance=.08)
# Reload the exchange file to verify the exported solid.
loaded=cq.importers.importStep(str(out/'32cb_flat.step'))
assert loaded.val().isValid() and len(loaded.solids().vals())==1
verts,faces=solid.tessellate(.10)
v=np.array([[p.x,p.y,p.z] for p in verts]); f=np.array(faces)
fig=plt.figure(figsize=(12,8),layout='constrained'); gs=fig.add_gridspec(2,2)
ax=fig.add_subplot(gs[0,0],projection='3d')
tri=v[f]; normals=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]); normals/=np.maximum(np.linalg.norm(normals,axis=1)[:,None],1e-12)
light=np.array([.4,-.6,.7]); light/=np.linalg.norm(light); shade=.45+.55*np.maximum(0,normals@light); colors=shade[:,None]*np.array([.64,.78,.86])[None,:]
poly=Poly3DCollection(tri,facecolors=colors,edgecolor='none'); ax.add_collection3d(poly)
ax.set(xlim=(-24,24),ylim=(-24,24),zlim=(0,35)); ax.set_box_aspect((48,48,35)); ax.view_init(22,-55); ax.set_axis_off(); ax.set_title('Isometric: no pin, no mounting holes')
ax=fig.add_subplot(gs[0,1]); ax.add_patch(Rectangle((-22,0),44,4,fc='#c3d5df',ec='black'))
for x in [-14,7.5]: ax.add_patch(Rectangle((x,4),6.5,28,fc='#c3d5df',ec='black'))
ax.plot([-14,14],[22,22],ls='-.',c='gray'); ax.annotate('15 clear gap',xy=(0,15),ha='center',fontsize=10)
ax.annotate('',xy=(-14,35),xytext=(14,35),arrowprops=dict(arrowstyle='<->')); ax.text(0,36,'28 outside',ha='center')
ax.annotate('',xy=(18,0),xytext=(18,22),arrowprops=dict(arrowstyle='<->')); ax.text(19,12,'22',rotation=90)
ax.text(-20,6,'4 plate',fontsize=9); ax.set_title('Along pin axis (root fillets omitted)'); ax.set_xlim(-25,25); ax.set_ylim(-3,40)
ax=fig.add_subplot(gs[1,0]); ax.add_patch(Rectangle((-22,0),44,4,fc='#c3d5df',ec='black'))
t=np.linspace(0,np.pi,80); points=[(-10,4),(10,4),(10,22)]+list(zip(10*np.cos(t),22+10*np.sin(t)))+[(-10,4)]
ax.add_patch(plt.Polygon(points,fc='#c3d5df',ec='black')); ax.add_patch(Circle((0,22),5,fc='white',ec='black'))
ax.plot([-15,15],[22,22],ls='-.',c='gray'); ax.plot([0,0],[4,34],ls='-.',c='gray'); ax.text(6,24,'D10'); ax.text(-9,11,'Ear width 20')
ax.annotate('',xy=(18,0),xytext=(18,32),arrowprops=dict(arrowstyle='<->')); ax.text(19,16,'32 total',rotation=90); ax.set_xlim(-25,25); ax.set_ylim(-3,40); ax.set_title('Ear face (root fillets omitted)')
ax=fig.add_subplot(gs[1,1]); ax.add_patch(Rectangle((-22,-22),44,44,fc='#e6edf1',ec='black'))
for x in [-14,7.5]: ax.add_patch(Rectangle((x,-10),6.5,20,fc='#91b0c2',ec='black'))
ax.text(0,15,'44 x 44 plate\nNo mounting holes',ha='center'); ax.set_xlim(-25,25); ax.set_ylim(-25,25); ax.set_title('Top (corner/root fillets omitted)')
for ax in fig.axes[1:]: ax.set_aspect('equal'); ax.axis('off')
fig.suptitle('F-SDA32CB flat-base modification | REVIEW v1 | mm\nPhoto-based; plate thickness, second side, root/corner radii provisional',fontsize=14)
fig.savefig(out/'preview.png',dpi=170); fig.savefig(out/'review_drawing.pdf')
b=solid.BoundingBox(); print('Valid single solid; STEP round-trip passed; bounds mm:',b.xlen,b.ylen,b.zlen,'volume mm3:',solid.Volume())
