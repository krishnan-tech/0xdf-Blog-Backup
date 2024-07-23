# Advent of Code 2019: Day 6

[ctf](/tags#ctf ) [advent-of-code](/tags#advent-of-code )
[python](/tags#python ) [recursion](/tags#recursion )
[defaultdict](/tags#defaultdict )  
  
Dec 6, 2019

  * [Day1](/adventofcode2019/1)
  * [Day2](/adventofcode2019/2)
  * [Day3](/adventofcode2019/3)
  * [Day4](/adventofcode2019/4)
  * [Day5](/adventofcode2019/5)
  * Day6
  * [Day7](/adventofcode2019/7)
  * [Day8](/adventofcode2019/8)
  * [Day9](/adventofcode2019/9)
  * [Day10](/adventofcode2019/10)
  * [Day11](/adventofcode2019/11)
  * [Day12](/adventofcode2019/12)
  * [Day13](/adventofcode2019/13)
  * [Day14](/adventofcode2019/14)

![](https://0xdfimages.gitlab.io/img/aoc2019-6-cover.png)

This was a fun challenge, because it seemed really hard at first, but once I
figured out how to think about it, it was quite simple. I’m given a set of
pairings, each of which contains two objects, the second orbits around the
first. I’ll play with counting the number of orbits going on, as well as
working a path through the orbits. This was the first time I brought out
recurrisive programming this year, and it really fit well.

## Challenge

The puzzle can be found [here](https://adventofcode.com/2019/day/6). The idea
is that something orbits around it’s parent, and all parents of the parent.
For part one, I’m simply asked to count the orbits. So if A orbits B, and B
orbits C, then there are 3: A around B, B around C, and A around C. For part
two, I’m given a start and an end, and asked to figure out how many hops
between the two spots.

## Solution

### Part 1

This looked at first like a spatial problem, but it’s really not. The picture
they give for an example really just shows a tree:

    
    
            G - H       J - K - L
           /           /
    COM - B - C - D - E - F
                   \
                    I
    

I’ll notice that each time I add a node, the number of orbits added is just
the depth of the node on the tree. Adding a child to COM just adds one. Adding
a child to B adds two, B and COM.

So if I can just track each node’s children, I can walk the three and sum each
node’s depth to get the total number of nodes. that code looks like this:

    
    
    #!/usr/bin/env python3
    
    import sys
    from collections import defaultdict
    
    
    def count_orbits(orbit, depth):
        return depth + sum([count_orbits(o, depth + 1) for o in orbits[orbit]])
    
    
    with open(sys.argv[1], "r") as f:
        orbit_input = [l.strip().split(")") for l in f.readlines()]
    
    
    orbits = defaultdict(list)
    for orbit in orbit_input:
        orbits[orbit[0]].append(orbit[1])
    
    
    print(f"Part 1: {count_orbits('COM', 0)}")
    

First, I walk through my input list and convert it into dictionary of lists,
such that for each node as a key, the value is the child nodes.

Then I use this `count_orbits` function to add the depth of the current node,
plus the sum of the depths of all the child nodes. If a node has no children,
it just returns its depth.

This works nicely:

    
    
    $ time ./day6.py 06-puzzle_input.txt 
    Part 1: 130681
    
    real    0m0.022s
    user    0m0.015s
    sys     0m0.007s
    

### Part 2

In part two, I’ll no longer just need to track from parent to child to walk
the tree. Now I need to be able to explore from a child back to a parent. I’ll
create a second structure for this, `orbits2`, this time which is a
`defaultdict` of sets (because I don’t need duplicates and will have them).
For each pairing of A orbits B, I’ll add A to B’s list, and B to A’s list.
That way each node knows of all it’s neighbors. I’ll also track the `YOU` node
that gives me the starting spot:

    
    
    orbits = defaultdict(list)
    orbits2 = defaultdict(set)
    for orbit in orbit_input:
        orbits[orbit[0]].append(orbit[1])
        orbits2[orbit[1]].add(orbit[0])
        orbits2[orbit[0]].add(orbit[1])
        if orbit[1] == "YOU":
            start = orbit[0]
    

I’ll use a similar recursive strategy, this time walking both directions in
search of the end, `SAN`. I’ll also track the previous nodes visited on that
walk. It doesn’t seem there are loops, but I’ll track the entire path to be
sure. If a node is a neighbor of the current node, but also in the previous
list, I don’t need to head back that way.

    
    
    def find_path(orbit, prev, count):
        if "SAN" in orbits[orbit]:
            print(f"Part 2: {count}")
            sys.exit()
        for o in orbits2[orbit]:
            if o in prev:
                continue
            find_path(o, prev + [o], count + 1)
    

Putting that together, it still runs fast:

    
    
    $ time ./day6.py 06-puzzle_input.txt 
    Part 1: 130681
    Part 2: 313
    
    real    0m0.028s
    user    0m0.024s
    sys     0m0.004s
    

## Final Code

    
    
    #!/usr/bin/env python3
    
    import sys
    from collections import defaultdict
    
    
    def count_orbits(orbit, depth):
        return depth + sum([count_orbits(o, depth + 1) for o in orbits[orbit]])
    
    
    def find_path(orbit, prev, count):
        if "SAN" in orbits[orbit]:
            print(f"Part 2: {count}")
            sys.exit()
        for o in orbits2[orbit]:
            if o in prev:
                continue
            find_path(o, prev + [o], count + 1)
    
    
    with open(sys.argv[1], "r") as f:
        orbit_input = [l.strip().split(")") for l in f.readlines()]
    
    
    orbits = defaultdict(list)
    orbits2 = defaultdict(set)
    for orbit in orbit_input:
        orbits[orbit[0]].append(orbit[1])
        orbits2[orbit[1]].add(orbit[0])
        orbits2[orbit[0]].add(orbit[1])
        if orbit[1] == "YOU":
            start = orbit[0]
    
    
    print(f"Part 1: {count_orbits('COM', 0)}")
    find_path(start, ["YOU"], 0)
    

[« Day5](/adventofcode2019/5)[Day7 »](/adventofcode2019/7)

[](/adventofcode2019/6)

