from .mapSys import *


class LatticeMap2DActor:
    def __init__(self, map):
        self.__pos = None
        self.__dir = None
        self.__path = None
        self.__pathIndex = 0
        self.__map = map

    def setPosition(self, pos):
        self.__pos = pos
        if self.__path != None:
            self.__pathIndex += 1

    def getPosition(self):
        return self.__pos

    def setDirection(self, dir):
        self.__dir = dir

    def getDirection(self):
        return self.__dir

    def getNextBehavior(self):
        if self.__path == None or self.__pathIndex + 1 >= len(self.__path):
            if self.__map.getGoalItem() == None:
                return None
            else:
                self.updatePath()
                if self.__path == None:
                    return None
                if self.__pathIndex + 1 >= len(self.__path):
                    self.__path = None
                    return None

        x, y = self.__pos
        nextX, nextY = self.__path[self.__pathIndex + 1]
        dx, dy = self.__dir
        if nextX - x == dx and nextY - y == dy:
            return "move"
        return "rotate"

    def updatePath(self):
        print("updatePath")
        self.__path = self.__map.getPath(self)
        self.__pathIndex = 0

    def isOnPath(self):
        if self.__pos == None or self.__path == None:
            return False
        x, y = self.__pos
        expectedX, expectedY = self.__path[self.__pathIndex]
        if x == expectedX and y == expectedY:
            return True
        return False

    def isOnGoal(self):
        return (self.__pathIndex == self.__path.length - 1) and self.isOnPath()

    def getStatData(self):
        return {"pos": self.__pos, "dir": self.__dir}

    def getPathData(self):
        if self.__path == None:
            return None
        return self.__path[:]
