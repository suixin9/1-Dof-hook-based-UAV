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
bracket=cq.importers.importStep(str(out/'inputs'/'32cb_flat.step')).val()
bracket=bracket.rotate((0,0,0),(0,0,1),90).rotate((0,0,0),(1,0,0),180).translate((0,cy,0))
merged=source.fuse(bracket).clean()
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
 ax=fig.add_subplot(2,2,idx+1,projection='3d');draw(ax,source,[.65,.8,.9]);draw(ax,bracket,[.95,.65,.35]);ax.set(xlim=(-60,60),ylim=(cy-30,cy+30),zlim=(-34,3));ax.set_box_aspect((120,60,37));ax.view_init(*view);ax.set_axis_off();ax.set_title(['Top oblique','Underside oblique','Side: pin along left/right (Y)','Top: local slots covered'][idx])
fig.suptitle('Battery plate + central double-ear bracket | mm\nBlue: original 112 x 54 x 1 plate; orange: 44 x 44 x 4 reinforcement and ears\nX = front/back; Y = left/right pin axis; Z = up; pivot Z = -22; overall H = 33',fontsize=13)
fig.savefig(out/'preview.png',dpi=160);fig.savefig(out/'review_drawing.pdf')
