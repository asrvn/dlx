import sys; args = sys.argv[1:]
import time; startTime = time.process_time()
import math

# A modern implementation of Dancing Links by Donald Knuth
# (I hope this pays off for another lab)

puzzles = open(args[0]).read().splitlines()

def setGlobals(puzzle):

    global N, W, H, puzzleLength, solutionGrid

    puzzleLength = len(puzzle)

    N = math.floor(math.sqrt(puzzleLength))
    H = int(math.sqrt(N))
    W = N // H

    solutionGrid = [[0] * N for _ in range(N)]

class Node():  # https://docs.python.org/3/tutorial/classes.html#class-objects

    def __init__(self, rowIdx):

        self.up = None
        self.down = None
        self.left = None
        self.right = None

        self.column = None

        self.rowIdx = rowIdx

class ColumnNode(Node):  # https://docs.python.org/3/tutorial/classes.html#inheritance

    def __init__(self, ID):

        super().__init__(None)

        self.ID = ID
        self.size = 0

class Matrix():  # Determine all columns to selectively use for Dancing Links

    def __init__(self, rows):

        rowLength = len(rows)
        colLength = len(rows[0])

        # Necessary as class attributes for the DancingLinks class
        self.h = ColumnNode("h")
        self.columnList = [ColumnNode(idx) for idx in range(colLength)] + [self.h]

        nodeDict = {(row, col):Node(row) for row in range(rowLength) for col in range(colLength) if rows[row][col] == 1}

        # Circularly link the column nodes

        prev = self.columnList[0]

        for current in self.columnList:

            prev.right = current
            current.left = prev

            prev = current

        self.h.right = self.columnList[0]
        self.columnList[0].left = self.h

        # Circularly link the row nodes

        for row in sorted(set(node[0] for node in nodeDict)):

            colIdx = sorted(set(node[1] for node in nodeDict if node[0] == row)) ###

            prev = nodeDict[(row, colIdx[-1])]

            for col in colIdx:
                
                current = nodeDict[(row, col)]

                prev.right = current
                current.left = prev

                prev = current

            current.right = nodeDict[(row, colIdx[0])]
            nodeDict[(row, colIdx[0])].left = current

        # Circularly link the column nodes to the row nodes

        for col in sorted(set(node[1] for node in nodeDict)):

            rowIdx = sorted(set(node[0] for node in nodeDict if node[1] == col)) ###

            column = self.columnList[col]
            column.size = len(rowIdx)

            prev = nodeDict[(rowIdx[-1], col)]

            for row in rowIdx:

                current = nodeDict[(row, col)]
                current.column = column

                prev.down = current
                current.up = prev

                prev = current
                
            column.up = current
            current.down = column
            
            column.down = nodeDict[(rowIdx[0], col)]
            nodeDict[(rowIdx[0], col)].up = column

    def cover(self, c):  # Page 9 https://www.kth.se/social/files/58861771f276547fe1dbf8d1/HLaestanderMHarrysson_dkand14.pdf

        # Temporarily remove the column node from the column header list

        c.right.left = c.left
        c.left.right = c.right
        i = c.down

        while i != c:

            j = i.right

            while j != i:

                j.down.up = j.up
                j.up.down = j.down
                j.column.size -= 1

                j = j.right

            i = i.down

    def uncover(self, c):  # Page 9 https://www.kth.se/social/files/58861771f276547fe1dbf8d1/HLaestanderMHarrysson_dkand14.pdf

        # Restore the column node to the column header list

        i = c.up

        while i != c:

            j = i.left

            while j != i:

                j.column.size += 1  # Page 9 says j.column.size = j.column.size - 1?
                # Corrected by Page 6 https://www.ocf.berkeley.edu/~jchu/publicportal/sudoku/0011047.pdf
                j.down.up = j
                j.up.down = j

                j = j.left

            i = i.up

        c.right.left = c
        c.left.right = c

class DancingLinks():

    def __init__(self, matrix):

        self.matrix = matrix
        self.h = matrix.h
        self.s = (len(matrix.columnList) - 1) * [0]

    def choose_column_object(self, h):  # Page 6 https://www.ocf.berkeley.edu/~jchu/publicportal/sudoku/0011047.pdf

        # Page 8 https://www.kth.se/social/files/58861771f276547fe1dbf8d1/HLaestanderMHarrysson_dkand14.pdf 
        # c = choose_column_object(h) in search

        j = h.right
        ideal = j

        while j != h:

            if j.size < ideal.size:

                ideal = j

            j = j.right

        self.matrix.cover(ideal)

        return ideal  # Most constrained column

    def search(self, k):  # Page 8 https://www.kth.se/social/files/58861771f276547fe1dbf8d1/HLaestanderMHarrysson_dkand14.pdf
        
        # Find a solution to the exact cover problem defined by the matrix

        if self.h.right == self.h:  # All columns have been covered
                
            return self.s
        
        else:  # Still columns to cover, select a column object

            c = self.choose_column_object(self.h)   # Choose the most constrained column
            r = c.down   # Choose the first row in the column

            while r != c:  # Cover all rows in the column

                self.s[k] = r  # Add the row to the solution

                j = r.right

                while j != r:  # Cover all columns in the row

                    self.matrix.cover(j.column)

                    j = j.right

                if search := self.search(k + 1):  # Recursively search for a solution

                    return search
                
                # No solution found, backtrack and reset

                r = self.s[k]
                c = r.column
                j = r.left

                while j != r:   # Uncover all columns in the row

                    self.matrix.uncover(j.column)

                    j = j.left

                r = r.down

            self.matrix.uncover(c)

def constraintList(x, y):

    #  x          y
    #  row        col
    #  row        val
    #  col        val
    #  subblock   val

    return [0] * (x * N + y) + [1] + [0] * (N * N - (x * N + y) - 1)

def unpackList(constraintList):

    return (constraintPos := constraintList.index(1)) // N, constraintPos % N

def compute(grid):

    dlinks = []

    #  Weightage: 9 per dot, 1 per normal value
    #  An additional dot in the puzzle would increase the links by 8 (Subtract 1, add 9)

    for row in range(N):

        for col in range(N):

            subblock = (row // H) * W + col // W

            # Constraint 1: constraintList(row, col)
            # All row and column positions must contain a symbol.

            # Constraint 2: constraintList(row, value)
            # Each row can only contain each symbol once.

            # Constraint 3: constraintList(col, value)
            # Each column can only contain each symbol once.

            # Constraint 4: constraintList(subblock, value)
            # Each subblock can only contain each symbol once.

            if (value := grid[row][col]) == 0:

                for value in range(N):  # N different possible values, append N different constraint lists

                    dlinks.append(constraintList(row, col) + constraintList(row, value) + constraintList(col, value) + constraintList(subblock, value))

                    #  Slow:
                    #  dlinks = constraintList(row, col)
                    #  dlinks.extend(constraintList(row, val))
                    #  dlinks.extend(constraintList(col, val))
                    #  dlinks.extend(constraintList(subblock, val))

            else:  # Value already exists in the grid, append 1 constraint list

                dlinks.append(constraintList(row, col) + constraintList(row, value - 1) + constraintList(col, value - 1) + constraintList(subblock, value - 1))

    search = [dlinks[row] for row in [node.rowIdx for node in DancingLinks(Matrix(dlinks)).search(0) if node != 0]]  # Convert row indices to rows
    result = {(*unpackList(dlink[0:puzzleLength]), unpackList(dlink[puzzleLength:puzzleLength * 2])[1] + 1) for dlink in search}  # Convert rows to coordinates

    for row, col, value in result:  # Convert coordinate + values to a 2D array

        solutionGrid[row][col] = value

    return "".join(str(value) for row in solutionGrid for value in row)  # Convert 2D array to a string

def checkSum(puzzle, puzzleLength):

    sum = 0
    min = puzzle[0]

    for tile in puzzle:

        sum += ord(tile)

        if tile < min:

            min = tile
    
    return sum - ord(min) * puzzleLength

def main():

    puzzleNum = 0

    for puzzle in puzzles:

        puzzleNum += 1
        setGlobals(puzzle)
        parsePuzzle = puzzle.replace(".", "0")  # Compiled regex faster?

        grid = [[int(parsePuzzle[col + row * N]) for col in range(N)] for row in range(N)]
        solution = compute(grid)

        print(f"{puzzleNum}: {puzzle}")
        print(f"{' ' * (int(math.log10(puzzleNum)) + 2)} {solution} {checkSum(solution, puzzleLength)} {time.process_time() - startTime:.3}")

main()
