# Advent of Code 2019: Day 13

[ctf](/tags#ctf ) [advent-of-code](/tags#advent-of-code )
[python](/tags#python ) [intcode-computer](/tags#intcode-computer )
[defaultdict](/tags#defaultdict )  
  
Dec 13, 2019

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
  * [Day11](/adventofcode2019/11)
  * [Day12](/adventofcode2019/12)
  * Day13
  * [Day14](/adventofcode2019/14)

![](https://0xdfimages.gitlab.io/img/aoc2019-13-cover.png)

Continuing with the computer, now I’m using it to power an arcade game. I’ll
use the given intcodes to run the game, and I’m responsible for moving the
joystick via input to the game. This challenge was awesome. I made a video of
the game running in my terminal, which wasn’t necessary, but turned out pretty
good.

## Challenge

The puzzle can be found [here](https://adventofcode.com/2019/day/13). I need
to write the code for an aracade game that is a take on the classic game
[Breakout](https://en.wikipedia.org/wiki/Breakout_\(video_game\)). The program
will draw the blocks on the screen. In part 1, it just paints a board, and I
need to count the number of blocks. For part two, I change the input into game
mode, and then I’m also responsible for moving the joystick and trying to keep
the ball alive.

### Part 1

Part 1 was really easy. I’ve already got the Computer. I just need to create a
`Computer` object using the program input and then run it until it finishing,
counting the number of times it returns a block type (every 3rd output) of 2.

    
    
    comp = Computer(program_str)
    count = 0
    while not comp.done:
        _, _, block = comp.compute(None), comp.compute(None), comp.compute(None)
        if block == 2:
            count += 1
    
    print(f'Part 1: {count}')
    

That runs and returns the answer:

    
    
    $ time ./day13.py 13-puzzle_input.txt 
    Part 1: 251
    
    real    0m0.066s
    user    0m0.059s
    sys     0m0.004s
    

### Part 2

Now I need to wrap the arcade game around this computer. I started to create a
`Breakout` class, but then realized that I’d be doing the entire game in the
`__init__` function. I created a

    
    
    program_str = '2' + program_str[1:]
    comp = Computer(program_str)
    screen = defaultdict(int)
    joystick = 0
    score = 0
    
    while not comp.done:
        x = comp.compute(joystick)
        y = comp.compute(joystick)
        b = comp.compute(joystick)
    
        if (x, y) == (-1, 0):
            score = b
        else:
            screen[(x,y)] = b
    

Now I wanted to see the screen, so I created a `print_screen` function as
well:

    
    
    def print_screen(screen, score):
        icons = {0: ' ', 1: chr(9608), 2: '.', 3: '_', 4: 'o'}
        for y in range(20):
            output = ''
            for x in range(37):
                output += icons[screen[(x,y)]]
            print(output)
        print(f'  {"-"*16}{score:05d}{"-"*16}')
    

I’ll add a call at the end of each loop. The ranges or 30x37 comes from
playing with it a few times to get the dimensions correct.

The first print looks like:

    
    
    █                                    
                                         
                                         
                                         
                                         
                                         
                                         
                                         
                                         
                                         
                                         
                                         
    
    
    
    
    
    
    
    
    --000000--
    

Then a few more:

    
    
    █████                                
                                         
                                         
                                         
                                         
                                         
                                         
                                         
                                         
                                         
                                         
                                         
                                         
                                         
                                         
                                         
                                         
                                         
                                         
                                         
    --000000--
    

It’s building the top across the board. I’ll skip forward a bunch, and can see
the board built, with walls and blocks, and then the ball is added:

    
    
    █████████████████████████████████████
    █                                   █
    █     .. .. ..........  .  .. . ... █
    █ ... .. ............ . ...... .    █
    █    .... .  ..  ... ... .. . . . . █
    █ .... ...... ....... ..  ...   ... █
    █  ........ . ..  ... .. ... .    . █
    █ .. .  .. .. .. ........   ... ..  █
    █ ...  .... ..  .... . ........ .   █
    █   .... ... .. .. ... ..   .. ..   █
    █  . .   .. .   .  .. ... ... . ..  █
    █ .....  . .. ...   ...  .. ... ..  █
    █  ....  .  .... ...   .   .. . ... █
    █ ..   ...  .    .... . ..  .  .... █
    █                                   █
    █               o                    
                                         
                                         
                                         
                                         
    --000000--
    

A bunch more cycles and I get the paddle:

    
    
    █████████████████████████████████████
    █                                   █
    █     .. .. ..........  .  .. . ... █
    █ ... .. ............ . ...... .    █
    █    .... .  ..  ... ... .. . . . . █
    █ .... ...... ....... ..  ...   ... █
    █  ........ . ..  ... .. ... .    . █
    █ .. .  .. .. .. ........   ... ..  █
    █ ...  .... ..  .... . ........ .   █
    █   .... ... .. .. ... ..   .. ..   █
    █  . .   .. .   .  .. ... ... . ..  █
    █ .....  . .. ...   ...  .. ... ..  █
    █  ....  .  .... ...   .   .. . ... █
    █ ..   ...  .    .... . ..  .  .... █
    █                                   █
    █               o                   █
    █                                   █
    █                                   █
    █                 _                 █
    █                                   █
    --000000--
    

Then the ball starts moving diagonally down to the right and bounces off the
paddle:

    
    
    █████████████████████████████████████
    █                                   █
    █     .. .. ..........  .  .. . ... █
    █ ... .. ............ . ...... .    █
    █    .... .  ..  ... ... .. . . . . █
    █ .... ...... ....... ..  ...   ... █
    █  ........ . ..  ... .. ... .    . █
    █ .. .  .. .. .. ........   ... ..  █
    █ ...  .... ..  .... . ........ .   █
    █   .... ... .. .. ... ..   .. ..   █
    █  . .   .. .   .  .. ... ... . ..  █
    █ .....  . .. ...   ...  .. ... ..  █
    █  ....  .  .... ...   .   .. . ... █
    █ ..   ...  .    .... . ..  .  .... █
    █                                   █
    █                                   █
    █                o                  █
    █                                   █
    █                 _                 █
    █                                   █
    --000000--
    
    █████████████████████████████████████
    █                                   █
    █     .. .. ..........  .  .. . ... █
    █ ... .. ............ . ...... .    █
    █    .... .  ..  ... ... .. . . . . █
    █ .... ...... ....... ..  ...   ... █
    █  ........ . ..  ... .. ... .    . █
    █ .. .  .. .. .. ........   ... ..  █
    █ ...  .... ..  .... . ........ .   █
    █   .... ... .. .. ... ..   .. ..   █
    █  . .   .. .   .  .. ... ... . ..  █
    █ .....  . .. ...   ...  .. ... ..  █
    █  ....  .  .... ...   .   .. . ... █
    █ ..   ...  .    .... . ..  .  .... █
    █                                   █
    █                                   █
    █                                   █
    █                 o                 █
    █                 _                 █
    █                                   █
    --000000--
    █████████████████████████████████████
    █                                   █
    █     .. .. ..........  .  .. . ... █
    █ ... .. ............ . ...... .    █
    █    .... .  ..  ... ... .. . . . . █
    █ .... ...... ....... ..  ...   ... █
    █  ........ . ..  ... .. ... .    . █
    █ .. .  .. .. .. ........   ... ..  █
    █ ...  .... ..  .... . ........ .   █
    █   .... ... .. .. ... ..   .. ..   █
    █  . .   .. .   .  .. ... ... . ..  █
    █ .....  . .. ...   ...  .. ... ..  █
    █  ....  .  .... ...   .   .. . ... █
    █ ..   ...  .    .... . ..  .  .... █
    █                                   █
    █                                   █
    █                  o                █
    █                                   █
    █                 _                 █
    █                                   █
    --000000--
    █████████████████████████████████████
    █                                   █
    █     .. .. ..........  .  .. . ... █
    █ ... .. ............ . ...... .    █
    █    .... .  ..  ... ... .. . . . . █
    █ .... ...... ....... ..  ...   ... █
    █  ........ . ..  ... .. ... .    . █
    █ .. .  .. .. .. ........   ... ..  █
    █ ...  .... ..  .... . ........ .   █
    █   .... ... .. .. ... ..   .. ..   █
    █  . .   .. .   .  .. ... ... . ..  █
    █ .....  . .. ...   ...  .. ... ..  █
    █  ....  .  .... ...   .   .. . ... █
    █ ..   ...  .    .... . ..  .  .... █
    █                                   █
    █                   o               █
    █                                   █
    █                                   █
    █                 _                 █
    █                                   █
    --000000--
    
    

I’ll need to add code to watch the ball and set the joystick. I’ll find them
using a list comprehension:

    
    
        ball = [p for p in screen if screen[p] == 4]
        paddle = [p for p in screen if screen[p] == 3]
    

Each of those should return `[]` before the item is added to the screen or if
it’s taken off because it’s been moved, and `[(x,y)]` otherwise.

Now I’ll just tilt my joystick to follow the ball:

    
    
        if ball and paddle:
            if ball[0][0] < paddle[0][0]:
                joystick = -1
            elif ball[0][0] > paddle[0][0]:
                joystick = 1
            else:
                joystick = 0
    

At this point I have all I need to run to completion and print the score:

    
    
    $ time ./day13.py 13-puzzle_input.txt
    Part 1: 251
    Part 2: 12779
    
    real    0m2.627s
    user    0m2.623s
    sys     0m0.004s
    

But I wanted to add the graphic part to this. I’ll add a variable
`need_to_print`, set to `False` at the start of each loop. If the score or the
ball position changes, I’ll set it to true. I’ll print the graphic version if
`sys.argv[2] == watch`. I’ll also print the code to clear the terminal before
each print, so it looks like a video. It looks pretty good for terminal
output:

![](https://0xdfimages.gitlab.io/img/aoc-13-breakout.gif)

## Final Code

    
    
    #!/usr/bin/env python3
    
    import sys
    import time
    from collections import defaultdict
    
    
    class Computer:
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
    
    
    def print_screen(screen, score):
        print("\33[2J")
        icons = {0: " ", 1: chr(9608), 2: ".", 3: "_", 4: "o"}
        for y in range(20):
            output = "  "
            for x in range(37):
                output += icons[screen[(x, y)]]
            print(output)
        print(f'  {"-"*16}{score:05d}{"-"*16}')
    
    
    with open(sys.argv[1], "r") as f:
        program_str = f.read().strip()
    
    
    comp = Computer(program_str)
    count = 0
    while not comp.done:
        _, _, block = comp.compute(None), comp.compute(None), comp.compute(None)
        if block == 2:
            count += 1
    
    
    watch = int(len(sys.argv) > 2 and sys.argv[2] == "watch")
    program_str = "2" + program_str[1:]
    comp = Computer(program_str)
    screen = defaultdict(int)
    joystick = 0
    score = 0
    
    while not comp.done:
        need_to_print = False
        x = comp.compute(joystick)
        y = comp.compute(joystick)
        b = comp.compute(joystick)
    
        if (x, y) == (-1, 0):
            score = b
            need_to_print = True
        else:
            screen[(x, y)] = b
    
        if b == 4:
            need_to_print = True
    
        ball = [p for p in screen if screen[p] == 4]
        paddle = [p for p in screen if screen[p] == 3]
    
        if ball and paddle:
            if ball[0][0] < paddle[0][0]:
                joystick = -1
            elif ball[0][0] > paddle[0][0]:
                joystick = 1
            else:
                joystick = 0
    
        if watch and need_to_print:
            print_screen(screen, score)
            time.sleep(0.05)
    
    print(f"Part 1: {count}")
    print(f"Part 2: {score}")
    

[« Day12](/adventofcode2019/12)[Day14 »](/adventofcode2019/14)

[](/adventofcode2019/13)

