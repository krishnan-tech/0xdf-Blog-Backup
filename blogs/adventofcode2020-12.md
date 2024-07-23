# Advent of Code 2020: Day 12

[ctf](/tags#ctf ) [advent-of-code](/tags#advent-of-code )
[python](/tags#python )  
  
Dec 12, 2020

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
  * Day12
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
  * [Day24](/adventofcode2020/24)
  * [Day25](/adventofcode2020/25)

![](https://0xdfimages.gitlab.io/img/aoc2020-12-cover.png)

Day 12 is about moving a ship across a coordinate plane using directions and a
way point that moves and rotates around the ship. There’s a bit of geometry,
and I made a really dumb mistake that took me a long time to figure out.

## Challenge

The puzzle can be found [here](https://adventofcode.com/2020/day/12). The
puzzle input will look like:

    
    
    F10
    N3
    F7
    R90
    F11
    

Each line has one of seven actions: move (N)orth, (S)outh, (E)ast, (W)est or
(F)orward, or turn (L)eft or (Right) in degrees, and then an integer number of
spaces to move or degrees to turn.

For part one, the ship starts facing east (90 degrees), and moving does not
change the direction of the ship. I need to find the manhattan distance
between the ship’s starting and ending positions.

In part two, the directional move commands are actually for a wayfinding
beacon that starts at 1 north and 10 east. The directional commands move the
beacon, and the turn commands rotate the beacon around the ship. Only the
forward command moves the ship.

## Solution

### Part 1

I’m sure there are prettier ways to do it, but I just loop over the
instructions, moving the ship or changing the direction each time. A quick
glance shows that all the turn instructions are in increments of 90 degrees,
but the math isn’t too complicated to handle any values

    
    
    #!/usr/bin/env python3
    
    import math
    import sys
    
    
    with open(sys.argv[1], "r") as f:
        insts = f.readlines()
    
    
    direction = 90
    x, y = 0, 0
    
    for i in insts:
        d, p = i[0], int(i[1:])
        if d == "N":
            y += p
        elif d == "S":
            y -= p
        elif d == "E":
            x += p
        elif d == "W":
            x -= p
        elif d == "L":
            direction = (direction - p) % 360
        elif d == "R":
            direction = (direction + p) % 360
        elif d == "F":
            y += round(math.cos(math.radians(direction)) * p)
            x += round(math.sin(math.radians(direction)) * p)
    
    print(f"Part 1: {abs(x)+abs(y)}")
    

This gets the correct result.

### Part 2

I think there’s a way to conceptualize part two such that I can turn part one
into a solve function and get either back. But for sake of speed and clarity,
I just copied all of part one and started changing bits. I’ll add a position
for the waypoint, and handle rotations using [geometric
calculations](https://en.wikipedia.org/wiki/Rotation_\(mathematics\)#Two_dimensions)
with `sin` and `cos`. To turn right, I’ll just set the angle to 360 minus the
angle and then turn left that amount.

    
    
    sx, sy = 0, 0
    wx, wy = 10, 1
    
    for i in insts:
        d, p = i[0], int(i[1:])
        if d == "N":
            wy += p
        elif d == "S":
            wy -= p
        elif d == "E":
            wx += p
        elif d == "W":
            wx -= p
        elif d == "L":
            wx_orig = wx
            wx = round((math.cos(math.radians(p)) * wx) - (math.sin(math.radians(p)) * wy))
            wy = round(
                (math.sin(math.radians(p)) * wx_orig) + (math.cos(math.radians(p)) * wy)
            )
        elif d == "R":
            p = 360 - p
            wx_orig = wx
            wx = round((math.cos(math.radians(p)) * wx) - (math.sin(math.radians(p)) * wy))
            wy = round(
                (math.sin(math.radians(p)) * wx_orig) + (math.cos(math.radians(p)) * wy)
            )
        elif d == "F":
            sy += wy * p
            sx += wx * p
    
    print(f"Part 2: {abs(sx) + abs(sy)}")
    

What got me stuck for a long while was that I was forgetting to keep the
original `wx` so when it changed in the first calculation, the calculation of
`wy` was wrong. I added a line to print the status at the end of each loop:
`print(f'{i.strip():5s} {sx} {sy} {wx} {wy}')` and watched how it was
breaking, and eventually figured that out.

### Final Code

Script runs instantly:

    
    
    $ time python3 day12.py 12-puzzle.txt 
    Part 1: 759
    Part 2: 45763
    
    real    0m0.021s
    user    0m0.014s
    sys     0m0.007s
    
    
    
    #!/usr/bin/env python3
    
    import math
    import sys
    
    
    with open(sys.argv[1], "r") as f:
        insts = f.readlines()
    
    
    direction = 90
    x, y = 0, 0
    
    for i in insts:
        d, p = i[0], int(i[1:])
        if d == "N":
            y += p
        elif d == "S":
            y -= p
        elif d == "E":
            x += p
        elif d == "W":
            x -= p
        elif d == "L":
            direction = (direction - p) % 360
        elif d == "R":
            direction = (direction + p) % 360
        elif d == "F":
            y += round(math.cos(math.radians(direction)) * p)
            x += round(math.sin(math.radians(direction)) * p)
    
    print(f"Part 1: {abs(x)+abs(y)}")
    
    
    sx, sy = 0, 0
    wx, wy = 10, 1
    
    for i in insts:
        d, p = i[0], int(i[1:])
        if d == "N":
            wy += p
        elif d == "S":
            wy -= p
        elif d == "E":
            wx += p
        elif d == "W":
            wx -= p
        elif d == "L":
            wx_orig = wx
            wx = round((math.cos(math.radians(p)) * wx) - (math.sin(math.radians(p)) * wy))
            wy = round(
                (math.sin(math.radians(p)) * wx_orig) + (math.cos(math.radians(p)) * wy)
            )
        elif d == "R":
            p = 360 - p
            wx_orig = wx
            wx = round((math.cos(math.radians(p)) * wx) - (math.sin(math.radians(p)) * wy))
            wy = round(
                (math.sin(math.radians(p)) * wx_orig) + (math.cos(math.radians(p)) * wy)
            )
        elif d == "F":
            sy += wy * p
            sx += wx * p
        # print(f'{i.strip():5s} {sx} {sy} {wx} {wy}')
    
    print(f"Part 2: {abs(sx) + abs(sy)}")
    

[« Day11](/adventofcode2020/11)[Day13 »](/adventofcode2020/13)

[](/adventofcode2020/12)

