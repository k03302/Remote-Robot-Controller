from queue import Queue


class PathCalculator:
    def __init__(self, map):
        self.__map = map
        width, height = map.getMapSize()
        self.__inf = width * height
        self.__minMove = [[self.__inf for i in range(width)] for j in range(height)]

    def calculatePath(self, actor):
        startPos = actor.getPosition()
        goalItem = self.__map.getGoalItem()

        if goalItem == None:
            return None
        goalCell = goalItem.getCell()
        goalPos = goalCell.getPosition()

        self.__fillMinMove(startPos, goalPos)
        return self.__getRoute(startPos, goalPos)

    def __initMinMove(self):
        width, height = self.__map.getMapSize()
        for y in range(height):
            for x in range(width):
                self.__minMove[y][x] = self.__inf

    def __fillMinMove(self, startPos, goalPos):
        self.__initMinMove()

        x, y = startPos
        width, height = self.__map.getMapSize()

        q = Queue()
        q.put((x, y, 0))
        while not q.empty():
            x, y, moveCnt = q.get()
            if moveCnt >= self.__minMove[y][x]:
                continue
            self.__minMove[y][x] = moveCnt
            if (x, y) == goalPos:
                break
            if x > 0 and self.__map.getItemName((x - 1, y)) != "hazard":
                q.put((x - 1, y, moveCnt + 1))
            if x < width - 1 and self.__map.getItemName((x + 1, y)) != "hazard":
                q.put((x + 1, y, moveCnt + 1))
            if y > 0 and self.__map.getItemName((x, y - 1)) != "hazard":
                q.put((x, y - 1, moveCnt + 1))
            if y < height - 1 and self.__map.getItemName((x, y + 1)) != "hazard":
                q.put((x, y + 1, moveCnt + 1))

    def __getRoute(self, startPos, goalPos):
        x, y = goalPos
        width, height = self.__map.getMapSize()

        if self.__minMove[y][x] >= self.__inf:
            return None
        route = []
        move_cnt = self.__minMove[y][x]
        route.append((x, y))
        while move_cnt > 0:
            if x > 0 and self.__minMove[y][x - 1] == move_cnt - 1:
                x -= 1
            elif x < width - 1 and self.__minMove[y][x + 1] == move_cnt - 1:
                x += 1
            elif y > 0 and self.__minMove[y - 1][x] == move_cnt - 1:
                y -= 1
            elif y < height - 1 and self.__minMove[y + 1][x] == move_cnt - 1:
                y += 1
            else:
                return None
            route.append((x, y))
            move_cnt -= 1

        a, b = startPos
        if x != a and y != b:
            return None

        route.reverse()
        return route


class Cell:
    def __init__(self, x, y):
        self.__x = x
        self.__y = y
        self.__item = None
        self.__visited = False

    def setVisited(self):
        self.__visited = True

    def getVisited(self):
        return self.__visited

    def setItem(self, item):
        self.__item = item

    def getItem(self):
        return self.__item

    def getPosition(self):
        return (self.__x, self.__y)


class LatticeMap2D:
    def __init__(self, width, height):
        self.__width = width
        self.__height = height
        self.__mapCells = [[Cell(i, j) for i in range(width)] for j in range(height)]
        self.__itemFactory = ItemFactory()
        self.__pathCalculator = PathCalculator(self)

    def isValidLocation(self, loc):
        if loc != None:
            x, y = loc
            return x >= 0 and x < self.__width and y >= 0 and y < self.__height
        return False

    def getPath(self, actor):
        return self.__pathCalculator.calculatePath(actor)

    def setVisited(self, pos):
        if self.isValidLocation(pos):
            x, y = pos
            cell = self.__mapCells[y][x]
            cell.setVisited()
            item = cell.getItem()

            if item != None:
                cell.setItem(None)
                self.__itemFactory.removeItem(item)

    def addItem(self, type, loc):
        if not self.isValidLocation(loc):
            return
        cell = self.__getCell(loc)
        oldItem = cell.getItem()
        if oldItem != None:
            if oldItem.getItemName() == type:
                return
            self.__itemFactory.removeItem(oldItem)
        item = self.__itemFactory.createItem(type)
        if item != None:
            cell.setItem(item)
            item.setCell(cell)

    def removeItem(self, loc):
        if not self.isValidLocation(loc):
            return
        cell = self.__getCell(loc)
        item = cell.getItem()
        if item != None:
            cell.setItem(None)
            self.__itemFactory.removeItem(item)

    def getItem(self, loc):
        if not self.isValidLocation(loc):
            return None
        cell = self.__getCell(loc)
        item = cell.getItem()
        return item

    def getItemName(self, loc):
        item = self.getItem(loc)
        if item == None:
            return None
        return item.getItemName()

    def getItemData(self):
        return self.__itemFactory.getData()

    def getVisitedData(self):
        visitedData = []
        for cellRow in self.__mapCells:
            visitedDataRow = []
            for cell in cellRow:
                visitedDataRow.append(cell.getVisited())
            visitedData.append(visitedDataRow)
        return visitedData

    def getGoalItem(self):
        return self.__itemFactory.getNextGoal()

    def getMapSize(self):
        return (self.__width, self.__height)

    def __getCell(self, loc):
        if self.isValidLocation(loc):
            x, y = loc
            return self.__mapCells[y][x]
        return None


class MapItem:
    def __init__(self):
        self.__cell = None

    def getItemName(self):
        return "default"

    def setCell(self, cell):
        self.__cell = cell

    def getCell(self):
        return self.__cell


class Target(MapItem):
    def getItemName(self):
        return "target"


class ColorBlob(MapItem):
    def getItemName(self):
        return "blob"


class Hazard(MapItem):
    def getItemName(self):
        return "hazard"


class ItemFactory:
    def __init__(self):
        self.__itemStore = {}

    def createItem(self, type):
        item = None
        if type == "target":
            item = Target()
        elif type == "blob":
            item = ColorBlob()
        elif type == "hazard":
            item = Hazard()

        if item != None:
            if type not in self.__itemStore:
                self.__itemStore[type] = []
            self.__itemStore[type].append(item)
        return item

    def removeItem(self, item):
        if item != None:
            itemName = item.getItemName()
            self.__itemStore[itemName].remove(item)

    def getItemList(self, type):
        if type in self.__itemStore:
            return self.__itemStore[type]
        return []

    def getNextGoal(self):
        for blob in self.getItemList("blob"):
            if blob != None:
                return blob
        for target in self.getItemList("target"):
            if target != None:
                return target

        return None

    def getData(self):
        data = {}
        for itemName in self.__itemStore:
            data[itemName] = []
            for item in self.__itemStore[itemName]:
                cell = item.getCell()
                data[itemName].append(cell.getPosition())

        return data
