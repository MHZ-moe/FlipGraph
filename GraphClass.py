import numpy as np
import itertools
from collections import Counter
import json


class Node:

    def __init__(self, name, coord, adj=[]):
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
        self._name = name
        self._coord = coord

    def get_coord(self):
        """
        Getter of coord member.

        Returns
        -------
        tuple(int,int)
            coordinate of the node
        """
        return self._coord

    def set_coord(self, x, y):
        """
        Setter of coord member.

        Parameters
        ----------
        x: int
            x-coordinate
        y: int
            y-coordinate
        """
        self._coord = (x, y)

    def get_name(self):
        """
        Getter of coord member.

        Returns
        -------
        str
            name of the node
        """
        return self._name

    def dist(self, x, y):
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
        return np.sqrt(pow(x - self._coord[0], 2) + pow(y - self._coord[1], 2))

    def is_in(self, x, y):
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
        return self.dist(x, y) < 7

    def __eq__(self, node):
        if (node is not None):
            return (self._name == node._name and self._coord == node._coord)

    def __repr__(self):
        return self._name + \
            "(" + str(self._coord[0]) + ", " + str(self._coord[1]) + ")"

    def __hash__(self):
        return hash((self._name, self._coord))

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__)


class Line:

    def __init__(self, point1, point2):
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
        self._point1 = point1
        self._point2 = point2

    def getPoints(self):
        """
        Get the both end points of the Line.

        Returns
        -------
        tuple[tuple[int]]
            tuple of two points
        """
        return (self._point1, self._point2)

    def setPoints(self, point1, point2):
        """
        Set the both end points of the Line.

        Parameters:
        -----------
        point1: tuple[int]
            coordinate of first point
        point2: tuple[int]
            coordinate of second point
        """
        self._point1 = point1
        self._point2 = point2

    def __eq__(self, line):
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
        return (self._point1 == line._point1 and self._point2 == line._point2) or (
            self._point1 == line._point2 and self._point2 == line._point1)

    def intersect(self, line):
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
        A = self._point1
        B = self._point2
        C = line._point1
        D = line._point2
        if (any([A == C, A == D, B == C, B == D])):
            return False
        else:
            def is_clockwise(A, B, C): return (
                C[1] - A[1]) * (B[0] - A[0]) > (B[1] - A[1]) * (C[0] - A[0])
            return is_clockwise(
                A,
                C,
                D) != is_clockwise(
                B,
                C,
                D) and is_clockwise(
                A,
                B,
                C) != is_clockwise(
                A,
                B,
                D)

    def dist(self, point):
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
        x_d = self._point2[0] - self._point1[0]
        y_d = self._point2[1] - self._point1[1]
        num = np.abs(
            y_d *
            point[0] -
            x_d *
            point[1] +
            self._point2[0] *
            self._point1[1] -
            self._point2[1] *
            self._point1[0])
        den = np.sqrt(pow(x_d, 2) + pow(y_d, 2))
        return num / den

    def is_in(self, point):
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
        return self.dist(point) < 5

    def __repr__(self):
        return "{" + str(self._point1) + ", " + str(self._point2) + "}"

    def __hash__(self):
        return hash((self._point1, self._point2))

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__)


class Graph:

    def __init__(self, Nodes=[], Lines=[]):
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
        self._Nodes = Nodes
        self._Lines = []

        self._adj_matrix = np.zeros(
            (len(self._Nodes), len(self._Nodes)), dtype=int)
        for line in Lines:
            nodes = self.whichNodes(line)
            self.connect(nodes[0], nodes[1])

    def getNodes(self):
        """
        Getter of Node list of a Graph.

        Returns
        -------
        list[Node]
            list of nodes in a graph
        """
        return self._Nodes

    def getAdjMatrix(self):
        """
        Getter of adjacency matrix of a graph.

        Returns
        -------
        numpy.ndarray
            adjacency matrix of a graph
        """
        return self._adj_matrix

    def getLines(self):
        """
        Get the Line list of the Path

        Returns
        -------
        list[Line]
            Line list
        """
        return self._Lines

    def adj(self, node: Node):
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
        assert (node in self._Nodes)
        return [v for v in self._Nodes if self.is_connected(node, v)]

    def whichNodes(self, line: Line) -> tuple[Node, Node]:
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
        vs = [v for v in self.getNodes() if v.get_coord() in line.getPoints()]
        return vs

    def addNode(self, node: Node):
        """
        Add a single Node in the Graph.

        Adjacency matrix is expanded along the way.

        Parameters:
        -----------
        node: Node
            the Node to be added
        """
        if (node not in self._Nodes):
            self._Nodes.append(node)
            self._adj_matrix = np.column_stack(
                (self._adj_matrix, np.zeros(
                    self._adj_matrix.shape[0], dtype=int)))
            self._adj_matrix = np.row_stack(
                (self._adj_matrix, np.zeros(
                    self._adj_matrix.shape[1], dtype=int)))

    def removeNode(self, node: Node):
        """
        Remove a Node from a Graph.

        Adjacency matrix is changed along the way.

        Parameters:
        -----------
        node: Node
            the Node to be added
        """
        assert (node in self._Nodes)
        i = self._Nodes.index(node)
        self._adj_matrix = np.delete(self._adj_matrix, (i), axis=0)
        self._adj_matrix = np.delete(self._adj_matrix, (i), axis=1)
        self._Nodes.remove(node)
        del node

    def addLine(self, line: Line):
        """
        Add a Line to the Line list

        Parameters:
        -----------
        line: Line
            the Line
        """
        self.getLines().append(line)

    def delLine(self, line: Line):
        """
        delete a Line in the Line list

        Parameters:
        -----------
        line: Line
            the Line
        """
        assert (line in self.getLines())
        self.getLines().remove(line)
        del line

    def is_connected(self, node1: Node, node2: Node) -> bool:
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
        assert (node1 in self._Nodes and node2 in self._Nodes)
        i = self._Nodes.index(node1)
        j = self._Nodes.index(node2)
        return self._adj_matrix[i][j] == 1

    def deg(self, node: Node) -> int:
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
        assert (node in self._Nodes)
        i = self._Nodes.index(node)
        return np.sum(self._adj_matrix[i])

    def angle(self, node1: Node, node2: Node, node3: Node) -> float:
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
        # assume node2 is center
        node1_rel = (node1.get_coord()[
                     0] - node2.get_coord()[0]) + (node1.get_coord()[1] - node2.get_coord()[1]) * 1j
        node3_rel = (node3.get_coord()[
                     0] - node2.get_coord()[0]) + (node3.get_coord()[1] - node2.get_coord()[1]) * 1j
        val3 = np.angle(node3_rel, deg=True)
        val1 = np.angle(node1_rel, deg=True)
        val = val1 - val3
        if (val < 0):
            val += 360
        return val

    def compute_ch(self):
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
        # Graham Scan
        try:
            nodelist = sorted(
                self._Nodes,
                key=lambda node: node.get_coord()[1],
                reverse=True)
            first_node = nodelist.pop(0)
            nodelist = sorted(
                nodelist, key=lambda node: np.angle(
                    (node.get_coord()[0] - first_node.get_coord()[0]) + (
                        node.get_coord()[1] - first_node.get_coord()[1]) * 1j))
            nodelist.insert(0, first_node)
            n = len(nodelist)
            stack = [nodelist[0], nodelist[1], nodelist[2]]
            for i in range(3, n):
                while (self.angle(stack[-2], stack[-1], nodelist[i]) > 180):
                    stack.pop()
                stack.append(nodelist[i])
            return stack
        except BaseException:
            pass

    def crosses(self):
        """
        Find all the Lines that intersect in the Path

        Returns
        -------
        list[Line]
            A Line list, such that each intersects with at least one other in the list
        """
        lines = []
        for l1, l2 in itertools.combinations(self._Lines, 2):
            if (l1.intersect(l2)):
                if (l1 not in lines):
                    lines.append(l1)
                if (l2 not in lines):
                    lines.append(l2)
        return lines

    def connect(self, node1: Node, node2: Node):
        """
        Overloaded method of Graph.connect()

        Parameters:
        ----------
        node1: Node
            first Node
        node2: Node
            second Node
        """
        # assert(node1 in self._Nodes and node2 in self._Nodes)
        i = self._Nodes.index(node1)
        j = self._Nodes.index(node2)
        if (not Line(node1.get_coord(), node2.get_coord()) in self._Lines):
            self.addLine(Line(node1.get_coord(), node2.get_coord()))
        self._adj_matrix[i][j] = 1
        self._adj_matrix[j][i] = 1

    def disconnect(self, node1: Node, node2: Node):
        """
        Overloaded method of Graph.disconnect()

        Parameters:
        ----------
        node1: Node
            first Node
        node2: Node
            second Node
        """
        assert (node1 in self._Nodes and node2 in self._Nodes)
        i = self._Nodes.index(node1)
        j = self._Nodes.index(node2)
        if (Line(node1.get_coord(), node2.get_coord()) in self._Lines):
            self.delLine(Line(node1.get_coord(), node2.get_coord()))
        self._adj_matrix[i][j] = 0
        self._adj_matrix[j][i] = 0

    def __repr__(self):
        return "Nodes: " + str(self._Nodes) + "\nLines: " + str(self._Lines) + \
            "\nAdj. Matrix: \n" + str(self._adj_matrix) + "\n"

    def __eq__(self, graph):
        if (graph is not None):
            return Counter(
                self._Nodes) == Counter(
                graph._Nodes) and Counter(
                self._Lines) == Counter(
                graph._Lines)

    def __hash__(self):
        return hash((tuple(self._Nodes), tuple(self._Lines)))

    def toJson(self):
        return json.dumps(self, default=lambda o: o.__dict__)


class Path(Graph):

    def __init__(self, Nodes=[], start=None, end=None, Lines=[]):
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
        super().__init__(Nodes)
        self._start = start
        self._end = end

    def getStart(self):
        """
        Get the start Node of the Path

        Returns
        -------
        Node
            start Node
        """
        return self._start

    def getEnd(self):
        """
        Get the end Node of the Path

        Returns
        -------
        Node
            end Node
        """
        return self._end

    def expandPath(self, node: Node):
        """
        Extend the Path from the Node by one vertex and edge.
        Start and ende Nodes are changed along the function call.

        Parameters:
        -----------
        node: Node
            the node
        """
        if (len(self.getNodes()) == 0):
            self.addNode(node)
            self._start = node
            self._end = node
        else:
            self.addNode(node)
            self.connect(self._end, node)
            self._end = node

    def is_spanning_path(self):
        """
        Determine whether the Path graph is a spanning path.
        i.e. a path that go through all Nodes

        Returns
        -------
        bool
            whether the Path is a spanning path
        """
        endpoints = [v for v in self._Nodes if self.deg(v) == 1]
        innerpoints = [v for v in self._Nodes if self.deg(v) == 2]
        if (len(endpoints) != 2 or len(innerpoints) != len(self._Nodes) - 2):
            return False
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
                    if (w not in explored):
                        explored.append(w)
                        queue.append(w)
            if (len(explored) < len(self._Nodes)):
                return False
            else:
                return True

    def path_node_order(self):
        """
        Get the list of nodes ordered as in the path.

        Returns
        ---------
        list[Node]
            The list of nodes
        """
        assert (self.is_spanning_path())
        queue = []
        explored = [self._start]
        queue.append(self._start)
        while (queue):
            v = queue.pop(0)
            for w in self.adj(v):
                if (w not in explored):
                    explored.append(w)
                    queue.append(w)
        return explored
