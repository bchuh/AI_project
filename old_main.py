from PySide2.QtCore import QPoint, QLineF, QPointF, QTime, QCoreApplication, QEventLoop, Qt
from PySide2.QtWidgets import QApplication, QMainWindow, QGraphicsView, QGraphicsScene
from PySide2.QtGui import QPolygon, QTransform
'''
注意：此文件已废弃
'''

app = QApplication([])
view = QGraphicsView()
scene = QGraphicsScene()
view.setScene(scene)
view.showMaximized()
def getTriangleEdge(poly:QPolygon, start_index,reverse=False):
    edge_count=3
    if reverse==False:
        return QLineF(view.mapToScene(poly.at(start_index)),view.mapToScene(poly.at(start_index+1 % edge_count)))
    else:
        return QLineF(-view.mapToScene(poly.at(start_index)), -view.mapToScene(poly.at(start_index + 1 % edge_count)))




triangle1 = QPolygon()
triangle2 = QPolygon()
# 顶点顺序规范：使得边向量的左向法线指向内部
triangle_large = [QPoint(0,0),QPoint(0,200), QPoint(200,200)]
triangle_small = [QPoint(0,0),QPoint(0,100), QPoint(100,100)]

triangle1.append(triangle_large)
triangle2.append(triangle_small)
triangle2.translate(200,0)

tri_pt1=scene.addPolygon(triangle1)
tri_pt2 = scene.addPolygon(triangle2)
tri_pt1.setBrush(Qt.blue)
tri_pt2.setBrush(Qt.red)
scale_factor=2
view.scale(scale_factor,scale_factor)
view.show()

#小的移到大的上

dieTime = QTime.currentTime().addMSecs(800)
while (QTime.currentTime() < dieTime):
    QCoreApplication.processEvents(QEventLoop.AllEvents, 20)


triangle2.translate(-scale_factor*(view.mapToScene(triangle2.at(1))-view.mapToScene(triangle1.at(0))).toPoint())
scene.removeItem(tri_pt2)
tri_pt2=scene.addPolygon(triangle2)
tri_pt2.setBrush(Qt.red)

dieTime = QTime.currentTime().addMSecs(800)
while (QTime.currentTime() < dieTime):
    QCoreApplication.processEvents(QEventLoop.AllEvents, 20)

_t2edge=getTriangleEdge(triangle2, 1, True)
_t1edge=getTriangleEdge(triangle1, 2)
angle=_t2edge.angleTo(_t1edge)
trans=QTransform()
trans.rotate(360-angle)#360-angle
# rotate会使其逆时针旋转（正常坐标系），但因为widget坐标系y轴向下，所以在widget中做顺时针旋转。这里我们用360-angle调整回正确的角度
triangle2=trans.map(triangle2)
scene.removeItem(tri_pt2)
tri_pt2=scene.addPolygon(triangle2)
tri_pt2.setBrush(Qt.red)
tri2_edge=1
tri1_edge=2
result_inter=triangle1.intersected(triangle2)
print(result_inter.length())
is_intersect=False
'''
for i in range(3):
    for j in range(3):
        if i==tri2_edge or j==tri1_edge:
            continue
        if getTriangleEdge(triangle2, i).intersects(getTriangleEdge(triangle1,j))==True:
            is_intersect=True
'''
view.repaint()


app.exec_()