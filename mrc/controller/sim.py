import random


class SIM:
    __ITEM_NUM = {"hazard": 1, "blob": 2}
    __NO_MOVE_PROB = 0.05
    __TWO_MOVE_PROB = 0.05
    __DIR_LIST = [[1, 0], [0, 1], [-1, 0], [0, -1]]

    def __init__(self, mapSize=None, robotPos=None, robotDir=None):
        self.__mapSize = None
        self.__map = None
        self.__hazardChecked = None
        self.__blobChecked = None
        self.__robotPos = None
        self.__robotDir = None

        if mapSize != None:
            self.setMapSize(mapSize)
        if robotPos != None:
            self.setRobotPos(robotPos)
        if robotDir != None:
            self.setRobotDir(robotDir)

    def setMapSize(self, mapSize):
        self.__mapSize = mapSize
        width, height = mapSize
        self.__map = [[0 for i in range(width)] for j in range(height)]
        self.__hazardChecked = [[False for i in range(width)] for j in range(height)]
        self.__blobChecked = [[False for i in range(width)] for j in range(height)]

    def addItemRandPos(self, typeName, checked=False):
        if typeName in self.__ITEM_NUM:
            while True:
                x, y = random.randint(0, self.__mapSize[0] - 1), random.randint(
                    0, self.__mapSize[1] - 1
                )
                if self.__map[y][x] == 0:
                    self.__map[y][x] = self.__ITEM_NUM[typeName]
                    if typeName == "hazard":
                        self.__hazardChecked[y][x] = checked
                    elif typeName == "blob":
                        self.__blobChecked[y][x] = checked
                    break

    def addItem(self, typeName, pos, checked=False):
        x, y = pos
        if typeName in self.__ITEM_NUM:
            self.__map[y][x] = self.__ITEM_NUM[typeName]
            if typeName == "hazard":
                self.__hazardChecked[y][x] = checked
            elif typeName == "blob":
                self.__blobChecked[y][x] = checked

    def setRobotPos(self, pos):
        self.__robotPos = list(pos)
        x, y = pos

    def setRobotDir(self, dir):
        self.__robotDir = dir

    def rotate(self):
        x, y = self.__robotDir
        self.__robotDir = (y, -x)

    def move(self):
        prob = random.random()
        if prob < self.__NO_MOVE_PROB:
            return

        x, y = self.__robotPos
        dx, dy = self.__robotDir

        if self.isSafe(x + dx, y + dy):
            self.__robotPos[0] += dx
            self.__robotPos[1] += dy
            if prob > 1 - self.__TWO_MOVE_PROB and self.isSafe(x + 2 * dx, y + 2 * dy):
                self.__robotPos[0] += dx
                self.__robotPos[1] += dy

    def isSafe(self, x, y):
        return x >= 0 and x < self.__mapSize[0] and y >= 0 and y < self.__mapSize[1]

    def getRobotPos(self):
        return self.__robotPos

    def getRobotDir(self):
        return self.__robotDir

    def getAddedItem(self):
        addedItem = {"hazard": [], "blob": []}
        x, y = self.__robotPos
        dx, dy = self.__robotDir
        front_x, front_y = x + dx, y + dy

        for dir in self.__DIR_LIST:
            i, j = dir

            _x, _y = x + i, y + j
            if self.isSafe(_x, _y):
                if (
                    not self.__blobChecked[_y][_x]
                    and self.__map[_y][_x] == self.__ITEM_NUM["blob"]
                ):
                    addedItem["blob"].append((_x, _y))
                    self.__blobChecked[_y][_x] = True
                if (
                    not self.__hazardChecked[_y][_x]
                    and _x == front_x
                    and _y == front_y
                    and self.__map[_y][_x] == self.__ITEM_NUM["hazard"]
                ):
                    addedItem["hazard"].append((_x, _y))
                    self.__hazardChecked[_y][_x] = True

        return addedItem
