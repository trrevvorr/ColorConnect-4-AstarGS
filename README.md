# Color Connect - Greedy Best-First Graph Search

## How to Build the Script
#### Compiling*
* *Use Python 2.7*  
* Type `python solve_color_connect.py input_p1.txt`
* Tested and working on OS X, Unix, and Windows
* NOTE: 'output' directory must be created in same directory as solve_color_connect.py for script to function

#### Output
`180088` <- solution took 180088 **_microseconds_**   
`10`     <- there were 10 moves made  
`0 1 0, 0 2 0, 0 3 0, 0 3 1, 0 3 2, 1 1 1, 1 1 2, 1 0 2, 0 3 3, 1 0 3` <- these are the moves  
`0  0  0  0` <- resulting grid with colors connected  
`e  1  1  0`  
`1  1  e  0`  
`1  e  e  0`  

#### Output 2
If you instead compile with `python solve_color_connect.py input_p1.txt pretty`, the output will look something like this:  
![Pretty Output](https://farm2.staticflickr.com/1638/24925140366_6c2556f34f_o.png)

## Heuristic
Moves (or actions) are prioritized by the sum of the distances from each color's path head to its endpoint. Here is an example of how this distance is calculated:  
![heuristic example](https://farm2.staticflickr.com/1592/24324585403_a47bf97959_o.png)  

#### General Case
`row_diff = |row_of_head - row_of_end|`  
`col_diff = |col_of_head - col_of_end|`  
`distance = (row_diff^2 + col_diff^2)^0.5`  

#### Color Specific
`0: (1^2 + 1^2)^0.5 = 1.414`  
`1: (3^2 + 1^2)^0.5 = 3.162`  
`2: (0^2 + 0^2)^0.5 = 0`  
`3: (1^2 + 2^2)^0.5 = 2.236`  
__Total Distance__ = 1.414 + 3.162 + 0 + 2.236 = __6.812__  
#### Choosing a Child
Each child's heuristic value will be calculated and then sent to a priority queue such that the first node in the priority queue will have the smallest total distance of any node in the queue. Nodes with the same total distance will be ordered by which was added first.


## Puzzle Details
The game is Color Connect. Given a square playing board (n x n), connect the matching colors with an unbroken line. All colors must be connected and no two lines may cross. When referencing a point in the grid, the upper left corner is 0x0 and the column should be listed first. Ex: 1,2 = column 1, row 2

#### Example Input
`4 2`      <- 4x4 grid with 2 colors  
`0 e e e`  <- first row, color 0 starts at position 0,0  
`e e 1 e`  <- color 1 starts at 2,1  
`e e e e`  
`1 e e 0`	<- colors 1 and 0 end on row 4



_* I know python isn't technically compiled, it's interpreted, but whatever_
