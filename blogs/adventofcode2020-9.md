# Advent of Code 2020: Day 9

[ctf](/tags#ctf ) [advent-of-code](/tags#advent-of-code )
[python](/tags#python )  
  
Dec 9, 2020

  * [Day1](/adventofcode2020/1)
  * [Day2](/adventofcode2020/2)
  * [Day3](/adventofcode2020/3)
  * [Day4](/adventofcode2020/4)
  * [Day5](/adventofcode2020/5)
  * [Day6](/adventofcode2020/6)
  * [Day7](/adventofcode2020/7)
  * [Day8](/adventofcode2020/8)
  * Day9
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

![](https://0xdfimages.gitlab.io/img/aoc2020-9-cover.png)

Day 9 is two challenges about looking across lists of ints to find pairs or
slices with a given sum.

## Challenge

The puzzle can be found [here](https://adventofcode.com/2020/day/9). Stripping
away the story, I’m given a list of integers and asked to find features in
them. For part one, I’m given a window of 25. Starting at the 26th number,
there should be two numbers in the 25 proceeding numbers that sum to that
number. I’m asked to walk the list and find the first number where that is not
the case. For part two, I need to find a contiguous group of numbers that sum
to the answer to part one.

## Solution

### Part 1

For part one, I’ll read the puzzle input and the window size from `argv`
(because in the examples they use a window of five instead of 25). I’ll loop
over `i` from that window size to the end of the array, and for each `i`, I’ll
check from `nums[i-window:i]` for pairs of numbers that total `nums[i]`. I’ll
get those pairs using `combinations` from
[itertools](https://docs.python.org/3/library/itertools.html).

Because I love list comprehensions, I can check all sums for each `i` in one
line:

    
    
    for i in range(window, len(nums)):
        if all([x + y != nums[i] for x,y in combinations(nums[i-window:i], 2)]):
            break
    

At that point, I’ve got part one.

### Part 2

Next I’m asked to find a subsection of the list that contains numbers adding
up to the part one answer. To find the starting index of that subsection, I’ll
walk the list again with an `i`, and for each `i`, I’ll loop over `j` from `i`
to the end of the list, checking if `sum(nums[i:j]) == target`.

    
    
    for i in range(len(nums)):
        for j in range(i+1, len(nums)):
            if sum(nums[i:j]) == target:
                print(f'Part 2: {min(nums[i:j]) + max(nums[i:j])}')
                sys.exit()
    

### Final Code

The first part returns instantly, which the second runs for a second:

    
    
    $ time python3 day9.py 09-puzzle.txt 25
    Part 1: 393911906
    Part 2: 59341885
    
    real    0m0.900s
    user    0m0.892s
    sys     0m0.008s
    
    
    
    #!/usr/bin/env python3
    
    import sys
    from itertools import combinations
    
    with open(sys.argv[1], "r") as f:
        nums = list(map(int, f.readlines()))
    
    window = int(sys.argv[2])
    
    for i in range(window, len(nums)):
        if all([x + y != nums[i] for x, y in combinations(nums[i - window : i], 2)]):
            break
    
    target = nums[i]
    print(f"Part 1: {target}")
    
    
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if sum(nums[i:j]) == target:
                print(f"Part 2: {min(nums[i:j]) + max(nums[i:j])}")
                sys.exit()
    

[« Day8](/adventofcode2020/8)[Day10 »](/adventofcode2020/10)

[](/adventofcode2020/9)

