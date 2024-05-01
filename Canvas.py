from enum import IntEnum
from copy import deepcopy
import itertools

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtCore import QPoint
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter
from PyQt5.QtGui import QPen
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QLabel

from GraphClass import Graph
from GraphClass import Line
from GraphClass import Node
from GraphClass import Path
from base64 import b64decode, b64encode


class MainMode(IntEnum):
    """
    MainMode Enum class.

    Major drawing mode of the program
    """
    EDIT_MODE = 0
    FLIP_MODE = 1


class SubMode(IntEnum):
    """
    SubMode Enum class.

    Drawing mode of the program
    """
    START = 0
    DRAW_NODE = 1
    DRAW_EDGE = 2
    DEL_NODE = 3
    DEL_EDGE = 4


class Canvas(QLabel):
    message = pyqtSignal(str)
    main_mode_change = pyqtSignal()
    sub_mode_change = pyqtSignal(SubMode)

    def __init__(self, width, height):
        """
        the Canvas class.

        Built upon the QLabel class from the PyQt5 framework.
        This class offers the baseline for drawing graphs.

        Parameters
        ----------
        width: int
            width of the window
        height: int
            height of the window
        """
        super(QLabel, self).__init__()

        self.width_ = width
        self.height_ = height

        self.setAlignment(Qt.AlignCenter)
        whiteboard = QPixmap(self.width_, self.height_)
        whiteboard.fill(Qt.white)
        self.setPixmap(whiteboard)

        self.x_ = 0
        self.y_ = 0

        self.main_mode_ = MainMode.EDIT_MODE
        self.sub_mode_ = SubMode.DRAW_NODE

        self.i_ = 0
        self.first_point = None
        self.second_point = None
        self.third_point = None
        self.showing_layer = False

        self.last_graphs = []
        self.next_graphs = []

        self.last_main_mode = []
        self.next_main_mode = []

        self.last_sub_mode = []
        self.next_sub_mode = []

        self.graph = Path(Nodes=[])
        self.layers = []

        self.bad_node = []
        self.bad_edge = []
        self.edge_diff = 0

    def inc(self):
        """
        Increment i_ by 1
        """
        self.i_ = max([int(node._name) for node in self.graph.getNodes()]) + 1

    def get_xy(self):
        """
        Get x_ and y_

        Returns
        -------
        tuple[int]
            tuple of x_ and y_
        """
        return (self.x_, self.y_)

    def coord_update(self, x, y):
        """
        Update/Set values of x_ and y_

        Parameters:
        -----------
        x: int
            x coordinate
        y: int
            y coordinate
        """
        self.x_ = x
        self.y_ = y

    def setSubMode(self, mode=None):
        """
        Set the SubMode of the Canvas

        Parameters:
        -----------
        mode: SubMode
            the mode to be set
        """
        if (mode is not None):
            self.sub_mode_ = mode

    def setMainMode(self, mode=None):
        """
        Set the MainMode of the Canvas

        Parameters:
        -----------
        mode: MainMode
            the mode to be set
        """
        if (mode is not None):
            self.main_mode_ = mode
            self.first_point = None
            self.second_point = None
            self.third_point = None

    def getMode(self):
        """
        Get the mode of the Canvas

        Returns
        -------
        Mode
            the mode
        """
        return (self.main_mode_, self.sub_mode_)

    def draw_node(self, pen, painter, point):
        """
        Draw a Node (a small circle) on the screen

        Parameters:
        -----------
        pen: QPen
            the QPen class
        painter: QPainter
            the QPainter class
        point: tuple[int]
            the coordinate where the circle is drawn
        """
        if (self.main_mode_ == MainMode.EDIT_MODE):
            self.last_graphs.append(deepcopy(self.graph))
            self.last_main_mode.append(self.main_mode_)
            self.last_sub_mode.append(self.sub_mode_)
            self.next_graphs.clear()
            self.layers.clear()
            pen.setColor(Qt.black)
            painter.setPen(pen)
            painter.drawEllipse(QPoint(point[0], point[1]), 7, 7)
            node = Node(str(self.i_), (point[0], point[1]))
            if (len(self.graph.getNodes()) > 0):
                last_end = self.graph.getEnd()
                self.graph.expandPath(node)
                end = self.graph.getEnd()
                painter.drawLine(
                    last_end.get_coord()[0],
                    last_end.get_coord()[1],
                    end.get_coord()[0],
                    end.get_coord()[1])
            else:
                self.graph.expandPath(node)
            self.inc()
            self.message.emit("Added: " + str(node))
        else:
            if (not self.graph.crosses() and self.graph.is_spanning_path()):
                self.last_graphs.append(deepcopy(self.graph))
                self.last_main_mode.append(self.main_mode_)
                self.last_sub_mode.append(self.sub_mode_)
                self.next_graphs.clear()
                self.layers.clear()
                pen.setColor(Qt.black)
                painter.setPen(pen)
                painter.drawEllipse(QPoint(point[0], point[1]), 7, 7)
                node = Node(str(self.i_), (point[0], point[1]))
                if (len(self.graph.getNodes()) > 0):
                    last_end = self.graph.getEnd()
                    self.graph.expandPath(node)
                    end = self.graph.getEnd()
                    painter.drawLine(
                        last_end.get_coord()[0],
                        last_end.get_coord()[1],
                        end.get_coord()[0],
                        end.get_coord()[1])
                else:
                    self.graph.expandPath(node)
                self.inc()
                self.message.emit("Added: " + str(node))
            else:
                self.message.emit("Not yet. The path is not valid.")
        self.edge_diff = len(self.graph._Lines) + 1 - len(self.graph._Nodes)

    def draw_edge(
            self,
            painter: QPainter,
            pen: QPen,
            node1: Node,
            node2: Node):
        """
        Draw an edge (a line) between two Nodes

        Parameters:
        -----------
        pen: QPen
            the QPen class
        painter: QPainter
            the QPainter class
        node1: Node
            first Node
        node2: Node
            second Node
        """
        if (self.main_mode_ == MainMode.EDIT_MODE):
            self.last_graphs.append(deepcopy(self.graph))
            self.last_main_mode.append(self.main_mode_)
            self.last_sub_mode.append(self.sub_mode_)
            self.next_graphs.clear()
            pen.setColor(Qt.black)
            pen.setWidth(1)
            painter.setPen(pen)
            if (not self.graph.is_connected(node1, node2)):
                self.graph.connect(node1, node2)
            painter.drawLine(
                node1.get_coord()[0],
                node1.get_coord()[1],
                node2.get_coord()[0],
                node2.get_coord()[1])
            self.edge_diff = len(self.graph._Lines) + \
                1 - len(self.graph._Nodes)
            self.message.emit(
                "Connected: {" + str(node1) + ", " + str(node2) + "}")
        else:
            if (self.edge_diff < 1):
                self.last_graphs.append(deepcopy(self.graph))
                self.last_main_mode.append(self.main_mode_)
                self.last_sub_mode.append(self.sub_mode_)
                self.next_graphs.clear()
                pen.setColor(Qt.black)
                painter.setPen(pen)
                if (not self.graph.is_connected(node1, node2)):
                    self.graph.connect(node1, node2)
                painter.drawLine(
                    node1.get_coord()[0],
                    node1.get_coord()[1],
                    node2.get_coord()[0],
                    node2.get_coord()[1])
                self.edge_diff = len(self.graph._Lines) + \
                    1 - len(self.graph._Nodes)
                self.message.emit(
                    "Connected: {" + str(node1) + ", " + str(node2) + "}")
            else:
                self.message.emit("Too many edges.")

    def delete_edge(
            self,
            painter: QPainter,
            pen: QPen,
            node1: Node,
            node2: Node) -> None:
        """
        Delete an edge between two Nodes

        Parameters:
        -----------
        pen: QPen
            the QPen class
        painter: QPainter
            the QPainter class
        node1: Node
            first Node
        node2: Node
            second Node
        """
        if (self.main_mode_ == MainMode.EDIT_MODE):
            self.last_graphs.append(deepcopy(self.graph))
            self.last_main_mode.append(self.main_mode_)
            self.last_sub_mode.append(self.sub_mode_)
            self.next_graphs.clear()
            pen.setColor(Qt.white)
            painter.setPen(pen)
            if (self.graph.is_connected(node1, node2)):
                self.graph.disconnect(node1, node2)
            painter.drawLine(
                node1.get_coord()[0],
                node1.get_coord()[1],
                node2.get_coord()[0],
                node2.get_coord()[1])
            pen.setColor(Qt.black)
            painter.setPen(pen)
            painter.drawEllipse(
                QPoint(
                    node1.get_coord()[0],
                    node1.get_coord()[1]),
                7,
                7)
            painter.drawEllipse(
                QPoint(
                    node2.get_coord()[0],
                    node2.get_coord()[1]),
                7,
                7)
            self.edge_diff = len(self.graph._Lines) + \
                1 - len(self.graph._Nodes)
            self.message.emit(
                "Disconnected: {" + str(node1) + ", " + str(node2) + "}")
        else:
            if (self.edge_diff > -1):
                self.last_graphs.append(deepcopy(self.graph))
                self.last_main_mode.append(self.main_mode_)
                self.last_sub_mode.append(self.sub_mode_)
                self.next_graphs.clear()
                pen.setColor(Qt.white)
                painter.setPen(pen)
                if (self.graph.is_connected(node1, node2)):
                    self.graph.disconnect(node1, node2)
                painter.drawLine(
                    node1.get_coord()[0],
                    node1.get_coord()[1],
                    node2.get_coord()[0],
                    node2.get_coord()[1])
                pen.setColor(Qt.black)
                painter.setPen(pen)
                painter.drawEllipse(
                    QPoint(
                        node1.get_coord()[0],
                        node1.get_coord()[1]),
                    7,
                    7)
                painter.drawEllipse(
                    QPoint(
                        node2.get_coord()[0],
                        node2.get_coord()[1]),
                    7,
                    7)
                self.edge_diff = len(self.graph._Lines) + \
                    1 - len(self.graph._Nodes)
                self.message.emit(
                    "Disconnected: {" + str(node1) + ", " + str(node2) + "}")
            else:
                self.message.emit("Too few edges.")

    def delete_node(self, painter: QPainter, pen: QPen, node: Node):
        """
        Delete a Node and all its coincident edges on the screen

        Parameters:
        -----------
        pen: QPen
            the QPen class
        painter: QPainter
            the QPainter class
        point: tuple[int]
            the coordinate where the circle is drawn
        """
        if (self.main_mode_ == MainMode.EDIT_MODE):
            assert (node in self.graph.getNodes())
            self.last_graphs.append(deepcopy(self.graph))
            self.last_main_mode.append(self.main_mode_)
            self.last_sub_mode.append(self.sub_mode_)
            self.next_graphs.clear()
            self.layers.clear()
            pen.setColor(Qt.white)
            painter.setPen(pen)
            nodelist = self.graph.getNodes()
            i = nodelist.index(node)
            n = len(nodelist)
            adj = [nodelist[j]
                   for j in range(n) if self.graph.getAdjMatrix()[i][j] == 1]
            for point in adj:
                painter.drawLine(
                    node.get_coord()[0],
                    node.get_coord()[1],
                    point.get_coord()[0],
                    point.get_coord()[1])
                pen.setColor(Qt.black)
                painter.setPen(pen)
                painter.drawEllipse(
                    QPoint(
                        node.get_coord()[0],
                        node.get_coord()[1]),
                    7,
                    7)
                painter.drawEllipse(
                    QPoint(
                        point.get_coord()[0],
                        point.get_coord()[1]),
                    7,
                    7)
                self.graph.disconnect(node, point)
                pen.setColor(Qt.white)
                painter.setPen(pen)
            painter.drawEllipse(
                QPoint(
                    node.get_coord()[0],
                    node.get_coord()[1]),
                7,
                7)
            self.graph.removeNode(node)
            self.edge_diff = len(self.graph._Lines) + \
                1 - len(self.graph._Nodes)
            self.message.emit("Deleted: " + str(node))
        else:
            self.message.emit("This is only available in EDIT mode.")

    def flip(self, painter: QPainter):
        """
        Perform a flip on a graph,
        i.e. deleting an edge and adding a new one
        (Deprecated)

        Parameters:
        -----------
        painter: QPainter
            the QPainter class
        """
        self.last_graphs.append(deepcopy(self.graph))
        self.last_main_mode.append(self.main_mode_)
        self.last_sub_mode.append(self.sub_mode_)
        self.next_graphs.clear()
        pen = QPen()
        nodelist = self.graph.getNodes()
        nodelist = [v for v in nodelist if v.is_in(self.x_, self.y_)]
        if (len(nodelist) == 0):
            pass
        else:
            if (self.first_point is None):
                self.first_point = nodelist[0]
                pen.setColor(Qt.blue)
                painter.setPen(pen)
                painter.drawEllipse(
                    QPoint(
                        self.first_point.get_coord()[0],
                        self.first_point.get_coord()[1]),
                    7,
                    7)
            else:
                if (self.second_point is None):
                    self.second_point = nodelist[0]
                    if (not self.graph.is_connected(
                            self.first_point, self.second_point)):
                        self.second_point = None
                    else:
                        pen.setColor(Qt.red)
                        painter.setPen(pen)
                        painter.drawEllipse(
                            QPoint(
                                self.second_point.get_coord()[0],
                                self.second_point.get_coord()[1]),
                            7,
                            7)
                else:
                    self.third_point = nodelist[0]
                    if (self.first_point != self.second_point and self.first_point !=
                            self.third_point and not self.graph.is_connected(self.first_point, self.third_point)):
                        pen.setColor(Qt.white)
                        painter.setPen(pen)
                        painter.drawLine(
                            self.first_point.get_coord()[0],
                            self.first_point.get_coord()[1],
                            self.second_point.get_coord()[0],
                            self.second_point.get_coord()[1])
                        pen.setColor(Qt.black)
                        painter.setPen(pen)
                        painter.drawEllipse(
                            QPoint(
                                self.first_point.get_coord()[0],
                                self.first_point.get_coord()[1]),
                            7,
                            7)
                        painter.drawEllipse(
                            QPoint(
                                self.second_point.get_coord()[0],
                                self.second_point.get_coord()[1]),
                            7,
                            7)
                        self.graph.disconnect(
                            self.first_point, self.second_point)
                        painter.drawLine(
                            self.first_point.get_coord()[0],
                            self.first_point.get_coord()[1],
                            self.third_point.get_coord()[0],
                            self.third_point.get_coord()[1])
                        self.graph.connect(self.first_point, self.third_point)
                        self.first_point, self.second_point, self.third_point = None, None, None
                    else:
                        pen.setColor(Qt.black)
                        painter.setPen(pen)
                        painter.drawEllipse(
                            QPoint(
                                self.first_point.get_coord()[0],
                                self.first_point.get_coord()[1]),
                            7,
                            7)
                        painter.drawEllipse(
                            QPoint(
                                self.second_point.get_coord()[0],
                                self.second_point.get_coord()[1]),
                            7,
                            7)
                        self.first_point, self.second_point, self.third_point = None, None, None

    def compute_ch(self):
        """
        Compute the layers of the graph.
        """
        self.layers.clear()
        nodelist = deepcopy(self.graph.getNodes())
        while (nodelist):
            graph_copy = Graph(Nodes=nodelist, Lines=[])
            if (len(nodelist) == 1):
                convex_hull = Graph(Nodes=graph_copy.getNodes())
                self.layers.append(convex_hull)
                nodelist = [
                    node for node in nodelist if node not in convex_hull.getNodes()]
            elif (len(nodelist) == 2):
                convex_hull = Graph(Nodes=graph_copy.getNodes())
                first = convex_hull.getNodes()[0]
                second = convex_hull.getNodes()[1]
                convex_hull.connect(first, second)
                self.layers.append(convex_hull)
                nodelist = [
                    node for node in nodelist if node not in convex_hull.getNodes()]
            else:
                convex_hull = Graph(graph_copy.compute_ch())
                n = len(convex_hull.getNodes())
                for i in range(n - 1):
                    first = convex_hull.getNodes()[i]
                    second = convex_hull.getNodes()[i + 1]
                    convex_hull.connect(first, second)
                first = convex_hull.getNodes()[0]
                second = convex_hull.getNodes()[n - 1]
                convex_hull.connect(first, second)
                self.layers.append(convex_hull)
                nodelist = [
                    node for node in nodelist if node not in convex_hull.getNodes()]

    def show_ch(self):
        """
        Display the layer of the Node list on the screen.
        """
        self.layers.clear()
        pen = QPen(Qt.darkGreen, Qt.DashLine)
        painter = QPainter(self.pixmap())
        painter.setPen(pen)
        nodelist = deepcopy(self.graph.getNodes())
        while (nodelist):
            graph_copy = Graph(Nodes=nodelist, Lines=[])
            if (len(nodelist) == 1):
                convex_hull = Graph(Nodes=graph_copy.getNodes())
                self.layers.append(convex_hull)
                nodelist = [
                    node for node in nodelist if node not in convex_hull.getNodes()]
            elif (len(nodelist) == 2):
                convex_hull = Graph(Nodes=graph_copy.getNodes())
                first = convex_hull.getNodes()[0]
                second = convex_hull.getNodes()[1]
                painter.drawLine(
                    first.get_coord()[0],
                    first.get_coord()[1],
                    second.get_coord()[0],
                    second.get_coord()[1])
                convex_hull.connect(first, second)
                self.layers.append(convex_hull)
                nodelist = [
                    node for node in nodelist if node not in convex_hull.getNodes()]
            else:
                convex_hull = Graph(graph_copy.compute_ch())
                n = len(convex_hull.getNodes())
                for i in range(n - 1):
                    first = convex_hull.getNodes()[i]
                    second = convex_hull.getNodes()[i + 1]
                    painter.drawLine(
                        first.get_coord()[0],
                        first.get_coord()[1],
                        second.get_coord()[0],
                        second.get_coord()[1])
                    convex_hull.connect(first, second)
                first = convex_hull.getNodes()[0]
                second = convex_hull.getNodes()[n - 1]
                convex_hull.connect(first, second)
                painter.drawLine(
                    first.get_coord()[0],
                    first.get_coord()[1],
                    second.get_coord()[0],
                    second.get_coord()[1])
                self.layers.append(convex_hull)
                nodelist = [
                    node for node in nodelist if node not in convex_hull.getNodes()]
            self.update()
        painter.end()
        self.showing_layer = True
        self.message.emit("Showing layer. Click anywhere to disable.")

    def reset(self):
        """
        Reset the whole Canvas and all member variables.
        Graphs are removed and reset to empty.
        """
        self.last_graphs.append(deepcopy(self.graph))
        self.last_main_mode.append(self.main_mode_)
        self.last_sub_mode.append(self.sub_mode_)
        self.next_graphs.clear()
        self.clear()
        whiteboard = QPixmap(self.width_, self.height_)
        whiteboard.fill(Qt.white)
        self.setPixmap(whiteboard)
        del self.graph
        self.graph = Path(Nodes=[], start=None, end=None, Lines=[])
        self.layers.clear()
        self.i_ = 0
        self.edge_diff = 0
        self.showing_layer = False
        self.message.emit("Cleared.")
        self.main_mode_change.emit()

    def problem_node(self):
        """
        If the Path does not fulfill the condition,
        i.e. is not a spanning path or has edge intersections.

        This can find the problematic Nodes.
        """
        nodes = []
        # assert(not self.graph.is_spanning_path())
        deg0 = [v for v in self.graph._Nodes if self.graph.deg(v) == 0]
        deg1 = [v for v in self.graph._Nodes if self.graph.deg(v) == 1]
        deg2 = [v for v in self.graph._Nodes if self.graph.deg(v) == 2]
        deg3 = [v for v in self.graph._Nodes if self.graph.deg(v) > 2]
        if (len(deg2) == len(self.graph._Nodes)):
            pass
        else:
            if (len(deg3) > 0):
                nodes = itertools.chain(nodes, deg0, deg3)
            else:
                nodes = itertools.chain(nodes, deg0, deg1)
        return list(nodes)

    def problem_edge(self):
        """
        If the Path does not fulfill the condition,
        i.e. is not a spanning path or has edge intersections.

        This can find the problematic edges.
        """
        lines = []
        deg1 = [v for v in self.graph._Nodes if self.graph.deg(v) == 1]
        deg2 = [v for v in self.graph._Nodes if self.graph.deg(v) == 2]
        deg3 = [v for v in self.graph._Nodes if self.graph.deg(v) > 2]

        # added one edge
        if (self.edge_diff == 1):
            for v in deg2 + deg3:
                adj = self.graph.adj(v)
                for w in adj:
                    assert (
                        Line(
                            v.get_coord(),
                            w.get_coord()) in self.graph._Lines)
                    self.graph.disconnect(v, w)
                    if (not self.graph.crosses()
                            and self.graph.is_spanning_path()):
                        lines.append(Line(v.get_coord(), w.get_coord()))
                    self.graph.connect(v, w)
        # deleted one edge
        elif (self.edge_diff == -1):
            for v in deg2 + deg1:
                nodelist = self.graph._Nodes
                nodelist = [w for w in nodelist if w not in self.graph.adj(v)]
                for w in nodelist:
                    assert (Line(v.get_coord(), w.get_coord())
                            not in self.graph._Lines)
                    self.graph.connect(v, w)
                    if (not self.graph.crosses()
                            and self.graph.is_spanning_path()):
                        lines.append(Line(v.get_coord(), w.get_coord()))
                    self.graph.disconnect(v, w)

        elif (self.edge_diff == 0):
            if (self.graph.crosses()):
                lines = itertools.chain(lines, self.graph.crosses())

        return list(lines)

    def identify_problems(self):
        """
        If the Path does not fulfill the condition,
        i.e. is not a spanning path or has edge intersections.

        Store the problematic Nodes and edges and mark them
        in color red on the Canvas
        """
        if (self.main_mode_ == MainMode.EDIT_MODE):
            pass
        else:
            if (not self.graph.crosses() and self.graph.is_spanning_path()):
                self.clear()
                whiteboard = QPixmap(self.width_, self.height_)
                whiteboard.fill(Qt.white)
                self.setPixmap(whiteboard)
                pen = QPen()
                painter = QPainter(self.pixmap())
                pen.setColor(Qt.black)
                painter.setPen(pen)
                for node in self.graph._Nodes:
                    painter.drawEllipse(
                        QPoint(
                            node.get_coord()[0],
                            node.get_coord()[1]),
                        7,
                        7)
                for line in self.graph._Lines:
                    points = line.getPoints()
                    painter.drawLine(
                        points[0][0],
                        points[0][1],
                        points[1][0],
                        points[1][1])
                self.update()
                painter.end()
            else:
                pen = QPen()
                painter = QPainter(self.pixmap())
                pen.setColor(Qt.red)
                self.bad_node = self.problem_node()
                self.bad_edge = self.problem_edge()
                for node in self.bad_node:
                    painter.setPen(pen)
                    painter.drawEllipse(
                        QPoint(
                            node.get_coord()[0],
                            node.get_coord()[1]),
                        7,
                        7)
                if (self.edge_diff == 1):
                    for line in self.bad_edge:
                        painter.setPen(pen)
                        points = line.getPoints()
                        painter.drawLine(
                            points[0][0], points[0][1], points[1][0], points[1][1])
                elif (self.edge_diff == -1):
                    for line in self.bad_edge:
                        pen.setStyle(Qt.DashDotLine)
                        painter.setPen(pen)
                        points = line.getPoints()
                        painter.drawLine(
                            points[0][0], points[0][1], points[1][0], points[1][1])
                elif (self.edge_diff == 0):
                    for line in self.bad_edge:
                        painter.setPen(pen)
                        points = line.getPoints()
                        painter.drawLine(
                            points[0][0], points[0][1], points[1][0], points[1][1])
                self.update()
                painter.end()

    def drawGraph(self):
        """
        Clean the Canvas and redraw the underlying Path member.
        """
        painter = QPainter(self.pixmap())
        pen = QPen()
        pen.setColor(Qt.black)
        painter.setPen(pen)
        for node in self.graph.getNodes():
            painter.drawEllipse(
                QPoint(
                    node.get_coord()[0],
                    node.get_coord()[1]),
                7,
                7)
        for line in self.graph.getLines():
            points = line.getPoints()
            painter.drawLine(
                points[0][0],
                points[0][1],
                points[1][0],
                points[1][1])
        if (len(self.graph.getNodes()) == 0):
            self.i_ = 0
        else:
            self.i_ = max([int(node.get_name())
                          for node in self.graph.getNodes()])
        self.edge_diff = len(self.graph._Lines) + 1 - len(self.graph._Nodes)
        self.update()
        painter.end()
        self.identify_problems()

    def saveGraph(self):
        """
        Request to save the graph into a '.grph' file using the Python package json
        """
        fileName = QFileDialog.getSaveFileName(
            self, "Save Graph", "./.grph", "Graph Files (*.grph)")

        data = {
            "graph adj matrix": self.graph.getAdjMatrix().tolist(),
            "graph nodes": [n.toJson() for n in self.graph.getNodes()],
            "graph lines": [l.toJson() for l in self.graph.getLines()],
            "main mode": self.main_mode_,
            "sub mode": self.sub_mode_,
            "size": (self.size().width(), self.size().height())
        }
        data = b64encode(json.dumps(data).encode())
        try:
            with open(fileName[0], "wb") as file:
                file.write(data)
        except BaseException:
            self.message.emit("Save failed")

    def loadGraph(self):
        """
        Request to load a '.grph' file using the Python package json
        """
        try:
            fileName = QFileDialog.getOpenFileName(
                self, "Load Graph", ".", "Graph Files (*.grph)")
            new_list = None
            with open(fileName[0], "rb") as file:
                new_list = json.loads(b64decode(file.read()).decode())
            new_main, new_sub, new_size = MainMode(
                new_list["main mode"]), SubMode(
                new_list["sub mode"]), QSize(
                new_list["size"][0], new_list["size"][1])

            if (new_main != self.main_mode_):
                self.main_mode_change.emit()
            self.sub_mode_change.emit(new_sub)
            new_nodes = [json.loads(n) for n in new_list["graph nodes"]]
            self.graph._Nodes = [Node(d["_name"], tuple(d["_coord"])) for d in new_nodes]
            new_lines = [json.loads(l) for l in new_list["graph lines"]]
            self.graph._Lines = [Line(tuple(d["_point1"]), tuple(d["_point2"]))
                                for d in new_lines]
            self.graph._adj_matrix = np.array(new_list["graph adj matrix"])
            self.layers.clear()
            if (new_size != self.size()):
                r_w = self.size().width() / new_size.width()
                r_h = self.size().height() / new_size.height()
                graph = self.graph
                for p in graph._Nodes:
                    p.set_coord(int(r_w * p._coord[0]), int(r_h * p._coord[1]))
                for l in graph._Lines:
                    ps = l.getPoints()
                    p1, p2 = ps[0], ps[1]
                    new_p1 = (int(r_w * p1[0]), int(r_h * p1[1]))
                    new_p2 = (int(r_w * p2[0]), int(r_h * p2[1]))
                    l.setPoints(new_p1, new_p2)
                whiteboard = QPixmap(self.size().width(), self.size().height())
                whiteboard.fill(Qt.white)
                self.setPixmap(whiteboard)
            self.drawGraph()
            self.message.emit("Welcome again.")
        except BaseException:
            self.message.emit("Load failed")
    

    def undo(self):
        """
        Undo a change done on the Canvas/graph.
        """
        try:
            last_graph = self.last_graphs.pop(-1)
            last_mainmode = self.last_main_mode.pop(-1)
            last_submode = self.last_sub_mode.pop(-1)

            self.next_graphs.append(deepcopy(self.graph))
            self.next_main_mode.append(self.main_mode_)
            self.next_sub_mode.append(self.sub_mode_)

            if (self.main_mode_ != last_mainmode):
                self.main_mode_change.emit()
            if (self.sub_mode_ != last_submode):
                self.sub_mode_change.emit(self.sub_mode_)
            self.main_mode_ = last_mainmode
            self.sub_mode_ = last_submode

            self.graph = deepcopy(last_graph)
            self.clear()
            whiteboard = QPixmap(self.width_, self.height_)
            whiteboard.fill(Qt.white)
            self.setPixmap(whiteboard)
            self.drawGraph()
            self.i_ = max([int(node.get_name())
                          for node in self.graph.getNodes()]) + 1
            self.edge_diff = len(self.graph._Lines) + \
                1 - len(self.graph._Nodes)
            self.identify_problems()
            self.message.emit("Changed reverted.")
        except BaseException:
            self.message.emit("Nothing to undo.")

    def redo(self):
        """
        Redo a change previously undone on the Canvas/graph.
        """
        try:
            next_graph = self.next_graphs.pop(-1)
            next_mainmode = self.next_main_mode.pop(-1)
            next_submode = self.next_sub_mode.pop(-1)

            self.last_graphs.append(deepcopy(self.graph))
            self.last_main_mode.append(self.main_mode_)
            self.last_sub_mode.append(self.sub_mode_)

            if (self.main_mode_ != next_mainmode):
                self.main_mode_change.emit()
            if (self.sub_mode_ != next_submode):
                self.sub_mode_change.emit(self.sub_mode_)
            self.main_mode_ = next_mainmode
            self.sub_mode_ = next_submode

            self.graph = deepcopy(next_graph)
            self.clear()
            whiteboard = QPixmap(self.width_, self.height_)
            whiteboard.fill(Qt.white)
            self.setPixmap(whiteboard)
            self.drawGraph()
            self.i_ = max([int(node.get_name())
                          for node in self.graph.getNodes()]) + 1
            self.edge_diff = len(self.graph._Lines) + \
                1 - len(self.graph._Nodes)
            self.identify_problems()
            self.message.emit("Changed reverted.")
        except BaseException:
            self.message.emit("Nothing to redo.")

    def to_start(self):
        """
        Go to the very start, i.e. Undo until there is nothing to uodo.
        """
        if (len(self.last_graphs) == 0):
            self.message.emit("Nothing to undo")
        else:
            while (len(self.last_graphs) > 0):
                try:
                    last_graph = self.last_graphs.pop(-1)
                    self.next_graphs.append(deepcopy(self.graph))
                    self.next_main_mode.append(self.main_mode_)
                    self.next_sub_mode.append(self.sub_mode_)
                    self.graph = deepcopy(last_graph)
                except BaseException:
                    break
            self.clear()
            whiteboard = QPixmap(self.width_, self.height_)
            whiteboard.fill(Qt.white)
            self.setPixmap(whiteboard)
            self.drawGraph()
            if (len(self.graph.getNodes()) == 0):
                self.i_ = 0
            else:
                self.i_ = max([int(node.get_name())
                              for node in self.graph.getNodes()]) + 1
            self.edge_diff = len(self.graph._Lines) + \
                1 - len(self.graph._Nodes)
            self.identify_problems()
            self.message.emit("Back to start")

    def to_end(self):
        """
        Go to the very end, i.e. Redo until there is nothing to redo.
        """
        if (len(self.next_graphs) == 0):
            self.message.emit("Nothing to redo")
        else:
            while (len(self.next_graphs) > 0):
                try:
                    next_graph = self.next_graphs.pop(-1)
                    self.last_graphs.append(deepcopy(self.graph))
                    self.last_main_mode.append(self.main_mode_)
                    self.last_sub_mode.append(self.sub_mode_)
                    self.graph = deepcopy(next_graph)
                except BaseException:
                    break
            self.clear()
            whiteboard = QPixmap(self.width_, self.height_)
            whiteboard.fill(Qt.white)
            self.setPixmap(whiteboard)
            self.drawGraph()
            if (len(self.graph.getNodes()) == 0):
                self.i_ = 0
            else:
                self.i_ = max([int(node.get_name())
                              for node in self.graph.getNodes()]) + 1
            self.edge_diff = len(self.graph._Lines) + \
                1 - len(self.graph._Nodes)
            self.identify_problems()
            self.message.emit("Back to end")

    def resizeEvent(self, e):
        """
        Resize the canvas and the graphs inside the screen.

        Parameters
        ----------
        e: PyQt5.QtGui.QResizeEvent
            the resize event
        """
        r_w = e.size().width() / e.oldSize().width()
        r_h = e.size().height() / e.oldSize().height()
        graphs = [self.graph] + self.last_graphs + self.next_graphs
        for graph in graphs:
            for p in graph._Nodes:
                p.set_coord(int(r_w * p._coord[0]), int(r_h * p._coord[1]))
            for l in graph._Lines:
                ps = l.getPoints()
                p1, p2 = ps[0], ps[1]
                new_p1 = (int(r_w * p1[0]), int(r_h * p1[1]))
                new_p2 = (int(r_w * p2[0]), int(r_h * p2[1]))
                l.setPoints(new_p1, new_p2)
        self.width_ = e.size().width()
        self.height_ = e.size().height()
        whiteboard = QPixmap(e.size().width(), e.size().height())
        whiteboard.fill(Qt.white)
        self.setPixmap(whiteboard)
        self.drawGraph()

    def mouseReleaseEvent(self, e):
        """
        Perform an action when a mouse button is released.

        The action can be based on the mode currently the program
        is on.

        Parameters:
        -----------
        e: QtGui.QMouseEvent
            the mouse event
        """
        if (self.showing_layer):
            whiteboard = QPixmap(self.width_, self.height_)
            whiteboard.fill(Qt.white)
            self.setPixmap(whiteboard)
            painter = QPainter(self.pixmap())
            pen = QPen()
            pen.setColor(Qt.black)
            painter.setPen(pen)
            for node in self.graph.getNodes():
                painter.drawEllipse(
                    QPoint(
                        node.get_coord()[0],
                        node.get_coord()[1]),
                    7,
                    7)
            for line in self.graph.getLines():
                points = line.getPoints()
                painter.drawLine(
                    points[0][0],
                    points[0][1],
                    points[1][0],
                    points[1][1])
            if (not self.graph.getNodes()):
                self.i_ = 0
            else:
                self.i_ = max([int(node.get_name())
                            for node in self.graph.getNodes()])
            self.edge_diff = len(self.graph._Lines) + \
                1 - len(self.graph._Nodes)
            self.update()
            painter.end()
            self.showing_layer = False
            self.message.emit(" ")
        else:
            if e.button() == Qt.LeftButton:
                self.coord_update(e.x(), e.y())
                pen = QPen(Qt.black)
                painter = QPainter(self.pixmap())
                if (self.sub_mode_ == SubMode.START):
                    pass
                elif (self.sub_mode_ == SubMode.DRAW_NODE):
                    self.draw_node(pen, painter, (self.x_, self.y_))
                elif (self.sub_mode_ == SubMode.DRAW_EDGE):
                    pen = QPen()
                    nodelist = self.graph.getNodes()
                    nodelist = [
                        v for v in nodelist if v.is_in(
                            self.x_, self.y_)]
                    linelist = self.bad_edge
                    linelist = [
                        l for l in linelist if l.is_in(
                            (self.x_, self.y_))]
                    if (len(linelist) == 0 or self.edge_diff != -1):
                        pass
                    else:
                        line = linelist[0]
                        nodes = self.graph.whichNodes(line)
                        self.draw_edge(painter, pen, nodes[0], nodes[1])
                    if (len(nodelist) == 0):
                        pass
                    else:
                        if (self.first_point is None):
                            self.message.emit(f"Selected: {nodelist[0]}")
                            self.first_point = nodelist[0]
                            pen = QPen(Qt.magenta)
                            painter.setPen(pen)
                            painter.drawEllipse(
                                QPoint(
                                    self.first_point.get_coord()[0],
                                    self.first_point.get_coord()[1]),
                                7,
                                7)
                        else:
                            self.message.emit(f"Selected: {nodelist[0]}")
                            self.second_point = nodelist[0]
                            pen.setColor(Qt.black)
                            painter.setPen(pen)
                            painter.drawEllipse(
                                QPoint(
                                    self.first_point.get_coord()[0],
                                    self.first_point.get_coord()[1]),
                                7,
                                7)
                            if (self.first_point != self.second_point):
                                self.draw_edge(
                                    painter, pen, self.first_point, self.second_point)
                                self.first_point, self.second_point = None, None
                            else:
                                self.second_point = None
                elif (self.sub_mode_ == SubMode.DEL_NODE):
                    if (self.main_mode_ == MainMode.FLIP_MODE):
                        self.message.emit("Not available in FLIP MODE.")
                    else:
                        nodelist = self.graph.getNodes()
                        nodelist = [
                            v for v in nodelist if v.is_in(
                                self.x_, self.y_)]
                        if (len(nodelist) == 0):
                            pass
                        else:
                            self.delete_node(painter, pen, nodelist[0])
                        pass
                elif (self.sub_mode_ == SubMode.DEL_EDGE):
                    pen = QPen()
                    pen.setColor(Qt.magenta)
                    painter.setPen(pen)
                    nodelist = self.graph.getNodes()
                    nodelist = [
                        v for v in nodelist if v.is_in(
                            self.x_, self.y_)]
                    if (len(nodelist) == 0):
                        pass
                    else:
                        if (self.first_point is None):
                            self.message.emit(f"Selected: {nodelist[0]}")
                            self.first_point = nodelist[0]
                            painter.drawEllipse(
                                QPoint(
                                    self.first_point.get_coord()[0],
                                    self.first_point.get_coord()[1]),
                                7,
                                7)
                        else:
                            self.message.emit(f"Selected: {nodelist[0]}")
                            self.second_point = nodelist[0]
                            pen.setColor(Qt.black)
                            painter.setPen(pen)
                            painter.drawEllipse(
                                QPoint(
                                    self.first_point.get_coord()[0],
                                    self.first_point.get_coord()[1]),
                                7,
                                7)
                            if (self.first_point != self.second_point):
                                self.delete_edge(
                                    painter, pen, self.first_point, self.second_point)
                                self.first_point, self.second_point = None, None
                            else:
                                self.first_point = None
                self.update()
                painter.end()

            elif e.button() == Qt.RightButton:
                self.coord_update(e.x(), e.y())
                pen = QPen()
                painter = QPainter(self.pixmap())
                linelist = self.graph.getLines()
                linelist = [l for l in linelist if l.is_in((self.x_, self.y_))]
                if (len(linelist) == 1):
                    line = linelist[0]
                    if (self.main_mode_ == MainMode.FLIP_MODE and self.edge_diff !=
                            0 and line not in self.bad_edge):
                        self.message.emit(
                            "Invalid Action: Path already not valid")
                        self.first_point, self.second_point = None, None
                    else:
                        nodes = self.graph.whichNodes(line)
                        self.delete_edge(painter, pen, nodes[0], nodes[1])
                        self.first_point, self.second_point = None, None
                self.update()
                painter.end()

            if (self.first_point is None):
                self.identify_problems()

        # configure layers
        self.compute_ch()

    def __hash__(self):
        return hash(self.canvas.graph, self.main_mode_, self.sub_mode_)
