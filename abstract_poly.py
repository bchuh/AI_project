from PySide2.QtCore import QLineF
from PySide2.QtGui import QPolygon
from PySide2.QtWidgets import QGraphicsView


class Poly(QPolygon):
    '''
    Collection of pieces, also represent current state
    - useful parent methods: united(), indexOf(), intersected(), toList
    '''

    def __init__(self):
        super(Poly, self).__init__()
        self.pieces = []
        self.next_step = 0

    def getEdgeCount(self):
        return len(super(Poly, self).toList())

    def getEdge(self, view: QGraphicsView, start_index, reverse=False):
        _edge_count = self.getEdgeCount()
        if reverse == False:
            return QLineF(view.mapToScene(self.at(start_index)),
                          view.mapToScene(self.at(start_index + 1 % _edge_count)))
        else:
            return QLineF(view.mapToScene(self.at(start_index + 1 % _edge_count)),
                          view.mapToScene(self.at(start_index)),)


