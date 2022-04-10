import os

from PySide2.QtCore import QTime, QCoreApplication, QEventLoop, Qt
from PySide2.QtWidgets import QApplication, QGraphicsView, QGraphicsScene

from node_class import Node
from main import load_node
import glob

app = QApplication([])
view = QGraphicsView()
scene = QGraphicsScene()
view.setScene(scene)
view.show()
view.showMaximized()
nodes_dir = os.path.join(os.getcwd(), 'nodes')
folder_dirs = glob.glob(nodes_dir + "\*")
folder_dirs.reverse()
for dir in folder_dirs:
    if ".py" in dir:
        continue
    _node: Node = load_node(dir, with_suffix_and_absolute_path=True)
    encoding = _node.encodeMatrix()
    _node.paint(scene)
    view.show()
    view.setBackgroundBrush(Qt.gray)
    view.update()
    dieTime = QTime.currentTime().addMSecs(1000)
    while (QTime.currentTime() < dieTime):
        QCoreApplication.processEvents(QEventLoop.AllEvents, 20)
    _node.clearPoly(scene)
    scene.clear()  # not working for some reason
    view.update()
    dieTime = QTime.currentTime().addMSecs(500)
    while (QTime.currentTime() < dieTime):
        QCoreApplication.processEvents(QEventLoop.AllEvents, 20)
    #view.hide()

app.exec_()