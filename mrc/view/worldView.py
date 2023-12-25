import tkinter as tk
from PIL import Image, ImageTk
import re
from .voiceRcgSys import VoiceRcg

MAPSIZE_DEFAULT = "(5 5)"
STARTING_POINT_DEFAULT = "(0 0)"
TARGET_DEFAULT = "((4 4))"
HAZARD_DEFAULT = "((1 1)(2 2)(2 3))"
MOVE_DELAY = 0.3


class WorldView:
    __CELL_SIZE = 80
    __ICON_SIZE = 40
    __MAP_MARGIN = 20
    __ITEM_IMG_SRC = {
        "robot_up": "mrc/resources/robot_up_icon.png",
        "robot_down": "mrc/resources/robot_down_icon.png",
        "robot_left": "mrc/resources/robot_left_icon.png",
        "robot_right": "mrc/resources/robot_right_icon.png",
        "hazard": "mrc/resources/hazard_icon.png",
        "blob": "mrc/resources/colorBlob_icon.png",
        "target": "mrc/resources/goal_icon.png",
    }

    def __init__(self):
        self.__mapSize = None
        self.__isRobotStop = True
        self.__callbackMap = {}
        self.__root = tk.Tk()
        self.__root.resizable(True, True)
        self.__root.protocol("WM_DELETE_WINDOW", self.__onWindowClose)
        self.__voiceRcg = VoiceRcg()
        self.__voiceRcg.registerResultEventListener(self.__onVoiceResult)

        self.__initMapFrame()
        self.__initConfigFrame()
        self.__initControlFrame()
        self.__buttonEventMapping()

    def initialize(self, mapSize):
        self.__mapSize = mapSize
        self.__resizeCanvas()

    def __runCallback(self, eventName, *args):
        if eventName in self.__callbackMap:
            callback = self.__callbackMap[eventName]
            if callable(callback):
                callback(*args)

    def __evaludateInputForm(self):
        mapSizeInput = self.__mapSizeInput.get()
        startingPointInput = self.__startingPointInput.get()
        targetInput = self.__targetInput.get()
        hazardInput = self.__hazardInput.get()

        tuplePattern = r"\((\d+)\s(\d+)\)"
        doubleTuplePattern = r"\((\((\d+)\s(\d+)\))*\)"

        success = True

        if not re.fullmatch(tuplePattern, mapSizeInput):
            self.__mapSizeValid.config(text="invalid value")
            success = False
        else:
            self.__mapSizeValid.config(text="")

        if not re.fullmatch(tuplePattern, startingPointInput):
            self.__startingPointValid.config(text="invalid value")
            success = False
        else:
            self.__startingPointValid.config(text="")

        if not re.fullmatch(doubleTuplePattern, targetInput):
            self.__targetValid.config(text="invalid value")
            success = False
        else:
            self.__targetValid.config(text="")

        if not re.fullmatch(doubleTuplePattern, hazardInput):
            self.__hazardValid.config(text="invalid value")
            success = False
        else:
            self.__hazardValid.config(text="")

        return success

    def __getInputData(self):
        mapSizeInput = self.__mapSizeInput.get()
        startingPointInput = self.__startingPointInput.get()
        targetInput = self.__targetInput.get()
        hazardInput = self.__hazardInput.get()

        data = {}
        for text, name in [
            (mapSizeInput, "mapSize"),
            (startingPointInput, "startingPoint"),
            (targetInput, "target"),
            (hazardInput, "hazard"),
        ]:
            integers = [int(match) for match in re.findall(r"\b\d+\b", text)]
            pairs = [
                (integers[i], integers[i + 1]) for i in range(0, len(integers) - 1, 2)
            ]
            if name == "mapSize" or name == "startingPoint":
                data[name] = pairs[0]
            else:
                data[name] = pairs
        return data

    def __showConfigView(self):
        self.__configFrame.pack(side=tk.LEFT, padx=10, pady=10)
        self.__mapFrame.pack_forget()
        self.__controlFrame.pack_forget()

    def __showMainView(self, data):
        self.__configFrame.pack_forget()
        self.__mapFrame.pack(side=tk.LEFT, padx=10, pady=10)
        self.__controlFrame.pack(side=tk.RIGHT, padx=10, pady=10)

    def __onWindowClose(self):
        self.__root.destroy()
        self.__runCallback("windowClose")

    def __onSubmit(self):
        isValidInput = self.__evaludateInputForm()
        if isValidInput:
            data = self.__getInputData()
            if data != None:
                self.__runCallback("submit", data)
                self.__showMainView(data)

    def __onVoiceResult(self, text):
        if text == None:
            self.__voiceRcgText.config(text="no input")
            self.__runCallback("voiceResult", None)
        else:
            nums = re.findall(r"\d+", text)
            itemName = None
            if len(nums) < 2:
                self.__voiceRcgText.config(text=f"invalid input: {text}")
                return
            if text[0] == "H":
                itemName = "hazard"
            elif text[0] == "B":
                itemName = "blob"
            elif text[0] == "T":
                itemName = "target"
            else:
                self.__voiceRcgText.config(text=f"invalid input: {text}")

            if itemName != None:
                self.__runCallback(
                    "voiceResult", [itemName, (int(nums[0]), int(nums[1]))]
                )
            else:
                self.__runCallback("voiceResult", None)

        self.__robotMoveButton.config(state="normal")

    def __onVoiceRcg(self):
        isRecording = self.__voiceRcg.isRecording()
        if not isRecording:
            self.__robotMoveButton.config(state="disabled")
            self.__voiceRcg.record()

    def __robotMove(self):
        self.__isRobotStop = not self.__isRobotStop
        if self.__isRobotStop:
            self.__voiceRcgButton.config(state="normal")
            self.__robotMoveButton.config(text="start")
        else:
            self.__voiceRcgButton.config(state="disabled")
            self.__robotMoveButton.config(text="stop")
        self.__runCallback("robotMove", self.__isRobotStop)

    def __buttonEventMapping(self):
        self.__submitButton.config(command=self.__onSubmit)
        self.__voiceRcgButton.config(command=self.__onVoiceRcg)
        self.__robotMoveButton.config(command=self.__robotMove)

    def __initMapFrame(self):
        self.__mapFrame = tk.Frame(self.__root)

        if self.__mapSize == None:
            self.__canvas = tk.Canvas(
                self.__mapFrame,
                width=100,
                height=100,
            )
        else:
            self.__canvas = tk.Canvas(
                self.__mapFrame,
                width=self.__CELL_SIZE * self.__mapSize[0],
                height=self.__CELL_SIZE * self.__mapSize[1],
            )
        self.__canvas.pack(padx=10, pady=10)

    def __resizeCanvas(self):
        if self.__canvas == None:
            self.__initMapFrame()
        elif self.__mapSize != None:
            self.__canvas.config(
                width=self.__CELL_SIZE * self.__mapSize[0],
                height=self.__CELL_SIZE * self.__mapSize[1],
            )

    def __initConfigFrame(self):
        self.__configFrame = tk.Frame(self.__root)

        self.__mapSizeLabel = tk.Label(self.__configFrame, text="map size")
        self.__mapSizeLabel.grid(row=0, column=0, pady=10)
        self.__mapSizeInput = tk.Entry(self.__configFrame, width=20)
        self.__mapSizeInput.grid(row=0, column=1, pady=10, sticky=tk.W)
        self.__mapSizeInput.insert(0, MAPSIZE_DEFAULT)
        self.__mapSizeValid = tk.Label(self.__configFrame)
        self.__mapSizeValid.grid(row=0, column=2, pady=10)

        self.__startingPointLabel = tk.Label(self.__configFrame, text="starting point")
        self.__startingPointLabel.grid(row=1, column=0, pady=10)
        self.__startingPointInput = tk.Entry(self.__configFrame, width=20)
        self.__startingPointInput.grid(row=1, column=1, pady=10, sticky=tk.W)
        self.__startingPointInput.insert(0, STARTING_POINT_DEFAULT)
        self.__startingPointValid = tk.Label(self.__configFrame)
        self.__startingPointValid.grid(row=1, column=2, pady=10)

        self.__targetLabel = tk.Label(self.__configFrame, text="predefined spot")
        self.__targetLabel.grid(row=2, column=0, pady=10)
        self.__targetInput = tk.Entry(self.__configFrame, width=100)
        self.__targetInput.grid(row=2, column=1, pady=10)
        self.__targetInput.insert(0, TARGET_DEFAULT)
        self.__targetValid = tk.Label(self.__configFrame)
        self.__targetValid.grid(row=2, column=2, pady=10)

        self.__hazarLabel = tk.Label(self.__configFrame, text="hazard")
        self.__hazarLabel.grid(row=3, column=0, pady=10)
        self.__hazardInput = tk.Entry(self.__configFrame, width=100)
        self.__hazardInput.grid(row=3, column=1, pady=10)
        self.__hazardInput.insert(0, HAZARD_DEFAULT)
        self.__hazardValid = tk.Label(self.__configFrame)
        self.__hazardValid.grid(row=3, column=2, pady=10)

        self.__submitButton = tk.Button(self.__configFrame, text="submit")
        self.__submitButton.grid(row=4, column=0, pady=10)
        self.__inputValidLabel = tk.Label(self.__configFrame)
        self.__inputValidLabel.grid(row=4, column=1, pady=10)

    def __initControlFrame(self):
        self.__controlFrame = tk.Frame(self.__root)

        self.__robotMoveButton = tk.Button(self.__controlFrame, text="start")
        self.__robotMoveButton.grid(row=0, column=0, padx=10, pady=10)

        self.__voiceRcgButton = tk.Button(self.__controlFrame, text="start voice rcg")
        self.__voiceRcgButton.grid(row=0, column=1, padx=10, pady=10)

        self.__voiceRcgText = tk.Label(self.__controlFrame)
        self.__voiceRcgText.grid(row=1, column=0, columnspan=2)

    def drawMap(self, worldData):
        if self.__mapSize == None:
            return

        itemData = worldData["itemData"]
        robotData = worldData["robotData"]
        visitedData = worldData["visitedData"]

        self.__canvas.image_references = []

        cols, rows = self.__mapSize

        self.__canvas.config(
            width=rows * self.__CELL_SIZE + 2 * self.__MAP_MARGIN,
            height=cols * self.__CELL_SIZE + 2 * self.__MAP_MARGIN,
        )
        self.__canvas.delete("all")
        for i in range(cols):
            for j in range(rows):
                if not visitedData[j][i]:
                    x = i * self.__CELL_SIZE
                    y = j * self.__CELL_SIZE
                    self.__canvas.create_rectangle(
                        x + self.__MAP_MARGIN - self.__CELL_SIZE / 2,
                        y + self.__MAP_MARGIN - self.__CELL_SIZE / 2,
                        x + self.__MAP_MARGIN + self.__CELL_SIZE / 2,
                        y + self.__MAP_MARGIN + self.__CELL_SIZE / 2,
                        fill="gray",
                        outline="",
                    )

        for j in range(rows):
            y = j * self.__CELL_SIZE
            self.__canvas.create_line(
                self.__MAP_MARGIN,
                y + self.__MAP_MARGIN,
                (cols - 1) * self.__CELL_SIZE + self.__MAP_MARGIN,
                y + self.__MAP_MARGIN,
                fill="black",
            )

        for i in range(cols):
            x = i * self.__CELL_SIZE
            self.__canvas.create_line(
                x + self.__MAP_MARGIN,
                self.__MAP_MARGIN,
                x + self.__MAP_MARGIN,
                (rows - 1) * self.__CELL_SIZE + self.__MAP_MARGIN,
                fill="black",
            )

        if "target" in itemData:
            targetPosArr = itemData["target"]
            for targetPos in targetPosArr:
                self.__drawItem("target", targetPos)

        if "blob" in itemData:
            blobPosArr = itemData["blob"]
            for blobPos in blobPosArr:
                self.__drawItem("blob", blobPos)

        if "hazard" in itemData:
            hazardPosArr = itemData["hazard"]
            for hazardPos in hazardPosArr:
                self.__drawItem("hazard", hazardPos)

        robotPos = robotData["pos"]
        robotDir = robotData["dir"]
        if robotDir == (1, 0):
            self.__drawItem("robot_right", robotPos)
        elif robotDir == (-1, 0):
            self.__drawItem("robot_left", robotPos)
        elif robotDir == (0, 1):
            self.__drawItem("robot_down", robotPos)
        elif robotDir == (0, -1):
            self.__drawItem("robot_up", robotPos)

    def __drawItem(self, type, pos):
        if self.__mapSize == None:
            return
        if not (type in self.__ITEM_IMG_SRC):
            return
        x, y = pos
        if x < 0 or y < 0 or x >= self.__mapSize[0] or y >= self.__mapSize[1]:
            return
        img = Image.open(self.__ITEM_IMG_SRC[type])
        img_resized = img.resize((self.__ICON_SIZE, self.__ICON_SIZE))

        image = ImageTk.PhotoImage(img_resized)

        self.__canvas.create_image(
            x * self.__CELL_SIZE + self.__MAP_MARGIN,
            y * self.__CELL_SIZE + self.__MAP_MARGIN,
            anchor=tk.CENTER,
            image=image,
        )
        self.__canvas.image_references.append(image)

    def runGUI(self):
        self.__showConfigView()
        self.__root.mainloop()

    def registerEventListener(self, eventName, callback):
        if callable(callback):
            self.__callbackMap[eventName] = callback
