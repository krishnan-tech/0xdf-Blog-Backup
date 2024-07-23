# Advent of Code 2020: Day 15

[ctf](/tags#ctf ) [advent-of-code](/tags#advent-of-code )
[python](/tags#python ) [defaultdict](/tags#defaultdict )  
  
Dec 15, 2020

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
  * Day15
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

![](https://0xdfimages.gitlab.io/img/aoc2020-15-cover.png)

Day 15 is a game the elves play, where you have to remember the numbers said
in a list, and append the next number based on when it was previously said.
I’ll solve by storing the numbers not in a list and searching it each time,
but rather in a dictionary of lists, where the key is the number and the value
is a list of indexes. It still runs a bit slow in part two, but it works.

## Challenge

The puzzle can be found [here](https://adventofcode.com/2020/day/15). The
puzzle input will be a list of numbers, typically three numbers in the
examples, but even my puzzle input was only six numbers.

To add a number, I’ll look at the last number in the list, and see if it was
in the list before that. If not, I’ll add a 0. If it was, I’ll calculate the
difference between the index of the last number and the index of the prior
occurrence and add that. The two parts are the same, just looking for the
2020th number in part one, and the 30,000,000th number in part two.

## Solution

### Part 1

The most obvious way to approach this would be to build the list of items, and
search it each time for the last number. That would work for part one, but not
in part two. And it would be a bit of a mess in code. After thinking for a
minute (not having seen part two), I decided to store the numbers in a
dictionary of lists, where the key is the number, and the values are a list of
indexes where the number was named.

That allows me to quickly find the last two times a number was present, just
by looking at the last two values in that list.

    
    
    #!/usr/bin/env python3
    
    import sys
    from collections import defaultdict
    
    
    with open(sys.argv[1], 'r') as f:
        inputs = list(map(int, f.read().split(',')))
    
    
    nums = defaultdict(list)
    
    for i,n in enumerate(inputs):
        nums[n].append(i)
    
    last = n
    for i in range(len(inputs), 2020):
        if len(nums[last]) < 2:
            nums[0].append(i)
            last = 0
        else:
            last = nums[last][-1] - nums[last][-2]
            nums[last].append(i)
    
    print(f'Part 1: {last}')
    

I used a `defaultdict` for the numbers so that it would default to an empty
list if I tried to read a number that didn’t exist.

### Part 2

Because of the design decision I made in part one, this actually works just by
changing the bound in the for loop. It is not instant, but takes about 30
seconds to complete.

I suspect I could make it a bit faster by not storing the entire list of
indexes, but rather just the last one. But I didn’t know in part one what I
might need in part two, so I figured it was better to keep it.

### Final Code

Part one is basically instant, but part two grinds for a short while:

    
    
    $ time python3 day15.py 15-puzzle.txt
    Part 1: 755
    Part 2: 11962
    
    real    0m27.873s
    user    0m27.228s
    sys     0m0.644s
    
    
    
    #!/usr/bin/env python3
    
    import sys
    from collections import defaultdict
    
    
    with open(sys.argv[1], "r") as f:
        inputs = list(map(int, f.read().split(",")))
    
    
    nums = defaultdict(list)
    
    for i, n in enumerate(inputs):
        nums[n].append(i)
    
    last = n
    for i in range(len(inputs), 30000000):
        if len(nums[last]) < 2:
            nums[0].append(i)
            last = 0
        else:
            last = nums[last][-1] - nums[last][-2]
            nums[last].append(i)
        if i == 2019:
            print(f"Part 1: {last}")
    
    print(f"Part 2: {last}")
    

[« Day14](/adventofcode2020/14)[Day16 »](/adventofcode2020/16)

[](/adventofcode2020/15)

