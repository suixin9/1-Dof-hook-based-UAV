from pathlib import Path
import cadquery as cq
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
out=Path(__file__).parent
# mm; Z up, X towards hook opening, hole axis Y.
r=28.5
rod=cq.Workplane('XY').circle(5).extrude(400)
neck=cq.Workplane('XY',origin=(0,0,-76.5)).circle(5).extrude(76.5)
path=cq.Workplane('XZ').moveTo(0,-76.5).threePointArc((28.5,-105),(57,-76.5))
hook=cq.Workplane('XY',origin=(0,0,-76.5)).circle(5).sweep(path)
cap=cq.Workplane('XY').sphere(5).translate((57,0,-76.5))
head=cq.Workplane('XY',origin=(0,0,400)).circle(10).extrude(41.5)
for y in [-17,17]:
 cutter=cq.Workplane('XY').box(40,20,40).translate((0,y,433.5))
 head=head.cut(cutter)
# Rounded top edge is a provisional detail not specified by supplier.
head=head.edges('>Z').fillet(2)
hole=cq.Solid.makeCylinder(5,40,cq.Vector(0,-20,431.5),cq.Vector(0,1,0))
head=head.cut(hole)
part=rod.union(neck).union(hook).union(cap).union(head)
assert part.val().isValid()
assert len(part.solids().vals())==1
cq.exporters.export(part,str(out/'hook_review.step'))
cq.exporters.export(part,str(out/'hook_review.stl'),tolerance=0.05,angularTolerance=0.1)
# Small test coupon, exact same connection geometry, with 15 mm of rod.
coupon=head.union(cq.Workplane('XY',origin=(0,0,385)).circle(5).extrude(15)).translate((0,0,-385))
cq.exporters.export(coupon,str(out/'connector_test.stl'),tolerance=0.05,angularTolerance=0.1)
verts,faces=part.val().tessellate(0.15)
v=np.array([[p.x,p.y,p.z] for p in verts]); f=np.array(faces)
fig=plt.figure(figsize=(12,9))
ax=fig.add_subplot(131,projection='3d'); ax.plot_trisurf(v[:,0],v[:,1],v[:,2],triangles=f,color='silver',linewidth=0,shade=True)
ax.set_box_aspect((72,20,551.5)); ax.view_init(10,-65); ax.set_axis_off(); ax.set_title('3D review (mm)'); ax.set_xlabel('X'); ax.set_ylabel('Y'); ax.set_zlabel('Z')
ax=fig.add_subplot(132); ax.triplot(v[:,0],v[:,2],f,lw=.12,color='gray'); ax.set_aspect('equal'); ax.set_title('Front: hook plane'); ax.set_xlabel('X (mm)'); ax.set_ylabel('Z (mm)'); ax.grid(alpha=.2)
ax=fig.add_subplot(133); ax.triplot(v[:,1],v[:,2],f,lw=.12,color='gray'); ax.set_aspect('equal'); ax.set_title('Side: ear thickness 14'); ax.set_xlabel('Y (mm)'); ax.grid(alpha=.2)
fig.suptitle('REVIEW PROTOTYPE | rod D10 x 400 | hook outer W67 x H110 | total H551.5\nSingle eye: base D20, H41.5, hole D10 at 31.5 above base; no internal thread')
fig.tight_layout(); fig.savefig(out/'preview.png',dpi=160); fig.savefig(out/'review_drawing.pdf')
b=part.val().BoundingBox()
print('valid:',part.val().isValid(),'solids:',len(part.solids().vals()),'bounds mm:',b.xlen,b.ylen,b.zlen,'volume mm3:',part.val().Volume())
