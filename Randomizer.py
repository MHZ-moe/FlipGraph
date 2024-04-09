from PyQt5.QtCore import QSize,Qt,pyqtSlot,QObject
from random import shuffle
from Canvas import *
from time import sleep


"""
The Randomizer Object. 

Define the QObject (from Qt Framework) to be run inside a thread.
"""
class Randomizer(QObject):
    randomize_done = pyqtSignal()
    randomize_forced_stop = pyqtSignal()
    
    def __init__(self, canvas, parent=None):
        super().__init__()
        self._canvas = canvas
        self.stopped = True
    
    """
    Generate a random non-crossing spanning path.
    """
    @pyqtSlot()
    def run(self): 
        nodelist = self._canvas.graph.getNodes()
        self.stopped = False
        n = len(nodelist)
        if (n == 0):
            self._canvas.message.emit("The graph is empty.")
        else:
            sample_graph = Path()
            past_nodelist = []
            x = 0
            while (True):
                x += 1
                shuffle(nodelist)
                if (nodelist in past_nodelist):
                    continue
                print("Step:", str(x))
                first_node = nodelist[0]
                sample_graph = Path(Nodes=[first_node],start=first_node,end=first_node,Lines=[])
                for i in range(1,n):
                    node = nodelist[i]
                    sample_graph.expandPath(node)
                    if (sample_graph.crosses() or not sample_graph.is_spanning_path()):
                        break
                if (self.stopped):
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
                    self.randomize_forced_stop.emit()
                    self._canvas.message.emit("Forced stop")
                    break
                if (len(sample_graph.getNodes()) < n or (sample_graph.crosses() or not sample_graph.is_spanning_path())):
                    past_nodelist.append(deepcopy(nodelist))
                    continue
                else:
                    break
            if (not self.stopped):
                self._canvas.last_graphs.append(self._canvas.graph)
                self._canvas.graph = deepcopy(sample_graph)
                self._canvas.drawGraph()
                self.randomize_done.emit()
                self._canvas.message.emit("Done")
    
    """
    Change the status of the function to stop.
    """
    @pyqtSlot() 
    def change_stop(self):
        self.stopped = True
        
""" 
The thread object for Randomizer
"""
class RandomizerThread(QThread):
    stopped = pyqtSignal()
    
    def __init__(self, randomizer, parent=None):
        super().__init__()
        self._randomizer = randomizer
        self._randomizer.moveToThread(self)
        self.started.connect(self._randomizer.run)
        self._randomizer.randomize_done.connect(self.stop)
        self._randomizer.randomize_forced_stop.connect(self.stop)
        self._randomizer.randomize_forced_stop.connect(self.deleteLater)
        self._randomizer.randomize_forced_stop.connect(self._randomizer.deleteLater)
     
    """ 
    Terminate the thread after Randomizer terminates gracefully.
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
        self._randomizer.change_stop()
        self.requestInterruption()
        self.wait()
        self.stopped.emit()

""" 
The message box object.

Generate a message box when the thread is running
"""
class RandomizerWaitBox(QMessageBox):
    def __init__(self, randomizerThread,parent=None):
      super().__init__()
      self._randomizerThread = randomizerThread
      self.cancelButton = QPushButton("Cancel")
      self.addButton(self.cancelButton, QMessageBox.RejectRole)
      self.setText("Generating random graph, please wait...")
      self.move(100,200)
      
      self.cancelButton.clicked.connect(self.reject)
      self.rejected.connect(self._randomizerThread.force_stop)
      self._randomizerThread.stopped.connect(self.accept)
      
    """ 
    Start the randomizer thread.
    """
    def randomize(self):
      self._randomizerThread.start()
      self._randomizerThread.quit()
      if (len(self._randomizerThread._randomizer._canvas.graph.getNodes()) != 0):
        self.show()
        self.exec()
        sleep(1)