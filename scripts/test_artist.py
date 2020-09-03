from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

import compas
import compas_rhino

from compas_rhino.utilities import volmesh_from_polysurfaces

from compas_3gs.diagrams import ForceVolMesh
from compas_3gs.rhino import draw_cell_labels

from compas_rhino import unload_modules
unload_modules("compas")


polysurfilter = compas_rhino.rs.filter.polysurface
guids = compas_rhino.rs.GetObjects("select polysurfaces", filter=polysurfilter)
compas_rhino.rs.HideObjects(guids)

forcevolmesh       = ForceVolMesh()
forcevolmesh       = volmesh_from_polysurfaces(forcevolmesh, guids)


# ==============================================================================
# Visualize and Interact
# ==============================================================================

from compas_3gs.rhino import ForceVolMeshArtist
artist = ForceVolMeshArtist(forcevolmesh)
artist.draw()
#
#artist.draw_vertexlabels()
#artist.draw_edgelabels()
#
#artist.draw_faces()
#artist.draw_facelabels()

artist.draw_cells()
artist.draw_celllabels()