# Advent of Code 2020: Day 8

[ctf](/tags#ctf ) [advent-of-code](/tags#advent-of-code )
[python](/tags#python )  
  
Dec 8, 2020

  * [Day1](/adventofcode2020/1)
  * [Day2](/adventofcode2020/2)
  * [Day3](/adventofcode2020/3)
  * [Day4](/adventofcode2020/4)
  * [Day5](/adventofcode2020/5)
  * [Day6](/adventofcode2020/6)
  * [Day7](/adventofcode2020/7)
  * Day8
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

![](https://0xdfimages.gitlab.io/img/aoc2020-8-cover.png)

Today I’m asked to build a small three instruction computer, and parse a
series of instructions (puzzle input). I’m told that the instructions form an
infinite loop, which is easy to identify in this simple computer any time an
instruction is executed a second time. I’ll look at finding where that
infinite loop is entered, as well as finding the one instruction that can be
patched to fix the code. I’ll create a class for the computer with the
thinking that I might be coming back to use it again and build on it later.

## Challenge

The puzzle can be found [here](https://adventofcode.com/2020/day/8). It’s time
to introduce an emulator. In past years, once I built this kind of emulator,
I’d keep building on it over successive challenges. This one has three
instructions:

  * `acc [x]` \- Add `x` to the global accumulator value (starts at 0), and move to next instruction;
  * `jump [x]` \- Move to instruction `x` away (forward or backwards with negative);
  * `nop` \- No operation, move to next instruction

The boot code (my puzzle input) is corrupted so that it run in an infinite
loop.

For part one, I’m asked to run the program until it reaches an instruction it
already ran. Given the simplicity of the computer, this guarantees an infinite
loop. Before running that instruction again, I’ll just exit and provide the
accumulator value.

In part two, I’m told that there is either a `jmp` that should be a `nop` or a
`nop` that should be a `jmp`, and that that one change will fix the infinite
loop such that it runs the last instruction and then should exit.

## Solution

### Part 1

Given the chances that this computer will continue throughout the year, I
opted to write a simple class for it:

    
    
    class console:
        def __init__(self, puzzle_input):
    
            self.acc = 0
            self.prog = [
                (line.split(" ")[0], int(line.split(" ")[1])) for line in puzzle_input
            ]
            self.eip = 0
            self.executed_insts = set()
    
    
        def run(self):
    
            while self.eip not in self.executed_insts:
                self.executed_insts.add(self.eip)
                op, arg = self.prog[self.eip]
                if op == "acc":
                    self.acc += arg
                    self.eip += 1
                elif op == "jmp":
                    self.eip += arg
                elif op == "nop":
                    self.eip += 1
                else:
                    raise ValueError(f"Invalid op code: [{self.eip}] {self.prog}")
    

On initialization, it will take the raw puzzle input and convert it to an
array of instructions with two parts, the op code and the integer argument. It
starts an `eip` variable to represent the current instruction, and initializes
the accumulator to 0. It also starts an empty array to hold run instructions.

In the `run` function, it will loop as long as the instruction has not been
executed before, updating based on the rules for the three op codes.

Now I’ll simply create a `console` object, call the `run` function, and then
get the `acc` value:

    
    
    with open(sys.argv[1], "r") as f:
        data = f.read().strip()
    
    c = console(data)
    print(c.run())
    print(f"Part 1: {c.acc}")
    

### Part 2

Now I need to track a second way to exit the loop, when the computer tries to
run the instruction beyond the last one. I’ll leave the while condition the
same, but add to the end of the loop code that checks if `eip` is now equal to
the size of the list, and if so, return 0. Then I can have it return -1 if the
while exits, so I’ll know an infinite loop was found.

I could add something to the computer that does the swap, but I want to keep
the `console` class clean, so I’m going to manipulate the input before passing
it in. I’ll loop over the lines of input, and for each line, I’ll continue if
there’s an `acc`. Otherwise, I’ll make that swap in that line, and then run a
new `console` using that one modified line. Whenever I get back a 0 (the
program exited without loop), I’ll know I found the good input, and print the
`acc` value.

    
    
    for i in range(len(data)):
        if "acc" in data[i]:
            continue
        elif "jmp" in data[i]:
            mod = data[i].replace("jmp", "nop")
        elif "nop" in data[i]:
            mod = data[i].replace("nop", "jmp")
        else:
            raise ValueError(f"Invalid op code: [{self.eip}] {self.prog}")
        c = console(data[:i] + [mod] + data[i + 1 :])
        if c.run() == 0:
            print(f"Part 2: {c.acc}")
            break
    

This runs instantly and gives the values I’m looking for:

    
    
    $ time python3 day8.py 08-puzzle_input.txt
    Part 1: 1594
    Part 2: 758
    
    real    0m0.115s
    user    0m0.101s
    sys     0m0.012s
    

### Final Code

    
    
    #!/usr/bin/env python3
    
    import sys
    
    
    class console:
        def __init__(self, puzzle_input):
    
            self.acc = 0
            self.prog = [
                (line.split(" ")[0], int(line.split(" ")[1])) for line in puzzle_input
            ]
            self.eip = 0
            self.executed_insts = set()
    
        def run(self):
    
            while self.eip not in self.executed_insts:
                self.executed_insts.add(self.eip)
                op, arg = self.prog[self.eip]
                if op == "acc":
                    self.acc += arg
                    self.eip += 1
                elif op == "jmp":
                    self.eip += arg
                elif op == "nop":
                    self.eip += 1
                else:
                    raise ValueError(f"Invalid op code: [{self.eip}] {self.prog}")
                if self.eip == len(self.prog):
                    return 0
            return -1
    
    
    with open(sys.argv[1], "r") as f:
        data = f.read().strip().split("\n")
    
    c = console(data)
    c.run()
    print(f"Part 1: {c.acc}")
    
    for i in range(len(data)):
        if "acc" in data[i]:
            continue
        elif "jmp" in data[i]:
            mod = data[i].replace("jmp", "nop")
        elif "nop" in data[i]:
            mod = data[i].replace("nop", "jmp")
        else:
            raise ValueError(f"Invalid op code: [{self.eip}] {self.prog}")
        c = console(data[:i] + [mod] + data[i + 1 :])
        if c.run() == 0:
            print(f"Part 2: {c.acc}")
            break
    

[« Day7](/adventofcode2020/7)[Day9 »](/adventofcode2020/9)

[](/adventofcode2020/8)

