import random
from copy import deepcopy
from typing import Dict, List

from utils import bucket_combinations, combine_buckets, new_bucket_coordinate


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


class Knowledge:
    def __init__(self, dependency: set[tuple[int, int]], bombs: int) -> None:
        self.dependency = dependency
        self.bomb_count = bombs

    def __repr__(self) -> str:
        return f"{self.dependency} = {self.bomb_count}"

    def remove_bomb(self, bomb: tuple[int, int]):
        if bomb not in self.dependency:
            return

        self.dependency.remove(bomb)
        self.bomb_count -= 1

    def evaluate(self, model: Dict) -> bool:
        count = 0
        for c in self.dependency:
            count += model[c]

        return count == self.bomb_count

    def remove_safe(self, safe: tuple[int, int]):
        if safe not in self.dependency:
            return

        self.dependency.remove(safe)

    def add_nodes(self, node: tuple[int, int]):
        # only used for bucket_coordinate
        self.dependency.add(node)


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
        self.safe = set()
        self.mines = set()

        # probabilities of each coordinate
        self.knowledge = dict()

        # knowledge helper
        # this is for finding clusters so that in individual cluster
        # we can perform probability
        self.bucket: List[List[Knowledge]] = list()
        # List[Knowledge]
        self.bucket_coordinate: List[Knowledge] = list()

    def mark_safe_move(self, safe: tuple[int, int]):
        i = None
        for val in self.bucket_coordinate:
            if safe in val.dependency:
                i = val.bomb_count

        if i != None:
            for k in self.bucket[i]:
                k.remove_safe(safe)

        self.safe.add(safe)

    def mark_bomb_move(self, bomb: tuple[int, int]):
        i = None
        for val in self.bucket_coordinate:
            if bomb in val.dependency:
                i = val.bomb_count

        if i != None:
            for k in self.bucket[i]:
                k.remove_bomb(bomb)

        self.mines.add(bomb)

    def add_knowledge(self, cell, count):
        # update probabilities after making a move
        self.moves_made.add(cell)
        self.mark_safe_move(cell)

        new_knowledge = set()
        all_cells_surrounding = set()

        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):
                if 0 <= i < self.height and 0 <= j < self.width:
                    all_cells_surrounding.add((i, j))

        new_knowledge = all_cells_surrounding - self.moves_made.union(self.mines)
        new_knowledge = new_knowledge - set(cell)
        new_knowledge = new_knowledge - self.safe
        count = count - len(self.mines.intersection(all_cells_surrounding))

        n = None
        bcn = None
        for k in new_knowledge:
            for bci in range(len(self.bucket_coordinate)):
                if k in self.bucket_coordinate[bci].dependency:
                    n = self.bucket_coordinate[bci].bomb_count
                    bcn = bci

        if n != None and bcn != None:
            self.bucket[n].append(Knowledge(new_knowledge, count))
            for nk in new_knowledge:
                self.bucket_coordinate[bcn].add_nodes(nk)
        else:
            self.bucket.append([Knowledge(new_knowledge, count)])
            self.bucket_coordinate.append(
                (Knowledge(new_knowledge, len(self.bucket) - 1))
            )

        # now see if there are common and combine buckets
        self.bucket = combine_buckets(self.bucket)
        self.bucket_coordinate = new_bucket_coordinate(self.bucket)

        for bt in self.bucket:
            index = []
            for k in range(len(bt)):
                if len(bt[k].dependency) == 0:
                    index.append(k)

            for i in index:
                bt.pop(i)

        # then apply probabilities to each bucket and get result
        for bt in self.bucket:
            d = set([m for k in bt for m in k.dependency])
            model = dict()
            count = dict()
            total = {"total": 0}

            for m in d:
                model[m] = 0
                count[m] = 0

            bucket_combinations(bt, d, model, count, total)

            for i in count:
                self.knowledge[i] = count[i] / total["total"]

        # then remove all the mines with prob = 1
        temp_knowledge = deepcopy(self.knowledge)
        for k in temp_knowledge:
            if temp_knowledge[k] == 1:
                self.mark_bomb_move(k)
                del self.knowledge[k]

        print(self.knowledge)
        print(self.mines)
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
        # make a random move where there are 0.5 and other unknown blocks involved
        available_moves = self.moves - self.moves_made
        available_moves = available_moves - self.mines

        probmore0dot5 = set()
        for cell in self.knowledge:
            if self.knowledge[cell] > 0.5:
                probmore0dot5.add(cell)

        available_moves = available_moves - probmore0dot5
        random_move = random.randint(0, len(available_moves) - 1)

        return list(available_moves)[random_move]
