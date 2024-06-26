import sys

from PyQt5.QtCore import QSize
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtWidgets import QToolBar

from Canvas import Canvas
from Canvas import MainMode
from Canvas import SubMode

from Randomizer import Randomizer
from Randomizer import RandomizerThread
from Randomizer import RandomizerWaitBox

from Solver import Solver
from Solver import SolverThread
from Solver import SolverWaitBox

from Wrapper import Wrapper
from Wrapper import WrapperThread
from Wrapper import WrapperWaitBox

VERSION = "v.2024-4-30"


class MainWindow(QMainWindow):

    def __init__(self, width, height):
        """
        The MainWindow class.

        Built upon the QMainWindow class from the PyQt5 framework.

        Initialize the main program.
        """
        super(MainWindow, self).__init__()

        self.width_ = width
        self.height_ = height

        self.oldsize = QSize(width, height)

        # MainWindow set
        self.setWindowTitle("FlipGraphin")
        self.setMinimumSize(QSize(800, 600))

        # Variables
        self.main_mode_ = MainMode.EDIT_MODE
        self.sub_mode_ = SubMode.DRAW_NODE

        # Canvas
        self.canvas = Canvas(self.width_, self.height_)
        self.setCentralWidget(self.canvas)

        # Toolbar & Buttons
        self.toolbar1 = QToolBar()
        self.toolbar2 = QToolBar()
        self.toolbar3 = QToolBar()
        self.addToolBar(Qt.TopToolBarArea, self.toolbar1)
        self.addToolBarBreak()
        self.addToolBar(Qt.TopToolBarArea, self.toolbar2)
        self.addToolBarBreak()
        self.addToolBar(Qt.TopToolBarArea, self.toolbar3)

        self.toolbar1.setFixedHeight(32)
        self.toolbar2.setFixedHeight(32)
        self.toolbar3.setFixedHeight(32)

        self.button1 = QPushButton("NODE")
        self.button2 = QPushButton("EDGE")
        self.button3 = QPushButton("DEL_NODE")
        self.button4 = QPushButton("DEL_EDGE")
        self.button5 = QPushButton("FLIP")
        self.button6 = QPushButton("CLEAR")
        self.button7 = QPushButton("LAYERS")
        self.button8 = QPushButton("UNDO")
        self.button9 = QPushButton("REDO")
        self.button10 = QPushButton("TO START")
        self.button11 = QPushButton("TO END")
        self.button12 = QPushButton("RANDOM")
        self.button13 = QPushButton("SOLVE")
        self.button14 = QPushButton("WRAP")
        self.button15 = QPushButton("SAVE")
        self.button16 = QPushButton("LOAD")
        self.button17 = QPushButton("ABOUT")
        self.button18 = QPushButton("HELP")
        self.statusText = QLabel("Welcome")
        self.buttons = [self.button1, self.button2, self.button3, self.button4]
        self.check_dict = {SubMode.DRAW_NODE: 0, SubMode.DRAW_EDGE: 1,
                           SubMode.DEL_NODE: 2, SubMode.DEL_EDGE: 3}

        # Flip Button
        self.toolbar1.addWidget(self.button5)
        self.button5.setCheckable(True)
        self.button5.setStyleSheet("color: black; background-color: yellow")
        self.toolbar1.addSeparator()

        # Basic functions
        for button in self.buttons:
            button.setCheckable(True)
            button.setChecked(False)
            self.toolbar1.addWidget(button)
        self.button1.setChecked(True)
        self.toolbar1.addSeparator()

        # Flip graph specific functions
        self.toolbar1.addWidget(self.button12)
        self.toolbar1.addWidget(self.button13)
        self.toolbar1.addWidget(self.button14)

        # Advanced functions
        self.toolbar2.addWidget(self.button6)
        self.toolbar2.addWidget(self.button8)
        self.toolbar2.addWidget(self.button9)
        self.toolbar2.addWidget(self.button10)
        self.toolbar2.addWidget(self.button11)
        self.toolbar2.addWidget(self.button7)
        self.toolbar2.addSeparator()

        # Miscellaneous functions
        self.toolbar2.addWidget(self.button15)
        self.toolbar2.addWidget(self.button16)

        self.toolbar3.addWidget(self.button17)
        self.toolbar3.addWidget(self.button18)
        self.toolbar3.addSeparator()
        self.toolbar3.addWidget(self.statusText)

        self.button1.clicked.connect(
            lambda: self.check_sub_mode(
                SubMode.DRAW_NODE))
        self.button2.clicked.connect(
            lambda: self.check_sub_mode(
                SubMode.DRAW_EDGE))
        self.button3.clicked.connect(
            lambda: self.check_sub_mode(
                SubMode.DEL_NODE))
        self.button4.clicked.connect(
            lambda: self.check_sub_mode(
                SubMode.DEL_EDGE))
        self.button5.clicked.connect(lambda: self.switch_flip_mode())
        self.button6.clicked.connect(lambda: self.canvas.reset())
        self.button7.clicked.connect(lambda: self.canvas.show_ch())
        self.button8.clicked.connect(lambda: self.canvas.undo())
        self.button9.clicked.connect(lambda: self.canvas.redo())
        self.button10.clicked.connect(lambda: self.canvas.to_start())
        self.button11.clicked.connect(lambda: self.canvas.to_end())
        self.button12.clicked.connect(lambda: self.start_randomize())
        self.button13.clicked.connect(lambda: self.start_solve())
        self.button14.clicked.connect(lambda: self.start_wrap())
        self.button15.clicked.connect(lambda: self.canvas.saveGraph())
        self.button16.clicked.connect(lambda: self.canvas.loadGraph())
        self.button17.clicked.connect(lambda: self.about_page())
        self.button18.clicked.connect(lambda: self.help_page())
        self.canvas.message.connect(self.statusText.setText)
        self.canvas.main_mode_change.connect(self.switch_flip_mode)
        self.canvas.sub_mode_change.connect(self.check_sub_mode)

        # disabled
        self.button12.setEnabled(False)
        self.button13.setEnabled(False)
        self.button14.setEnabled(False)

    # Methods for buttons

    def check_sub_mode(self, mode_after=None):
        """
        Check the mode of the program based on the buttons clicked.
        Applied buttons are: NODE, EDGE, DEL_NODE, DEL_EDGE

        Parameters:
        -----------
        mode_after: Mode
            the Mode after the function call
        """
        if (mode_after is not None):
            if (self.sub_mode_ == SubMode.START):
                self.buttons[self.check_dict[mode_after]].setChecked(True)
            else:
                self.buttons[self.check_dict[self.sub_mode_]].setChecked(False)
                self.buttons[self.check_dict[mode_after]].setChecked(True)
            self.sub_mode_ = mode_after
            self.canvas.first_point, self.canvas.second_point = None, None
            self.canvas.setSubMode(mode_after)

    def switch_flip_mode(self):
        """
        Switch between MAIN mode and FLIP mode.
        """
        if (self.main_mode_ == MainMode.EDIT_MODE):
            if (self.canvas.graph.crosses()
                    or not self.canvas.graph.is_spanning_path()):
                self.canvas.message.emit("CANNOT SWITCH: Not a valid path")
                self.canvas.first_point, self.canvas.second_point = None, None
                self.button5.setChecked(False)
            else:
                self.main_mode_ = MainMode.FLIP_MODE
                self.canvas.setMainMode(MainMode.FLIP_MODE)
                self.canvas.message.emit("Switched to: FLIP MODE")
                self.button5.setChecked(True)
                self.button5.setStyleSheet(
                    "color: yellow; background-color: black")
                self.button5.setText("EDIT")
                self.button12.setEnabled(True)
                self.button13.setEnabled(True)
                self.button14.setEnabled(True)
                self.button1.setEnabled(False)
                self.button2.setEnabled(False)
                self.button3.setEnabled(False)
                self.button4.setEnabled(False)
                self.canvas.drawGraph()
                self.canvas.first_point, self.canvas.second_point = None, None
                self.check_sub_mode(SubMode.DRAW_EDGE)
        else:
            if (self.canvas.graph.getNodes() and (
                    self.canvas.graph.crosses() or not self.canvas.graph.is_spanning_path())):
                self.canvas.message.emit("CANNOT SWITCH: Not a valid path")
                self.canvas.first_point, self.canvas.second_point = None, None
                self.button5.setChecked(True)
            else:
                self.main_mode_ = MainMode.EDIT_MODE
                self.canvas.setMainMode(MainMode.EDIT_MODE)
                self.canvas.message.emit("Switched to: EDIT MODE")
                self.button5.setChecked(False)
                self.button5.setStyleSheet(
                    "color: black; background-color: yellow")
                self.button5.setText("FLIP")
                self.button12.setEnabled(False)
                self.button13.setEnabled(False)
                self.button14.setEnabled(False)
                self.button1.setEnabled(True)
                self.button2.setEnabled(True)
                self.button3.setEnabled(True)
                self.button4.setEnabled(True)
                self.canvas.drawGraph()
                self.canvas.first_point, self.canvas.second_point = None, None

    def start_randomize(self):
        """
        Start the randomizer thread.
        """
        if (self.main_mode_ == MainMode.EDIT_MODE):
            self.canvas.message.emit("Not available in EDIT mode.")
        else:
            self.randomizer = Randomizer(self.canvas)
            self.thread = RandomizerThread(self.randomizer)
            self.waitbox = RandomizerWaitBox(self.thread)
            self.waitbox.randomize()

    def start_solve(self):
        """
        Start the solver thread.
        """
        if (self.main_mode_ == MainMode.EDIT_MODE):
            self.canvas.message.emit("Not available in EDIT mode.")
        else:
            self.solver = Solver(self.canvas)
            self.solver.message.connect(self.statusText.setText)
            self.thread = SolverThread(self.solver)
            self.waitbox = SolverWaitBox(self.thread)
            self.waitbox.solve()

    def start_wrap(self):
        """
        Start the wrapper thread.
        """
        if (self.main_mode_ == MainMode.EDIT_MODE):
            self.canvas.message.emit("Not available in EDIT mode.")
        else:
            self.wrapper = Wrapper(self.canvas)
            self.wrapper.message.connect(self.statusText.setText)
            self.thread = WrapperThread(self.wrapper)
            self.waitbox = WrapperWaitBox(self.thread)
            self.waitbox.wrap()

    def about_page(self):
        """
        Display the about page
        """
        msg = "A Graph Drawing Program\nVersion: " + VERSION
        QMessageBox.about(self, "FlipGraphin", msg)

    def help_page(self):
        """
        Display the help page
        """
        msg = "General Functionality:\n\n"
        msg += "NODE: Append a node at the end of the path\n"
        msg += "EDGE: Click on two points to draw an edge\n"
        msg += "DEL_NODE: Delete a node and edges adjacent to it\n"
        msg += "DEL_EDGE: Click on two points to delete an edge\n"
        msg += "CLEAR: Clear the board\n"
        msg += "UNDO: Undo previous change\n"
        msg += "REDO: Redo next change\n"
        msg += "TO_START: Undo until it's not undoable\n"
        msg += "TO_END: Redo until it's not redoable\n\n"
        msg += "Flip graph specific Functionality: \n\n"
        msg += "FLIP: Switch to Flip Mode\n"
        msg += "LAYERS: Show the iteratively constructed convex layers\n"
        msg += "RANDOM: Randomly generate a path fulfilling all conditions\n"
        msg += "SOLVE: Reconfigure the graph into a canonical path\n"
        msg += "WRAP: Reconfigure a canonical path into a wrapping path\n\n"
        msg += "Miscellaneous Functionality:\n\n"
        msg += "SAVE: Save the graph into a .grph file\n"
        msg += "LOAD: Load a .grph file\n"
        msg += "ABOUT: Display the about page\n"
        msg += "HELP: Display this page\n"
        QMessageBox.about(self, "FlipGraphin", msg)

    def resizeEvent(self, e):
        """
        Resize the canvas when the window is resized.
        """
        if (not self.isMaximized()):
            self.oldsize = e.oldSize()
        else:
            self.resize(self.oldsize.width(), self.oldsize.height())
        self.canvas.graph.compute_ch()

    def closeEvent(self, e):
        """
        Request to save the graph before closing the program.

        Parameters:
        -----------
        e: QtGui.QMouseEvent
        """
        msg = "You're about to exit the program.\nWould you like to save?"
        msgbox = QMessageBox.question(
            self, "FlipGraphin", msg, QMessageBox.StandardButtons(
                QMessageBox.Cancel | QMessageBox.Yes | QMessageBox.No))

        if (msgbox == QMessageBox.Yes):
            self.canvas.saveGraph()
            e.accept()
        elif (msgbox == QMessageBox.No):
            e.accept()
        else:
            e.ignore()


if __name__ == '__main__':
    """
    The main function.
    """
    app = QApplication(sys.argv)
    size = app.primaryScreen().size()
    window = MainWindow(size.width(), size.height())
    window.showMaximized()
    window.show()
    sys.exit(app.exec())
