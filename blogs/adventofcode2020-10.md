# Advent of Code 2020: Day 10

[ctf](/tags#ctf ) [advent-of-code](/tags#advent-of-code )
[python](/tags#python ) [lru-cache](/tags#lru-cache )  
  
Dec 10, 2020

  * [Day1](/adventofcode2020/1)
  * [Day2](/adventofcode2020/2)
  * [Day3](/adventofcode2020/3)
  * [Day4](/adventofcode2020/4)
  * [Day5](/adventofcode2020/5)
  * [Day6](/adventofcode2020/6)
  * [Day7](/adventofcode2020/7)
  * [Day8](/adventofcode2020/8)
  * [Day9](/adventofcode2020/9)
  * Day10
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

![](https://0xdfimages.gitlab.io/img/aoc2020-10-cover.png)

Day 10 is about looking at a list of numbers. In the first part I’ll just need
to make a histogram of the differences between the numbers when sorted. For
part two, it’s the first challenge this year where I’ll need to come up with
an efficient algorithm to handle it. I’m asked to come up with the number of
valid combinations according to some constraints. I’ll use recursion to solve
it, and it only works in reasonable time with caching on that recursion.

## Challenge

The puzzle can be found [here](https://adventofcode.com/2020/day/10). The
puzzle input is a list of integers, though the problem states that there are
implied values of zero and three larger than the largest value, so I’ll need
to add those to the list. For part one, I’m asked to sort them and look at the
delta between values, counting the number of times that is one and three. For
part two, I’ve got the constraint that I can skip ahead as long as the values
don’t jump by more than three. I’m tasked with finding the number of valid
combinations.

The example given uses this list:

    
    
    16
    10
    15
    5
    1
    11
    7
    19
    6
    12
    4
    

The number of valid combinations is eight:

    
    
    (0), 1, 4, 5, 6, 7, 10, 11, 12, 15, 16, 19, (22)
    (0), 1, 4, 5, 6, 7, 10, 12, 15, 16, 19, (22)
    (0), 1, 4, 5, 7, 10, 11, 12, 15, 16, 19, (22)
    (0), 1, 4, 5, 7, 10, 12, 15, 16, 19, (22)
    (0), 1, 4, 6, 7, 10, 11, 12, 15, 16, 19, (22)
    (0), 1, 4, 6, 7, 10, 12, 15, 16, 19, (22)
    (0), 1, 4, 7, 10, 11, 12, 15, 16, 19, (22)
    (0), 1, 4, 7, 10, 12, 15, 16, 19, (22)
    

## Solution

### Part 1

Part one was really straight forward. First I need a bit of work to prep the
list. I’ll read it in, convert to ints, append zero and three plus the max,
and sort. Now I’ll just use a list comprehension from one to the length of the
list to get a list of the deltas, and a `Counter` from
[collections](https://docs.python.org/3/library/collections.html) to quickly
count the number of each value. I can multiple the ones and threes count to
get the answer:

    
    
    with open(sys.argv[1], "r") as f:
        adapters = list(map(int, f.readlines()))
    adapters = sorted(adapters + [0, max(adapters) + 3])
    
    diffs = [adapters[i] - adapters[i - 1] for i in range(1, len(adapters))]
    hist = Counter(diffs)
    
    print(f"Part 1: {hist[1] * hist[3]}")
    

### Part 2

This is the hardest challenge yet this year, because it forces you to think
through the best algorithm to figure this out. The most obvious idea would be
to generate all possible combinations of any length, and then throw away any
that contain jumps of more than three. But there would be way too many to do
that, and it would run forever.

Instead, I’ll use a recursive approach, creating a function that looks at an
index in the list and figured out how many paths there are to the end from
there. I’ll posit that from any given node, the number of paths to the end is
the sums of the number of paths to the end for each of the nodes that could
possibly come next.

I’ll use this example input: `(0), 1, 4, 5, 6, 7,(10)`. If I start at the end
of the list (`paths_to_end(6)`), how many paths are there? Well…one. It’s a
single node. Simple base case. Now I’ll step back one node
(`paths_to_end(5)`). The list is now `7, (10)`. Still just one way to traverse
the list. The same for `paths_to_end(4)`.

Stepping back again is where it gets interesting. The list is now `5, 6, 7,
(10)`. From there, I could go `5, 6, 7, (10)` or `5, 7, (10)`. And thinking
about this more generically, `paths_to_end(3) = paths_to_end(4) +
paths_to_end(5)`.

From this understanding, I can create a recursive function:

    
    
    @lru_cache(maxsize=256)
    def paths_to_end(i):
        if i == len(adapters) - 1:
            return 1
        return sum(
            [
                paths_to_end(j)
                for j in range(i + 1, min(i + 4, len(adapters)))
                if adapters[j] - adapters[i] <= 3
            ]
        )
    

If I’m at the last node, the number of paths is one. Otherwise, look ahead at
the next three nodes (or to the end of the list, whichever is first), and for
any that are valid jumps (value is no more than three more), find the number
of paths from that node to the end.

For back to this example: `(0), 1, 4, 5, 6, 7,(10)`

i | nums[i] | paths_to_end(i) | Result  
---|---|---|---  
0 | 0 | paths_to_end(1) | 4  
1 | 1 | path_to_end(2) | 4  
2 | 4 | paths_to_end(3) + paths_to_end(4) + paths_to_end(5) | 4  
3 | 5 | paths_to_end(4) + paths_to_end(5) | 2  
4 | 6 | paths_to_end(5) | 1  
5 | 7 | paths_to_end(6) | 1  
6 | 10 | 1 | 1  
  
I can work forward to fill in the third column, and once that’s done, work up
from the bottom to generate the forth column to get the final answer.

### Final Code

With caching, this returns instantly:

    
    
    $ time python3 day10.py 10-puzzle.txt 
    Part 1: 2080
    Part 2: 6908379398144
    
    real    0m0.056s
    user    0m0.044s
    sys     0m0.012s
    
    
    
    #!/usr/bin/env python3
    
    import sys
    from collections import Counter
    from functools import lru_cache
    
    
    with open(sys.argv[1], "r") as f:
        adapters = list(map(int, f.readlines()))
    adapters = sorted(adapters + [0, max(adapters) + 3])
    
    diffs = [adapters[i] - adapters[i - 1] for i in range(1, len(adapters))]
    hist = Counter(diffs)
    
    print(f"Part 1: {hist[1] * hist[3]}")
    
    
    @lru_cache(maxsize=256)
    def paths_to_end(i):
        if i == len(adapters) - 1:
            return 1
        return sum(
            [
                paths_to_end(j)
                for j in range(i + 1, min(i + 4, len(adapters)))
                if adapters[j] - adapters[i] <= 3
            ]
        )
    
    
    print(f"Part 2: {paths_to_end(0)}")
    

### On Caching

Caching is critical for this piece. I used `lru_cache` from
[functools](https://docs.python.org/3/library/functools.html), but I could
have just as easily defined a dict outside the function, and at the end of the
function, add the key / value `i` / `result` to the dict. At the start of the
function I could check to see if i was in the dict, and if so, returned the
same value.

If I comment out the `@lru_cache` decorator in the code above, my puzzle input
runs for longer than I was willing to wait (I killed it after 30 minutes). So
to illustrate this, I’ll add a counter outside the function, starting at 0,
and then declare it as `global` and increment it each time `path_to_end` is
called.

I’ll use two small examples from the challenge:

    
    
    $ wc -l 10-test*.txt
     11 10-test1.txt
     31 10-test2.txt
     42 total
    

With caching, the function is actually executed (as opposed to returning from
cache) the length of input pus two times:

    
    
    $ python3 day10.py 10-test1.txt 
    Part 1: 35
    Part 2: 8
    Called path_to_end 13 times
    
    $ python3 day10.py 10-test2.txt 
    Part 1: 220
    Part 2: 19208
    Called path_to_end 33 times
    

If I comment out the caching, it goes up exponentially:

    
    
    $ python3 day10.py 10-test1.txt
    Part 1: 35
    Part 2: 8
    Called path_to_end 58 times
    
    $ python3 day10.py 10-test2.txt
    Part 1: 220
    Part 2: 19208
    Called path_to_end 76217 times
    

[« Day9](/adventofcode2020/9)[Day11 »](/adventofcode2020/11)

[](/adventofcode2020/10)

