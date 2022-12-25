from evennia.contrib.grid.xyzgrid import xymap_legend

# Roads
class Intersection(xymap_legend.MapNode):
    display_symbol = "o"
    prototype = {
            "prototype_parent": "riverport_xyz_room",
            "key": "An intersection",
            "desc": "An intersection of Riverport roads."
        }

class RoadNode(xymap_legend.MapNode):
    display_symbol = "o"
    prototype = {
            "prototype_parent": "riverport_xyz_room",
            "key": "A road",
            "desc": "A road through Riverport."
        }

class GateNode(xymap_legend.MapNode):
    # Note: these nodes will need to be manually connected to the overworld
    display_symbol = "#"
    prototype = {
            "prototype_parent": "riverport_xyz_room",
            "key": "A gate",
            "desc": "A gateway set into the walls of Riverport.",
            "tags": [('area_exit', 'area_def')],
        }

class HouseNode(xymap_legend.MapNode):
    display_symbol = "∆"
    prototype = {
            "prototype_parent": "riverport_xyz_room",
            "key": "Inside",
            "desc": "A building inside Riverport."
        }



class BridgeNode(xymap_legend.MapNode):
    display_symbol = "Ξ"
    prototype = {
            "prototype_parent": "riverport_xyz_room",
            "key": "A bridge",
            "desc": "A bridge over the river."
        }

class BridgeLink(xymap_legend.MapLink):
    symbol = "Ξ"
    display_symbol = "Ξ"
    directions = { 'e': 'w', 'w': 'e' }
    prototype = {
            "prototype_parent": "xyz_exit",
        }



LEGEND = {
    'B': BridgeNode,
    'Ξ': BridgeLink,
    'X': Intersection,
    'R': RoadNode,
    'G': GateNode,
    'H': HouseNode,
}

PROTOTYPES = {
    (13, 8): {
        "prototype_parent": "riverport_xyz_room",
        "key": "A fountain",
        "desc": "A fountain in the center of Riverport.",
    },
}

MAP_STR = """
                       1                   2                   3                   4
 + 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0

17                                                                                
                                                                                   
16                                               G                                 
                                                 |                                  
15                                     H         |                                 
                                       |         |                                  
14         o----------ΞBΞ--------------R---------X-------o                         
           |                                             |                            
13         R-H                                           o---o                     
           |                                                 |                      
12         |                                               H-R                     
           |                                                 |                      
11         |                                                 o---o                
           |                                                     |                 
10         o---o                                                 R-H              
               |                                                 |                 
 9             |   H     H   H                                   |                
               |   |     |   |                                   |                 
 8       G-----X---R-----R---#-----R------ΞBΞ--------------------X-----------G    
               |             |     |                             |                 
 7             |             H     H                             R-H              
               |                                                 |                 
 6             o-----o                                       o---o                
                     |                                       |                    
 5                   o---o                             o-----o                    
                         |                             |                         
 4                     H-R                 H         H-R                          
                         |                 |           |                         
 3                       o----ΞBΞ----X-----R-----X-----o                          
                                     |           |                               
 2                                   |   H   H   |                              
                                     |   |   |   |                               
 1                                   o-ΞΞBΞΞΞBΞΞ-o                              
                                                                                   
 0                                                                                

 + 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0
                       1                   2                   3                   4
"""

XYMAP_DATA = {
    "zcoord": "riverport",
    "map": MAP_STR,
    "legend": LEGEND,
    "prototypes": PROTOTYPES,
}