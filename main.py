import os

from PySide2.QtCore import QPoint, QLineF, QPointF, QTime, QCoreApplication, QEventLoop, Qt
from PySide2.QtWidgets import QApplication, QMainWindow, QGraphicsView, QGraphicsScene, QVBoxLayout, QLabel
from PySide2.QtGui import QPolygon, QTransform
from node_class import Node
from piece import Piece
from copy import deepcopy
import pickle
import time
from queue import PriorityQueue
from util import PrioritizedItem

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


def save_node(node: Node, file_name: str, mode:str):
    '''
    保存为 “file_name.node"， 置于”DFS_nodes“ 之类的文件夹中
    :param node:
    :param file_name: 保存的node文件的名字
    :param mode: 必须是"DFS", "BFS", "ASTAR", "GREEDY" 中的一种
    :return:
    '''
    _path = os.getcwd()
    _name = file_name + '.node'
    _folder = mode+"_nodes"
    if not os.path.exists(os.path.join(_path, _folder)):
        os.mkdir(os.path.join(_path, _folder))
    _path = os.path.join(_path, _folder, _name)
    with open(_path, 'wb') as f:
        pickle.dump(node, f)


def load_node(file_name: str, with_suffix_and_absolute_path = False):
    '''
    load node class from .json

    :param file_name: name, with out '.json' suffix
    :param with_suffix: file_name是否带有.node后缀，若无则自动加上该后缀
    :return: Node object
    '''

    _path = os.getcwd()
    if not with_suffix_and_absolute_path:
        _name = file_name + '.node'
        _folder = "nodes"
        _path = os.path.join(_path, _folder)
        _path = os.path.join(_path,  _name)
    else:
        _path = file_name

    with open(_path, 'rb') as f:
        node = pickle.load(f)

    ### Debug
    '''app = QApplication([])
    view = QGraphicsView()
    scene = QGraphicsScene()
    view.setScene(scene)
    node.paint(scene)
    view.repaint()
    view.showMaximized()
    app.exec_()'''
    ###
    return node

def DFSsequence(view: QGraphicsView, scene: QGraphicsScene, result_list: list, shape_list: list, exampler_pieces :list, change_to_BFS=False):
    '''
    DFS 搜索模块（同时BFS模块也依赖该模块）

    :param view:
    :param scene:
    :param result_list:
    :param shape_list:
    :param exampler_pieces:
    :param change_to_BFS: 若为True则pop,push行为改为BFS模式，即queue模式（先进先出)
    :return:
    '''

    start=time.time()
    stack = []
    iter_count = 0
    _node = Node()
    _node.addPiece(
        Piece(shape_list[_node.candidates.pop(2)], 2),
        False
    )

    stack.append(_node)
    id = 0
    while len(stack) != 0:
        # 当前分支号码
        app.processEvents()
        if not change_to_BFS:
            _const_parent_node = stack.pop()
        else:
            _const_parent_node = stack.pop(0)
        candidates = _const_parent_node.candidates

        #-----Debug------------
        '''scene.clear()
        view.update()
        _const_parent_node.paint(scene)
        view.repaint()
        view.show()
        dieTime = QTime.currentTime().addMSecs(50)
        while (QTime.currentTime() < dieTime):
            QCoreApplication.processEvents(QEventLoop.AllEvents, 20)
        '''
        #------------------------------------
        # print("Node expand:")
        # print("#result: ", len(result_list))
        if len(candidates) == 0:
            # Debug
            # view.show
            '''scene.clear()
            view.repaint()
            view.update()
            _const_parent_node.paint(scene)
            view.repaint()
            view.show()
            dieTime = QTime.currentTime().addMSecs(50)
            while (QTime.currentTime() < dieTime):
                QCoreApplication.processEvents(QEventLoop.AllEvents, 20)
            #_const_parent_node.clearPoly(scene)
            #scene.clear()  # not working for some reason
            #view.update()
'''
            #
            iter_count += 1  # 第几个组合
            if _const_parent_node.getEdgeCount() == 5:
                print("#result: ", len(result_list))
                result_list.append(_const_parent_node)
                # Debug
                '''# view.hide()
                # view.show()
                scene.clear()
                view.update()
                _const_parent_node.paint(scene)
                view.repaint()
                view.update()
                encoding = _const_parent_node.encodeMatrix()
                dieTime = QTime.currentTime().addMSecs(1)
                while (QTime.currentTime() < dieTime):
                    QCoreApplication.processEvents(QEventLoop.AllEvents, 20)
                # _const_parent_node.clearPoly(scene)
                # scene.clear()  # not working for some reason
                # view.update()

                #'''
            continue
        skip_L_tri = False
        skip_S_tri = False
        for cand_no in range(len(candidates)):  # debug
            # print("Len(candidates):", len(candidates))
            # 开始创建新的子节点， 不需要深拷贝因为这是父节点
            _parent_node = pickle.loads(pickle.dumps(_const_parent_node))
            _cand = _parent_node.candidates.pop(cand_no)  # _cand是指第几号拼图，是shape_list的某个位置下标
            _exampler_piece = Piece(shape_list[_cand], _cand)  # piece样品，跟本次迭代中创建的piece一模一样，只是为了方便查看形状的边长而存在
            if shape_list[_cand] == 0 and skip_L_tri:
                continue
            if shape_list[_cand] == 2 and skip_S_tri:
                continue
            if shape_list[_cand] == 0:
                skip_L_tri = True
            if shape_list[_cand] == 2:
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
                        _n_edge_len = _node_edge.length()
                        _p_edge_len = _piece_edge.length()
                        # is_original_edge = _parent_node.isOriginalPieceEdge(_parent_node.edge_owner[node_edge_no], exampler_pieces, _node_edge)
                        # is_combo_original_edge = _parent_node.isComboOfOriginalPieceEdge(_parent_node.edge_owner[node_edge_no], exampler_pieces, _node_edge)
                        longer_piece_edge = (_p_edge_len > _n_edge_len)
                        if len(_parent_node.candidates) == 5:  # 若为第二块，加入剪枝
                            if round(_n_edge_len) != round(2 * _p_edge_len) and \
                                    round(2 * _n_edge_len) != round(_p_edge_len) and \
                                    round(_n_edge_len) != round(_p_edge_len):
                                continue

                        if round(_n_edge_len) == round(_p_edge_len):
                            _loop_count = 1
                        else:
                            _loop_count = 2
                        ## Debug:
                        '''if _cand==6 and _exampler_piece.flipped and node_edge_no==2:
                            _loop_count=1'''
                        ###
                        for i in range(_loop_count):
                            _node = pickle.loads(pickle.dumps(_parent_node))
                            _piece = pickle.loads(pickle.dumps(_exampler_piece))  # create a new one instead of sharing
                            _node.parent_ID = _parent_node.ID
                            _node_edge = _node.getEdge(view, node_edge_no, True)
                            _piece_edge = _piece.getEdge(view, piece_edge_no)
                            # 开始旋转
                            angle = _piece_edge.angleTo(_node_edge)
                            trans = QTransform()
                            trans.rotate(360 - angle)
                            _piece.q_object = trans.map(_piece.q_object)
                            # 因为旋转改变了坐标，要再获取一次
                            _node_edge = _node.getEdge(view, node_edge_no)
                            _piece_edge = _piece.getEdge(view, piece_edge_no, True)
                            if i == 0:
                                _piece.q_object.translate(
                                    -scale_factor * (_piece_edge.p1() - _node_edge.p1()).toPoint()
                                )
                                _neighbor_edge = _node.getEdge(view, node_edge_no - 1)
                                node_angle = _neighbor_edge.angleTo(_node_edge)
                            else:
                                _piece.q_object.translate(
                                    -scale_factor * (_piece_edge.p2() - _node_edge.p2()).toPoint()
                                )
                                _neighbor_edge = _node.getEdge(view, node_edge_no + 1)
                                node_angle = _node_edge.angleTo(_neighbor_edge)
                            # check if connect to an outer vertex
                            if node_angle >= 180:
                                continue
                            if _piece.q_object.intersected(_node.q_object).length() == 0:  # 检查有无非法重叠
                                _node.addPiece(_piece, longer_piece_edge, True, node_edge_no + 1,
                                               piece_edge_no + 1)  # addPiece会对piece做deepcopy，所以这里不需要
                                # 因为insert()输入的位置参数需要是当前位置的后一位，所以node_edge_no+1, 因为画图可知priece要从边向量终点添加，所以也+1
                                _node.reduce(view, exampler_pieces, _cand)
                                if len(_node.candidates) <= 2 and _node.getEdgeCount() > 9:  # 因为最后一块填进去最多消除2条边，倒数第二块填进去最多消除
                                    continue
                                '''
                                检查当前组合是否重复：
                                '''

                                encoding = _node.encodeMatrix()
                                if encoding in combo_dict:  # 防止过早剪枝， 会错减
                                    continue
                                else:
                                    combo_dict[encoding] = 1  # 随便给键赋个值
                                ### debug

                                '''_node.paint(scene)
                                view.repaint()
                                view.show()
                                dieTime = QTime.currentTime().addMSecs(50)
                                while (QTime.currentTime() < dieTime):
                                    QCoreApplication.processEvents(QEventLoop.AllEvents, 20)
                                scene.clear()  # not working for some reason
                                view.update()'''

                                ###
                                id += 1
                                _node.ID = id
                                #### debug 2
                                '''_debug_matrix=_node.matrix
                                _debug_list=[]
                                for i in range(7):
                                    if _debug_matrix[5][i] in _debug_list and _debug_matrix[5][i]!=0:
                                        print("WTF?")
                                    _debug_list.append(_debug_matrix[5][i])'''
                                ####
                                if len(_node.candidates) == 0 and _node.getEdgeCount() == 5:
                                    print('stop')
                                stack.append(_node)
    end = time.time()
    print("The time of execution is :", (end - start) / 60 / 60, "hours")


def BFSsequence(view: QGraphicsView, scene: QGraphicsScene, result_list: list, shape_list: list, exampler_pieces: list,
                change_to_BFS=False):
    DFSsequence(view, scene, result_list, shape_list, exampler_pieces, change_to_BFS=True)

def ASTARsequence(view: QGraphicsView, scene: QGraphicsScene, result_list: list, shape_list: list, exampler_pieces: list, change_to_greedy = False, change_to_UniCostSearch = False, heuristic = "depth"):
    if change_to_greedy:
        assert not change_to_UniCostSearch #两个change不能同时为true
    start = time.time()
    label = QLabel()
    layout = QVBoxLayout(view)
    layout.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
    layout.addWidget(label)
    #label.show()
    prio_queue= PriorityQueue()
    iter_count = 0
    _node :Node = Node()
    _node.addPiece(
        Piece(shape_list[_node.candidates.pop(2)], 2),
        False
    )
    prio_queue.put(PrioritizedItem(3+(-2*6), _node))
    id = 0
    while not prio_queue.empty():
        # 当前分支号码
        app.processEvents()
        temp_p_item=prio_queue.get()
        _const_parent_node = temp_p_item.item
        candidates = _const_parent_node.candidates

        # -----Debug------------
        #print("priority: ", temp_p_item.priority)
        '''scene.clear()
        view.update()
        _const_parent_node.paint(scene)
        view.repaint()
        view.show()
        dieTime = QTime.currentTime().addMSecs(1)
        while (QTime.currentTime() < dieTime):
            QCoreApplication.processEvents(QEventLoop.AllEvents, 20)'''

        # ------------------------------------
        # print("Node expand:")
        # print("#result: ", len(result_list))
        if len(candidates) == 0:
            # Debug
            # view.show
            '''scene.clear()
            view.repaint()
            view.update()
            _const_parent_node.paint(scene)
            view.repaint()
            view.show()
            dieTime = QTime.currentTime().addMSecs(50)
            while (QTime.currentTime() < dieTime):
                QCoreApplication.processEvents(QEventLoop.AllEvents, 20)
            #_const_parent_node.clearPoly(scene)
            #scene.clear()  # not working for some reason
            #view.update()
'''
            #
            iter_count += 1  # 第几个组合
            if _const_parent_node.getEdgeCount() == 5:
                result_list.append(_const_parent_node)
                print("#result: ", len(result_list))
                label.setText("<font size=300 color=white>" + str(len(result_list)) + "</font>")
                if (len(result_list)==1507):
                    break
                # Debug
                '''# view.hide()
                # view.show()
                scene.clear()
                view.update()
                _const_parent_node.paint(scene)
                view.setBackgroundBrush(Qt.gray)
                view.repaint()
                view.update()
                encoding = _const_parent_node.encodeMatrix()
                dieTime = QTime.currentTime().addMSecs(1)
                while (QTime.currentTime() < dieTime):
                    QCoreApplication.processEvents(QEventLoop.AllEvents, 20)
                # _const_parent_node.clearPoly(scene)
                # scene.clear()  # not working for some reason
                # view.update()

                #'''
            continue
        skip_L_tri = False
        skip_S_tri = False
        for cand_no in range(len(candidates)):  # debug
            # print("Len(candidates):", len(candidates))
            # 开始创建新的子节点， 不需要深拷贝因为这是父节点
            _parent_node = pickle.loads(pickle.dumps(_const_parent_node))
            _cand = _parent_node.candidates.pop(cand_no)  # _cand是指第几号拼图，是shape_list的某个位置下标
            _exampler_piece = Piece(shape_list[_cand], _cand)  # piece样品，跟本次迭代中创建的piece一模一样，只是为了方便查看形状的边长而存在
            if shape_list[_cand] == 0 and skip_L_tri:
                continue
            if shape_list[_cand] == 2 and skip_S_tri:
                continue
            if shape_list[_cand] == 0:
                skip_L_tri = True
            if shape_list[_cand] == 2:
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
                        _n_edge_len = _node_edge.length()
                        _p_edge_len = _piece_edge.length()
                        # is_original_edge = _parent_node.isOriginalPieceEdge(_parent_node.edge_owner[node_edge_no], exampler_pieces, _node_edge)
                        # is_combo_original_edge = _parent_node.isComboOfOriginalPieceEdge(_parent_node.edge_owner[node_edge_no], exampler_pieces, _node_edge)
                        longer_piece_edge = (_p_edge_len > _n_edge_len)
                        if len(_parent_node.candidates) == 5:  # 若为第二块，加入剪枝
                            if round(_n_edge_len) != round(2 * _p_edge_len) and \
                                    round(2 * _n_edge_len) != round(_p_edge_len) and \
                                    round(_n_edge_len) != round(_p_edge_len):
                                continue

                        if round(_n_edge_len) == round(_p_edge_len):
                            _loop_count = 1
                        else:
                            _loop_count = 2
                        ## Debug:
                        '''if _cand==6 and _exampler_piece.flipped and node_edge_no==2:
                            _loop_count=1'''
                        ###
                        for i in range(_loop_count):
                            _node = pickle.loads(pickle.dumps(_parent_node))
                            _piece = pickle.loads(pickle.dumps(_exampler_piece))  # create a new one instead of sharing
                            _node.parent_ID = _parent_node.ID
                            _node_edge = _node.getEdge(view, node_edge_no, True)
                            _piece_edge = _piece.getEdge(view, piece_edge_no)
                            # 开始旋转
                            angle = _piece_edge.angleTo(_node_edge)
                            trans = QTransform()
                            trans.rotate(360 - angle)
                            _piece.q_object = trans.map(_piece.q_object)
                            # 因为旋转改变了坐标，要再获取一次
                            _node_edge = _node.getEdge(view, node_edge_no)
                            _piece_edge = _piece.getEdge(view, piece_edge_no, True)
                            if i == 0:
                                _piece.q_object.translate(
                                    -scale_factor * (_piece_edge.p1() - _node_edge.p1()).toPoint()
                                )
                                _neighbor_edge = _node.getEdge(view, node_edge_no - 1)
                                node_angle = _neighbor_edge.angleTo(_node_edge)
                            else:
                                _piece.q_object.translate(
                                    -scale_factor * (_piece_edge.p2() - _node_edge.p2()).toPoint()
                                )
                                _neighbor_edge = _node.getEdge(view, node_edge_no + 1)
                                node_angle = _node_edge.angleTo(_neighbor_edge)
                            # check if connect to an outer vertex
                            if node_angle >= 180:
                                continue
                            if _piece.q_object.intersected(_node.q_object).length() == 0:  # 检查有无非法重叠
                                _node.addPiece(_piece, longer_piece_edge, True, node_edge_no + 1,
                                               piece_edge_no + 1)  # addPiece会对piece做deepcopy，所以这里不需要
                                # 因为insert()输入的位置参数需要是当前位置的后一位，所以node_edge_no+1, 因为画图可知priece要从边向量终点添加，所以也+1
                                _node.reduce(view, exampler_pieces, _cand)
                                if len(_node.candidates) <= 2 and _node.getEdgeCount() > 9:  # 因为最后一块填进去最多消除2条边，倒数第二块填进去最多消除
                                    continue
                                '''
                                检查当前组合是否重复：
                                '''

                                encoding = _node.encodeMatrix()
                                if encoding in combo_dict:  # 防止过早剪枝， 会错减
                                    continue
                                else:
                                    combo_dict[encoding] = 1  # 随便给键赋个值
                                ### debug

                                '''_node.paint(scene)
                                view.repaint()
                                view.show()
                                dieTime = QTime.currentTime().addMSecs(50)
                                while (QTime.currentTime() < dieTime):
                                    QCoreApplication.processEvents(QEventLoop.AllEvents, 20)
                                scene.clear()  # not working for some reason
                                view.update()'''

                                ###
                                id += 1
                                _node.ID = id
                                #### debug 2
                                '''_debug_matrix=_node.matrix
                                _debug_list=[]
                                for i in range(7):
                                    if _debug_matrix[5][i] in _debug_list and _debug_matrix[5][i]!=0:
                                        print("WTF?")
                                    _debug_list.append(_debug_matrix[5][i])'''
                                ####
                                if change_to_greedy:
                                    if heuristic == "depth":
                                        F_score = _node.getHScore()
                                    elif heuristic == "edge":
                                        F_score = abs(5-_node.getGScore())
                                    else:
                                        raise NotImplementedError()
                                elif change_to_UniCostSearch:
                                    F_score = _node.getGScore()
                                else:
                                    F_score=_node.getGScore()+_node.getHScore()
                                prio_queue.put(PrioritizedItem(F_score, _node))

    end = time.time()
    print("The time of execution is :", (end - start) / 60 / 6, "hours")

def GreedySequence(view: QGraphicsView, scene: QGraphicsScene, result_list: list, shape_list: list, exampler_pieces: list, heuristic):
    assert heuristic in ["edge", "depth"]
    ASTARsequence(view, scene, result_list, shape_list, exampler_pieces, change_to_greedy=True, heuristic = heuristic)
def UniCostSearchSequence(view: QGraphicsView, scene: QGraphicsScene, result_list: list, shape_list: list, exampler_pieces: list):
    ASTARsequence(view, scene, result_list, shape_list, exampler_pieces, change_to_UniCostSearch=True)

if __name__ == "__main__":
    start = time.time()
    app = QApplication([])
    view = QGraphicsView()
    scene = QGraphicsScene()
    view.setScene(scene)
    #view.show()
    #view.showMaximized()
    combo_dict = {}  #记录所有组合的dict
    scale_factor = 1
    view.scale(scale_factor, scale_factor)
    #view.hide()
    result_list = []
    shape_list = [0, 0, 1, 2, 2, 3, 4]  # shape ID of 7 pieces
    exampler_pieces = []  # 创建7个块的样板，用来查边长
    for i in range(len(shape_list)):
        exampler_pieces.append(Piece(shape_list[i], i, view=view))
    mode="BFS"
    assert mode in ["DFS", "BFS", "ASTAR", "GREEDY", "UCS"]

    if mode == "DFS":
        DFSsequence(view, scene, result_list, shape_list, exampler_pieces)
        #DFS 逻辑序列集
    elif mode == "BFS":
        BFSsequence(view, scene, result_list, shape_list, exampler_pieces)
    elif mode == "ASTAR":
        ASTARsequence(view, scene, result_list, shape_list, exampler_pieces)
    elif mode == "GREEDY":
        GreedySequence(view, scene, result_list, shape_list, exampler_pieces, "edge")
    elif mode == "UCS":
        UniCostSearchSequence(view, scene, result_list, shape_list, exampler_pieces)
    else:
        raise NotImplementedError()


    end=time.time()
    print(len(result_list), "combination found!")
    print("Stored combinations: ", len(combo_dict))
    print("The time of execution is :", (end - start)/60/60, "hours")
    print("saving all the nodes...")
    #save all results:
    i=1
    for node in result_list:
        save_node(node, str(i), mode=mode)
        i+=1
    print("Saving complete")
    exit(0)
    app.exec_()

