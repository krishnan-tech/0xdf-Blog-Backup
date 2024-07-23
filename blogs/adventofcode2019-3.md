# Advent of Code 2019: Day 3

[ctf](/tags#ctf ) [advent-of-code](/tags#advent-of-code )
[python](/tags#python )  
  
Dec 3, 2019

  * [Day1](/adventofcode2019/1)
  * [Day2](/adventofcode2019/2)
  * Day3
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
  * [Day14](/adventofcode2019/14)

![](https://0xdfimages.gitlab.io/img/aoc2019-3-cover.png)

I always start to struggle when AOC moves into spatial challenges, and this is
where the code starts to get a bit ugly. In this challenge, I have to think
about two wires moving across a coordinate plane, and look for positions where
they intersect. Then I’ll score each intersection, first by Manhattan distance
to the origin, and then by total number of steps from the origin along both
wires, and return the minimum.

## Challenge

The puzzle can be found [here](https://adventofcode.com/2019/day/3). I’m given
two lines of input, where each is a series of moves with a direct (up, down,
left, right) and a distance. I’m asked to find where the two wires cross. For
the first part, I’ll return the crossing with the shortest Manhattan distance
to the origin. For the second part, I’ll return the intersection with the
fewest steps back to the origin combined for the two wires.

## Solution

### Part 1

I decided that for each wire, I would take the list of moves and convert it
into two lists, `vertical_segments` and `horizontal_segments`. For the
`vertical_segments`, I’ll store a segment as `(x, (y1, y2))`, and for
`horizontal_segments`, `(y, (x1, x2))`. To see if two segments cross, I can
simply check that `v[1][0] < h[0] < v[1][1] and h[1][0] < v[0] < h[1][1]`.

On my first attempt, I didn’t differentiate between the two wires, just
finding all segments, and looking for crossings. This worked for the initial
example input, but in the second example, it didn’t match the given
expectation of 159. The program produced the following output (with some debug
printing on to identify the intersections and their distances):

    
    
    $ ./day3.py 03-test_input-1.txt
    intersection: 158,4 162
    intersection: 158,11 169
    intersection: 158,-12 170
    intersection: 146,11 157
    intersection: 146,46 192
    intersection: 155,4 159
    intersection: 155,11 166
    Part 1: 157 
    

The correct answer is in the list, but there’s extra intersections, including
one with a lower distance than the expected answer. That tells me that I need
to only consider when the two wires cross, and not when a wire crosses itself.

I updated the code (and again, this isn’t pretty) and got a working result:

    
    
    #!/usr/bin/env python3
    
    import sys
    from collections import defaultdict
    
    dir_key = {"R": 1, "U": 1, "L": -1, "D": -1}
    vertical = ["U", "D"]
    
    def wire_rel_to_abs(wire):
    
        vertical_segments = []
        horizontal_segments = []
        x,y = 0,0
        for w in wire:
            if w[0] in vertical:
                delta = dir_key[w[0]] * int(w[1:])
                vertical_segments.append(((x,sorted((y,y+delta)))))
                y += delta
            else:
                delta = dir_key[w[0]] * int(w[1:])
                horizontal_segments.append(((y,sorted((x,x+delta)))))
                x += delta
        return vertical_segments, horizontal_segments
    
    
    def check_intersect(verts, hors):
        intersects = []
        for v in verts:
            for h in hors:
                if h[1][0] < v[0] < h[1][1] and v[1][0] < h[0] < v[1][1]:
                    intersects.append((v[0],h[0]))
        return intersects
    
    
    def min_manhattan_dist(points):
        min_dist = abs(points[0][0]) + abs(points[0][1])
        for p in points[1:]:
            dist = abs(p[0]) + abs(p[1])
            min_dist = min(min_dist, dist)
        return min_dist
    
    
    with open(sys.argv[1], 'r') as f:
        wires = [x.strip().split(',') for x in f.readlines()]
    
    verts1, hors1 = wire_rel_to_abs(wires[0])
    verts2, hors2 = wire_rel_to_abs(wires[1])
    
    
    min_dist = None
    intersections = check_intersect(verts1, hors2)
    intersections.extend(check_intersect(verts2, hors1))
    print(f"Part 1: {min_manhattan_dist(intersections)}")
    

Basically I get two sets of segments, and then run `check_intersect` for each
vertical set of segments on the other wire’s horizontal segments. Once I have
the list of intersections, I can run over them to find the minimum Manhattan
distance.

When I run this, I get the result:

    
    
    $ time ./day3.py 03-puzzle_input.txt 
    Part 1: 260
    
    real    0m0.050s
    user    0m0.039s
    sys     0m0.011s
    

I’m still watching the time of execution, but this is instant.

### Part 2

Now the metric for each intersection is changing, from a simple Manhattan
distance to the sum of the number of steps along each wire to reach the
intersection point. I suspect there’s a better way to do this, but I just
walked each wire again, this time checking each point along the wire, and if
it was an intersection, saving the number of steps.

    
    
    intersect_delay = defaultdict(int)
    for wire in wires:
        x,y = 0,0
        steps = 0
        for w in wire:
            for _ in range(int(w[1:])):
                if w[0] in vertical:
                    y += dir_key[w[0]]
                else:
                    x += dir_key[w[0]]
                steps += 1
                if x == 5 and y == 6:
                    z = 1
                if (x,y) in intersections:
                    intersect_delay[(x,y)] += steps
    
    print(f"Part 2: {intersect_delay[min(intersect_delay, key=lambda k: intersect_delay[k])]}")
    

I’ll use a `defaultdict` to store the steps for each intersection, so that I
don’t have to check if the key exists when I want to add the steps to an
intersection.

To find the minimum, I’ll use `min` with the `key` parameter basically saying
to get the value of the item. Without the `key` parameter, it would return the
minimum dictionary key, not the value.

When I run this, it does take just over a second to run:

    
    
    $ time ./day3.py 03-puzzle_input.txt 
    Part 1: 260
    Part 2: 15612
    
    real    0m1.118s
    user    0m1.110s
    sys     0m0.008s
    

That’s not too long, so I’m still in the phase where I can afford to make
brute force decisions like re-walking the each wire.

## Final Code

    
    
    #!/usr/bin/env python3
    
    import sys
    from collections import defaultdict
    
    dir_key = {"R": 1, "U": 1, "L": -1, "D": -1}
    vertical = ["U", "D"]
    
    def wire_rel_to_abs(wire):
    
        vertical_segments = []
        horizontal_segments = []
        x,y = 0,0
        for w in wire:
            if w[0] in vertical:
                delta = dir_key[w[0]] * int(w[1:])
                vertical_segments.append(((x,sorted((y,y+delta)))))
                y += delta
            else:
                delta = dir_key[w[0]] * int(w[1:])
                horizontal_segments.append(((y,sorted((x,x+delta)))))
                x += delta
        return vertical_segments, horizontal_segments
    
    
    def check_intersect(verts, hors):
        intersects = []
        for v in verts:
            for h in hors:
                if h[1][0] < v[0] < h[1][1] and v[1][0] < h[0] < v[1][1]:
                    intersects.append((v[0],h[0]))
        return intersects
    
    
    def min_manhattan_dist(points):
        min_dist = abs(points[0][0]) + abs(points[0][1])
        for p in points[1:]:
            dist = abs(p[0]) + abs(p[1])
            min_dist = min(min_dist, dist)
        return min_dist
    
    
    with open(sys.argv[1], 'r') as f:
        wires = [x.strip().split(',') for x in f.readlines()]
    
    verts1, hors1 = wire_rel_to_abs(wires[0])
    verts2, hors2 = wire_rel_to_abs(wires[1])
    
    
    min_dist = None
    intersections = check_intersect(verts1, hors2)
    intersections.extend(check_intersect(verts2, hors1))
    print(f"Part 2: {min_manhattan_dist(intersections)}")
    
    intersect_delay = defaultdict(int)
    for wire in wires:
        x,y = 0,0
        steps = 0
        for w in wire:
            for _ in range(int(w[1:])):
                if w[0] in vertical:
                    y += dir_key[w[0]]
                else:
                    x += dir_key[w[0]]
                steps += 1
                if x == 5 and y == 6:
                    z = 1
                if (x,y) in intersections:
                    intersect_delay[(x,y)] += steps
    
    print(f"Part 2: {intersect_delay[min(intersect_delay, key=lambda k: intersect_delay[k])]}")
    

[« Day2](/adventofcode2019/2)[Day4 »](/adventofcode2019/4)

[](/adventofcode2019/3)

