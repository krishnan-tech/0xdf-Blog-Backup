# Advent of Code 2019: Day 2

[ctf](/tags#ctf ) [advent-of-code](/tags#advent-of-code )
[python](/tags#python ) [intcode-computer](/tags#intcode-computer )  
  
Dec 2, 2019

  * [Day1](/adventofcode2019/1)
  * Day2
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

![](https://0xdfimages.gitlab.io/img/aoc2019-2-cover.png)

This puzzle is to implement a little computer with three op codes, add,
multiply, and finish. In the first part, I’m given two starting register
values, 12 and 2. In the second part, I need to brute force those values to
find a given target output.

## Challenge

The puzzle can be found [here](https://adventofcode.com/2019/day/2). I’m given
a text file with a single line of numbers, comma separated. I’m to implement a
computer that runs over the input. The first number (position 0) is the op
code. For this computer, there are only three:

  * 1 = add
  * 2 = multiply
  * 99 = exit

Add and multiply each use the next three values. The first two are the
registers to take as input, and the third is the register to write the result
to.

For part 1, I’m given puzzle input, but instructed to overwrite positions 1
and 2 with the values 12 and 2, and then return the output. For part two, I’m
given a target output, and asked to find initial values for positions 1 and 2
that will achieve that.

## Solution

### Part 1

For part 1, I’ll read in the data and keep it as a string. Originally I
converted this to a list of ints right there, but for part 2, it’s easier to
have the string to get a fresh computer. I’ll also create a function to do the
compute, taking in a list of ints, and returning the value in position 0 once
it reaches op code 99. The function just implements a `while True` loop,
breaking on opcode 99, and doing the operations for the other two op codes.

    
    
    #!/usr/bin/env python3
    
    import sys
    
    
    def compute(program):
        eip = 0
        while True:
            if program[eip] == 1:
                program[program[eip+3]] = program[program[eip+1]] + program[program[eip+2]]
            elif program[eip] == 2:
                program[program[eip+3]] = program[program[eip+1]] * program[program[eip+2]]
            elif program[eip] == 99:
                break
            else:
                print("Error")
                sys.exit()
            eip += 4
    
        return program[0]
    
    
    with open(sys.argv[1], 'r') as f:
        program_str = f.read().strip()
    
    program = list(map(int, program_str.split(',')))
    program[1], program[2] = 12, 2
    print(f"Part 1: {compute(program)}")
    

When I run this, I get the result:

    
    
    $ time ./day2.py 02-puzzle_input.txt 
    Part 1: 4330636
    
    real    0m0.027s
    user    0m0.023s
    sys     0m0.004s
    

I also notice that the output is very fast. This will be useful for brute
forcing in the next part.

### Part 2

In part 2, I need to find a `noun` (initial position 1) and `verb` (initial
position 2) that result in the value 19690720. Given that the program ran so
fast in the prior run, I decided to first try just brute forcing all possible
inputs between 0 and 100.

    
    
    for noun in range(100):
        for verb in range(100):
            program = list(map(int, program_str.split(',')))
            program[1], program[2] = noun, verb
            if compute(program) == 19690720:
                print(f"Part 2: {(100*noun)+verb}")
                sys.exit()
    

This does solve the challenge, and still pretty quickly:

    
    
    $ time ./day2.py 02-puzzle_input.txt 
    Part 1: 4330636
    Part 2: 6086
    
    real    0m0.140s
    user    0m0.135s
    sys     0m0.004s
    

When I start getting to later challenges, the compute time will likely be much
longer, meaning I’ll have to think about better strategies than just trying
10,000 different inputs and looking for the correct one. In this case, I can
see that if either input gets larger, the output can only get larger, since
I’m just using addition and multiplication. That means I could do some smarter
jumping up, and then falling back down when I get larger than the target. But
no need to implement that here.

## Final Code

    
    
    #!/usr/bin/env python3
    
    import sys
    
    
    def compute(program):
        eip = 0
        while True:
            if program[eip] == 1:
                program[program[eip+3]] = program[program[eip+1]] + program[program[eip+2]]
            elif program[eip] == 2:
                program[program[eip+3]] = program[program[eip+1]] * program[program[eip+2]]
            elif program[eip] == 99:
                break
            else:
                print("Error")
                sys.exit()
            eip += 4
    
        return program[0]
    
    
    with open(sys.argv[1], 'r') as f:
        program_str = f.read().strip()
    
    program = list(map(int, program_str.split(',')))
    program[1], program[2] = 12, 2
    print(f"Part 1: {compute(program)}")
    
    for noun in range(100):
        for verb in range(100):
            program = list(map(int, program_str.split(',')))
            program[1], program[2] = noun, verb
            if compute(program) == 19690720:
                print(f"Part 2: {(100*noun)+verb}")
                sys.exit()
    

[« Day1](/adventofcode2019/1)[Day3 »](/adventofcode2019/3)

[](/adventofcode2019/2)

