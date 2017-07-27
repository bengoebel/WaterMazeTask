# By: Benjamin Goebel
# Date: July 27th, 2017
# Description: This program models the research work by Richard G.M. Morris
#              titled "Spatial localization does not require the presence of
#              local cues". In this program a mouse (M) learns the location
#              of a hidden platform (P), through a series of trials. While the
#              platform is visible throughout the program to the user, the
#              mouse is unaware of the platform's location and must learn the
#              platform's location through a series of trials where the mouse
#              searches the watermaze for the platform. The mouse can only tell
#              if it found the platform if it is at the platform's location. In
#              the beginning, the mouse searches randomly for the platform, but
#              after each trial, the mouse begins to move more directly towards
#              the platform. How quickly the mouse learns the location of the
#              platform is significantly influenced by the value inputted to
#              the program at the start of the program. This value, which
#              can be from 0 to 100% indicates the quality of the mouse's
#              spatial memory.

import random
import time
import math
import matplotlib.pyplot as plt
class WaterMazeTask(object):
    __MAX_ROWS = 7
    __MAX_COLS = 7
    __ROUND_TO = 3
    __NUM_DIRS = 8
    __NOT_APPLIC = -1.0
    __placements = [(1, 1), (1, __MAX_COLS), (__MAX_ROWS, __MAX_COLS),
                    (__MAX_ROWS, 1)]
    __row_pos_plat = math.ceil(__MAX_ROWS / 2)
    __col_pos_plat = math.ceil(__MAX_COLS / 2)
    __row_pos_mouse = -1      # Value initialized at the start of a new trial
    __col_pos_mouse = -1      # Value initialized at the start of a new trial
    __direction = -1          # Value initialized after each move
    __found_platform = False
    __started_trial = False
    __trials_completed = 0
    __moves_in_trial = 0
    __full_len = 5
    __full = [12.5] * __full_len
    __symm_edge_len = 3
    __symm_edge = [20.0] * __symm_edge_len
    __asymm_edge_len = 4
    __asymm_edge = [20.0] * __asymm_edge_len
    __aasymm_edge_len = 5
    __aasymm_edge = [20.0] * __aasymm_edge_len
    __symm_corner_len = 2
    __symm_corner = [round(100.0/3, __ROUND_TO)] * __symm_corner_len
    __asymm_corner_len = 3
    __asymm_corner = [round(100.0/3, __ROUND_TO)] * __asymm_corner_len
    __N = 0
    __NE = 1
    __E = 2
    __SE = 3
    __S = 4
    __SW = 5
    __W = 6
    __NW = 7
    __MODIFIED_N = 8

    # Purpose: Initializes class variables
    # Arguments: A float: The quality of spatial memory of the mouse from
    #            zero to one hundred, inclusive.
    # Returns: Nothing
    def __init__(self, inp):
        self.__input = round(inp / 100, self.__ROUND_TO)
        self.__moves = [] # a list of the number of moves in each trial
        self.__directions_grid = [] # the direction the mouse should move in
                                    # at each position on the grid
        self.__viewable_grid = []   # the grid to be printed
        self.__viewable_grid.append(['+'] + ['-'] * self.__MAX_COLS + ['+'])
        for r in range(self.__MAX_ROWS):
            self.__directions_grid.append([self.__NOT_APPLIC] * self.__MAX_COLS)
            self.__viewable_grid.append(['|'] + [' '] * self.__MAX_COLS + ['|'])
        self.__viewable_grid.append(['+'] + ['-'] * self.__MAX_COLS + ['+'])
        self.__viewable_grid[self.__row_pos_plat][self.__col_pos_plat] = 'P'
        self.__init_directions_grid()

    # Purpose: Starts a new trial
    # Arguments: None
    # Returns: A bool: True if a new trial has been initiated and False if
    #          otherwise.
    def new_trial(self):
        if not self.__started_trial or self.__found_platform:
            if self.__trials_completed != 0:
                self.__update()
            self.__started_trial = True
            self.__found_platform = False
            self.__moves_in_trial = 0
            (self.__row_pos_mouse, self.__col_pos_mouse) = \
            self.__placements[random.randint(0, 3)]
            while self.__row_pos_mouse == self.__row_pos_plat and \
                  self.__col_pos_mouse == self.__col_pos_plat:
                  (self.__row_pos_mouse, self.__col_pos_mouse) = \
                  self.__placements[random.randint(0, 3)]
            self.__viewable_grid[self.__row_pos_mouse][self.__col_pos_mouse] \
                                                                           = 'M'
            self.__direction = self.__directions_grid[self.__row_pos_mouse - 1]\
                                                     [self.__col_pos_mouse - 1]
            self.__viewable_grid[self.__row_pos_plat][self.__col_pos_plat] = 'P'
            return True
        return False

    # Purpose: Simulates the trial, allowing the mouse to move until it finds
    #          the platform. The watermaze is printed after each move.
    # Arguments: None
    # Returns: A bool: True if the simulation is completed and False if
    #          otherwise.
    def trial_simulation(self):
        if self.__started_trial:
            self.view_watermaze()
            time.sleep(0.7)
            while not self.__found_platform:
                self.make_move()
                self.view_watermaze()
                if self.__trials_completed == 0:
                    time.sleep(0.1)
                else:
                    time.sleep(1.0)
            return True
        return False

    # Purpose: Moves the mouse one position on the board.
    # Arguments: None
    # Returns: A bool: True if the mouse can be moved and False if the mouse
    #          cannot be moved.
    def make_move(self):
        if self.__found_platform or not self.__started_trial:
            return False
        self.__moves_in_trial += 1
        (surrounding, facing) = self.__situation()
        directional_probs = self.__move_probabilities(surrounding, facing)
        dir_decision = self.__decide_move(directional_probs)
        print(("Mouse moved %s") % \
              (self.__constant_direction_conversion(dir_decision)))
        (row_move, col_move) = self.__direction_rowcol_conversion(dir_decision)
        self.__viewable_grid[self.__row_pos_mouse][self.__col_pos_mouse] = ' '
        self.__row_pos_mouse += row_move
        self.__col_pos_mouse += col_move
        if self.__row_pos_mouse == self.__row_pos_plat and \
           self.__col_pos_mouse == self.__col_pos_plat:
           self.__found_platform = True
           self.__viewable_grid[self.__row_pos_plat][self.__col_pos_plat] = 'F'
           print("Found platform")
           self.__moves.append(self.__moves_in_trial)
           self.__trials_completed += 1
           print (("Trials completed: %d") % self.__trials_completed)
        else:
            self.__viewable_grid[self.__row_pos_mouse][self.__col_pos_mouse] \
                                                                           = 'M'
        self.__direction = self.__directions_grid[self.__row_pos_mouse - 1] \
                                                 [self.__col_pos_mouse - 1]
        return True

    # Purpose: Prints the watermaze.
    # Arguments: None.
    # Returns: Nothing.
    def view_watermaze(self):
        for row in self.__viewable_grid:
            print (" ".join(row))
        print("")

    # Purpose: Outputs a graph that indicates the number of moves the mouse
    #          made in each trial.
    # Arguments: None.
    # Returns: Nothing.
    def stats(self):
        trials = []
        for num in range(1, self.__trials_completed + 1):
            trials.append(num)
        plt.plot(trials, self.__moves)
        plt.xlabel("Trials")
        plt.ylabel("Number of Moves")
        plt.title("Number of Moves as a Function of Trials")
        plt.show()

    # Purpose: Outputs the number of trials completed, thus far.
    # Arguments: None.
    # Returns: An int: The number of trials completed, thus far.
    def get_trial_number(self):
        return self.__trials_completed

    # Purpose: Initializes a 2-dimensional grid that indicates the direction
    #          of the platform at each position in the grid.
    # Arguments: None.
    # Returns: Nothing.
    def __init_directions_grid(self):
        for r in range(self.__MAX_ROWS):
            for c in range(self.__MAX_COLS):
                if r < self.__row_pos_plat - 1:
                    if c < self.__col_pos_plat - 1:
                        self.__directions_grid[r][c] = self.__SE
                    elif c > self.__col_pos_plat - 1:
                        self.__directions_grid[r][c] = self.__SW
                    else:
                        self.__directions_grid[r][c] = self.__S
                elif r > self.__row_pos_plat - 1:
                    if c < self.__col_pos_plat - 1:
                        self.__directions_grid[r][c] = self.__NE
                    elif c > self.__col_pos_plat - 1:
                        self.__directions_grid[r][c] = self.__NW
                    else:
                        self.__directions_grid[r][c] = self.__N
                else:
                    if c < self.__col_pos_plat - 1:
                        self.__directions_grid[r][c] = self.__E
                    elif c > self.__col_pos_plat - 1:
                        self.__directions_grid[r][c] = self.__W
                    else:
                        self.__directions_grid[r][c] = self.__NOT_APPLIC

    # Purpose: Determines whether the mouse is in the corner, edge, or middle
    #          region of the watermaze. If the mouse is on the edge or corner
    #          of the watermaze, the method indicates which way the edge or
    #          corner is facing.
    # Arguments: None.
    # Returns: A tuple containing a string and an int. The string indicates
    #          the region of the watermaze that the mouse is located. The int
    #          corresponds to a direction, which is the direction the corner or
    #          edge is facing, if the mouse is located on the corner or edge
    #          of the watermaze. If the mouse is located in the middle region
    #          of the watermaze, the int is ignored.
    def __situation(self):
        if self.__row_pos_mouse == 1:
            if self.__col_pos_mouse == 1:
                return ("corner", self.__SE)
            elif self.__col_pos_mouse == self.__MAX_COLS:
                return ("corner", self.__SW)
            else:
                return ("edge", self.__S)
        elif self.__col_pos_mouse == self.__MAX_COLS:
            if self.__row_pos_mouse == self.__MAX_ROWS:
                return ("corner", self.__NW)
            else:
                return ("edge", self.__W)
        elif self.__row_pos_mouse == self.__MAX_ROWS:
            if self.__col_pos_mouse == 1:
                return ("corner", self.__NE)
            else:
                return ("edge", self.__N)
        elif self.__col_pos_mouse == 1:
            return ("edge", self.__E)
        else:
            return ("full", self.__NOT_APPLIC)

    # Purpose: Outputs the probabilities that the mouse moves in each
    #          particular direction
    # Arguments: A string: Indicates which region of the watermaze the mouse
    #            is in. An int: the direction the corner or edge is
    #            facing, if the mouse is located on the corner or edge of the
    #            watermaze.
    # Returns: A list of 8 floats: The probabilities that the mouse moves in
    #          each particular direction. Position 0 corresponds to N; position
    #          1 corresponds to NE; position 2 corresponds to E; position 3
    #          corresponds to SE; position 4 corresponds to S; position 5
    #          corresponds to SW; position 6 corresponds to W, and position 7
    #          corresponds to NW.
    def __move_probabilities(self, surrounding, facing):
        probs = None  # Probabilities that are going to be mapped to
                      # particular directions
        directional_probs = None  # Probabilities that are mapped to
                                  # particular directions
        if surrounding == "corner":
            probs = self.__which_corner()
            directional_probs = self.__corner_move_probabilities(probs, facing)
        elif surrounding == "edge":
            probs = self.__which_edge(facing)
            directional_probs = self.__edge_move_probabilities(probs, facing)
        else:
            directional_probs = self.__full_move_probabilities(self.__full)
        return directional_probs

    # Purpose: This method picks between two list of floats, which are the
    #          probabilities that the mouse, in a corner, moves in an
    #          available direction. The list chosen is based on the direction
    #          the platform is located. The probabilities are not mapped to
    #          particular directions, yet.
    # Arguments: None.
    # Returns: A list of floats: the probabilities that the mouse, in a corner,
    #          moves in an available direction.
    def __which_corner(self):
        if self.__direction % 2 != 0:
            return self.__symm_corner
        else:
            return self.__asymm_corner

    # Purpose: This method picks between three lists of floats, which are the
    #          probabilities that the mouse, on an edge, moves in an available
    #          direction. The list chosen is based on the direction that the
    #          platform is located. The probabilities are not mapped to
    #          particular directions, yet.
    # Arguments: An int: the direction the edge is facing.
    # Returns: A list of floats: the probabilities that the mouse, on an edge,
    #          moves in an available direction.
    def __which_edge(self, facing):
        lower_lower_bound = facing - 2
        lower_bound = facing - 1
        upper_bound = facing + 1
        upper_upper_bound = facing + 2
        if lower_lower_bound < 0:
            lower_lower_bound += self.__NUM_DIRS
            lower_bound += self.__NUM_DIRS
        elif upper_upper_bound == self.__NUM_DIRS:
            upper_upper_bound -= self.__NUM_DIRS
        if self.__direction == upper_upper_bound or \
           self.__direction == lower_lower_bound:
            return self.__aasymm_edge
        elif self.__direction == upper_bound or self.__direction == lower_bound:
            return self.__asymm_edge
        else:
            return self.__symm_edge

    # Purpose: This method maps probabilities that the mouse, in a corner,
    #          moves in an available direction to particular directions. This
    #          results in a list of probabilities that the mouse, in a corner,
    #          moves in a particular direction.
    # Arguments: A list of floats: the probabilities that the mouse, in a
    #            corner, moves in an available direction. An int: the direction
    #            the corner is facing.
    # Returns: A list of floats: the probabilities that the mouse, in a corner,
    #          moves in a particular direction.
    def __corner_move_probabilities(self, corner_lst, facing):
        directional_probs = []
        low_bound = facing - 1
        high_bound = facing + 1
        modified_d = False
        modified_dir = False
        if facing == self.__NW and self.__direction == self.__N:
            self.__direction = self.__MODIFIED_N
            modified_dir = True
        for d in range(self.__N, self.__NW + 1):
            if facing == self.__NW and d == self.__N:
                d = self.__MODIFIED_N
                modified_d = True
            if d >= low_bound and d <= high_bound:
                directional_probs.append(corner_lst[abs(self.__direction - d)])
            else:
                directional_probs.append(self.__NOT_APPLIC)
            if modified_d:
                d = self.__N
                modified_d = False
        if modified_dir:
            self.__direction = self.__N
            modified_dir = False
        return directional_probs

    # Purpose: This method maps probabilities that the mouse, on an edge,
    #          moves in an available direction to particular directions. This
    #          results in a list of probabilities that the mouse, on an edge,
    #          moves in a particular direction.
    # Arguments: A list of floats: the probabilities that the mouse, on an
    #            edge, moves in an available direction. An int: the direction
    #            the edge is facing.
    # Returns: A list of floats: the probabilities that the mouse, on an edge,
    #          moves in a particular direction.
    def __edge_move_probabilities(self, edge_lst, facing):
        directional_probs = []
        diff = 0
        low_bound = facing - 2
        high_bound = facing + 2
        if low_bound == -2:
            low_bound += self.__NUM_DIRS
        elif high_bound == self.__NUM_DIRS:
            high_bound -= self.__NUM_DIRS
        for d in range(self.__N, self.__NW + 1):
            if (facing != self.__N and facing != self.__W and \
                d >= low_bound and d <= high_bound) or \
                ((facing == self.__N or facing == self.__W) and \
                (d >= low_bound or d <= high_bound)):
                diff = abs(self.__direction - d)
                if diff > 4:
                    diff = self.__NUM_DIRS - diff
                directional_probs.append(edge_lst[diff])
            else:
                directional_probs.append(self.__NOT_APPLIC)
        return directional_probs

    # Purpose: This method maps probabilities that the mouse, in the middle
    #          region of the watermaze, moves in an available direction to
    #          particular directions. This results in a list of probabilities
    #          that the mouse, in the middle region of the watermaze, moves in
    #          a particular direction.
    # Arguments: A list of floats: the probabilities that the mouse, in the
    #            middle region of the watermaze, moves in an available
    #            direction.
    # Returns: A list of floats: the probabilities that the mouse, in the middle
    #          region of the watermaze, moves in a particular direction.
    def __full_move_probabilities(self, full_lst):
        directional_probs = []
        diff = 0
        for d in range(self.__N, self.__NW + 1):
            diff = abs(self.__direction - d)
            if diff > 4:
                diff = self.__NUM_DIRS - diff
            directional_probs.append(full_lst[diff])
        return directional_probs

    # Purpose: This method decides which direction to move the mouse. This is
    #          based on a list of possible directions with weighted percentages
    #          that indicate the likelihood that the mouse moves in a
    #          particular direction.
    # Arguments: A list of floats, which is the likelihood that the mouse
    #            moves in a particular direction.
    # Returns: An int: the direction to move the mouse.
    def __decide_move(self, directional_probs):
        decision = round(random.uniform(0, 100), self.__ROUND_TO)
        curr = 0.0
        d_probs_sum = 0.0
        for d in range(0, self.__NUM_DIRS):
            curr = directional_probs[d]
            if curr != self.__NOT_APPLIC:
                d_probs_sum += curr
                if decision <= d_probs_sum or d == self.__NW:
                    return d

    # Purpose: Converts a direction to a tuple of two ints, which represents the
    #          changes to the mouse's row and col position, respectively.
    # Arguments: An int: the direction to be converted.
    # Returns: A tuple of two ints: the changes to the mouse's row and col
    #          position, respectively.
    def __direction_rowcol_conversion(self, direct):
        conversions = [(-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), \
                       (0, -1), (-1, -1)]
        return conversions[direct]

    # Purpose: Converts an int representation of a direction to a string
    #          representation of that direction.
    # Arguments: An int: the direction to be converted.
    # Returns: A string: the converted direction.
    def __constant_direction_conversion(self, direct):
        conversions = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
        return conversions[direct]

    # Purpose: Updates the likelihood that the mouse moves in available
    #          directions. This specific update deals with situations where
    #          the likelihood of a mouse moving in available directions is
    #          symmetrical.
    # Arguments: A list of floats: the probabilities that the mouse moves in
    #            a given direction. An int: the length of the list. An int:
    #            the level of symmetry from 0 to 2.
    # Returns: Nothing.
    def __symm_update(self, list_to_update, list_len, symm):
        curr = 0.0
        transfer = 0.0
        remainder = 0.0
        for i in range(list_len - 1, 0, -1):
            curr = round(list_to_update[i] + transfer, self.__ROUND_TO)
            transfer = round(curr * self.__input, self.__ROUND_TO)
            remainder = round(curr * (1 - self.__input), self.__ROUND_TO)
            list_to_update[i] = remainder
            if i == list_len - symm:
                transfer /= 2
        list_to_update[0] = round(list_to_update[0] + 2 * transfer,
                                  self.__ROUND_TO)

    # Purpose: Updates the likelihood that the mouse moves in available
    #          directions. This specific update deals with situations where
    #          the likelihood of a mouse moving in available directions is
    #          asymmetrical.
    # Arguments: A list of floats: the probabilities that the mouse moves in
    #            a given direction. An int: the length of the list.
    # Returns: Nothing.
    def __asymm_update(self, list_to_update, list_len):
        curr = 0.0
        transfer = 0.0
        remainder = 0.0
        for i in range(list_len - 1, 0, -1):
            curr = round(list_to_update[i] + transfer, self.__ROUND_TO)
            transfer = round(curr * self.__input, self.__ROUND_TO)
            remainder = round(curr * (1 - self.__input), self.__ROUND_TO)
            list_to_update[i] = remainder
        list_to_update[0] = round(list_to_update[0] + transfer, self.__ROUND_TO)

    # Purpose: Updates the likelihood that the mouse moves in particular
    #          directions.
    # Arguments: None.
    # Returns: Nothing.
    def __update(self):
        self.__symm_update(self.__symm_corner, self.__symm_corner_len, 0)
        self.__asymm_update(self.__asymm_corner, self.__asymm_corner_len)
        self.__symm_update(self.__symm_edge, self.__symm_edge_len, 0)
        # Draw this one out to understand
        self.__symm_update(self.__asymm_edge, self.__asymm_edge_len, 2)
        self.__asymm_update(self.__aasymm_edge, self.__aasymm_edge_len)
        self.__symm_update(self.__full, self.__full_len, 1)

# Purpose: Runs and controls the WaterMazeTask program.
# Arguments: None.
# Returns: Nothing.
def watermazetask_runner():
    valid_type = True
    valid_value = False
    print("Welcome to the WaterMazeTask. This program models research on " + \
          "the spatial memory of mice. In this program, a mouse (M) " + \
          "searches and learns the location of a hidden platform (P) in a " + \
          "watermaze. While the platform is visible to the user, it is not " + \
          "visible to the mouse. The user of this program will be able to " + \
          "enter an integer into the program to represent the quality of " + \
          "the spatial memory of the mouse. Following the inputted number, " + \
          "the user will then be able to start a new trial and move the " + \
          "mouse in the watermaze, through a single-move command or " + \
          "through a simulate-trial command. Please note that a trial must " + \
          "be initiated, in order to move the mouse or simulate a trial. " + \
          "Furthermore, after the platform has been found, a new trial " + \
          "must be initiated in order to move the mouse or simulate the " + \
          "trial again.")
    input_statement = "Please input an integer to represent the quality of " + \
                      "the spatial memory of the mouse between 0 and 100% " + \
                      "(inclusive): "
    while not valid_type or not valid_value:
        _input = input(input_statement)
        try:
            _input = int(_input)
        except:
            print("Invalid input. Input must be an integer.")
            valid_type = False
        if valid_type:
             if _input < 0 or _input > 100:
                 print("Invalid input. Input must be between 0 and 100" + \
                       " (inclusive).")
             else:
                 valid_value = True
        else:
            valid_type = True
    wmt_runner = WaterMazeTask(_input)
    _command = input("Please enter one of the following commands: " + \
          " ""New-Trial"", ""Move-Mouse"", ""Sim-Trial"", ""View-Grid""," + \
          " ""Stats"", or ""End"": ")
    _command = _command.lower()
    while _command != "end":
        if _command == "new-trial":
            if wmt_runner.new_trial():
                print(("Started trial number %d") %
                      (wmt_runner.get_trial_number() + 1))
            else:
                print("Unable to start new trial")
        elif _command == "move-mouse":
            if not wmt_runner.make_move():
                print("Unable to move mouse")
        elif _command == "sim-trial":
            if not wmt_runner.trial_simulation():
                print("Simulation could not be completed")
        elif _command == "view-grid":
            wmt_runner.view_watermaze()
        elif _command == "stats":
            wmt_runner.stats()
        else:
            print("Invalid Input.")
        _command = input("Please enter one of the following commands: " + \
              " ""New-Trial"", ""Move-Mouse"", ""Sim-Trial"", ""View-Grid"","+ \
              " ""Stats"", or ""End"": ")
        _command = _command.lower()
watermazetask_runner()
