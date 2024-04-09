from PyQt5.QtCore import QSize,Qt,pyqtSlot,QObject
from time import sleep
from random import shuffle,randint
from math import atan2
from Canvas import *

"""
The Solver Object. 

Define the QObject (from Qt Framework) to be run inside a thread.
"""
class Wrapper(QObject):
    wrapped = pyqtSignal()
    forced_stop = pyqtSignal()
    message = pyqtSignal(str)
    
    def __init__(self,canvas,parent=None):
        super().__init__()
        self._canvas = canvas
        self.stopped = True
    
    """ 
    Determine the layer, where the node lies.
    
    Parameters
    ----------
    layers: list[Graph]
        The layer set. 
    
    node: Node
        The node to be checked

    Returns
    -------
    layer: Graph
        the layer, where the node lies.
    """
    def NodeWhichlayer(self,layers,node):
        for layer in layers:
            if (node in layer.getNodes()):
                return layer
        return None
    
    """ 
    Determine the wrapping path based on the configuration of the canonical path.
    
    Parameters
    ----------
    path: Path
        The path
    
    layers: list[Graph]
        The layer set. 
    
    start: Node
        The start of the path

    Returns
    -------
    list[Node]
        the list of nodes ordered in the way of a wrapping path.
    """
    def get_wrapping(self,path,layers,start):
        nodes_in_order = path.path_node_order()
        assert(start == nodes_in_order[0] or start == nodes_in_order[-1])
        if (start == nodes_in_order[-1]):
            nodes_in_order.reverse()
        assert(layers.index(self.NodeWhichlayer(layers,nodes_in_order[0])) == 0)
        wrapping_path_order = [nodes_in_order[0]]
        other_nodes = nodes_in_order[1:]
        second = next(node for node in other_nodes if layers.index(self.NodeWhichlayer(layers,nodes_in_order[0])) == 0)
        wrapping_path_order.append(second)
        other_nodes = [node for node in other_nodes if node != second]
        while (other_nodes):
            other_nodes.sort(key = lambda node:
                            min(path.angle(wrapping_path_order[-2],wrapping_path_order[-1],node),
                                path.angle(node,wrapping_path_order[-1],wrapping_path_order[-2])),
                            reverse=True)
            x = other_nodes.pop(0)
            wrapping_path_order.append(x)
        print(wrapping_path_order,"\n")
        return wrapping_path_order
    
    """ 
    Connect the edge connecting the two nodes 
    and see if any edge can be deleted.
    
    Parameters
    ----------
    painter: QPainter
        The painter object
        
    pen: QPen
        The pen object
        
    path: Path
        The path
    
    node1: Node
        First node to be checked
        
    node2: Node
        Second node to be checked
    
    Returns
    ---------
    int
        1 if a change is made
        0 otherwise
    """
    def try_edge(self,painter: QPainter, pen: QPen, path: Path,layer,node1: Node,node2: Node):
        print("Trying Edge...")
        print("Connecting:", node1,node2)
        if (not Line(node1.get_coord(),node2.get_coord()) in path.getLines()):
            self._canvas.draw_edge(painter,pen,node1,node2)
            bad_edges = self._canvas.problem_edge()
            bad_edges = [line for line in bad_edges if line != Line(node1.get_coord(),node2.get_coord())]
            comp = lambda line: layer.index(self.NodeWhichlayer(layer,path.whichNodes(line)[0])) + layer.index(self.NodeWhichlayer(layer,path.whichNodes(line)[1]))
            print("Can delete:", bad_edges)
            if (bad_edges):
                bad_edges.sort(key = comp,reverse=True)
                val = comp(bad_edges[0])
                bad_edges = [line for line in bad_edges if comp(line) == val]
                '''
                bad_edges.sort(key = lambda line:
                                1 if node1 in path.whichNodes(line) or node2 in path.whichNodes(line) else 0, reverse = True)
                '''
                shuffle(bad_edges)
                todel_edge = bad_edges[0]
                todel_points = path.whichNodes(todel_edge)
                print("Disconnecting:",todel_points[0],todel_points[1])
                self._canvas.delete_edge(painter,pen,todel_points[0],todel_points[1])
                self._canvas.update()
                return 1
            else:
                print("Reverting change.")
                self._canvas.delete_edge(painter,pen,node1,node2)
                self._canvas.update()
                return 0
        else:
            print("Already connected.")
            return 0
        pass
    
    """ 
    Delete the edge connecting two nodes 
    and see if any edge can be added.
    
    Parameters
    ----------
    painter: QPainter
        The painter object
        
    pen: QPen
        The pen object
        
    path: Path
        The path
    
    node1: Node
        First node to be checked
        
    node2: Node
        Second node to be checked

    Returns
    ---------
    int
        1 if a change is made
        0 otherwise
    """
    def try_del_edge(self,painter:QPainter, pen:QPen, path:Path,layer,node1:Node,node2:Node):
        print("Trying to delete Edge...")
        print("Disconnecting:",node1, node2)
        if (Line(node1.get_coord(),node2.get_coord()) in path.getLines()):
            self._canvas.delete_edge(painter,pen,node1,node2)
            bad_edges = self._canvas.problem_edge()
            bad_edges = [line for line in bad_edges if line != Line(node1.get_coord(),node2.get_coord())]
            comp = lambda line: layer.index(self.NodeWhichlayer(layer,path.whichNodes(line)[0])) + layer.index(self.NodeWhichlayer(layer,path.whichNodes(line)[1]))
            print("Can add:", bad_edges)
            if (bad_edges):
                bad_edges.sort(key = comp,reverse=True)
                val = comp(bad_edges[0])
                bad_edges = [line for line in bad_edges if comp(line) == val]
                '''
                bad_edges.sort(key = lambda line:
                                1 if node1 in path.whichNodes(line) or node2 in path.whichNodes(line) else 0, reverse = True)
                '''
                shuffle(bad_edges)
                toadd_edge = bad_edges[0]
                toadd_points = path.whichNodes(toadd_edge)
                print("Connecting:",toadd_points[0],toadd_points[1])
                self._canvas.draw_edge(painter,pen,toadd_points[0],toadd_points[1])
                self._canvas.update()
                return 1
            else:
                print("Reverting change.")
                self._canvas.draw_edge(painter,pen,node1,node2)
                self._canvas.update()
                return 0
        else:
            print("Already disconnected.")
            return 0
    
    """ 
    Try if all nodes in 'nodelist' can be connected with 'current' node.
    
    If yes, then the edge is added and then it will be checked if any edge
    can be deleted.
    
    Parameters
    ----------
    painter: QPainter
        The painter object
        
    pen: QPen
        The pen object
        
    path: Path
        The path
    
    node1: Node
        First node to be checked
        
    node2: Node
        Second node to be checked

    Returns
    ---------
    int
        1 if a change is made
        0 otherwise
    """
    def try_all(self,painter:QPainter, pen:QPen, path:Path, layer, current:Node, nodelist, ordered=True):
        errcode = 0
        if (not ordered):
            shuffle(nodelist)
        for node in nodelist:
            errcode = self.try_edge(painter,pen,path,layer,current, node)
            if (errcode == 1):
                break
        return errcode
    
    """ 
    Try if all nodes in 'nodelist' can be disconnected with 'current' node.
    
    If yes, then the edge is deleted and then it will be checked if any edge
    can be added.
    
    Parameters
    ----------
    painter: QPainter
        The painter object
        
    pen: QPen
        The pen object
        
    path: Path
        The path
    
    node1: Node
        First node to be checked
        
    node2: Node
        Second node to be checked

    Returns
    ---------
    int
        1 if a change is made
        0 otherwise
    """
    def try_del_all(self,painter:QPainter, pen:QPen, path:Path, layer, current:Node, nodelist, ordered=True):
        errcode = 0
        if (not ordered):
            shuffle(nodelist)
        for node in nodelist:
            errcode = self.try_del_edge(painter,pen,path,layer,current, node)
            if (errcode == 1):
                break
        return errcode
    
    """ 
    Check if the edges adjacent to the node can be deleted.
    
    If yes, then the edge is added and then it will be checked if any edge
    can be deleted.
    
    Parameters
    ----------
    painter: QPainter
        The painter object
        
    pen: QPen
        The pen object
        
    path: Path
        The path
    
    node1: Node
        First node to be checked
        
    node2: Node
        Second node to be checked

    Returns
    ---------
    int
        1 if a change is made
        0 otherwise
    """
    def try_node(self,painter:QPainter, pen:QPen, path:Path,layer, current:Node, node:Node, nodelist, path_start):
        print("Trying node:",node)
        adj_list = path.adj(node)
        shuffle(adj_list)
        for other in adj_list:
            print("Scanning second node:",other)
            print("Disconnected:",node,other)
            self._canvas.delete_edge(painter,pen,node,other)
            bad_edges = self._canvas.problem_edge()
            bad_edges = [line for line in bad_edges if line != Line(node.get_coord(),other.get_coord())]
            '''
            if (path_start != None):
                bad_edges = [line for line in bad_edges if not path_start in path.whichNodes(line)]
            '''
            print("Can add:", bad_edges)
            comp = lambda line: layer.index(self.NodeWhichlayer(layer,path.whichNodes(line)[0])) + layer.index(self.NodeWhichlayer(layer,path.whichNodes(line)[1]))
            if (bad_edges):
                bad_edges.sort(key = comp,reverse=True)
                val = comp(bad_edges[0])
                bad_edges = [line for line in bad_edges if comp(line) == val]
                '''
                bad_edges.sort(key = lambda line:
                                1 if other in path.whichNodes(line) else 0, reverse = True)
                '''
                shuffle(bad_edges)
                toadd_edge = bad_edges[0]
                toadd_points = path.whichNodes(toadd_edge)
                print("Connecting:",toadd_points[0], toadd_points[1])
                self._canvas.draw_edge(painter,pen, toadd_points[0], toadd_points[1])
                self._canvas.update()
                errcode = self.try_all(painter,pen,path,layer,current,nodelist)
                if (errcode == 1):
                    path_nodes = path.path_node_order()
                    if (path.deg(path_start) > 1):
                        start_adj = path.adj(path_start)
                        others = [node for node in start_adj if node != path_nodes[1]]
                        self.try_del_all(painter,pen,path,layer,path_start,others)
                    return 1
            else:
                print("Reverting change.")
                self._canvas.draw_edge(painter,pen,node,other)
                self._canvas.update()
        return 0
    
    """ 
    Partition the ordered nodes in the path as in layer set.
    
    Parameters
    ----------
    path: Path
        The path
        
    layer: list[Graph]
        The 

    Returns
    ---------
    list[list[Node]]
        The node partition
    """
    def node_partition(self,path:Path, layer):
        node_order = path.path_node_order()
        if (layer.index(self.NodeWhichlayer(layer,node_order[0])) != 0):
            node_order.reverse()
        partition = []
        for i in range(len(layer)):
            temp_list = [node for node in node_order if layer.index(self.NodeWhichlayer(layer,node)) == i]
            partition.append(temp_list)
        return partition
    
    """ 
    Initialize a step in reconfiguration of canonical path to 
    a wrapping path.
    
    Parameters
    ----------
    path: Path
        The current path
 
    layer: list[Graph]
        The layer set
    
    old_path_order: list[Node]
        The node order of the current path
        
    new_path_order: list[Node]
        The node order of its corresponding wrapping path
        
    i: int
        Order of the node in the current path
    """
    def wrap_path_step(self,path,layer,old_path_order,new_path_order,i):
        current = new_path_order[i-1]
        to_be_connected = new_path_order[i]
        old_next = old_path_order[i]
        # find all nodes to be checked
        nodes_to_be_checked = old_path_order[i:]
        print("Current:", current)
        print("Next: ", old_next)
        nodes_to_be_checked = [node for node in nodes_to_be_checked 
                                if min(path.angle(old_next,current,to_be_connected),path.angle(to_be_connected,current,old_next))
                                >= min(path.angle(node,current,to_be_connected), path.angle(to_be_connected, current, node))]
        """
        nodes_to_be_checked = [node for node in nodes_to_be_checked if node != old_next]
        nodes_to_be_checked.sort(key = lambda node: layer.index(self.NodeWhichlayer(layer,node)))
        new_nodes = []
        for x in range(len(layer)):
            temp_nodelist = [node for node in nodes_to_be_checked 
                             if layer.index(self.NodeWhichlayer(layer,node)) == x]
            temp_nodelist.sort(key = lambda node:
                                min(path.angle(node, current, to_be_connected),
                                path.angle(to_be_connected, current, node)))
            new_nodes = itertools.chain(new_nodes,temp_nodelist)
        '''  
        nodes_to_be_checked.sort(key = lambda node:
                                min(path.angle(node, current, to_be_connected),
                                    path.angle(to_be_connected, current, node)))
        '''
        """
        nodes_to_be_checked.sort(key = lambda node:
                                min(path.angle(node, current, to_be_connected),
                                    path.angle(to_be_connected, current, node)))
        print("Nodes to be checked:", nodes_to_be_checked)
        painter = QPainter(self._canvas.pixmap())
        pen = QPen()
        start = old_path_order[0]
        for possible in nodes_to_be_checked:
            errcode = self.try_node(painter,pen,path,layer,current, possible,nodes_to_be_checked,start)
            if (errcode == 1):
                break
            else:
                errcode = self.try_all(painter,pen,path,layer,current, nodes_to_be_checked)
                if (errcode != 1):
                    self.try_del_all(painter,pen,path,layer,possible, path.adj(possible))
                else:
                    break
        if (path.deg(start) > 1):
            start_adj = path.adj(start)
            others = [node for node in start_adj if node != old_path_order[1]]
            self.try_del_all(painter,pen,path,layer,start,others)
        self._canvas.update()
        painter.end()
    
    """ 
    An alternative version of 'wrap_path_step'.
    
    Parameters
    ----------
    path: Path
        The current path
 
    layer: list[Graph]
        The layer set
    
    old_path_order: list[Node]
        The node order of the current path
        
    new_path_order: list[Node]
        The node order of its corresponding wrapping path
        
    i: int
        Order of the node in the current path
    """
    def wrap_path_step_alt(self,path,layer,old_path_order,new_path_order,i):
        current = new_path_order[i-1]
        to_be_connected = new_path_order[i]
        old_next = old_path_order[i]
        # find all nodes to be checked
        nodes_to_be_checked = old_path_order[i:]
        print("Current:", current)
        print("Next: ", old_next)
        nodes_to_be_checked = [node for node in nodes_to_be_checked 
                                if min(path.angle(old_next,current,to_be_connected),path.angle(to_be_connected,current,old_next))
                                >= min(path.angle(node,current,to_be_connected), path.angle(to_be_connected, current, node))]
        """
        nodes_to_be_checked = [node for node in nodes_to_be_checked if node != old_next]
        nodes_to_be_checked.sort(key = lambda node: layer.index(self.NodeWhichlayer(layer,node)))
        new_nodes = []
        for x in range(len(layer)):
            temp_nodelist = [node for node in nodes_to_be_checked 
                             if layer.index(self.NodeWhichlayer(layer,node)) == x]
            temp_nodelist.sort(key = lambda node:
                                min(path.angle(node, current, to_be_connected),
                                path.angle(to_be_connected, current, node)))
            new_nodes = itertools.chain(new_nodes,temp_nodelist)
        '''  
        nodes_to_be_checked.sort(key = lambda node:
                                min(path.angle(node, current, to_be_connected),
                                    path.angle(to_be_connected, current, node)))
        '''
        """
        nodes_to_be_checked.sort(key = lambda node:
                                min(path.angle(node, current, to_be_connected),
                                    path.angle(to_be_connected, current, node)))
        print("Nodes to be checked:", nodes_to_be_checked)
        painter = QPainter(self._canvas.pixmap())
        pen = QPen()
        start = old_path_order[0]
        errcode = self.try_all(painter,pen,path,layer,current,nodes_to_be_checked)
        if (errcode != 1):
            for possible in nodes_to_be_checked:
                errcode = self.try_node(painter,pen,path,layer,current, possible,nodes_to_be_checked, start)
                if (errcode == 1):
                    break
                else:
                    errcode = self.try_del_all(painter,pen,path,layer,current, nodes_to_be_checked)
                    if (errcode != 1):
                        self.try_all(painter,pen,path,layer,possible, path.adj(possible))
                    else:
                        break
            if (path.deg(start) > 1):
                start_adj = path.adj(start)
                others = [node for node in start_adj if node != old_path_order[1]]
                self.try_del_all(painter,pen,path,layer,start,others)
        self._canvas.update()
        painter.end()

    """ 
    if the start node is not the same after the step, this function
    attempts to make sure the start node remains the same.
    
    This is not guaranteed to work in more complicated graphs.
    
    Parameters
    ----------
    path: Path
        The current path
 
    layer: list[Graph]
        The layer set
    
    start: Node
        The start of the node
        
    Returns
    ----------
    int
        1 if a change is made
        0 otherwise
    """
    def wrap_path_correction(self,path,layer,start:Node):
        nodelist = path.adj(start)
        painter = QPainter(self._canvas.pixmap())
        pen = QPen()
        self.try_del_all(painter,pen,path,layer,start,nodelist)
        if (path.deg(start) == 1):
            return 1
        else:
            return 0
    
    """ 
    Initialize this step of wrapping, if the node to be corrected is 
    at the end of first layer.
    
    Parameters
    ----------
    path: Path
        The current path
 
    layer: list[Graph]
        The layer set
    """
    def wrap_path_step_first(self,path:Path,layer):
        partition = self.node_partition(path,layer)
        outer_layer = partition[0]
        next_layer = partition[1]
        painter = QPainter(self._canvas.pixmap())
        pen = QPen()
        if (len(next_layer) > 2):
            is_clockwise = lambda A,B,C : (C[1]-A[1])*(B[0]-A[0]) > (B[1]-A[1])*(C[0]-A[0])
            if (is_clockwise(outer_layer[0].get_coord(),outer_layer[1].get_coord(),outer_layer[2].get_coord()) !=
                is_clockwise(outer_layer[-2].get_coord(),outer_layer[-1].get_coord(),next_layer[0].get_coord())):
                self.try_edge(painter,pen,path,layer,outer_layer[-1],next_layer[0])
            if (is_clockwise(outer_layer[0].get_coord(),outer_layer[1].get_coord(),outer_layer[2].get_coord()) !=
                is_clockwise(next_layer[0].get_coord(),next_layer[1].get_coord(),next_layer[2].get_coord())):
                self.try_del_edge(painter,pen,path,layer,outer_layer[-1],outer_layer[-2])
    
    """ 
    Try to delete all edges that is after the node specified
    by the index 'i'
    
    Parameters
    ----------
    path: Path
        The current path
 
    layer: list[Graph]
        The layer set
    
    i: int
        Index of the node
        
    Returns
    ----------
    int
        1 if a change is made
        0 otherwise
    """
    def del_later(self,path: Path,layer, i, old_path_order):
        nodelist = old_path_order[i:]
        painter = QPainter(self._canvas.pixmap())
        pen = QPen()
        for j in range(len(nodelist) - 1):
            self.try_del_edge(painter,pen,path,layer,nodelist[j], nodelist[j+1])  
        
    """ 
    The main heuristic of wrapping a path.
    
    """
    def wrap_path(self):
        path = self._canvas.graph
        layers = self._canvas.layers
        self._canvas.compute_ch()
        if (not layers):
            self.message.emit("Configure the layerS first.")
        else:
            self.stopped = False
            path = self._canvas.graph
            candidates = [path.getStart(), path.getEnd()]
            if (not any([layers.index(self.NodeWhichlayer(layers,node)) == 0 for node in candidates])):
                self.message.emit("Try SOLVE it first.")
            else:
                candidates = [node for node in candidates if layers.index(self.NodeWhichlayer(layers,node)) == 0]
                start = candidates[0]
                old_path = path.path_node_order()
                new_path = self.get_wrapping(path,layers,start)
                if (old_path[0] != new_path[0]):
                    old_path.reverse()
                steps = 0
                while (old_path != new_path):
                    steps += 1
                    if (steps > 100): break
                    print("Wrap step:", steps)
                    if (self.stopped): break
                    i = next(j for j in range(len(old_path)) if old_path[j] != new_path[j])
                    if (layers.index(self.NodeWhichlayer(layers,new_path[i-1])) == 0):
                        print("FIRST STEP:")
                        self.wrap_path_step_first(path,layers)
                    if (steps % 2 == 0):
                        self.wrap_path_step(path,layers,old_path,new_path,i)
                    else:
                        self.wrap_path_step_alt(path,layers,old_path,new_path,i)
                    if (steps % 10 == 0):
                        self.del_later(path,layers,i,old_path)
                    old_path = path.path_node_order()
                    candidates = [path.getStart(), path.getEnd()]
                    try:
                        candidates = [node for node in candidates if layers.index(self.NodeWhichlayer(layers,node)) == 0]
                        start = candidates[0]
                        new_path = self.get_wrapping(path,layers,start)
                        if (old_path[0] != new_path[0]):
                            old_path.reverse()
                    except IndexError:
                        print("PATH INVALID, CORRECTING...")
                        code = self.wrap_path_correction(path,layers,old_path[0])
                        if (code == 1):
                            code = self.wrap_path_correction(path,layers,old_path[1])
                            if (code == 1):
                                '''
                                new_path = self.get_wrapping(path,layers,start)
                                if (old_path[0] != new_path[0]):
                                    old_path.reverse()
                                '''
                                continue
                            else:
                                print("UNABLE TO CORRECT, TERMINATING...")
                                break
                    '''
                    except AssertionError:
                        print("PATH INVALID, CORRECTING...")
                        code = self.wrap_path_correction(path,layers,old_start)
                        if (code == 1):
                            code = self.wrap_path_correction(path,layers,old_second)
                            if (code == 1):
                                continue
                            else:
                                print("UNABLE TO CORRECT, TERMINATING...")
                                break
                        else:
                            print("UNABLE TO CORRECT, TERMINATING...")
                            break
                    '''
                    print("\n")
                if (old_path == new_path):
                    self._canvas.message.emit("Success")
                    self.wrapped.emit()
                elif (self.stopped or old_path != new_path):
                    path = deepcopy(self._canvas.graph)
                    nodes = path.getNodes()
                    path_start =  path.getStart()
                    path_end = path.getEnd()
                    lines = path.getLines()
                    self._canvas.graph = Path(Nodes=nodes,start=path_start,end=path_end,Lines=[])
                    for line in lines:
                        points = self._canvas.graph.whichNodes(line)
                        self._canvas.graph.connect(points[0],points[1])
                    self._canvas.drawGraph()
                    if ((layers.index(self.NodeWhichlayer(layers,old_path[0])) != 0 and 
                        layers.index(self.NodeWhichlayer(layers,old_path[-1])) != 0)):
                        self._canvas.message.emit("Path invalid. Consider SOLVE it again.")
                    else:
                        self._canvas.message.emit("Forced stop: Cancel")
                    self.forced_stop.emit()
            self.stopped = True
            
    """ 
    Run the wrap path function of Wrapper object.
    """
    @pyqtSlot()
    def run(self):
        self.wrap_path()
    
    """ 
    Change the status of the function to stop.
    """  
    @pyqtSlot()
    def change_stop(self):
        self.stopped = True
    
""" 
The thread object for Wrapper
""" 
class WrapperThread(QThread):
    stopped = pyqtSignal()
    
    def __init__(self, wrapper, parent=None):
        super().__init__()
        self._wrapper = wrapper
        self._wrapper.moveToThread(self)
        self.started.connect(self._wrapper.run)
        self._wrapper.wrapped.connect(self.stop)
        self._wrapper.forced_stop.connect(self.stop)
        self._wrapper.forced_stop.connect(self.deleteLater)
        self._wrapper.forced_stop.connect(self._wrapper.deleteLater)
    
    """ 
    Terminate the thread after Solver terminates gracefully.
    """
    @pyqtSlot()
    def stop(self):
        self.requestInterruption()
        self.wait()
        self.stopped.emit()

    """ 
    Force the thread to stop.
    """
    @pyqtSlot() 
    def force_stop(self):
        self._wrapper.change_stop()
        self.requestInterruption()
        self.wait()
        self.stopped.emit()
        
class WrapperWaitBox(QMessageBox):
    def __init__(self,wrapperThread, parent=None):
        super().__init__()
        self._wrapperThread = wrapperThread
        self.cancelButton = QPushButton("Cancel")
        self.addButton(self.cancelButton, QMessageBox.RejectRole)
        self.setText("Wrapping path, please wait...")
        self.move(100,200)
        
        self.cancelButton.clicked.connect(self.reject)
        self.rejected.connect(self._wrapperThread.force_stop)
        self._wrapperThread.stopped.connect(self.accept)
    
    """ 
    Start the Wrapper thread.
    """
    def wrap(self):
        self._wrapperThread.start()
        self._wrapperThread.quit()
        if (self._wrapperThread._wrapper._canvas.layers):
            self.show()
            self.exec()
            sleep(1)