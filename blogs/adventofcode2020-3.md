# Advent of Code 2020: Day 3

[ctf](/tags#ctf ) [advent-of-code](/tags#advent-of-code )
[python](/tags#python )  
  
Dec 3, 2020

  * [Day1](/adventofcode2020/1)
  * [Day2](/adventofcode2020/2)
  * Day3
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
  * [Day24](/adventofcode2020/24)
  * [Day25](/adventofcode2020/25)

![](https://0xdfimages.gitlab.io/img/aoc2020-3-cover.png)

Advent of code always dives into visual mapping in a way that makes you
conceptualize 2D (or 3D) space and move through it. I’ve got a map that
represents a slope with clear spaces and trees, and that repeats moving to the
right. As this is an early challenge, it’s still relatively simple to handle
the map with just an array of strings, which I’ll do to count the trees I
encounter on different trajectories moving across the map.

## Challenge

The puzzle can be found [here](https://adventofcode.com/2020/day/3). I’m given
an ASCII map of a slope with `.` that represents open spaces and `#` that
represent trees. The example map is:

>
>     ..##.......
>     #...#...#..
>     .#....#..#.
>     ..#.#...#.#
>     .#...##..#.
>     ..#.##.....
>     .#.#.#....#
>     .#........#
>     #.##...#...
>     #...##....#
>     .#..#...#.#
>  

The pattern there also repeats as I move to the right.

For part one, I start at the top left, and move down at a slope of down one,
right three. At that trajectory, I’m asked to figure out how many trees I will
encounter on the way to the bottom.

For part two I need to look at five different trajectories and do the same,
multiplying the results to get an answer.

## Solution

### Part 1

My immediate instinct was to create a map grid that I could pass in a
coordinate and get back tree or no tree. But as I started reading in the map,
I realized it was mostly already there. I’ll read the map in as a list of
strings, where the index into that list is the y coordinate. Because Python
handles strings as lists as well, the x coordinate will be the index in that
string.

The only remaining tricky part is to handle the repeating pattern as I move
right. I’ll do that be measuring the width of the map, and when I increment
the x coordinate, take the result mod the width to loop it back to the left
side of the map.

    
    
    #!/usr/bin/env python3
    
    import sys
    
    
    with open(sys.argv[1], "r") as f:
        map_ = list(map(str.strip, f.readlines()))
    
    w = len(map_[0])
    x, trees = 0, 0
    
    for y in range(len(map_)):
        if map_[y][x] == "#":
            trees += 1
        x = (x + 3) % w
    
    print(f"Part 1: {trees}")
    

### Part 2

I will just move the calculations into a function that takes the slope as dx
and dy:

    
    
    #!/usr/bin/env python3
    
    import math
    import sys
    
    
    with open(sys.argv[1], "r") as f:
        map_ = list(map(str.strip, f.readlines()))
    
    w = len(map_[0])
    
    
    def count_trees(dx, dy):
        x, trees = 0, 0
        for y in range(0, len(map_), dy):
            if map_[y][x] == "#":
                trees += 1
            x = (x + dx) % w
        return trees
    
    
    print(f"Part 1: {count_trees(3,1)}")
    
    slopes = [(1, 1), (3, 1), (5, 1), (7, 1), (1, 2)]
    part2 = math.prod([count_trees(dx, dy) for dx, dy in slopes])
    print(f"Part 2: {part2}")
    

Running this gives both answers (still instantly):

    
    
    $ time python3 day3.py 03-puzzle_input.txt 
    Part 1: 230
    Part 2: 9533698720
    
    real    0m0.032s
    user    0m0.022s
    sys     0m0.007
    

[« Day2](/adventofcode2020/2)[Day4 »](/adventofcode2020/4)

[](/adventofcode2020/3)

