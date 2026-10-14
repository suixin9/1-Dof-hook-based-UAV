from pathlib import Path
import json
import cadquery as cq
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection
out=Path(__file__).resolve().parent
source=cq.importers.importStep(str(out/'source_battery.step')).val()
b=source.BoundingBox(); cy=(b.ymin+b.ymax)/2
bottom=[f for f in source.Faces() if f.geomType()=='PLANE' and f.normalAt().z < -.99][0]
slots=[w for w in bottom.Wires() if w.BoundingBox().xmin > -12 and w.BoundingBox().xmax < 12]
assert len(slots)==3
filled=source
for w in slots:
 plug=cq.Solid.extrudeLinear(w,[],cq.Vector(0,0,1))
 filled=filled.fuse(plug).clean()
assert abs(filled.Volume()-source.Volume()-sum(cq.Face.makeFromWires(w).Area() for w in slots))<1e-5
merged=cq.Workplane(obj=filled)
for y in [cy+14,cy-7.5]:
 ear=(cq.Workplane('XZ',origin=(0,y,0)).moveTo(-10,0).lineTo(10,0).lineTo(10,-22)
      .threePointArc((0,-32),(-10,-22)).close().extrude(6.5))
 merged=merged.union(ear)
edges=[]
for e in merged.val().Edges():
 box=e.BoundingBox()
 if abs(box.zmin)<1e-6 and abs(box.zmax)<1e-6 and abs(e.Length()-20)<1e-6:
  edges.append(e)
assert len(edges)==4
merged=merged.newObject(edges).fillet(2).val()
hole=cq.Solid.makeCylinder(5,40,cq.Vector(0,cy-20,-22),cq.Vector(0,1,0))
merged=merged.cut(hole).clean()
bracket=merged.cut(filled)
source=filled
assert merged.isValid() and len(merged.Solids())==1
assert source.cut(merged).Volume()<1e-6, 'Original battery plate material must be retained'
cq.exporters.export(merged,str(out/'battery_with_clevis.step'))
cq.exporters.export(merged,str(out/'battery_with_clevis.stl'),tolerance=.03,angularTolerance=.08)
loaded=cq.importers.importStep(str(out/'battery_with_clevis.step')).val()
assert loaded.isValid() and len(loaded.Solids())==1
hook=cq.importers.importStep(str(out/'inputs'/'hook_review.step')).val().translate((0,cy,-453.5))
results={}
for a in range(-90,91,5):
 rotated=hook.rotate((0,cy,-22),(0,cy+1,-22),a)
 results[a]=round(rotated.intersect(merged).Volume(),6)
(out/'clearance_check.json').write_text(json.dumps(results,indent=2))
print('Hook overlap volumes mm3 at angles deg:',results)
print('Valid merged single solid; STEP roundtrip passed; original material retained; volume mm3:',merged.Volume())
fig=plt.figure(figsize=(13,9),layout='constrained')
def draw(ax,solid,color):
 verts,faces=solid.tessellate(.12); v=np.array([p.toTuple() for p in verts]); tri=v[np.array(faces)];n=np.cross(tri[:,1]-tri[:,0],tri[:,2]-tri[:,0]);n/=np.maximum(np.linalg.norm(n,axis=1)[:,None],1e-12)
 shade=.40+.60*np.maximum(0,n@np.array([.3,-.4,.866]));ax.add_collection3d(Poly3DCollection(tri,facecolors=shade[:,None]*np.array(color),edgecolors='none'))
for idx,view in enumerate([(25,-60),(-25,-60),(0,-90),(90,-90)]):
 ax=fig.add_subplot(2,2,idx+1,projection='3d');draw(ax,source,[.65,.8,.9]);draw(ax,bracket,[.95,.65,.35]);ax.set(xlim=(-60,60),ylim=(cy-30,cy+30),zlim=(-34,3));ax.set_box_aspect((120,60,37));ax.view_init(*view);ax.set_axis_off();ax.set_title(['Top oblique','Underside oblique','Side: pin along left/right (Y)','Top: three central slots filled'][idx])
fig.suptitle('Battery plate + central double-ear bracket | mm\nBlue: 112 x 54 x 1 plate, three central slots filled; orange: directly attached ears\nX = front/back; Y = left/right pin axis; Z = up; pivot Z = -22; overall H = 33',fontsize=13)
fig.savefig(out/'preview.png',dpi=160);fig.savefig(out/'review_drawing.pdf')
