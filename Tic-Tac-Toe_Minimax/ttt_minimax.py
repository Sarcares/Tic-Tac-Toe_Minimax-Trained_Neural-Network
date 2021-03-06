#!/usr/bin/env python3
# -*- coding: utf-8 -*-
################################################################################################
#  _____ _          _____               _____                                        __    __  #
# /__   (_) ___    /__   \__ _  ___    /__   \___   ___      /\/\    /\/\         /\ \ \/\ \ \ #
#   / /\/ |/ __| __  / /\/ _` |/ __| __  / /\/ _ \ / _ \    /    \  /    \ _____ /  \/ /  \/ / #
#  / /  | | (__ (__)/ / | (_| | (__ (__)/ / | (_) |  __/   / /\/\ \/ /\/\ \_____/ /\  / /\  /  #
#  \/   |_|\___|    \/   \__,_|\___|    \/   \___/ \___|   \/    \/\/    \/     \_\ \/\_\ \/   #
#                                                                                              #
# (c) July 2017 by Luca Mannella                                                               #
# Tic-Tac-Toe Minimax-Neural Network is distributed under GNU GENERAL PUBLIC LICENSE v.3       #
#                                                                                              #
################################################################################################
import copy
import logging
import math
import os
import random
import sys

VERSION = "v0.2"

COMBINATIONS = 19683
WIN_SCORE = 10
T_T_PERC = 0.6  # Training/Testing percentage

# Files
OUTPUT_FILENAME = "ttt_config.txt"
TRAINING_FILENAME = os.path.join("..", "files", "nn_training.txt")
TESTING_FILENAME = os.path.join("..", "files", "nn_testing.txt")
MATLAB_INPUT = os.path.join("..", "files", "nn_input.txt")
MATLAB_OUTPUT = os.path.join("..", "files", "nn_output.txt")

""" Modify these variable to enable/disable debug functionalities """
TEST = False
GENERATE_OUTPUT_FILE = False
FOR_MATLAB = True

VERBOSE = True


def main_generate_output(output_file_name):
    """ This function generates all the valid combination of a Tic-Tac-Toe game and it write them on an output_file """
    count = 0
    board = [0, 0, 0, 0, 0, 0, 0, 0, 0]
    out_file = open(output_file_name, "w")

    for a in range(3):
        if a == 0:
            board[0] = 0
        elif a == 1:
            board[0] = -1
        else:
            board[0] = 1

        for b in range(3):
            if b == 0:
                board[1] = 0
            elif b == 1:
                board[1] = -1
            else:
                board[1] = 1

            for c in range(3):
                if c == 0:
                    board[2] = 0
                elif c == 1:
                    board[2] = -1
                else:
                    board[2] = 1

                for d in range(3):
                    if d == 0:
                        board[3] = 0
                    elif d == 1:
                        board[3] = -1
                    else:
                        board[3] = 1

                    for e in range(3):
                        if e == 0:
                            board[4] = 0
                        elif e == 1:
                            board[4] = -1
                        else:
                            board[4] = 1

                        for f in range(3):
                            if f == 0:
                                board[5] = 0
                            elif f == 1:
                                board[5] = -1
                            else:
                                board[5] = 1

                            for g in range(3):
                                if g == 0:
                                    board[6] = 0
                                elif g == 1:
                                    board[6] = -1
                                else:
                                    board[6] = 1

                                for h in range(3):
                                    if h == 0:
                                        board[7] = 0
                                    elif h == 1:
                                        board[7] = -1
                                    else:
                                        board[7] = 1

                                    for i in range(3):
                                        if i == 0:
                                            board[8] = 0
                                        elif i == 1:
                                            board[8] = -1
                                        else:
                                            board[8] = 1

                                        if is_playable(board):
                                            # __loop_function is called only if the configuration is valid!
                                            __loop_function(board, out_file)
                                            count += 1

    out_file.close()
    print(str(count) + " valid configuration were generated! The output was written in " + OUTPUT_FILENAME)
    return


def __loop_function(board, out_file):
    """ This function is called for each valid configuration of the board.
        It looks if a player can play and then it choose the best move for the player(s).
        It creates a configuration useful to train a neural-network according to the syntax of generate_training_string,
        this configuration will be written on the file (already open) given as parameter.

    :param board: The board of the game (an array of 9 elements), it must contains only [-1, 0, +1] values
    :param out_file: The output file on which you want to write (it must be already opened!)
    """
    players = who_is_next(board)
    for p in players:
        if p == 0:  # additional check to be sure to not generate wrong configurations
            logging.error("Invalid configuration generated!!! ", generate_training_string(board, p, -11))
        else:
            move = next_move(board, p)
            output = generate_training_string(board, p, move)
            out_file.write(output + "\n")
            if VERBOSE:
                logging.info(output)

    return


def is_playable(board):
    """ This function checks if the configuration is considerable playable or not.
        A configuration is considered playable if in the board the difference between X and O is at most equal to 1.

    :param board: The board of the game (an array of 9 elements), it must contains only [-1, 0, +1] values
    :return: True if the configuration is acceptable, False otherwise.
    """
    if is_winner(board):
        return False

    x_count = board.count(1)
    o_count = board.count(-1)

    if math.fabs(x_count - o_count) > 1:
        return False
    else:
        return True


def is_playable_for(board, player):
    """ This function checks if the configuration is considerable playable or not for a given player.
        A configuration is considered playable if in the board the difference between X and O is at most equal to 1.

    :param board: The board of the game (an array of 9 elements), it must contains only [-1, 0, +1] values
    :param player: Who is the player that has to play now [ +1 (X) or -1 (O) ]
    :return: True if the configuration is acceptable, False otherwise.
    """
    if is_winner(board):
        return False

    x_count = board.count(1)
    o_count = board.count(-1)

    if math.fabs(x_count - o_count) > 1:
        return False
    elif(x_count > o_count) and player == 1:
        return False
    elif(o_count > x_count) and player == -1:
        return False
    else:
        return True


def who_is_next(board):
    """ This function returns a value or an array that contains the player(s) that can play the next move.
        If the game is already won or if the configuration is not valid the function returns 0.

    :param board: The board of the game (an array of 9 elements), it must contains only [-1, 0, +1] values
    :return: 0 if the game is already won or if it is invalid, +1 or -1 if only one of the two players can play or
             an array with both values if the board is in a tie state.
    """
    if is_winner(board):
        return [0]

    x_count = board.count(1)
    o_count = board.count(-1)

    if math.fabs(x_count - o_count) > 1:
        return [0]
    elif x_count > o_count:
        return [-1]
    elif x_count < o_count:
        return [1]
    else:
        return [1, -1]


def is_winner(board):
    """ This function return true if the board is in a winning state.

        :param board: The board of the game (an array of 9 elements), it must contains only [-1, 0, +1] values
        :return: True if the board is in a winning state, False otherwise.
    """
    # checking rows
    # when we have a winning configuration we will have only one element in the set
    for i in range(3):
        value_set = set(board[i * 3: i * 3 + 3])
        if len(value_set) is 1 and board[i * 3] is not 0:
            return True

    # checking columns
    for i in range(3):
        if (board[i] is board[i + 3]) and (board[i] is board[i + 6]) and board[i] is not 0:
            return True

    # checking diagonals
    if board[0] is board[4] and board[4] is board[8] and board[4] is not 0:
        return True
    if board[2] is board[4] and board[4] is board[6] and board[4] is not 0:
        return True

    # There is no winning configuration
    return False


def is_tie(board):
    """ This function returns True if there are empty cell on the board, False otherwise.

    :param board: The board of the game (an array of 9 elements), it must contains only [-1, 0, +1] values
    :return: True if there are empty cell on the board, False otherwise.
    """
    for i in board:
        if i == 0:
            return False
    return True


def someone_won(board):
    """ This function returns true if the board is in a winning state and a value that represents who is the winner.

    :param board: The board of the game (an array of 9 elements), it must contains only [-1, 0, +1] values
    :return: True if the board is in a winning state, False and 0 otherwise.
             If the board is in a winning state, the function returns also who is the winner.
    """
    # checking rows
    # when we have a winning configuration we will have only one element in the set
    for i in range(3):
        value_set = set(board[i*3: i*3 + 3])
        if len(value_set) is 1 and board[i*3] is not 0:
            return True, value_set.pop()

    # checking columns
    for i in range(3):
        if (board[i] is board[i+3]) and (board[i] is board[i+6]) and board[i] is not 0:
            return True, board[i]

    # checking diagonals
    if board[0] is board[4] and board[4] is board[8] and board[4] is not 0:
        return True, board[4]
    if board[2] is board[4] and board[4] is board[6] and board[4] is not 0:
        return True, board[4]

    # There is no winning configuration
    return False, 0


def next_move(board, player):
    """ Computes the next move for a player given the current board state.
        If the board is full or if a player already won the game -1 is returned.

    :param board: The board of the game (an array of 9 elements), it must contains only [-1, 0, +1] values
    :param player: Who is the player that has to play now [ +1 (X) or -1 (O) ]
    :return: The position where the player have to play the next move (or -1 if no one can play)
    """
    # Additional_checks
    res = someone_won(board)
    if res[0]:
        return -1
    elif is_tie(board):
        return -1

    # If the board is empty the best move is to put your symbol in the center
    if len(set(board)) == 1:
        return 4

    n_move, score = __minimax(board, player)
    return n_move


def __minimax(board, player):
    """ This function returns the best move and the relative score for the given player.
        The function assumes that a move is always feasible.

    :param board: The board of the game (an array of 9 elements), it must contains only [-1, 0, +1] values
    :param player: Who is the player that has to play now [ +1 (X) or -1 (O) ]
    :return: The position where the player have to play the next move and the relative score
    """
    # Next player initialization
    next_player = 1 if player == -1 else -1

    # empty cells evaluations
    empty_cells = []  # list for storing the indexes where "0" appears
    for i in range(len(board)):
        if board[i] == 0:
            empty_cells.append(i)

    res_dict = {}  # dictionary for appending the result
    # evaluate all the possibilities
    for i in empty_cells:
        board[i] = player
        score = evaluation_function(board)

        # Termination condition
        x = someone_won(board)
        if x[0]:
            board[i] = 0  # backtracking
            return i, score
        elif is_tie(board):
            board[i] = 0  # backtracking
            return i, score
        else:
            res_dict[i] = score

        n_move, next_score = __minimax(board, next_player)

        res_dict[i] += next_score
        board[i] = 0  # backtracking

    # fetching the best move
    best_move = -1
    if player == 1:
        # X is playing, we have to maximize
        best_score = -1000
        for k in res_dict.keys():
            score = res_dict[k]
            if score > best_score:
                best_score = score
                best_move = k
    else:
        # O is playing, we have to minimize
        best_score = 1000
        for k in res_dict.keys():
            score = res_dict[k]
            if score < best_score:
                best_score = score
                best_move = k

    return best_move, best_score


def evaluation_function(board):
    """ This function return the evaluation value of the grid at the actual state of the game.
        The score will be positive if X (+1) is winning or negative if O (-1) is winning

    :param board: The board of the game (an array of 9 elements), it must contains only [-1, 0, +1] values
    :return: The score of the current situation of the grid
    """
    result = someone_won(board)
    if result[0]:
        return WIN_SCORE * result[1]

    x_score = __partial_score(board, 1)
    o_score = __partial_score(board, -1)

    return x_score - o_score


def __partial_score(board, player):
    """ This function calculate the score of a player given the actual situation o the board.

    :param board: The board of the game (an array of 9 elements), it must contains only [-1, 0, +1] values
    :param player: The player that we have to consider in the score calculation [ +1 (X) or -1 (O) ]
    :return: The score of the given player
    """
    score = 0
    acceptable_values = (0, player)

    # counting rows
    if board[0] in acceptable_values and board[1] in acceptable_values and board[2] in acceptable_values:
        score += 1
    if board[3] in acceptable_values and board[4] in acceptable_values and board[5] in acceptable_values:
        score += 1
    if board[6] in acceptable_values and board[7] in acceptable_values and board[8] in acceptable_values:
        score += 1

    # counting columns
    if board[0] in acceptable_values and board[3] in acceptable_values and board[6] in acceptable_values:
        score += 1
    if board[1] in acceptable_values and board[4] in acceptable_values and board[7] in acceptable_values:
        score += 1
    if board[2] in acceptable_values and board[5] in acceptable_values and board[8] in acceptable_values:
        score += 1

    # counting diagonals
    if board[0] in acceptable_values and board[4] in acceptable_values and board[8] in acceptable_values:
        score += 1
    if board[2] in acceptable_values and board[4] in acceptable_values and board[6] in acceptable_values:
        score += 1

    return score


def generate_training_string(board, p, move):
    """ This function generate a string version of the data that have to be written on the output file.
        The string does not have parenthesis, comma or any other symbols, the first nine values represents the state of
        the grid, the 10th value represent who is the next player to play and the last value is the position in which
        the player should put his symbol.

    :param board: The board of the game (an array of 9 elements), it must contains only [-1, 0, +1] values
    :param p: Who is the player that has to play now [ +1 (X) or -1 (O) ]
    :param move: The cell in which the player should put its symbol (a value from 0 to 8)
    :return: A string value that could be printed on a file or on the screen
    """
    to_ret = ""
    for i in range(len(board)):
        to_ret += str(board[i]) + " "
    to_ret += str(p) + " "
    to_ret += str(move)
    return to_ret


def print_board(board):
    """ This function print a Tic-Tac-Toe board on the stdout """

    new_grid = [" ", " ", " ", " ", " ", " ", " ", " ", " "]
    for i in range(len(board)):
        if board[i] == 1:
            new_grid[i] = "X"
        elif board[i] == -1:
            new_grid[i] = "O"

    print()
    print(" %s | %s | %s " % (new_grid[0], new_grid[1], new_grid[2]))
    print("-----------")
    print(" %s | %s | %s " % (new_grid[3], new_grid[4], new_grid[5]))
    print("-----------")
    print(" %s | %s | %s " % (new_grid[6], new_grid[7], new_grid[8]))
    return


def main_generate_nn_files(source_filename, training_filename, testing_filename):
    """ This function reads a source file and split its entry in two files, the first one for the training and the
        second one for the testing of a neural-network according to T_T_PERC value.
        If the output files already exists they will be overwritten.
    """
    c_train = 0
    c_test = 0
    random.seed()  # initialization of the random generator

    if FOR_MATLAB:
        count = 0
        input_file = open(MATLAB_INPUT, "w")
        output_file = open(MATLAB_OUTPUT, "w")

        with open(source_filename) as source_file:
            for line in source_file:
                count += 1
                input_line = line[:-3]  # removing from the string the output move and the '\n' character
                output_line = line.strip()[-1]  # taking the last value of the string

                input_file.write(input_line + "\n")
                output_file.write(output_line + "\n")
            print("The source file contains " + str(count) + " entries.")
    else:
        training_file = open(training_filename, "w")
        testing_file = open(testing_filename, "w")

        with open(source_filename) as source_file:
            for line in source_file:
                if random.random() < T_T_PERC:
                    training_file.write(line)
                    c_train += 1
                else:
                    testing_line = line[:-3]  # removing from the string the output move and the '\n' character
                    testing_file.write(testing_line + "\n")
                    c_test += 1

        training_file.close()
        testing_file.close()
        print("The source file has been split in " + training_filename + " (" + str(c_train) + " combinations) and " +
              testing_filename + " (" + str(c_test) + " combinations)")
    return


def test():
    """ This function is used to perform some testing, it should be removed in the final version of the program. """
    board1 = [1, 1, 0, -1, -1, 0, 0, 0, 0]
    test_routine(board1)
    board2 = [1, 1, 0, -1, -1, 0, 1, 0, 0]
    test_routine(board2)
    board3 = [1, 0, 0, -1, -1, 0, 1, 0, -1]
    test_routine(board3)

    w_board = [0, 0, 0, 1, 1, 1, -1, -1, 0]
    l_board = [-1, 0, 1, 1, -1, 0, 1, 0, -1]
    test_routine(w_board)
    test_routine(l_board)
    return


def test_routine(board):
    """ This function performs tests on a board, it should be removed in the final version of the program. """
    print_board(board)
    res = someone_won(board)
    if res[1] is 1:
        logging.debug("X won")
    elif res[1] is -1:
        logging.debug("O won")
    else:
        logging.debug("No one won")
    logging.debug("Grid score = %d", evaluation_function(board))
    logging.debug("X score is %d and O score is %d", __partial_score(board, +1), __partial_score(board, -1))

    next_p = who_is_next(board)
    for p in next_p:
        if p != 0:
            logging.debug("Who is next? " + str(p))
            move = next_move(board, p)
            logging.debug(generate_training_string(board, p, move))

            new_board = copy.deepcopy(board)
            new_board[move] = p
            logging.debug("Configuration after next move:")
            print_board(new_board)

    return


if __name__ == "__main__":
    print(r"         _       _                          _____           _       _    (!) %s    " % VERSION)
    print(r"   /\/\ (_)_ __ (_)_ __ ___   __ ___  __   /__   \_ __ __ _(_)_ __ (_)_ __   __ _  ")
    print(r"  /    \| | '_ \| | '_ ` _ \ / _` \ \/ /____ / /\/ '__/ _` | | '_ \| | '_ \ / _` | ")
    print(r" / /\/\ \ | | | | | | | | | | (_| |>  <_____/ /  | | | (_| | | | | | | | | | (_| | ")
    print(r" \/    \/_|_| |_|_|_| |_| |_|\__,_/_/\_\    \/   |_|  \__,_|_|_| |_|_|_| |_|\__, | ")
    print(r"  Developed by Luca Mannella - July 2017                                    |___/  ")
    print(r"                                                                                   ")
    logging.basicConfig(format="%(message)s")
    logging.getLogger().setLevel(level=logging.DEBUG)
    logging.getLogger().handlers[0].setFormatter(logging.Formatter(
        "%(asctime)s.%(msecs)04d %(levelname)s: %(message)s", datefmt="%H:%M:%S"))

    if TEST:
        test()
        sys.exit()

    if GENERATE_OUTPUT_FILE:
        main_generate_output(OUTPUT_FILENAME)

    main_generate_nn_files(OUTPUT_FILENAME, TRAINING_FILENAME, TESTING_FILENAME)