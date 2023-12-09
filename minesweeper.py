import copy
import random

from utils import nCr


class Minesweeper:
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):
        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):
                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class MinesweeperAI:
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):
        # Set initial height and width
        self.height = height
        self.width = width

        self.moves = set()
        for i in range(8):
            for j in range(8):
                self.moves.add((i, j))

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # mines, if the probability of block is 1, then add it to this
        self.mines = set()

        # probabilities of each coordinate
        self.knowledge = dict()

    def add_knowledge(self, cell, count):
        # update probabilities after making a move
        self.moves_made.add(cell)

        new_knowledge = set()
        all_cells_surrounding = set()

        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):
                if 0 <= i < self.height and 0 <= j < self.width:
                    all_cells_surrounding.add((i, j))

        new_knowledge = all_cells_surrounding - self.moves_made.union(self.mines)
        new_knowledge = new_knowledge - set(cell)
        count = count - len(self.mines.intersection(all_cells_surrounding))

        if count == 0:
            probability_value = 0
        else:
            length = len(new_knowledge)
            probability_value = nCr(length, count - 1) / nCr(length, count)

        for c in new_knowledge:
            if c in self.knowledge:
                if self.knowledge[c] != 0 or self.knowledge[c] != 1:
                    self.knowledge[c] = probability_value
            else:
                self.knowledge[c] = probability_value

        copied_dict = copy.deepcopy(self.knowledge)
        for c in copied_dict:
            if self.knowledge[c] == 1:
                self.mines.add(c)
                del self.knowledge[c]

        print(self.knowledge)
        return

    def make_safe_move(self):
        # make a move which has probabilities <= 0.5
        move = None
        lowest_prob = 1
        for key in self.knowledge:
            if self.knowledge[key] < lowest_prob:
                move = key
                lowest_prob = self.knowledge[key]

        if lowest_prob >= 0.5:
            move = None

        if move != None:
            print("Made safe move", move)
            self.moves_made.add(move)
            del self.knowledge[move]

        return move

    def make_random_move(self):
        # if there are not any moves with less than or equal to 0.5, then make a random move
        # also remove mines from available moves
        available_moves = self.moves - self.moves_made.union(self.mines)

        random_move = random.randint(0, len(available_moves) - 1)

        move = list(available_moves)[random_move]
        print("Made random move", move)
        return move
