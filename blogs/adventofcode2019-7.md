# Advent of Code 2019: Day 7

[ctf](/tags#ctf ) [advent-of-code](/tags#advent-of-code )
[python](/tags#python ) [intcode-computer](/tags#intcode-computer )  
  
Dec 8, 2019

  * [Day1](/adventofcode2019/1)
  * [Day2](/adventofcode2019/2)
  * [Day3](/adventofcode2019/3)
  * [Day4](/adventofcode2019/4)
  * [Day5](/adventofcode2019/5)
  * [Day6](/adventofcode2019/6)
  * Day7
  * [Day8](/adventofcode2019/8)
  * [Day9](/adventofcode2019/9)
  * [Day10](/adventofcode2019/10)
  * [Day11](/adventofcode2019/11)
  * [Day12](/adventofcode2019/12)
  * [Day13](/adventofcode2019/13)
  * [Day14](/adventofcode2019/14)

![](https://0xdfimages.gitlab.io/img/aoc2019-7-cover.png)

The computer is back again, and this time, I’m chaining it and using it as an
amplifier. In the each part, I’ll find the way to get maximum thrust from five
amplifiers given that each can take one of five given phases. In part two,
there’s a loop of amplification.

## Challenge

The puzzle can be found [here](https://adventofcode.com/2019/day/7). I’ve got
five amplifiers, and I give each one a phase, 0-4, so that each phase is used.
Then I run each computer on two inputs - the phase, and the output of the
previous amp.

In part two, the last amp actually feeds back into the first one, and now I’m
using phases 5-9.

## Solution

### Part 1

For part 1, I just changed my print statement for output to a return. I also
set the input to be an array, and let each input read pop off from that array:

    
    
                elif op == 3:
                    self.program[self.program[eip + 1]] = self.input.pop()
                    eip += 2
                elif op == 4:
                    eip += 2
                    return self.program[self.program[eip + 1]]
    

Otherwise left the computer the same. Then I created an `amplify` function:

    
    
    def amplify(phase_seq):
    
        sig = 0
        for phase in phase_seq:
            comp = computer(list(map(int, program_str.split(","))), [phase, sig])
            sig = comp.compute()
    
        return sig
    

I also created a loop to go across all possible orderings of 0-4 and get the
max:

    
    
    max_thrust = max([amplify(comb) for comb in permutations([0, 1, 2, 3, 4])])
    print(f"Part 1: {max_thrust}")
    

It runs immediately:

    
    
    $ time ./day7.py 07-puzzle_input.txt
    Part 1: 51679
    
    real    0m0.083s
    user    0m0.079s
    sys     0m0.004s
    

### Part 2

In part two, I’ll need to play with the computer a bit more. I changed it so
that the input was still defined at `__init__()`, but not I’ll have signal
passed to `compute` so that each call can have a new signal. I’m making the
assumption that after the first run which has two inputs and then an output,
it will alternate in then out until the program ends. And if it does have a
second input before an output, it takes the same signal.

It took me a while trouble shooting to realize I needed to move `eip` to also
be persistent across runs. And to handle exiting by getting the result,
incrementing `eip`, and then returning the result.

This one was particularly difficult to debug, and for the first time in a long
time, I wished I had something visual/GUI rather than `pdb`. But I eventually
got there:

    
    
    $ time ./day7.py 07-puzzle_input.txt
    Part 1: 51679
    Part 2: 19539216
    
    real    0m0.100s
    user    0m0.100s
    sys     0m0.000s
    

## Final Code

    
    
    #!/usr/bin/env python3
    
    import sys
    from itertools import permutations
    
    
    class computer:
        def __init__(self, program, input_):
            self.program = program
            self.input = input_
            self.first_in = True
            self.done = False
            self.eip = 0
    
        def get_param(self, mode, value):
            if mode == "0":
                return self.program[value]
            else:
                return value
    
        def compute(self, signal):
            while True:
                inst = self.program[self.eip]
                op = inst % 100
                mode3, mode2, mode1 = f"{inst // 100:03d}"
                assert mode3 == "0"
                if op == 1:
                    self.program[self.program[self.eip + 3]] = self.get_param(
                        mode1, self.program[self.eip + 1]
                    ) + self.get_param(mode2, self.program[self.eip + 2])
                    self.eip += 4
                elif op == 2:
                    self.program[self.program[self.eip + 3]] = self.get_param(
                        mode1, self.program[self.eip + 1]
                    ) * self.get_param(mode2, self.program[self.eip + 2])
                    self.eip += 4
                elif op == 3:
                    if self.first_in:
                        self.program[self.program[self.eip + 1]] = self.input
                        self.first_in = False
                    else:
                        self.program[self.program[self.eip + 1]] = signal
                    self.eip += 2
                elif op == 4:
                    self.eip += 2
                    return self.program[self.program[self.eip - 1]]
                elif op == 5:
                    if self.get_param(mode1, self.program[self.eip + 1]) != 0:
                        self.eip = self.get_param(mode2, self.program[self.eip + 2])
                    else:
                        self.eip += 3
                elif op == 6:
                    if self.get_param(mode1, self.program[self.eip + 1]) == 0:
                        self.eip = self.get_param(mode2, self.program[self.eip + 2])
                    else:
                        self.eip += 3
                elif op == 7:
                    self.program[self.program[self.eip + 3]] = int(
                        self.get_param(mode1, self.program[self.eip + 1])
                        < self.get_param(mode2, self.program[self.eip + 2])
                    )
                    self.eip += 4
                elif op == 8:
                    self.program[self.program[self.eip + 3]] = int(
                        self.get_param(mode1, self.program[self.eip + 1])
                        == self.get_param(mode2, self.program[self.eip + 2])
                    )
                    self.eip += 4
                elif op == 99:
                    self.done = True
                    return None
                else:
                    print("Error")
                    sys.exit()
    
    
    def amplify(phase_seq):
    
        sig = 0
        for phase in phase_seq:
            comp = computer(list(map(int, program_str.split(","))), phase)
            sig = comp.compute(sig)
    
        return sig
    
    
    def feedback_amplify(phase_seq):
    
        sig = 0
        last_valid = None
        comps = [
            computer(list(map(int, program_str.split(","))), phase) for phase in phase_seq
        ]
        while not any([comp.done for comp in comps]):
            for i in range(5):
                sig = comps[i].compute(sig)
                if sig is not None:
                    last_valid = sig
        return last_valid
    
    
    with open(sys.argv[1], "r") as f:
        program_str = f.read().strip()
    
    max_thrust = max([amplify(comb) for comb in permutations([0, 1, 2, 3, 4])])
    print(f"Part 1: {max_thrust}")
    
    max_feedback_thrust = max(
        [feedback_amplify(comb) for comb in permutations([5, 6, 7, 8, 9])]
    )
    print(f"Part 2: {max_feedback_thrust}")
    

[« Day6](/adventofcode2019/6)[Day8 »](/adventofcode2019/8)

[](/adventofcode2019/7)

