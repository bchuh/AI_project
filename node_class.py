from PySide2.QtCore import QPoint, QLineF
from PySide2.QtGui import QPolygon
from PySide2.QtWidgets import QGraphicsScene, QGraphicsView

from abstract_poly import Poly
from piece import Piece
from copy import deepcopy
import numpy as np


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
        self.edge_owner = [((0, 0), (0, 0))]  # 格式：（（边向量起点所属顶点），（边向量终点所属顶点））
        self.matrix = np.zeros((7, 7), dtype=int)
        self.parent_ID=0
        self.ID=0
    def addPiece(self, piece: Piece, longer_piece_edge: bool, into_idx: int = 0, from_idx: int = 0):
        '''
        Add piece to node.
        !!Unfinished!!

        :param piece: the piece to add
        :return: None
        '''
        _node_edge_count = self.getEdgeCount()
        is_initial = False
        if _node_edge_count == 0:
            _node_edge_count = 1
            is_initial = True
            longer_piece_edge = True  # 强制改变，因为初始情况必须要True才能正常添加
        into_idx = into_idx % _node_edge_count
        from_idx = from_idx % piece.getEdgeCount()
        _into = into_idx
        original_node_edge_owner = self.edge_owner[(into_idx - 1) % _node_edge_count]
        _skip_head = False
        _skip_tail = False

        if piece.flipped:
            flip_marker = -1
        else:
            flip_marker = 1

        if _node_edge_count != 1:
            if piece.q_object.at(from_idx) == self.q_object.at((into_idx - 1) % _node_edge_count):
                _skip_head = True
            if piece.q_object.at((from_idx - 1) % piece.getEdgeCount()) == self.q_object.at(into_idx):
                _skip_tail = True

        self.updateMatrix(piece, into_idx, from_idx, _skip_head, _skip_tail, is_initial)

        if _node_edge_count != 1:
            if _skip_head:
                self.edge_owner[(into_idx - 1) % _node_edge_count] = (
                    (piece.number, flip_marker * (from_idx + 1)), (piece.number, flip_marker * (from_idx + 1)))
            elif longer_piece_edge:
                self.edge_owner[(into_idx - 1) % _node_edge_count] = (
                    (piece.number, flip_marker * (1 + (from_idx - 1) % piece.getEdgeCount())),
                    (piece.number, flip_marker * (1 + (from_idx - 1) % piece.getEdgeCount())))
            else:
                _original = self.edge_owner[(into_idx - 1) % _node_edge_count]
                self.edge_owner[(into_idx - 1) % _node_edge_count] = (_original[0], _original[0])

        for i in range(from_idx, from_idx + piece.getEdgeCount()):
            if not (i == from_idx and _skip_head) and not (i == from_idx + piece.getEdgeCount() - 1 and _skip_tail):
                _piece_edge_no = i % piece.getEdgeCount()
                self.q_object.insert(
                    _into, piece.q_object.at(_piece_edge_no)
                )
                if not _skip_tail and i == (from_idx + piece.getEdgeCount() - 1) and not longer_piece_edge:
                    self.edge_owner.insert(_into, (original_node_edge_owner[1], original_node_edge_owner[1]))
                    continue
                # previous_node_edge = (_into-1) % _node_edge_count
                # self.edge_owner[previous_node_edge][-1] = (piece.number, _piece_edge_no)
                self.edge_owner.insert(_into, (
                    (piece.number, flip_marker * (1 + _piece_edge_no)),
                    (piece.number, flip_marker * (1 + _piece_edge_no))))

                _into += 1

        if _node_edge_count == 1:
            self.edge_owner.pop()  # 初始化时的0,0搞不掉，只能手动pop了
        self.pieces.append(deepcopy(piece))

    def updateMatrix(self, piece: Piece, into_idx: int, from_idx: int,
                     connect_head: bool, connect_tail: bool, initialize=False, piece_filpped=False):
        if initialize:
            return
        if piece_filpped == True:
            flip_marker = -1
        else:
            flip_marker = 1
        from_idx = (from_idx-1) % piece.getEdgeCount()  # 找回0~2表示下的出发点号码
        from_idx += 1  #转为1~3表述
        if connect_head:
            _N_info = self.edge_owner[into_idx - 1][0]
            _p_info = (piece.number, flip_marker*from_idx)
            self.matrix[_N_info[0]][_p_info[0]] = _N_info[1]
            self.matrix[_p_info[0]][_N_info[0]] = _p_info[1]
        if connect_tail:
            _N_info = self.edge_owner[into_idx - 1][1]
            _p_info = (piece.number, flip_marker*from_idx)
            self.matrix[_N_info[0]][_p_info[0]] = _N_info[1]
            self.matrix[_p_info[0]][_N_info[0]] = _p_info[1]

    def paint(self, scene: QGraphicsScene):
        for item in self.pieces:
            _handle = scene.addPolygon(item.q_object)
            item.setBrush(_handle)
            self.scene_item_handle = []
            self.scene_item_handle.append(_handle)

    def clearPoly(self, scene: QGraphicsScene):
        for i in self.scene_item_handle:
            scene.removeItem(i)
            self.scene_item_handle.pop()

    def reduce(self, view: QGraphicsView, exampler_pieces: list):
        _node_edge_count = self.getEdgeCount() - 1
        while _node_edge_count >= 0:
            _current_edge = self.getEdge(view, _node_edge_count)
            _previous_edge = self.getEdge(view, (_node_edge_count - 1) % self.getEdgeCount())
            angle = _current_edge.angleTo(_previous_edge)
            if round(angle) == 0 or round(angle) == 180:
                self.q_object.remove(_node_edge_count)
                if angle == 180:
                    if self.hasSameVertix(self.edge_owner[_node_edge_count]) and \
                        self.hasSameVertix(self.edge_owner[_node_edge_count-1]) and \
                            self.isOriginalPieceEdge(self.edge_owner[_node_edge_count], exampler_pieces, _current_edge) and \
                            self.isOriginalPieceEdge(self.edge_owner[_node_edge_count-1], exampler_pieces, _previous_edge):
                        connect = True
                    else:
                        connect = False
                    _N_info1 = self.edge_owner[_node_edge_count][-1]
                    _N_info2 = self.edge_owner[_node_edge_count-1][0] #可能会有[-1]，不过python问题不大
                    if connect:
                        self.matrix[_N_info1[0]][_N_info2[0]] = _N_info1[1]
                        self.matrix[_N_info2[0]][_N_info1[0]] = _N_info2[1]
                    _prev_temp=(_node_edge_count-1)%self.getEdgeCount()
                    if self.q_object.at(
                            _prev_temp
                    )==self.q_object.at(_node_edge_count):
                        self.q_object.remove(_prev_temp)
                        self.edge_owner.pop(_node_edge_count)
                        self.edge_owner.pop(_prev_temp)
                        _node_edge_count-=1
                        continue
                    elif _current_edge.length() > _previous_edge.length():
                        _num, _edge = self.edge_owner[_node_edge_count][-1]
                        self.edge_owner[_node_edge_count - 1] = ((_num, _edge), (_num, _edge))
                        self.edge_owner.pop(_node_edge_count)
                        _node_edge_count-=1
                        continue
                _num, _edge = self.edge_owner[_node_edge_count][-1]
                _prev_num, _prev_old = self.edge_owner[_node_edge_count - 1][0]
                self.edge_owner[_node_edge_count - 1] = ((_prev_num, _prev_old), (_num, _edge))
                self.edge_owner.pop(_node_edge_count)

            _node_edge_count -= 1

    def encodeMatrix(self):
        mat = self.reorganizeMatrix()
        return tuple([tuple(e) for e in mat])

    def reorganizeMatrix(self):
        matrix = deepcopy(self.matrix)
        swap_L_tri = False
        swap_S_tri = False
        _L_done = False
        _S_done = False
        first_square_edge=0
        for i in range(7):
            if not _L_done:
                if matrix[0][i] > matrix[1][i]:
                    swap_L_tri = True
                    _L_done = True
                elif matrix[0][i] < matrix[1][i]:
                    _L_done = True
            if not _S_done:
                if matrix[3][i] > matrix[4][i]:
                    swap_S_tri = True
                    _S_done = True
                elif matrix[3][i] < matrix[4][i]:
                    _S_done = True
            if matrix[5][i] > 0:
                if first_square_edge == 0:
                    first_square_edge = matrix[5][i]
                matrix[5][i] = (matrix[5][i]-1 - (first_square_edge-1)) % 4 + 1
        if swap_L_tri:
            matrix[[0, 1], :] = matrix[[1, 0], :]
            matrix[:, [0, 1]] = matrix[:, [1, 0]]
        if swap_S_tri:
            matrix[[3, 4], :] = matrix[[4, 3], :]
            matrix[:, [3, 4]] = matrix[:, [4, 3]]
        return matrix

    def hasSameVertix(self, edge_tup_of_tup: tuple):
        if edge_tup_of_tup[0] == edge_tup_of_tup[1]:
            return True
        else:
            return False

    def isOriginalPieceEdge(self, edge_tup_of_tup, exampler_pieces, edge :QLineF):
        num, edge_no = edge_tup_of_tup[0]
        piece: Piece = exampler_pieces[num]
        if edge_no<0:
            edge_no = -1*edge_no
        edge_no-=1
        original_length = piece.edge_length[edge_no]
        if round(edge.length()) == round(original_length):
            return True
        else:
            return False


