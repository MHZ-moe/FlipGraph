import numpy as np
import itertools
from collections import Counter

class Node:
    """
    The Node class. 
    
    It represents a vertex in a mathmatical graph.
    
    Parameters
    ----------
    name: str
        Name of the node
    coord: tuple(int, int)
        Coordinate of the node
    adj: list[Node]
        adjacent nodes in a Graph class
    """
    def __init__(self, name, coord, adj = []):
        self._name = name
        self._coord = coord
        
    """
    Getter of coord member.
    
    Returns
    -------
    tuple(int,int)
        coordinate of the node
    """
    def get_coord(self):
        return self._coord
    
    def set_coord(self, x, y):
        self._coord = (x,y)
    
    """
    Getter of coord member.
    
    Returns
    -------
    str
        name of the node
    """
    def get_name(self):
        return self._name
    
    """
    Calculate the distance between a node and another point.
    
    Parameters:
    -----------
    x: int
        coordinate x of the point
    y: int
        coordinate y of the point
    
    Returns
    -------
    float
        distance
    """
    def dist(self,x,y):
        return np.sqrt(pow(x - self._coord[0],2) + pow(y - self._coord[1],2))
    
    """
    Determine if the point (x,y) lies in the node 
    
    Parameters:
    -----------
    x: int
        coordinate x of the point
    y: int
        coordinate y of the point
    
    Returns
    -------
    bool
    """ 
    def is_in(self,x,y):
        return self.dist(x,y) < 7
    
    def __eq__(self,node):
        if (node != None):
            return (self._name == node._name and self._coord == node._coord)
    
    def __repr__(self):
        return self._name + "(" + str(self._coord[0]) + ", " + str(self._coord[1]) + ")"
    
    def __hash__(self):
        return hash((self._name,self._coord))
    
class Line:
    """
    The Line class.
    
    Line represents the edges in a mathematical graph.
    
    Parameters:
    -----------
    point1: tuple[int]
        coordinate of first point
    point2: tuple[int]
        coordinate of second point
    """
    def __init__(self,point1,point2):
        self._point1 = point1
        self._point2 = point2
    
    """
    Get the both end points of the Line.
    
    Returns
    -------
    tuple[tuple[int]]
        tuple of two points
    """
    def getPoints(self):
        return (self._point1, self._point2)
    
    def setPoints(self, point1, point2):
        self._point1 = point1
        self._point2 = point2
    
    """        
    Check if two Lines are equal.
    
    Parameters:
    -----------
    line: Line
        the other Line
    
    Returns
    -------
    bool
        whether two Lines are the same.
    """
    
    def __eq__(self, line):
        return (self._point1 == line._point1 and self._point2 == line._point2) or (self._point1 == line._point2 and self._point2 == line._point1)
    
    """
    Check if two Lines intersect
    
    Parameters:
    -----------
    line: Line
        the other Line
    
    Returns
    -------
    bool 
        whether two Lines intersect
    """
    def intersect(self, line):
        A = self._point1
        B = self._point2
        C = line._point1
        D = line._point2
        if (any([A == C, A == D, B == C, B == D])):
            return False
        else:
            is_clockwise = lambda A,B,C : (C[1]-A[1])*(B[0]-A[0]) > (B[1]-A[1])*(C[0]-A[0])
            return is_clockwise(A,C,D) != is_clockwise(B,C,D) and is_clockwise(A,B,C) != is_clockwise(A,B,D)

    """
    Calculate the distance between the Line and a point
    
    Parameters:
    -----------
    point: tuple[int]
        the coordinate of the point
    
    Returns
    -------
    float
        the shortest distance between the Line and the point
    """
    def dist(self,point):
        x_d = self._point2[0] - self._point1[0]
        y_d = self._point2[1] - self._point1[1]
        num = np.abs(y_d * point[0] - x_d * point[1] + self._point2[0] * self._point1[1] - self._point2[1] * self._point1[0])
        den = np.sqrt(pow(x_d,2)+pow(y_d,2))
        return num / den
    
    """
    Check if the point is close enough to the Line
    
    Parameters:
    -----------
    point: tuple[int]
        the coordinate of the point
        
    Returns
    -------
    bool
        whether the distance is less than 5
    """
    def is_in(self,point):
        return self.dist(point) < 5
    
    def __repr__(self):
        return "{" + str(self._point1) + ", " + str(self._point2) + "}"
    
    def __hash__(self):
        return hash((self._point1,self._point2))
    
class Graph:
    """
    The Graph class.
    
    Simulates a mathematical graph.
    
    Connectivity of nodes are represented in adjacency matrix
    
    Parameters:
    -----------
    Nodes: list[Node]
        list of nodes in a graph
    
    Lines: list[Line]
        list of lines (edges) in a graph
    """
    def __init__(self,Nodes = [],Lines = []):
        self._Nodes = Nodes
        self._Lines = []
        
        self._adj_matrix = np.zeros((len(self._Nodes),len(self._Nodes)),dtype=int)
        for line in Lines:
            nodes = self.whichNodes(line)
            self.connect(nodes[0],nodes[1])
    
    """
    Getter of Node list of a Graph.
    
    Returns
    -------
    list[Node]
        list of nodes in a graph
    """
    def getNodes(self):
        return self._Nodes
    
    """
    Getter of adjacency matrix of a graph.
    
    Returns
    -------
    numpy.ndarray
        adjacency matrix of a graph
    """
    def getAdjMatrix(self):
        return self._adj_matrix
    
        """
    Get the Line list of the Path
    
    Returns
    -------
    list[Line]
        Line list
    """
    def getLines(self):
        return self._Lines
    
    """
    Get all adjacent Nodes of a Node in the Path
    
    Parameters:
    -----------
    node: Node
        the Node
    
    Returns
    -------
    list[Node]
        list of Nodes that are adjacent to "node"
    """
    def adj(self,node: Node):
        assert(node in self._Nodes)
        return [v for v in self._Nodes if self.is_connected(node, v)]
    
    """
    Find the Nodes connected to the Line
    
    Parameters:
    -----------
    line: Line
        the Line to be checked
    
    Returns
    -------
    list[Node]
        list of Nodes that are connected to the Line
    """
    def whichNodes(self,line: Line) -> tuple[Node,Node]:
        vs = [v for v in self.getNodes() if v.get_coord() in line.getPoints()]
        return vs
    
    """
    Add a single Node in the Graph.
    
    Adjacency matrix is expanded along the way.
    
    Parameters:
    -----------
    node: Node
        the Node to be added
    """
    def addNode(self,node: Node):
        if (not node in self._Nodes):
            self._Nodes.append(node)
            self._adj_matrix = np.column_stack((self._adj_matrix,np.zeros(self._adj_matrix.shape[0],dtype=int)))
            self._adj_matrix = np.row_stack((self._adj_matrix,np.zeros(self._adj_matrix.shape[1],dtype=int)))
        
    """
    Remove a Node from a Graph.
    
    Adjacency matrix is changed along the way.
    
    Parameters:
    -----------
    node: Node
        the Node to be added
    """
    def removeNode(self,node: Node):
        assert (node in self._Nodes)
        i = self._Nodes.index(node)
        self._adj_matrix = np.delete(self._adj_matrix,(i),axis=0)
        self._adj_matrix = np.delete(self._adj_matrix,(i),axis=1)
        self._Nodes.remove(node)
        del node
        
    """
    Add a Line to the Line list
    
    Parameters:
    -----------
    line: Line
        the Line
    """
    def addLine(self,line: Line):
        self.getLines().append(line)
        
    """
    delete a Line in the Line list
    
    Parameters:
    -----------
    line: Line
        the Line
    """
    def delLine(self,line: Line):
        assert(line in self.getLines())
        self.getLines().remove(line)
        del line
    
    """
    Check if two Nodes are connected in a Graph.
    
    Parameters:
    -----------
    node1: Node
        first node
    node2: Node
        second node
    
    Returns
    -------
    bool
        whether node1 and node2 are connected
    """
    def is_connected(self,node1: Node,node2: Node) -> bool:
        assert(node1 in self._Nodes and node2 in self._Nodes)
        i = self._Nodes.index(node1)
        j = self._Nodes.index(node2)
        return self._adj_matrix[i][j] == 1
    
    """
    Get the degree of a Node in a Graph, i.e. number of Nodes connected to it
    
    Parameters:
    -----------
    node: Node
        the node
        
    Returns
    -------
    int
        degree of node
    """
    
    def deg(self,node: Node) -> int:
        assert(node in self._Nodes)
        i = self._Nodes.index(node)
        return np.sum(self._adj_matrix[i])
    
    """
    Get the angle of (node1, node2, node3), where node2 is the center
    
    The angle is relative to the polygon formed by the graph and thus is possible to be greater equal 180 degree.
    
    Parameters:
    -----------
    node1: Node
        first node
    node2: Node
        second node
    node3: Node
        third node
        
    Returns
    -------
    float
        the degree value of the angle
    """
    def angle(self,node1: Node,node2: Node,node3: Node) -> float:
        # assume node2 is center
        node1_rel = (node1.get_coord()[0]-node2.get_coord()[0])+(node1.get_coord()[1]-node2.get_coord()[1])*1j
        node3_rel = (node3.get_coord()[0]-node2.get_coord()[0])+(node3.get_coord()[1]-node2.get_coord()[1])*1j
        val3 = np.angle(node3_rel,deg=True)
        val1 = np.angle(node1_rel,deg=True)
        val = val1 - val3
        if (val < 0): val += 360
        return val
    
    """
    Construct a convex hull of the graph.
    
    (Not constructed directly, but the list of Nodes are given in order, such that 
    a convex hull can be constructed by simply connecting each node and its next one)
    
    Algorithm used: Graham Scan
    
    Returns
    -------
    list[node]
        list of Nodes that forms the convex hull
    """
    def compute_ch(self):
        # Graham Scan
        try:
            nodelist = sorted(self._Nodes, key = lambda node: node.get_coord()[1], reverse=True)
            first_node = nodelist.pop(0)
            nodelist = sorted(nodelist, key = lambda node: np.angle((node.get_coord()[0]-first_node.get_coord()[0])+(node.get_coord()[1]-first_node.get_coord()[1])*1j))
            nodelist.insert(0,first_node)
            n = len(nodelist)
            stack = [nodelist[0], nodelist[1], nodelist[2]]
            for i in range(3,n):
                while(self.angle(stack[-2],stack[-1],nodelist[i]) > 180):
                    stack.pop()
                stack.append(nodelist[i])
            return stack
        except:
            pass
    
    """
    Find all the Lines that intersect in the Path
    
    Returns
    -------
    list[Line]
        A Line list, such that each intersects with at least one other in the list
    """
    def crosses(self):
        lines = []
        for l1, l2 in itertools.combinations(self._Lines,2):
            if(l1.intersect(l2)):
                if (l1 not in lines): lines.append(l1)
                if (l2 not in lines): lines.append(l2)
        return lines
            
    """
    Overloaded method of Graph.connect()
    
    Parameters:
    ----------
    node1: Node
        first Node
    node2: Node
        second Node
    """
    def connect(self,node1: Node,node2: Node):
        # assert(node1 in self._Nodes and node2 in self._Nodes)
        i = self._Nodes.index(node1)
        j = self._Nodes.index(node2)
        if (not Line(node1.get_coord(),node2.get_coord()) in self._Lines):
            self.addLine(Line(node1.get_coord(),node2.get_coord()))
        self._adj_matrix[i][j] = 1
        self._adj_matrix[j][i] = 1
    
    """
    Overloaded method of Graph.disconnect()
    
    Parameters:
    ----------
    node1: Node
        first Node
    node2: Node
        second Node
    """
    def disconnect(self,node1: Node,node2: Node):
        assert(node1 in self._Nodes and node2 in self._Nodes)
        i = self._Nodes.index(node1)
        j = self._Nodes.index(node2)
        if (Line(node1.get_coord(),node2.get_coord()) in self._Lines):
            self.delLine(Line(node1.get_coord(),node2.get_coord()))
        self._adj_matrix[i][j] = 0
        self._adj_matrix[j][i] = 0
        
    def __repr__(self):
        return "Nodes: " + str(self._Nodes) + "\nLines: " + str(self._Lines) + "\nAdj. Matrix: \n" + str(self._adj_matrix) + "\n"

    def __eq__(self,graph):
        if (graph != None):
            return Counter(self._Nodes) == Counter(graph._Nodes) and Counter(self._Lines) == Counter(graph._Lines)
            
    def __hash__(self):
        return hash((tuple(self._Nodes),tuple(self._Lines)))
    
class Path(Graph):
    """
    the Path class.
    
    Built upon the Graph class, this class offers additional functionalities
    specified for the thesis, i.e. path detection, cross detection, etc.
    
    Parameters:
    -----------
    Nodes: list[Node]
        Node list
    start: Node
        the starting Node of the Path
    end: Node
        the Node other than "start" of the Path
        (Note: start and end are in most cases interchangeable)
    Lines: list[Line]
        Line list
    """
    def __init__(self,Nodes=[],start = None,end = None, Lines = []):
        super().__init__(Nodes)
        self._start = start
        self._end = end
    
    """
    Get the start Node of the Path
    
    Returns
    -------
    Node
        start Node
    """
    def getStart(self):
        return self._start

    """
    Get the end Node of the Path
    
    Returns
    -------
    Node
        end Node
    """
    def getEnd(self):
        return self._end
        
    """
    Extend the Path from the Node by one vertex and edge.
    Start and ende Nodes are changed along the function call.
    
    Parameters:
    -----------
    node: Node
        the node
    """
    def expandPath(self,node: Node):
        if (len(self.getNodes()) == 0):
            self.addNode(node)
            self._start = node
            self._end = node
        else:
            self.addNode(node)
            self.connect(self._end,node)
            self._end = node
    
    """
    Determine whether the Path graph is a spanning path. 
    i.e. a path that go through all Nodes
    
    Returns
    -------
    bool
        whether the Path is a spanning path
    """
    def is_spanning_path(self):
        endpoints = [v for v in self._Nodes if self.deg(v) == 1]
        innerpoints = [v for v in self._Nodes if self.deg(v) == 2]
        if (len(endpoints) != 2 or len(innerpoints) != len(self._Nodes) - 2): return False
        else:
            self._start = endpoints[0]
            self._end = endpoints[1]
            # run BFS starting from _start
            queue = []
            explored = [self._start]
            queue.append(self._start)
            while (len(queue) > 0):
                v = queue.pop(0)
                for w in self.adj(v):
                    if (not w in explored):
                        explored.append(w)
                        queue.append(w)
            if (len(explored) < len(self._Nodes)): 
                return False
            else: 
                return True
    
    """ 
    Get the list of nodes ordered as in the path.
    
    Returns
    ---------
    list[Node]
        The list of nodes
    """
    def path_node_order(self):
        assert(self.is_spanning_path())
        queue = []
        explored = [self._start]
        queue.append(self._start)
        while (queue):
            v = queue.pop(0)
            for w in self.adj(v):
                if (not w in explored):
                    explored.append(w)
                    queue.append(w)
        return explored
        