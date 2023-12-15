import random
from copy import deepcopy
from typing import Dict, List, Set, Tuple

from utils import Knowledge, bucket_probability, create_buckets


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

        # safe so on future we can remove elements
        self.safe: Set[Tuple[int, int]] = set()
        self.mines: Set[Tuple[int, int]] = set()

        # probabilities of each coordinate
        self.knowledge: Dict[Tuple[int, int], float] = dict()
        self.knowledge_base: List[Knowledge] = list()

    def mark_safe_move(self, safe: Tuple[int, int]):
        for knowledge in self.knowledge_base:
            knowledge.remove_safe(safe)

        self.safe.add(safe)

    def mark_bomb_move(self, bomb: Tuple[int, int]):
        for knowledge in self.knowledge_base:
            knowledge.remove_bomb(bomb)

        self.mines.add(bomb)

    def mark_move_made(self, move: Tuple[int, int]):
        for knowledge in self.knowledge_base:
            knowledge.remove_safe(move)

        self.moves_made.add(move)
        if move in self.knowledge:
            del self.knowledge[move]

    def add_knowledge(self, cell, count):
        # update probabilities after making a move
        self.mark_move_made(cell)

        new_knowledge = set()
        all_cells_surrounding = set()

        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):
                if 0 <= i < self.height and 0 <= j < self.width:
                    all_cells_surrounding.add((i, j))

        new_knowledge = all_cells_surrounding - self.moves_made.union(self.mines)
        new_knowledge = new_knowledge - self.safe
        count = count - len(self.mines.intersection(all_cells_surrounding))

        self.knowledge_base.append(Knowledge(new_knowledge, count))

        # remove set() = 0 from knowledge_base
        new_knowledge_base = []
        for k in self.knowledge_base:
            if len(k.dependency) != 0:
                new_knowledge_base.append(k)
        self.knowledge_base = new_knowledge_base

        # get buckets
        buckets = create_buckets(self.knowledge_base)

        # then get probabilities and update the current knowledge
        for bucket in buckets:
            prob, total = bucket_probability(bucket)

            if len(prob) == 0:
                raise Exception("Empty model returned for bucket_probability")

            # print("total", total)
            for key in prob:
                self.knowledge[key] = prob[key] / total
                # print(key, "key")
                # print(prob[key], "prob[key]")
                # print(self.knowledge[key], "self.knowledge[key]")

        # print(self.knowledge, "knowledge after finding probabilities")
        # then remove all the mines with prob = 1 and prob = 0
        temp_knowledge = deepcopy(self.knowledge)
        for k in temp_knowledge:
            if temp_knowledge[k] == 1:
                self.mark_bomb_move(k)
                del self.knowledge[k]
            elif temp_knowledge[k] == 0:
                self.mark_safe_move(k)
                del self.knowledge[k]

        print(self.knowledge, "probabilities")
        # print(self.knowledge_base, "knowledge_base")
        print(self.mines, "mines")
        return

    def make_safe_move(self):
        # make a move which has probabilities <= 0.5
        if len(self.safe) != 0:
            move = self.safe.pop()
            print("Made safe move", move)
            return move

        move = None
        lowest_prob = 1
        for key in self.knowledge:
            if self.knowledge[key] < lowest_prob:
                move = key
                lowest_prob = self.knowledge[key]

        if lowest_prob >= 0.15:
            move = None

        if move != None:
            print("Made safe move", move)

        return move

    def make_random_move(self):
        # make a random move where there are 0.5 and other unknown blocks involved
        available_moves = self.moves - self.moves_made
        available_moves = available_moves - self.mines

        probmore0dot5 = set()
        for cell in self.knowledge:
            if self.knowledge[cell] > 0.15:
                probmore0dot5.add(cell)

        if available_moves != probmore0dot5:
            available_moves = available_moves - probmore0dot5

        if len(available_moves) < 3:
            for i in range(self.height):
                for j in range(self.width):
                    if (i, j) in self.moves_made:
                        print(".", end="")
                    elif (i, j) in self.mines:
                        print("*", end="")
                    elif (i, j) in self.safe:
                        print("s", end="")
                    else:
                        print(" ", end="")
                print()

        if len(available_moves) == 0:
            return None

        random_move = random.randint(0, len(available_moves) - 1)

        return list(available_moves)[random_move]
