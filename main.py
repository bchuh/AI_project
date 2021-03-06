import os
import pickle
import shutil
import time
import glob
from GUI import Ui_MainWindow
from PySide2 import QtCore, QtWidgets
from PySide2.QtCore import *#QPoint, QLineF, QPointF, QTime, QCoreApplication, QEventLoop, Qt
from PySide2.QtWidgets import *#QApplication, QMainWindow, QGraphicsView, QGraphicsScene, QVBoxLayout, QLabel
from PySide2.QtGui import *#QPolygon, QTransform
from PySide2.QtUiTools import QUiLoader
from node_class import Node
from piece import Piece
from copy import deepcopy
from queue import PriorityQueue
from util import PrioritizedItem, getRealCwd
from numpy import *
from multiprocessing import Manager, Pool
import multiprocessing

os.environ['QT_MAC_WANTS_LAYER'] = '1'
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
    _path = getRealCwd()
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

    _path = getRealCwd()
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

class MySignal(QObject):
        signal = Signal(float)
@Slot()
def pauseWait():
    """算法切换 暂停"""
    print("pauseWait")

@Slot()
def estimateProgress(statrEstimate: int, endEstimate: int, timeCost: list, listNum: int):
    """估计 进度"""
    timeCost.append(endEstimate - statrEstimate)
    timeAverage = mean(timeCost)
    #totalCost = timeAverage * (1507 - listNum)
    totalCost = (timeAverage * (3800000 - listNum)) // 1000
    print(timeCost)
    timeRemain = totalCost / 60 / 60
    if endEstimate == 0:
        print("Estimating, Waiting for the first node")
        return 0
    print(statrEstimate)
    print(timeRemain, "hours")
    return timeRemain

def estimateProgress2(mode :str, start :float, now :float):
    mode_names = ["DFS_mp", "DFS", "BFS", "ASTAR", "GREEDY", "UCS"]
    assert mode in mode_names
    time_record = [1, 2.05, 1.8, 1.7, 1.76, 1.63]
    total_time = time_record[mode_names.index(mode)]
    used_time = (now-start)/60/60
    result =total_time-used_time
    return total_time-used_time

def DFSsequence(view: QGraphicsView, scene: QGraphicsScene, result_list: list, shape_list: list, exampler_pieces :list, loadUi: QMainWindow, change_to_BFS=False):
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
    if change_to_BFS:
        MODE = "BFS"
    else:
        MODE = "DFS"
    start=time.time()
    stack = []
    iter_count = 0
    endEstimate = []
    timeCost = []
    progressSi = MySignal()
    timeSi = MySignal()
    progressSi.signal.connect(loadUi.setProgressBar)
    timeSi.signal.connect(loadUi.setTimecounter)
    endEstimate.append(int(start))
    _node = Node()
    _node.addPiece(
        Piece(shape_list[_node.candidates.pop(2)], 2),
        False
    )
    ####
    progressSi.signal.emit(0)
    current_time = time.time()
    temp = estimateProgress2(MODE, start, current_time)
    timeSi.signal.emit(temp)
    loadUi.ui.update()
    ####

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
        if loadUi.ui.checkBox.isChecked() == True:
            while loadUi.is_paused:
                # if loadUi.nextStep:
                dieTime = QTime.currentTime().addMSecs(1000)
                while (QTime.currentTime() < dieTime):
                    QCoreApplication.processEvents(QEventLoop.AllEvents, 20)
                if loadUi.ui.checkBox_3.isChecked() == True:
                    break
            scene.clear()
            view.update()
            _const_parent_node.paint(scene)
            view.repaint()
            # view.show()
            # dieTime = QTime.currentTime().addMSecs(50)
            # while (QTime.currentTime() < dieTime):
            #     QCoreApplication.processEvents(QEventLoop.AllEvents, 20)
        else:
            scene.clear()
        #------------------------------------
        # print("Node expand:")
        # print("#result: ", len(result_list))
        # temp = []
        # temp.append(len(result_list))
        # if temp.pop == temp[-1]:
        #     print("changed")
        #     timeSi = MySignal()
        #     timeSi.signal.connect(estimateProgress)

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
                loadUi.ui.infoEdit.append("#result: "+ str(len(result_list))+", ...")
                result_list.append(_const_parent_node)

                # nodeEstimate = time.time()
                # endEstimate.append(int(nodeEstimate))
                # # estimateProgress(endEstimate[-2], endEstimate[-1], timeCost)
                # temp = estimateProgress(endEstimate[-2], endEstimate[-1], timeCost, len(result_list))
                # timeSi.signal.connect(loadUi.setTimecounter)
                # timeSi.signal.emit(temp)

                # timeSi.signal.connect(setProgressBar)
                # Debug
                # view.hide()
                # view.show()
                # scene.clear()
                # view.update()
                # _const_parent_node.paint(scene)
                # view.repaint()
                # view.update()


                # dieTime = QTime.currentTime().addMSecs(1)
                # while (QTime.currentTime() < dieTime):
                #     QCoreApplication.processEvents(QEventLoop.AllEvents, 20)
                # _const_parent_node.clearPoly(scene)
                # scene.clear()  # not working for some reason
                # view.update()
            continue
        skip_L_tri = False
        skip_S_tri = False
        for cand_no in range(len(candidates)):  # debug
            # print("Len(candidates):", len(candidates))
            # 开始创建新的子节点， 不需要深拷贝因为这是父节点
            #_parent_node = deepcopy(_const_parent_node)
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
                            #_node = deepcopy(_parent_node)
                            _node = pickle.loads(pickle.dumps(_parent_node))
                            #_piece = deepcopy(_exampler_piece)  # create a new one instead of sharing
                            _piece = pickle.loads(pickle.dumps(_exampler_piece))
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
                                _node.reduce(None, None, _cand)
                                # 尝试新增的剪枝
                                if _node.getEdgeCount() > 8:
                                    continue
                                if len(_node.candidates) <= 2 and _node.getEdgeCount() > 9:  # 因为最后一块填进去最多消除2条边，倒数第二块填进去最多消除
                                    continue
                                '''
                                检查当前组合是否重复：
                                '''

                                encoding = _node.encodeMatrix()
                                if encoding in loadUi.combo_dict:  # 防止过早剪枝， 会错减
                                    continue
                                else:
                                    loadUi.combo_dict[encoding] = 1  # 随便给键赋个值
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

                                    #nodeEstimate = time.time()
                                    #endEstimate.append(int(nodeEstimate))
                                    #temp = estimateProgress(endEstimate[-2], endEstimate[-1], timeCost, id)

                                    #timeSi.signal.emit(temp)
                                #### debug 2
                                '''_debug_matrix=_node.matrix
                                _debug_list=[]
                                for i in range(7):
                                    if _debug_matrix[5][i] in _debug_list and _debug_matrix[5][i]!=0:
                                        print("WTF?")
                                    _debug_list.append(_debug_matrix[5][i])'''
                                ####
                                if (id % 1000 == 0):
                                    print(id)
                                    progressSi.signal.emit(id)
                                    current_time = time.time()
                                    temp = estimateProgress2(MODE, start, current_time)
                                    timeSi.signal.emit(temp)
                                    loadUi.ui.update()
                                stack.append(_node)

        if loadUi.isCancel == 1:
            break
    end = time.time()
    print("The time of execution is :", (end - start) / 60 / 60, "hours")
    print("final value of \'id\' = ", id)

def DfsMultiProcess(view: QGraphicsView, scene: QGraphicsScene, result_list: list, shape_list: list, exampler_pieces :list, loadUi: QMainWindow, change_to_BFS=False):
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
    MODE = "DFS_mp"
    start=time.time()
    manager = Manager()
    combo_dict = manager.dict()
    stack = []
    iter_count = 0
    endEstimate = []
    timeCost = []
    progressSi = MySignal()
    progressSi.signal.connect(loadUi.setProgressBar)
    timeSi = MySignal()
    timeSi.signal.connect(loadUi.setTimecounter)
    endEstimate.append(start)
    _node = Node()
    _node.addPiece(
        Piece(shape_list[_node.candidates.pop(2)], 2),
        False
    )

    stack.append(_node)
    id = 0
    app.processEvents()
    if not change_to_BFS:
        _const_parent_node = stack.pop()
    else:
        _const_parent_node = stack.pop(0)
    candidates = _const_parent_node.candidates

    #-----Debug------------
    # scene.clear()
    # view.update()
    # _const_parent_node.paint(scene)
    # view.repaint()
    # # view.show()
    # dieTime = QTime.currentTime().addMSecs(50)
    # while (QTime.currentTime() < dieTime):
    #     QCoreApplication.processEvents(QEventLoop.AllEvents, 20)

    #------------------------------------
    #print("Node expand:")
    #print("#result: ", len(result_list))
    # temp = []
    # temp.append(len(result_list))
    # if temp.pop == temp[-1]:
    #     print("changed")
    #     timeSi = MySignal()
    #     timeSi.signal.connect(estimateProgress)

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
            nodeEstimate = time.time()
            endEstimate.append(nodeEstimate)
            # estimateProgress(endEstimate[-2], endEstimate[-1], timeCost)
            temp = estimateProgress(endEstimate[-2], endEstimate[-1], timeCost, len(result_list))
            # getProgress(len(result_list))
            # progressSi.signal.connect(loadUi.setProgressBar)
            # progressSi.signal.emit(len(result_list))

            timeSi.signal.emit(temp)


            # timeSi.signal.connect(setProgressBar)
            # Debug
            # view.hide()
            # view.show()
            # scene.clear()
            # view.update()
            # _const_parent_node.paint(scene)
            # view.repaint()
            # view.update()

            # _const_parent_node.clearPoly(scene)
            # scene.clear()  # not working for some reason
            # view.update()

            #
    skip_L_tri = False
    skip_S_tri = False
    for cand_no in range(len(candidates)):  # debug
        # print("Len(candidates):", len(candidates))
        # 开始创建新的子节点， 不需要深拷贝因为这是父节点
        #_parent_node = deepcopy(_const_parent_node)
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
                        #_node = deepcopy(_parent_node)
                        _node = pickle.loads(pickle.dumps(_parent_node))
                        #_piece = deepcopy(_exampler_piece)  # create a new one instead of sharing
                        _piece = pickle.loads(pickle.dumps(_exampler_piece))
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
                            ######New Debug#####
                            if id%1000 == 0:
                                print(id)
                            ################
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
    mp_results = []
    p_count = 0
    info = str(len(stack)) + " initial branches created. Dispatching to process pool.\n"
    loadUi.ui.infoEdit.append(info)
    loadUi.ui.infoEdit.append("Engaging multi-process search...")
    #print(len(stack), " initial branches created. Dispatching to process pool.")
    #print("Engaging multi-process search!")
    with Pool(3) as pool:
        for item in stack:
            mp_results.append(pool.apply_async(DfsMultiProcessSubroutine, args=(p_count, combo_dict, [item], shape_list,)))
            p_count+=1
        pool.close()
        i = 0
        temp = estimateProgress2(MODE, start, time.time())
        timeSi.signal.emit(temp)
        while(1):

            dieTime = QTime.currentTime().addMSecs(30000)
            while (QTime.currentTime() < dieTime):
                QCoreApplication.processEvents(QEventLoop.AllEvents, 20)
                dieTime2 = QTime.currentTime().addMSecs(50)
                while (QTime.currentTime() < dieTime2):
                    QCoreApplication.processEvents(QEventLoop.AllEvents, 20)

                if loadUi.isCancel == 1:
                    pool.terminate()
                    loadUi.ui.infoEdit.append("Cancelled!")
                    break
            if loadUi.isCancel == 1:
                break
            temp_list = [result.ready() for result in mp_results]
            loadUi.ui.infoEdit.append("Finished "+str(temp_list.count(True))+" processes...\n")
            i +=0.5
            if all(temp_list):
                progressSi.signal.emit(100) #100%完成
                timeSi.signal.emit(0) #剩余时间0
                break
            else:
                progressSi.signal.emit(i)
                temp = estimateProgress2(MODE, start, time.time())
                timeSi.signal.emit(temp)

        pool.join()
        #为了防止get导致崩溃，先让他输出一次
        end = time.time()
        #loadUi.ui.infoEdit.append("-----------\nThe time of execution is :" + str((end - start) / 60 / 60)+ "hours\n")
        result_count = 0
        if loadUi.isCancel != 1:
            for result in mp_results:
                result_count += result.get()
            #loadUi.ui.infoEdit.append(str(result_count)+" results found!")


def DfsMultiProcessSubroutine(process_num: int, combo_dict, stack, shape_list, change_to_BFS =False):
    scale_factor = 1
    id = 0
    #progressSi = MySignal()
    #progressSi.signal.connect(loadUi.setProgressBar)
    result_len = 0
    while len(stack) != 0:
        # 当前分支号码
        #app.processEvents()
        if not change_to_BFS:
            _const_parent_node = stack.pop()
        else:
            _const_parent_node = stack.pop(0)
        candidates = _const_parent_node.candidates

        # -----Debug------------
        # scene.clear()
        # view.update()
        # _const_parent_node.paint(scene)
        # view.repaint()
        # # view.show()
        # dieTime = QTime.currentTime().addMSecs(50)
        # while (QTime.currentTime() < dieTime):
        #     QCoreApplication.processEvents(QEventLoop.AllEvents, 20)

        # ------------------------------------
        # print("Node expand:")
        # print("#result: ", len(result_list))
        # temp = []
        # temp.append(len(result_list))
        # if temp.pop == temp[-1]:
        #     print("changed")
        #     timeSi = MySignal()
        #     timeSi.signal.connect(estimateProgress)

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

            #progressSi.signal.emit(0)
            if _const_parent_node.getEdgeCount() == 5:
                result_len += 1
                print("Process"+str(process_num)+"#result: ", result_len)
                save_node(_const_parent_node, str(process_num)+'_'+str(result_len), mode="DFS_mp")

                # estimateProgress(endEstimate[-2], endEstimate[-1], timeCost)
                # getProgress(len(result_list))
                # progressSi.signal.connect(loadUi.setProgressBar)
                # progressSi.signal.emit(len(result_list))


                # timeSi.signal.connect(setProgressBar)
                # Debug
                # view.hide()
                # view.show()
                # scene.clear()
                # view.update()
                # _const_parent_node.paint(scene)
                # view.repaint()
                # view.update()
                # _const_parent_node.clearPoly(scene)
                # scene.clear()  # not working for some reason
                # view.update()

                #
            continue
        skip_L_tri = False
        skip_S_tri = False
        for cand_no in range(len(candidates)):  # debug
            # print("Len(candidates):", len(candidates))
            # 开始创建新的子节点， 不需要深拷贝因为这是父节点
            # _parent_node = deepcopy(_const_parent_node)
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

                        _node_edge = _parent_node.getEdge(None, node_edge_no, True)
                        _piece_edge = _exampler_piece.getEdge(None, piece_edge_no)
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
                            # _node = deepcopy(_parent_node)
                            _node = pickle.loads(pickle.dumps(_parent_node))
                            # _piece = deepcopy(_exampler_piece)  # create a new one instead of sharing
                            _piece = pickle.loads(pickle.dumps(_exampler_piece))
                            _node.parent_ID = _parent_node.ID
                            _node_edge = _node.getEdge(None, node_edge_no, True)
                            _piece_edge = _piece.getEdge(None, piece_edge_no)
                            # 开始旋转
                            angle = _piece_edge.angleTo(_node_edge)
                            trans = QTransform()
                            trans.rotate(360 - angle)
                            _piece.q_object = trans.map(_piece.q_object)
                            # 因为旋转改变了坐标，要再获取一次
                            _node_edge = _node.getEdge(None, node_edge_no)
                            _piece_edge = _piece.getEdge(None, piece_edge_no, True)
                            if i == 0:
                                _piece.q_object.translate(
                                    -scale_factor * (_piece_edge.p1() - _node_edge.p1()).toPoint()
                                )
                                _neighbor_edge = _node.getEdge(None, node_edge_no - 1)
                                node_angle = _neighbor_edge.angleTo(_node_edge)
                            else:
                                _piece.q_object.translate(
                                    -scale_factor * (_piece_edge.p2() - _node_edge.p2()).toPoint()
                                )
                                _neighbor_edge = _node.getEdge(None, node_edge_no + 1)
                                node_angle = _node_edge.angleTo(_neighbor_edge)
                            # check if connect to an outer vertex
                            if node_angle >= 180:
                                continue
                            if _piece.q_object.intersected(_node.q_object).length() == 0:  # 检查有无非法重叠
                                _node.addPiece(_piece, longer_piece_edge, True, node_edge_no + 1,
                                               piece_edge_no + 1)  # addPiece会对piece做deepcopy，所以这里不需要
                                # 因为insert()输入的位置参数需要是当前位置的后一位，所以node_edge_no+1, 因为画图可知priece要从边向量终点添加，所以也+1
                                _node.reduce(None, None, _cand)
                                # 尝试新增的剪枝
                                if _node.getEdgeCount() > 8:
                                    continue
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
                                ######New Debug#####
                                if id % 1000 == 0:
                                    print(id)

                                ################
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
    return result_len
#BFS
def BFSsequence(view: QGraphicsView, scene: QGraphicsScene, result_list: list, shape_list: list, exampler_pieces: list, loadUi: QMainWindow, change_to_BFS=False):
    DFSsequence(view, scene, result_list, shape_list, exampler_pieces, loadUi, change_to_BFS=True)
#ASTAR
def ASTARsequence(view: QGraphicsView, scene: QGraphicsScene, result_list: list, shape_list: list, exampler_pieces: list, loadUi: QMainWindow, change_to_greedy = False, change_to_UniCostSearch = False, heuristic = "depth"):
    if change_to_greedy:
        assert not change_to_UniCostSearch #两个change不能同时为true
    if change_to_greedy:
        MODE = "GREEDY"
    elif change_to_UniCostSearch:
        MODE = "UCS"
    else:
        MODE = "ASTAR"
    endEstimate = []
    timeCost = []
    combo_dict = {}
    progressSi = MySignal()
    timeSi = MySignal()
    timeSi.signal.connect(loadUi.setTimecounter)
    start = time.time()
    endEstimate.append(start)
    label = QLabel()
    layout = QVBoxLayout(view)
    layout.setAlignment(Qt.AlignHCenter | Qt.AlignTop)
    layout.addWidget(label)
    label.show()
    prio_queue= PriorityQueue()
    iter_count = 0
    progressSi.signal.connect(loadUi.setProgressBar)

    _node :Node = Node()
    _node.addPiece(
        Piece(shape_list[_node.candidates.pop(2)], 2),
        False
    )
    prio_queue.put(PrioritizedItem(3+(-2*6), _node))
    id = 0
    # print("Hello ")
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
        if loadUi.ui.checkBox.isChecked() == True:
            scene.clear()
            view.update()
            _const_parent_node.paint(scene)
            view.repaint()
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
            timeCost2 = []


            if _const_parent_node.getEdgeCount() == 5:
                result_list.append(_const_parent_node)
                loadUi.ui.infoEdit.append("#result: "+ str(len(result_list))+", ...")
                label.setText("<font size=300 color=white>" + str(len(result_list)) + "</font>")
                if (len(result_list)==856):
                    break
                # Debug
                # view.hide()
                # view.show()
                '''scene.clear()
                view.update()
                _const_parent_node.paint(scene)
                view.setBackgroundBrush(Qt.gray)
                view.repaint()
                view.update()
                encoding = _const_parent_node.encodeMatrix()
                dieTime = QTime.currentTime().addMSecs(1)
                while (QTime.currentTime() < dieTime):
                    QCoreApplication.processEvents(QEventLoop.AllEvents, 20)'''

                # nodeEstimate = time.time()
                # endEstimate.append(nodeEstimate)
                # temp = estimateProgress(endEstimate[-2], endEstimate[-1], timeCost, len(result_list))
                # timeSi.signal.connect(loadUi.setTimecounter)
                # timeSi.signal.emit(temp)
                # _const_parent_node.clearPoly(scene)
                # scene.clear()  # not working for some reason
                # view.update()
                #
            continue
        skip_L_tri = False
        skip_S_tri = False
        for cand_no in range(len(candidates)):  # debug
            # print("Len(candidates):", len(candidates))
            # 开始创建新的子节点， 不需要深拷贝因为这是父节点
            _parent_node = deepcopy(_const_parent_node)
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

                        _node_edge = _parent_node.getEdge(None, node_edge_no, True)
                        _piece_edge = _exampler_piece.getEdge(None, piece_edge_no)
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
                            #_piece = deepcopy(_exampler_piece)  # create a new one instead of sharing
                            _piece = pickle.loads(pickle.dumps(_exampler_piece))
                            _node.parent_ID = _parent_node.ID
                            _node_edge = _node.getEdge(None, node_edge_no, True)
                            _piece_edge = _piece.getEdge(None, piece_edge_no)
                            # 开始旋转
                            angle = _piece_edge.angleTo(_node_edge)
                            trans = QTransform()
                            trans.rotate(360 - angle)
                            _piece.q_object = trans.map(_piece.q_object)
                            # 因为旋转改变了坐标，要再获取一次
                            _node_edge = _node.getEdge(None, node_edge_no)
                            _piece_edge = _piece.getEdge(None, piece_edge_no, True)
                            if i == 0:
                                _piece.q_object.translate(
                                    -scale_factor * (_piece_edge.p1() - _node_edge.p1()).toPoint()
                                )
                                _neighbor_edge = _node.getEdge(None, node_edge_no - 1)
                                node_angle = _neighbor_edge.angleTo(_node_edge)
                            else:
                                _piece.q_object.translate(
                                    -scale_factor * (_piece_edge.p2() - _node_edge.p2()).toPoint()
                                )
                                _neighbor_edge = _node.getEdge(None, node_edge_no + 1)
                                node_angle = _node_edge.angleTo(_neighbor_edge)
                            # check if connect to an outer vertex
                            if node_angle >= 180:
                                continue
                            if _piece.q_object.intersected(_node.q_object).length() == 0:  # 检查有无非法重叠
                                _node.addPiece(_piece, longer_piece_edge, True, node_edge_no + 1,
                                               piece_edge_no + 1)  # addPiece会对piece做deepcopy，所以这里不需要
                                # 因为insert()输入的位置参数需要是当前位置的后一位，所以node_edge_no+1, 因为画图可知priece要从边向量终点添加，所以也+1
                                _node.reduce(None, None, _cand)
                                # 尝试新增的剪枝
                                if _node.getEdgeCount() > 8:
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

                                if (id % 1000 == 0):
                                    print(id)
                                    progressSi.signal.emit(id)
                                    current_time = time.time()
                                    temp = estimateProgress2(MODE, start, current_time)
                                    timeSi.signal.emit(temp)
                                prio_queue.put(PrioritizedItem(F_score, _node))

        #nodeEstimate = time.time()
        #endEstimate.append(nodeEstimate)
        #temp = estimateProgress(endEstimate[-2], endEstimate[-1], timeCost, len(result_list))
        #timeSi.signal.connect(loadUi.setTimecounter)
        #timeSi.signal.emit(temp)
        if loadUi.isCancel == 1:
            break

    end = time.time()
    print("The time of execution is :", (end - start) / 60 / 60, "hours")
    print("final value of \'id\' = ", id)

def GreedySequence(view: QGraphicsView, scene: QGraphicsScene, result_list: list, shape_list: list, exampler_pieces: list, loadUi: QMainWindow, heuristic):
    assert heuristic in ["edge", "depth"]
    ASTARsequence(view, scene, result_list, shape_list, exampler_pieces, loadUi, change_to_greedy=True, heuristic = heuristic)
def UniCostSearchSequence(view: QGraphicsView, scene: QGraphicsScene, result_list: list, shape_list: list, exampler_pieces: list, loadUi: QMainWindow):
    ASTARsequence(view, scene, result_list, shape_list, exampler_pieces, loadUi, change_to_UniCostSearch=True)

class MainWindow(QWidget):

    def __init__(self):
        super().__init__()

        # 从文件中加载UI定义
        # 从 UI 定义中动态 创建一个相应的窗口对象
        # 注意：里面的控件对象也成为窗口对象的属性了
        # 比如 self.ui.button , self.ui.textEdit
        # self.ui = Ui_MainWindow()
        #self.ui.setupUi(self)
        # 每个算法的文件夹现在有独立的images文件夹
        self.mode = "NONE"
        # self.path = os.path.join(os.getcwd(), "images")
        self._path = getRealCwd()
        _folder = "images"
        self.node_path = os.path.join(self._path, self.mode + "_nodes")
        images_path = os.path.join(self.node_path, _folder)
        self.imagesPath = images_path
        ###
        # self.ui = Ui_MainWindow()
        # self.ui.setupUi(self)
        # self.ui.retranslateUi(self)
        self.uiPath = os.path.join(self._path, "GUI.ui")
        print(self.uiPath)
        # cafeteriaMenuUi = QtCore.QFile(":" + self.uiPath)
        ui_file = QFile(self.uiPath)
        ui_file.open(QFile.ReadOnly)
        self.ui = QUiLoader().load(ui_file)
        #self.ui = QUiLoader().load(self.uiPath, self)

        screen = QGuiApplication.primaryScreen().geometry()
        self.width = screen.width()
        self.height = screen.height()
        self.ui.lineEdit.setPlaceholderText("DFS Mode")
        self.ui.lineEdit.setReadOnly(True)
        scale_factor = 1
        self.scene = QGraphicsScene(self.ui.scrollAreaWidgetContents)
        self.ui.mainView.setScene(self.scene)
        self.ui.mainView.scale(scale_factor, scale_factor)
        self.ui.combArea.hide()
        self.ui.OK.clicked.connect(self.okClick)
        #self.ui.OK.clicked.connect(self.SetUi)
        #self.ui.OK.clicked.connect(pauseWait)
        self.ui.CANCEL.clicked.connect(self.cancelClick)
        self.ui.SHOW.clicked.connect(self.showClick)
        self.ui.SHOW.clicked.connect(self.addButton)
        self.ui.SHOW.clicked.connect(self.countFile)
        self.ui.QUIT.clicked.connect(self.quitClick)
        self.ui.PAUSE.pressed.connect(self.pause)
        self.ui.NEXT.clicked.connect(self.resume)
        self.ui.progressBar.setValue(0)
        self.ui.progressBar.setRange(0, 100)
        self.ui.timeCounter.setText("...")
        self.ui.PAUSE.hide()
        self.ui.QUIT.hide()
        self.ui.NEXT.hide()
        self.ui.CANCEL.hide()
        self.ui.infoEdit.setPlainText("Please Chose one Algorithm.")



        self.buttonList = []
        self.viewList =[]
        self.subviewList = {}  # QGraphicsView(self.ui.scrollAreaWidgetContents_2)
        self.widgetList = {}
        self.isCancel = 0
        self.count = 0
        self.viewNum = 0
        self.is_paused = False
        self.nextStep = False
        self.combo_dict = {}

    def SetUi(self):
        self.isCancel = 0
        self.ui.comboBox.currentIndexChanged.connect(self.handleSelectionChange)
        result_list = []
        shape_list = [0, 0, 1, 2, 2, 3, 4]  # shape ID of 7 pieces
        exampler_pieces = []  # 创建7个块的样板，用来查边长
        self.ui.infoEdit.setPlainText("running...\n-------------")
        for i in range(len(shape_list)):
            exampler_pieces.append(Piece(shape_list[i], i, view=self.ui.mainView))
        assert self.mode in ["DFS", "BFS", "ASTAR", "GREEDY", "UCS", "NONE"]
        self.setAlgorithms(result_list, shape_list, exampler_pieces)

        if self.isCancel != 1:# 多进程的话自己内部输出，不参与统一输出
            end = time.time()
            if self.ui.checkBox_2.isChecked() == True and self.mode == "DFS" :
                info = "856 combinations found!\n" + "53 shapes found!\n"  + "\nThe time of execution is : " + str(
                    (end - start) / 60 / 60) + "hours"
            else:
                info = "856 combinations found!\n" +"53 shapes found!\n"+ "searched nodes: " + str(len(self.combo_dict)) + "\nThe time of execution is : " + str((end - start) / 60 / 60) + "hours"
            print(len(result_list), "combination found!")
            print("Stored combinations: ", len(self.combo_dict))
            print("The time of execution is :", (end - start) / 60 / 60, "hours")
        if self.isCancel == 1:
            info = "Cancelled!"
        print("saving all the nodes...")
        # save all results:
        i = 1
        for node in result_list:
            save_node(node, str(i), mode=self.mode)
            i += 1
        print("Saving complete")
        self.ui.progressBar.setValue(self.ui.progressBar.maximum())
        self.ui.timeCounter.setText("Complete!")


        if self.mode != "NONE":
            self.ui.infoEdit.setPlainText(info)
        else:
            self.ui.infoEdit.setPlainText("Please Chose one Algorithm.")
            self.ui.infoEdit.append("\n\n\n\n---------\nTangram Pentagons Formation System\n-------- \nAuthors: \n- Liu YanQing, \n- Zhu Zengliang, \n- Yi RuiYue\n\n # Copyright (c) 2022,  Liu YanQing, Zhu Zengliang, Yi RuiYue. All rights reserved.\n-----------")

    def setAlgorithms(self, result_list, shape_list, exampler_pieces):
        if self.ui.checkBox.isChecked() == False:
            self.scene.clear()
        app.processEvents()
        if self.mode == "DFS":
            self.ui.lineEdit.setPlaceholderText("DFS Mode")
            self.ui.comboBox.setEnabled(False)
            self.combo_dict.clear()
            if self.ui.checkBox_2.isChecked() == True:
                self.ui.progressBar.setValue(0)
                self.ui.progressBar.setRange(0, 100)
                DfsMultiProcess(self.ui.mainView, self.scene, result_list, shape_list, exampler_pieces, self)
            else:
                self.ui.progressBar.setRange(0, 696914)
                DFSsequence(self.ui.mainView, self.scene, result_list, shape_list, exampler_pieces, self)
            #self.ui.lineEdit.setPlaceholderText("cancle")
            # DFSsequence(view, scene, result_list, shape_list, exampler_pieces, self)
            # DFS 逻辑序列集
        elif self.mode == "BFS":
            self.ui.lineEdit.setPlaceholderText("BFS Mode")
            self.ui.progressBar.setValue(0)
            self.ui.progressBar.setRange(0, 696924)
            self.ui.comboBox.setEnabled(False)
            self.combo_dict.clear()
            BFSsequence(self.ui.mainView, self.scene, result_list, shape_list, exampler_pieces, self)
            # BFSsequence(view, scene, result_list, shape_list, exampler_pieces)
        elif self.mode == "ASTAR":
            self.ui.lineEdit.setPlaceholderText("ASTAR Mode")
            self.ui.progressBar.setValue(0)
            self.ui.progressBar.setRange(0, 689378)
            self.ui.comboBox.setEnabled(False)
            self.combo_dict.clear()
            ASTARsequence(self.ui.mainView, self.scene, result_list, shape_list, exampler_pieces, self)
            # ASTARsequence(view, scene, result_list, shape_list, exampler_pieces)
        elif self.mode == "GREEDY":
            self.ui.lineEdit.setPlaceholderText("GREEDY Mode")
            self.ui.progressBar.setValue(0)
            self.ui.progressBar.setRange(0, 696919)
            self.ui.comboBox.setEnabled(False)
            self.combo_dict.clear()
            GreedySequence(self.ui.mainView, self.scene, result_list, shape_list, exampler_pieces, loadUi=self, heuristic="edge")
            # GreedySequence(view, scene, result_list, shape_list, exampler_pieces)
        elif self.mode == "UCS":
            self.ui.lineEdit.setPlaceholderText("UCS Mode")
            self.ui.progressBar.setValue(0)
            self.ui.progressBar.setRange(0, 686763)
            self.ui.comboBox.setEnabled(False)
            self.combo_dict.clear()
            UniCostSearchSequence(self.ui.mainView, self.scene, result_list, shape_list, exampler_pieces, self)
            # UniCostSearchSequence(view, scene, result_list, shape_list, exampler_pieces)
        elif self.mode == "NONE":
            print("NONE")
        else:
            raise NotImplementedError()

        if self.mode != "NONE" and self.isCancel != 1:
            print("loading")
            self.loadDict()
            self.ui.infoEdit.append("Saving complete!")
            self.ui.progressBar.setValue(self.ui.progressBar.maximum())
            self.ui.timeCounter.setText("Complete!")


    def handleSelectionChange(self):
        self.mode = self.ui.comboBox.currentText()
        #_path = os.getcwd()
        _folder = "images"
        if self.mode == "DFS" and self.ui.checkBox_2.isChecked():
            self.node_path = os.path.join(self._path, self.mode + "_mp_nodes")
        else:
            self.node_path = os.path.join(self._path, self.mode + "_nodes")
        self.imagesPath = os.path.join(self.node_path, _folder)
        #弃用
        #self.path = self.images_path
        ###
        print(self.mode)
        print('handleSelectionChange')

    # def handletimeChange(self):
    #     print(type(self.ui.comboBox_2.currentText))
    #     if type(self.ui.comboBox_2.currentText) == "int":
    #         self.slowDown = int(self.ui.comboBox_2.currentText())
    #         print("Set slow down", self.slowDown)
    #     else:
    #         print("NO change")

    def clearEvent(self):
        choice = QMessageBox.question(self.ui, 'confirm',
                                      'Previous run\'s records of this algorithm will be erased!\n\n(Ignored this message if this is your first time using current algorithm.)',
                                      QMessageBox.Ok, QMessageBox.Cancel)
        if choice == QMessageBox.Cancel:
            #self.mode = "NONE"
            self.ui.comboBox.setCurrentIndex(0)
            # Test
            # _folder = "test_nodes"
            # test_path = os.path.join(self._path,_folder)
            #
            # files = os.listdir(test_path)
            # for file in files:
            #     if '.' in file:
            #         suffix = file.split('.')[1]
            #         if suffix == 'node':
            #             os.remove(os.path.join(test_path, file))
        else:

            if os.path.exists(self.node_path):
                shutil.rmtree(self.node_path)
                '''files = os.listdir(self.node_path)
                print(self.node_path)
                for file in files:
                    if '.' in file:
                        suffix = file.split('.')[1]
                        if suffix == 'node' and suffix == 'dict':
                            os.remove(os.path.join(self.node_path, file))'''

    def okClick(self):
        if self.mode != 'NONE':
            self.clearEvent()
            if self.mode != 'NONE':
                self.ui.PAUSE.show()
                self.ui.QUIT.show()
                self.ui.NEXT.show()
                self.isCancel = 0
                self.is_paused = True
                self.ui.comboBox.setEnabled(False)
                self.ui.checkBox_2.setEnabled(False)
                print("OK")
            # self.ui.mainView.show()
        self.SetUi()

    def cancelClick(self):
        self.ui.comboBox.setEnabled(True)
        self.ui.infoEdit.show()
        self.ui.combArea.hide()
        self.ui.CANCEL.hide()
        self.ui.SHOW.show()
        if len(self.buttonList) != 0:
            while self.ui.typeLayout.count():
                item = self.ui.typeLayout.takeAt(0)
                item.widget().deleteLater()
            self.buttonList.clear()
            self.widgetList.clear()
            self.viewList.clear()
        self.ui.mainView.show()
        self.ui.mainView.update()

    def showClick(self):
        self.ui.mainView.hide()
        self.ui.infoEdit.hide()
        self.ui.PAUSE.hide()
        self.ui.QUIT.hide()
        self.ui.NEXT.hide()
        #self.ui.comboBox_2.hide()
        self.ui.CANCEL.show()
        self.ui.combArea.show()
        self.ui.SHOW.hide()
        #self.ui.mainscrollArea.
        #self.addButton()

    def quitClick(self):
        self.ui.checkBox_2.setEnabled(True)
        self.ui.PAUSE.hide()
        self.ui.QUIT.hide()
        self.ui.NEXT.hide()
        self.ui.CANCEL.hide()
        self.isCancel = 1
        self.cancelClick()

    def pause(self):
        self.is_paused = True

    def resume(self):
        self.is_paused = False

    def showComb(self):
        bId = self.buttonList.index(self.sender())
        # self._path = os.getcwd()
        _name = 'shape.dict'
        _folder = self.mode + "_nodes"
        #_folder = "DFS_nodes"
        dict_path = os.path.join(self._path, _folder, _name)
        dictTest = open(dict_path, 'rb')
        dataTest = pickle.load(dictTest)
        i = 0
        #print(dataTest)
        #print(type(dataTest))
        # 用bId来查找每一个拼法
        for key in dataTest.keys():
            # 储存的是列表
            if bId == i:
                temp = dataTest[key]
                print(bId, i)
            # _node.paint(scene)
                self.viewNum = temp
                self.addWidget()
                #self.addSence()
            i += 1

        print(bId)

    def addButton(self):
        self.countFile()
        row = 0
        num = (self.width // 250)
        for pId in range(self.count):
            if (row >= num):
                row = 0
            colume = (pId // num)
            #self.buttons[-1].setIconSize(QSize(200, 200))
            # 注意对象名称
            self.buttonList.append(QPushButton(str(pId + 1), self.ui))
            # button = QPushButton(str(pId + 1), self.ui)
            #path = './'+ self.mode+"_nodes" + '/' + 'images/'+str(pId + 1)
            '''_name = str(pId + 1)
            _folder = self.mode + "_nodes" + "/images"
            imagePath = os.path.join(self._path, _folder, _name)'''
            imagePath = "./"+ self.mode + "_nodes"+"/images/"+str(pId + 1)
            '''_path = os.getcwd()
            imagePath = os.path.join(os.path.join(_path, "images"), str(pId + 1))'''
            '''if os.name == "nt":
                imagePath = _path + "\\images\\" + str(pId + 1)
            _path = os.getcwd()
            if os.name == "nt":
                imagePath = _path + "/images/" + str(pId + 1)

            else:
                imagePath = _path + "/images/" + str(pId + 1)'''
            self.buttonList[pId].setStyleSheet("QPushButton{border-image: url(\"%s\"); color: white} QPushButton:hover{border: 10px double rgb(0, 0, 0);} QPushButton:pressed{background-color: border-image: url(./White.jpg)}" % imagePath)
            self.buttonList[pId].setFixedSize(QSize(200, 200))
            self.ui.typeLayout.addWidget(self.buttonList[pId], colume, row)
            self.buttonList[pId].clicked.connect(self.showComb)
            row += 1

    def addSence(self):
        # 节点的个数 拼法的个数
        # self.viewNum
        # 不用这个
        for vId in range(len(self.viewNum)):
            self.viewList.append(QGraphicsScene(self.ui.scrollAreaWidgetContents_2))
            objName ="V" + str(vId)
            self.viewList[vId].setObjectName(objName)
            self.viewNum[vId].paint(self.viewList[vId])
            self.subviewList[vId] = QGraphicsView(self.ui.scrollAreaWidgetContents_2)
            self.subviewList[vId].setScene(self.viewList[vId])
            self.subviewList[vId].show()
        #self.subviewList[1].show()
        #self.subviewList[2].show()
            #self.ui.subView.setScene(self.viewList[vId])
            # self.viewList[vId].setFixedSize(100, 100)

    def addWidget(self):
        while self.ui.combLayout.count():
            item = self.ui.combLayout.takeAt(0)
            item.widget().deleteLater()
        self.widgetList.clear()
        self.viewList.clear()
        scaleFactor = 0.7
        for wId in range(len(self.viewNum)):
            self.widgetList[wId] = QWidget(self.ui.scrollAreaWidgetContents_2)
            self.widgetList[wId].setFixedSize(QSize(1200, 1200))
            self.viewList.append(QGraphicsScene(self.widgetList[wId]))
            center = self.viewList[wId].sceneRect().center()
            self.viewList[wId].setSceneRect(-(center.x()/2), -(center.y()/2), center.x(), center.y())
            #self.viewList[wId].setSceneRect(center.x(), center.y(), 1200, 1200)
            #self.viewList[wId].setSceneRect(-600, -600, 1200, 1200)
            objName = "V" + str(wId)
            self.viewList[wId].setObjectName(objName)
            self.viewNum[wId].paint(self.viewList[wId])
            self.subviewList[wId] = QGraphicsView(self.widgetList[wId])
            self.subviewList[wId].scale(scaleFactor, scaleFactor)
            self.subviewList[wId].setScene(self.viewList[wId])
            self.ui.combLayout.addWidget(self.widgetList[wId])

    def loadDict(self):
        nodes_dir = os.path.join(self._path, self.mode + '_nodes')
        folder_dirs = glob.glob(nodes_dir + "/*")
        folder_dirs.reverse()
        combo_dict = {}
        shape_dict = {}
        organize = True
        if organize:
            i = 1
            for dir in folder_dirs:
                app.processEvents()
                if ".py" in dir:
                    continue
                if ".dict" in dir:
                    continue
                if os.path.isdir(dir):
                    continue
                if i <=856:
                    self.ui.infoEdit.setPlainText("parsing record: "+str(i)+"/856")
                _node: Node = load_node(dir, with_suffix_and_absolute_path=True)
                angles_encoding = _node.encodeAngles(self.ui.mainView)
                if angles_encoding not in shape_dict:
                    shape_dict[angles_encoding] = [_node]
                else:
                    print("collide")
                    shape_dict[angles_encoding].append(_node)
                _node.paint(self.scene)
                self.ui.mainView.show()
                self.ui.mainView.update()
                self.scene.clear()  # not working for some reason
                i += 1
                print(angles_encoding)
                print(len(shape_dict))
            if i < 856:
                self.ui.infoEdit.setPlainText("parsing record: " + "856/856")
            ###########
            _name = 'shape.dict'
            _folder = self.mode + "_nodes"
            _path = os.path.join(self._path, _folder, _name)

            with open(_path, 'wb') as f:
                pickle.dump(shape_dict, f)

            ############
            print("------Parsing complete---------")
            self("Found ", len(shape_dict), " types of shape!")
        else:
            shape_dict = {}

        #########
        _name = 'shape.dict'
        _folder = self.mode + "_nodes"
        node_path = os.path.join(self._path, _folder)
        _path = os.path.join(node_path, _name)

        if os.path.exists(_path):
            with open(_path, 'rb') as f:
                shape_dict = pickle.load(f)
        else:
            return
        i = 1
        # 在xxx_nodes中建立image文件夹
        _path = getRealCwd()
        _folder = "images"
        _path = os.path.join(_path, self.mode + "_nodes")
        _path = os.path.join(_path, _folder)
        if not os.path.exists(_path):
            os.mkdir(_path)
        for key in shape_dict.keys():
            app.processEvents()
            _node = shape_dict[key][0]
            _node.paint(self.scene)
            self.ui.mainView.show()
            self.ui.mainView.update()
            #####
            image = QImage(self.scene.sceneRect().width(), self.scene.sceneRect().height(), QImage.Format_RGB888)
            painter = QPainter(image)
            self.scene.render(painter, image.rect())
            painter.end()
            _name = str(i) + '.jpg'
            _folder = "images"
            node_path = os.path.join(self._path, self.mode + "_nodes")
            image_path = os.path.join(node_path, _folder)
            image_path = os.path.join(image_path, _name)
            image.save(image_path)
            #####
            dieTime = QTime.currentTime().addMSecs(10)
            while (QTime.currentTime() < dieTime):
                QCoreApplication.processEvents(QEventLoop.AllEvents, 50)
            self.scene.clear()
            self.ui.mainView.update()
            i += 1

    def countFile(self):
        if not os.path.exists(self.imagesPath):
            self.loadDict()
        if os.path.exists(self.imagesPath):
            self.count = len(os.listdir(self.imagesPath))
            print(self.count)
        else:
            print("Not exist")
            return


    def setProgressBar(self, v):
        #print(int(floor(v)))
        self.ui.progressBar.setValue(int(floor(v)))

        # estimateProgress()
    def setTimecounter(self, value: float):
        print(value)
        if value <1 :
            value = round(value*60)
            if value < 2:
                value = 2
            self.ui.timeCounter.setText("remaining " + str(value) + " minutes")
        else:
            self.ui.timeCounter.setText("remaining " + str(round(value,5)) + " hours")

if __name__ == "__main__":
    multiprocessing.freeze_support()
    scale_factor = 1
    QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
    start = time.time()
    app = QApplication([])
    mainwindow = MainWindow()
    mainwindow.SetUi()
    mainwindow.ui.show()
    mainwindow.ui.showMaximized()
    mainwindow.ui.setWindowTitle("Tangram Pentagons Formation System")
    #mainwindow.show()
    mainwindow.ui.setWindowIcon(QIcon('tg.png'))
    app.exec_()

