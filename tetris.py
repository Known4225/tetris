'''
Requires turtletools
Shift key - turtools.keyPressed(50) (16 on windows)
Space key - turtools.keyPressed(65) (32 on windows)
Up arrow - turtools.keyPressed(111) (38 on windows)
Left arrow - turtools.keyPressed(113) (37 on windows)
Right arrow - turtools.keyPressed(114) (39 on windows)
Down arrow - turtools.keyPressed(116) (40 on windows)

Z: 52, 90
'''
import turtle as t
from turtletools import turtleTools
import math as m
import random as r
import argparse
t.setup(960, 720)
t.colormode(255)
t.title("Tetris")

parser = argparse.ArgumentParser()
parser.add_argument("-vf", "--variableframerate", help="disable variable framerate", action="store_true")
parser.add_argument("-tps", "--tps", help="fix tps")
parser.add_argument("-fps", "--fps", help="print fps", action="store_true")
args = parser.parse_args()
if args.tps == None: # for fixed tps
    tps = 'inf'
else:
    tps = int(args.tps)
if not args.variableframerate: # import time for variable framerate (beta)
    import time
turtools = turtleTools(t.getcanvas(), -240, -180, 240, 180, True)
class main:
    def __init__(self):
        self.defaultFramerate = 600 # default (expected) framerate (framerates get as low as 7 on the chromebook)
        self.defaultTicks = 500 # default ticks (based on default framerate)
        self.fallTicks = self.defaultTicks # number of ticks between falls (speeds up by 10% per level) (TOADD: variable tick rate (depending on how fast the game is running))
        self.downThresh = round(self.fallTicks * 0.05) # number of ticks between falls when the down arrow key is pressed
        self.buttonTicks = round(self.fallTicks * 0.4) # number of ticks a button is held before it spams the input
        self.buttonTicksRel = round(self.fallTicks * 0.08) # number of ticks between spams of buttons
        self.ticksF = self.fallTicks # number of ticks until next fall (decreases every tick until it's 0 then refills back to self.fallTicks)
        if not args.variableframerate: # variable framerate variable init
            self.curSec = time.gmtime().tm_sec
            self.oldSec = self.curSec - 1
            self.fps = 'unknown'
            self.frameCount = self.defaultTicks

        self.themeColors = [(230, 230, 230), (30, 30, 30), (0, 0, 0), (60, 60, 60), (200, 200, 200), (195, 195, 195)] # light theme default
        self.theme = 0 # move to change theme
        t.Screen().bgcolor(self.themeColors[self.theme])

        self.sp = t.Turtle(shape = "square") # sp is used to draw the grid, the played blocks, and the current falling block
        self.sp.hideturtle()
        self.sp.penup()
        self.sp2 = t.Turtle() # sp2 is used to draw text
        self.sp2.hideturtle()
        self.sp2.pencolor(self.themeColors[self.theme + 1])
        self.sp2.pensize(2)
        self.sp2.penup()
        self.sp3 = t.Turtle(shape = "square") # sp3 is used to draw the "next" block
        self.sp3.hideturtle()
        self.sp3.penup()
        self.size = 15 # size of grid square (absolute)
        self.sp.turtlesize(self.size / 10.5)
        self.sp3.turtlesize(self.size / 10.5)
        self.blockX = 0 # x value of the current block (absolute)
        self.blockY = 0 # y value of the current block (absolute)
        self.boardX = 0 # x value of current block (in list)
        self.boardY = 0 # y value of current block (in list)
        
        # self.bottomRow = [None, None, None, None] # depreciated
        self.newBlock = 1 # triggers a newBlock event
        self.keyPressed = [] # list of keys currently held down
        self.bufferFrames = 1 #buffer input (technical)
        
        self.level = 1 # game level
        self.oldLevel = 0 # for updating
        self.score = 0 # game score
        self.oldScore = -1 # for updating
        self.lines = 0 # number of lines cleared
        self.oldLines = -1 # for updating
        self.gameOver = False # checks for if the game is paused or over
        self.bounds = [0, 0, 1, 1] #bounds record the max and min x and y values, format: min x, min y, max x, max y
        self.boardBounds = [-75, -160, 75, 140] # like bounds but for the board, min x, min y, max x, max y
        
        

        self.currentBlockType = 0 # currentBlockType is a number from 0 to 6, representing what piece is currently falling
        self.nextRand = r.randint(0, 6) # nextRand is like current block but represents the next block that will fall
        self.currentBlock = [0, 0, 0, 0, (0, 0, 0)] # currentBlock data (render)
        self.nextBlock = [0, 0, 0, 0, (0, 0, 0)] # nextBlock data (render)
        self.modList = [] # important for turning currentBlock grid into coordinates (X)
        self.divList = [] # important for turning currentBlock grid into coordinates (Y)


        #blockData is on a grid
        '''
        1  2  3  4
        5  6  7  8
        9  10 11 12
        13 14 15 16
        '''
        # index 0 - line (I) block
        # index 1 - Z block
        # index 2 - S block
        # index 3 - L block
        # index 4 - J block
        # index 5 - T block
        # index 6 - square (O) block
        self.blockData = [6, 5, 7, 8, (0,165,233), 4, # I
                          6, 1, 2, 7, (228,44,8), 3, # Z
                          6, 2, 3, 5, (124,191,50), 3, # S
                          6, 3, 5, 7, (241,124,28), 3, # L
                          6, 1, 5, 7, (2,93,166), 3, # J
                          6, 2, 5, 7, (143,70,151), 3, # T
                          6, 2, 3, 7, (248,199,0), 2, # O
                          ]

        # cool blue and purple colors VV
        # self.blockData = [6, 5, 7, 8, (165,233,255), 4,
        #                   6, 1, 2, 7, (47,7,255), 3,
        #                   6, 2, 3, 5, (185,54,255), 3,
        #                   6, 3, 5, 7, (120,21,255), 3,
        #                   6, 1, 5, 7, (88,165,255), 3,
        #                   6, 2, 5, 7, (77,151,255), 3,
        #                   6, 2, 3, 7, (200,1,255), 2,
        #                   ]
        # rotation matrix
        self.twoMapClock = [2, 3, 6, 7, 
                            3, 7, 2, 6]
        self.twoMapCounter = [2, 3, 6, 7, 
                              6, 2, 7, 3]
        self.threeMapClock = [1, 2,  3, 5, 6,  7, 9, 10, 11, 
                              3, 7, 11, 2, 6, 10, 1,  5,  9]

        self.threeMapCounter = [1, 2, 3,  5, 6, 7,  9, 10, 11, 
                                9, 5, 1, 10, 6, 2, 11,  7,  3]

        self.fourMapClock = [1, 2,  3,  4, 5, 6,  7,  8, 9, 10, 11, 12, 13, 14, 15, 16, 
                             4, 8, 12, 16, 3, 7, 11, 15, 2,  6, 10, 14,  1,  5,  9, 13]

        self.fourMapCounter = [ 1, 2, 3, 4,  5,  6, 7, 8,  9, 10, 11, 12, 13, 14, 15, 16, 
                               13, 9, 5, 1, 14, 10, 6, 2, 15, 11,  7,  3, 16, 12,  8,  4]
        self.packageRot()
        self.boardSizeX = 10
        self.boardSizeY = 20
        self.board = [] # the board (1s and 0s to indicate filed and unfilled squares)
        self.boardColors = [] # board render colors
        for i in range(self.boardSizeX): # 20 rows of 10 plus 10 1s for the bottom
            self.board.append(1)
            self.boardColors.append((0,0,0))
        for i in range(self.boardSizeX * self.boardSizeY):
            self.board.append(0)
            self.boardColors.append((0,0,0))
        self.renderBoardX = [] # where to draw played pieces (X)
        self.renderBoardY = [] # where to draw played pieces (Y)
        self.renderBoardColor = [] # what color to draw played pieces

        t.setworldcoordinates(-240, -180, 240, 180) # coordinates of screen (absolute, not in pixels)
    def packageRot(self):
        self.rotation = []
        for i in range(97):
            self.rotation.append(0)
        offset = 0
        length = len(self.twoMapClock) >> 1
        for i in range(1, 17): # twoMapClock
            if self.twoMapClock.count(i) > 0:
                self.rotation[i + offset] = self.twoMapClock[self.twoMapClock.index(i) + length]
        offset += 16
        for i in range(1, 17): # twoMapCounter
            if self.twoMapCounter.count(i) > 0:
                self.rotation[i + offset] = self.twoMapCounter[self.twoMapClock.index(i) + length]
        offset += 16

        length = len(self.threeMapClock) >> 1
        for i in range(1, 17): # threeMapClock
            if self.threeMapClock.count(i) > 0:
                self.rotation[i + offset] = self.threeMapClock[self.threeMapClock.index(i) + length]
        offset += 16
        for i in range(1, 17): # threeMapCounter
            if self.threeMapCounter.count(i) > 0:
                self.rotation[i + offset] = self.threeMapCounter[self.threeMapClock.index(i) + length]
        offset += 16

        length = len(self.fourMapClock) >> 1
        for i in range(1, 17): # fourMapClock
            if self.fourMapClock.count(i) > 0:
                self.rotation[i + offset] = self.fourMapClock[self.fourMapClock.index(i) + length]
        offset += 16
        for i in range(1, 17): # fourMapCounter
            if self.fourMapCounter.count(i) > 0:
                self.rotation[i + offset] = self.fourMapCounter[self.fourMapClock.index(i) + length]
    def grid(self, size):
        for i in range(self.boardSizeY): # new system, just check if there's a [1] in the board list
            for j in range(self.boardSizeX):
                if self.board[(i + 1) * self.boardSizeX + j] == 1:
                    self.block(self.boardBounds[0] + (j + 0.5) * self.size, self.boardBounds[1] + (i + 0.5) * self.size, self.size, self.boardColors[(i + 1) * self.boardSizeX + j])
        self.sp.pensize(1)
        self.sp.pencolor(self.themeColors[self.theme + 2])
        self.sp.goto(self.boardBounds[0], self.boardBounds[1])
        self.originX = (self.boardBounds[0] + self.boardBounds[2]) / 2 - size * 0.5
        self.originY = self.boardBounds[1] + size * 18.5
        # self.sp.pendown()
        for i in range(self.boardSizeY + 1):
            self.sp.goto(self.boardBounds[2], self.boardBounds[1] + size * i)
            self.sp.pendown()
            self.sp.goto(self.boardBounds[0], self.boardBounds[1] + size * i)
            self.sp.penup()
        for j in range(self.boardSizeX + 1):
            self.sp.goto(self.boardBounds[0] + size * j, self.boardBounds[1])
            self.sp.pendown()
            self.sp.goto(self.boardBounds[0] + size * j, self.boardBounds[3])
            self.sp.penup()
    def piece(self, x, y, size):
        for i in range(4):
            self.block(x + size * ((self.currentBlock[i] + 3) % 4 - 1), y + size * (int((self.currentBlock[i] - 1) / 4) * -1 + 1), size, self.currentBlock[4])
    def block(self, x, y, size, color=(0, 0, 0)):
        self.sp.goto(x, y) # new system based on stamping
        self.sp.color(color)
        self.sp.stamp()
    def sp3block(self, x, y, size, color=(0, 0, 0)): # special next block renderer
        self.sp3.goto(x, y)
        self.sp3.color(color)
        self.sp3.stamp()
    def refillKey(self, key):
        if self.keyPressed.count(key) > 0:
            ind = self.keyPressed.index(key)
            self.keyPressed[ind + 1] = self.bufferFrames
            if key == 'right' or key == 'left':
                self.keyPressed[ind + 2] -= 1
                if self.keyPressed[ind + 2] <= 0:
                    self.keyPressed[ind + 2] = self.buttonTicksRel
                    if key == 'right':
                        self.moveRight()
                    else:
                        self.moveLeft()
        else:
            self.keyPressed.append(key)
            self.keyPressed.append(self.bufferFrames)
            self.keyPressed.append(self.buttonTicks)
    def removeKey(self, key):
        if self.keyPressed.count(key) > 0:
            ind = self.keyPressed.index(key)
            if self.keyPressed[ind + 1] == 0:
                self.keyPressed.pop(ind)
                self.keyPressed.pop(ind)
                self.keyPressed.pop(ind)
            else:
                self.keyPressed[ind + 1] -= 1
    def control(self):
        if turtools.keyPressed(111) or turtools.keyPressed(38):
            if self.keyPressed.count('up') < 1:
                self.rotateClockwise()
            self.refillKey('up')
        else:
            self.removeKey('up')
        if turtools.keyPressed(52) or turtools.keyPressed(90):
            if self.keyPressed.count('z') < 1:
                self.rotateCounter()
            self.refillKey('z')
        else:
            self.removeKey('z')
        if turtools.keyPressed(113) or turtools.keyPressed(37):
            if self.keyPressed.count('left') < 1:
                self.moveLeft()
            self.refillKey('left')
        else:
            self.removeKey('left')
        if turtools.keyPressed(114) or turtools.keyPressed(39):
            if self.keyPressed.count('right') < 1:
                self.moveRight()
            self.refillKey('right')
        else:
            self.removeKey('right')
        if turtools.keyPressed(116) or turtools.keyPressed(40):
            if self.ticksF > self.downThresh:
                self.ticksF = self.downThresh
        if turtools.keyPressed(65) or turtools.keyPressed(32):
            if self.keyPressed.count('space') < 1:
                self.instaDrop()
            self.refillKey('space')
        else:
            self.removeKey('space')
    def load(self, piece, where):
        piece = piece * 6
        if where == 0: # corresponds to loading to currentBlock
            for i in range(6):
                if len(self.currentBlock) < 6:
                    self.currentBlock.append(0)
                self.currentBlock[i] = self.blockData[piece + i]
        else: # corresponds to loading to nextBlock
            for i in range(6):
                    if len(self.nextBlock) < 6:
                        self.nextBlock.append(0)
                    self.nextBlock[i] = self.blockData[piece + i]
    def setCoordLists(self):
        self.modList = []
        self.divList = []
        for i in range(4):
            self.modList.append((self.currentBlock[i] - 1)  % 4 - 1)
            self.divList.append((m.floor((self.currentBlock[i] - 1) / 4) - 1) * -1)
    def setBounds(self):
        self.setCoordLists()
        self.bounds[0] = min(self.modList)
        self.bounds[1] = min(self.divList)
        self.bounds[2] = max(self.modList)
        self.bounds[3] = max(self.modList)
    def rotateClockwise(self):
        savedValues = self.blockX, self.blockY, self.currentBlock.copy() # lists are pass by reference and therefore must be copied
        for i in range(4):
            self.currentBlock[i] = self.rotation[(self.currentBlock[5] - 2) * 32 + self.currentBlock[i]]
        self.setBounds() # move out from edge
        while self.blockX + self.bounds[0] * self.size < self.boardBounds[0]:
            self.blockX += self.size
        while self.blockX + self.bounds[2] * self.size > self.boardBounds[2]:
            self.blockX -= self.size
        if self.collision():
            self.blockX = savedValues[0] # undo last action if it causes a collision conflict    
            self.blockY = savedValues[1]
            self.currentBlock = savedValues[2]
    def rotateCounter(self):
        savedValues = self.blockX, self.blockY, self.currentBlock.copy()
        for i in range(4):
            self.currentBlock[i] = self.rotation[(self.currentBlock[5] - 2) * 32 + self.currentBlock[i] + 16]
        self.setBounds() # move out from edge
        while self.blockX + self.bounds[0] * self.size < self.boardBounds[0]:
            self.blockX += self.size
        while self.blockX + self.bounds[2] * self.size > self.boardBounds[2]:
            self.blockX -= self.size
        if self.collision():
            self.blockX = savedValues[0] # undo last action if it causes a collision conflict    
            self.blockY = savedValues[1]
            self.currentBlock = savedValues[2]
    def moveLeft(self):
        if self.blockX + self.bounds[0] * self.size - self.size > self.boardBounds[0]: # check for out of bounds
            self.blockX -= self.size
            if self.collision():
                self.blockX += self.size # undo last action if it causes a collision conflict
    def moveRight(self):
        if self.blockX + self.bounds[2] * self.size + self.size < self.boardBounds[2]: # check for out of bounds
            self.blockX += self.size
            if self.collision():
                self.blockX -= self.size # undo last action if it causes a collision conflict
    def instaDrop(self): # perform an instant drop move
        while not self.collision():
            self.ticksF = self.fallTicks
            self.blockY -= self.size
        self.blockY += self.size
        self.newBlock = 1
        self.boardUpdate()
    def checkLines(self):
        lines = []
        for i in range(self.boardSizeY):
            triggerLine = False
            for j in range(self.boardSizeX):
                if self.board[(i + 1) * self.boardSizeX + j] == 0:
                    triggerLine = True
                    break
            if triggerLine == False:
                lines.append(i - len(lines))
        self.lines += len(lines) # add to lines
        if self.lines - self.oldLines == 1: # add to score
            self.score += 40 * self.level
        if self.lines - self.oldLines == 2: # add to score
            self.score += 100 * self.level
        if self.lines - self.oldLines == 3: # add to score
            self.score += 300 * self.level
        if self.lines - self.oldLines == 4: # add to score
            self.score += 1200 * self.level
        if self.lines >= self.level * 10: # add to level
            self.level += 1
            self.defaultTicks = round(self.defaultTicks * 0.9) # for variable framerate
            self.fallTicks = round(self.fallTicks * 0.9) # for static framerate
            self.downThresh = round(self.fallTicks * 0.05)
        for i in lines:
            self.clear(i)
    def clear(self, line): # clear a line
        for i in range(line + 1, self.boardSizeY):
            for j in range(self.boardSizeX):
                self.board[i * self.boardSizeX + j] = self.board[(i + 1) * self.boardSizeX + j]
                self.boardColors[i * self.boardSizeX + j] = self.boardColors[(i + 1) * self.boardSizeX + j]
    def boardPosition(self):
        self.boardX = (self.blockX - self.size / 2 - self.boardBounds[0]) / self.size
        self.boardY = (self.blockY - self.size / 2 - self.boardBounds[1]) / self.size
    def collision(self): # check if block is colliding with objects on the board
        self.boardPosition()
        self.setCoordLists()
        for i in range(4):
            if self.board[round((self.boardX + self.modList[i]) + self.boardSizeX * (self.boardY + self.divList[i])) + self.boardSizeX] == 1:
                # print("collision!")
                return True
        return False
    def boardUpdate(self): # update the board to include the current block's position and orientation
        self.boardPosition()
        self.setCoordLists()
        for i in range(4):
            self.renderBoardX.append(self.blockX + (self.modList[i]) * self.size)
            self.renderBoardY.append(self.blockY + (self.divList[i]) * self.size)
            self.renderBoardColor.append(self.currentBlock[4])
            self.board[round((self.boardX + self.modList[i]) + self.boardSizeX * (self.boardY + self.divList[i])) + self.boardSizeX] = 1
            self.boardColors[round((self.boardX + self.modList[i]) + self.boardSizeX * (self.boardY + self.divList[i])) + self.boardSizeX] = self.currentBlock[4]
        self.checkLines()
    def write(self, level, score, lines):
        if level or score or lines:
            self.sp2.clear()

            self.sp2.goto(160, 120)
            self.sp2.write("level: " + str(self.level), move=False, align='center', font=('Roberto', 20))
            self.oldLevel = self.level

            self.sp2.goto(160, 100)
            self.sp2.write("score: " + str(self.score), move=False, align='center', font=('Roberto', 20))
            self.oldScore = self.score

            self.sp2.goto(160, 80)
            self.sp2.write("lines: " + str(self.lines), move=False, align='center', font=('Roberto', 20))
            self.oldLines = self.lines

            self.sp2.goto(160, 25)
            self.sp2.write("next", move=False, align='center', font=('Roberto', 20))
            self.sp2.goto(120, 20)
            self.sp2.pendown()
            self.sp2.goto(200, 20)
            self.sp2.goto(200, -20)
            self.sp2.goto(120, -20)
            self.sp2.goto(120, 20)
            self.sp2.penup()
    def drawNext(self, x, y, size):
        self.sp3.clear()
        if self.nextBlock[5] == 4:
            x -= self.size * 0.5
            y += self.size * 0.5
        if self.nextBlock[5] == 2:
            x -= self.size * 0.5
        for i in range(4):
            self.sp3block(x + size * ((self.nextBlock[i] + 3) % 4 - 1), y + size * (int((self.nextBlock[i] - 1) / 4) * -1 + 1), size, self.nextBlock[4])
    def variableFramerate(self):
        self.fallTicks = self.defaultTicks * (self.fps / self.defaultFramerate) # adjust fallspeed and other parameters based on current framerate (beta)
        # print(self.fallTicks)
        self.downThresh = round(self.fallTicks * 0.05) # number of ticks between falls when the down arrow key is pressed
        self.buttonTicks = round(self.fallTicks * 0.4) # number of ticks a button is held before it spams the input
        self.buttonTicksRel = round(self.fallTicks * 0.08) # number of ticks between spams of buttons
    def tick(self):
        if not self.gameOver:
            self.sp.clear()
            self.piece(self.blockX, self.blockY, self.size)
            self.grid(self.size)
            self.write(self.oldLevel != self.level, self.oldScore != self.score, self.oldLines != self.lines)
            if self.newBlock == 1:
                self.currentBlockType = self.nextRand # currentBlockType is a number from 0 to 6, representing what piece is currently falling
                self.nextRand = r.randint(0, 6)
                # self.currentBlockType = 0
                self.load(self.currentBlockType, 0)
                self.load(self.nextRand, 1)
                self.drawNext(160, -7, self.size)
                self.newBlock = 0
                self.blockX = self.originX
                self.blockY = self.originY
                self.ticksF = self.fallTicks
                self.setBounds()
                if self.collision():
                    print("Game Over!")
                    print("Level: " + str(self.level))
                    print("Score: " + str(self.score))
                    print("Lines: " + str(self.lines))
                    self.gameOver = True
            if self.ticksF < 1:
                self.ticksF = self.fallTicks
                self.blockY -= self.size
                if self.collision():
                    self.blockY += self.size
                    self.newBlock = 1
                    self.boardUpdate()
            self.ticksF -= 1
            self.control()
        else:
            self.sp.clear()
            self.piece(self.blockX, self.blockY, self.size)
            self.grid(self.size)
            self.write(self.oldLevel != self.level, self.oldScore != self.score, self.oldLines != self.lines)

# mainloop
obj = main()
def tick():
    obj.tick()
    # t.setworldcoordinates(-240, -180, 240, 180) do this to stretch the program on higher resolutions
    t.Screen().update() # do this to keep the program bounded at original resolutions (making the window bigger or smaller won't make things on the screen bigger or smaller)
def variableFramerate():
    obj.frameCount += 1
    obj.curSec = time.gmtime().tm_sec
    if obj.curSec != obj.oldSec:
        obj.oldSec = obj.curSec
        obj.fps = obj.frameCount
        obj.frameCount = 0
        obj.variableFramerate()
        if args.fps:
            print(obj.fps)
if args.variableframerate:
    if tps == 'inf' or tps == 'infinity':
        while True:
            tick()
    else:
        while True:
            t.ontimer(tick(), int(1000/tps))
else:
    if tps == 'inf' or tps == 'infinity':
        while True:
            tick()
            variableFramerate()
    else:
        while True:
            t.ontimer(tick(), int(1000/tps))
            variableFramerate()