from .mapSys import *
from .actorSys import *


class WorldStateModel:
    def __init__(self):
        self.__map = None
        self.__robot = None

    def initialize(self, mapSize, robotPos, robotDir):
        width, height = mapSize
        self.__map = LatticeMap2D(width, height)
        self.__robot = LatticeMap2DActor(self.__map)
        self.setRobotPosition(robotPos)
        self.setRobotDirection(robotDir)
        self.printRobotStat()

    def addItem(self, type, pos, updatePath=True):
        if self.__map == None or self.__robot == None:
            return
        if self.__map.isValidLocation(pos):
            self.__map.addItem(type, pos)
        if updatePath:
            self.__robot.updatePath()

    def setRobotPosition(self, pos):
        if self.__map == None or self.__robot == None:
            return
        self.__robot.setPosition(pos)
        self.__map.setVisited(pos)
        if not self.__robot.isOnPath():
            self.__robot.updatePath()

    def getWorldData(self):
        if self.__map == None or self.__robot == None:
            return
        itemData = self.__map.getItemData()
        visitedData = self.__map.getVisitedData()
        robotStatData = self.__robot.getStatData()

        worldData = {}
        worldData["visitedData"] = visitedData
        worldData["robotData"] = robotStatData
        worldData["itemData"] = itemData

        return worldData

    def getPathData(self):
        return self.__getPathData()

    def moveRobot(self):
        if self.__robot == None:
            return
        x, y = self.__robot.getPosition()
        dx, dy = self.__robot.getDirection()
        self.setRobotPosition((x + dx, y + dy))

    def setRobotDirection(self, dir):
        if self.__robot == None:
            return
        self.__robot.setDirection(dir)

    def rotateRobot(self):
        if self.__robot == None:
            return
        dx, dy = self.__robot.getDirection()
        self.setRobotDirection((dy, -dx))

    def getNextRobotBehavior(self):
        if self.__robot == None:
            return
        return self.__robot.getNextBehavior()

    def printRobotStat(self):
        if self.__robot == None:
            return
        print(self.__robot.getStatData())
