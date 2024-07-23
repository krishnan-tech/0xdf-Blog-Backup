# Advent of Code 2020: Day 2

[ctf](/tags#ctf ) [advent-of-code](/tags#advent-of-code )
[python](/tags#python )  
  
Dec 2, 2020

  * [Day1](/adventofcode2020/1)
  * Day2
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

![](https://0xdfimages.gitlab.io/img/aoc2020-2-cover.png)

Day 2 was about processing lines that contained two numbers, a character, and
a string which is referred to as a password. Both parts are about using the
numbers and the character to determine if the password is “valid”. How the
numbers and character become a rule is different in parts 1 and 2.

## Challenge

The puzzle can be found [here](https://adventofcode.com/2020/day/2). I’m given
a text file with many lines, each with three parts - a number range, a
character, and a password, in the following format:

>
>     1-3 a: abcde
>     1-3 b: cdefg
>     2-9 c: ccccccccc
>  

For part one, the range represents the number of times that that given
characters has to appear in the password, and I need to figure out how many
valid passwords are in my list.

For part two the policy is different. The two numbers represent two character
positions in the password, where one and only one of those positions must be
the given character. Again, I’m to return the number of valid passwords in the
list.

## Solution

### Part 1

For part one, I’ll create a function that takes a line, breaks it into the
four parts (two numbers, character, and password), and then returns true or
false based on the number of times the character is in the password. Then I’ll
use that function in a list comprehension to create a list of passwords that
return true from that function, and just take the length of it:

    
    
    #!/usr/bin/env python3
    
    import sys
    
    
    def line_valid(line):
        r, c, p = line.split(" ")
        c = c.rstrip(":")
        r_low, r_high = map(int, r.split("-"))
        return r_low <= p.count(c) <= r_high
    
    
    with open(sys.argv[1], "r") as f:
        lines = f.readlines()
    
    num_valid1 = len([x for x in lines if line_valid(x)])
    
    print(f"Part 1: {num_valid1}")
    

### Part 2

In part two, same idea, just different interpretation of the numbers. I
thought about creating a new function to parse the line into its four
components, but then I realized I could just use the same function with
another arg. I’ll add an arg `part` with a default value of 1, and then just
branch at the end based on that arg as to which criteria to apply:

    
    
    #!/usr/bin/env python3
    
    import sys
    
    
    def line_valid(line, part=1):
        r, c, p = line.split(" ")
        c = c.rstrip(":")
        r_low, r_high = map(int, r.split("-"))
        if part==1:
            return r_low <= p.count(c) <= r_high
        return (p[r_low - 1] == c) ^ (p[r_high - 1] == c)
    
    
    with open(sys.argv[1], "r") as f:
        lines = f.readlines()
    
    num_valid1 = len([x for x in lines if line_valid(x)])
    num_valid2 = len([x for x in lines if line_valid(x, part=2)])
    
    print(f"Part 1: {num_valid1}")
    print(f"Part 2: {num_valid2}")
    

It is important to note the question’s hint about their numbering starting at
1, not 0, which is why I subtract 1 from the number before finding that value
in the string, as Python is 0 based.

Running this gives both answers:

    
    
    $ time python3 day02.py 02-puzzle_input.txt 
    Part 1: 454
    Part 2: 649
    
    real    0m0.040s
    user    0m0.023s
    sys     0m0.012s
    

[« Day1](/adventofcode2020/1)[Day3 »](/adventofcode2020/3)

[](/adventofcode2020/2)

