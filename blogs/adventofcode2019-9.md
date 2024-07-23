# Advent of Code 2019: Day 9

[ctf](/tags#ctf ) [advent-of-code](/tags#advent-of-code )
[python](/tags#python ) [intcode-computer](/tags#intcode-computer )
[defaultdict](/tags#defaultdict )  
  
Dec 9, 2019

  * [Day1](/adventofcode2019/1)
  * [Day2](/adventofcode2019/2)
  * [Day3](/adventofcode2019/3)
  * [Day4](/adventofcode2019/4)
  * [Day5](/adventofcode2019/5)
  * [Day6](/adventofcode2019/6)
  * [Day7](/adventofcode2019/7)
  * [Day8](/adventofcode2019/8)
  * Day9
  * [Day10](/adventofcode2019/10)
  * [Day11](/adventofcode2019/11)
  * [Day12](/adventofcode2019/12)
  * [Day13](/adventofcode2019/13)
  * [Day14](/adventofcode2019/14)

![](https://0xdfimages.gitlab.io/img/aoc2019-9-cover.png)

More computer work in day 9, this time adding what is kind of a stack pointer
and an opcode to adjust that pointer. Now I can add a relative address mode,
getting positions relative to the stack pointer.

## Challenge

The puzzle can be found [here](https://adventofcode.com/2019/day/9). Today I’m
to add a new address mode, relative base. I’ll keep a pointer to the current
relative base, which starts at 0. Now address mode 2 is to look that many
spots from the base pointer. I’ll also need to handle memory space beyond my
initial proram.

## Solution

### Part 1

The first thing I did was add the new mode to the computer. Since I’m already
working with a `get_param` function, it was relatively easy. I’ll initialize
the relative base at object creation. I did a bit of refactoring so that I
could clean up my code calling `get_param` which included calling with the reg
offset vs the value. And I added the new mode:

    
    
        def get_param(self, mode, reg):
            value = self.program[self.eip + reg]
            if mode == "0":
                return self.program[value]
            elif mode == "1":
                return value
            elif mode == "2":
                return self.program[self.rel_base + value]
            else:
                print("Error: Invalid Parameter Mode")
                sys.exit()
    

I’ll also handle the new op code:

    
    
                elif op == 9:
                    self.rel_base += self.get_param(mode1, 1)
                    self.eip += 3
    

To handle the larger computer memory, with default values of 0, I’ll start
using a `defaultdict` instead of a `list`. I’ll also move the processing of
the string into the `__init__` function, so I’m not having to handle it
outside the class:

    
    
        def __init__(self, program):
            self.program = defaultdict(int)
            for i, v in enumerate(list(map(int, program.split(",")))):
                self.program[i] = v
            self.eip = 0
            self.rel_base = 0
    

In day 7, I had to handle two inputs, and I ended up splitting that into a
`phase` that was passed in at computer initialization, and a `signal` that was
passed on each call to `compute`. Since the BOOST program for today only takes
one input, I’ll just pass it to `compute`. This results in less stuff in
`__init__` above, and as well as a simplified opcode 3:

    
    
                elif op == 3:
                    self.program[self.get_address(mode1, 1)] = signal
                    self.eip += 2
    

I spent a lot of time troubleshooting, and eventually figured out that I was
mishandling how a result could be written to relatively mode. I had an assert
to check that `mode3` was 0, but other commands used earlier args to get the
address to write to. I eventually added a `get_address` function:

    
    
        def get_address(self, mode, reg):
            value = self.program[self.eip + reg]
            if mode == "0":
                return value
            elif mode == "2":
                return self.rel_base + value
            else:
                print("Error: Invalid Address Mode")
                sys.exit()
    

Putting it all together, I get a quick answer:

    
    
    $ time python3 ./day9.py 09-puzzle_input.txt 
    Part 1:
    3989758265
    
    real    0m0.018s
    user    0m0.009s
    sys     0m0.009s
    

### Part 2

Nothing changed for part 2, other than the input. So I added a new computer
and called `compute(2)`, and ran it, and got the result, albeit slightly more
slowly:

    
    
    $ time python3 ./day9.py 09-puzzle_input.txt 
    Part 1:
    3989758265
    Part 2:
    76791
    
    real    0m0.534s
    user    0m0.534s
    sys     0m0.000s
    

## Final Code

    
    
    #!/usr/bin/env python3
    
    import sys
    from collections import defaultdict
    from itertools import permutations
    
    
    class computer:
        def __init__(self, program):
            self.program = defaultdict(int)
            for i, v in enumerate(list(map(int, program.split(",")))):
                self.program[i] = v
            self.eip = 0
            self.rel_base = 0
    
        def get_param(self, mode, reg):
            value = self.program[self.eip + reg]
            if mode == "0":
                return self.program[value]
            elif mode == "1":
                return value
            elif mode == "2":
                return self.program[self.rel_base + value]
            else:
                print("Error: Invalid Parameter Mode")
                sys.exit()
    
        def get_address(self, mode, reg):
            value = self.program[self.eip + reg]
            if mode == "0":
                return value
            elif mode == "2":
                return self.rel_base + value
            else:
                print("Error: Invalid Address Mode")
                sys.exit()
    
        def compute(self, signal):
            while True:
                inst = self.program[self.eip]
                op = inst % 100
                mode3, mode2, mode1 = f"{inst // 100:03d}"
                if op == 1:
                    self.program[self.get_address(mode3, 3)] = self.get_param(
                        mode1, 1
                    ) + self.get_param(mode2, 2)
                    self.eip += 4
                elif op == 2:
                    self.program[self.get_address(mode3, 3)] = self.get_param(
                        mode1, 1
                    ) * self.get_param(mode2, 2)
                    self.eip += 4
                elif op == 3:
                    self.program[self.get_address(mode1, 1)] = signal
                    self.eip += 2
                elif op == 4:
                    print(self.get_param(mode1, 1))
                    self.eip += 2
                elif op == 5:
                    if self.get_param(mode1, 1) != 0:
                        self.eip = self.get_param(mode2, 2)
                    else:
                        self.eip += 3
                elif op == 6:
                    if self.get_param(mode1, 1) == 0:
                        self.eip = self.get_param(mode2, 2)
                    else:
                        self.eip += 3
                elif op == 7:
                    self.program[self.get_address(mode3, 3)] = int(
                        self.get_param(mode1, 1) < self.get_param(mode2, 2)
                    )
                    self.eip += 4
                elif op == 8:
                    self.program[self.get_address(mode3, 3)] = int(
                        self.get_param(mode1, 1) == self.get_param(mode2, 2)
                    )
                    self.eip += 4
                elif op == 9:
                    self.rel_base += self.get_param(mode1, 1)
                    self.eip += 2
                elif op == 99:
                    self.done = True
                    return None
                else:
                    print("Error")
                    sys.exit()
    
    
    with open(sys.argv[1], "r") as f:
        program_str = f.read().strip()
    
    print("Part 1:")
    comp = computer(program_str)
    comp.compute(1)
    
    print("Part 2:")
    comp = computer(program_str)
    comp.compute(2)
    

[« Day8](/adventofcode2019/8)[Day10 »](/adventofcode2019/10)

[](/adventofcode2019/9)

