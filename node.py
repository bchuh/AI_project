from PySide2.QtCore import QPoint
from PySide2.QtGui import QPolygon
from PySide2.QtWidgets import QGraphicsScene

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

    def addPiece(self, piece: Piece):
        '''
        Add piece to node.
        !!Unfinished!!

        :param piece: the piece to add
        :return: None
        '''
        self.q_object = self.q_object.united(piece.q_object)
        self.pieces.append(deepcopy(piece))

    def paint(self, scene: QGraphicsScene):
        for item in self.pieces:
            self.scene_item_handle = []
            self.scene_item_handle.append(scene.addPolygon(item.q_object))

    def clearPoly(self, scene: QGraphicsScene):
        for i in self.scene_item_handle:
            scene.removeItem(i)
            self.scene_item_handle.pop()
