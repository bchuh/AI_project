from PySide2.QtCore import QPoint, QLineF, QPointF, QTime, QCoreApplication, QEventLoop, Qt
from PySide2.QtWidgets import QApplication, QMainWindow, QGraphicsView, QGraphicsScene
from PySide2.QtGui import QPolygon, QTransform
from node import Node
from piece import Piece

app = QApplication([])
view = QGraphicsView()
scene = QGraphicsScene()
view.setScene(scene)
view.showMaximized()

scale_factor = 2
view.scale(scale_factor, scale_factor)
view.show()
stack = []
shape_list = [0, 0, 1, 2, 2, 3, 4]  # shape ID of 7 pieces

_node = Node()
_node.addPiece(
    Piece(shape_list[_node.next_step])
)
stack.append(_node)

while len(stack) != 0:
    _node = stack.pop()
    next_step = _node.next_step
    _piece = Piece(next_step)
    for node_edge_no in range(_node.getEdgeCount()):
        for piece_edge_no in range(_piece.getEdgeCount()):
            # TODO: 非等长边相接
            # TODO: node可视化
            # TODO: merge piece into node
            _node_edge = _node.getEdge(view, node_edge_no, True)
            _piece_edge = _piece.getEdge(view, piece_edge_no)
            if _node_edge.length() == _piece_edge.length():
                angle = _piece_edge.angleTo(_node_edge)
                trans = QTransform()
                trans.rotate(360 - angle)
                _piece = trans.map(_piece)
                _piece.translate(
                    -scale_factor * (_piece_edge.p1() - _node_edge.p1()).toPoint()
                )
                if _piece.intersected(_node).length() == 0:  # 检查有无非法重叠
                    _node.addPiece(_piece)
                    stack.append(_node)
