from PyQt5.QtCore import QSize,Qt,pyqtSlot,QObject
from time import sleep
from random import shuffle,randint
from Canvas import *

"""
The Solver Object. 

Define the QObject (from Qt Framework) to be run inside a thread.
"""
class Solver(QObject):
    solved = pyqtSignal()
    forced_stop = pyqtSignal()
    message = pyqtSignal(str)
    
    def __init__(self,canvas,parent=None):
        super().__init__()
        self._canvas = canvas
        self.stopped = True
        self.previous_steps = [deepcopy(self._canvas.graph)]
    
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
    Determine the layer, where the line lies.
    
    Parameters
    ----------
    layers: list[Graph]
        The layer set. 
    
    line: Line
        The line to be checked

    Returns
    -------
    layer: Graph
        the layer, where the line lies.
    """ 
    def LineWhichlayer(self,layers,line):
        for layer in layers:
            if (line in layer.getLines()):
                return layer
        return None
    
    """ 
    Subroutine of the actual solution.
    
    More information: Akl. et. al. "On planar path transformation"
    
    
    Parameters
    ----------
    path: Path
        The path
        
    layers: list[Graph]
        The layer set. 
    
    node: Node
        The node to be checked
    """  
    def boundary_alg(self,path: Path,layers,node: Node):
        assert (node in path.getNodes())
        self.stopped = False
        painter = QPainter(self._canvas.pixmap())
        pen = QPen()
        node_in_order = []
        # find which layer the point is in
        layer = self.NodeWhichlayer(layers,node)
        if (not len(layer.getNodes()) in [1,2]):
            node_i_layer = layer.getNodes().index(node)
            neighbor_node = [layer.getNodes()[node_i_layer - 1], 
                             layer.getNodes()[(node_i_layer + 1) % len(layer.getNodes())]]
            neighbor_node = [node0 for node0 in neighbor_node if
                             not Line(node.get_coord(),node0.get_coord()) in path.getLines()]
            print("Scanned node:", str(neighbor_node))
            if (node == path._end):
                node_in_order = list(reversed(path.path_node_order()))
            else:
                node_in_order = path.path_node_order()
            for i in range(2,len(node_in_order)):
                other_node = node_in_order[i]
                if (other_node in neighbor_node):
                    self._canvas.delete_edge(painter,pen,node_in_order[i-1],other_node)
                    print("Disconnected:", str(node_in_order[i-1]),",", str(other_node))
                    self._canvas.draw_edge(painter,pen,node,other_node)
                    print("Connected: ", str(node), ",", str(other_node))
                    if (not (path.is_spanning_path() and not path.crosses())):
                        # Revert change
                        print("Path invalid: Reverting change")
                        self._canvas.delete_edge(painter,pen,node,other_node)
                        self._canvas.draw_edge(painter,pen,node_in_order[i-1],other_node)
                        continue
                    else:
                        break
        elif (len(layer.getNodes()) == 2):
            first = layer.getNodes()[0]
            second = layer.getNodes()[1]
            if (not path.is_connected(first,second)):
                self._canvas.draw_edge(painter,pen,first,second)
                bad_edge = self._canvas.problem_edge()
                if (bad_edge):
                    shuffle(bad_edge)
                    del_edge = bad_edge[0]
                    del_points = self._canvas.graph.whichNodes(del_edge)
                    self._canvas.delete_edge(painter,pen,del_points[0],del_points[1])
                else:
                    self._canvas.delete_edge(painter, pen,first,second)
        self._canvas.update()
        painter.end()
        if (not path == self.previous_steps[-1]):
            self.previous_steps.append(deepcopy(path))
    
    """ 
    Delete an edge, choose a random (missing) edge to add.
    
    Parameters
    ----------
    painter: QPainter
        The painter object
        
    pen: QPen
        The pen object
        
    path: Path
        The path

    line: Line
        the line 
    """ 
    def allocate_edge(self,painter:QPainter, pen:QPen, path: Path,line: Line):
        print("Allocating edges:", line)
        points = path.whichNodes(line)
        self._canvas.delete_edge(painter,pen,points[0],points[1])
        toadd_edge = self._canvas.problem_edge()
        toadd_edge = [line0 for line0 in toadd_edge if line0 != line]
        if (toadd_edge):
            shuffle(toadd_edge)
            readd_edge = toadd_edge[0]
            print("Edge added:", readd_edge)
            readd_points = path.whichNodes(readd_edge)
            self._canvas.draw_edge(painter,pen,readd_points[0],readd_points[1])
        else:
            print("Path invalid: Reverting change")
            self._canvas.draw_edge(painter,pen,points[0],points[1])
    
    """ 
    An alternative version of the "boundary_alg" function above
    to avoid infinite loops
    
    
    Parameters
    ----------
    path: Path
        The path
        
    layers: list[Graph]
        The layer set. 
    
    node: Node
        The node to be checked
    """        
    def boundary_alg_alt(self,path: Path, layers, node: Node):
        assert (node in path.getNodes())
        self.stopped = False
        painter = QPainter(self._canvas.pixmap())
        pen = QPen()
        node_in_order = []
        # find which layer the point is in
        layer = self.NodeWhichlayer(layers,node)
        if (not len(layer.getNodes()) in [1,2]):
            # detect neighboring nodes in this layer
            node_i_layer = layer.getNodes().index(node)
            neighbor_node = [layer.getNodes()[node_i_layer - 1], 
                             layer.getNodes()[(node_i_layer + 1) % len(layer.getNodes())]]
            neighbor_node = [node0 for node0 in neighbor_node if
                             not Line(node.get_coord(),node0.get_coord()) in path.getLines()]
            print("Scanned node:", str(neighbor_node))
            # go through the path in order
            if (node == path._end):
                node_in_order = list(reversed(path.path_node_order()))
            else:
                node_in_order = path.path_node_order()
            for i in range(2,len(node_in_order)):
                other_node = node_in_order[i]
                if (other_node in neighbor_node):
                    self._canvas.draw_edge(painter,pen,node,other_node)
                    print("Connected: ", str(node), ",", str(other_node))
                    # if cross
                    if (not (path.is_spanning_path() and not path.crosses())):
                        bad_edge = self._canvas.problem_edge()
                        bad_edge = [line for line in bad_edge if 
                                    line != Line(node.get_coord(),other_node.get_coord())]
                        if (bad_edge):
                            shuffle(bad_edge)
                            allocated_edge = bad_edge[0]
                            alloc_points = path.whichNodes(allocated_edge)
                            self._canvas.delete_edge(painter,pen,alloc_points[0],alloc_points[1])
                            continue
                        else:
                            self._canvas.delete_edge(painter,pen,node,other_node)
                    else:
                        break
        elif (len(layer.getNodes()) == 2):
            first = layer.getNodes()[0]
            second = layer.getNodes()[1]
            if (not path.is_connected(first,second)):
                self._canvas.draw_edge(painter,pen,first,second)
                bad_edge = self._canvas.problem_edge()
                if (bad_edge):
                    shuffle(bad_edge)
                    del_edge = bad_edge[0]
                    del_points = self._canvas.graph.whichNodes(del_edge)
                    self._canvas.delete_edge(painter,pen,del_points[0],del_points[1])
                else:
                    self._canvas.delete_edge(painter, pen,first,second)
        self._canvas.update()
        painter.end()
        if (not path == self.previous_steps[-1]):
            self.previous_steps.append(deepcopy(path))
    
    """ 
    Delete an layer crossing edge, choose a (missing) edge to add.
    
    The newly added edge is determined by the layer edge vector
    and added to where the layer edge vector value is less than desired.
    
    If multiple possibilities exist, then choose randomly between them.
    
    Parameters
    ----------
        
    path: Path
        The path

    layers: list[Graph]
        The layer set
    
    mode: int
        choose if the choice of new edge is random or not
        (0 if no, 1 if yes)
    """ 
    def allocate_non_layer(self,path: Path,layers,mode=0):
        painter = QPainter(self._canvas.pixmap())
        pen = QPen()
        linelist = [line for line in path.getLines() if self.LineWhichlayer(layers,line) == None]
        if (mode == 1):
            shuffle(linelist)
            line = linelist[0]
        else: 
            arr = self.check_layercross(path, layers)
            diag = arr.diagonal(1)
            filter_arr = diag > 1
            if (np.any(filter_arr)):
                to_be_checked = diag[filter_arr]
                check_element = to_be_checked[0]
                i,j = np.where(arr == check_element)[0][0], np.where(arr == check_element)[1][0]
                possible_line = []
                for line in linelist:
                    nodes = path.whichNodes(line)
                    node_i = layers.index(self.NodeWhichlayer(layers,nodes[0]))
                    node_j = layers.index(self.NodeWhichlayer(layers,nodes[1]))
                    if ((node_i, node_j) in [(i,j),(j,i)]):
                        possible_line.append(line)
                line = possible_line[0]
            else:
                shuffle(linelist)
                line = linelist[0]
        self.allocate_edge(painter,pen,path,line)
        self._canvas.update()
        painter.end()
        if (not path == self.previous_steps[-1]):
            self.previous_steps.append(deepcopy(path))
        
    """ 
    Get the layer edge vector of the path.
    
    Parameters
    ----------
    path: Path
        The path
        
    layers: list[Graph]
    
    Returns
    ----------
    list[int]
        list of integers representing the number of edges on a layer
    """              
    def check_bound(self,path: Path,layers):
        num_path_layers = [0] * len(layers)
        for line in path.getLines():
            if (self.LineWhichlayer(layers,line) != None):
                line_i = layers.index(self.LineWhichlayer(layers,line))
                num_path_layers[line_i] += 1
        return num_path_layers
    
    """ 
    Check if the layer edge vector fulfills the condition of a canonical path.
    
    Parameters
    ----------
    path: Path
        The path
        
    layers: list[Graph]
        The layer set. 
    
    Returns
    ---------
    bool
    """  
    def check_if_bound(self,path: Path,layers):
        num_in_layers = []
        for layer in layers:
            num_in_layers.append(len(layer.getLines()))
        num_path_layers = self.check_bound(path,layers)
        if (len(layers[-1].getNodes()) in [1,2]):
            return all([x-y==1 for x,y in zip(num_in_layers[:-1],num_path_layers[:-1])]
                       + [num_in_layers[-1] == num_path_layers[-1]])
        else:   
            return all([x-y==1 for x,y in zip(num_in_layers,num_path_layers)])
    
    """ 
    Get the layer connectivity matrix of the path.
    
    Parameters
    ----------
    path: Path
        The path
        
    layers: list[Graph]
        The layer set
    
    Returns
    ----------
    numpy.ndarray(int)
        A matrix of integers representing the number of edges 
        that are between two layers
    """
    def check_layercross(self,path: Path,layers):
        n = len(layers)
        arr = np.zeros((n,n),dtype=int)
        linelist = [line for line in path.getLines() if self.LineWhichlayer(layers,line) == None]
        for line in linelist:
            nodes = path.whichNodes(line)
            node_i = layers.index(self.NodeWhichlayer(layers,nodes[0]))
            node_j = layers.index(self.NodeWhichlayer(layers,nodes[1]))
            arr[node_i][node_j] += 1
            arr[node_j][node_i] += 1
        return arr
    
    """ 
    Check if the layer connectivity matrix fulfills the condition of a canonical path.
    
    Parameters
    ----------
    path: Path
        The path
        
    layers: list[Graph]
        The layer set
    
    Returns
    ----------
    bool
    """
    def check_if_layercross(self, path: Path, layers):
        n = len(layers)
        arr = self.check_layercross(path,layers)
        sample_arr = np.eye(n,k=1,dtype=int) + np.eye(n,k=-1,dtype=int)
        return np.all(arr == sample_arr)
    
    """ 
    Check if the path is a canonical path.
    
    Parameters
    ----------
    path: Path
        The path
        
    layers: list[Graph]
        The layer set
    
    Returns
    ----------
    bool
    """
    def valid_canonical(self,path: Path,layers):
        return self.check_if_bound(path, layers) and self.check_if_layercross(path,layers) and (path.is_spanning_path() and not path.crosses())
    
    
    """ 
    Reconfigure the path into a canonical path.
    """
    @pyqtSlot()  
    def solve_to_canonical(self):
        self._canvas.compute_ch()
        if (not self._canvas.layers):
            self.message.emit("Configure the layerS first.")
        else:
            path = self._canvas.graph
            layers = self._canvas.layers
            self.stopped = False
            rand = 3
            steps = 0
            layercross = []
            layercross.append(self.check_layercross(path,layers))
            while (not self.valid_canonical(path,layers)):
                if (self.stopped): break
                steps += 1
                print("\nSolve step:", str(steps))
                candidates = [path.getStart(), path.getEnd()]
                for anchor_node in candidates:
                    if (self.valid_canonical(path,layers)): break
                    if (self.stopped): break
                    if (steps % 5 == 0):
                        try:
                            print("Trying:",str(anchor_node))
                            self.boundary_alg_alt(path,layers,anchor_node)
                        except AssertionError as e:
                            print(e)
                            continue
                    else:
                        try:
                            print("Trying:",str(anchor_node))
                            self.boundary_alg(path,layers,anchor_node)
                        except AssertionError as e:
                            print(e)
                            continue
                if (steps % 5 == rand):
                    if (steps < 50 and steps > 5):
                        self.allocate_non_layer(path,layers)
                        rand = randint(2,3)
                    elif (steps > 50 and steps < 800):
                        self.allocate_non_layer(path,layers,1)   
                        rand = randint(2,3)
                    else:
                        self.allocate_non_layer(path,layers,1)   
                        rand = 1
                if (steps > 1000):
                    self._canvas.message.emit("Forced stop: Too many steps")
                    self.forced_stop.emit()
                    break
                layercross.append(self.check_layercross(path,layers))
            if (self.valid_canonical(path,layers)):
                self._canvas.message.emit("Solved")
                self.solved.emit()
            elif (self.stopped):
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
                self._canvas.message.emit("Forced stop: Cancel")
                self.forced_stop.emit()
            self._canvas.last_graphs = self.previous_steps
            self.stopped = True
    
    """ 
    Run the solution function of Solver object.
    """
    @pyqtSlot()
    def run(self):
        self.solve_to_canonical()
        
    """ 
    Change the status of the function to stop.
    """
    @pyqtSlot()
    def change_stop(self):
        self.stopped = True

""" 
The thread object for Solver
"""   
class SolverThread(QThread):
    stopped = pyqtSignal()
    
    def __init__(self, solver, parent=None):
        super().__init__()
        self._solver = solver
        self._solver.moveToThread(self)
        self.started.connect(self._solver.run)
        self._solver.solved.connect(self.stop)
        self._solver.forced_stop.connect(self.stop)
        self._solver.forced_stop.connect(self.deleteLater)
        self._solver.forced_stop.connect(self._solver.deleteLater)
    
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
        self._solver.change_stop()
        self.requestInterruption()
        self.wait()
        self.stopped.emit()

""" 
The message box object.

Generate a message box when the thread is running
"""
class SolverWaitBox(QMessageBox):
    def __init__(self, solverThread, parent=None):
        super().__init__()
        self._solverThread = solverThread
        self.cancelButton = QPushButton("Cancel")
        self.addButton(self.cancelButton, QMessageBox.RejectRole)
        self.setText("Solving graph, please wait...")
        self.move(100,200)
      
        self.cancelButton.clicked.connect(self.reject)
        self.rejected.connect(self._solverThread.force_stop)
        self._solverThread.stopped.connect(self.accept)
    
    """ 
    Start the Solver thread.
    """    
    def solve(self):
        self._solverThread.start()
        self._solverThread.quit()
        if (self._solverThread._solver._canvas.layers):
            self.show()
            self.exec()
            sleep(1)