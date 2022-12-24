from evennia.contrib.grid.xyzgrid import xymap_legend

# Roads
class Intersection(xymap_legend.MapNode):
    display_symbol = "#"
    prototype = {
            "prototype_parent": "riverport_xyz_room",
            "key": "An intersection",
            "desc": "An intersection of Riverport roads."
        }

class RoadNode(xymap_legend.MapNode):
    display_symbol = "#"
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
                       1                   2                   3 
 + 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 

12                                                                                 
                                                                                    
11                                 H         G                                 
                                   |         |                                  
10         o------------ΞBΞ--------R---------X-----o                        
           |                                       |                          
 9         R-H                                   H-R                     
           |                                       |                      
 8         o---o   H   H   H                       R-H                
               |   |   |   |                       |                 
 7         G---X---R---R---#---R--ΞBΞ--------------X---G    
               |           |   |                   |                 
 5             o---o       H   H             o-----R-H                  
                   |                         |                         
 4               H-R                     H   R-H                        
                   |                     |   |                         
 3                 o--------ΞBΞ--X---R---X---o                          
                                 |       |                               
 2                               | H   H |                              
                                 | |   | |                               
 1                               oΞBΞΞΞBΞo                              
                                                                                   
 0                                                                                

 + 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5 6 7 8 9 0 
                       1                   2                   3 
"""

XYMAP_DATA = {
    "zcoord": "riverport",
    "map": MAP_STR,
    "legend": LEGEND,
    "prototypes": PROTOTYPES,
}