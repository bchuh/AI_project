from PySide2.QtCore import QLineF
from PySide2.QtGui import QPolygon
from PySide2.QtWidgets import QGraphicsView


class Poly:
    '''
    Collection of pieces, also represent current state
    - useful parent methods: united(), indexOf(), intersected(), toList
    '''

    def __init__(self):
        self.q_object=QPolygon()
        self.pieces = []
        self.next_step = 0

    def getEdgeCount(self):
        return len(self.q_object.toList())

    def getEdge(self, view: QGraphicsView, start_index, reverse=False):
        _edge_count = self.getEdgeCount()
        start_index = start_index % _edge_count
        if view is not None:
            if not reverse :
                line = QLineF(view.mapToScene(self.q_object.at(start_index)),
                              view.mapToScene(self.q_object.at((start_index + 1) % _edge_count)))
            else:
                line = QLineF(view.mapToScene(self.q_object.at((start_index + 1) % _edge_count)),
                              view.mapToScene(self.q_object.at(start_index)))
        else:
            if not reverse :
                line = QLineF(self.q_object.at(start_index),
                              self.q_object.at((start_index + 1) % _edge_count))
            else:
                line = QLineF(self.q_object.at((start_index + 1) % _edge_count),
                              self.q_object.at(start_index))
        return line

