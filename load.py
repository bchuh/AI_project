import os
import pickle
import sys
import time

from PySide2.QtCore import QTime, QCoreApplication, QEventLoop, Qt
from PySide2.QtGui import QImage, QPainter
from PySide2.QtWidgets import QApplication, QGraphicsView, QGraphicsScene, QLabel, QVBoxLayout

from node_class import Node
from main import load_node
import glob

def x_in_y(query, base):
    try:
        l = len(query)
    except TypeError:
        l = 1
        query = type(base)((query,))

    for i in range(len(base)):
        if base[i:i+l] == query:
            return True
    return False


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
mode = "BFS"
nodes_dir = os.path.join(os.getcwd(), mode+'_nodes')
folder_dirs = glob.glob(nodes_dir + "\*")
folder_dirs.reverse()
#Debug:
combo_dict = {}
shape_dict = {}
organize = False
if organize:
    i=1
    for dir in folder_dirs:
        app.processEvents()
        if ".py" in dir:
           continue
        if ".dict" in dir:
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
    ###########
    _path = os.getcwd()
    _name = 'shape.dict'
    _folder = mode+"_nodes"
    _path = os.path.join(_path, _folder, _name)
    with open(_path, 'wb') as f:
        pickle.dump(shape_dict, f)
    ############
    print("------Parsing complete---------")
    print("Found ", len(shape_dict), " types of shape!")
else:
    shape_dict = {}


#########
_path = os.getcwd()
_dfspath = os.getcwd()
_name = 'shape.dict'
_folder = mode+"_nodes"
_dfsfolder = "DFS_nodes"
_path = os.path.join(_path, _folder)
_path = os.path.join(_path,  _name)
_dfspath = os.path.join(_dfspath, _dfsfolder)
_dfspath = os.path.join(_dfspath,  _name)
with open(_path, 'rb') as f:
    shape_dict = pickle.load(f)
with open(_dfspath, 'rb') as k:
    combo_dict = pickle.load(k)
#########
print("------Showing all shapes---------")

'''_key = list(shape_dict.keys())[0]
for item in shape_dict[_key]:
    app.processEvents()
    _node = item
    _node.paint(scene)
    view.show()
    view.setBackgroundBrush(Qt.gray)
    view.update()
    dieTime = QTime.currentTime().addMSecs(500)
    while (QTime.currentTime() < dieTime):
        QCoreApplication.processEvents(QEventLoop.AllEvents, 20)
    scene.clear()
    view.update()'''
m = 1
for key in shape_dict.keys():
    m += 1
    if key not in combo_dict.keys():
        print(m)
        print(key)
        app.processEvents()
        _node = shape_dict[key][0]
        _node.paint(scene)
        view.show()
        view.setBackgroundBrush(Qt.gray)
        view.update()
        #####
        image = QImage(scene.sceneRect().width(), scene.sceneRect().height(), QImage.Format_RGB888)
        painter = QPainter(image)
        scene.render(painter, image.rect())
        painter.end()
        dieTime = QTime.currentTime().addMSecs(2000)
        while (QTime.currentTime() < dieTime):
            QCoreApplication.processEvents(QEventLoop.AllEvents, 50)
        scene.clear()
        view.update()
        time.sleep(3)

i=1
for key in shape_dict.keys():
    '''test_tup = (90.0, 90.0, 90.0)
    if not x_in_y(test_tup,key[0]):
        continue'''

    app.processEvents()
    _node = shape_dict[key][0]
    _node.paint(scene)
    view.show()
    view.setBackgroundBrush(Qt.gray)
    view.update()
    #####
    image = QImage(scene.sceneRect().width(), scene.sceneRect().height(), QImage.Format_RGB888)
    painter = QPainter(image)
    scene.render(painter, image.rect())
    painter.end()
    _path = os.getcwd()
    _name = str(i)+'.jpg'
    _folder = "images"
    _path = os.path.join(_path, _folder)
    _path = os.path.join(_path, _name)
    image.save(_path)
    #####
    dieTime = QTime.currentTime().addMSecs(2)
    while (QTime.currentTime() < dieTime):
        QCoreApplication.processEvents(QEventLoop.AllEvents, 20)
    scene.clear()
    view.update()
    i+=1
exit(0)
app.exec_()
