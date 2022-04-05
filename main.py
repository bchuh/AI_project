from PySide2.QtCore import QPoint, QLineF, QPointF, QTime, QCoreApplication, QEventLoop, Qt
from PySide2.QtWidgets import QApplication, QMainWindow, QGraphicsView, QGraphicsScene
from PySide2.QtGui import QPolygon, QTransform
from node import Node
from piece import Piece
from copy import deepcopy

app = QApplication([])
view = QGraphicsView()
scene = QGraphicsScene()
view.setScene(scene)
view.showMaximized()

scale_factor = 1
view.scale(scale_factor, scale_factor)
view.show()
stack = []
result_list = []
shape_list = [0, 0, 1, 2, 2, 3, 4]  # shape ID of 7 pieces

_node = Node()
_node.addPiece(
    Piece(shape_list[_node.candidates.pop(2)])
)
stack.append(_node)

while len(stack) != 0:
    _parent_node = stack.pop()
    candidates = _parent_node.candidates
    if len(candidates) == 0:
        result_list.append(_parent_node)
        continue
    for _ in range(len(candidates)):
        # 开始创建新的子节点， 不需要深拷贝因为这是父节点
        _cand = _parent_node.candidates.pop()  # _cand是指第几号拼图，是shape_list的某个位置下标
        _exampler_piece = Piece(shape_list[_cand]) # piece样品，跟本次迭代中创建的piece一模一样，只是为了方便查看形状的边长而存在
        for node_edge_no in range(_parent_node.getEdgeCount()-1):
            for piece_edge_no in range(_exampler_piece.getEdgeCount(reduced=True)):
                # TODO: 非等长边相接
                # TODO: 检查重复
                # TODO：平行四边形之类改为只有两种旋转情况
                # TODO: 检查边数
                # TODO: 检查组合体内角判断两组合体是否外形一样

                _node_edge = _parent_node.getEdge(view, node_edge_no, True)
                _piece_edge = _exampler_piece.getEdge(view, piece_edge_no)
                if round(_node_edge.length()) == round(_piece_edge.length()):
                    _loop_count = 1
                else:
                    _loop_count = 2

                for i in range(_loop_count):
                    _node = deepcopy(_parent_node)
                    _piece = Piece(shape_list[_cand])  # create a new one instead of sharing
                    _node_edge = _node.getEdge(view, node_edge_no, True)
                    _piece_edge = _piece.getEdge(view, piece_edge_no)

                    angle = _piece_edge.angleTo(_node_edge)
                    trans = QTransform()
                    trans.rotate(360 - angle)
                    _piece.q_object = trans.map(_piece.q_object)
                    # 因为旋转改变了坐标，要再获取一次
                    _node_edge = _node.getEdge(view, node_edge_no, True)
                    _piece_edge = _piece.getEdge(view, piece_edge_no)
                    if i==0:
                        _piece.q_object.translate(
                            -scale_factor * (_piece_edge.p1() - _node_edge.p1()).toPoint()
                        )
                    else:
                        _piece.q_object.translate(
                            -scale_factor * (_piece_edge.p2() - _node_edge.p2()).toPoint()
                        )
                    if _piece.q_object.intersected(_node.q_object).length() == 0:  # 检查有无非法重叠
                        _node.addPiece(_piece, node_edge_no+1, piece_edge_no+1)  # addPiece会对piece做deepcopy，所以这里不需要
                        _node.paint(scene)
                        ### debug
                        view.repaint()
                        dieTime = QTime.currentTime().addMSecs(50)
                        while (QTime.currentTime() < dieTime):
                            QCoreApplication.processEvents(QEventLoop.AllEvents, 20)
                        _node.clearPoly(scene)
                        scene.clear()  # not working for some reason
                        view.update()
                        ###
                        stack.append(_node)


app.exec_()
