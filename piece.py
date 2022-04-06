from PySide2.QtCore import QPoint
from PySide2.QtGui import QPolygon, QTransform
from abstract_poly import Poly


class Piece(Poly):
    '''
    Individual piece like "small triangle", "big triangle", etc.
    shape list: L triangle (L size), M triangle, S triangle, square, parallelogram
    '''

    def __init__(self, shape: int):
        super(Piece, self).__init__()
        '''
        shape: range, from 0 to 4
        :param shape:
        '''
        self.shape = shape
        temp_list = []
        if shape == 0:
            # L triangle
            self.edgeCount = 3
            temp_list = [QPoint(0, 0), QPoint(-200, 200), QPoint(200, 200)]
        elif shape == 1:
            self.edgeCount = 3
            temp_list = [QPoint(0, 0), QPoint(0, 200), QPoint(200, 200)]
        elif shape == 2:
            self.edgeCount = 3
            temp_list = [QPoint(0, 0), QPoint(-100, 100), QPoint(100, 100)]
        elif shape == 3:
            self.edgeCount = 4
            temp_list = [QPoint(0, 0), QPoint(-100, 100), QPoint(0, 200), QPoint(100, 100)]
        elif shape == 4:
            self.edgeCount = 4
            temp_list = [QPoint(0, 0), QPoint(200, 0), QPoint(300, -100), QPoint(100, -100)]
        else:
            NotImplementedError()
        self.q_object.append(temp_list)

    def getEdgeCount(self, reduced=False):
        '''
        获取可用的边数，默认返回所有可用边数

        :param reduced: 是否去掉重复的情况（用于piece姿态枚举）
        :return:
        '''
        if reduced:
            if self.shape == 3:
                return 1
            if self.shape == 4:
                return 2
        return len(self.q_object.toList())

    def isFlippable(self):
        return self.shape == 4

    def flip(self):
        temp_list = [QPoint(0, 0), QPoint(200, 0), QPoint(100, -100), QPoint(-100, -100)]
        self.q_object=QPolygon()
        self.q_object.append(temp_list)
