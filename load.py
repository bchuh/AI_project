import os

from PySide2.QtCore import QTime, QCoreApplication, QEventLoop, Qt
from PySide2.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QLabel, QVBoxLayout

from node_class import Node
from main import load_node
import glob

app = QApplication([])
label = QLabel()
view = QGraphicsView()
scene = QGraphicsScene()
view.setScene(scene)
view.show()

layout = QVBoxLayout(view)
layout.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
layout.addWidget(label)
label.show()
view.showMaximized()
nodes_dir = os.path.join(os.getcwd(), 'nodes')
folder_dirs = glob.glob(nodes_dir + "\*")
folder_dirs.reverse()
#Debug:
combo_dict = {}
shape_dict = {}
#
i=1
for dir in folder_dirs:
    app.processEvents()
    if ".py" in dir:
       continue
    label.setText("<font size=300 color=white>"+str(i)+"</font>")
    _node: Node = load_node(dir, with_suffix_and_absolute_path=True)
    angles_encoding = _node.encodeAngles(view)
    if angles_encoding not in shape_dict:
        shape_dict[angles_encoding] = [_node]
    else:
        print("collide")
        shape_dict[angles_encoding].append(_node)
    _node.paint(scene)
    view.show()
    view.setBackgroundBrush(Qt.gray)
    view.update()
    '''dieTime = QTime.currentTime().addMSecs(2)
    while (QTime.currentTime() < dieTime):
        QCoreApplication.processEvents(QEventLoop.AllEvents, 20)'''
    scene.clear()  # not working for some reason
    '''view.update()
    dieTime = QTime.currentTime().addMSecs(5)
    while (QTime.currentTime() < dieTime):
        QCoreApplication.processEvents(QEventLoop.AllEvents, 20)'''
    #view.hide()
    i+=1
    print(angles_encoding)
    print(len(shape_dict))
print("------Parsing complete---------")
print("Found ", len(shape_dict), " types of shape!")
app.exec_()