# Advent of Code 2020: Day 1

[ctf](/tags#ctf ) [advent-of-code](/tags#advent-of-code )
[python](/tags#python )  
  
Dec 1, 2020

  * Day1
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
  * [Day24](/adventofcode2020/24)
  * [Day25](/adventofcode2020/25)

![](https://0xdfimages.gitlab.io/img/aoc2020-1-cover.png)

Advent of Code is a CTF put on by Google every December, providing coding
challenges, and it’s a favorite of mine to practice. There are 25 days to
collect 50 stars. For Day 1, the puzzle was basically reading a list of
numbers, and looking through them for a pair and a set of three that summed to
2020. For each part, I’ll multiple the identified numbers together to get the
solution.

## Challenge

The puzzle can be found [here](https://adventofcode.com/2020/day/1). I’m given
a text file with many lines, each with a single int. For part one, I’m asked
to identify two numbers in the list that sum to 2020. For part two, I’m now
asked to look for a set of three numbers that sum to 2020. In each case, I’m
asked to return the product of the numbers.

## Solution

### Part 1

For part one, after reading in the file and converting each line to an int
using `map`, I’ll loop over the list. For each int, I’ll check if `2020 - x`
is also in the list. This allows me to loop over the list just once.

    
    
    #!/usr/bin/env python3
    
    import sys
    
    
    with open(sys.argv[1], "r") as f:
        nums = list(map(int, f.readlines()))
    
    for x in nums:
        if 2020 - x in nums:
            break
    
    print(f"Part 1: {x * (2020-x)}")
    

Of course I could make this faster by removing each number from the list once
it’s been checked, but for data of this size, it’s not really necessary.

### Part 2

In part two, now I need to look for three numbers that total 2020. I’ll do it
in the same loop, but this time, for each number, looping the list again
checking all pairs of numbers to see if a third number is in the list:

    
    
    #!/usr/bin/env python3
    
    import sys
    
    
    with open(sys.argv[1], "r") as f:
        nums = list(map(int, f.readlines()))
    
    s1, s2x = None, None
    
    for x in nums:
        if 2020 - x in nums:
            s1 = x
        for y in nums:
            if 2020 - (x + y) in nums:
                s2x, s2y = x, y
                break
        if s1 and s2x:
            break
    
    print(f"Part 1: {s1 * (2020-s1)}")
    print(f"Part 2: {s2x * s2y * (2020 - s2x - s2y )}")
    

Because I’m doing it in one loop, I’ll save the answers in variables, and if
both are set, then break.

### Running It

I can run this and get both solutions instantly:

    
    
    $ time python3 day01.py 01-puzzle_input.txt 
    Part 1: 1005459
    Part 2: 92643264
    
    real    0m0.088s
    user    0m0.085s
    sys     0m0.000s
    

For what it’s worth, if I remote the check to see if both solutions were
found, it consistently come out a bit slower:

    
    
    $ time python3 day01-slow.py 01-puzzle_input.txt 
    Part 1: 1005459
    Part 2: 92643264
    
    real    0m0.143s
    user    0m0.131s
    sys     0m0.004s
    

[Day2 »](/adventofcode2020/2)

[](/adventofcode2020/1)

