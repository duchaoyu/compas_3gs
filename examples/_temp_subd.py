from compas_rhino import unload_modules  
unload_modules("compas")

import compas

from compas_3gs.diagrams import FormNetwork
from compas_3gs.diagrams import ForceVolMesh


from compas_rhino.geometry import RhinoSurface
from compas_3gs.diagrams import Cell 

from compas_3gs.algorithms import volmesh_dual_network
from compas_3gs.algorithms import volmesh_reciprocate


from compas_3gs.rhino import draw_corresponding_elements
from compas_3gs.rhino import draw_network_pipes
from compas_3gs.rhino import draw_compression_tension
from compas_3gs.rhino import draw_network_external_forces
from compas_3gs.rhino import draw_network_internal_forces

from compas_3gs.rhino import Mesh3gsArtist, VolMesh3gsArtist
from compas_3gs.rhino import Network3gsArtist

try:
    import rhinoscriptsyntax as rs
except ImportError:
    compas.raise_if_ironpython()



# select the polysurface which you create in Rhino
guid = rs.GetObject("select a closed polysurface", filter=rs.filter.polysurface)
# turn Rhino polysurface to a COMPAS single polyhedral cell
cell = RhinoSurface.from_guid(guid).brep_to_compas(cls=Cell())
rs.HideObjects(guid)

# draw the polyhedral cell
layer = 'cell' 
cellartist = Mesh3gsArtist(cell, layer=layer)
cellartist.draw()
cellartist.redraw()

from compas_3gs.operations import check_cell_convexity
print(check_cell_convexity(cell))

print(cell)
#================== cell_cut_face_subdiv ==================
def rhino_cell_face_subdivide_barycentric(cell):
    from compas_rhino.selectors import volmesh_select_face
    from compas_3gs.operations import cell_face_subdivide_barycentric
    fkey = volmesh_select_face(cell)
    volmesh = cell_face_subdivide_barycentric(cell, fkey)
    return volmesh

def rhino_cell_subdivide_barycentric(cell, k=2):
    from compas_3gs.operations import cell_subdivide_barycentric
    volmesh = cell_subdivide_barycentric(cell, k=k)
    return volmesh
    
#volmesh = rhino_cell_face_subdivide_barycentric(cell)
forcediagram = rhino_cell_subdivide_barycentric(cell)


cellartist.clear()
forcediagramartist = VolMesh3gsArtist(forcediagram, layer=layer)
forcediagramartist.draw_vertexlabels()
forcediagramartist.draw()
forcediagramartist.redraw()

print(list(forcediagram.vertices()))
print(list(forcediagram.cells()))


#==========================DRAW FORM NETWORK============================
# construct the dual network (form diagram) from volmesh (force diagram)
form_layer = 'form_network'
formdiagram       = volmesh_dual_network(forcediagram, cls=FormNetwork)
formdiagram.layer = form_layer
formdiagram.attributes['name'] = form_layer


# transform dual_network and visualise it
x_move = formdiagram.bounding_box()[0] * 2
for vkey in formdiagram.node:
    formdiagram.node[vkey]['x'] += x_move

formdiagramartist = Network3gsArtist(formdiagram, layer=form_layer)
formdiagramartist.draw_nodes()
formdiagramartist.draw_edges()



# ------------------------------------------------------------------------------
# 3. get reciprocation weight factor
# ------------------------------------------------------------------------------

# input weight factor to control how much the form and force diagrams are chaning
# relatively to each other during the form-finding procedure
weight = rs.GetReal(
    "Enter weight factor : 1  = form only... 0 = force only...", 1.0, 0)


# ------------------------------------------------------------------------------
# 4. reciprocate
# ------------------------------------------------------------------------------

# clear the original force and form diagrams
formdiagramartist.clear()

# conduit
from compas_3gs.rhino import ReciprocationConduit
conduit = ReciprocationConduit(forcediagram, formdiagram)




def callback(forcediagram, formdiagram, k, args):
    print(k)
    if k % 2:
        conduit.redraw()

# reciprocation
with conduit.enabled():
    volmesh_reciprocate(forcediagram,
                        formdiagram,
                        kmax=100,
                        weight=weight,
                        edge_min=50,
                        edge_max=1000,
                        tolerance=0.01,
                        callback=callback,
                        print_result_info=True)

# update / redraw the force and form diagrams
formdiagramartist.draw_nodes()
formdiagramartist.draw_edges()
