"""
Solves Color Connect Puzzle via greedy best-first graph search as per
Puzzle 2 requirement

AI - CS 5400 - Sec 1A
Puzzle Assignmet 2 - Phase 1

Trevor Ross
02/09/2016
"""
import copy
import random
import time
import heapq

################################################################################
# CLASSES
################################################################################

class Node(object):
    """Tree node for State Tree"""
    def __init__(self, ID, state, parent_node=None, action=None):
        # Unique identifier for this node
        self.ID = ID  # integer
        # the curent state of this node in the form of a 2D array
        self.state = state  # format: [[... row 1 ...], [... row 2 ...], ...]
        # action that was taken on the parent node to produce this child node
        self.action = action  # format: [color_num, row_shift, col_shift]
        # the sum of the distances between each color's path_heads and path_end
        # if all colors are connected, total_dist will be 0
        self.total_dist = None

        # copy info from parent if one exists
        if parent_node is None:
            self.p_ID = None
            self.path_cost = None
            self.path_start = None
            self.path_heads = None
            self.path_end = None
        else:
            # ID of parent node
            self.p_ID = parent_node.ID  # integer
            # the cost of the path starting at the root, ending at this node
            self.path_cost = parent_node.path_cost + 1  # integer
            # coordinates of start positions of all colors in puzzle
            self.path_start = parent_node.path_start.copy()  # format: {0:[r0,c0], 1:[r1,c1], ...}
            # coordinates of trail head positions of all colors in puzzle
            self.path_heads = parent_node.path_heads.copy()  # format: {0:[r0,c0], 1:[r1,c1], ...}
            # coordinates of end positions of all colors in puzzle
            self.path_end = parent_node.path_end.copy()  # format: {0:[r0,c0], 1:[r1,c1], ...}

    def heuristic(self):
        """
        Finds the total distance from each color's path_head to its path_end.

        WARNING: self.path_heads must be updated before running this method.
        This number is stored in self.total_dist and is used as the hueristic
        to prioritize actions on a color path. The smaller the distance, the
        more it will be prioritized.
        """
        self.total_dist = 0.0

        for color_num in self.path_start.keys():
            head = self.path_heads[color_num]
            end = self.path_end[color_num]

            row_diff = abs(head[0] - end[0])
            col_diff = abs(head[1] - end[1])
            # MANHATTAN DISTANCE
            # path_len = row_diff + col_diff
            # EUCHLIDIAN DISTANC
            path_len = (row_diff ** 2 + col_diff ** 2) ** (0.5)
            if path_len == 0:
                path_len = -1
            self.total_dist += path_len
        self.total_dist += self.path_cost

    def hashable_state(self):
        """
        Returns a hashable object containing nessisary information to uniquely
        identify a particular state (path_heads and state).

        INPUT: uses self.path_heads and self.state
        OUTPUT: string in the form '00eee*0e*1eeeeeeee' which is the concatination
        of row1, row2, row3, etc. with each '*' representing the path heads. Each
        '*' apears before its respective cell.
        """
        state_list = []
        for r, row in enumerate(self.state):
            for c, cell in enumerate(row):
                if [r,c] in self.path_heads.values():
                    state_list.append('*')
                state_list.append(cell)

        return ''.join(state_list)

    def state_info(self):
        """Prints contents of all member variables in node"""
        print '=' * 30
        print 'ID:', self.ID
        print 'p_ID:', self.p_ID
        print 'action:', self.action
        print 'path_cost:', self.path_cost
        print 'path_start:', self.path_start
        print 'path_heads:', self.path_heads
        print 'path_end:', self.path_end
        print 'total distance:', self.total_dist

    def visualize(self):
        """
        Prints out a visual representation of the node

        OUTPUT: 2D array of the state of the node, start and end points are
        underlined, trail heads are bolded
        """
        # pretty colors
        COLORS = ['\033[95m', '\033[92m', '\033[93m', '\033[91m', '\033[94m']
        BOLD = '\033[1m'
        UNDERLINE = '\033[4m'
        ENDC = '\033[0m'

        # top horizontal divider
        print '%s%s' % (('+---' * len(self.state)), '+')
        for r, row in enumerate(self.state):
            print '|',  # front vertical divider
            for c, char in enumerate(row):
                # empty + vertical divider
                if char == 'e':
                    print ' ', '|',
                # color num + vertical divider
                else:
                    c_num = int(char)
                    start_coord = self.path_start[c_num]
                    head_coord = self.path_heads[c_num]
                    end_coord = self.path_end[c_num]
                    # apply colors and styles to color number
                    # apply color
                    style = COLORS[c_num % 5]
                    if [r, c] == start_coord or [r, c] == end_coord:
                        # start and end points are underlined
                        style = UNDERLINE + style
                    if [r, c] == head_coord:
                        # trail heads are bolded
                        style = BOLD + style
                    # print the cell with style
                    print style + char + ENDC, '|',
            # horizontal divider
            print '\n%s%s' % (('+---' * len(row)), '+')


class StateTree(object):
    """Creates a State Tree for the puzzle, allowing ID-DFTS on said puzzle"""
    def __init__(self, initial_puzzle, number_of_colors):
        self.num_colors = number_of_colors
        # a globla ID index for creating unique node IDs
        self.uniq_ID = 0

        # create a root node and fill in the details
        self.root = Node(self.uniq_ID, state=initial_puzzle)
        # find coordinates of the start of the color path
        self.root.path_start = FindColorStart(self.root.state, self.num_colors)
        self.root.path_heads = copy.deepcopy(self.root.path_start)
        # find coordinates of the end of the color path
        self.root.path_end = FindColorEnd(self.root.state, self.num_colors)
        # initialize root's path cost and total distance from goal
        self.root.path_cost = 0
        self.root.heuristic()
        # timing variable
        self.run_time = None
        # used to look up a node by its ID
        self.node_dict = {self.root.ID: self.root}

    def AstarGS(self):
        """
        Uses A-Star Graph Search to find solution

        Heuristic = shortest distance between path_head and path_end
        Action that produces the state with the smallest heuristic(n) is chosen
        """
        self.run_time = time.time()
        # create the priority queue and put the root in it
        # format: [node_priority, node_ID]
        frontier = []
        heapq.heappush(frontier, [self.root.total_dist, self.root.ID])
        # the explored set contains all the states already evaluated as well as
        # those in the frontier. Rather than searching the frontier and the
        # set of evaluated nodes seperatly, this set contains the union of those
        # two sets so they can both be be searched at the same time.
        explored = set(self.root.hashable_state())

        # loop until broken by final state or no nodes left in frontier
        while frontier:
            # pop the first item of the priority queue, it will be evaluated
            node_ev = heapq.heappop(frontier)
            node_ev = self.node_dict[node_ev[1]]

            #######
            # node_ev.visualize()
            # print 'f(n) =', node_ev.total_dist,
            # print '=', node_ev.path_cost,
            # print '+', node_ev.total_dist - node_ev.path_cost
            #
            # time.sleep(0.1)
            #######

            # check if the node is the final state
            if VerifyFinal(node_ev) is True:
                self.run_time = time.time() - self.run_time
                return TraceBack(node_ev, self.node_dict)

            # find all the valid actions from node_ev and iterate through them
            valid_actions = Action(node_ev, self.num_colors)
            # if a parent has no children, remove it from the node_dict
            if len(valid_actions) == 0:
                del self.node_dict[node_ev.ID]

            for color_num, action, new_coord in valid_actions:
                self.uniq_ID += 1
                # retulting child state from parent acted on by action
                child_state = Result(node_ev.state, node_ev.path_heads[color_num], action)
                # create the new child node
                child = Node(self.uniq_ID, child_state, action=([color_num] + new_coord), parent_node=node_ev)
                # updated the child's path head and total_dist
                child.path_heads[color_num] = new_coord
                # GRAPH SEARCH
                # if the child exists in the explored set, do not add it to the frontier
                if child.hashable_state() in explored:
                    continue
                # otherwise, add it to the explored set, the node_dict, and the frontier
                explored.add(child.hashable_state())
                child.heuristic()
                self.node_dict[child.ID] = child
                # adding child to frontier will automatically insert it at the
                # correct position in the priority queue
                heapq.heappush(frontier, [child.total_dist, child.ID])

        # No solution was found
        self.run_time = time.time() - self.run_time
        return False

################################################################################
## FUNCTIONS
################################################################################

def OutOfBounds(coord, puzzle_dim):
    """
    Returns true if coordinats are out of bounds of the puzzle
    Returs false otherwise
    """
    new_row, new_col = coord
    LOWER_BOUND = 0
    UPPER_BOUND = puzzle_dim

    if new_col < LOWER_BOUND or new_col >= UPPER_BOUND:
        return True
    if new_row < LOWER_BOUND or new_row >= UPPER_BOUND:
        return True

    return False


def FindColorStart(puzzle, num_colors):
    """
    Given the puzzle and the number of colors to find, function will
    return a dict with the FIRST occurance of the number as the key and its
    coordinates as the value

    OUTPUT: dictionary in the format: {0:[r0,c0], 1:[r1,c1],...}
    """
    coordinates = {}  # format: {0:[r0,c0], 1:[r1,c1],...} where r = row, c = col
    dim = len(puzzle)
    # list of all color numbers
    color_nums = range(num_colors)
    # find coordinate for each color start
    for row_i in xrange(dim):
        for col_i in xrange(dim):
            char_found = puzzle[row_i][col_i]
            if char_found == 'e':
                continue
            # if number has not been seen yet, it is the Start Position
            if int(char_found) in color_nums:
                num_found = int(char_found)
                # remove it from the list so it won't be found again
                color_nums.remove(num_found)
                coordinates[num_found] = [row_i, col_i]

    # error checking to make sure correct number of colors were found
    if len(coordinates) != num_colors:
        print 'ERROR: PROBLEMS FINDING COLORS'
        print 'COORDINATES: %r' % coordinates
        print 'START COLORS TO BE FOUND: %r' % range(num_colors)
        exit(1)

    return coordinates


def FindColorEnd(puzzle, num_colors):
    """
    Given the puzzle and the number of colors to find, function will return
    a dict with the LAST occurance of the number as the key and its
    coordinates as the value

    OUTPUT: dictionary in the format: {0:[r0,c0], 1:[r1,c1],...}
    """
    coordinates = {}  # format: {0:[r0,c0], 1:[r1,c1],...}  where r = row, c = col
    dim = len(puzzle)
    color_nums = range(num_colors)  # list of all color numbers
    # find coordinate for each color start
    for row_i in xrange(dim):
        for col_i in xrange(dim):
            char_found = puzzle[row_i][col_i]
            # if char found is an e then go to then skip it
            if char_found == 'e':
                continue
            # remove the first number of the pair from the color_nums list
            if int(char_found) in color_nums:
                num_found = int(char_found)
                color_nums.remove(num_found)
            # if the number no longer exists in color_nums, it is an end number
            else:
                num_found = int(char_found)
                coordinates[num_found] = [row_i, col_i]

    # error checking to make sure correct number of colors were found
    if len(coordinates) != num_colors:
        print 'ERROR: PROBLEMS FINDING COLORS'
        print 'COORDINATES: %r' % coordinates
        print 'END COLORS TO BE FOUND: %r' % range(num_colors)
        exit(1)

    return coordinates


def Action(node, num_colors):
    """
    Given a node, return a shuffled list of valid actions on that node

    VALID MOVE DISQUALIFICATION: if even ONE of the colors has no valid
    moves and is not in a goal state, no valid moves will be returned for
    ANY other colors. Furthermore, ActionOnColor() is called and it further
    limits the amount of actions returned
    OUTPUT: shuffled list of color nums , actions, and new coords
    """
    # shuffled list of valid actions to perform on node
    # format: [[n, [r_, c_], [r', c']], [n, [r_, c_], [r', c']], ...]
    # such that n is the color number, r_ is the row action,
    # c_ is the column action, r' is the new row, c' is the new column
    valid_actions = []

    # find which colors are already connected
    colors_connected = VerifyFinal(node)
    if colors_connected is True:
        return []
    # get a list of colors in puzzle
    color_numbers = range(num_colors)
    # if the color is already connected, no further action needed on color
    for color in colors_connected:
        color_numbers.remove(color)

    # iterate through remaining colors, finding actions for each
    for color in color_numbers:
        # add actions for this color to the valid actions list
        valid_actions += (ActionOnColor(node, color))

    random.shuffle(valid_actions)
    return valid_actions


def ActionOnColor(node, color):
    """
    Given a node and a color, the function will return a list of all
    valid moves for that color

    VALID MOVE DISQUALIFICATION:
    1) action moves color path out of puzzle's bounds
    2) action moves color path onto a pre-existing path
    OUTPUT: returns a list of valid actions as well as the coordinates they
    result in, along with the color the action was performed on
    FORMAT: the 4 possible actions are: [[-1,0], [0,1], [1,0], [0,-1]]
    """
    coord = node.path_heads[color]
    end_coord = node.path_end[color]
    valid_actions = []

    # actions in order: up, right, down, left
    action_options = [[-1,0], [0,1], [1,0], [0,-1]]
    for action in action_options:
        new_row = coord[0] + action[0]
        new_col = coord[1] + action[1]
        new_coord = [new_row, new_col]
        # if new cell is the the goal cell, add it to the list of valid actions
        if [new_row, new_col] == end_coord:
            valid_actions.append([color, action, new_coord])
            continue
        # 1) invalid if action is out-of-bounds
        if OutOfBounds([new_row, new_col], len(node.state)):
            continue
        # 2) invalid if new cell is already occupied
        if node.state[new_row][new_col] != 'e':
            continue
        # otherwise, it is invalid
        valid_actions.append([color, action, new_coord])

    return valid_actions


def Result(p_state, coord, action):
    """
    Return the result of taking action on the coordinate of the given state

    OUTPUT: Puzzle state in the form: [[... row 1 ...], [... row 2 ...], ...]
    """
    new_state = copy.deepcopy(p_state)
    # retrieve the 'color' of the path to be extended
    color_path_to_extend = p_state[coord[0]][coord[1]]
    # find the location to place the extention
    new_row = coord[0] + action[0]
    new_col = coord[1] + action[1]
    # 'color' the new loaction, extending the line
    new_state[new_row][new_col] = color_path_to_extend

    return new_state


def VerifyFinal(node):
    """
    Verify that the passed node has a final state

    IF FINAL: return True
    IF NOT FINAL: return a list of those colors who are final
    """
    colors_connected = []

    for color in node.path_end:
        # get path_end and path_head coordinates for color
        end = node.path_end[color]
        head = node.path_heads[color]
        if end == head:
            colors_connected.append(color)

    # if all colors are connected, return true
    if len(colors_connected) == len(node.path_end):
        return True
    # otherwise return a list of the colors who are connected
    else:
        return colors_connected


def TraceBack(end_node, node_dict):
    """
    Given the final node. find path from the final node to the root

    OUTPUT: list of all the nodes from root to final. [root, ... , final]
    """
    node_path = []
    node = end_node
    # keep adding node to node_path until root node is found
    while node.action is not None:
        # insert in front of list since traversal is bottom-up
        node_path.insert(0, node)
        # move to parent node
        node = node_dict[node.p_ID]
    # add the root
    node_path.insert(0, node)
    return node_path

################################################################################
# Main
################################################################################

def solve(pzzl_array, num_colors):
    random.seed()

    # build state tree and find solution
    PTree = StateTree(pzzl_array, num_colors)
    solution = PTree.AstarGS()

    return (solution, PTree.run_time)
