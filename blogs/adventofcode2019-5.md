# Advent of Code 2019: Day 5

[ctf](/tags#ctf ) [advent-of-code](/tags#advent-of-code )
[python](/tags#python ) [intcode-computer](/tags#intcode-computer )  
  
Dec 5, 2019

  * [Day1](/adventofcode2019/1)
  * [Day2](/adventofcode2019/2)
  * [Day3](/adventofcode2019/3)
  * [Day4](/adventofcode2019/4)
  * Day5
  * [Day6](/adventofcode2019/6)
  * [Day7](/adventofcode2019/7)
  * [Day8](/adventofcode2019/8)
  * [Day9](/adventofcode2019/9)
  * [Day10](/adventofcode2019/10)
  * [Day11](/adventofcode2019/11)
  * [Day12](/adventofcode2019/12)
  * [Day13](/adventofcode2019/13)
  * [Day14](/adventofcode2019/14)

![](https://0xdfimages.gitlab.io/img/aoc2019-5-cover.png)

Today I’m tasked with building on the simple computer I built in [day
2](/adventofcode2019/2). I’ll add new instructions for input / output and
comparisons / branching. I’ll also get parameter modes, so in addition to
reading values from other positions, I can now handle constants (known in
computer architecture as immediates).

## Challenge

The puzzle can be found [here](https://adventofcode.com/2019/day/5). I’ll
start with the computer from [day 2](/adventofcode2019/2), and in part one
I’ll add the concept of input and output. The user is prompted for input using
opcode 3 (which is provided for each part), and then a series of diagnostic
tests are run. For each of them, the result is printed using opcode 4. Each of
these opcodes use only one parameter, so I’ll have to now take that into
account and move eip forward only 2 spots for these instructions.

There’s also now the concept of parameter modes. If the instruction’s low two
digists are the opcode, and the high up to three (implied 0 if less than 3)
are flags. 0 means that the parameter references a location in the program,
just as before. A 1 means that the parameter is an immediate value, and to use
it.

For part two, I’m given four more opcodes - two conditional jumps and two
comparisons. These are enough to allow me to change what the program does
based on the input.

## Solution

### Part 1

The first thing I did was to turn my computer into a class. As the computer
becomes more complex, this just gives me more flexibility to keep the program
as a value in the class and call various functions.

In the `__init__` function, I’ll save the program and the input value. I’ll
have a `compute` function that is largely the function from day 2. And I’ll
add a function `get_param` that takes a mode and a value and returns either
the value or the value from that location in the program.

The logic for opcode 3 and 4 is quite simple to add. I’ll make some other
small changes, like incrementing eip inside of the switch block instead of
just advancing four for all instructions.

The biggest challenge is parsing the instruction to get the opcode and the
modes. I’ll use mod to get the opcode, and then integer division to isolate
the mode, and string formatting to produce a three-digit string that I can
split into three modes. Even if all instructions don’t require three modes,
it’s easier to just zero-pad and store three for all.

    
    
    #!/usr/bin/env python3
    
    import sys
    
    
    class computer:
        def __init__(self, program, input_):
            self.program = program
            self.input = input_
    
        def get_param(self, mode, value):
            if mode == "0":
                return self.program[value]
            else:
                return value
    
        def compute(self):
            eip = 0
            while True:
                inst = self.program[eip]
                op = inst % 100
                mode3, mode2, mode1 = f"{inst // 100:03d}"
                assert mode3 == "0"
                if op == 1:
                    self.program[self.program[eip + 3]] = self.get_param(
                        mode1, self.program[eip + 1]
                    ) + self.get_param(mode2, self.program[eip + 2])
                    eip += 4
                elif op == 2:
                    self.program[self.program[eip + 3]] = self.get_param(
                        mode1, self.program[eip + 1]
                    ) * self.get_param(mode2, self.program[eip + 2])
                    eip += 4
                elif op == 3:
                    self.program[self.program[eip + 1]] = self.input
                    eip += 2
                elif op == 4:
                    print(f"{self.program[self.program[eip+1]]}")
                    eip += 2
                elif op == 99:
                    break
                else:
                    print("Error")
                    sys.exit()
    
    
    with open(sys.argv[1], "r") as f:
        program_str = f.read().strip()
    
    comp = computer(list(map(int, program_str.split(","))), 1)
    print("Part 1:")
    comp.compute()
    

When I run this, I get the result:

    
    
    $ time ./day5.py 05-puzzle_input.txt 1
    Part 1:
    3
    0
    0
    0
    0
    0
    0
    0
    0
    9219874
    
    real    0m0.021s
    user    0m0.016s
    sys     0m0.004s
    

As the prompt told me, it will print the result of each diagnostic, and then
give a diagnostic code at the end. My solution is 9219874.

### Part 2

Part two is relatively straight forwrad. I just need to add these four
additional op codes. The two jumps are simply comparing the first parameter to
0, and then setting or incrementing eip based on the result:

    
    
                elif op == 5:
                    if self.get_param(mode1, self.program[eip + 1]) != 0:
                        eip = self.get_param(mode2, self.program[eip + 2])
                    else:
                        eip += 3
                elif op == 6:
                    if self.get_param(mode1, self.program[eip + 1]) == 0:
                        eip = self.get_param(mode2, self.program[eip + 2])
                    else:
                        eip += 3
    

The two comparisons are just setting the third parameter to the result of the
comparison of the first two:

    
    
                elif op == 7:
                    self.program[self.program[eip+3]] = int(self.get_param(mode1, self.program[eip + 1]) < self.get_param(mode2, self.program[eip + 2]))
                    eip += 4
                elif op == 8:
                    self.program[self.program[eip+3]] = int(self.get_param(mode1, self.program[eip + 1]) == self.get_param(mode2, self.program[eip + 2]))
                    eip += 4
    

Now I’ll add code at the bottom to create a new computer with input 5, and
`compute`:

    
    
    $ time ./day5.py 05-puzzle_input.txt
    Part 1:
    3
    0
    0
    0
    0
    0
    0
    0
    0
    9219874
    
    Part 2:
    5893654
    
    real    0m0.027s
    user    0m0.023s
    sys     0m0.004s
    

## Final Code

    
    
    #!/usr/bin/env python3
    
    import sys
    
    
    class computer:
        def __init__(self, program, input_):
            self.program = program
            self.input = input_
    
        def get_param(self, mode, value):
            if mode == "0":
                return self.program[value]
            else:
                return value
    
        def compute(self):
            eip = 0
            while True:
                inst = self.program[eip]
                op = inst % 100
                mode3, mode2, mode1 = f"{inst // 100:03d}"
                assert mode3 == "0"
                if op == 1:
                    self.program[self.program[eip + 3]] = self.get_param(
                        mode1, self.program[eip + 1]
                    ) + self.get_param(mode2, self.program[eip + 2])
                    eip += 4
                elif op == 2:
                    self.program[self.program[eip + 3]] = self.get_param(
                        mode1, self.program[eip + 1]
                    ) * self.get_param(mode2, self.program[eip + 2])
                    eip += 4
                elif op == 3:
                    self.program[self.program[eip + 1]] = self.input
                    eip += 2
                elif op == 4:
                    print(f"{self.program[self.program[eip+1]]}")
                    eip += 2
                elif op == 5:
                    if self.get_param(mode1, self.program[eip + 1]) != 0:
                        eip = self.get_param(mode2, self.program[eip + 2])
                    else:
                        eip += 3
                elif op == 6:
                    if self.get_param(mode1, self.program[eip + 1]) == 0:
                        eip = self.get_param(mode2, self.program[eip + 2])
                    else:
                        eip += 3
                elif op == 7:
                    self.program[self.program[eip + 3]] = int(
                        self.get_param(mode1, self.program[eip + 1])
                        < self.get_param(mode2, self.program[eip + 2])
                    )
                    eip += 4
                elif op == 8:
                    self.program[self.program[eip + 3]] = int(
                        self.get_param(mode1, self.program[eip + 1])
                        == self.get_param(mode2, self.program[eip + 2])
                    )
                    eip += 4
                elif op == 99:
                    break
                else:
                    print("Error")
                    sys.exit()
    
    
    with open(sys.argv[1], "r") as f:
        program_str = f.read().strip()
    
    print("Part 1:")
    comp = computer(list(map(int, program_str.split(","))), 1)
    comp.compute()
    
    print("\nPart 2:")
    comp = computer(list(map(int, program_str.split(","))), 5)
    comp.compute()
    

[« Day4](/adventofcode2019/4)[Day6 »](/adventofcode2019/6)

[](/adventofcode2019/5)

