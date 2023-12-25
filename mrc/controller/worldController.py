from mrc.model.worldModel import WorldStateModel
from mrc.view.worldView import WorldView
from threading import Thread
import time
from .sim import SIM


class MobileRobotController:
    __INIT_ROBOT_DIRECTION = (0, 1)
    __MOVE_DELAY = 0.3

    def __init__(self):
        self.__worldStateModel = WorldStateModel()
        self.__worldView = WorldView()
        self.__isStop = True
        self.__isTerminated = False
        self.__mainThread = Thread(target=self.__mainloop)
        self.__addEventListener()
        self.__sim = None

    def run(self):
        self.__worldView.runGUI()

    def __mainloop(self):
        while not self.__isTerminated:
            if self.__isStop:
                time.sleep(self.__MOVE_DELAY)
                continue

            behavior = self.__worldStateModel.getNextRobotBehavior()
            print("behavior: ", behavior)
            self.__worldStateModel.printRobotStat()
            if behavior == None:
                time.sleep(self.__MOVE_DELAY)
                continue
            # if behavior == "move":
            #    self.__worldStateModel.moveRobot()
            # elif behavior == "rotate":
            #    self.__worldStateModel.rotateRobot()

            # worldData = self.__worldStateModel.getWorldData()
            # self.__worldView.drawMap(worldData)

            if behavior == "move":
                self.__sim.move()
            elif behavior == "rotate":
                self.__sim.rotate()

            addedItem = self.__sim.getAddedItem()
            robotPos = self.__sim.getRobotPos()
            robotDir = self.__sim.getRobotDir()

            self.__worldStateModel.setRobotPosition(robotPos)
            self.__worldStateModel.setRobotDirection(robotDir)

            for itemName in addedItem:
                for itemPos in addedItem[itemName]:
                    self.__worldStateModel.addItem(itemName, itemPos)

            worldData = self.__worldStateModel.getWorldData()
            self.__worldView.drawMap(worldData)

            time.sleep(self.__MOVE_DELAY)

    def __onWindowClose(self):
        self.__isTerminated = True

    def __onRobotMove(self, isStop):
        self.__isStop = isStop

    def __onVoiceResult(self, data):
        if data != None:
            itemName = data[0]
            pos = data[1]
            self.__worldStateModel.addItem(itemName, pos)
            worldData = self.__worldStateModel.getWorldData()
            self.__worldView.drawMap(worldData)

    def __onSubmit(self, data):
        if data == None:
            return

        mapSize = data["mapSize"]
        startingPoint = data["startingPoint"]
        targetPosArray = data["target"]
        hazardPosArray = data["hazard"]

        self.__worldView.initialize(mapSize)
        self.__worldStateModel.initialize(
            mapSize, startingPoint, self.__INIT_ROBOT_DIRECTION
        )

        # sim 초기화 부분. sim 맵은 초기 입력의 모든 아이템을 가지고 있다.

        self.__sim = SIM(mapSize, startingPoint, self.__INIT_ROBOT_DIRECTION)

        for targetPos in targetPosArray:
            self.__worldStateModel.addItem("target", targetPos, updatePath=False)
            self.__sim.addItem("target", targetPos)
        for hazardPos in hazardPosArray:
            self.__worldStateModel.addItem("hazard", hazardPos, updatePath=False)
            self.__sim.addItem("hazard", hazardPos)

        # sim에서 랜덤 위치에 보이지 않는 아이템 추가
        self.__sim.addItemRandPos("blob")
        self.__sim.addItemRandPos("blob")
        self.__sim.addItemRandPos("hazard")
        self.__sim.addItemRandPos("hazard")

        addedItem = self.__sim.getAddedItem()
        for itemName in addedItem:
            for itemPos in addedItem[itemName]:
                self.__worldStateModel.addItem(itemName, itemPos)

        worldData = self.__worldStateModel.getWorldData()
        self.__worldView.drawMap(worldData)

        self.__mainThread.start()

    def __addEventListener(self):
        self.__worldView.registerEventListener("submit", self.__onSubmit)
        self.__worldView.registerEventListener("robotMove", self.__onRobotMove)
        self.__worldView.registerEventListener("windowClose", self.__onWindowClose)
        self.__worldView.registerEventListener("voiceResult", self.__onVoiceResult)
