from PySide2.QtCore import QPoint
from PySide2.QtGui import QPolygon
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
            temp_list = [QPoint(0, 0), QPoint(0, 200), QPoint(300, -100), QPoint(100, -100)]
        else:
            NotImplementedError()
        super(Piece, self).append(temp_list)


