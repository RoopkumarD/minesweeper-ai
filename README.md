# Playing Minesweeper with Probability

Utilizing probability inference to play the Minesweeper game created by CS50AI.

Inspired by [Code Bullet's video on creating a PERFECT Minesweeper AI](https://youtu.be/cGUHehFGqBc?si=gUWhlL9f7gJJBLVC).

This probability engine is not intended for serious use; rather, this project reflects my attempt to implement concepts
learned in a probability class.

For a more advanced probability engine, consider reading [this article](https://www.reddit.com/r/Minesweeper/comments/615ixy/innovative_method_to_calculate_probability/).

## Getting Started

Clone this repository and install the dependencies:

```bash
pip -r requirements.txt
```

Then, execute:

```bash
python runner.py
```

to initiate the game.

## How the Probability Engine Works

After making a move, the engine executes the `add_knowledge` function, incorporating new information obtained by clicking on a
tile.

| A | B |  
| C | D |

For instance, if A has been clicked and reveals a result of 1 (indicating that either B, C, or D is a mine), the new
knowledge can be represented as {A, B, C} = 1.

Subsequently, the function creates groups of knowledge based on shared tiles. For example:

| 1 | D | H |  
| A | E | I |  
| B | F | J |  
| C | G | 1 |

This results in two buckets: one containing {A, D, E} = 1 and another containing {F, J, G} = 1.

For each bucket, the function generates all possible states and calculates the probability for each cell by dividing number
of all states where that cell is mine by the total possible states.

Finally, to eliminate redundant cells with probabilities of 0 or 1, these cells are removed from the knowledge base and added
to the sets of safe and mined cells.

## How AI Determines its Moves

Initially, the AI checks for cells with a probability of 0 (here the probability is probability of cell being mine).
If none are found, it selects a cell with a probability less than 0.125.

If no cells have a probability less than 0.125, the AI makes a random move. If there are cells with probabilities in the
range of 0.125 < p < 0.5, it removes cells with p ≥ 0.5; otherwise, it utilizes any available cell in this range.
