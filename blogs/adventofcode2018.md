# Advent of Code 2018: Days 1-12

[ctf](/tags#ctf ) [advent-of-code](/tags#advent-of-code )
[python](/tags#python )  
  
Dec 12, 2018

Advent of Code 2018: Days 1-12

![](https://0xdfimages.gitlab.io/img/aoc2018-cover.png)Advent of Code is a fun
CTF because it forces you to program, and to think about data structures and
efficiency. It starts off easy enough, and gets really hard by the end. It’s
also a neat learning opportunity, as it’s one of the least competitive CTFs I
know of. After the first 20 people solve and the leaderboard is full, people
start to post answers on reddit on other places, and you can see how others
solved it, or help yourself when you get stuck. I’m going to create one post
and just keep updating it with my answers as far as I get.

## Day 12

![](https://0xdfimages.gitlab.io/img/aoc2018-12.png)

### Challenge

<https://adventofcode.com/2018/day/12>

Day 12 was another interesting spatial problem with iteration. I’m given a
starting plot that looks like this: `#..#.#..##......###...###`

I’m also given a set of rules that define what will be in each pot in the next
generation depending on current status of the pot and it’s two neighbors to
each side. Each rule looks like `...## => #`

In the first challenge, I’m asked to find the status after 20 generations. In
the second, I’m asked to find it after 50,000,000,000.

### Solution

To solve the first part, I created a `garden` class, which takes my input and
keys, and then has a `grow` function to advance to the next generation. My
line of plants is just a string. I’ll add four empty pots to each side to
start, and then walk down the string, using a dictionary of my rules to get
the next value. I’ll also need to track what index the start of the list is as
I add and subtract pots, as the checksum I need to submit at the end is based
on the index of the pot and if there’s a plant in it. I created a `value`
function to return the value of the garden.

That solved part 1 quite easily. But part 2 is so large, it would take a
really long time to run. I needed to find something else. I let it grow for
10000 generations more, and added a line to print the output including
generation, index value of the first item, the value of the garden, and the
garden itself, with empty pots trimmed from each side. My results looked like
this:

    
    
    ...[snip]...
    10008 [9974][  692820]: ###...###...###...###...###...###...###...###...###...###...###...###...###...###...###...###...###...###...###...###...###..###..###.
    10009 [9975][  692889]: ###...###...###...###...###...###...###...###...###...###...###...###...###...###...###...###...###...###...###...###...###..###..###.
    10010 [9976][  692958]: ###...###...###...###...###...###...###...###...###...###...###...###...###...###...###...###...###...###...###...###...###..###..###.
    10011 [9977][  693027]: ###...###...###...###...###...###...###...###...###...###...###...###...###...###...###...###...###...###...###...###...###..###..###.
    10012 [9978][  693096]: ###...###...###...###...###...###...###...###...###...###...###...###...###...###...###...###...###...###...###...###...###..###..###.
    10013 [9979][  693165]: ###...###...###...###...###...###...###...###...###...###...###...###...###...###...###...###...###...###...###...###...###..###..###.
    10014 [9980][  693234]: ###...###...###...###...###...###...###...###...###...###...###...###...###...###...###...###...###...###...###...###...###..###..###.
    10015 [9981][  693303]: ###...###...###...###...###...###...###...###...###...###...###...###...###...###...###...###...###...###...###...###...###..###..###.
    10016 [9982][  693372]: ###...###...###...###...###...###...###...###...###...###...###...###...###...###...###...###...###...###...###...###...###..###..###.
    10017 [9983][  693441]: ###...###...###...###...###...###...###...###...###...###...###...###...###...###...###...###...###...###...###...###...###..###..###.
    10018 [9984][  693510]: ###...###...###...###...###...###...###...###...###...###...###...###...###...###...###...###...###...###...###...###...###..###..###.
    10019 [9985][  693579]: ###...###...###...###...###...###...###...###...###...###...###...###...###...###...###...###...###...###...###...###...###..###..###.
    10020 [9986][  693648]: ###...###...###...###...###...###...###...###...###...###...###...###...###...###...###...###...###...###...###...###...###..###..###.
    

It’s the same, only the plants are sliding to the right, as you can see by the
growing initial index number. More importantly, the value is clearly growing
by 69 each generation. It grows by 69 because there are 69 plants, each moving
one spot to the right (larger value). This is easy enough to solve in O(1).

    
    
    m*10020 + b = 693648
    m*10019 + b = 693579
    m = 69
    b = 2268
    
    value(t) = 69*t + 2268
    

So, update code for steady state solution:

    
    
      1 #!/usr/bin/env python3
      2 
      3 import sys
      4 from collections import defaultdict
      5 
      6 
      7 class garden:
      8     def __init__(self, initial_state, key_input):
      9         self.generation = 0
     10         self.first_idx = 0
     11         self.state = initial_state.split(' ')[-1]
     12         self.keys = defaultdict(lambda: '.')
     13         for keystr in key_input:
     14             key, value = map(str.strip, keystr.split('='))
     15             self.keys[key] = value[-1]
     16 
     17     def grow(self):
     18         while self.state[:4] != '....':
     19             self.state = '.' + self.state
     20             self.first_idx -= 1
     21         while self.state[-4:] != '....':
     22             self.state = self.state + '.'
     23         new_state = '..'
     24         for i in range(len(self.state) - 4):
     25             new_state += self.keys[self.state[i:i+5]]
     26         self.first_idx += new_state.index('#')
     27         self.state = new_state.lstrip('.')
     28         self.generation += 1
     29         #print(f"{self.generation:>2} [{self.first_idx:>4}][{self.value():>8}]: {self.state}")
     30 
     31 
     32     def value(self):
     33         return sum((i+self.first_idx) for i, x in enumerate(self.state) if x == '#')
     34 
     35 
     36 with open(sys.argv[1], 'r') as f:
     37     init, _, *keys = map(str.strip, f.readlines())
     38 
     39 g = garden(init, keys)
     40 for _ in range(20): g.grow()
     41 print(f"Part 1: {g.value()}")
     42 
     43 #for _ in range(10000): g.grow()
     44 print(f"Part 2: {69*50000000000 + 2268}")
    
    
    
    $ time ./day12.py 12-puzzle_input.txt
    Part 1: 3903
    Part 2: 3450000002268
    
    real    0m0.018s
    user    0m0.008s
    sys     0m0.011s
    

## Day 11

![](https://0xdfimages.gitlab.io/img/aoc2018-11.png)

### Challenge

<https://adventofcode.com/2018/day/11>

I found day 11 pretty straight forward. I’m given a complex formula to find a
value for each coordinate in a 300x300 grid, based on the x value, the y
value, and one input integer. First, I’m then asked to find the 3x3 square
with the max total value. Then I’m asked to find the square of any size with
the max total value. The only trick comes into play deciding when I could cut
off the search over different square sizes.

### Solution

I created a few functions, and keep building on them. First, I created a
function to create a grid using a dictionary, where the key was the tuple (x,
y), and the value was the power value for that cell.

Next I created a function to take a grid of cells, and find the 3x3 square
with the largest total power by walking across the grid. I later updated this
to take a size parameter, so I could find the largest value for a given size
square.

Finally, I created a function that takes a grid of cells, and loops over a
given range of square sizes, calling the second function, and keeping the
maximum square size. It also keeps track of if the resulting value is going up
or down, and if it is decreasing for 3 sizes in a row, it exits.

The logic behind that exit is as follows. There must be a lot of negative
values in the grid. If there numbers were all positive, the largest square
would be 300x300. Given that the creators likely didn’t want that answer, and
they even went do far as to call out that there could be negative values,
there’s likely a place where increasing the square size stops increasing the
result, and starts decreasing. Once I see three decreases in a row, I’ll stop
and try my answer.

    
    
      1 #!/usr/bin/env python3
      2 
      3 
      4 def make_cells(serial):
      5     cells = {}
      6     for y in range (1,301):
      7         for x in range(1, 301):
      8             cells[(x,y)] = ((((((10 + x) * y) + serial) * (10 + x)) % 1000) // 100) - 5
      9     return cells
     10 
     11 
     12 def find_square(cells, size=3):
     13     max_total = 0
     14     max_top_left = (0,0)
     15     for y in range(1,301-size):
     16         for x in range(1,301-size):
     17             square = 0
     18             for dy in range(0,size):
     19                 for dx in range(0,size):
     20                     square += cells[(x+dx, y+dy)]
     21             if max_total < square:
     22                 max_total = square
     23                 max_top_left = (x,y)
     24     return max_total, max_top_left
     25 
     26 
     27 def find_axa(cells, start_size=1, stop_size=300):
     28     max_power = 0
     29     max_top_left = (0,0)
     30     max_size = 1
     31     decreasing_count = 0
     32     prev_power = 0
     33     for x in range(start_size, stop_size):
     34         power, top_left = find_square(cells, x)
     35         if power > max_power:
     36             max_power = power
     37             max_top_left = top_left
     38             max_size = x
     39 
     40         if power < prev_power:
     41             decreasing_count += 1
     42         else:
     43             decreasing_count = 0
     44 
     45         if decreasing_count > 2:
     46             break
     47 
     48         prev_power = power
     49         #print(f"size {x}: largest: {power}, top_left: {top_left}")
     50     return (max_top_left[0], max_top_left[1], max_power)
     51 
     52 
     53 
     54 #print(make_cells(8)[(3,5)])
     55 #print(make_cells(57)[(122,79)])
     56 #print(make_cells(39)[(217,196)])
     57 #print(make_cells(71)[(101,153)])
     58 
     59 #print(find_square(make_cells(18)))
     60 #print(find_square(make_cells(42)))
     61 cells = make_cells(6392)
     62 print(f"Part 1: {find_square(cells)[1]}")
     63 print(f"Part 2: {find_axa(cells)}")
    
    
    
    $ time ./day11.py
    Part 1: (20, 58)
    Part 2: (233, 268, 83)
    
    real    0m13.968s
    user    0m13.944s
    sys     0m0.024s
    

## Day 10

![](https://0xdfimages.gitlab.io/img/aoc2018-10.png)

### Challenge

<https://adventofcode.com/2018/day/10>

Today’s challenge was one of the first that required not only some programming
skills, but also some skill to pragmatically determine when you’re done. I’m
given positions and velocities for points on a two dimensional space. Over
time, the points will spell something out, but it’s up to me to figure out
when that is, and what it says.

### Solution

I decided that the stars were all moving around, and that I could look at the
size of the box that they all fit into, and that the smallest time would
likely be the time I’m looking for. So I ran the points through their
progressions recording time and size, and then I plotted that. I got this
output:

![1544460212146](https://0xdfimages.gitlab.io/img/1544460212146.png)

Then I recorded the minimum size, and that time at that point, and ran the
points from the start to that point again, and plotted it to get my letters:

![1544460254559](https://0xdfimages.gitlab.io/img/1544460254559.png)

    
    
      1 #!/usr/bin/env python3
      2
      3 import re
      4 import sys
      5 import matplotlib.pyplot as plt
      6
      7
      8 class point():
      9     def __init__(self, coord, vel):
     10         self.x = coord[0]
     11         self.y = coord[1]
     12         self.dx = vel[0]
     13         self.dy = vel[1]
     14
     15     def __lt__(self, other):
     16         return (self.y, self.x) < (other.y, other.x)
     17
     18     def advance(self):
     19         self.x += self.dx
     20         self.y += self.dy
     21
     22
     23 def get_size(points):
     24     min_x = min([p.x for p in points])
     25     max_x = max([p.x for p in points])
     26     min_y = min([p.y for p in points])
     27     max_y = max([p.y for p in points])
     28     return (max_x - min_x) * (max_y - min_y)
     29
     30
     31 with open(sys.argv[1], 'r') as f:
     32     steps = [tuple(map(int, re.findall(r'(-?\d+)', line))) for line in f.readlines()]
     33
     34 points = []
     35 for p in steps:
     36     points.append(point((p[0], p[1]), (p[2], p[3])))
     37
     38 sizes = []
     39 for i in range(20000):
     40     sizes.append(get_size(points))
     41     [p.advance() for p in points]
     42
     43 plt.scatter(list(range(20000)), sizes)
     44 plt.show()
     45 min_size = min(sizes)
     46 min_time = sizes.index(min_size)
     47 print(f"Smallest size is {min_size} at time {min_time}")
     48
     49 points = []
     50 for p in steps:
     51     points.append(point((p[0], p[1]), (p[2], p[3])))
     52
     53 sizes = []
     54 for i in range(min_time):
     55     sizes.append(get_size(points))
     56     [p.advance() for p in points]
     57
     58 xs = [p.x for p in points]
     59 ys = [-p.y for p in points]
     60 plt.scatter(xs, ys)
     61 plt.show()
    

There is almost certainly a more efficient way to do that, but this didn’t
take too long (run without plots for time):

    
    
    $ time ./day10.py 10-puzzle_input.txt
    Smallest size is 549 at time 10240
    
    real    0m5.360s
    user    0m5.326s
    sys     0m0.604s
    

## Day 9

![](https://0xdfimages.gitlab.io/img/aoc2018-09.png)

### Challenge

<https://adventofcode.com/2018/day/9>

Day 9 was pretty quick to solve, until part two asks you to do it with a huge
data set, and list splicing in python grinds things to a halt. This is a good
chance to play with another `collections` class, `deque`. It’s efficient
enough to handle this problem super fast.

We’re given a game where numbers are inserted into a list following certain
rules, and then pulled out based on certain rules. Our input is just the
number of players and the number of marbles.

### Solution

Like I said above, this was a good chance to use `deque` to build the
structure of the game, and then it was quite simple:

    
    
      1 #!/usr/bin/env python3
      2
      3 from collections import defaultdict, deque
      4
      5
      6 def run_game(num_players, max_mar):
      7
      8     players = defaultdict(int)
      9     game = deque([1,0])
     10
     11     for i in range(2, max_mar + 1):
     12
     13         if i % 23:
     14             game.append(i)
     15             game.rotate(-1)
     16             #print(game)
     17         else:
     18             game.rotate(8)
     19             val = game.pop()
     20             players[i % num_players] += i  + val
     21             game.rotate(-2)
     22
     23     return max(players.values())
     24
     25 #print(f"Part 1: {run_game(10,1618)}")
     26 print(f"Part 1: {run_game(464, 70918)}")
     27 print(f"Part 2: {run_game(464,70918*100)}")
    
    
    
    $ time ./day9.py
    Part 1: 370210
    Part 1: 3101176548
    
    real    0m1.132s
    user    0m1.076s
    sys     0m0.056s
    

## Day 8

![](https://0xdfimages.gitlab.io/img/aoc2018-08.png)

### Challenge

<https://adventofcode.com/2018/day/8>

We get a string of numbers, which form nodes consisting of header (two
numbers) giving the number of children and number of metadata, then the
children nodes, and then the metadata numbers.

The example from the site is this:

    
    
    2 3 0 3 10 11 12 1 1 0 1 99 2 1 1 2
    A----------------------------------
        B----------- C-----------
                         D-----
    

So above, A has two children, and three metadata. D has no children (see the 0
above it), and 1 metadata.

In part one, we need to find the sum of the metadata. In part two, we need to
find the value of the root node. Value is the sum of the metadata if the node
has no children. If the node has children, then the metadata are 1-based
indexes to the children of the node, and the value of the node is the sum of
the values of the children referenced. If a metadata value points to a non-
existent child, then the value is 0.

### Solution

This just screams recurrsion. To process a node:

  * Pop the first two values from the list, number of children and number of metadata.
  * For each child, pass the current list back into the function.
  * Now process the metadata

For part 1, I just need to track the total of the metadata, so I just return
that, and add it to a running total.

For part 2, I still just needed to get a value for the node based on the
metadata and the child values. It required a bit more structure. I’ll track
the child values in a defaultdict, which is perfect since I know I may be
referencing indexes outside of the defined range, and it will set those to 0
as I want. Then, once I have a defaultdict of child values, I can loop over
the meta indexes and add to a total, and finally, if there are no children,
just set that value to the metadata total.

    
    
      1 #!/usr/bin/env python3
      2
      3 import sys
      4 from collections import defaultdict
      5
      6
      7 def walk_tree(nums):
      8     num_child = nums.pop(0)
      9     num_meta = nums.pop(0)
     10     meta_total = 0
     11     value_total = 0
     12     child_values = defaultdict(int)
     13
     14     for i in range(num_child):
     15         meta, child_values[i] = walk_tree(nums)
     16         meta_total += meta
     17
     18     for i in range(num_meta):
     19         x = nums.pop(0)
     20         meta_total += x
     21         value_total += child_values[x-1]
     22
     23     if num_child == 0:
     24         value_total = meta_total
     25
     26     return meta_total, value_total
     27
     28
     29 with open(sys.argv[1], 'r') as f:
     30     nums = [int(i) for i in f.read().split(' ')]
     31
     32 solution1, solution2 = walk_tree(nums)
     33 print(f"Part 1: {solution1}")
     34 print(f"Part 2: {solution2}")
    
    
    
    $ time ./day8.py 08-puzzle_input.txt
    Part 1: 47112
    Part 2: 28237
    
    real    0m0.061s
    user    0m0.053s
    sys     0m0.008s
    

### Note

This is the kind of challenge that I suspect could be done in something like 5
lines of python, using some fancy mapping or reducing. I’m looking forward to
reading more creative solutions.

## Day 7

![](https://0xdfimages.gitlab.io/img/aoc2018-07.png)

### Intro

Today’s challenge was about getting an order of steps based on given
dependencies, and then to look at how to order that work given a number of
workers and time per task. Today took me way too long. There were multiple
times where I thought, “oh, it’s easy from here”, and then was completely
wrong. But that’s the fun of it. And it didn’t help that I got distracted in
the second part, where I had the right algorithm for a while but was trying to
submit the order and not the number steps. Always read carefully.

### Challenge

<https://adventofcode.com/2018/day/7>

We get a list of phrases, each that defines that a task relies on another
task. Tasks are single, uppercase letters..

The example data looks like:

    
    
    Step C must be finished before step A can begin.
    Step C must be finished before step F can begin.
    Step A must be finished before step B can begin.
    Step A must be finished before step D can begin.
    Step B must be finished before step E can begin.
    Step D must be finished before step E can begin.
    Step F must be finished before step E can begin.
    

In part one, we’re tasked to find the order the steps are performed, where the
task coming first alphabetically is done first if two are available.

In part two, we’re told each step takes 60 seconds plus the letter of the
alphabet (A=1, B=2, …, Y=25, Z=26) to complete. We also have 5 workers working
at the same time. We are to find how long will it take to complete the tasks.

### Solution

When I just had part 1, I solve this one way. But on seeing the instructions
for part two, I completely refactored that code. Because the solution to part
1 is just a one worker solution to part 2, where you don’t care about time.

My `solve` function takes an list of dependencies (steps), as well as the
number of workers and the base_time for a task (60 in the puzzle).

First, I create a defaultdict of sets called blocked_by. For each task, I’ll
have a set of the tasks that are outstanding that block it. Then I’ll get a
list of all the tasks, and from there, I’ll generate a list called
available_tasks as ones that are not currently blocked. Finally, I’ll
initialize time, my solution, and an array of workers.

For workers, I’ll use a namedtuple, just to make it more readable. Each worker
will have a task and a time_finished.

Then I loop, first checking each worker to see if they are done, and if so,
moving the result into the solution. Then over the available tasks and workers
to start new tasks. I’ll return whenever there’s no workers working and no
tasks available at the same time.

    
    
      1 #!/usr/bin/env python3
      2
      3 import re
      4 import sys
      5 from collections import defaultdict, namedtuple
      6 from itertools import chain
      7
      8
      9 worker = namedtuple('worker', 'task, time_finished')
     10
     11
     12 def solve(steps, num_workers, base_time):
     13
     14     # create map of steps
     15     blocked_by = defaultdict(set)
     16     [blocked_by[y].add(x) for x,y in steps]
     17     all_steps = set([x for y in steps for x in y]) # flatten steps
     18     available_tasks = [x for x in all_steps if x not in blocked_by]
     19     solution = ''
     20     t = 0
     21     busy_workers = []
     22
     23     while True:
     24
     25         # finish complete tasks
     26         remove_queue = []
     27         solution_queue = ''
     28         for w in busy_workers:
     29             if w.time_finished == t:
     30                 solution_queue += w.task
     31                 # remove blocker from tree
     32                 [blocked_by[task].discard(w.task) for task in blocked_by]
     33                 # update available tasks
     34                 available_tasks.extend([k for k,v in blocked_by.items() if not v])
     35                 # remove empty branches
     36                 blocked_by = {k: v for k,v in blocked_by.items() if v}
     37                 remove_queue.append(w)
     38
     39         for w in remove_queue: busy_workers.remove(w)
     40         solution += ''.join(sorted(solution_queue))
     41
     42         # assign new tasks
     43         for i in range(min(len(available_tasks), num_workers - len(busy_workers))):
     44             available_tasks.sort(reverse=True)
     45             current =  available_tasks.pop()
     46             busy_workers.append(worker(current, t + ord(current) - 0x40 + base_time))
     47
     48         if not busy_workers and not blocked_by:
     49             break
     50         t += 1
     51
     52     return (solution, t)
     53
     54
     55 with open(sys.argv[1], 'r') as f:
     56     steps = [re.findall(r' (\w) ', line) for line in f.readlines()]
     57
     58 solution1, _ = solve(steps, 1, 0)
     59 print(f"Part 1: {solution1}")
     60
     61 _, solution2 = solve(steps, int(sys.argv[2]), int(sys.argv[3]))
     62 print(f"Part 2: {solution2}")
    
    
    
    $ time ./day7.py 07-puzzle_input.txt 5 60
    Part 1: FHICMRTXYDBOAJNPWQGVZUEKLS
    Part 2: 946
    
    real    0m0.058s
    user    0m0.042s
    sys     0m0.017s
    

## Day 6

![](https://0xdfimages.gitlab.io/img/aoc2018-06.png)

### Intro

Today’s challenge was not too hard, but did push us out into two dimensional
space again. Definitely got to put my comprehensions to work, again.

### Challenge

<https://adventofcode.com/2018/day/6>

We get a string of coordinates, and we don’t know if they are safe spots of
dangerous spots.

The coordinate list looks like:

    
    
    1, 1
    1, 6
    8, 3
    3, 4
    5, 5
    8, 9
    

In part 1, we assume these coordinates make dangerous spots, and thus we want
to find the biggest area around one of them, ignoring the ones with infinite
area on the edges. We’ll use Manhatten distance, which is just the change in x
plus the change in y.

In part 2, we assume the coordinates mark safe spots, and thus we’re asked to
find the spots on the map that where the sum of the distance to every spot is
under some threshold.

### Solution

To track space, I’ll use a dictionary where the key is x,y as a tuple. I
created a function to find the closest given coordinate for each point on the
map. I’ll start with the square region bounded by the min x and y and the max
x and y, and I’ll find the closest coordinate to each point in that grid.
Then, I’ll find the set of coordinates that are closest to an edge point on my
square. Those will be infinite regions. Then I can count the number of points
closest to each coordinate, and take the largest that isn’t in the infinite
list.

For part two, I’ll loop over a region again, this time bounded by the min x
and y and max x and y, but plus the threshold distance divided by the number
of points. If a space is outside of the min/max /x/y box, then by definition
the distance to each point is greater than the distance to the box. So if the
distance to the box > (threshold / num_points), and then we sum distance over
all the points, then distance is greater than the threshold, and we can ignore
those points. On that loop, I’ll calculate the total distance to all the
points, and save that. I can get the number of points under the threshold by
looking at the length of the array of sums of distance, throwing out the ones
that are too long.

    
    
      1 #!/usr/bin/python3
      2
      3 import sys
      4
      5 from collections import Counter
      6
      7
      8 def distance(x, y):
      9     return abs(x[0] - y[0]) + abs(x[1] - y[1])
     10
     11
     12 def find_closest(coord, points):
     13     closest, second_closest = sorted([(distance(p, coord), p) for p in points])[:2]
     14     if closest[0] == second_closest[0]:
     15         return None
     16     else:
     17         return closest[1]
     18
     19
     20 def find_total(coord, points):
     21     return sum(distance(p, coord) for p in points)
     22
     23
     24 with open(sys.argv[1], 'r') as f:
     25     points = list(map(lambda s: tuple(map(int, s.split(','))), f.readlines()))
     26
     27 min_x = min(x[0] for x in points)
     28 max_x = max(x[0] for x in points)
     29 min_y = min(y[1] for y in points)
     30 max_y = max(y[1] for y in points)
     31
     32 plot = {(x,y): find_closest((x,y), points) for x in range(min_x, max_x+1) for y in range(min_y, max_y+1)}
     33
     34 infinates = set([v for k,v in plot.items() if (k[0] in (min_x, max_x) or k[1] in (min_y, max_y))])
     35
     36 print("Part 1: {}".format(Counter([v for v in plot.values() if v not in infinates]).most_common(1)[0][1]))
     37
     38 dist = int(sys.argv[2])
     39 survey = (dist // len(points)) + 1
     40 plot2 = {(x,y): find_total((x,y), points) for x in range(min_x - survey, max_x + survey) for y in range(min_y - survey, max_y + survey)}
     41 print("Part 2: {}".format(len([v for v in plot2.values() if v < dist])))
    
    
    
    $ time python3 ./day6.py 06-puzzle_input.txt 10000
    Part 1: 3358
    Part 2: 45909
    
    real    0m6.849s
    user    0m6.764s
    sys     0m0.076s
    

## Day 5

![](https://0xdfimages.gitlab.io/img/aoc2018-05.png)

### Intro

I actually found today’s challenge easier than the last couple. I spent the
majority of my time trying to come up with a slick regex to handle the
reduction necessary, but in the end, gave up in favor of a loop a replace.

### Challenge

<https://adventofcode.com/2018/day/5>

The input this time is a long string of letters, upper and lowercase, that
represents a polymer. When the polymer reacts, any instance where an uppercase
letter and the same letter in lowercase are next to each other is removed
entirely. So

    
    
    dabAcCaCBAcCcaDA  - remove cC
    dabAaCBAcCcaDA    - remove Aa
    dabCBAcCcaDA      - remove cC (or Cc)
    dabCBAcaDA
    

For part 1, I’m asked to return the length of the polymer once it reacts. For
part 2, I’m asked to try to find the shortest polymer I can by first removing
one letter pair before the reaction.

### Solution

I really wanted to find a regex that would detect the pattern of the same
letter in upper and lower case. I couldn’t do it (if you can, please comment).

So I opted to write a react function that first gets the letters in the
polymer (using set and lower to get the smallest possible list), and then
loops over that list, replacing and instances of upper/lower or lower/upper
with ‘’. After doing this for all the characters, it checks if the string
changed at all. If yes, it continues. If it doesn’t change, it returns.

Then it’s simply a matter of first reacting the input, and then looping over
the letters in the input, and for each removing them from the input, reacting
it, and getting the length.

    
    
       1 #!/usr/bin/env python3
      2
      3 import sys
      4
      5
      6 def react(polymer):
      7     while True:
      8         orig = polymer
      9         for c in set(polymer.lower()):
     10             polymer = polymer.replace(c.upper() + c.lower(), '').replace(c.lower() + c.upper(), '')
     11         if orig == polymer:
     12             return polymer
     13
     14 with open(sys.argv[1], 'r') as f:
     15     polymer = f.read().rstrip()
     16
     17 polymer_len = len(react(polymer))
     18 print(f"Part 1: {polymer_len}")
     19
     20 shortest = min([len(react(polymer.replace(c.upper(), '').replace(c.lower(), ''))) for c in set(polymer.lower())])
     21
     22 print(f"Part 2: {shortest}")
    
    
    
    $ time ./day5.py 05-puzzle_input.txt
    Part 1: 9154
    Part 2: 4556
    
    real    0m7.308s
    user    0m7.291s
    sys     0m0.016s
    

## Day 4

![](https://0xdfimages.gitlab.io/img/aoc2018-04.png)

### Intro

Today the challenge is really centered around parsing a series of logs to
create data in a structure that can be sorted multiple different ways. I’ll
use a nested defaultdict to solve this. It’ll probably go without saying that
from now on, I suspect my solutions are not the most elegant!

### Challenge

<https://adventofcode.com/2018/day/4>

Again I’m given a log file. This time the information I need for any given
entry spans multiple lines, as a shift is expressed as:

    
    
    [1518-11-01 00:00] Guard #10 begins shift
    [1518-11-01 00:05] falls asleep
    [1518-11-01 00:25] wakes up
    [1518-11-01 00:30] falls asleep
    [1518-11-01 00:55] wakes up
    

Also, the lines are not in time order. So I’ll need to sort the data, then
track the various minutes that each guard is asleep to find the right guard to
target by two different strategies.

First, this challenge asks me to find the guard who sleeps the most total
minutes, and then find the minute that that guard is most often asleep, and
then the minute that guard is most frequently asleep, and multiple the id and
minute together.

In the second part, I’m asked to find the guard who is most frequently asleep
on the same minute, and then multiply the guard id and minute together.

### Solution

The key to this challenge is structuring your data in such a way that you can
find different maximums later. I’ll make use of `defaultdict` again, this time
actually nesting two defaultdicts. The top level defaultdict will hold a
dictionary of default dicts, by guard id. The internal defaultdict will be
ints, which initialize to 0, for each minute in the hour (since all the shifts
take place at the 1200-0100 hour).

Sorting the lines isn’t much of a challenge, as the log data strings are
already in order of descending importance (year, month, day, hour, minute).

I’ll loop over the lines, and assume there’s not errors in the logs, that they
will always go “guard starting”, followed by some number of sleeps and wakes.

Once I have my nested defaultdicts, getting the answers is just a matter of
sorting them by different keys, and grabbing the first one.

    
    
      1 #!/usr/bin/env python3
      2
      3 import re
      4 import sys
      5
      6 from collections import defaultdict, Counter
      7
      8 with open(sys.argv[1], 'r') as f:
      9     records = [l.rstrip() for l in f.readlines()]
     10
     11 guard_sleep_time = defaultdict(int)
     12 clock = defaultdict(lambda: defaultdict(int))
     13
     14 for r in sorted(records):
     15     minute, action = re.findall(r'\[\d{4}-\d{2}-\d{2} \d{2}:(\d{2})\] (.+)', r)[0]
     16     if "Guard" in action:
     17         guard = action.split(' ')[1][1:]
     18     if "falls asleep" == action:
     19         sleep_time = int(minute)
     20     if "wakes up" == action:
     21         for m in range(sleep_time, int(minute)):
     22             clock[guard][m] += 1
     23
     24 most_sleep_guard = sorted(clock.items(), key=lambda x: sum(x[1].values()), reverse=True)[0][0]
     25 most_sleep_minute = sorted(clock[most_sleep_guard].items(), key=lambda x: x[1], reverse=True)[0][0]
     26 print("Part 1: {}".format(int(most_sleep_guard) * most_sleep_minute))
     27
     28 most_freq = sorted(clock.items(), key=lambda x: max(x[1].values()), reverse=True)[0]
     29 most_freq_guard = int(most_freq[0])
     30 most_freq_minute = sorted(most_freq[1].items(), key=lambda x: x[1], reverse=True)[0][0]
     31 print("Part 2: {}".format(most_freq_guard * most_freq_minute))
    
    
    
    $ time ./day4.py 04-puzzle_input.txt
    Part 1: 72925
    Part 2: 49137
    
    real    0m0.045s
    user    0m0.034s
    sys     0m0.011s
    

## Day 3

![](https://0xdfimages.gitlab.io/img/aoc2018-03.png)

### Intro

Today they have us already having to think in 2 dimensional space, which is
something that already starts to get me into a space of “I can solve this, but
I’m sure I don’t solve it the best way”. That said, here’s my solutions.

### Challenge

<https://adventofcode.com/2018/day/3>

The challenge is to take a list of strings which define the size and location
of a square on a two dimensional grid, and then I’ll analyze overlaps. The
input lines like like `#123 @ 3,2: 5x4`, where this example has an Id of 123,
starts three squares offset from the left, two squares offset from the top,
has a width of five and a height of four.

First, I’ll need to count how many squares contain marks from more than one
square. The next challenge is to find the one square that doesn’t overlap with
any others.

### Solution

This seems like a good case to use a `defaultdict` from the `collections`
module. It allows me to create a dictionary with a default value so I don’t
have to worry about initializing every entry. When I first solve the first
part, I used an `int` for the `defaultdict`, and just counted. But in the
second part I needed to know which Id was in each area, so I changed it to a
list and went by the length of the list. After building the grid, I use a list
comprehension to count items with a length of their list greater than 1.

For the second part, I’ll loop over each Id, and again use a similar list
comprehension to get the length of the list of Ids for all the squares that
have that Id in their list. If all of those lengths are 1, then there’s no
overlap for that Id, so I found the solution.

    
    
    #!/usr/bin/env python3
    
    import sys
    
    from collections import defaultdict
    
    with open(sys.argv[1], 'r') as f:
        lines = [l.rstrip() for l in f.readlines()]
    
    grid = defaultdict(list)
    
    for line in lines:
        Id, _, margin, dim = line.split(' ')
        Id = int(Id.lstrip('#'))
        left, top = [int(x) for x in margin.rstrip(':').split(',')]
        width, height = [int(x) for x in dim.split('x')]
        for i in range(left, left+width):
            for j in range(top, top+height):
                grid[f"{i}-{j}"].append(Id)
    
    print("Part 1: {}".format(len([x for x in grid.items() if len(x[1]) > 1])))
    
    
    for i in range(1, Id+1):
        if all(len(x[1]) == 1 for x in grid.items() if i in x[1]):
            print(f"Part 2: {i}")
            break
    
    
    
    $ time ./day3.py 03-puzzle_input.txt
    Part 1: 104241
    Part 2: 806
    
    real    0m3.865s
    user    0m3.833s
    sys     0m0.032s
    

This is one where I suspect there’s a more efficient way to solve. I’ll be
interested to see how others do it.

## Day 2

![](https://0xdfimages.gitlab.io/img/aoc2018-02.png)

### Intro

Another challenge that involves sorting through text data, looking for a
specific criteria. And another good chance to use iterools.

### Challenge

<https://adventofcode.com/2018/day/2>

The challenge is to take a list of strings, and look for the differeneces in
those strings, first by looking at character counts, and then by small changes
between strings.

Given a list of IDs (strings of random letters), count the number of strings
that have exactly two of the same character, and then the number of strings
that have exactly three of the same character. A string can count towards
both, but doesn’t contribute more than once to the count.

In part 2, I’m looking for two IDs that are different by only one character
(including order).

### Solution

For the first part, I’ll simply loop over all the IDs, and keep count of each
id that has two of the same letter, and three of the same letter. To do this,
I’ll create an array over each character in the string, where the value is the
`.count(letter)`. Then I can check if 2 and/or 3 are in the array, and
increment a counter for each.

For the second part, I’ll use the `itertools.combinations` function, to get
each pairing of IDs. Then for each id in the pair, I’ll convert the letters to
ints. Then I can use `zip` to match each letter with it’s pair in the other
id, and then subtract them, and compare to 0. This will leave me with an array
of `True` and `False`. If I sum that array, I’ll get the number of true, so I
can look for one. Finally, to get the answer, I’ll get all the letters where
the two are equal.

    
    
    #!/usr/bin/env python3
    
    import itertools
    import sys
    
    with open(sys.argv[1], 'r') as f:
        ids = [x.strip() for x in f.readlines()]
    
    twos = 0
    threes = 0
    
    for i in ids:
        res = [i.count(x) for x in set(i)]
        if 2 in res: twos += 1
        if 3 in res: threes += 1
    
    print(f"Part 1: {twos * threes}")
    
    for comb in itertools.combinations(ids, 2):
        id1, id2 = [[ord(c) for c in x] for x in comb]
        if sum([a - b != 0 for a,b in zip(id1, id2)]) == 1:
            print("Part 2: {}".format(''.join([chr(a) for a,b in zip(id1, id2) if a == b])))
            break
    
    
    
    $ time ./day2.py 02-puzzle_input.txt
    Part 1: 7163
    Part 2: ighfbyijnoumxjlxevacpwqtr
    
    real    0m0.056s
    user    0m0.056s
    sys     0m0.000s
    

## Day 1

![](https://0xdfimages.gitlab.io/img/aoc2018-01.png)

### Challenge

<https://adventofcode.com/2018/day/1>

The challenge is to take a list of ints (frequencies) and treat them as deltas
from the previous sum. So I start at 0, then add the first number, the second,
etc.

First, given a long list of input, find the last output. Next, find the first
time the resulting sum repeats. If you reach the end of the list of inputs,
wrap back around to the start and keep going.

### Solution

This was a good chance to use two functions from `itertools`: `cycle` and
`accumulate`. `cycle` takes a list, and produces an infinite iterator that
will go to the end of the list, and then start back at the beginning. So
`cycle([1,2,3]` will produce 1,2,3,1,2,3,1,2,3,1,…

`accumulate` returns an iterator that will return the sum of the first number,
then the first two numbers, then the first three numbers, etc. So
`accumulate([1,2,3]) return 1,3,6.

Together, I can easily loop over the number I’m looking for, looking for a
repeat, tracking seen frequencies in a set. I’ll start that set with the 0
value, since the frequency starts at 0.

    
    
    #!/usr/bin/env python3
    
    import itertools
    import sys
    
    with open(sys.argv[1], 'r') as f:
        nums = [int(l) for l in f.readlines()]
    
        print(f"Part 1: {sum(nums)}")
    
        freqs ={0}
    
        for f in itertools.accumulate(itertools.cycle(nums)):
            if f in freqs:
                print(f"Part 2: {f}")
                break
            freqs.add(f)
    
    
    
    $ time ./day1.py 01-puzzle_input.txt
    Part 1: 516
    Part 2: 71892
    
    real    0m0.049s
    user    0m0.038s
    sys     0m0.011s
    

[](/adventofcode2018/)

