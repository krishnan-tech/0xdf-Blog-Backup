# Advent of Code 2020: Day 11

[ctf](/tags#ctf ) [advent-of-code](/tags#advent-of-code )
[python](/tags#python )  
  
Dec 11, 2020

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
  * Day11
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

![](https://0xdfimages.gitlab.io/img/aoc2020-11-cover.png)

Day 11 is grid-based challenge, where I’m giving a grid floor, empty seat, and
occupied seat, and asked to step through time using rules that define how a
seat will be occupied at time t+1 given the state of it and it’s neighbors at
time t. My code gets really ugly today, but it solves.

## Challenge

The puzzle can be found [here](https://adventofcode.com/2020/day/11). The
puzzle input is grid of characters where `L` represents an open seat, `#`
represents an occupied seat, and `.` represents floor with no seat. The
example given looks like:

    
    
    L.LL.LL.LL
    LLLLLLL.LL
    L.L.L..L..
    LLLL.LL.LL
    L.LL.LL.LL
    L.LLLLL.LL
    ..L.L.....
    LLLLLLLLLL
    L.LLLLLL.L
    L.LLLLL.LL
    

In part one, the rules state that a seat will go from `L` –> `#` if none of
the eight seats adjacent to it are occupied. A seat will go from `#` –> `L` if
four or more of the adjacent seats are occupied. Otherwise, it will stay the
same.

In part two, the rules change slightly. I no longer care about the seats
directly next to the seat, but rather the first seat the occupant would see
moving in each of the eight directions. The single seat in this example would
have eight occupied neighbors:

    
    
    .......#.
    ...#.....
    .#.......
    .........
    ..#L....#
    ....#....
    .........
    #........
    ...#.....
    

The other difference in part two is that now there must be five or more
occupied seats before the seat goes to empty (up from four).

## Solution

### Part 1

I decided to handle my input as a list of lists called `chairs`. I’ll use `R`
and `C` as short cuts for `len(chairs)` and `len(chairs[0])`, as those are
used a lot, and a second grid called `next_chairs` which is the next state (as
I don’t want to modify the original state while still calculating it). Now I
can start a loop that updates the state into `next_chairs`, and then either
breaks if no change happened, or copy `next_chairs` into `chairs`.

    
    
    #!/usr/bin/env python3
    
    import sys
    
    
    with open(sys.argv[1], "r") as f:
        chairs = list(map(str.strip, f.readlines()))
    
    R = len(chairs)
    C = len(chairs[0])
    neigh = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    
    next_chairs = [["x" for c in r] for r in chairs]
    
    while True:
    
        changed = False
        for r in range(R):
            for c in range(C):
                num_occ = sum(
                    [
                        chairs[r + y][c + x] == "#"
                        for x, y in neigh
                        if 0 <= r + y < R and 0 <= c + x < C
                    ]
                )
    
                if chairs[r][c] == "L" and num_occ == 0:
                    next_chairs[r][c] = "#"
                    changed = True
                elif chairs[r][c] == "#" and num_occ >= 4:
                    next_chairs[r][c] = "L"
                    changed = True
                else:
                    next_chairs[r][c] = chairs[r][c]
    
        if not changed:
            break
    
        chairs = [[next_chairs[r][c] for c in range(C)] for r in range(R)]
    
    part1 = sum([sum([chairs[r][c] == "#" for c in range(C)]) for r in range(R)])
    print(f"Part 1: {part1}")
    

The only tricky part here is getting the number of occupied chairs for each
chair. I used a list comprehension (I love them too much, I know). I’m looping
over the eight possible neighbors, but only if that delta results in a number
still in the valid range for `chairs`. Then I’ll check that neighbor spot to
see if it’s occupied, and `sum` over that list (which effectively counts the
`True`).

This runs and gives the result.

### Part 2

For part two, I basically copied all of my part one code and modified it
slightly. I could have made this into a function as well. This code gets a bit
ugly with loops.

Two changes needed here. The easy one is to update the number of occupied
neighbors that trigger the seat going empty:

    
    
                elif chairs[r][c] == "#" and num_occ >= 5:
                    next_chairs[r][c] = "L"
                    changed = True
    

The more difficult one is the sight-line look at neighbor seats. I replaced my
list comprehension that counts neighbors with a proper loop over each
direction:

    
    
                num_occ = 0
                for dr, dc in neigh:
                    x = c + dc
                    y = r + dr
                    while 0 <= x < C and 0 <= y < R and chairs[y][x] == ".":
                        x += dc
                        y += dr
                    if 0 <= x < C and 0 <= y < R and chairs[y][x] == "#":
                        num_occ += 1
    

For each direction, I’ll start by getting the positions `x` and `y` that is
the first coordinate in that direction. Then, as long as it’s in-bounds and a
floor place, I’ll continue moving in that direction. Once I hit non-floor or
leave the grid, I’ll check if it’s in the grid and occupied, and if so, add it
to the count.

### Final Code

These aren’t instant, but not too slow either:

    
    
    $ time python3 day11.py 11-puzzle.txt
    Part 1: 2338
    Part 2: 2134
    
    real    0m5.627s
    user    0m5.607s
    sys     0m0.020s
    
    
    
    #!/usr/bin/env python3
    
    import sys
    
    
    with open(sys.argv[1], "r") as f:
        chairs = list(map(str.strip, f.readlines()))
    
    R = len(chairs)
    C = len(chairs[0])
    neigh = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]
    
    next_chairs = [["x" for c in r] for r in chairs]
    
    while True:
    
        changed = False
        for r in range(R):
            for c in range(C):
                num_occ = sum(
                    [
                        chairs[r + y][c + x] == "#"
                        for x, y in neigh
                        if 0 <= r + y < R and 0 <= c + x < C
                    ]
                )
    
                if chairs[r][c] == "L" and num_occ == 0:
                    next_chairs[r][c] = "#"
                    changed = True
                elif chairs[r][c] == "#" and num_occ >= 4:
                    next_chairs[r][c] = "L"
                    changed = True
                else:
                    next_chairs[r][c] = chairs[r][c]
    
        if not changed:
            break
    
        chairs = [[next_chairs[r][c] for c in range(C)] for r in range(R)]
    
    part1 = sum([sum([chairs[r][c] == "#" for c in range(C)]) for r in range(R)])
    print(f"Part 1: {part1}")
    
    
    with open(sys.argv[1], "r") as f:
        chairs = list(map(str.strip, f.readlines()))
    
    R = len(chairs)
    C = len(chairs[0])
    
    next_chairs = [["x" for c in r] for r in chairs]
    
    while True:
    
        changed = False
        for r in range(R):
            for c in range(C):
                num_occ = 0
                for dr, dc in neigh:
                    x = c + dc
                    y = r + dr
                    while 0 <= x < C and 0 <= y < R and chairs[y][x] == ".":
                        x += dc
                        y += dr
                    if 0 <= x < C and 0 <= y < R and chairs[y][x] == "#":
                        num_occ += 1
    
                if chairs[r][c] == "L" and num_occ == 0:
                    next_chairs[r][c] = "#"
                    changed = True
                elif chairs[r][c] == "#" and num_occ >= 5:
                    next_chairs[r][c] = "L"
                    changed = True
                else:
                    next_chairs[r][c] = chairs[r][c]
    
        if not changed:
            break
    
        chairs = [[next_chairs[r][c] for c in range(C)] for r in range(R)]
    
    part2 = sum([sum([chairs[r][c] == "#" for c in range(C)]) for r in range(R)])
    print(f"Part 2: {part2}")
    

[« Day10](/adventofcode2020/10)[Day12 »](/adventofcode2020/12)

[](/adventofcode2020/11)

