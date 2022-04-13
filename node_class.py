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
        #self.edge_owner = [((0, 0), (0, 0))]  # 格式：（（边向量起点所属顶点），（边向量终点所属顶点））
        #self.matrix = np.zeros((7, 7), dtype=int)
        self.piece_matrix = np.ones((7, 8), dtype=int)
        #self.vertex_matrix = np.ones((7, 7, 2), dtype=int)
        self.parent_ID=0
        self.ID=0
    def addPiece(self, piece: Piece, longer_piece_edge: bool, is_original_edge :bool = True, into_idx: int = 0, from_idx: int = 0, i: int = 0):
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
        #original_node_edge_owner = self.edge_owner[(into_idx - 1) % _node_edge_count]
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
        #has_same_vertex = self.hasSameVertix(original_node_edge_owner)
       #self.updateMatrix(piece, into_idx, from_idx, _skip_head, _skip_tail, is_original_edge, has_same_vertex, i, is_initial, piece.flipped)
        self.updateCoordMatrix(piece)
        '''if _node_edge_count != 1:
            if _skip_head:
                self.edge_owner[(into_idx - 1) % _node_edge_count] = (
                    (piece.number, flip_marker * (from_idx + 1)), (piece.number, flip_marker * (from_idx + 1)))
            elif longer_piece_edge:
                self.edge_owner[(into_idx - 1) % _node_edge_count] = (
                    (piece.number, flip_marker * (1 + (from_idx - 1) % piece.getEdgeCount())),
                    (piece.number, flip_marker * (1 + (from_idx - 1) % piece.getEdgeCount())))
            else:
                _original = self.edge_owner[(into_idx - 1) % _node_edge_count]
                self.edge_owner[(into_idx - 1) % _node_edge_count] = (_original[0], _original[0])'''

        for i in range(from_idx, from_idx + piece.getEdgeCount()):
            if not (i == from_idx and _skip_head) and not (i == from_idx + piece.getEdgeCount() - 1 and _skip_tail):
                _piece_edge_no = i % piece.getEdgeCount()
                self.q_object.insert(
                    _into, piece.q_object.at(_piece_edge_no)
                )
                if not _skip_tail and i == (from_idx + piece.getEdgeCount() - 1) and not longer_piece_edge:
                    #self.edge_owner.insert(_into, (original_node_edge_owner[1], original_node_edge_owner[1]))
                    continue
                # previous_node_edge = (_into-1) % _node_edge_count
                # self.edge_owner[previous_node_edge][-1] = (piece.number, _piece_edge_no)
                '''self.edge_owner.insert(_into, (
                    (piece.number, flip_marker * (1 + _piece_edge_no)),
                    (piece.number, flip_marker * (1 + _piece_edge_no))))'''

                _into += 1

        '''if _node_edge_count == 1:
            self.edge_owner.pop()  # 初始化时的0,0搞不掉，只能手动pop了'''
        self.pieces.append(deepcopy(piece))

    def updateMatrix(self, piece: Piece, into_idx: int, from_idx: int,
                     connect_head: bool, connect_tail: bool, is_original_edge :bool, has_same_vertex :bool, i,  initialize=False, piece_filpped=False):
        if initialize:
            return

        _node_edge_count = self.getEdgeCount()
        if piece_filpped == True:
            flip_marker = -1
        else:
            flip_marker = 1
        from_idx = (from_idx-1) % piece.getEdgeCount()  # 找回0~2表示下的出发点号码
        from_idx += 1  #转为1~3表述

        if connect_head and connect_tail and not is_original_edge and has_same_vertex:
            if i==0:
                mark_head=True
                mark_tail=False
            if i==1:
                mark_head=False
                mark_tail=True
        else:
            mark_head = True
            mark_tail = True
        if connect_head:
            _N_info = self.edge_owner[into_idx - 1][0]
            _p_info = (piece.number, flip_marker*from_idx)
            self.matrix[_N_info[0]][_p_info[0]] = _N_info[1]
            self.matrix[_p_info[0]][_N_info[0]] = _p_info[1]
            connection_point = self.q_object.at((into_idx - 1) % _node_edge_count)
            if mark_head:
                self.vertex_matrix[_N_info[0]][_p_info[0]] = [connection_point.x(), connection_point.y()]
                self.vertex_matrix[_p_info[0]][_N_info[0]] = [connection_point.x(), connection_point.y()]

        if connect_tail:
            _connect2 = False
            if connect_head and is_original_edge:
                a = 100
                self.vertex_matrix[_N_info[0]][_p_info[0]] = [1, 1]  #完全连接不计连接点
                self.vertex_matrix[_p_info[0]][_N_info[0]] = [1, 1]
            else:

                a = 1
                _N_info = self.edge_owner[into_idx - 1][1]
                _p_info = (piece.number, flip_marker * from_idx)
                connection_point = self.q_object.at(into_idx)
                if mark_tail:
                    self.vertex_matrix[_N_info[0]][_p_info[0]] = [connection_point.x(), connection_point.y()]
                    self.vertex_matrix[_p_info[0]][_N_info[0]] = [connection_point.x(), connection_point.y()]
            _N_info = self.edge_owner[into_idx - 1][1]
            _p_info = (piece.number, flip_marker*from_idx)
            self.matrix[_N_info[0]][_p_info[0]] = a*_N_info[1]
            self.matrix[_p_info[0]][_N_info[0]] = a*_p_info[1]



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

    def reduce(self, view: QGraphicsView, exampler_pieces: list, last_cand :int):
        _node_edge_count = self.getEdgeCount() - 1
        while _node_edge_count >= 0:
            _current_edge = self.getEdge(view, _node_edge_count)
            _previous_edge = self.getEdge(view, (_node_edge_count - 1) % self.getEdgeCount())
            angle = _current_edge.angleTo(_previous_edge)
            if round(angle) == 0 or round(angle) == 180:
                #connection_point = self.q_object.at(_node_edge_count)
                self.q_object.remove(_node_edge_count)

                if angle == 180:
                    '''
                    connect = False
                    connect_full = False
                    if self.hasSameVertix(self.edge_owner[_node_edge_count]) and \
                        self.hasSameVertix(self.edge_owner[_node_edge_count-1]):
                        if self.isOriginalPieceEdge(self.edge_owner[_node_edge_count], exampler_pieces, _current_edge) and \
                            self.isOriginalPieceEdge(self.edge_owner[_node_edge_count-1], exampler_pieces, _previous_edge):
                            connect = True
                    elif self.isEqualOriginalPieceEdge(self.edge_owner[_node_edge_count][0], exampler_pieces, _previous_edge) or \
                            self.isEqualOriginalPieceEdge(self.edge_owner[_node_edge_count-1][1], exampler_pieces,
                                                          _current_edge):
                            connect_full = True

                    _N_info1 = self.edge_owner[_node_edge_count][-1]
                    _N_info2 = self.edge_owner[_node_edge_count-1][0]  # 可能会有[-1]，不过python问题不大
                    if connect:
                        self.vertex_matrix[_N_info1[0]][_N_info2[0]] = [connection_point.x(), connection_point.y()]
                        self.vertex_matrix[_N_info2[0]][_N_info1[0]] = [connection_point.x(), connection_point.y()]
                        self.matrix[_N_info1[0]][_N_info2[0]] = _N_info1[1]
                        self.matrix[_N_info2[0]][_N_info1[0]] = _N_info2[1]
                    if connect_full:  # 短边和长边一部分上的图形全连接
                        _N_info1 = self.edge_owner[_node_edge_count][0]
                        _N_info2 = self.edge_owner[_node_edge_count - 1][-1]
                        self.vertex_matrix[_N_info1[0]][_N_info2[0]] = [1,1]
                        self.vertex_matrix[_N_info2[0]][_N_info1[0]] = [1,1]
                        self.matrix[_N_info1[0]][_N_info2[0]] = 100*_N_info1[1]
                        self.matrix[_N_info2[0]][_N_info1[0]] = 100*_N_info2[1]'''


                    _prev_temp=(_node_edge_count-1)%self.getEdgeCount()
                    if self.q_object.at(
                            _prev_temp
                    )==self.q_object.at(_node_edge_count):
                        '''
                        _N_info1 = self.edge_owner[_node_edge_count][-1]
                        _N_info2 = self.edge_owner[_node_edge_count - 1][0]  # 可能会有[-1]，不过python问题不大
                        connection_point = self.q_object.at(_prev_temp)
                        self.vertex_matrix[_N_info1[0]][_N_info2[0]] = [connection_point.x(), connection_point.y()]
                        self.vertex_matrix[_N_info2[0]][_N_info1[0]] = [connection_point.x(), connection_point.y()]
                        if connect:
                            a = 100  #用100重新标
                            self.vertex_matrix[_N_info1[0]][_N_info2[0]] = [0, 0]
                            self.vertex_matrix[_N_info2[0]][_N_info1[0]] = [0, 0]
                        else:
                            a = 1
                        self.matrix[_N_info1[0]][_N_info2[0]] = a * _N_info1[1]
                        self.matrix[_N_info2[0]][_N_info1[0]] = a * _N_info2[1]
                        '''
                        self.q_object.remove(_prev_temp)
                        '''
                        self.edge_owner.pop(_node_edge_count)
                        self.edge_owner.pop(_prev_temp)
                        '''
                        _node_edge_count-=1
                        continue
                    '''elif _current_edge.length() > _previous_edge.length():
                        _num, _edge = self.edge_owner[_node_edge_count][-1]
                        self.edge_owner[_node_edge_count - 1] = ((_num, _edge), (_num, _edge))
                        self.edge_owner.pop(_node_edge_count)
                        _node_edge_count-=1
                        continue'''
                '''_num, _edge = self.edge_owner[_node_edge_count][-1]
                _prev_num, _prev_old = self.edge_owner[_node_edge_count - 1][0]
                self.edge_owner[_node_edge_count - 1] = ((_prev_num, _prev_old), (_num, _edge))
                self.edge_owner.pop(_node_edge_count)'''

            _node_edge_count -= 1

    def encodeMatrix(self):
        #mat = self.reorganizeMatrix()
        mat = self.reorgPieceMat()
        return tuple([tuple(e) for e in mat])

    def reorganizeMatrix(self):
        matrix = deepcopy(self.matrix)
        vertex_matrix = deepcopy(self.vertex_matrix)
        swap_L_tri = False
        swap_S_tri = False
        _L_done = False
        _S_done = False
        first_square_edge=0
        for i in range(7):
            if not _L_done:
                if matrix[0][i] > matrix[1][i]:
                    swap_L_tri = True
                    break
                elif matrix[0][i] < matrix[1][i]:
                    break
        if swap_L_tri:
            matrix[[0, 1], :] = matrix[[1, 0], :]
            matrix[:, [0, 1]] = matrix[:, [1, 0]]
            vertex_matrix[[0, 1], :] = vertex_matrix[[1, 0], :]
            vertex_matrix[:, [0, 1], :] = vertex_matrix[:, [1, 0], :]

        for i in range(7):
            if not _S_done:
                if matrix[3][i] > matrix[4][i]:
                    swap_S_tri = True
                    break
                elif matrix[3][i] < matrix[4][i]:
                    break
        if swap_S_tri:
            matrix[[3, 4], :] = matrix[[4, 3], :]
            matrix[:, [3, 4]] = matrix[:, [4, 3]]
            vertex_matrix[[3, 4], :] = vertex_matrix[[4, 3], :]
            vertex_matrix[:, [3, 4], :] = vertex_matrix[:, [4, 3], :]
        for i in range(7):
            if matrix[5][i] > 0:
                if matrix[5][i]<10:
                    scale=1
                elif matrix[5][i]<100:
                    scale=10
                elif matrix[5][i]<1000:
                    scale=100
                else:
                    NotImplementedError()
                matrix[5][i] = matrix[5][i] // scale
                if first_square_edge == 0:
                    first_square_edge = matrix[5][i]
                matrix[5][i] = (matrix[5][i]-1 - (first_square_edge-1)) % 4 + 1
                matrix[5][i] = matrix[5][i] * scale
        result = np.concatenate((matrix, vertex_matrix.reshape((14,7))), axis=0)
        return result

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
    def isEqualOriginalPieceEdge(self, edge_tup, exampler_pieces, edge :QLineF):
        num, edge_no = edge_tup
        piece: Piece = exampler_pieces[num]
        if edge_no<0:
            edge_no = -1*edge_no
        edge_no-=1
        original_length = piece.edge_length[edge_no]
        if round(edge.length()) == round(original_length):
            return True
        else:
            return False

    def isComboOfOriginalPieceEdge(self, edge_tup_of_tup, exampler_pieces, edge :QLineF):
        '''
        If is the combination of 2 origianl piece edge noted by edge_tupe_of_tupe
        :param edge_tup_of_tup:
        :param exampler_pieces:
        :param edge:
        :return:
        '''
        '''num1, edge_no1 = edge_tup_of_tup[0]
        num2, edge_no2 = edge_tup_of_tup[1]
        piece1: Piece = exampler_pieces[num1]
        piece2: Piece = exampler_pieces[num2]
        if edge_no1<0:
            edge_no1 = -1*edge_no1
        edge_no1-=1
        if edge_no2<0:
            edge_no2 = -1*edge_no2
        edge_no2-=1
        original_length1 = piece1.edge_length[edge_no1]
        original_length2 = piece2.edge_length[edge_no2]
        if round(edge.length()) == round(original_length1+original_length2):
            return True
        else:
            return False'''
        return True #函数暂时无用

    def updateCoordMatrix(self, piece:Piece):
        num = piece.number
        point1 = piece.q_object.at(0)
        point2 = piece.q_object.at(1)
        if num != 5:
            self.piece_matrix[num][0:4] = [point1.x(), point1.y(), point2.x(), point2.y()]
        else:
            for i in range(4):
                point = piece.q_object.at(i)
                self.piece_matrix[num][(2*i):(2*(i+1))] = [point.x(), point.y()]

    def reorgPieceMat(self):
        mat = deepcopy(self.piece_matrix)
        max = (-1, -1, -1)
        swap_L_tri = False
        swap_S_tri = False
        _L_done = False
        _S_done = False
        for i in range(4):
            if not _L_done:
                _L_done = True
                if mat[0][2*i] > mat[1][2*i]:
                    swap_L_tri = True
                elif mat[0][2*i] == mat[1][2*i]:
                    if mat[0][2*i+1] > mat[1][2*i+1]:
                        swap_L_tri = True
                    elif mat[0][2*i+1] == mat[1][2*i+1]:
                        _L_done = False
            if not _S_done:
                _S_done = True
                if mat[3][2*i] > mat[4][2*i]:
                    swap_S_tri = True
                elif mat[3][2*i] == mat[4][2*i]:
                    if mat[3][2*i+1] > mat[4][2*i+1]:
                        swap_S_tri = True
                    elif mat[3][2*i+1] == mat[4][2*i+1]:
                        _S_done = False
            current = mat[5][(2*i):(2*(i+1))]
            if current[0]>max[0]:
                max = (current[0], current[1], i)
            elif current[0]==max[0]:
                if current[1]>max[1]:
                    max = (current[0], current[1], i)
        index = max[2]
        if index>0:
            mat[5] = np.concatenate((mat[5][index:8], mat[5][0:index]))
        if swap_L_tri:
            mat[[0, 1], :] = mat[[1, 0], :]
        if swap_S_tri:
            mat[[3, 4], :] = mat[[3, 4], :]
        return mat










