from PySide2.QtCore import QPoint
from PySide2.QtGui import QPolygon
from PySide2.QtWidgets import QGraphicsScene, QGraphicsView

from abstract_poly import Poly
from piece import Piece
from copy import deepcopy


class Node(Poly):
    '''
    Collection of pieces, also represent current state
    - useful parent methods: united(), indexOf(), intersected(), toList
    '''

    def __init__(self):
        super(Node, self).__init__()
        self.pieces = []
        self.edge_count = 0
        self.candidates = [0, 1, 2, 3, 4, 5, 6]
        self.edge_owner=[((0,0), (0,0))]  #格式：（（边向量起点所属顶点），（边向量终点所属顶点））

    def addPiece(self, piece: Piece, longer_piece_edge: bool, into_idx: int = 0, from_idx: int = 0):
        '''
        Add piece to node.
        !!Unfinished!!

        :param piece: the piece to add
        :return: None
        '''
        _node_edge_count = self.getEdgeCount()
        if _node_edge_count == 0:
            _node_edge_count = 1
            longer_piece_edge = True  # 强制改变，因为初始情况必须要True才能正常添加
        into_idx = into_idx % _node_edge_count
        from_idx = from_idx % piece.getEdgeCount()
        _into = into_idx
        original_node_edge_owner = self.edge_owner[(into_idx - 1) % _node_edge_count]
        _skip_head = False
        _skip_tail = False
        if _node_edge_count != 1:
            if piece.q_object.at(from_idx) == self.q_object.at((into_idx - 1) % _node_edge_count):
                _skip_head = True
                self.edge_owner[(into_idx - 1) % _node_edge_count] = ((piece.number, from_idx), (piece.number, from_idx))
            elif longer_piece_edge:
                self.edge_owner[(into_idx - 1) % _node_edge_count] = ((piece.number, (from_idx-1) % piece.getEdgeCount()),
                                                                      (piece.number, (from_idx-1) % piece.getEdgeCount()))
            if piece.q_object.at((from_idx - 1) % piece.getEdgeCount()) == self.q_object.at(into_idx):
                _skip_tail = True
        for i in range(from_idx, from_idx + piece.getEdgeCount()):
            if not (i == from_idx and _skip_head) and not (i == from_idx + piece.getEdgeCount() - 1 and _skip_tail):
                _piece_edge_no = i % piece.getEdgeCount()
                self.q_object.insert(
                    _into, piece.q_object.at(_piece_edge_no)
                )
                if not _skip_tail and i==(from_idx + piece.getEdgeCount()-1) and not longer_piece_edge:
                    self.edge_owner.insert(_into, original_node_edge_owner)
                    continue
                #previous_node_edge = (_into-1) % _node_edge_count
                #self.edge_owner[previous_node_edge][-1] = (piece.number, _piece_edge_no)
                self.edge_owner.insert(_into, ((piece.number, _piece_edge_no), (piece.number, _piece_edge_no)) )

                _into += 1

        if _node_edge_count == 1:
            self.edge_owner.pop()  #初始化时的0,0搞不掉，只能手动pop了
        self.pieces.append(deepcopy(piece))

    def paint(self, scene: QGraphicsScene):
        for item in self.pieces:
            _handle=scene.addPolygon(item.q_object)
            item.setBrush(_handle)
            self.scene_item_handle = []
            self.scene_item_handle.append(_handle)

    def clearPoly(self, scene: QGraphicsScene):
        for i in self.scene_item_handle:
            scene.removeItem(i)
            self.scene_item_handle.pop()

    def reduce(self, view: QGraphicsView):
        _node_edge_count = self.getEdgeCount() - 1
        while _node_edge_count >= 0:
            _current_edge = self.getEdge(view, _node_edge_count)
            _previous_edge = self.getEdge(view, (_node_edge_count - 1) % self.getEdgeCount())
            angle = _current_edge.angleTo(_previous_edge)
            if round(angle) == 0 or round(angle) == 180:
                self.q_object.remove(_node_edge_count)
                _num, _edge = self.edge_owner[_node_edge_count][-1]
                _prev_num, _prev_old = self.edge_owner[_node_edge_count-1][0]
                self.edge_owner[_node_edge_count-1] = ((_prev_num, _prev_old), (_num, _edge))
                self.edge_owner.pop(_node_edge_count)
            _node_edge_count -= 1
