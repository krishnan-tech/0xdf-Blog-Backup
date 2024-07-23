# Advent of Code 2019: Day 10

[ctf](/tags#ctf ) [advent-of-code](/tags#advent-of-code )
[python](/tags#python )  
  
Dec 10, 2019

  * [Day1](/adventofcode2019/1)
  * [Day2](/adventofcode2019/2)
  * [Day3](/adventofcode2019/3)
  * [Day4](/adventofcode2019/4)
  * [Day5](/adventofcode2019/5)
  * [Day6](/adventofcode2019/6)
  * [Day7](/adventofcode2019/7)
  * [Day8](/adventofcode2019/8)
  * [Day9](/adventofcode2019/9)
  * Day10
  * [Day11](/adventofcode2019/11)
  * [Day12](/adventofcode2019/12)
  * [Day13](/adventofcode2019/13)
  * [Day14](/adventofcode2019/14)

![](https://0xdfimages.gitlab.io/img/aoc2019-10-cover.png)

This challenge gives me a map of asteroids. I’ll need to play with different
ways to find which ones are directly in the path of others, first to see which
asteroids can see the most others, and then to destroy them one by one with a
laser.

## Challenge

The puzzle can be found [here](https://adventofcode.com/2019/day/10). I’m
given a map, where `.` represents space, and `#` represents an asteroid. For
example:

    
    
    .#..#
    .....
    #####
    ....#
    ...##
    

An asteroid can see another one unless there is a third one directly in the
line of sight (which is to say, the center of the asteroid falls on the line
between the center of the first two).

In the first challenge, I’ll find the asteroid with direct line of sight to
the most other asteroids. In part two, I’ll swing a rotating laser around,
which blows up the first asteroid it can see. I need to find the 200th
asteroid blown up.

## Solution

### Part 1

I started by reading the input file, and creating a list of asteroids:

    
    
    with open(sys.argv[1], "r") as f:
        lines = list(map(str.strip, f.readlines()))
    
    asteroids = []
    for y, line in enumerate(lines):
        for x, xval in enumerate(line):
            if xval == "#":
                asteroids.append((x,y))
    

Next, I needed a function to see if one asteroid can see another. I’ll use the
idea that for x, y, and z, y is between x and z only if dist(x,y) + dist(y,z)
== dist(x, z). Since floating point math gets tough, I’ll give it a bit of
space (0.0001) seemed to work nicely. For a pair of asteroids, I’ll loop over
the others and see if any of them are between the two:

    
    
    def dist(a1, a2):
        return math.sqrt(pow(a1[0] - a2[0], 2) + pow(a1[1] - a2[1], 2))
    
    
    def can_see(a1, a2):
        if a1 == a2:
            return False
        for ast in asteroids:
            if a1 == ast or a2 == ast:
                continue
            if abs((dist(a1, ast) + dist(ast, a2)) - dist(a1, a2)) < 0.0001:
                return False
        return True
    

I kept a dictiony of lists that allows me to note for each asteroid what
others it can see. I’ll just loop over the list twice, checking each pair:

    
    
    vis = defaultdict(list)
    for i in range(len(asteroids)):
        for j in range(i + 1, len(asteroids)):
            if can_see(asteroids[i], asteroids[j]):
                vis[asteroids[i]].append(asteroids[j])
                vis[asteroids[j]].append(asteroids[i])
    

Now I can just use `max` with a custom key based on length of the list:

    
    
    base = max(vis, key=lambda x: len(vis[x]))
    print(f"Part 1: {len(vis[base])} (at asteroid located at {base})")
    

The samples ran pretty quickly, but the puzzle input took almost 30 seconds:

    
    
    $ time ./day10.py 10-puzzle_input.txt
    Part 1: 227 (at asteroid located at (11, 13))
    
    real    0m29.170s
    user    0m29.158s
    sys     0m0.012s
    

### Part 2

Starting from the base I found, now I need to think in terms of angles. I’ll
write a loop to go over each asteroid, and calculate the angle between it and
the base using some basic trig. I’ll add 90 to get it so that 0 is up. I’ll
use a dictionary I called `angels` to store a list of asteroids at each angle.
I’ll not only store the location, but the distance to base to make sorting
easier:

    
    
    angles = defaultdict(list)
    for ast in asteroids:
        if ast == base:
            continue
        angle = (math.degrees(math.atan2(ast[1] - base[1], ast[0] - base[0])) + 90) % 360
        angles[angle].append((dist(ast, base), ast))
    
    for angle in angles:
        angles[angle] = sorted(angles[angle], reverse=True)
    

In a second loop, I’ll make sure each list of asteroids at a given angel is
sorted so that the closest is at the end.

Now I’ll loop over the angles using `pop` to remove the last item from the
list (the closest to the base).

    
    
    i = 0
    for angle in sorted(angles):
        boom = angles[angle].pop()
        i += 1
        if i == 200:
            print(f"Part 2: {boom[1]}")
            sys.exit()
    

It turns out that I hit the 200th asteroid in my first pass. Had I not, I
would have needed to wrap this all in a `while True`, and handled skipping
over empty lists.

This second part runs instantly (the time is all from part 1):

    
    
    $ time ./day10.py 10-puzzle_input.txt
    Part 1: 227 (at asteroid located at (11, 13))
    Part 2: (6, 4)
    
    real    0m31.261s
    user    0m31.223s
    sys     0m0.000s
    

## Final Code

    
    
    #!/usr/bin/env python3
    
    import math
    import sys
    from collections import defaultdict
    
    
    def dist(a1, a2):
        return math.sqrt(pow(a1[0] - a2[0], 2) + pow(a1[1] - a2[1], 2))
    
    
    def can_see(a1, a2):
        if a1 == a2:
            return False
        for ast in asteroids:
            if a1 == ast or a2 == ast:
                continue
            if abs((dist(a1, ast) + dist(ast, a2)) - dist(a1, a2)) < 0.0001:
                return False
        return True
    
    
    with open(sys.argv[1], "r") as f:
        lines = list(map(str.strip, f.readlines()))
    
    asteroids = []
    for y, line in enumerate(lines):
        for x, xval in enumerate(line):
            if xval == "#":
                asteroids.append((x, y))
    
    vis = defaultdict(list)
    for i in range(len(asteroids)):
        for j in range(i + 1, len(asteroids)):
            if can_see(asteroids[i], asteroids[j]):
                vis[asteroids[i]].append(asteroids[j])
                vis[asteroids[j]].append(asteroids[i])
    
    base = max(vis, key=lambda x: len(vis[x]))
    print(f"Part 1: {len(vis[base])} (at asteroid located at {base})")
    
    angles = defaultdict(list)
    for ast in asteroids:
        if ast == base:
            continue
        angle = (math.degrees(math.atan2(ast[1] - base[1], ast[0] - base[0])) + 90) % 360
        angles[angle].append((dist(ast, base), ast))
    
    for angle in angles:
        angles[angle] = sorted(angles[angle], reverse=True)
    
    i = 0
    for angle in sorted(angles):
        boom = angles[angle].pop()
        i += 1
        if i == 200:
            print(f"Part 2: {boom[1]}")
            sys.exit()
    

[« Day9](/adventofcode2019/9)[Day11 »](/adventofcode2019/11)

[](/adventofcode2019/10)

