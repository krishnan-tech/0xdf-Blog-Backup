# Advent of Code 2020: Day 7

[ctf](/tags#ctf ) [advent-of-code](/tags#advent-of-code )
[python](/tags#python ) [lru-cache](/tags#lru-cache )
[defaultdict](/tags#defaultdict )  
  
Dec 7, 2020

  * [Day1](/adventofcode2020/1)
  * [Day2](/adventofcode2020/2)
  * [Day3](/adventofcode2020/3)
  * [Day4](/adventofcode2020/4)
  * [Day5](/adventofcode2020/5)
  * [Day6](/adventofcode2020/6)
  * Day7
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

![](https://0xdfimages.gitlab.io/img/aoc2020-7-cover.png)

Day 7 gives me a list of bags, and what bags must go into those bags. The two
parts are based on looking for what can hold what and how many. I’ll use
defaultdicts to manage the rules, and two recurrsive functions (including one
that benefits from lru_cache) to solve the parts.

## Challenge

The puzzle can be found [here](https://adventofcode.com/2020/day/7). I’m given
a list of bags by color, and the rules for which bags go into each bag (also
by color). The example input is:

    
    
    light red bags contain 1 bright white bag, 2 muted yellow bags.
    dark orange bags contain 3 bright white bags, 4 muted yellow bags.
    bright white bags contain 1 shiny gold bag.
    muted yellow bags contain 2 shiny gold bags, 9 faded blue bags.
    shiny gold bags contain 1 dark olive bag, 2 vibrant plum bags.
    dark olive bags contain 3 faded blue bags, 4 dotted black bags.
    vibrant plum bags contain 5 faded blue bags, 6 dotted black bags.
    faded blue bags contain no other bags.
    dotted black bags contain no other bags.
    

In part one, I’m told I want to carry a shiny gold bag inside at least one
other bag, and asked to find how many different bags could hold it (or hold
something else that could hold it).

For part two, I’m asked to start with a given bag, and count the number of
bags that go into it.

## Solution

### Part 1

I’ll approach this in two parts. First, I need to process the list into a
dictionary, where the key is a bag name, and the value is another dict, which
will be the color, and the number it can hold. My goal is to get to go from:

    
    
    light red bags contain 1 bright white bag, 2 muted yellow bags.
    

to:

    
    
    >>> bags['light red']
    {'bright white': 1, 'muted yellow': 2}
    

I’ll start with this Python to do that:

    
    
    #!/usr/bin/env python3
    
    import sys
    from collections import defaultdict
    from functools import lru_cache
    
    
    with open(sys.argv[1], 'r') as f:
        rules = f.readlines()
    
    bags = defaultdict(dict)
    
    for rule in rules:
        parts = rule.split(' ')
        color = ' '.join(parts[:2])
        in_parts = ' '.join(parts[4:]).split(',')
        for part in in_parts:
            if not 'no other bags' in part:
                sp = part.strip().split(' ')
                bags[color][' '.join(sp[1:3])] = int(sp[0])
            else:
                bags[color] = {}
    

Now I just need to recursively go through each bag, checking if it can hold a
shiny gold bag, and if not, checking if any of it’s children can (or their
children, etc).

    
    
    def can_hold(in_color, out_color):
        if in_color in str(bags[out_color]):
            return True
        return any([can_hold(in_color, b)for b in bags[out_color]])
    
    part1 = sum([can_hold('shiny gold', bag) for bag in bags])
    print(f'Part 1: {part1}')
    

The answer is a loop over all bag colors and counting the number that return
true.

One thing I noticed is that this hung for a fraction of a section while
running. The recursive loop is going to make a ton of repetitve calls. This is
where the `lru_cache` decorator can pay huge benefits. It will save the return
value from a call with given arguments, and if that same call is made again,
return it without running the code again. I figured (incorrectly) that
something more computationally intensive was coming in part two.

Just running the code as shown above takes about 0.3 seconds:

    
    
    $ time python3 day7.py 07-puzzle_input.txt 
    Part 1: 274
    
    real    0m0.295s
    user    0m0.291s
    sys     0m0.004s
    

Adding the `@lru_cache(maxsize=256)` decorator to the `can_hold` function
reduces that by a factor of ten:

    
    
    $ time python3 day7.py 07-puzzle_input.txt 
    Part 1: 274
    
    real    0m0.023s
    user    0m0.023s
    sys     0m0.000s
    

### Part 2

For part two, I need to count the number of bags that need to go inside a
given bag. I’ll end up with a one line list comprehension, but to get there,
I’ll look at the bags that the given bag must hold. Looping over those, I’ll
add to my total the number of those bags required and then that number times
the number of bags they must hold.

Based on my `bags` object above, that comes out to:

    
    
    def num_inside(color):
        return sum([bags[color][b] * (1 + num_inside(b)) for b in bags[color]])
    

For each bag, I get the number required and the number of bags in it, and sum
it all up.

No need for caching here. It shouldn’t call the function with the same input
that many times in this case.

### Final Code

    
    
    #!/usr/bin/env python3
    
    import sys
    from collections import defaultdict
    from functools import lru_cache
    
    
    with open(sys.argv[1], "r") as f:
        rules = f.readlines()
    
    bags = defaultdict(dict)
    
    for rule in rules:
        parts = rule.split(" ")
        color = " ".join(parts[:2])
        in_parts = " ".join(parts[4:]).split(",")
        for part in in_parts:
            if not "no other bags" in part:
                sp = part.strip().split(" ")
                bags[color][" ".join(sp[1:3])] = int(sp[0])
            else:
                bags[color] = {}
    
    
    @lru_cache(maxsize=256)
    def can_hold(in_color, out_color):
        if in_color in str(bags[out_color]):
            return True
        return any([can_hold(in_color, b) for b in bags[out_color]])
    
    
    def num_inside(color):
        return sum([bags[color][b] * (1 + num_inside(b)) for b in bags[color]])
    
    
    part1 = sum([can_hold("shiny gold", bag) for bag in bags])
    print(f"Part 1: {part1}")
    print(f'Part 2: {num_inside("shiny gold")}')
    

After the caching, this runs basically instantly:

    
    
    $ time python3 day7.py 07-puzzle_input.txt
    Part 1: 274
    Part 2: 158730
    
    real    0m0.034s
    user    0m0.034s
    sys     0m0.000s
    

[« Day6](/adventofcode2020/6)[Day8 »](/adventofcode2020/8)

[](/adventofcode2020/7)

