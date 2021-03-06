import requests
import datetime
import re
import ricochet
import model
import http.client
#/home/kwazinator/PycharmProjects/robits/venv/lib/python3.5/site-packages/selenium
from selenium import webdriver #http://stanford.edu/~mgorkove/cgi-bin/rpython_tutorials/Scraping_a_Webpage_Rendered_by_Javascript_Using_Python.php
from selenium.webdriver.chrome.options import Options
from pyvirtualdisplay import Display
import os
import sys

SHAPES = ['H', 'C', 'T', 'S']

def getSolution(thesolutions):
    result = ""
    for solution in thesolutions:
        for move in solution:
            if (move[0] == 'G'):
                result += "blue "
            elif (move[0] == 'Y'):
                result += "yellow "
            elif (move[0] == 'B'):
                result += "red "
            elif (move[0] == 'R'):
                result += "green "
            if (move[1] == 'N'):
                result += "up "
            elif (move[1] == 'S'):
                result += "down "
            elif (move[1] == 'E'):
                result += "right "
            elif (move[1] == 'W'):
                result += "left "
        result = result[:-1]
        result += '\n'
    linedata = result.splitlines() #split lines by \n
    z, v = 30, 5
    solutions = [["" for x in range(z)] for y in range(v)]
    for x, line in enumerate(linedata):
        liner = line.split(" ") #split lines by whitespace
        for y, line2 in enumerate(liner):
            solutions[x][y] = line2
    return solutions

def createStorePost(solutions, goals):
    arraysolutions = [{} for n in range(5)]
    for x, solutionNum in enumerate(solutions):
        arraysolutions[x] = {"solution": [], "goal": goals[x], "goalColor": goals[x][2]}
        for lineNum in solutionNum:
            if '' != lineNum:
                arraysolutions[x]['solution'] += [lineNum]
    return arraysolutions


def getHeaders():
    headers = {
        "Connection": "keep-alive",
        "Content-length": 16,
        "Content-type": "application/json; charset=utf-8",
        "Date": datetime.datetime.now(),
        "Etag": "W/\"10-oV4hJxRVSENxc/wX8+mA4/Pe4tA\"",
        "Server": "Cowboy",
        "Via": "1.1 vegur",
        "X-Powered-By": "Express"
    }
    return headers


def findLeftWalls(boardData, width, height):
    walls = [["" for n in range(16)] for x in range(16)]
    xNumPixelsPerSquare = int(height / 16)
    yNumPixelsPerSquare = int(width / 16)
    Horoffset = 3 * width * 4  # offset to put "line to check" in middle of squares
    Veroffset = 0  # 3*4
    for row in range(16):
        for column in range(16):
            if boardData[
               (row * width * 4 * yNumPixelsPerSquare + column * xNumPixelsPerSquare * 4 + Horoffset + Veroffset):(
                       row * width * 4 * yNumPixelsPerSquare + column * 4 * xNumPixelsPerSquare + 4 + Veroffset + Horoffset)] == [
                0, 0, 0, 255]:
                walls[row][column] += 'W'
                if column > 0:
                    walls[row][column-1] += 'E'
    return walls


def postDiscord(moves):
    # system library for getting the command line argument
    # your webhook URL
    webhookurl = "https://discordapp.com/api/webhooks/534861126723174400/AVmFD9SmF3_xoqXTCLbX08Bhp3MHKDjQ690DKvBY0_oUQZxIy_lHGjT9Tmz4XLOzXxD6"

    # compile the form data (BOUNDARY can be anything)
    formdata = "------:::BOUNDARY:::\r\nContent-Disposition: form-data; name=\"content\"\r\n\r\n" + str(moves) + "\r\n------:::BOUNDARY:::--"

    # get the connection and make the request
    connection = http.client.HTTPSConnection("discordapp.com")
    connection.request("POST", webhookurl, formdata, {
        'content-type': "multipart/form-data; boundary=----:::BOUNDARY:::",
        'cache-control': "no-cache",
    })
    # get the response
    response = connection.getresponse()
    result = response.read()
    # return back to the calling function with the result
    return result.decode("utf-8")


def findUpWalls(leftwalls, boardData, width, height):
    xNumPixelsPerSquare = int(height / 16)
    yNumPixelsPerSquare = int(width / 16)
    Horoffset = 0  # offset to put "line to check" in middle of squares
    Veroffset = int(xNumPixelsPerSquare / 2) * 4  # 20*4
    for row in range(16):
        for column in range(16):
            if boardData[
               (row * width * 4 * yNumPixelsPerSquare + column * xNumPixelsPerSquare * 4 + Horoffset + Veroffset):(
                       row * width * 4 * yNumPixelsPerSquare + column * 4 * xNumPixelsPerSquare + 4 + Veroffset + Horoffset)] == [
                0, 0, 0, 255]:
                leftwalls[row][column] += 'N'
                if row > 0:
                    leftwalls[row-1][column] += 'S'
    return leftwalls


def convertstringcolor(string):
    val = ""
    if "green" in string:
       val = 'H'
    elif "yellow" in string:
        val = 'C'
    elif "red" in string:
        val = 'S'
    else:
        val = 'T'
    return val


#0 = upper left  1 = upper right 2 = lower left 3 = lower right
def getQuads(wallarray, goals):
    quads = [["" for n in range(4)] for x in range(5)]
    for z, board in enumerate(wallarray):
        for y, row in enumerate(board):
            for x, column in enumerate(row):
                if y < 8 and x < 8:
                    quads[z][0] += column
                    if goals[z][0] == y and goals[z][1] == x:
                        quads[z][0] += convertstringcolor(goals[z][2]) + ','
                    else:
                        quads[z][0] += ','
                elif y < 8 and x >= 8:
                    quads[z][1] += column
                    if goals[z][0] == y and goals[z][1] == x:
                        quads[z][1] += convertstringcolor(goals[z][2]) + ','
                    else:
                        quads[z][1] += ','
                elif y >= 8 and x < 8:
                    quads[z][2] += column
                    if goals[z][0] == y and goals[z][1] == x:
                        quads[z][2] += convertstringcolor(goals[z][2]) + ','
                    else:
                        quads[z][2] += ','
                else:
                    quads[z][3] += column
                    if goals[z][0] == y and goals[z][1] == x:
                        quads[z][3] += convertstringcolor(goals[z][2]) + ','
                    else:
                        quads[z][3] += ','


    for x, quad in enumerate(quads):
        for y, lists in enumerate(quad):
            quads[x][y] = lists[:-1]
    print(quads)
    return quads

def getBoards(walls,robits,goals):
    for robot in robits:
        posx = robot[0]
        posy = robot[1]
        if "green" in robot[2]:
            col = 'G'
        elif "red" in robot[2]:
            col = 'R'
        elif "yellow" in robot[2]:
            col = 'Y'
        elif "blue" in robot[2]:
            col = 'B'
        else:
            col = 'X'
        if walls[posx][posy] == 'X':
            walls[posx][posy] = col
        else:
            walls[posx][posy] += col
    wallarray = [walls for n in range(5)]
    boardQuads = getQuads(wallarray, goals)
    return boardQuads


def getCanvasData():
    chrome_options = Options()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    # download the chrome driver from https://sites.google.com/a/chromium.org/chromedriver/downloads and put it in the
    # current directory
    #chrome_driver = os.getcwd() +"\\chromedriver.exe"
    browser = webdriver.Chrome(chrome_options = chrome_options)
    getURL = "http://www.robotreboot.com/challenge"
    browser.get(getURL)
    javascript = "canv = document.querySelector(\"canvas\"); canv2D = canv.getContext(\"2d\"); return canv2D.getImageData(0,0,canv.width,canv.height);"
    newdata = browser.execute_script(javascript)
    browser.close()
    return newdata


def getConfig():
    URL = "http://www.robotreboot.com/challenge/config"
    rget = requests.get(url=URL, params="")
    return rget.json()


def getWalls(boardData):
    leftwalls = findLeftWalls(boardData['data'], boardData['width'], boardData['height'])
    upwalls = findUpWalls(leftwalls, boardData['data'], boardData['width'], boardData['height'])
    for x, array in enumerate(upwalls):
        for y, attribute in enumerate(array):
            if y == 15:
                leftwalls[x][y] += 'E'
            if x == 15:
                leftwalls[x][y] += 'S'
            if attribute == '' and x != 15 and y != 15:
                leftwalls[x][y] = 'X'
    return leftwalls


def formatmessage(message):
    strtopost = ""
    for message1 in message:
        for message2 in message1:
            if message2 == "green":
                strtopost += ":g_"
            elif message2 == "blue":
                strtopost += ":b_"
            elif message2 == "red":
                strtopost += ":r_"
            elif message2 == "yellow":
                strtopost += ":y_"
            elif message2 == "up":
                strtopost += "U: "
            elif message2 == "down":
                strtopost += "D: "
            elif message2 == "left":
                strtopost += "L: "
            elif message2 == "right":
                strtopost += "R: "
            else:
                strtopost += ""
        strtopost += "\n"
    p = re.compile('(:b_D:)')
    strtopost = p.sub('<:b_D:534863114018226176>', strtopost, count=0)
    p = re.compile('(:b_U:)')
    strtopost = p.sub('<:b_U:534863131978104853>', strtopost, count=0)
    p = re.compile('(:b_L:)')
    strtopost = p.sub('<:b_L:534863145471180800>', strtopost, count=0)
    p = re.compile('(:b_R:)')
    strtopost = p.sub('<:b_R:534863560304623642>', strtopost, count=0)
    p = re.compile('(:g_U:)')
    strtopost = p.sub('<:g_U:534863064487428106>', strtopost, count=0)
    p = re.compile('(:g_D:)')
    strtopost = p.sub('<:g_D:534862990739111937>', strtopost, count=0)
    p = re.compile('(:g_L:)')
    strtopost = p.sub('<:g_L:534863071911346197>', strtopost, count=0)
    p = re.compile('(:g_R:)')
    strtopost = p.sub('<:g_R:534863044606689320>', strtopost, count=0)
    p = re.compile('(:r_U:)')
    strtopost = p.sub('<:r_U:534827521925971987>', strtopost, count=0)
    p = re.compile('(:r_D:)')
    strtopost = p.sub('<:r_D:534827269475139624>', strtopost, count=0)
    p = re.compile('(:r_L:)')
    strtopost = p.sub('<:r_L:534827750582648885>', strtopost, count=0)
    p = re.compile('(:r_R:)')
    strtopost = p.sub('<:r_R:534827476518567973>', strtopost, count=0)
    p = re.compile('(:y_U:)')
    strtopost = p.sub('<:y_U:534863097417039902>', strtopost, count=0)
    p = re.compile('(:y_D:)')
    strtopost = p.sub('<:y_D:534863081730473986>', strtopost, count=0)
    p = re.compile('(:y_L:)')
    strtopost = p.sub('<:y_L:534863105415446548>', strtopost, count=0)
    p = re.compile('(:y_R:)')
    strtopost = p.sub('<:y_R:534863089426890753>', strtopost, count=0)
    print(strtopost)
    return strtopost




def getRobots(robits):
    result = [int for n in range(4)]
    for x, robot in enumerate(robits):
        result[x] = robot[1] + robot[0] * 16
    return result

def placeGoals(grid,goals):
    green,yellow,red,blue = 0,0,0,0
    result = ["" for n in range(5)]
    for x, goal in enumerate(goals):
        if "green" in goal[2]:
            colshape = 'G'
            colshape += SHAPES[green]
            green += 1
        elif "red" in goal[2]:
            colshape = 'R'
            colshape += SHAPES[red]
            red += 1
        elif "yellow" in goal[2]:
            colshape = 'Y'
            colshape += SHAPES[yellow]
            yellow += 1
        elif "blue" in goal[2]:
            colshape = 'B'
            colshape += SHAPES[blue]
            blue += 1
        result[x] = colshape
        grid[goal[1] + goal[0]*16] += colshape
    return result


def callback():
    return

def solve(username):
    boardData = getCanvasData()
    walls = getWalls(boardData)
    data = getConfig()
    config = data['config']
    oldconfig = config
    challengeID = data['challengeId']
    goals = data['goals']
    robots = data['robots']
    # sort
    for x in range(4):
        if "green" in robots[x][2]:
            green = robots[x]
        elif "yellow" in robots[x][2]:
            yellow = robots[x]
        elif "blue" in robots[x][2]:
            blue = robots[x]
        elif "red" in robots[x][2]:
            red = robots[x]
    robots[0] = green
    robots[1] = blue
    robots[2] = red
    robots[3] = yellow
    print(walls)
    print(robots)
    print(goals)
    grid = []
    for wall in walls:
        grid += wall
    robits = getRobots(robots)
    listTokens = placeGoals(grid, goals)
    colorz = ['' for n in range(4)]
    for x, robot in enumerate(robots):
        if "green" in robot[2]:
            colorz[x] = 'G'
        elif "red" in robot[2]:
            colorz[x] = 'R'
        elif "yellow" in robot[2]:
            colorz[x] = 'Y'
        elif "blue" in robot[2]:
            colorz[x] = 'B'
    paths = [[] for n in range(5)]
    for x, tokenz in enumerate(listTokens):
        paths[x] = ricochet.search(model.Game(grid=grid, robots=robits, col=colorz, token=tokenz))
    solutions = getSolution(paths)
    if username is not '':
        print('will do something')
    return formatmessage(solutions)

if __name__ == "__main__":
    username = ''
    print(sys.argv[1])
    if sys.argv[1] == '--post':
        username = input("What is the username to submit: ")
    answer = solve(username)
    print(answer)
    





