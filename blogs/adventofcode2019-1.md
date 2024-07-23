# Advent of Code 2019: Day 1

[ctf](/tags#ctf ) [advent-of-code](/tags#advent-of-code )
[python](/tags#python )  
  
Dec 1, 2019

  * Day1
  * [Day2](/adventofcode2019/2)
  * [Day3](/adventofcode2019/3)
  * [Day4](/adventofcode2019/4)
  * [Day5](/adventofcode2019/5)
  * [Day6](/adventofcode2019/6)
  * [Day7](/adventofcode2019/7)
  * [Day8](/adventofcode2019/8)
  * [Day9](/adventofcode2019/9)
  * [Day10](/adventofcode2019/10)
  * [Day11](/adventofcode2019/11)
  * [Day12](/adventofcode2019/12)
  * [Day13](/adventofcode2019/13)
  * [Day14](/adventofcode2019/14)

![](https://0xdfimages.gitlab.io/img/aoc2019-1-cover.png)

This puzzle was basically reading a list of numbers, performing some basic
arithmetic, and summing the results. For part two, there’s a twist in that
I’ll need to do that same math on the results, and add then as long as they
are greater than 0.

## Challenge

The puzzle can be found [here](https://adventofcode.com/2019/day/1). I’m given
a text file with many lines, each with a single int. For part 1, I’m to read
each line as a weight, and calculate the amount of fuel necessary which is
proportional to the weight, fuel = max(floor(weight / 3) - 2, 0). I’m asked to
sum this fuel number to get a total fuel required. For part 2, I need to take
into account the weight of the fuel, and bring fuel for that.

## Solution

### Part 1

For part 1, after reading in the file and converting each line to an int, I
can use one of my favorite features in Python, [List
Comprehensions](https://www.python.org/dev/peps/pep-0202/). This allows me to
perform some action on each item in the array, resulting in a new array, which
I can them sum.

To solve part 1, my code was simply:

    
    
    #!/usr/bin/env python3
    
    import sys
    
    with open(sys.argv[1], 'r') as f:
        weights = [int(l) for l in f.readlines()]
    
    total_fuel = sum([(w//3)-2 for w in weights])
    print(f"Part 1: {total_fuel}")
    

### Part 2

In part 2, I need to take into account the weight of the fuel, and calculate
it stepwise and add it in as long as it’s positive. I started to think about a
recursive function, but a loop worked just find and lead to simpler code.

At first, I did make one mistake. See if you can spot it:

    
    
    total_fuel_plus = 0
    
    for w in weights:
        while w > 0:
            w = (w//3) - 2
            total_fuel_plus += w
    
    print(f"Part 2: {total_fuel_plus}")
    

My result was coming in too low. That’s because I was adding in a negative
before breaking. For example, if the `w` were 40, I would get 11, then 1, and
then -2, which sum to 10. But I really only want to add the positives.

I updated the code to check that `w` was greater than 0 before adding it to
the total, and it returns the correct answer:

    
    
    total_fuel_plus = 0
    
    for w in weights:
        w = (w//3) - 2
        while w > 0:
            total_fuel_plus += w
            w = (w//3) - 2
    
    print(f"Part 2: {total_fuel_plus}")
    

## Final Code

    
    
    #!/usr/bin/env python3
    
    import itertools
    import sys
    
    with open(sys.argv[1], 'r') as f:
        weights = [int(l) for l in f.readlines()]
    
    total_fuel = sum([(w//3)-2 for w in weights])
    print(f"Part 1: {total_fuel}")
    
    total_fuel_plus = 0
    
    for w in weights:
        w = (w//3) - 2
        while w > 0:
            total_fuel_plus += w
            w = (w//3) - 2
    
    print(f"Part 2: {total_fuel_plus}")
    

[Day2 »](/adventofcode2019/2)

[](/adventofcode2019/1)

