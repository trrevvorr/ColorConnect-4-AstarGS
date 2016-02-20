"""
Reads input puzzle file and prints the output of the solution

AI - CS 5400 - Sec 1A
Puzzle Assignmet 4

Trevor Ross
02/19/2016
"""
import AstarGS
import sys

def parse_arguments(args):
    """
    Takes as input a list of arguments from the script call. Returns the
    contents of the specified file or raises an error if input is invalid
    """
    num_args = len(args)
    appreciation_4_beauty = False

    if num_args > 1:
        # retrieve input file name
        p_file = sys.argv[1]
        # parse the input file
        try:
            (num_colors, pzzl_array) = ReadInput(p_file)
        except IOError:
            input_error('invalid name')
        # look for a third argument
        if num_args > 2:
            # retrieve optional 'pretty' command
            if sys.argv[2] == 'pretty':
                appreciation_4_beauty = True
            else:
                input_error('no pretty')
    else:
        input_error('no name')

    return (num_colors, pzzl_array, appreciation_4_beauty)


def ReadInput(pzzl_file):
    """
    Reads in a puzzle file and parses the data for solving

    INPUT: first line: # rows/columns, # of colors
    the input puzzle will follow as a square matrix
    OUTPUT: returns a tuple with the number of colors and the puzzle as a 2D array
    """
    in_file_path = 'input/' + pzzl_file
    f_hand = open(in_file_path)

    pzzl_array = []
    # read every line into pzzle_array (even first line)
    for line in f_hand:
        line = line.split()
        pzzl_array.append(line)
    # pop first line and store it's second element (num colors)
    first_line = pzzl_array.pop(0)
    num_colors = int(first_line.pop())

    f_hand.close()
    return (num_colors, pzzl_array)


def input_error(e_type):
    """
    Prints error message and exits script if user did not enter a valid input file
    """
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

    if e_type == "no name":
        # user did not enter input file name
        print FAIL + 'ERROR: you must include the file name in argument list'
        print 'EXAMPLE: "solve_color_connect.py input_p1.txt"\n' + ENDC
        exit(1)
    elif e_type == "invalid name":
        # input file does not exist
        print FAIL + 'ERROR: the file you enered as input does not exist in input directory'
        print 'CORRECT EXAMPLE: "solve_color_connect.py input_p1.txt"\n' + ENDC
        exit(1)
    elif e_type == 'no pretty':
        print WARNING + '\n!! TYPE "pretty" IF YOU WOULD LIKE VISUAL OUTPUT !!'
        print 'EXAMPLE: "solve_color_connect.py input_p1.txt pretty"' + ENDC
    else:
        print FAIL + "UNKNOWN e_type ENERED: %s" % e_type + ENDC
        exit(1)


def UglyPrint(sol_nodes, duration):
    """
    Prints out action sequence and final array to command line (as well as solution file)

    INPUT: list of nodes from root to final for solution path and duration of runtime
    OUTPUT: action format: color col_moved_to row_moved_to, color col_moved_to etc.
    NOTE: this function will not work properly if SMART_FINAL_DETECT set to True
    in the VerifyFinal() function
    """
    final_state = sol_nodes[-1].state
    in_file_name = sys.argv[1]
    out_file_name = 'p%s_solution.txt' % in_file_name[7]
    out_file_path = 'output/' + out_file_name
    out_file = open(out_file_path, 'w')

    # time in microseconds
    out_file.write(str(int(duration * 1000000)))
    out_file.write('\n')
    # path cost of solution
    out_file.write(str(sol_nodes[-1].path_cost))
    out_file.write('\n')

    # find all actions stored in nodes
    actions = []
    for node in sol_nodes:
        if node.action is None:
            continue
        else:
            actions.append(node.action)

    for i, action in enumerate(actions):
        if i + 1 < len(actions):
            comma = ','
        else:
            comma = ''
        # build output with rows and colums revered per Dr. T's request
        output = '%d %d %d%s' % (action[0], action[2], action[1], comma)
        # print actions
        out_file.write(output)
    out_file.write('\n')

    # print final state
    for row in final_state:
        for char in row:
            out_file.write(char + ' ')
        out_file.write('\n')

    out_file.close()
    print 'DONE!\nView %s for solution' % out_file_path


def PrettyPrint(start_node):
    """
    Reads the output files created by UglyPrint and visualizes them in stdout

    Also serves as a way to error-check the solution files
    """
    in_file_name = sys.argv[1]
    solution_file_name = 'p%s_solution.txt' % in_file_name[7]
    sol_file_path = 'output/' + solution_file_name
    solution_file = open(sol_file_path, 'r')

    # READ FROM FILE
    # line 1
    microseconds = float(solution_file.readline())
    seconds = microseconds / 1000000
    # line 2
    step_count = int(solution_file.readline())
    # line 3
    steps = solution_file.readline()
    solution_file.close()
    # seperate each action delimited by ','
    steps = steps.split(',')
    if len(steps) != step_count:
        print 'ERROR: step count does not agree with number of actions taken'
        print 'STEP COUNT:', step_count
        print 'ACTIONS:', steps
        exit(1)
    # put actions into a list
    actions = []
    for step in steps:
        # seperate each item of the action delimited by ' '
        action = step.split()
        actions.append(action)

    # BEGIN PRINTING
    # print the root
    print '\nVISUAL OUTPUT OF SOLUTION FILE'
    move_counter = 0
    print '<<< ACTION %d >>>' % move_counter
    start_node.visualize()
    # print the rest of the states
    for action in actions:
        color = action[0]
        col = int(action[1])
        row = int(action[2])

        start_node.state[row][col] = color
        start_node.path_heads[int(color)] = [row, col]
        # print the state
        move_counter += 1
        print '<<< ACTION %d >>>' % move_counter
        start_node.visualize()


    print '== FINISHED IN %4.4f SECONDS ==' % seconds

################################################################################
# Main
################################################################################

def main(args):
    # parse the arguments and return contents of input file
    (num_colors, pzzl_array, appreciation_4_beauty) = parse_arguments(args)

    # solve the input puzzle
    solution, run_time = AstarGS.solve(pzzl_array, num_colors)

    # print solution
    if solution is False:
        print '== NO SOLUTION POSSIBLE! =='
    else:
        UglyPrint(solution, run_time)
        if appreciation_4_beauty:
            PrettyPrint(solution[0])

if __name__ == "__main__":
    main(sys.argv)
