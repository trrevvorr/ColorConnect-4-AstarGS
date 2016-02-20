# Color Connect - A* Graph Search

## How to Build the Script
#### Compiling*
* *Use Python 2.7*  
* Type `python solve_color_connect.py input_p1.txt`
* Tested and working on OS X, Unix, and Windows
* NOTE: 'output' directory must be created in same directory as solve_color_connect.py for script to function

#### Output (/output/p1_solution.txt)
`180088` <- solution took 180088 **_microseconds_**   
`10`     <- there were 10 moves made  
`0 1 0, 0 2 0, 0 3 0, 0 3 1, 0 3 2, 1 1 1, 1 1 2, 1 0 2, 0 3 3, 1 0 3` <- these are the moves  
`0  0  0  0` <- resulting grid with colors connected  
`e  1  1  0`  
`1  1  e  0`  
`1  e  e  0`  

#### Output (visulized in terminal)
If you instead compile with `python solve_color_connect.py input_p1.txt pretty`, the output will look something like this:  
![Pretty Output](https://farm2.staticflickr.com/1638/24925140366_6c2556f34f_o.png)

## Heuristic
Moves (or actions) are prioritized by the sum of the distances from each color's path head to its endpoint. Here is an example of how this distance is calculated:  
![heuristic example](https://farm2.staticflickr.com/1622/24522523913_2791ae7566_o.png)  

#### g(n) [path cost]
`g(0) = 4`  
`g(1) = 5`  
`g(2) = 1`  
`g(3) = 3`  

#### h(n) [Euclidian distance]
`h(0) = (2^2 + 2^2)^0.5 = 2.828`  
`h(1) = (1^2 + 0^2)^0.5 = 1`  
`h(2) = (1^2 + 1^2)^0.5 = 1.414`  
`h(3) = -1` _(compels colors to connect)_  

#### f(n) = g(n) + h(n)
`f(0) = 4 + 2.828 = 6.828`  
`f(1) = 5 + 1 =  6`  
`f(2) = 1 + 1.414 = 2.414`  
`f(3) = 3 + -1 = 2`  

__Total Distance__ = 6.828 + 6 + 2.414 + 2 = __17.242__  

#### Choosing a Child
Each child's f(n) value will be calculated and then sent to a priority queue such that the first node in the priority queue will have the smallest f(n) of any node in the queue. Nodes with the same f(n) will be ordered by which was added first.


## Puzzle Details
The game is Color Connect. Given a square playing board (n x n), connect the matching colors with an unbroken line. All colors must be connected and no two lines may cross. When referencing a point in the grid, the upper left corner is 0x0 and the column should be listed first. Ex: 1,2 = column 1, row 2

#### Example Input
`4 2`      <- 4x4 grid with 2 colors  
`0 e e e`  <- first row, color 0 starts at position 0,0  
`e e 1 e`  <- color 1 starts at 2,1  
`e e e e`  
`1 e e 0`	<- colors 1 and 0 end on row 4



_* I know python isn't technically compiled, it's interpreted, but whatever_
