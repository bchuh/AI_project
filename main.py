import os

from PySide2.QtCore import QPoint, QLineF, QPointF, QTime, QCoreApplication, QEventLoop, Qt
from PySide2.QtWidgets import QApplication, QMainWindow, QGraphicsView, QGraphicsScene
from PySide2.QtGui import QPolygon, QTransform
from node import Node
from piece import Piece
from copy import deepcopy
import pickle


# 序列化
def serialize_instance(obj):
    d = {'__classname__': type(obj).__name__}
    d.update(vars(obj))
    return d


# 反序列化
def unserialize_object(d):
    clsname = d.pop('__classname__', None)
    if clsname:
        # 需要改进的地方，定义类；也可以通过getattr创建对象
        cls = Node
        obj = cls.__new__(cls)
        for key, value in d.items():
            setattr(obj, key, value)
        return obj
    else:
        return None


def save_node(node: Node, file_name: str):
    _path = os.getcwd()
    _name = file_name + '.node'
    _path = os.path.join(_path, _name)
    with open(_name, 'wb') as f:
        pickle.dump(node, f)


def load_node(file_name: str):
    '''
    load node class from .json

    :param file_name: name, with out '.json' suffix
    :return: Node object
    '''

    _path = os.getcwd()
    _name = file_name + '.node'
    _path = os.path.join(_path, _name)
    with open(_path, 'rb') as f:
        node = pickle.load(f)

    ### Debug
    app = QApplication([])
    view = QGraphicsView()
    scene = QGraphicsScene()
    view.setScene(scene)
    node.paint(scene)
    view.repaint()
    view.showMaximized()
    app.exec_()
    ###
    return node

if __name__ == "__main__":
    app = QApplication([])
    view = QGraphicsView()
    scene = QGraphicsScene()
    view.setScene(scene)
    view.show()
    view.showMaximized()

    scale_factor = 1
    view.scale(scale_factor, scale_factor)
    #view.hide()
    stack = []
    result_list = []
    shape_list = [0, 0, 1, 2, 2, 3, 4]  # shape ID of 7 pieces

    iter_count = 0
    _node = Node()
    _node.addPiece(
        Piece(shape_list[_node.candidates.pop(2)])
    )
    stack.append(_node)

    while len(stack) != 0:
        _const_parent_node = stack.pop()
        candidates = _const_parent_node.candidates
        print("Node expand:")
        print("#result: ", len(result_list))
        if len(candidates) == 0:
            # Debug
            '''view.show()
            _const_parent_node.paint(scene)
            view.repaint()
            dieTime = QTime.currentTime().addMSecs(10)
            while (QTime.currentTime() < dieTime):
                QCoreApplication.processEvents(QEventLoop.AllEvents, 20)
            _const_parent_node.clearPoly(scene)
            scene.clear()  # not working for some reason
            view.update()
            '''
            #
            iter_count += 1  # 第几个组合

            if _const_parent_node.getEdgeCount() == 5:
                result_list.append(_const_parent_node)
                # Debug
                '''
                view.show()
                _const_parent_node.paint(scene)
                view.repaint()
                dieTime = QTime.currentTime().addMSecs(800)
                while (QTime.currentTime() < dieTime):
                    QCoreApplication.processEvents(QEventLoop.AllEvents, 20)
                _const_parent_node.clearPoly(scene)
                scene.clear()  # not working for some reason
                view.update()
                view.hide()'''


                #save_node(_const_parent_node, str(iter_count))
            continue
        skip_L_tri = False
        skip_S_tri = False
        for cand_no in range(len(candidates)):
            # print("Len(candidates):", len(candidates))
            # 开始创建新的子节点， 不需要深拷贝因为这是父节点
            _parent_node = deepcopy(_const_parent_node)
            _cand = _parent_node.candidates.pop(cand_no)  # _cand是指第几号拼图，是shape_list的某个位置下标
            _exampler_piece = Piece(shape_list[_cand])  # piece样品，跟本次迭代中创建的piece一模一样，只是为了方便查看形状的边长而存在
            if _cand == 0 and skip_L_tri:
                continue
            if _cand == 2 and skip_S_tri:
                continue
            if _cand == 0:
                skip_L_tri = True
            if _cand == 2:
                skip_S_tri = True
            if _exampler_piece.isFlippable():
                _flip_loop = 2
            else:
                _flip_loop = 1
            for flip_count in range(_flip_loop):
                if flip_count == 1:
                    _exampler_piece.flip()
                for node_edge_no in range(_parent_node.getEdgeCount()):
                    for piece_edge_no in range(_exampler_piece.getEdgeCount(reduced=True)):

                        # TODO: 非等长边相接
                        # TODO: 检查重复
                        # TODO：平行四边形之类改为只有两种旋转情况
                        # TODO: 检查边数
                        # TODO: 检查组合体内角判断两组合体是否外形一样

                        _node_edge = _parent_node.getEdge(view, node_edge_no, True)
                        _piece_edge = _exampler_piece.getEdge(view, piece_edge_no)
                        if len(candidates) == 6:  # 若为第二块，加入剪枝
                            _ = round(_node_edge.length())
                            __ = round(_piece_edge.length())
                            if _node_edge.length() != (2 * _piece_edge.length()) and \
                                    (2 * _node_edge.length()) != _piece_edge.length() and \
                                    round(_node_edge.length()) != round(_piece_edge.length()):
                                continue

                        if round(_node_edge.length()) == round(_piece_edge.length()):
                            _loop_count = 1
                        else:
                            _loop_count = 2

                        for i in range(_loop_count):
                            _node = deepcopy(_parent_node)
                            _piece = deepcopy(_exampler_piece)  # create a new one instead of sharing
                            _node_edge = _node.getEdge(view, node_edge_no, True)
                            _piece_edge = _piece.getEdge(view, piece_edge_no)
                            # 开始旋转
                            angle = _piece_edge.angleTo(_node_edge)
                            trans = QTransform()
                            trans.rotate(360 - angle)
                            _piece.q_object = trans.map(_piece.q_object)
                            # 因为旋转改变了坐标，要再获取一次
                            _node_edge = _node.getEdge(view, node_edge_no, True)
                            _piece_edge = _piece.getEdge(view, piece_edge_no)
                            if i == 0:
                                _piece.q_object.translate(
                                    -scale_factor * (_piece_edge.p1() - _node_edge.p1()).toPoint()
                                )
                            else:
                                _piece.q_object.translate(
                                    -scale_factor * (_piece_edge.p2() - _node_edge.p2()).toPoint()
                                )
                            if _piece.q_object.intersected(_node.q_object).length() == 0:  # 检查有无非法重叠
                                _node.addPiece(_piece, node_edge_no + 1,
                                               piece_edge_no + 1)  # addPiece会对piece做deepcopy，所以这里不需要
                                _node.reduce(view)
                                if len(_node.candidates) <= 2 and _node.getEdgeCount() > 9:  # 因为最后一块填进去最多消除2条边，倒数第二块填进去最多消除
                                    continue
                                ### debug

                                _node.paint(scene)
                                view.repaint()
                                dieTime = QTime.currentTime().addMSecs(30)
                                while (QTime.currentTime() < dieTime):
                                    QCoreApplication.processEvents(QEventLoop.AllEvents, 20)
                                _node.clearPoly(scene)
                                scene.clear()  # not working for some reason
                                view.update()

                                ###
                                stack.append(_node)

    app.exec_()

