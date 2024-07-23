# Advent of Code 2020: Day 24

[ctf](/tags#ctf ) [advent-of-code](/tags#advent-of-code )
[python](/tags#python )  
  
Dec 24, 2020

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
  * [Day17](/adventofcode2020/17)
  * [Day18](/adventofcode2020/18)
  * [Day19](/adventofcode2020/19)
  * [Day20](/adventofcode2020/20)
  * [Day21](/adventofcode2020/21)
  * [Day22](/adventofcode2020/22)
  * [Day23](/adventofcode2020/23)
  * Day24
  * [Day25](/adventofcode2020/25)

![](https://0xdfimages.gitlab.io/img/aoc2020-24-cover.png)

The twist on day 24 is that it takes place on a grid of hexagons, so each tile
has six neighbors, and a normal x,y or r,c coordinate system will be very
difficult to use. I’ll use an x, y, z coordinate system to flip tiles based on
some input and then watch it evolve based on it’s neighbors.

## Challenge

The puzzle can be found [here](https://adventofcode.com/2020/day/24). I’m
given a list of steps to take in one of six directions: s, se, sw, w, nw, or
ne. The input has no delimiters, so it’s one long string of input. One path
might look like:

    
    
    sesenwnenenewseeswwswswwnenewsewsw
    

In part one, I’ll walk each line of instruction and flip the tile at the end,
where all tiles start as white, flip to black, and go back to white if flipped
again.

In part two, the tiles change each day based on their neighbors, and they want
to know how many tiles will be black after 100 days. If a tile was black with
zero or more than two black neighbors, it flips to white. If a tile was white
with two black tile neighbors, it flipped to black.

## Solution

### Part 1

To track spaces in a hex grid, I’ll use an x,y,z coordinate system as
described [here](https://math.stackexchange.com/questions/2254655/hexagon-
grid-coordinate-system). I’m going to change the instructions, replacing `se`
with `s`, `sw` with `S`, `ne` with `n`, and `nw` with `N`, so that each
instruction is one characters. Then I can make a dictionary to map from a
character to the offsets in the coordinate system:

    
    
    dirs = {
        "e": [1, -1, 0],
        "s": [0, -1, 1],  # s == se
        "S": [-1, 0, 1],  # S == sw
        "w": [-1, 1, 0],
        "N": [0, 1, -1],  # N == nw
        "n": [1, 0, -1],  # n == ne
    }
    
    
    with open(sys.argv[1], "r") as f:
        paths = [
            l.strip()
            .replace("sw", "S")
            .replace("se", "s")
            .replace("nw", "N")
            .replace("ne", "n")
            for l in f.readlines()
        ]
    

Now I need to loop over each path, find the tile at the end, and flip it. I’ll
track black tiles in a set, where flipping a tile from white to black involves
adding it to the set, and flipping from black to white just removing it.

    
    
    black_tiles = set()
    
    for path in paths:
        coord = (0, 0, 0)
        for p in path:
            coord = tuple([a + b for a, b in zip(coord, dirs[p])])
        if coord in black_tiles:
            black_tiles.remove(coord)
        else:
            black_tiles.add(coord)
    
    print(f"Part 1: {len(black_tiles)}")
    

For each path, I start at 0,0,0, and then for each instruction, fetch the
direction. `zip(coord, dirs[p])` will pair the current x with the change in x,
the current y with the change in y, and the current z with the change in z. So
in this list comprehension, the `a` is the current position on each access,
and the `b` is the change. I’ll add them together, and then form a new tuple
out of the result. Once the full path is walked, I’ll flip the tile.

At the end of the loop, the answer is the size of the set.

### Part 2

My immediate intuition was to get the min and max of each coordinate each day,
and then nest three for loops to walk that entire space checking for flips.
The problem is that this space becomes large quickly, and becomes too much to
do. Instead, I’ll start each day by creating a list of all the currently black
titles, as well as all of the neighbors of those tiles. If a tile is white and
has no black neighbors, it can’t change to black, so I can ignore it.

Now I just walk over these tiles, checking their neighbors, and recording the
new color for the next day.

    
    
    for _ in range(100):
        new_tiles = set()
        to_check = set()
        for coord in black_tiles:
            to_check.add(coord)
            for diff in dirs.values():
                to_check.add(tuple([a + b for a, b in zip(coord, diff)]))
    
        for coord in to_check:
            num_neigh = sum(
                [
                    tuple(a + b for a, b in zip(coord, d)) in black_tiles
                    for d in dirs.values()
                ]
            )
            if (coord in black_tiles and 0 < num_neigh <= 2) or (
                coord not in black_tiles and num_neigh == 2
            ):
                new_tiles.add(coord)
        black_tiles = new_tiles
    
    print(f"Part 2: {len(black_tiles)}")
    

### Final Code

Part one is quick, but part two runs for eight seconds:

    
    
    $  time python3 day24.py 24-puz 
    Part 1: 388
    Part 2: 4002
    
    real    0m8.855s
    user    0m8.805s
    sys     0m0.025s
    
    
    
    #!/usr/bin/env python3
    
    import sys
    
    
    dirs = {
        "e": [1, -1, 0],
        "s": [0, -1, 1],  # s == se
        "S": [-1, 0, 1],  # S == sw
        "w": [-1, 1, 0],
        "N": [0, 1, -1],  # N == nw
        "n": [1, 0, -1],  # n == ne
    }
    
    
    with open(sys.argv[1], "r") as f:
        paths = [
            l.strip()
            .replace("sw", "S")
            .replace("se", "s")
            .replace("nw", "N")
            .replace("ne", "n")
            for l in f.readlines()
        ]
    
    black_tiles = set()
    
    for path in paths:
        coord = (0, 0, 0)
        for p in path:
            coord = tuple([x + y for x, y in zip(coord, dirs[p])])
        if coord in black_tiles:
            black_tiles.remove(coord)
        else:
            black_tiles.add(coord)
    
    print(f"Part 1: {len(black_tiles)}")
    
    for _ in range(100):
        new_tiles = set()
        to_check = set()
        for coord in black_tiles:
            to_check.add(coord)
            for diff in dirs.values():
                to_check.add(tuple([a + b for a, b in zip(coord, diff)]))
    
        for coord in to_check:
            num_neigh = sum(
                [
                    tuple(a + b for a, b in zip(coord, d)) in black_tiles
                    for d in dirs.values()
                ]
            )
            if (coord in black_tiles and 0 < num_neigh <= 2) or (
                coord not in black_tiles and num_neigh == 2
            ):
                new_tiles.add(coord)
        black_tiles = new_tiles
    
    print(f"Part 2: {len(black_tiles)}")
    

### Look At Size

To show why my original solution wasn’t a good idea, I’ll run the solution
with `python -i` to get a shell at the end. My puzzle input has 4002 black
tiles after 100 days. If I want to do a 101st day, I would build a list of
those 4002 and their neighbors, which would be at most `7 * 4,002 = 28,014`.
Because many of those tiles are neighbors already, it ends up being 10,504:

    
    
    >>> to_check = set()
    >>> for coord in black_tiles:
    ...     to_check.add(coord)
    ...     for diff in dirs.values():        
    ...         to_check.add(tuple([a + b for a, b in zip(coord, diff)]))
    ... 
    >>> len(to_check)
    10504
    

On the other hand, had I wanted to loop over the entire space covered in that
floor, I’d need to find the min/max of each coordinate:

    
    
    >>> for i in range(3):
    ...    min(black_tiles, key=lambda x: x[i])[i]
    ...    max(black_tiles, key=lambda x: x[i])[i]
    ... 
    -67
    65
    -63
    67
    -65
    65
    

To find the size of that space, I’ll find the difference of that max and min,
and multiple them all together:

    
    
    >>> for i in range(3):
    ...    max(black_tiles, key=lambda x: x[i])[i] - min(black_tiles, key=lambda x: x[i])[i]
    ... 
    132
    130
    130
    >>> 132*130*130
    2230800
    

So instead of ten thousand points to check and then count neighbors on, I’d
have to check 2.2 million, which explains why it’s so much slower.

[« Day23](/adventofcode2020/23)[Day25 »](/adventofcode2020/25)

[](/adventofcode2020/24)

