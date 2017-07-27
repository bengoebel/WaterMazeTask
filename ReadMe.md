Purpose: This is the ReadMe for the WaterMazeTask program.
By: Benjamin Goebel
Date: July 27th, 2017

1. The purpose of this program is to model the research work by
   Richard G.M. Morris titled "Spatial localization does not require the
   presence of local cues". In this program a mouse (M) learns the location
   of a hidden platform (P), through a series of trials. While the
   platform is visible throughout the program to the user, the
   mouse is unaware of the platform's location and must learn the platform's
   location. The mouse learns the platform's location through a series of trials
   where the mouse searches the watermaze for the platform. The mouse can
   only tell if it found the platform if it is at the platform's location. In
   the beginning the mouse searches randomly for the platform but after
   each trial, the mouse begins to move more directly towards the
   platform. How quickly the mouse learns the location of the
   platform is significantly influenced by the value inputted to
   the program at the start of the program. This value, which
   can be from 0 to 100% indicates the quality of the spatial memory of the
   mouse.
2. Excluding this file, there is one other file in this program:
   WaterMazeTask.py.
3. In this program, the watermaze is stored as a 2-D list. The probabilities
   that the mouse moves in a particular direction are stored in a list of
   eight values. These eight values correspond to the directions: N, NE, E, SE,
   S, SW, W, NW, respectively. If the mouse cannot move in any of these
   particular directions, its value is not applicable.
4. The general algorithm for this program is as follows. The mouse moves to
   a location in the watermaze. It retrieves the likelihoods that it moves
   in each particular direction. Based on these probabilities, the mouse
   randomly selects a direction to move in, and the mouse moves one position
   in that direction.
5. This program can be compiled with a Makefile. Users running this program
   must have matplotlib installed on their computers.
