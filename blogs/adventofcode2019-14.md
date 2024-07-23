# Advent of Code 2019: Day 14

[ctf](/tags#ctf ) [advent-of-code](/tags#advent-of-code )
[python](/tags#python ) [defaultdict](/tags#defaultdict )  
  
Dec 14, 2019

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
  * [Day13](/adventofcode2019/13)
  * Day14

![](https://0xdfimages.gitlab.io/img/aoc2019-14-cover.png)

Day 14 is all about stacking requirements and then working them to understand
the inputs required to get the output desired. I’ll need to organize my list
of reactions in such a way that I can work back from the desired end output to
how much ore is required to get there.

## Challenge

The puzzle can be found [here](https://adventofcode.com/2019/day/14). I’m
given a list of reactions that describe how various chemicals can be combined
to make other chemicals. For example:

    
    
    10 ORE => 10 A
    1 ORE => 1 B
    7 A, 1 B => 1 C
    7 A, 1 C => 1 D
    7 A, 1 D => 1 E
    7 A, 1 E => 1 FUEL
    

The challenge is to determine how much `ORE` I need to start with to get 1
`FUEL`.

In part 2, I’ll be given a large amount of `ORE`, and asked to figure out how
much `FUEL` it can produce. This isn’t just dividing by the amount of `ORE`
required to make 1 `FUEL`, because there are leftover chemicals after 1 is
created that can be used in the next.

## Solution

### Part 1

This challenge breaks into a couple parts. First, I need to read in the puzzle
input and translate it into a structure to easily reference. I’m going to be
looking at an output, and trying to determine how much input is needed, so
I’ll use the output as the dictionary key. For each output, I’ll have an `out`
which is the number that are produced, and an `in`, which is a dict of inputs
as keys and amounts required as values:

    
    
    with open(sys.argv[1], 'r') as f:
        reaction_lines = list(map(str.strip, f.readlines()))
    
    reactions = {}
    for r in reaction_lines:
        i, o = r.split(" => ")
        o_num, o_chem = o.split(" ")
        inputs = {}
        for in_str in i.split(", "):
            i_num, i_chem = in_str.split(" ")
            inputs[i_chem] = int(i_num)
        reactions[o_chem] = {"out": int(o_num), "in": inputs}
    

For example, the example about would produce:

    
    
    {'A': {'out': 2, 'in': {'ORE': 9}}, 'B': {'out': 3, 'in': {'ORE': 8}}, 'C': {'out': 5, 'in': {'ORE': 7}}, 'AB': {'out': 1, 'in': {'A': 3, 'B': 4}}, 'BC': {'out': 1, 'in': {'B': 5, 'C': 7}}, 'CA': {'out': 1, 'in': {'C': 4, 'A': 1}}, 'FUEL': {'out': 1, 'in': {'AB': 2, 'BC': 3, 'CA': 4}}}
    

Next, I’ll create a dictionary of needs, which starts with the thing I’m
trying to create, 1 `FUEL`:

    
    
    chem_needs = defaultdict(int, {'FUEL': 1})
    

I’ll also initialize a list of leftover chemicals. This happens when I need
three of something, but the recipe to make it creates four. I’ll make four,
use three, and have one left. I’ll also create an `ORE` counter as well:

    
    
    chem_have = defaultdict(int)
    ore = 0
    

Now I loop as long as there are items in the needs list. For each item, I find
out how to create it. If I have enough in the leftovers list (`chem_have`), I
subtract that many from the have list, delete the item from the needs list,
and continue the loop.

Otherwise, I’ll calculate the number more I need to create, and delete the
balance in the have list and the need list. Then I’ll go about determining the
inputs to make that many. First, I’ll find the number produced by one recipe,
and then determine how many reactions I need to perform. I’ll add the extras
to the have list. Then I’ll loop over the items required for that output and
add them to the need list, unless they are `ORE`, in which case I add to the
count needed.

    
    
    while chem_needs:
        item = list(chem_needs.keys())[0]
        if chem_needs[item] <= chem_have[item]:
            chem_have[item] -= chem_needs[item]
            del chem_needs[item]
            continue
    
        num_needed = chem_needs[item] - chem_have[item]
        del chem_have[item]
        del chem_needs[item]
        num_produced = reactions[item]["out"]
    
        if (num_needed / num_produced) == int(num_needed / num_produced):
            num_reactions = num_needed // num_produced
        else:
            num_reactions = (num_needed // num_produced) + 1
    
        chem_have[item] += (num_reactions * num_produced) - num_needed
        for chem in reactions[item]["in"]:
            if chem == "ORE":
                ore += reactions[item]["in"][chem] * num_reactions
            else:
                chem_needs[chem] += reactions[item]["in"][chem] * num_reactions
    
    print(f"Part 1: {ore}")
    

When it’s done, it prints the amount of `ORE` needed:

    
    
    $ time ./day14.py 14-puzzle_input.txt 
    Part 1: 136771
    
    real    0m0.054s
    user    0m0.049s
    sys     0m0.004s
    

### Part 2

For part 2, I need to think about how many `FUEL` I can make with
_1000000000000_ `ORE` (that’s 112). An initial guess might be that I could
take the `ORE` required to make 1 `FUEL` and divide a trillion by that. But
that’s not quite right, because as the lefover chemicals build, I’ll be able
to start getting extra `FUEL` out.

Rather than try to back calculate, I can use the work I’ve already done. I’ll
convert the code from part 1 that finds how much `ORE` is required for one
`FUEL` into a function, and have it take the number of `FUEL` as an input.

I’ll think about a range of possible numbers of `FUEL`. It has to be at least
a trillion divided by the number of `ORE` required to create one `FUEL`. I’ll
use a loop to find a upper bound by multiplying that lower bound by 10 until
it is over 112.

    
    
    low = 1e12 // ore_required(1)
    high = 10 * low
    
    while ore_required(high) < 1e12:
        low = high
        high = 10 * low
    

Now with an upper and lower bound in place, I’ll check how many `ORE` are
required for the midpoint, and compare it to 112. Then I can adjust my range,
until I know the most I can make without requiring more than 112.

    
    
    while low < high - 1:
        mid = (low + high) // 2
        ore = ore_required(mid)
        if ore < 1e12:
            low = mid
        elif ore > 1e12:
            high = mid
        else:
            break
    
    print(f"Part 2: {int(mid)}")
    

This all still runs basically instantly:

    
    
    $ time ./day14.py 14-puzzle_input.txt
    Part 1: 136771
    Part 2: 8193614
    
    real    0m0.059s
    user    0m0.050s
    sys     0m0.008s
    

## Final Code

    
    
    #!/usr/bin/env python3
    
    import sys
    from collections import defaultdict
    
    
    def ore_required(fuel=1):
        chem_needs = defaultdict(int, {"FUEL": fuel})
        chem_have = defaultdict(int)
        ore = 0
    
        while chem_needs:
            item = list(chem_needs.keys())[0]
            if chem_needs[item] <= chem_have[item]:
                chem_have[item] -= chem_needs[item]
                del chem_needs[item]
                continue
    
            num_needed = chem_needs[item] - chem_have[item]
            del chem_have[item]
            del chem_needs[item]
            num_produced = reactions[item]["out"]
    
            if (num_needed // num_produced) * num_produced == num_needed:
                num_reactions = num_needed // num_produced
            else:
                num_reactions = (num_needed // num_produced) + 1
            # print(num_needed, num_produced, num_reactions)
    
            chem_have[item] += (num_reactions * num_produced) - num_needed
            for chem in reactions[item]["in"]:
                if chem == "ORE":
                    ore += reactions[item]["in"][chem] * num_reactions
                else:
                    chem_needs[chem] += reactions[item]["in"][chem] * num_reactions
            # print(f'{ore} {chem_needs} {chem_have}')
    
        return ore
    
    
    with open(sys.argv[1], "r") as f:
        reaction_lines = list(map(str.strip, f.readlines()))
    
    reactions = {}
    for r in reaction_lines:
        i, o = r.split(" => ")
        o_num, o_chem = o.split(" ")
        inputs = {}
        for in_str in i.split(", "):
            i_num, i_chem = in_str.split(" ")
            inputs[i_chem] = int(i_num)
        reactions[o_chem] = {"out": int(o_num), "in": inputs}
    
    
    print(f"Part 1: {ore_required()}")
    
    low = 1e12 // ore_required()
    high = 10 * low
    
    while ore_required(high) < 1e12:
        low = high
        high = 10 * low
    
    while low < high - 1:
        mid = (low + high) // 2
        ore = ore_required(mid)
        if ore < 1e12:
            low = mid
        elif ore > 1e12:
            high = mid
        else:
            break
    
    print(f"Part 2: {int(mid)}")
    

[« Day13](/adventofcode2019/13)

[](/adventofcode2019/14)

