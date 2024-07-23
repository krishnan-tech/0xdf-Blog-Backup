# Advent of Code 2019: Day 12

[ctf](/tags#ctf ) [advent-of-code](/tags#advent-of-code )
[python](/tags#python )  
  
Dec 12, 2019

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
  * Day12
  * [Day13](/adventofcode2019/13)
  * [Day14](/adventofcode2019/14)

![](https://0xdfimages.gitlab.io/img/aoc2019-12-cover.png)

Day 12 asks me to look at moons and calculate their positions based on a
simplified gravity between them. In the first part, I’ll run the system for
1000 steps and return a calculation (“energy”) based on each moons position
and velocity at that point. In the second part, I’ll have to find when the
positions repeat, which I can do by recognizing that the three axes are
independent of each other, and that I can find the cycle time for each axis,
and then find the least common multiple of them to get when all three are in
order.

## Challenge

The puzzle can be found [here](https://adventofcode.com/2019/day/12). I’m
given starting positions (x, y, z) for four moons, and each is assumed to
start with velocity 0. First, I’ll update velocity for each moon, but looking
at each axis, and adding one for each moon with a greater position on that
axis and subtracting one for each moon for a lesser position on that axis.
Then, once all the moons have new velocities, I’ll update each position by
adding the velocity. After 1000 iterations, I’m asked to return the total
energy, which is the total sum of the positions times the sum of the
velocities across the moons.

In part 2, I have to think a bit more algorithmically. I’m looking for the
number of steps until all the moons are in a repeated position. The prompt
tells me that it will just take too long (and likely require storing too many
states) to just run this. I’ll need to think creatively.

## Solution

### Part 1

I struggled with where to add classes in this code. I eventually wrote a
`Moon` class, though I’m not going to stand by any of this code as elegant or
even not ugly. I also wrote a helper function to calculate energy, though it
ended up being a one-liner:

    
    
    class Moon:
        def __init__(self, coords):
            self.pos = [int(x) for x in coords]
            self.vel = [0, 0, 0]
    
    
    def energy(moons):
        return sum([sum(map(abs, m.pos)) * sum(map(abs, m.vel)) for m in moons])
    

Now I’ll read my input and create a list of moons:

    
    
    with open(sys.argv[1], "r") as f:
        moons_str = [m.strip("\n<>") for m in f.readlines()]
    moons_coords = [re.findall(r"x=(-?\d+), y=(-?\d+), z=(-?\d+)", m)[0] for m in moons_str]
    moons = [Moon(m) for m in moons_coords]
    

Next, I’ll run 1000 iterations, each time updating velocity, and then updating
positions:

    
    
    for t in range(1000):
        for moon in moons:
            for other_moon in moons:
                for i in range(3):
                    if moon.pos[i] < other_moon.pos[i]:
                        moon.vel[i] += 1
                    elif moon.pos[i] > other_moon.pos[i]:
                        moon.vel[i] += -1
        for moon in moons:
            for i in range(3):
                moon.pos[i] += moon.vel[i]
    
    print(f"Part 1: {energy(moons)}")
    

Running this gives me the answer instantly:

    
    
    $ time ./day12.py 12-puzzle_input.txt
    Part 1: 10189
    
    real    0m0.042s
    user    0m0.038s
    sys     0m0.004s
    

### Part 2

The trick here is to realize that the x, y, and z coordinates are independent
of each other. Even as these multiple moons are flying around, where a moon is
in y and z doesn’t have any impact on the x for any other moon.

That means I can find the cycles in each of the three coordinates, and then
find the least common multiple (lcm) of the three cycle times to get the full
cycle time.

I kind of took a guess that the first position would be the one repeated and
submitted that lcm, and it work.

This code is ugly, and I probably could have added more structure around it,
or worked it into the loops in part 1, but I just created new `moons` and re-
ran a lot of the same code to advance the moons. This time, I keep three
lists, each containing states, where a state is all of the positions and
velocities on one axis at a given time. Once all three are at repeats, I know
I’ve reached the cycle length for each. Then I can just find the lcm of the
lengths of each of the three states:

    
    
    moons = [Moon(m) for m in moons_coords]
    x_states, y_states, z_states = set(), set(), set()
    while True:
        for moon in moons:
            for other_moon in moons:
                for i in range(3):
                    if moon.pos[i] < other_moon.pos[i]:
                        moon.vel[i] += 1
                    elif moon.pos[i] > other_moon.pos[i]:
                        moon.vel[i] += -1
        for moon in moons:
            for i in range(3):
                moon.pos[i] += moon.vel[i]
        x_state = tuple((m.pos[0], m.vel[0]) for m in moons)
        y_state = tuple((m.pos[1], m.vel[1]) for m in moons)
        z_state = tuple((m.pos[2], m.vel[2]) for m in moons)
        if x_state in x_states and y_state in y_states and z_state in z_states:
            break
        x_states.add(x_state)
        y_states.add(y_state)
        z_states.add(z_state)
    
    print(f"Part 2: {lcm(len(x_states), lcm(len(y_states), len(z_states)))}")
    

This takes a few seconds to run, but isn’t too bad:

    
    
    $ time ./day12.py 12-puzzle_input.txt
    Part 1: 10189
    Part 2: 469671086427712
    
    real    0m6.892s
    user    0m6.756s
    sys     0m0.136s
    

## Final Code

    
    
    #!/usr/bin/env python3
    
    import re
    import sys
    
    
    class Moon:
        def __init__(self, coords):
            self.pos = [int(x) for x in coords]
            self.vel = [0, 0, 0]
    
    
    def energy(moons):
        return sum([sum(map(abs, m.pos)) * sum(map(abs, m.vel)) for m in moons])
    
    
    def lcm(x, y):
        a, b = x, y
        while a:
            a, b = b % a, a
        return x // b * y
    
    
    with open(sys.argv[1], "r") as f:
        moons_str = [m.strip("\n<>") for m in f.readlines()]
    moons_coords = [re.findall(r"x=(-?\d+), y=(-?\d+), z=(-?\d+)", m)[0] for m in moons_str]
    moons = [Moon(m) for m in moons_coords]
    
    for t in range(1000):
        for moon in moons:
            for other_moon in moons:
                for i in range(3):
                    if moon.pos[i] < other_moon.pos[i]:
                        moon.vel[i] += 1
                    elif moon.pos[i] > other_moon.pos[i]:
                        moon.vel[i] += -1
        for moon in moons:
            for i in range(3):
                moon.pos[i] += moon.vel[i]
    
    print(f"Part 1: {energy(moons)}")
    
    moons = [Moon(m) for m in moons_coords]
    x_states, y_states, z_states = set(), set(), set()
    while True:
        for moon in moons:
            for other_moon in moons:
                for i in range(3):
                    if moon.pos[i] < other_moon.pos[i]:
                        moon.vel[i] += 1
                    elif moon.pos[i] > other_moon.pos[i]:
                        moon.vel[i] += -1
        for moon in moons:
            for i in range(3):
                moon.pos[i] += moon.vel[i]
        x_state = tuple((m.pos[0], m.vel[0]) for m in moons)
        y_state = tuple((m.pos[1], m.vel[1]) for m in moons)
        z_state = tuple((m.pos[2], m.vel[2]) for m in moons)
        if x_state in x_states and y_state in y_states and z_state in z_states:
            break
        x_states.add(x_state)
        y_states.add(y_state)
        z_states.add(z_state)
    
    print(f"Part 2: {lcm(len(x_states), lcm(len(y_states), len(z_states)))}")
    

[« Day11](/adventofcode2019/11)[Day13 »](/adventofcode2019/13)

[](/adventofcode2019/12)

