# Woodster Jigsaw Puzzle

This Christmas I was gifted this [extremely difficult jigsaw puzzle](https://www.amazon.com/Bending-Wooden-Labyrinth-Difficult-Puzzles/dp/B08DDFNGV6).

Inspired by day 12 of [Advent of Code 2025](https://adventofcode.com/2025), I decided to make a solver for this puzzle.

**Place holder for demo video**

## Usage

To run the jigsaw puzzle solver, execute the main Python script with the paths to the board and puzzle pictures:

```bash
python main.py --board <path_to_board_image> --puzzle <path_to_puzzle_image>
```

For example:

```bash
python main.py --board images/board.jpg --puzzle images/pieces.jpg
```

## Technology Stack

This project was built using Python 3 along with the following libraries:

- [opencv](https://pypi.org/project/opencv-python/) - For image processing
- [numpy](https://numpy.org/) - For efficient array storage and processing
- [matplotlib](https://matplotlib.org/) - For animating the solving process
