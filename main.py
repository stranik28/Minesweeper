import random
import re
from string import ascii_lowercase
from cryptography.fernet import Fernet

# Ключ для шифрования/дешифрования файла сохранения игры

cipher_key = "HgSztes5-wt3yM04qm4fmy6vGEY1zgczn_EAy612N1g="
cipher_key = str.encode(cipher_key)

# Функция для начального заполнения игрового поля

def setupgrid(gridsize, start, numberofmines):
    emptygrid = [['0' for _ in range(gridsize)] for _ in range(gridsize)]

    mines = getmines(emptygrid, start, numberofmines)
    for i, j in mines:
        emptygrid[i][j] = 'X'
    grid = getnumbers(emptygrid)
    return grid, mines

# Функция для отображения игрового поля

def showgrid(grid):

    gridsize = len(grid)
    horizontal = '   ' + (4 * gridsize * '-') + '-'
    toplabel = '     '
    for i in ascii_lowercase[:gridsize]:
        toplabel = toplabel + i + '   '

    print(toplabel + '\n' + horizontal)
    for idx, i in enumerate(grid):
        row = '{0:2} |'.format(idx + 1)

        for j in i:
            row = row + ' ' + j + ' |'

        print(row + '\n' + horizontal)

    print('')

# Функция генерации случайных коардинат

def getrandomcell(grid):
    gridsize = len(grid)
    a = random.randint(0, gridsize - 1)
    b = random.randint(0, gridsize - 1)
    return a, b

# Функция получения соседей клетки

def getneighbors(grid, rowno, colno):

    gridsize = len(grid)
    neighbors = []

    for i in range(-1, 2):
        for j in range(-1, 2):
            if i == 0 and j == 0:
                continue
            elif -1 < (rowno + i) < gridsize and -1 < (colno + j) < gridsize:
                neighbors.append((rowno + i, colno + j))
    return neighbors

# Функция заполнения массива mines коардинатами мин

def getmines(grid, start, numberofmines):

    mines = []
    neighbors = getneighbors(grid, *start)

    for i in range(numberofmines):
        cell = getrandomcell(grid)
        while cell == start or cell in mines or cell in neighbors:
            cell = getrandomcell(grid)
        mines.append(cell)

    return mines

# Заполнение ячеек grid

def getnumbers(grid):

    for rowno, row in enumerate(grid):
        for colno, cell in enumerate(row):
            if cell != 'X':
                values = [grid[r][c] for r, c in getneighbors(grid,
                                                              rowno, colno)]
                grid[rowno][colno] = str(values.count('X'))

    return grid


def show(grid, currgrid, row_numb, colno):

    if currgrid[row_numb][colno] != ' ':
        return

    currgrid[row_numb][colno] = grid[row_numb][colno]
    if grid[row_numb][colno] == '0':
        for r, c in getneighbors(grid, row_numb, colno):
            if currgrid[r][c] != 'F':
                show(grid, currgrid, r, c)


def playagain():
    choice = input('Play again? (y/n): ')

    return choice.lower() == 'y'

# Функция обработки введенных данных

def in_data(inputstring, gridsize, helpmessage):
    cell = ()
    flag = False
    message = "Invalid cell. " + helpmessage

    pattern = r'([a-{}])([0-9]+)(f?)'.format(ascii_lowercase[gridsize - 1])
    validinput = re.match(pattern, inputstring)

    if inputstring == 'help':
        message = helpmessage
    if inputstring == 'save':
        return 1

    elif validinput:
        row_number = int(validinput.group(2)) - 1
        colno = ascii_lowercase.index(validinput.group(1))
        flag = bool(validinput.group(3))

        if -1 < row_number < gridsize:
            cell = (row_number, colno)
            message = ''

    return {'cell': cell, 'flag': flag, 'message': message}

# Функция сохранения игры

def save(grid, currgrid, gridsize, mines, flags):
    cipher = Fernet(cipher_key)
    string_grid = str(gridsize)+"@"
    string_currgrid = ""
    string_flag = ""
    string_mines = ""

    for q in grid:
        for a in q:
            string_grid += a
    for q in currgrid:
        for a in q:
            string_currgrid += a
    for i in range(0,len(flags)):
        string_flag += str(flags[i][0])+","+str(flags[i][1]) + " "
    for i in range(0,len(mines)):
        string_mines += str(mines[i][0])+","+str(mines[i][1]) + " "
    if string_flag == '':
        string_flag += "0"

    string_grid = str.encode(string_grid + "@")
    string_currgrid = str.encode(string_currgrid + "@")
    flag = str.encode(string_flag+"@")
    string_mines = str.encode(str(string_mines))
    fil = string_grid + string_currgrid + flag + string_mines
    ecript = cipher.encrypt(fil)

    print('Введите имя партии для сохранения\n')
    name = input()
    name = name + ".txt"
    file = open(name, 'wb')
    file.write(ecript)
    file.close()

# Функция перевода String-to-Matrix

def convertToMatrix(test_str, K):
    temp = [test_str[idx: idx + K] for idx in range(0, len(test_str), K)]
    res = [list(ele) for ele in temp]
    return res

# Функция загрузки сохраненной игры

def load():
    cipher = Fernet(cipher_key)
    print('Введите имя партии которую вы хотите загрузить\n')
    name = input()
    name = name + ".txt"
    file = open(name,'rb')
    q = file.read()
    fil = cipher.decrypt(q)
    fil = fil.decode()
    size,string_grid, string_currgrid,string_flag,numbmines = fil.split("@")

    size = int(size)
    grid = convertToMatrix(string_grid, size)
    currgrid = convertToMatrix(string_currgrid, size)

    if string_flag != "0":
        if(len(string_flag)) > 4:
            flag = list(map(eval,string_flag[:-1].split(" ")))
        else:
            flag = [(int(string_flag[0]),int(string_flag[2]))]
    else:
        flag = []

    if (len(numbmines)) > 4:
        numbmines = list(map(eval, numbmines[:-1].split(" ")))
    else:
        numbmines = [(int(numbmines[0]), int(numbmines[2]))]

    return grid, currgrid, size, flag, numbmines


def main(is_new):
    global mines

    if (is_new):
        print("Введите размер поля")
        gridsize = int(input())
        correct = True
        while correct:
            print("Введите количество мин")
            numMines = int(input())
            if 0 < numMines < gridsize**2:
                correct = False
            else:
                print("Вы ввели некоректное количество мин попробуйте еще раз")

        currgrid = [[' ' for _ in range(gridsize)] for _ in range(gridsize)]
        grid = []
        flags = []
    else:
        grid, currgrid, gridsize,flags, mines = load()
        numMines = len(mines)
        if flags == '0':
            flags = []

    helpless = "Укажите колонку а затем строку (например a5).\nЧтобы добавить/удалить флаг напишите (например a5f).\n "\
               "Для сохранения этой игры напишите 'save' "

    showgrid(currgrid)
    print(helpless + "\nНапишите 'help' чтобы увидеть это сообщение еще раз.\n")
    while True:
        left = numMines - len(flags)
        prompt = input('Введите ячейку ({} мин осталось): '.format(left))
        result = in_data(prompt, gridsize, helpless + '\n')

        if result == 1:
            if not grid:
                print("Сначала сделайте первый ход\n")
            else:
                save(grid, currgrid, gridsize, mines, flags)
                break
        else:
            message = result['message']
            cell = result['cell']

            if cell:
                print('\n\n')

                row_numb, colno = cell
                currcell = currgrid[row_numb][colno]
                flag = result['flag']

                if not grid:
                    grid, mines = setupgrid(gridsize, cell, numMines)

                if flag:
                    if currcell == ' ':
                        currgrid[row_numb][colno] = 'F'
                        flags.append(cell)
                    elif currcell == 'F':
                        currgrid[row_numb][colno] = ' '
                        flags.remove(cell)
                    else:
                        message = 'Cannot put a flag there'

                elif cell in flags:
                    message = 'здесь уже есть флаг'

                elif grid[row_numb][colno] == 'X':
                    print('Game Over\n')
                    showgrid(grid)
                    if playagain():
                        main()
                    return

                elif currcell == ' ':
                    show(grid, currgrid, row_numb, colno)

                else:
                    message = "Эта ячейка уже открыта"

                if set(flags) == set(mines):
                    print(
                        'Поздравляем с победой. \n')
                    showgrid(grid)
                    if playagain():
                        main(True)
                    return

            showgrid(currgrid)
            print(message)


print("Введите load чтобы загрузить сохранённую игру либо start для старта новой")
start = input()
if start == "load":
    main(False)
else:
    main(True)
