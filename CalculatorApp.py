import matplotlib.pyplot as plt
import numpy as np
import random
import sys

# pyinstaller -c -F CalculatorApp.py -i "icon.ico" --noconsole

maxPrecision = 10

restricted  = 'bdefghjklmpqruvwyz,_!@#$'
allowed = ['1', '2', '3',
           '4', '5', '6',
           '7', '8', '9',
           '0', 'e', 'π',
           '.', '(', ')',
           '^', '*', '+',
           '%', '/', '-',
           'cos', 'sin', 'tan',
           '.']

bracketException    = 'brackets do not match.'
charException       = 'multiple characters are not supported.'

# general use functions
def RGBtoHex(rgbList):
    hexcodes = []
    
    for rgbIndex, rgb in enumerate(rgbList):
        red = rgbList[rgbIndex][0]
        green = rgbList[rgbIndex][1]
        blue = rgbList[rgbIndex][2]

        hexcodes.append('#{:02x}{:02x}{:02x}'.format(red, green, blue))

    return hexcodes

def MsgExit(strEquation, errortype, message):
    print('Equation:', strEquation)
    sys.exit(f'{errortype} error: {message}')

def ListScrambler(list2d:list) -> list:

    list2d = np.array(list2d)

    listshape = np.shape(list2d)
    listsize = sum(len(c) for c in list2d)
    list2d = list2d.reshape(listsize)
    templist = np.arange(listsize, dtype=object)
    
    i = 0
    while len(list2d) > 0:
        listsize = len(list2d)
        
        chosenIndex = random.randint(0, listsize-1)

        templist[i] = list2d[chosenIndex]
        
        list2d = np.delete(list2d, np.where(list2d == list2d[chosenIndex]))

        i += 1

    list2d = templist.reshape(listshape)
    return list2d.tolist()

def CheckInput(strEquation):
    if any((c in restricted) for c in strEquation):
        raise SyntaxError(charException)
    
    countOpen = 0
    countClosed = 0

    for c in strEquation:
        if c == '(':
            countOpen += 1
        elif c == ')':
            countClosed += 1
    
    if not (countOpen == countClosed):
        raise SyntaxError(bracketException)

def CheckInputAllowed(arrEquation):
    strItems = []

    for c in arrEquation:
        if type(c) == float:
            for c in str(c):
                strItems.append(str(c))
        else:
            strItems.append(str(c))

    allAllowed = all(item in allowed for item in strItems)

    if not allAllowed:
        raise SyntaxError(charException)
    
    countOpen = 0
    countClosed = 0

    for c in arrEquation:
        if c == '(':
            countOpen += 1
        elif c == ')':
            countClosed += 1
    
    if not (countOpen == countClosed):
        raise SyntaxError(bracketException)

def ListToString(list_input):
        items = ''

        for item in list_input:
            items += item
        
        return items

def CountDecimals(string):
    count = 0    
    boolPointIsBehind = False
    minPrecision = 0

    for c in string:
        if boolPointIsBehind:
            count += 1

        if c == '.':
            boolPointIsBehind = True
    
    if len(string) <= 1:
        return minPrecision

    if count > maxPrecision:
        return maxPrecision
    
    return count

def GetPrecision(figs):
    # handle precision
    for figIndex, fig in enumerate(figs):
        figs[figIndex] = CountDecimals(fig)
    
    if len(figs) == 0:
        return maxPrecision
    else:
        return int(min(figs))

class Rainbow:
    def __init__(self, increments, b=np.pi/4):

        # mathematical constants
        self.a = 1/20
        self.b = b
        self.cRed = 0.45
        self.cGreen = 1.8
        self.cBlue = 0.9
        self.d = 1-self.a

        # increment logic
        self.increments = increments
        x = np.arange(increments)+1

        x = x/increments * 2 * np.pi

        self.x = x

        self.redChannel = self.red(x)
        self.greenChannel = self.green(x)
        self.blueChannel = self.blue(x)

    def red(self, x):
        return self.a*np.sin(self.b*x+self.cRed*np.pi)+self.d

    def green(self, x):
        return self.a*np.sin(self.b*x+self.cGreen*np.pi)+self.d

    def blue(self, x):
        return self.a*np.sin(self.b*x-self.cBlue*np.pi)+self.d

    def makeRGB(red, green, blue):
        red = int(red*255)
        green = int(green*255)
        blue = int(blue*255)

        return tuple((red, green, blue))
    
    def get(self):
        rgb = np.array([], dtype=np.int8)
        for xindex, xitem in enumerate(self.x):
            a = Rainbow.makeRGB(self.redChannel[xindex], self.greenChannel[xindex], self.blueChannel[xindex])
            rgb = np.append(rgb, a)
        
        rgb = rgb.reshape(self.increments,3)

        return rgb

class Grapher:
    def __init__(self, strEquation, letters):
        self.strEquation = strEquation
        self.letters = letters

        for c in strEquation:
            if c == '&':
                self.stepsize = 1
                self.maxrange = 100*self.stepsize
                break
                
            else:
                self.stepsize = 0.1
                self.maxrange = 100*self.stepsize

    def Plot(self):
        letter = self.letters[0]

        xrange = np.arange(start=0+self.stepsize, stop=self.maxrange, step=self.stepsize)
        y = np.array([], dtype=object)

        for x in xrange:
            equation = self.strEquation.replace(letter, str(x))
            y = np.append(y, Calculator(equation, False).execute())

        plt.subplots(figsize=(6,5))
        plt.plot(xrange, y)
        plt.legend(letter)
        plt.title(f'equation: {self.strEquation} :3')
        plt.xlabel('x-axis')
        plt.ylabel('y-axis')
        plt.show()

# class with calculator algorithm toolkit
class Calculator:
    def __init__(self, strEquation: str, doSigfigs:bool=True, doGraphing:bool=True):
        # arguments
        self.doSigfigs = doSigfigs
        # self.doGraphing = doGraphing

        self.varContainer   = 'x'
        arrEquation = np.array([], dtype=object)
        arrSide     = np.array([], dtype=object)
        strSide     = ''

        arrTxt      = np.array([], dtype=object)
        strTxt      = ''

        figs     = np.array([], dtype=np.int8)

        if len(strEquation) == 0:
            strEquation = '0'

        strEquation = '(' + strEquation + ')'

        # tokenize
        for c in strEquation:
            if c == '.' or c.isnumeric():
                arrSide = np.append(arrSide, c)

            elif c.isalpha():
                arrTxt = np.append(arrTxt, c)

            else:
                if len(arrTxt) >= 1:
                    strTxt  = ListToString(arrTxt)
                    arrTxt  = np.array([], dtype=object)

                    arrEquation = np.append(arrEquation, strTxt)
                
                if len(arrSide) >= 1:
                    strSide = ListToString(arrSide)
                    arrSide = np.array([], dtype=object)

                    arrEquation = np.append(arrEquation, float(strSide))
                    figs     = np.append(figs, strSide)

                arrEquation = np.append(arrEquation, c)

        if len(arrSide) >= 1:
            strSide = ListToString(arrSide)
            arrSide = np.array([])

            arrEquation = np.append(arrEquation, float(strSide))
            figs     = np.append(figs, strSide)

        # handle special mathematical cases (constants and brackets)
        arrEquation = self.TokenizeSpecialCases(arrEquation)
        strEquation = ''.join(str(c) for c in arrEquation)

        # check for graphing flag
        if doGraphing:
            # graph the equation if (one!) letter is present.
            letters = []
            for c in arrEquation:
                if (c != 'cos' and c != 'sin' and c != 'tan') and type(c) != float and c.isalpha() and c not in letters:
                    
                    letters.append(c)
                    pass
            if len(letters) == 1:
                self.doSigfigs = False
                Grapher(strEquation, letters).Plot()
                raise Exception('graphing...')

        # check if brackets match and all characters are allowed
        CheckInputAllowed(arrEquation)

        self.strEquation    = strEquation
        self.arrEquation    = arrEquation

        # set calculator precision with flag
        if self.doSigfigs:
            self.precision  = GetPrecision(figs)
        else:
            self.precision  = maxPrecision

    def add(self, a:float, b:float):
        return float(a + b)
    
    def subtract(self, a:float, b:float):
        return float(a - b)
    
    def multiply(self, a:float, b:float):
        return float(a * b)
    
    def divide(self, a:float, b:float):
        return float(a / b)

    def modulo(self, a:float, b:float):
        if int(b) == 0:
            b = 1
        return int(a) % int(b)
    
    def exponent(self, a:float, b:float):
        return float(a ** b)
    
    def sinus(self, a:float):
        return float(np.sin(a))

    def cosinus(self, a:float):
        return float(np.cos(a))

    def tangent(self, a:float):
        return float(np.tan(a))
    
    def TokenizeSpecialCases(self, arrEquation:np.array) -> np.array:
        # replace mathematical constants with numerical values.
        arrEquation = np.where(arrEquation == 'π', np.pi, arrEquation)
        arrEquation = np.where(arrEquation == 'e', np.e, arrEquation)

        # turn numbers with minus signs in front of them into negative numbers
        for cIndex, c in enumerate(arrEquation):
            if c == '-' and type(arrEquation[cIndex-1]) != float and arrEquation[cIndex+1] != ')':
                arrEquation[cIndex] = -1*arrEquation[cIndex+1]
                arrEquation = np.delete(arrEquation, cIndex+1)

        # if two brackets are facing away from one another, add a multiplication sign between them
        addMultIndex = []
        
        for cIndex, c in enumerate(arrEquation):
            if (arrEquation[cIndex-1] == ')' or type(arrEquation[cIndex-1]) == float) and c == '(' and cIndex != 0:
                addMultIndex.append(cIndex)

        for cIndex, c in enumerate(arrEquation):
            if (str(arrEquation[cIndex-1]).isalpha() and type(c) == float) or (type(arrEquation[cIndex-1]) == float and str(c).isalpha()):
                addMultIndex.append(cIndex)
        
        arrEquation = np.insert(arrEquation, addMultIndex, '*')

        return arrEquation
        
    def BracketOrder(self) -> np.array:
        arrHierarchy = np.array([], dtype=int)
        intHierarchy = 0

        for c in self.arrEquation:
            if c == '(':
                intHierarchy += 1
                arrHierarchy = np.append(arrHierarchy, intHierarchy)
            
            elif c == ')':
                arrHierarchy = np.append(arrHierarchy, intHierarchy)
                intHierarchy -= 1
            
            else:
                arrHierarchy = np.append(arrHierarchy, intHierarchy)

        maxInHierarchy = max(arrHierarchy)
        alreadyPassedMax = False
        
        for cIndex, c in enumerate(arrHierarchy):
            if c != maxInHierarchy and arrHierarchy[cIndex-1] == maxInHierarchy:
                alreadyPassedMax = True

            elif c == maxInHierarchy and alreadyPassedMax:
                arrHierarchy[cIndex] = maxInHierarchy-1
        
        return arrHierarchy

    def CalculationFocus(self, arrHierarchy) -> np.array:
        
        # assign inside brackets
        maskHierarchy_in = arrHierarchy == max(arrHierarchy)

        firstIndexInside = np.where(maskHierarchy_in == True)[0][0]

        inside = self.arrEquation[maskHierarchy_in]

        # assign outside brackets
        maskHierarchy_out = arrHierarchy != max(arrHierarchy)

        outside = self.arrEquation[maskHierarchy_out]

        outside = np.insert(outside, firstIndexInside, self.varContainer)
        
        return inside, outside

    # calculate inside
    def InnerCalculator(self, inside:np.array) -> np.array:
        # remove brackets if applicable
        inside = np.delete(inside, np.where(inside == '('))
        inside = np.delete(inside, np.where(inside == ')'))

        i = 0
        while len(inside) > 1:
            if i > 10:
                raise Exception('softlock detected! Equation may be ambiguous.')

            OperatorList = []
            for c in inside:
                if type(c) != float:
                    if c == 'sin' or c == 'cos' or c == 'tan':
                        OperatorList.append(4)
                    
                    elif c == '^':
                        OperatorList.append(3)

                    elif c == '*' or c == '/' or c == '%':
                        OperatorList.append(2)

                    elif c == '+' or c == '-':
                        OperatorList.append(1)
            
            maxOperator = max(OperatorList)
            for cIndex, c in enumerate(inside):
                if type(c) != float:
                    if (c == 'sin' or c == 'cos' or c == 'tan') and maxOperator == 4:
                        rightSide = inside[cIndex+1]
                        
                        if c == 'sin':
                            inside[cIndex] = self.sinus(rightSide)

                        elif c == 'cos':
                            inside[cIndex] = self.cosinus(rightSide)

                        else:
                            inside[cIndex] = self.tangent(rightSide)
                        
                        inside = np.delete(inside, cIndex+1)
                        
                        break

                    elif c == '^' and maxOperator == 3:
                        leftSide  = inside[cIndex-1]
                        rightSide = inside[cIndex+1]

                        inside[cIndex] = self.exponent(leftSide, rightSide)

                        inside = np.delete(inside, cIndex+1)
                        inside = np.delete(inside, cIndex-1)

                        break

                    elif (c == '*' or c == '/' or c == '%') and maxOperator == 2:
                        leftSide  = inside[cIndex-1]
                        rightSide = inside[cIndex+1]

                        if c == '*':
                            inside[cIndex] = self.multiply(leftSide, rightSide)
                        elif c == '/':
                            inside[cIndex] = self.divide(leftSide, rightSide)
                        else:
                            inside[cIndex] = self.modulo(leftSide, rightSide)

                        inside = np.delete(inside, cIndex+1)
                        inside = np.delete(inside, cIndex-1)

                        break
        
                    elif (c == '+' or c == '-') and maxOperator == 1:
                        leftSide  = inside[cIndex-1]
                        rightSide = inside[cIndex+1]

                        if c == '+':
                            inside[cIndex] = self.add(leftSide, rightSide)
                        else:
                            inside[cIndex] = self.subtract(leftSide, rightSide)

                        inside = np.delete(inside, cIndex+1)
                        inside = np.delete(inside, cIndex-1)

                        break
            i += 1
            
        return inside

    def execute(self) -> float:
        # bracket order
        arrHierarchy = self.BracketOrder()

        # assign calculation focus
        inside, outside = self.CalculationFocus(arrHierarchy)

        i = 0
        while len(outside) > 1:
            if i > 10:
                raise Exception('softlock detected! Equation may be ambiguous.')

            inside = self.InnerCalculator(inside)

            outside[outside == self.varContainer] = inside
            self.arrEquation = outside

            # account for brackets
            arrHierarchy = self.BracketOrder()

            # assign calculation focus
            inside, outside = self.CalculationFocus(arrHierarchy)

            i += 1

        outside[outside == self.varContainer] = self.InnerCalculator(inside)

        return round(outside[0], self.precision)

# print(Calculator('1x+x').execute())

import tkinter as tk
from tkinter import ttk
from functools import partial

# stylesheet
bgColor = "#CAE1DE"
btnColor = "#ffffff"
btnColorSubmit = "#aaffaa"
btnColorWarn = "#fff6aa"
btnColorExit = "#ffaaaa"
lblColor = "#ffffff"

warnTxtColor = "#ff6666"

strtitle = ':3 Calculator App :3'

txtfont = ('Cascadia Mono', 12)

nums = [['1', '2', '3'],
        ['4', '5', '6'],
        ['7', '8', '9'],
        ['0', 'e', 'π']]

chars = [['.', '(', ')'],
         ['^', '*', '+'],
         ['%', '/', '-'],
         ['cos', 'sin', 'tan']]

class MainGui:
    def __init__(self, master):
        self.master = master

        self.master.title(strtitle)

        # set up grid for frame
        self.master.columnconfigure(0, weight=1)
        self.master.rowconfigure(0, weight=1)

        frame = tk.Frame(self.master)
        frame.configure(background=bgColor)

        frame.grid(column=0, row=0, sticky='new')
        frame.grid_columnconfigure(0, weight=3)

        topframe = tk.Frame(frame)
        topframe.grid(column=0, row=0, columnspan=2, sticky='ew', pady=(0,8))
        topframe.columnconfigure(0, weight=3)

        numinputframe = tk.Frame(frame)
        numinputframe.configure(background=bgColor)
        numinputframe.grid(column=0, row=3, sticky='new', padx=(0,8))

        charinputframe = tk.Frame(frame)
        charinputframe.configure(background=bgColor)
        charinputframe.grid(column=1, row=3, sticky='new')

        btmframe = tk.Frame(frame)
        btmframe.configure(background=bgColor)
        btmframe.grid(column=0, row=4)
        btmframe.columnconfigure(0, weight=3)

        # initiate UI variables/elements
        doGraphing = tk.BooleanVar()
        doGraphing.set(True)
        self.doGraphing = doGraphing

        doPrecision = tk.BooleanVar()
        doPrecision.set(True)
        self.doPrecision = doPrecision

        warn = ttk.Label(topframe, text='', font=txtfont)
        warn.configure(background=bgColor, foreground=warnTxtColor)

        entry = ttk.Entry(topframe, font=txtfont)
        entry.configure(background=lblColor)
        entry.bind('<Return>', self.onReturnWidget)
        
        for i in range(len(nums)):
            numinputframe.grid_columnconfigure(i, weight=3)
        
        for i in range(len(chars)):
            charinputframe.grid_columnconfigure(i, weight=3)

        submit = tk.Button(charinputframe, text='submit', font=txtfont, command=self.calcWidget)
        submit.configure(background=btnColorSubmit)

        delete = tk.Button(charinputframe, text='delete', font=txtfont, command=self.deleteWidget)
        delete.configure(background=btnColorWarn)

        clear = tk.Button(charinputframe, text='clear', font=txtfont, command=self.clearWidget)
        clear.configure(background=btnColorWarn)

        btnexit = tk.Button(charinputframe, text='exit', font=txtfont, command=self.exitWidget)
        btnexit.configure(background=btnColorExit)

        lblmeminfo = ttk.Label(btmframe, text='', font=txtfont)
        lblmeminfo.configure(background=bgColor)

        btnx = tk.Button(btmframe, text='x', font=txtfont, command=partial(self.btnWidget, 'x'))
        if doGraphing.get():
            btnx.configure(state='disabled')
        else:
            btnx.configure(state='normal')
        self.btnx = btnx
        
        btngraph = tk.Button(btmframe, text='graphing', font=txtfont, command=self.graphWidget)
        if doGraphing.get():
            btnx.configure(state='normal')
            btngraph.configure(background=btnColorSubmit)
        else:
            btnx.configure(state='disabled')
            btngraph.configure(background=btnColorExit)
        self.btngraph = btngraph

        btnprec = tk.Button(btmframe, text='sigfigs', font=txtfont, command=self.precWidget)
        if self.doPrecision.get():
            btnprec.configure(background=btnColorSubmit)
        else:
            btnprec.configure(background=btnColorExit)
        self.btnprec = btnprec

        btnrandom = tk.Button(btmframe, text='RANDOMIZE', font=txtfont, command=self.randomWidget)

        btnreset = tk.Button(btmframe, text='reset', font=txtfont, command=self.resetWidget)
        self.btnreset = btnreset

        # place features
        warn.grid(column=0, row=0, sticky='ew')
        self.warn = warn

        entry.grid(column=0, row=1, sticky='ew')
        self.entry  = entry

        numcolors = Rainbow(sum(len(c) for c in nums)).get()
        charcolors = Rainbow(sum(len(c) for c in chars)).get()
        
        numcolors = RGBtoHex(numcolors)
        charcolors = RGBtoHex(charcolors)

        for rowIndex, rowNum in enumerate(nums):
            for colIndex, num in enumerate(rowNum):
                btnIndex = len(nums[0])*rowIndex+colIndex

                numinput = tk.Button(numinputframe, text=num, font=txtfont, command=partial(self.btnWidget, num))
                numinput.configure(background=numcolors[btnIndex], padx=20)
                numinput.grid(column=colIndex, row=rowIndex, sticky='new')
        
        self.numinputframe = numinputframe

        for rowIndex, rowChar in enumerate(chars):
            for colIndex, char in enumerate(rowChar):
                btnIndex = len(nums[0])*rowIndex+colIndex
                
                charinput = tk.Button(charinputframe, text=char, font=txtfont, command=partial(self.btnWidget, char))
                charinput.configure(background=charcolors[btnIndex])
                charinput.grid(column=colIndex, row=rowIndex, sticky='new')

        self.charinputframe = charinputframe

        submit.grid(column=3, row=0, sticky='ns')

        delete.grid(column=3, row=1, sticky='ns')

        clear.grid(column=3, row=2, sticky='new')

        btnexit.grid(column=3, row=3, sticky='new')

        lblmeminfo.grid(column=0, row=4, columnspan=3, sticky='ew')

        btnx.grid(column=0, row=5, sticky='ew')

        btngraph.grid(column=1, row=5, sticky='ew')

        btnprec.grid(column=2, row=5, sticky='ew')

        btnrandom.grid(column=3, row=5, sticky='new')

        btnreset.grid(column=4, row=5, sticky='new')

        frame.pack(padx=8, pady=8)

    def calcWidget(self):
        try:
            equation = self.entry.get()
            sigfigs = self.doPrecision.get()
            graphing = self.doGraphing.get()

            result = Calculator(strEquation=equation, doSigfigs=sigfigs, doGraphing=graphing).execute()
            self.entry.delete(0, tk.END)
            self.entry.insert(0, result)

            self.warn.configure(text='')
        
        except TypeError:
            self.warn.configure(text='Syntax error.')

        except Exception as error:
            print(error)
            self.warn.configure(text=f'Error: {error}')

    def btnWidget(self, char):
        if char == 'cos' or char == 'sin' or char == 'tan':
            self.entry.insert(tk.END, char+'(')
        else:
            self.entry.insert(tk.END, char)

    def deleteWidget(self):
        self.entry.delete(len(self.entry.get())-1)

    def clearWidget(self):
        self.entry.delete(0, tk.END)

    def exitWidget(self):
        sys.exit('Program ended normally')
    
    def graphWidget(self):
        self.doGraphing.set(not self.doGraphing.get())
        if self.doGraphing.get():
            self.btnx.configure(state='normal')
            self.btngraph.configure(background=btnColorSubmit)
        else:
            self.btnx.configure(state='disabled')
            self.btngraph.configure(background=btnColorExit)

    def precWidget(self):
        self.doPrecision.set(not self.doPrecision.get())
        if self.doPrecision.get():
            self.btnprec.configure(background=btnColorSubmit)
        else:
            self.btnprec.configure(background=btnColorExit)

    def onReturnWidget(self, event):
        self.calcWidget()

    def randomWidget(self):

        numcolors = Rainbow(sum(len(c) for c in nums)).get()
        charcolors = Rainbow(sum(len(c) for c in chars)).get()
        
        numcolors = RGBtoHex(numcolors)
        charcolors = RGBtoHex(charcolors)

        randomnums = ListScrambler(nums)
        randomchars = ListScrambler(chars)

        for rowIndex, rowNum in enumerate(randomnums):
            for colIndex, num in enumerate(rowNum):
                btnIndex = len(randomnums[rowIndex])*rowIndex+colIndex

                numinput = tk.Button(self.numinputframe, text=num, font=txtfont, command=partial(self.btnWidget, num))
                numinput.configure(background=numcolors[btnIndex], padx=20)
                numinput.grid(column=colIndex, row=rowIndex, sticky='new')

        for rowIndex, rowChar in enumerate(randomchars):
            for colIndex, char in enumerate(rowChar):
                btnIndex = len(randomchars[rowIndex])*rowIndex+colIndex
                
                charinput = tk.Button(self.charinputframe, text=char, font=txtfont, command=partial(self.btnWidget, char))
                charinput.configure(background=charcolors[btnIndex])
                charinput.grid(column=colIndex, row=rowIndex, sticky='new')      

    def resetWidget(self):
        
        numcolors = Rainbow(sum(len(c) for c in nums)).get()
        charcolors = Rainbow(sum(len(c) for c in chars)).get()
        
        numcolors = RGBtoHex(numcolors)
        charcolors = RGBtoHex(charcolors)

        for rowIndex, rowNum in enumerate(nums):
            for colIndex, num in enumerate(rowNum):
                btnIndex = len(nums[0])*rowIndex+colIndex

                numinput = tk.Button(self.numinputframe, text=num, font=txtfont, command=partial(self.btnWidget, num))
                numinput.configure(background=numcolors[btnIndex], padx=20)
                numinput.grid(column=colIndex, row=rowIndex, sticky='new')

        for rowIndex, rowChar in enumerate(chars):
            for colIndex, char in enumerate(rowChar):
                btnIndex = len(nums[0])*rowIndex+colIndex
                
                charinput = tk.Button(self.charinputframe, text=char, font=txtfont, command=partial(self.btnWidget, char))
                charinput.configure(background=charcolors[btnIndex])
                charinput.grid(column=colIndex, row=rowIndex, sticky='new')

    def checkPressedKey(event):
        # quit
        if event.keycode == 27 or event.keycode == 81:
            sys.exit('Program ended normally')

try:
    root = tk.Tk()
    icon = tk.PhotoImage(file='icon.png')
    root.iconphoto(True, icon)
    root.resizable(False, False)
    root.configure(bg=bgColor)

    MainGui(root)
    root.bind('<KeyRelease>', MainGui.checkPressedKey)

    root.mainloop()
except Exception as error:
    print(error)