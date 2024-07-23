# Advent of Code 2020: Day 18

[ctf](/tags#ctf ) [advent-of-code](/tags#advent-of-code )
[python](/tags#python )  
  
Dec 18, 2020

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
  * Day18
  * [Day19](/adventofcode2020/19)
  * [Day20](/adventofcode2020/20)
  * [Day21](/adventofcode2020/21)
  * [Day22](/adventofcode2020/22)
  * [Day23](/adventofcode2020/23)
  * [Day24](/adventofcode2020/24)
  * [Day25](/adventofcode2020/25)

![](https://0xdfimages.gitlab.io/img/aoc2020-18-cover.png)

Day 18 is reimplementing a simple math system with addition, multiplication,
and parentheses, where the order of operations changes. I’ll write a single
calc function that takes in the string to evaluate as well as the order of
operations to apply.

## Challenge

The puzzle can be found [here](https://adventofcode.com/2020/day/18). I’m
given a series of one line math problems containing numbers and `+*()`. In
both parts, I need to process anything inside `()` first. In part one, it’s
just left to right after that. In part two, I have to evaluate all the `+`
first, and then do the `*`.

## Solution

### Part 1

This is another case where recursion works well to get rid of the `()`. My
`calc` function has two modes. If there’s a `(` present in the input, it will
walk the string, starting from the first `(` counting open parentheses. Once
that count reaches zero, that sub-string is re-submitted to the `calc`
function, and replaced into the string, which is then passed back into `calc`.

When there are no parentheses, it splits the string into grams, taking the
first one as the total, and then evaluating the total with the next operator
and number to make a new total.

    
    
    def calc(s):
        if "(" in s:
            openp = 0
            start = s.index("(")
            for i in range(start, len(s)):
                if s[i] == "(":
                    openp += 1
                elif s[i] == ")":
                    openp -= 1
                if openp == 0:
                    break
            return calc(s[:start] + str(calc(s[start + 1 : i])) + s[i + 1 :])
    
        else:
            grams = s.split(" ")
            total = int(grams[0])
            for i in range(1, len(grams), 2):
                total = eval(f"{total} {grams[i]} {grams[i+1]}")
            return total
    

Now I just need to loop over all the lines and total each of their results:

    
    
    with open(sys.argv[1], "r") as f:
        probs = f.readlines()
    
    part1 = sum([calc(l) for l in probs])
    print(f"Part 1: {part1}")
    

### Part 2

I was tempted to create a `calc2` function, copying the first and modifying
it, but I wanted to make one calc that worked on any order of operations sent.

I added a second argument, `order`, which is an array of strings representing
operators that should be processed together. For example, actual math might
look like `['*/', '+-']` to process multiplication and division first, then
addition and subtraction. Part one is just this calc with order `['+*']`. But
for part two that will change to `['+', '*']`.

I’ll work through one time for each `ops` in `order`. So part one will just
take one pass since both are processed at the same time, where part two will
take two. I’ll check each operator, and if it’s in the current `ops`, then
evaluate it. When I take three items out of the list and replace it with one,
it actually works out that the next operator is now in the same position as
the previous one, so I don’t need to change `i`. When the operator isn’t in
`ops`, I’ll jump `i` to the next one.

    
    
    def calc(s, order):
        if "(" in s:
            openp = 0
            start = s.index("(")
            for i in range(start, len(s)):
                if s[i] == "(":
                    openp += 1
                elif s[i] == ")":
                    openp -= 1
                if openp == 0:
                    break
            return calc(s[:start] + calc(s[start + 1 : i], order) + s[i + 1 :], order)
    
        else:
            grams = s.split(" ")
            total = 0
            for ops in order:
                i = 1
                while i < len(grams):
                    if grams[i] in ops:
                        grams = (
                            grams[: i - 1]
                            + [str(eval(" ".join(grams[i - 1 : i + 2])))]
                            + grams[i + 2 :]
                        )
    
                    else:
                        i += 2
            assert len(grams) == 1
            return grams[0]
    

### Final Code

Don’t have speed issues on this challenge:

    
    
    $ time python3 day18.py 18-puzzle.txt
    Part 1: 29839238838303
    Part 2: 201376568795521
    
    real    0m0.129s
    user    0m0.124s
    sys     0m0.004s
    
    
    
    #!/usr/bin/env python3
    
    import sys
    
    
    def calc(s, order):
        if "(" in s:
            openp = 0
            start = s.index("(")
            for i in range(start, len(s)):
                if s[i] == "(":
                    openp += 1
                elif s[i] == ")":
                    openp -= 1
                if openp == 0:
                    break
            return calc(s[:start] + calc(s[start + 1 : i], order) + s[i + 1 :], order)
    
        else:
            grams = s.split(" ")
            total = 0
            for ops in order:
                i = 1
                while i < len(grams):
                    if grams[i] in ops:
                        grams = (
                            grams[: i - 1]
                            + [str(eval(" ".join(grams[i - 1 : i + 2])))]
                            + grams[i + 2 :]
                        )
    
                    else:
                        i += 2
            assert len(grams) == 2
            return grams[0]
    
    
    with open(sys.argv[1], "r") as f:
        probs = f.readlines()
    
    part1 = sum([int(calc(l, ["+*"])) for l in probs])
    print(f"Part 1: {part1}")
    
    part2 = sum([int(calc(l, ["+", "*"])) for l in probs])
    print(f"Part 2: {part2}")
    
    

[« Day17](/adventofcode2020/17)[Day19 »](/adventofcode2020/19)

[](/adventofcode2020/18)

