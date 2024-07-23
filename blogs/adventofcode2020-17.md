# Advent of Code 2020: Day 17

[ctf](/tags#ctf ) [advent-of-code](/tags#advent-of-code )
[python](/tags#python ) [conway](/tags#conway ) [game-of-life](/tags#game-of-
life )  
  
Dec 17, 2020

  * [Day1](/adventofcode2020/1)
  * [Day2](/adventofcode2020/2)
  * [Day3](/adventofcode2020/3)
  * [Day4](/adventofcode2020/4)
  * [Day5](/adventofcode2020/5)
  * [Day6](/adventofcode2020/6)
  * [Day7](/adventofcode2020/7)
  * [Day8](/adventofcode2020/8)
  * [Day9](/adventofcode2020/9)
  * [Day10](/adventofcode2020/10)
  * [Day11](/adventofcode2020/11)
  * [Day12](/adventofcode2020/12)
  * [Day13](/adventofcode2020/13)
  * [Day14](/adventofcode2020/14)
  * [Day15](/adventofcode2020/15)
  * [Day16](/adventofcode2020/16)
  * Day17
  * [Day18](/adventofcode2020/18)
  * [Day19](/adventofcode2020/19)
  * [Day20](/adventofcode2020/20)
  * [Day21](/adventofcode2020/21)
  * [Day22](/adventofcode2020/22)
  * [Day23](/adventofcode2020/23)
  * [Day24](/adventofcode2020/24)
  * [Day25](/adventofcode2020/25)

![](https://0xdfimages.gitlab.io/img/aoc2020-17-cover.png)

Day 17 was a modified version of Conway’s Game of Life, played across three
and four dimensions, where a cells state in the next time step is determined
by the its current state and the state of its neighbors.

## Challenge

The puzzle can be found [here](https://adventofcode.com/2020/day/17). The
puzzle input is a two dimensional grid where a space is either inactive (`.`)
or active (`#`). There are rules for how cells propagate in time based on the
neighboring cells. If the space is active and has two or three neighbors
active, it remains active. If a cell is inactive and has three neighbors
active, it becomes active. Otherwise, the cell becomes inactive. This is a
variation on [Conway’s Game of
Life](https://en.wikipedia.org/wiki/Conway%27s_Game_of_Life).

In each part, I’m asked to step out six steps. In part one, I’ll handle the
space as three dimensional, and in part two, four dimensional.

## Solution

### Part 1

I decided to keep my list in a set of coordinates rather than nesting arrays,
which I was happy with when I say part two. First step is to read in the data
and create the initial set:

    
    
    with open(sys.argv[1], 'r') as f:
        raw_in = f.readlines()
    
    cells = set()
    
    for y,line in enumerate(raw_in):
        for x,cell in enumerate(line):
            if cell == '#':
                cells.add((x,y,0))
    

Now I’ll create a `step` function, but first two helper functions.
`get_bounds` returns the outside edges of a set in each dimension:

    
    
    def get_bounds(cells):
        res = []
        for i in range(3):
            res.append(min(cells, key=lambda x: x[i])[i] - 1)
            res.append(max(cells, key=lambda x: x[i])[i] + 2)
        return res
    

`get_n_count` returns the number of neighbors that are active given a point
and a set:

    
    
    def get_n_count(x, y, z, cells):
        res = 0
        for dx in range(-1,2):
            for dy in range(-1,2):
                for dz in range(-1,2):
                    if not (dx == dy == dz == 0) and  ((x+dx, y+dy, z+dz) in cells):
                        res += 1
        return res
    

With those two, the `step` function is:

    
    
    def step(cells):
        bounds = get_bounds(cells)
        next_cells = set()
        for x in range(bounds[0], bounds[1]):
            for y in range(bounds[2], bounds[3]):
                for z in range(bounds[4], bounds[5]):
                    ns = get_n_count(x,y,z, cells)
                    if (x,y,z) in cells and (ns == 2 or ns == 3):
                        next_cells.add((x,y,z))
                    elif (x,y,z) not in cells and ns == 3:
                        next_cells.add((x,y,z))
        return next_cells
    

Now I can step through six times and return the length:

    
    
    p1 = cells.copy()
    for _ in range(6):
        p1 = step(p1)
    
    print(f'Part 1: {len(p1)}')
    

This is not instant, but runs in 0.2 seconds, so fast.

### Part 2

For part two, the fastest thing would be to completely copy the previous code
and just edit it to just solve part two. I’ll actually update it so that it
can still solve both. To do this, first I’ll try to solve part one but where
everything is working in four dimension. To do that, for part one, I’ll just
let every point have a w = 0.

Now reading in the data adds a forth coordinate to each point:

    
    
    for y,line in enumerate(raw_in):
        for x,cell in enumerate(line):
            if cell == '#':
                cells.add((x,y) + (0,) * 2)
    

`get_bounds` now collects four pairs:

    
    
    def get_bounds(cells):
        res = []
        for i in range(4):
            res.append(min(cells, key=lambda x: x[i])[i] - 1)
            res.append(max(cells, key=lambda x: x[i])[i] + 2)
        return res
    

I completely refactored `get_n_count` to use a list comprehension:

    
    
    def get_n_count(point, cells):
        dim = len(point)
        diffs = product([-1, 0, 1], repeat=dim)
        return sum(
            [
                tuple([x1 + x2 for x1, x2 in zip(d, point)]) in cells
                for d in diffs
                if d != tuple([0] * dim)
            ]
        )
    

Now for `step`, I will have it loop over the min/max w bounds like the other
coordinates in 4D, but for 3D I’ll just always have w be 0:

    
    
    def step(cells, d=3):
        bounds = get_bounds(cells)
        next_cells = set()
        w_range = [0] if d == 3 else range(bounds[6], bounds[7])
        for x in range(bounds[0], bounds[1]):
            for y in range(bounds[2], bounds[3]):
                for z in range(bounds[4], bounds[5]):
                    for w in w_range:
                        ns = get_n_count((x,y,z,w), cells)
                        if (x,y,z,w) in cells and (ns == 2 or ns == 3):
                            next_cells.add((x,y,z,w))
                        elif (x,y,z,w) not in cells and ns == 3:
                            next_cells.add((x,y,z,w))
        return next_cells
    

With that in place, I can check that my original loop over part one still
returns the correct answer, and then add the solution to part two:

    
    
    p1 = cells.copy()
    for _ in range(6):
        print(len(p1))
        p1 = step(p1)
    
    print(f'Part 1: {len(p1)}')
    
    p2 = cells.copy()
    for _ in range(6):
        p2 = step(p2, d=4)
    
    print(f'Part 2: {len(p2)}')
    

### Final Code

The code is slower now, as part one still takes less than a second, but part
two takes 17 seconds:

    
    
    $ time python3 day17.py 17-puz
    Part 1: 230
    Part 2: 1600
    
    real    0m17.353s
    user    0m17.343s
    sys     0m0.004s
    
    
    
    #!/usr/bin/env python3
    
    import sys
    from itertools import product
    
    
    def get_bounds(cells):
        res = []
        for i in range(4):
            res.append(min(cells, key=lambda x: x[i])[i] - 1)
            res.append(max(cells, key=lambda x: x[i])[i] + 2)
        return res
    
    
    def step(cells, d=3):
        bounds = get_bounds(cells)
        next_cells = set()
        w_range = [0] if d == 3 else range(bounds[6], bounds[7])
        for x in range(bounds[0], bounds[1]):
            for y in range(bounds[2], bounds[3]):
                for z in range(bounds[4], bounds[5]):
                    for w in w_range:
                        ns = get_n_count((x, y, z, w), cells)
                        if (x, y, z, w) in cells and (ns == 2 or ns == 3):
                            next_cells.add((x, y, z, w))
                        elif (x, y, z, w) not in cells and ns == 3:
                            next_cells.add((x, y, z, w))
        return next_cells
    
    
    def get_n_count(point, cells):
        dim = len(point)
        diffs = product([-1, 0, 1], repeat=dim)
        return sum(
            [
                tuple([x1 + x2 for x1, x2 in zip(d, point)]) in cells
                for d in diffs
                if d != tuple([0] * dim)
            ]
        )
    
    
    with open(sys.argv[1], "r") as f:
        raw_in = f.readlines()
    
    cells = set()
    
    for y, line in enumerate(raw_in):
        for x, cell in enumerate(line):
            if cell == "#":
                cells.add((x, y) + (0,) * 2)
    
    p1 = cells.copy()
    for _ in range(6):
        p1 = step(p1)
    
    print(f"Part 1: {len(p1)}")
    
    p2 = cells.copy()
    for _ in range(6):
        p2 = step(p2, d=4)
    
    print(f"Part 2: {len(p2)}")
    

[« Day16](/adventofcode2020/16)[Day18 »](/adventofcode2020/18)

[](/adventofcode2020/17)

