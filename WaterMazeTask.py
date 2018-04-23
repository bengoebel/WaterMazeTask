# Name: Benjamin Goebel
# Date: April 22, 2018
# Description: This program models the research work by Richard G.M. Morris
#              titled "Spatial localization does not require the presence of
#              local cues". In this program a mouse (M) learns the location
#              of a hidden platform (P), through a series of trials. While the
#              platform is visible throughout the program to the user, the
#              mouse is unaware of the platform's location and must learn the
#              platform's location through a series of trials where the mouse
#              searches the water maze for the platform. The mouse can only tell
#              if it has found the platform if it is at the platform's location.
#              The program uses reinforcement learning with a softmax to model
#              the spatial memory task.

import math
import random
import time
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import textwrap

NA = -1
N = 0
NE = 1
E = 2
SE = 3
S = 4
SW = 5
W = 6
NW = 7
NUM_DIRS = 8
NUM_ROWS = 7
NUM_COLS = 7
ROUND_TO = 3
LOWEST_TEMP = 0.3  # The lowest computational temperature that can be reached
# Number of moves needed to reset the computational temperature, given that
# the mouse is searching for the platform in the same position for at least
# the fourth trial (after the third, that's why TRIAL_TEMP_RESET_THRESHOLD = 3)
MOVES_TEMP_RESET_THRESHOLD = int((NUM_ROWS * NUM_COLS) * 0.75)
TRIAL_TEMP_RESET_THRESHOLD = 3

class Board(object):
    __board = []
    __row_pos_mouse = 0
    __col_pos_mouse = 0
    __started_trial = False
    __found_platform = False
    __num_trials = 0
    __num_trials_since_moved = 0  # Number of trials since the platform was
                                  # placed
    __quad_count = [0.0, 0.0, 0.0, 0.0]

    # Purpose: Creates a board and initializes instance variables.
    # Arguments: random_corner: A bool, if True, the mouse starts in a random
    #                           corner of the board at the beginning of each
    #                           trial. If False, the mouse's starting corner
    #                           position rotates for each trial
    #            plat_in_center: A bool, if True, the platform will be hidden
    #                            in the center of the board. If False, the
    #                            platform will be hidden, randomly, in one of
    #                            the four corners of the board
    #            remove_plat_exp: A bool, True if the remove platform
    #                             experiment is being conducted, and False if
    #                             otherwise
    # Returns: Nothing
    def __init__(self, random_corner, plat_in_center, remove_plat_exp):
        self.__plat_row = NA
        self.__plat_col = NA
        self.__random_corner = random_corner
        self.__plat_in_center = plat_in_center
        self.__remove_plat_exp = remove_plat_exp
        (self.__placements, (self.__plat_row, self.__plat_col)) = \
        self.__get_placements(False)
        if plat_in_center:
            self.__num_start_pos = 4
        else:
            self.__num_start_pos = 3
        self.__board.append(['+'] + ['-'] * NUM_COLS + ['+'])
        for r in range(NUM_ROWS):
            self.__board.append(['|'] + [' '] * NUM_COLS + ['|'])
        self.__board.append(['+'] + ['-'] * NUM_COLS + ['+'])

    # Purpose: Starts a new trial. Places the mouse and platform on the board.
    #          For a new trial to be initiated, there must not be a trial,
    #          currently, in progress.
    # Arguments: None
    # Returns: A tuple, containing a bool and another tuple. The bool is True
    #          if a new trial has been initiated, and it is False if otherwise.
    #          The other tuple contains two ints, which are the mouse's
    #          starting row and col positions, respectively. The row and col
    #          positions are both set to -1 if a new trial has not been
    #          successfully initiated.
    def new_trial(self):
        if not self.__started_trial or self.__found_platform:
            self.__num_trials += 1
            self.__num_trials_since_moved += 1
            self.__started_trial = True
            self.__found_platform = False
            self.__quad_count = [0.0, 0.0, 0.0, 0.0]
            if self.__random_corner:
                (self.__row_pos_mouse, self.__col_pos_mouse) = \
                self.__placements[random.randint(0, 3)]
            else:
                (self.__row_pos_mouse, self.__col_pos_mouse) = \
                self.__placements[(self.__num_trials - 1) % \
                                  (self.__num_start_pos)]
            self.__board[self.__row_pos_mouse][self.__col_pos_mouse] = 'M'
            self.__board[self.__plat_row][self.__plat_col] = 'P'
            return (True, (self.__row_pos_mouse, self.__col_pos_mouse))
        return (False, (NA, NA))

    # Purpose: Checks to see if the mouse can move. The mouse can move if
    #          a trial is, currently, in progress.
    # Arguments: None
    # Returns: A bool, True, if the mouse can move and False, if otherwise
    def can_move(self):
        return self.__started_trial and not self.__found_platform

    # Purpose: Moves the mouse in the board.
    # Arguments: direct: An int, the integer constant, corresponding to the
    #                    direction, in which, to move the mouse
    # Returns: A bool, True if the mouse finds the platform and False,
    #          if otherwise
    def make_move(self, direct):
        if self.__found_platform or not self.__started_trial:
            return False
        if self.__remove_plat_exp:
            self.__count_quad()
        (row_move, col_move) = self.__direction_rowcol_conversion(direct)
        self.__board[self.__row_pos_mouse][self.__col_pos_mouse] = ' '
        self.__row_pos_mouse += row_move
        self.__col_pos_mouse += col_move
        if self.__board[self.__row_pos_mouse][self.__col_pos_mouse] == 'P':
            self.__board[self.__row_pos_mouse][self.__col_pos_mouse] = 'F'
            self.__found_platform = True
            self.__started_trial = False
            return True
        else:
            self.__board[self.__row_pos_mouse][self.__col_pos_mouse] = 'M'
            return False

    # Purpose: Resets the __num_trials_since_moved class variable, the position
    #          of the platform, and the starting positions for the mouse.
    # Arguments: None
    # Returns: Nothing
    def reset_board(self):
        self.__num_trials_since_moved = 0
        (self.__placements, (self.__plat_row, self.__plat_col)) = \
        self.__get_placements(False)

    # Purpose: Prints the board.
    # Arguments: None
    # Returns: Nothing
    def print_board(self):
        for row in self.__board:
            print (" ".join(row))
        print("")

    # Purpose: Removes the platform from the board. The platform can only
    #          be removed if the remove platform experiment is being conducted.
    # Arguments: None
    # Returns: A bool, True if the platform was successfully removed from the
    #          board, and False if otherwise.
    def remove_platform(self):
        if self.__remove_plat_exp:
            self.__board[self.__plat_row][self.__plat_col] = ' '
            return True
        else:
            return False

    # Purpose: Moves the platform to a new location in the watermaze.
    # Arguments: None
    # Returns: A bool, True if the platform was successfully moved and
    #          False if otherwise.
    def move_platform(self):
        if self.__plat_in_center:
            return False
        if self.__num_trials_since_moved <= TRIAL_TEMP_RESET_THRESHOLD:
            # Need it to be at least the third trial since the plat was moved
            return False
        self.__board[self.__plat_row][self.__plat_col] = ' '
        (self.__placements, (self.__plat_row, self.__plat_col)) = \
        self.__get_placements(True)
        self.__num_trials_since_moved = 0
        return True

    # Purpose: Removes the mouse from the watermaze. This function is intended
    #          to solely be used for the remove platform experiment.
    # Arguments: None
    # Returns: Nothing
    def remove_mouse(self):
        self.__board[self.__row_pos_mouse][self.__col_pos_mouse] = ' '

    # Purpose: Gets the quadrant count, the number of moves the mouse makes
    #          in each quadrant. This function is intended to, solely, be used
    #          for the remove platform experiment.
    # Arguments: None
    # Returns: A list of 4 ints, the number of times the mouse moved in
    #          each of the 4 quadrants of the watermaze.
    def get_quad_count(self):
        return self.__quad_count

    # Purpose: Gets each quadrant's geographic relation to the target quadrant.
    # Arguments: None
    # Returns: A list of 4 chars, each quadrant's geographic relation to the
    #          target quadrant
    def get_quad_adj(self):
        if self.__plat_row < math.ceil(NUM_ROWS / 2):
            if self.__plat_col < math.ceil(NUM_COLS / 2):
                return ['TR', 'A/R', 'OP', 'A/L']
            elif self.__plat_col > math.ceil(NUM_COLS / 2):
                return ['A/L', 'TR', 'A/R', 'OP']
        elif self.__plat_row > math.ceil(NUM_ROWS / 2):
            if self.__plat_col < math.ceil(NUM_COLS / 2):
                return ['A/R', 'OP', 'A/L', 'TR']
            elif self.__plat_col > math.ceil(NUM_COLS / 2):
                return ['OP', 'A/L', 'TR', 'A/R']

    # Purpose: Sets the class variable, '__found_platform' to be True. This
    #          function is intended to solely be used for the remove platform
    #          experiment.
    # Arguments: None
    # Returns: Nothing
    def set_found_platform(self):
        self.__found_platform = True

    # Purpose: Converts an integer constant, corresponding to a direction,
    #          to a tuple of two ints. The two ints represent the
    #          changes to the mouse's row and col position needed
    #          to make one move in the inputted direction.
    # Arguments: direct: An int, the integer constant, corresponding to the
    #                    direction
    # Returns: A tuple of two ints, the changes to the mouse's row and col
    #          position, respectively
    def __direction_rowcol_conversion(self, direct):
        conversions = [(-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), \
                       (0, -1), (-1, -1)]
        return conversions[direct]

    # Purpose: Determines where the platform will be hidden on the board.
    #          Also, determines the possible locations, on the board, at which
    #          the mouse can start.
    # Arguments: move_plat: A bool, True if the platform is being moved and
    #                       False if otherwise.
    # Returns: A tuple, containing a list of possible starting positions for
    #                   the mouse, and a tuple with the row and col positions
    #                   of the platform.
    def __get_placements(self, move_plat):
        original_placements = [(1, 1), (1, NUM_COLS), (NUM_ROWS, NUM_COLS), \
                               (NUM_ROWS, 1)]
        if self.__plat_in_center:
            original_plat_loc = (math.ceil(NUM_ROWS / 2), \
                                 math.ceil(NUM_COLS / 2))
            return (original_placements, original_plat_loc)
        else:
            if move_plat:
                random_index = random.randint(0, 3)
                plat_loc = original_placements[random_index]
                while(plat_loc == (self.__plat_row, self.__plat_col)):
                    random_index = random.randint(0, 3)
                    plat_loc = original_placements[random_index]
            else:
                random_index = random.randint(0, 3)
                plat_loc = original_placements[random_index]
            del original_placements[random_index]
            return (original_placements, plat_loc)

    # Purpose: Adds one to the quadrant count for the quadrant, in which, the
    #          mouse is, currently, located.
    # Arguments: None
    # Returns: Nothing
    def __count_quad(self):
        if self.__row_pos_mouse < math.ceil(NUM_ROWS / 2):
            if self.__col_pos_mouse < math.ceil(NUM_COLS / 2):
                self.__quad_count[0] += 1
            elif self.__col_pos_mouse > math.ceil(NUM_COLS / 2):
                self.__quad_count[1] += 1
        elif self.__row_pos_mouse > math.ceil(NUM_ROWS / 2):
            if self.__col_pos_mouse < math.ceil(NUM_COLS / 2):
                self.__quad_count[3] += 1
            elif self.__col_pos_mouse > math.ceil(NUM_COLS / 2):
                self.__quad_count[2] += 1



class Q(object):
    __trials_completed = 0
    __row_pos_mouse = 0
    __col_pos_mouse = 0
    __num_moves = 0
    __num_moves_per_trial = []
    __pos_visited = []  # Places visited on board from least to most recent
                        # List consists of tuples with row and col positions
    __q_board = [] # 2-D array
                   # Each element is the Q-value at
                   # each location on the board
    __moved_plat = False  # Whether or not the platform has been moved, since
                          # the previous trial

    # Purpose: Initializes the Q-Learning instance variable paramaters based on
    #          the inputted values to the program. Initializes the q-values of
    #          each location on the board.
    # Arguments: init_temp: A float, the starting computational temperature
    #            temp_mod: A float, between 0 and 1, how much to reduce the
    #                      temperature by after each trial
    #            discount_factor: A float, the discount factor parameter
    #            learning_rate: A float, the learning rate parameter
    # Returns: Nothing
    def __init__(self, init_temp, temp_mod, discount_factor, learning_rate):
        self.__temp = init_temp
        self.__ORIG_TEMP = init_temp
        self.__TEMP_MOD = temp_mod

        # Given the MOVES_TEMP_RESET_THRESHOLD has been reached, this
        # variable is the largest computational temperature that can
        # reset the computational temperature. Every value lower than or
        # equal to the value of this variable can reset the computational
        # temperature
        self.__TEMP_RESET_THRESHOLD = init_temp * ((temp_mod) ** \
                                                   TRIAL_TEMP_RESET_THRESHOLD)
        self.__Y = discount_factor
        self.__ALPHA = learning_rate
        self.__curr_max_qval = init_temp # current largest q val on the q_board
        self.__init_q_board()

    # Purpose: Starts a new trial.
    # Arguments: row_pos: An int, the mouse's starting row position on the
    #                     board
    #            col_pos: An int, the mouse's starting col position on the
    #                     board
    # Returns: Nothing
    def new_trial(self, row_pos, col_pos):
        self.__num_moves = 0
        self.__pos_visited = []
        self.__row_pos_mouse = row_pos
        self.__col_pos_mouse = col_pos

    # Purpose: Ends the current trial, under the assumption that the
    #          platform has been found.
    # Arguments: None
    # Returns: Nothing
    def end_trial(self):
        self.__temp = round(self.__temp * self.__TEMP_MOD, ROUND_TO)
        if self.__temp < LOWEST_TEMP:
            self.__temp = LOWEST_TEMP
        self.__trials_completed += 1
        self.__num_moves_per_trial.append(self.__num_moves)
        self.__update_q_board()

    # Purpose: Gets the number of trials completed.
    # Arguments: None
    # Returns: An int, the number of trials completed
    def get_trials_completed(self):
        return self.__trials_completed

    # Purpose: Gets the number of moves in the current trial, thus far. If
    #          a current trial is not in progress, the function gets the
    #          number of moves in the previous trial.
    # Arguments: None
    # Returns: An int, the number of moves in the trial
    def get_num_moves(self):
        return self.__num_moves

    # Purpose: Gets the number of moves in each completed trial.
    # Arguments: None
    # Returns: A list of ints, the number of moves in each completed trial
    def get_num_moves_per_trial(self):
        return self.__num_moves_per_trial

    # Purpose: Decides the direction for the mouse to move.
    # Arguments: None
    # Returns: An int, the integer constant, corresponding to the direction for
    #          the mouse to move
    def make_move(self):
        if self.__num_moves >= MOVES_TEMP_RESET_THRESHOLD and \
           self.__temp <= self.__TEMP_RESET_THRESHOLD:
           # The platform has been moved!
           self.__temp = self.__ORIG_TEMP
           self.__moved_plat = True
        self.__pos_visited.append((self.__row_pos_mouse, self.__col_pos_mouse))
        direct = self.__decide_move()
        (row_move, col_move) = self.__direct_rowcol_conversion(direct)
        self.__row_pos_mouse += row_move
        self.__col_pos_mouse += col_move
        self.__num_moves += 1
        return direct

    # Purpose: Resets all the q-values on the board to zero. Resets all
    #          class variables. Also, the computational temperature instance
    #          variable is reset to the user's original input.
    # Arguments: None
    # Returns: Nothing
    def reset_q(self):
        self.__temp = self.__ORIG_TEMP
        self.__curr_max_qval = self.__ORIG_TEMP
        self.__moved_plat = False
        self.__trials_completed = 0
        self.__row_pos_mouse = 0
        self.__col_pos_mouse = 0
        self.__num_moves = 0
        self.__num_moves_per_trial = []
        self.__pos_visited = []
        self.__q_board = []
        self.__init_q_board()

    def get_temp(self):
        return self.__temp

    # Purpose: Initializes each q-value of each location on the board.
    # Arguments: None
    # Returns: Nothing
    def __init_q_board(self):
        for r in range(NUM_ROWS):
            row = []
            for c in range(NUM_COLS):
                row.append(0.0)
            self.__q_board.append(row)

    # Purpose: Updates the q-value of locations on the board. The updates
    #          are based on the q-learning parameters and the locations visited
    #          on the board on the previous trial. Locations are not updated on
    #          the board if they were not visited on the previous trial.
    # Arguments: None
    # Returns: Nothing
    def __update_q_board(self):
        # Maintained to keep sure each location is updated at most once after
        # each trial
        one_update = []
        for one_update_r in range(NUM_ROWS):
            one_update_row = []
            for one_update_c in range(NUM_COLS):
                one_update_row.append(False)
            one_update.append(one_update_row)
        if self.__moved_plat:
            self.__curr_max_qval *= 2
            self.__moved_plat = False
        self.__q_board[self.__row_pos_mouse][self.__col_pos_mouse] = \
        self.__curr_max_qval
        for pos_index in range(self.__num_moves - 1, -1, -1):
            (r, c) = self.__pos_visited[pos_index]
            if not one_update[r][c]:
                max_q = self.__find_max_q(r, c)
                q = self.__q_board[r][c]
                self.__q_board[r][c] = q + self.__ALPHA * (self.__Y * max_q - q)
                one_update[r][c] = True

    # Purpose: This function decides which direction to move the mouse.
    # Arguments: None
    # Returns: An int, the integer constant, corresponding to the direction for
    #          the mouse to move
    def __decide_move(self):
        decision = round(random.uniform(0, 1), ROUND_TO)
        probs_sum = 0.0
        next_qs = self.__get_next_qs()
        probabilities = self.__get_probabilities(next_qs)
        for d in range(NUM_DIRS):
            prob = probabilities[d]
            if prob != NA:
                probs_sum += prob
                if decision <= probs_sum or d == NW:
                    return d
        return NA

    # Purpose: Gets a list of the q-values in the eight adjacent locations to
    #          the mouse's current location. If the adjacent location is out
    #          of bounds, the q-value is set to NA.
    # Arguments: None
    # Returns: A list of floats, the list of the q-values in the eight adjacent
    #          locations to the mouse's current location
    def __get_next_qs(self):
        next_qs = [NA, NA, NA, NA, NA, NA, NA, NA]
        for direct in range(N, NW + 1):
            (row_move, col_move) = self.__direct_rowcol_conversion(direct)
            r = self.__row_pos_mouse + row_move
            c = self.__col_pos_mouse + col_move
            if self.__in_bounds(r, c):
                next_qs[direct] = self.__q_board[r][c]
        return next_qs

    # Purpose: Checks to see if the row, col coordinates are within the
    #          confines of the board.
    # Arguments: r: An int, the row coordinate
    #            c: An int, the col coordinate
    # Returns: A bool, True, if the coordinates are within the confines of
    #          the board, and False, if otherwise
    def __in_bounds(self, r, c):
        if r >= 0 and r <= NUM_ROWS - 1:
            if c >= 0 and c <= NUM_COLS - 1:
                return True
            return False
        return False

    # Purpose: Gets the probabilities of the mouse moving in each direction in a
    #          given location on the board.
    # Arguments: next_qs: A list of floats, the q-values of the locations
    #            surrounding the mouse's current location
    # Returns: A list of floats, the probabilities of the mouse moving in each
    #          direction, given the mouse's current location
    def __get_probabilities(self, next_qs):
        e_to_q = []
        e_to_q_sum = 0.0
        probabilities = []
        for qi in next_qs:
            if qi != NA:
                num = round(math.exp(qi/self.__temp), ROUND_TO)
                e_to_q.append(num)
                e_to_q_sum += num
            else:
                e_to_q.append(NA)
        for num in e_to_q:
            if num != NA:
                probabilities.append(round(num/e_to_q_sum, ROUND_TO))
            else:
                probabilities.append(NA)
        return probabilities

    # Purpose: Converts an integer constant, corresponding to a direction,
    #          to a tuple of two ints. The two ints represent the
    #          changes to the mouse's row and col position needed
    #          to make one move in the inputted direction.
    # Arguments: direct: An int, the integer constant, corresponding to the
    #                    direction
    # Returns: A tuple of two ints, the changes to the mouse's row and col
    #          position, respectively
    def __direct_rowcol_conversion(self, direct):
        conversions = [(-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), \
                       (0, -1), (-1, -1)]
        return conversions[direct]

    # Purpose: In the given location on the board, this function finds the
    #          the largest q-value of the adjacent locations.
    # Arguments: r: An int, the row location
    #            c: An int, the col location
    # Returns: A float, the largest q-value of the adjacent locations
    def __find_max_q(self, r, c):
        max_q = 0
        for row_index in range(r - 1, r + 2):
            for col_index in range(c - 1, c + 2):
                if self.__in_bounds(row_index, col_index):
                    q = self.__q_board[row_index][col_index]
                    if q > max_q:
                        max_q = q
        return max_q



class WaterMazeTask(object):

    # Purpose: Sets up the watermaze board, the Q-learning parameters, and
    #          the Q-values for each location on the board.
    # Arguments: init_temp: A float, the starting computational temperature
    #            temp_mod: A float, between 0 and 1, how much to reduce the
    #                      temperature by after each trial
    #            discount_factor: A float, the discount factor parameter
    #            learning_rate: A float, the learning rate parameter
    #            random_corner: A bool, if True, the mouse starts in a random
    #                           corner of the board at the beginning of each
    #                           trial. If False, the mouse's starting corner
    #                           position rotates for each trial
    #            plat_in_center: A bool, if True, the platform will be hidden
    #                            in the center of the board. If False, the
    #                            platform will be randomly hidden in one of
    #                            the four corners of the board
    #            remove_plat_exp: A bool, True if the remove platform
    #                             experiment is being conducted, and False if
    #                             otherwise
    # Returns: Nothing
    def __init__(self, init_temp, temp_mod, discount_factor, learning_rate, \
                 random_corner, plat_in_center, remove_plat_exp):
        self.__init_temp = round(init_temp, ROUND_TO)
        self.__TEMP_MOD = round(temp_mod, ROUND_TO)
        self.__Y = round(discount_factor, ROUND_TO)
        self.__ALPHA = round(learning_rate, ROUND_TO)
        self.__board = Board(random_corner, plat_in_center, remove_plat_exp)
        self.__q = Q(init_temp, temp_mod, discount_factor, learning_rate)

    # Purpose: Starts a new trial.
    # Arguments: None
    # Returns: A bool, True if a new trial was initiated, and False if
    #          otherwise. A new trial can only be initiated if there is not
    #          a trial, currently, in progress.
    def new_trial(self):
        (can_start, (r, c)) = self.__board.new_trial()
        if can_start:
            self.__q.new_trial(r - 1, c - 1) # Accounting for the border
            return True
        else:
            return False

    # Purpose: Simulates one trial.
    # Arguments: None
    # Returns: A bool, True if the trial simulation was initiated, and False if
    #         otherwise. A trial simulation can only be initiated if there is
    #         a trial in progress and the platform has not been found.
    def trial_simulation(self):
        if self.__board.can_move():
            self.view_watermaze()
            if self.get_trials_completed() == 0:
                time.sleep(0.1)
            else:
                time.sleep(0.5)
            while self.make_move():
                self.view_watermaze()
                if self.get_trials_completed() == 0:
                    time.sleep(0.1)
                else:
                    time.sleep(0.5)
            return True
        else:
            return False

    # Purpose: Simulates n (an inputed integer) trials and performs the
    #          simulations x (an inputed integer) times. Graphs the average
    #          number of moves for each trial.
    # Arguments: num_trials: An int, the number of trials
    #            num_iters: An int, the number of times to simulate each trial
    # Returns: Nothing
    def simulate_numtrials_numiters(self, num_trials, num_iters):
        moves = np.empty(num_trials)
        for t_num in range(num_trials):
            moves[t_num] = 0.0
        for iteration in range(num_iters):
            for t_num in range(num_trials):
                if self.new_trial():
                    while self.make_move():
                        pass
                else:
                    return
            moves = moves + np.array(self.__q.get_num_moves_per_trial())
            self.__board.reset_board()
            self.__q.reset_q()
        moves = moves / num_iters
        plt.plot(np.arange(1, num_trials + 1), moves)
        plt.xlabel("Trial Number")
        plt.ylabel("Number of Moves")
        plt.title("Number of Moves as a Function of Trial Number")
        plt.show()

    # Purpose: Runs the remove platform experiment.
    # Arguments: num_trials: An int, the number of trials for each iteration
    #                        of the experiment
    #            num_iters: An int, the number of iterations in the experiment
    #            num_moves: An int, the number of times the mouse moves in
    #                       the probe trial.
    # Returns: Nothing
    def probe_numtrials_numiters(self, num_trials, num_iters, num_moves):
        moves_in_quad_tot = pd.Series([0.0, 0.0, 0.0, 0.0], \
                                      ['A/L', 'TR', 'A/R', 'OP'])
        for iteration in range(num_iters):
            for t_num in range(num_trials):
                if self.new_trial():
                    while self.make_move():
                        pass
                else:
                    return
            if self.new_trial():
                if self.__board.remove_platform():
                    for nm in range(num_moves):
                        self.make_move()
                    moves_in_quad_iter = pd.Series(self.__board.get_quad_count(), \
                                                   self.__board.get_quad_adj())
                    moves_in_quad_tot = moves_in_quad_tot.add(moves_in_quad_iter)
                    self.__board.set_found_platform()
                    self.__board.remove_mouse()
                else:
                    return
            else:
                return
            self.__board.reset_board()
            self.__q.reset_q()
        moves_in_quad_avg = moves_in_quad_tot.divide(num_iters)
        moves_in_quad_avg = moves_in_quad_avg.reindex(index = \
                                                     ['A/L', 'TR', 'A/R', 'OP'])
        moves_in_quad_avg.plot(kind= 'bar')
        plt.xlabel("Quadrant")
        plt.ylabel("Number of Moves")
        plt.title("Number of Moves as a Function of Quadrant")
        plt.show()

    # Purpose: Runs the move platform experiment.
    # Arguments: num_trials: An int, the number of trials before and after
    #                        the platform is moved for each iteration
    #                        of the experiment
    #            num_iters: An int, the number of iterations in the experiment
    # Returns: Nothing
    def move_plat_numtrials_numiters(self, num_trials, num_iters):
        total_trials = num_trials * 2  # Before and After
        stats = []
        for t_index in range(total_trials):
            stats.append(0.0)
        total_stats = np.array(stats)
        for iteration_index in range(num_iters):
            for trial_before_index in range(num_trials):
                if self.new_trial():
                    while self.make_move():
                        pass
                else:
                    return
            self.move_plat()
            for trial_after_index in range(num_trials):
                if self.new_trial():
                    while self.make_move():
                        pass
                else:
                    return
            total_stats = \
            total_stats + np.array(self.__q.get_num_moves_per_trial())
            self.__board.reset_board()
            self.__q.reset_q()
        avg_stats = total_stats / num_iters
        plt.plot(np.arange(1, num_trials * 2 + 1), avg_stats)
        plt.xlabel("Trial Number")
        plt.ylabel("Number of Moves")
        plt.title('\n'.join(textwrap.wrap(("Number of Moves as a Function " + \
                   "of Trial Number With The Platform Being Moved " + \
                   "at Trial Number %d") % (num_trials + 1))))
        plt.show()

    # Purpose: Moves the mouse one position in the watermaze.
    # Arguments: None
    # Returns: A bool, True if the mouse was successfully moved, and False
    #          if otherwise. A mouse can only be moved if a trial is,
    #          currently, in progress.
    def make_move(self):
        if self.__board.can_move():
            direct = self.__q.make_move()
            if self.__board.make_move(direct):
                self.__q.end_trial()
            return True
        else:
            return False

    # Purpose: Moves the platform in the watermaze.
    # Arguments: None
    # Returns: A bool, True if the platform is successfully moved and
    #          False if the platform is not successfully moved.
    def move_plat(self):
        return self.__board.move_platform()

    # Purpose: Prints the watermaze in its current state.
    # Arguments: None
    # Returns: Nothing
    def view_watermaze(self):
        self.__board.print_board()

    # Purpose: Outputs a line graph that indicates the number of moves the mouse
    #          made in each trial, thus far.
    # Arguments: None
    # Returns: Nothing
    def stats(self):
        plt.plot(range(1, self.__q.get_trials_completed() + 1), \
                 self.__q.get_num_moves_per_trial())
        plt.xlabel("Trials")
        plt.ylabel("Number of Moves")
        plt.title(('\n'.join(textwrap.wrap("Number of Moves as a Function " + \
                   "of Trial (Initial Temp = %.3f, Temp " + \
                   "Modification = %.3f, Discount Factor = %.3f, Learning " + \
                   "Rate = %.3f)"))) % \
                   (self.__init_temp, self.__TEMP_MOD, self.__Y, self.__ALPHA),\
                   fontsize = 10)
        plt.show()

    # Purpose: Outputs the number of trials completed.
    # Arguments: None
    # Returns: An int, the number of trials completed
    def get_trials_completed(self):
        return self.__q.get_trials_completed()



# Purpose: Runs and controls the WaterMazeTask program.
# Arguments: None.
# Returns: Nothing.
def watermazetask_runner():
    valid_type = True
    valid_value = False
    print("Welcome to the WaterMazeTask. This program models research on " + \
          "mouse performance in the Morris water maze test, described in " + \
          "Morris (1981). In this program, a mouse (M) " + \
          "searches and learns the location of a hidden platform (P) in a " + \
          "water maze. While the platform is visible to the user, it is not " +\
          "visible to the mouse. At the start of this program, the user " + \
          "will be able to enter four floating point numbers. The first " + \
          "number represents the initial computational temperature " + \
          "parameter for Q-learning. The second number represents how " + \
          "much to modify the computational temperature parameter from " + \
          "trial-to-trial for Q-learning. The third number represents the " + \
          "discount factor parameter for Q-learning. The fourth number " + \
          "represents the learning rate parameter for Q-learning. " + \
          "Following the inputted numbers, the user will be able to run " + \
          "experiments and simulate trials.")

    print("Please input four floating point numbers. The first " + \
          "number represents the initial computational " + \
          "temperature parameter. This value should be " + \
          "between 50.0 and 100.0 (inclusive). The second " + \
          "number represents how much to modify the " + \
          "computational temperature parameter from " + \
          "trial-to-trial. This value should be between 0 and " + \
          "1 (inclusive). The third number represents the " + \
          "discount factor parameter for Q-learning. This " + \
          "value should be between 0 and 1 (inclusive). The " + \
          "fourth number represents the learning rate " + \
          "parameter for Q-learning. This value should be " + \
          "between 0 and 1 (inclusive).")

    while not valid_type or not valid_value:
        init_temp = input("Initial Computational Temperature: ")
        temp_mod = input("Computational Temperature Modification: ")
        discount_factor = input("Discount Factor: ")
        learning_rate = input("Learning Rate: ")
        try:
            init_temp = float(init_temp)
        except:
            print("Invalid input. Initial Computational Temperature must " + \
                  "be a floating point number.")
            valid_type = False
        try:
            temp_mod = float(temp_mod)
        except:
            print("Invalid input. Computational Temperature Modification " + \
                  "must be a floating point number.")
            valid_type = False
        try:
            discount_factor = float(discount_factor)
        except:
            print("Invalid input. Discount Factor parameter must be a " + \
                  "floating point number.")
            valid_type = False
        try:
            learning_rate = float(learning_rate)
        except:
            print("Invalid input. Learning Rate parameter must be a " + \
                  "floating point number.")
            valid_type = False
        if valid_type:
             if init_temp >= 50.0 and init_temp <= 100.0:
                if temp_mod >= 0.0 and temp_mod <= 1.0:
                    if discount_factor >= 0.0 and discount_factor <= 1.0:
                        if learning_rate >= 0.0 and learning_rate <= 1.0:
                            valid_value = True
                        else:
                            print("Invalid value. Learning rate parameter " + \
                                  "must be between 0 and 1 (inclusive).")
                    else:
                        print("Invalid value. Discount Factor parameter " + \
                              "must be between 0 and 1 (inclusive).")
                else:
                    print("Invalid value. Computational Temperature " + \
                          "Modification must be between 0 and 1 (inclusive).")
             else:
                 print("Invalid value. Initial Computational Temperature " + \
                       "must be between 50.0 and 100.0 (inclusive).")
        else:
            valid_type = True
    exp_inp = input("Please indicate 'Yes' if this is an " + \
                 "experiment, and 'No' if this is " + \
                 "not an experiment: ")
    exp_inp = exp_inp.lower()
    valid_inp = False
    while not valid_inp:
        if exp_inp == 'yes':
            correct_inp = False
            while not correct_inp:
                kind_of_exp = input("Please enter 'Trial-Sim' for the trial " +\
                                    "simulation experiment, 'Remove-Plat' " + \
                                    "for the remove platform experiment, " + \
                                    "and 'Move-Plat' for the move platform " + \
                                    "experiment: ")
                kind_of_exp = kind_of_exp.lower()
                if kind_of_exp == 'trial-sim':
                    try:
                        num_trials = int(input("Number Of Trials: "))
                        num_iters = int(input("Number Of Iterations: "))
                        if num_trials <= 0:
                            print("Invalid number of trials")
                            return False
                        if num_iters <= 0:
                            print("Invalid number of iterations")
                            return False
                        wmt_runner = WaterMazeTask(init_temp, temp_mod, \
                                                   discount_factor, \
                                                   learning_rate, False, True, \
                                                   False)
                        wmt_runner.simulate_numtrials_numiters(num_trials,num_iters)
                        return True
                    except:
                        print("Error simulating trials")
                elif kind_of_exp == 'remove-plat':
                    try:
                        num_trials = int(input("Number Of Trials: "))
                        num_iters = int(input("Number Of Iterations: "))
                        num_moves = int(input("Number Of Moves: "))
                        if num_trials <= 0:
                            print("Invalid number of trials")
                            return False
                        if num_iters <= 0:
                            print("Invalid number of iterations")
                            return False
                        if num_moves <= 0:
                            print("Invalid number of moves")
                            return False
                        wmt_runner = WaterMazeTask(init_temp, temp_mod, \
                                                   discount_factor, \
                                                   learning_rate, False, \
                                                    False, True)
                        wmt_runner.probe_numtrials_numiters(num_trials, \
                                                            num_iters, \
                                                            num_moves)
                        return True
                    except:
                        print("Error probing trials")
                elif kind_of_exp == 'move-plat':
                    try:
                        num_trials = int(input("Number Of Trials: "))
                        num_iters = int(input("Number Of Iterations: "))
                        if num_trials <= 0:
                            print("Invalid number of trials")
                            return False
                        if num_iters <= 0:
                            print("Invalid number of iterations")
                            return False
                        wmt_runner = WaterMazeTask(init_temp, temp_mod, \
                                                   discount_factor, \
                                                   learning_rate, False, \
                                                   False, False)
                        wmt_runner.move_plat_numtrials_numiters(num_trials, \
                                                                num_iters)
                        return True
                    except:
                        print("Error simulating trials")
                else:
                    print("Incorrect input")
            valid_inp = True
        elif exp_inp == "no":
            plat_loc_inp = input("Please enter 'Yes' if you would like " + \
                                 "the platform to be placed in the center " + \
                                 "of the watermaze. Enter any other input " + \
                                 "if you would like the platform to be " + \
                                 "placed in one of the four corners of the " + \
                                 "watermaze. Input is not case sensitive " + \
                                 "Input: ")
            plat_loc_inp = plat_loc_inp.lower()
            if plat_loc_inp == 'yes':
                wmt_runner = WaterMazeTask(init_temp, temp_mod,  \
                                           discount_factor, learning_rate, \
                                           False, True, False)
            else:
                wmt_runner = WaterMazeTask(init_temp, temp_mod,  \
                                           discount_factor, learning_rate, \
                                           False, False, False)
            command = input("Please enter one of the following commands: " + \
                  " 'New-Trial', 'Move-Mouse', 'Sim-Trial', 'View-Grid'," + \
                  " 'Move-Platform', 'Stats', or 'End': ")
            command = command.lower()
            while command != "end":
                if command == "new-trial":
                    if wmt_runner.new_trial():
                        print(("Started trial number %d") %
                              (wmt_runner.get_trials_completed() + 1))
                    else:
                        print("Unable to start new trial")
                elif command == "move-mouse":
                    if not wmt_runner.make_move():
                        print("Unable to move mouse")
                elif command == "sim-trial":
                    if not wmt_runner.trial_simulation():
                        print("Simulation could not be completed")
                elif command == "view-grid":
                    wmt_runner.view_watermaze()
                elif command == "stats":
                    wmt_runner.stats()
                elif command == "move-platform":
                    if wmt_runner.move_plat():
                        print("Platform moved.")
                    else:
                        print("Platform unable to be moved.")
                else:
                    print("Invalid Input")
                command = input("Please enter one of the following " + \
                      "commands: 'New-Trial', 'Move-Mouse', 'Sim-Trial', " + \
                      "'View-Grid', 'Move-Platform', 'Stats', or 'End': ")
                command = command.lower()
            valid_inp = True
        else:
            print("Incorrect input")
            exp_inp = input("Please indicate 'Yes' if this is an " + \
                         "experiment, and 'No' if this is " + \
                         "not an experiment: ")
            exp_inp = exp_inp.lower()
watermazetask_runner()
