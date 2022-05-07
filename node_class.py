from PySide2.QtCore import QPoint, QLineF
from PySide2.QtGui import QPolygon
from PySide2.QtWidgets import QGraphicsScene, QGraphicsView

from abstract_poly import Poly
from piece import Piece
from copy import deepcopy
import numpy as np
import math


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
        self.piece_angle = []
        #self.vertex_matrix = np.ones((7, 7, 2), dtype=int)
        self.parent_ID=0
        self.ID=0
        self.piece_angle=[]
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
            #self.scene_item_handle = []
            #self.scene_item_handle.append(_handle)

    def clearPoly(self, scene: QGraphicsScene):
        for i in self.scene_item_handle:
            scene.removeItem(i)
            self.scene_item_handle.pop()

    def reduce(self, view: QGraphicsView, exampler_pieces: list = None, last_cand :int = None):
        _node_edge_count = self.getEdgeCount() - 1
        while _node_edge_count >= 0:
            _current_edge = self.getEdge(view, _node_edge_count)
            _previous_edge = self.getEdge(view, (_node_edge_count - 1) % self.getEdgeCount())
            angle = _current_edge.angleTo(_previous_edge)
            if round(angle) == 0 or round(angle) == 180 or round(angle) == 360:
                #connection_point = self.q_object.at(_node_edge_count)
                self.q_object.remove(_node_edge_count)

                if angle == 180:
                    _prev_temp=(_node_edge_count-1)%self.getEdgeCount()
                    if self.q_object.at(
                            _prev_temp
                    )==self.q_object.at(_node_edge_count):
                        self.q_object.remove(_prev_temp)
                        _node_edge_count-=1
                        continue
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
                    raise NotImplementedError()
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
        if num < 5:
            self.piece_matrix[num][0:4] = [point1.x(), point1.y(), point2.x(), point2.y()]
        else:
            for i in range(4):
                point = piece.q_object.at(i)
                self.piece_matrix[num][(2*i):(2*(i+1))] = [point.x(), point.y()]

    def reorgPieceMat(self):
        mat = deepcopy(self.piece_matrix)
        max = (-1000, -1000, -1)
        max_parall = (-1000, -1000, -1)
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
            current_parall = mat[6][(2*i):(2*(i+1))]
            if current[0]>max[0]:
                max = (current[0], current[1], 2*i)
            elif current[0]==max[0]:
                if current[1]>max[1]:
                    max = (current[0], current[1], 2*i)

            if current_parall[0]>max_parall[0]:
                max_parall = (current_parall[0], current_parall[1], 2*i)
            elif current_parall[0]==max_parall[0]:
                if current_parall[1]>max_parall[1]:
                    max_parall = (current_parall[0], current_parall[1], 2*i)
        index = max[2]
        if index>0:
            mat[5] = np.concatenate((mat[5][index:8], mat[5][0:index]))

        index_parall = max_parall[2]
        if index_parall>0:
            mat[6] = np.concatenate((mat[6][index_parall:8], mat[6][0:index_parall]))

        if swap_L_tri:
            mat[[0, 1], :] = mat[[1, 0], :]
        if swap_S_tri:
            mat[[3, 4], :] = mat[[4, 3], :]
        return mat

    def getAngle(self, view: QGraphicsView):
        self.piece_angle = []
        self.node_edges = []
        for _node_edge_count in range(0, self.getEdgeCount()):
            _current_edge = self.getEdge(view, _node_edge_count, True)
            _next_edge = self.getEdge(view, (_node_edge_count + 1) % self.getEdgeCount(), True)
            _upper = round(_next_edge.length())//10
            _lower = round(_next_edge.length())%10
            if _lower%2 !=0:
                _lower += 1
            _edge_len = _upper*10+_lower
            if _edge_len ==224:
                _edge_len = 226
            self.node_edges.append(
                _edge_len
            )
            _next_edge.setPoints(_next_edge.p2(),_next_edge.p1())
            angle = _next_edge.angleTo(_current_edge)
            self.piece_angle.append(round(angle))


    def reorgAngles(self, do_reverse = False):
        angles = deepcopy(self.piece_angle)
        edges = deepcopy(self.node_edges)
        if do_reverse:
            angles.reverse()
            angles = angles[4:5] + angles[0:4]
            edges.reverse()
        if len(angles) !=5 or len(edges) != 5:
            raise NotImplementedError("condition: if len(angles) !=5 or len(edges) != 5")

        deri_angles = []
        for i in range(len(angles)):
            deri_angles.append(angles[i]-angles[(i+1)%5])
        max_index = np.argwhere(angles == np.amax(angles))
        mix_index = np.argwhere(angles == np.amin(angles))
        if len(max_index) == 1:
            index = max_index[0]
        elif len(mix_index) == 1:
            index = mix_index[0]
        else:
            plain_index = np.argwhere(np.array(deri_angles) == 0.0)
            if len(plain_index) == 1:
                index = plain_index[0]
            else:
                up_index = np.argwhere(deri_angles == np.amin(deri_angles))
                if len(up_index) !=1:
                    raise NotImplementedError(angles)
                index = up_index[0]
        if len(index) != 1:
            raise NotImplementedError()
        else:
            index = np.asscalar(index)
        if index == 0:
            result = angles
            result_edges = edges
        else:
            result = angles[index:5] + angles[0:index]
            result_edges = edges[index:5] + edges[0:index]
        return result, result_edges

    def encodeAngles(self, view):
        self.getAngle(view)
        angles, edges = self.reorgAngles()
        angles_reverse, edges_reverse = self.reorgAngles(do_reverse=True)
        reversed_first = False
        is_same_angle_list = True
        for i in range(len(angles)):
            if angles[i] == angles_reverse[i]:
                continue
            elif angles[i]>angles_reverse[i]:
                reversed_first = True
                is_same_angle_list = False
                break
            else:
                reversed_first = False
                is_same_angle_list = False
                break
        if is_same_angle_list:
            for i in range(len(edges)):
                if edges[i] == edges_reverse[i]:
                    continue
                elif edges[i] > edges_reverse[i]:
                    reversed_first = True
                    break
                else:
                    reversed_first = False
                    break
        if reversed_first:
            return tuple([tuple(angles_reverse), tuple(edges_reverse)])
        else:
            return tuple([tuple(angles), tuple(edges)])

    def getGScore(self):
        return self.getEdgeCount()

    def getHScore(self, factor=-2):
        return factor*len(self.candidates)












