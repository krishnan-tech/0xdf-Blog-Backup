# Advent of Code 2019: Day 11

[ctf](/tags#ctf ) [advent-of-code](/tags#advent-of-code )
[python](/tags#python ) [intcode-computer](/tags#intcode-computer )
[defaultdict](/tags#defaultdict )  
  
Dec 11, 2019

  * [Day1](/adventofcode2019/1)
  * [Day2](/adventofcode2019/2)
  * [Day3](/adventofcode2019/3)
  * [Day4](/adventofcode2019/4)
  * [Day5](/adventofcode2019/5)
  * [Day6](/adventofcode2019/6)
  * [Day7](/adventofcode2019/7)
  * [Day8](/adventofcode2019/8)
  * [Day9](/adventofcode2019/9)
  * [Day10](/adventofcode2019/10)
  * Day11
  * [Day12](/adventofcode2019/12)
  * [Day13](/adventofcode2019/13)
  * [Day14](/adventofcode2019/14)

![](https://0xdfimages.gitlab.io/img/aoc2019-11-cover.png)

Continuing with the computer, now I’m using it to power a robot. My robot will
walk around, reading the current color, submitting that to the program, and
getting back the color to paint the current square and instructions for where
to move next.

## Challenge

The puzzle can be found [here](https://adventofcode.com/2019/day/11). I need
to write the code for a robot that will start on an all black (0) grid at 0,0.
It will input the color of the current panel to the computer, read the first
output which tells it to pain the current square black or white (1). Then it
reads another output from the computer which tells it to turn left (0) or
right (1). Then it moves forward one space. In part 1, I just need to count
the number of squares painted at least once. In part 2, I’ll need to change
the initial square to white, and then print the output.

## Solution

### Part 1

I made some slight changes to my computer. I added back in the `done` flag
that will be `False` until I get an opcode 99. I also now set compute to
return with opcode 4, rather than print.

Then I wrote the robot. I’ll make another class. At start, it will have a
position and velocity, as well as a `defaultdict` to track the panels. That’s
really handy, because then to count the number of painted panels, I just have
to count the keys in the `defaultdict`. I’ll also have a `computer` object.

    
    
        turn = {
            0: {(0, 1): (-1, 0), (-1, 0): (0, -1), (0, -1): (1, 0), (1, 0): (0, 1)},
            1: {(0, 1): (1, 0), (1, 0): (0, -1), (0, -1): (-1, 0), (-1, 0): (0, 1)},
        }
    
        def __init__(self, program):
            self.pos = (0, 0)
            self.vel = (0, 1)
            self.panels = defaultdict(int)
            self.comp = computer(program)
    

I’ve also included a constant dictionaru to help with turning. I’ll create a
`move` function to handle the move:

    
    
        def move(self, direction):
            self.vel = self.turn[direction][self.vel]
            self.pos = tuple(map(operator.add, self.pos, self.vel))
    

Now I’ll create a `paint` function that will run the program. It checks the
`done` flag in the computer to know when to stop. Then it calls `compute`
twice. The first time it passes in the current square color. The second time
it passes in `None`. This will break things if the program tries to read in
the second `compute`, but that’s what I want, since I’m assuming it won’t do
that based on the puzzle description.

Running this gives me the answer instantly:

    
    
    $ time ./day11.py 11-puzzle_input.txt
    Part 1: 2041
    
    real    0m0.124s
    user    0m0.120s
    sys     0m0.004s
    

### Part 2

For part 2, I need to change one thing in how I initialize - the starting
square can be white. I’ll update the `__init__` to take an optional
`start_color` argument (default 0), and set `self.panels[self.pos] =
start_color`. I’ll also add another constant dictionary to help draw the
robot:

    
    
        icon = {(0, 1): "^", (-1, 0): "<", (0, -1): "v", (1, 0): ">"}
    

Now I just need to write a `draw` function. I’ll find the corners of the
canvas first, then I’ll loop over y (remembering that y grows as it goes down,
which is opposite my intuition). For each y, I’ll create a row of output by
looping over the x range, and then printing it.

    
    
        def draw(self):
            minx = min(self.panels, key=operator.itemgetter(0))[0]
            maxx = max(self.panels, key=operator.itemgetter(0))[0]
            miny = min(self.panels, key=operator.itemgetter(1))[1]
            maxy = max(self.panels, key=operator.itemgetter(1))[1]
            for y in range(maxy + 1, miny - 2, -1):
                out = ""
                for x in range(minx - 1, maxx + 2):
                    if self.pos == (x, y):
                        out += self.icon[self.vel]
                    else:
                        out += str(self.panels[(x, y)])
                print(out.replace("1", chr(9608)).replace("0", " "))
    

Just like in [day8](/adventofcode2019/8), I’ll use the unicode block character
to print nice solid squares, and space to print empty ones.

This runs instantly, and paints 8 characters as expected:

    
    
    $ time ./day11.py 11-puzzle_input.txt
    Part 1: 2041
    Part 2:
    
      ████ ███  ████ ███  █  █ ████ ████ ███
         █ █  █    █ █  █ █ █  █       █ █  █
        █  █  █   █  █  █ ██   ███    █  █  █
       █   ███   █   ███  █ █  █     █   ███  ^
      █    █ █  █    █    █ █  █    █    █ █
      ████ █  █ ████ █    █  █ ████ ████ █  █
    
    
    real    0m0.140s
    user    0m0.136s
    sys     0m0.004s
    

Here’s an image from my terminal in case the text doesn’t format right:

![image-20191212061954607](https://0xdfimages.gitlab.io/img/image-20191212061954607.png)

## Final Code

    
    
    #!/usr/bin/env python3
    
    import sys
    import operator
    from collections import defaultdict
    from itertools import permutations
    
    
    class computer:
        def __init__(self, program):
            self.program = defaultdict(int)
            for i, v in enumerate(list(map(int, program.split(",")))):
                self.program[i] = v
            self.done = False
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
                    self.eip += 2
                    return self.get_param(mode1, 1 - 2)
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
                    return 0
                else:
                    print("Error")
                    sys.exit()
    
    
    class robot:
        turn = {
            0: {(0, 1): (-1, 0), (-1, 0): (0, -1), (0, -1): (1, 0), (1, 0): (0, 1)},
            1: {(0, 1): (1, 0), (1, 0): (0, -1), (0, -1): (-1, 0), (-1, 0): (0, 1)},
        }
        icon = {(0, 1): "^", (-1, 0): "<", (0, -1): "v", (1, 0): ">"}
    
        def __init__(self, program, start_color=0):
            self.pos = (0, 0)
            self.vel = (0, 1)
            self.panels = defaultdict(int)
            self.panels[self.pos] = start_color
            self.comp = computer(program)
    
        def move(self, direction):
            self.vel = self.turn[direction][self.vel]
            self.pos = tuple(map(operator.add, self.pos, self.vel))
    
        def paint(self):
            while not self.comp.done:
                self.panels[self.pos] = self.comp.compute(self.panels[self.pos])
                self.move(self.comp.compute(None))
    
        def draw(self):
            minx = min(self.panels, key=operator.itemgetter(0))[0]
            maxx = max(self.panels, key=operator.itemgetter(0))[0]
            miny = min(self.panels, key=operator.itemgetter(1))[1]
            maxy = max(self.panels, key=operator.itemgetter(1))[1]
            for y in range(maxy + 1, miny - 2, -1):
                out = ""
                for x in range(minx - 1, maxx + 2):
                    if self.pos == (x, y):
                        out += self.icon[self.vel]
                    else:
                        out += str(self.panels[(x, y)])
                print(out.replace("1", chr(9608)).replace("0", " "))
    
    
    with open(sys.argv[1], "r") as f:
        program_str = f.read().strip()
    
    
    bot = robot(program_str)
    bot.paint()
    print(f"Part 1: {len(bot.panels)}")
    
    bot = robot(program_str, 1)
    bot.paint()
    print("Part 2:")
    bot.draw()
    

[« Day10](/adventofcode2019/10)[Day12 »](/adventofcode2019/12)

[](/adventofcode2019/11)

