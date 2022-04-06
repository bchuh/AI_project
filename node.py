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

    def addPiece(self, piece: Piece, into_idx: int = 0, from_idx: int = 0):
        '''
        Add piece to node.
        !!Unfinished!!

        :param piece: the piece to add
        :return: None
        '''
        _node_edge_count = self.getEdgeCount()
        if _node_edge_count == 0:
            _node_edge_count = 1
        into_idx = into_idx % _node_edge_count
        from_idx = from_idx % piece.getEdgeCount()
        _into = into_idx
        _skip_head = False
        _skip_tail = False
        if _node_edge_count != 1:
            _ = piece.q_object.at(from_idx)
            __ = self.q_object.at((into_idx - 1) % _node_edge_count)
            if piece.q_object.at(from_idx) == self.q_object.at((into_idx - 1) % _node_edge_count):
                _skip_head = True
            if piece.q_object.at((from_idx - 1) % piece.getEdgeCount()) == self.q_object.at(into_idx):
                _skip_tail = True
        for i in range(from_idx, from_idx + piece.getEdgeCount()):
            if not (i == from_idx and _skip_head) and not (i == from_idx + piece.getEdgeCount() - 1 and _skip_tail):
                self.q_object.insert(
                    _into, piece.q_object.at(i % piece.getEdgeCount())
                )
                _into += 1
        self.pieces.append(deepcopy(piece))

    def paint(self, scene: QGraphicsScene):
        for item in self.pieces:
            self.scene_item_handle = []
            self.scene_item_handle.append(scene.addPolygon(item.q_object))

    def clearPoly(self, scene: QGraphicsScene):
        for i in self.scene_item_handle:
            scene.removeItem(i)
            self.scene_item_handle.pop()

    def reduce(self, view: QGraphicsView):
        _node_edge_count = self.getEdgeCount() - 1
        while _node_edge_count >= 0:
            _current_edge = self.getEdge(view, _node_edge_count)
            _previous_edge = self.getEdge(view, _node_edge_count - 1)
            angle = _current_edge.angleTo(_previous_edge)
            if round(angle) == 0 or round(angle) == 180:
                self.q_object.remove(_node_edge_count)
            _node_edge_count -= 1
