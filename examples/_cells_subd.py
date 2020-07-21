from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import compas

from compas_rhino import unload_modules
unload_modules("compas")

from compas_rhino.geometry import RhinoSurface

from compas_3gs.diagrams import FormNetwork, ForceVolMesh
from compas_3gs.algorithms import volmesh_dual_network, volmesh_reciprocate
from compas_3gs.rhino import ReciprocationConduit
from compas_3gs.rhino import VolMesh3gsArtist, Network3gsArtist

try:
    import rhinoscriptsyntax as rs
except ImportError:
    compas.raise_if_ironpython()

# ------------------------------------------------------------------------------
# 1. make vomesh from rhino polysurfaces
# ------------------------------------------------------------------------------
# select Rhino polysurfaces
guids = rs.GetObjects("select polysurfaces", filter=rs.filter.polysurface)
rs.HideObjects(guids)

from compas_rhino.geometry._constructors import volmesh_from_polysurfaces
from compas.datastructures import VolMesh
forcediagram = volmesh_from_polysurfaces(ForceVolMesh, guids)

force_layer = 'force_volmesh'
forcediagram.layer = force_layer
forcediagram.attributes['name'] = force_layer

from compas_3gs.operations import volmesh_cell_subdivide_barycentric

from compas_rhino.selectors import volmesh_select_face
volmesh_cell_subdivide_barycentric(forcediagram, 0)

# visualise the force_volmesh
forcediagramartist = VolMesh3gsArtist(forcediagram, layer=force_layer)
forcediagramartist.draw()


#==========================DRAW FORM NETWORK============================
# construct the dual network (form diagram) from volmesh (force diagram)
form_layer = 'form_network'
formdiagram       = volmesh_dual_network(forcediagram, cls=FormNetwork)
formdiagram.layer = form_layer
formdiagram.attributes['name'] = form_layer

print(formdiagram)

# transform dual_network and visualise it
x_move = formdiagram.bounding_box()[0] * 2
for vkey in formdiagram.node:
    formdiagram.node[vkey]['x'] += x_move

formdiagramartist = Network3gsArtist(formdiagram, layer=form_layer)
formdiagramartist.draw_nodes()
formdiagramartist.draw_edges()
