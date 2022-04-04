from PySide2.QtCore import QPoint
from PySide2.QtGui import QPolygon
from abstract_poly import Poly
from piece import Piece


class Node(Poly):
    '''
    Collection of pieces, also represent current state
    - useful parent methods: united(), indexOf(), intersected(), toList
    '''

    def __init__(self):
        super(Node, self).__init__()
        self.pieces = []
        self.edge_count = 0
        self.next_step = 0

    def addPiece(self, piece: Piece):
        '''
        Add piece to node.
        !!Unfinished!!

        :param piece: the piece to add
        :return: None
        '''
        super(Node, self).append(piece.toList())  # 添加顶点
        self.pieces.append(piece)
        self.next_step += 1  # 接下来是第几块拼图
