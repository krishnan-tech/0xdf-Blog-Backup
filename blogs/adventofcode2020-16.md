# Advent of Code 2020: Day 16

[ctf](/tags#ctf ) [advent-of-code](/tags#advent-of-code )
[python](/tags#python )  
  
Dec 16, 2020

  * [Day1](/adventofcode2020/1)
  * [Day2](/adventofcode2020/2)
  * [Day3](/adventofcode2020/3)
  * [Day4](/adventofcode2020/4)
  * [Day5](/adventofcode2020/5)
  * [Day6](/adventofcode2020/6)
  * [Day7](/adventofcode2020/7)
  * [Day8](/adventofcode2020/8)
  * [Day9](/adventofcode2020/9)
  * [Day10](/adventofcode2020/10)
  * [Day11](/adventofcode2020/11)
  * [Day12](/adventofcode2020/12)
  * [Day13](/adventofcode2020/13)
  * [Day14](/adventofcode2020/14)
  * [Day15](/adventofcode2020/15)
  * Day16
  * [Day17](/adventofcode2020/17)
  * [Day18](/adventofcode2020/18)
  * [Day19](/adventofcode2020/19)
  * [Day20](/adventofcode2020/20)
  * [Day21](/adventofcode2020/21)
  * [Day22](/adventofcode2020/22)
  * [Day23](/adventofcode2020/23)
  * [Day24](/adventofcode2020/24)
  * [Day25](/adventofcode2020/25)

![](https://0xdfimages.gitlab.io/img/aoc2020-16-cover.png)

Day 16 was an interesting one to think about, as the algorithm for solving it
wasn’t obvious. It wasn’t the case like some of the previous ones where there
was an intuitive way to think about it but it would take too long. It was more
a case of wrapping your head around the problem and how to organize the data
so that you could match keys to values using validity rules and a bunch of
examples. I made a guess that the data might clean up nicely in a certain way,
and when it did, it made the second part much easier.

## Challenge

The puzzle can be found [here](https://adventofcode.com/2020/day/16). The
puzzle input will have three sections. First, there’s a list of fields with
rules for what number are valid for a given field. I’ll notice (though it’s
not explicitly stated) that each rule in the examples and my puzzle input is
of the format `a-b or c-d`. Then, there’s a list of numbers (the same length
as the number of fields) which represents my ticket. Finally, there’s a bunch
of other lists of numbers which represent other tickets I see. For example:

    
    
    class: 0-1 or 4-19
    row: 0-5 or 8-19
    seat: 0-13 or 16-19
    
    your ticket:
    11,12,13
    
    nearby tickets:
    3,9,18
    15,1,5
    5,14,9
    

In part one, I need to collect the numbers across all the nearby tickets that
couldn’t be valid in any field, and sum them.

In part two, I need to use the remaining valid tickets to determine which
field names match to which index in the list of numbers that represent a
ticket.

## Solution

### Part 1

This one took a while to wrap my head around. I went down some rabbit holes
over complicating it at first, thinking I might need to look for a case where
the individual number was ok but there weren’t enough valid fields (say there
were two fours, but only one field that could contain a four). But on re-
reading, I just need to look for values that aren’t valid for any field.

The first step is organizing the input. I’ll read the rules into a dictionary
of lists, where the key is the field name and the value is a list of integres
such that a valid number is `v[0] <= i <= v[1] or v[2] <= i <= v[3]`. I’ll
also get it so that `others` is a list of lists of ints, each list being a
ticket.

    
    
    rules_raw, myticket, others_raw = [x.split('\n') for x in puzin.split('\n\n')]
    
    rules = {}
    for rule in rules_raw:
        search = re.match(r'(.+): (\d+)-(\d+) or (\d+)-(\d+)', rule)
        name = search.group(1)
        nums = list(map(int, search.groups()[1:]))
        rules[name] = nums
    
    others = [list(map(int, o.split(','))) for o in others_raw[1:]]
    

Next I need a function that takes an int and returns if it is valid for and
field:

    
    
    def is_valid_field(i):
        return any([v[0] <= i <= v[1] or v[2] <= i <= v[3] for v in rules.values()])
    

This will loop over the set of rules, for each getting the array of four ints.
For each, it will check if `i` is valid, and if any of those return true, it
will return true.

Now I can find the rate by nested looping over each value in each of the other
tickets and keeping only the values that are invalid:

    
    
    ticket_scanning_error_rate = sum([o for other in others for o in other if not is_valid_field(o)])
    print(f'Part 1: {ticket_scanning_error_rate}')
    

### Part 2

For part two, first I’ll get a list of just the valid tickets:

    
    
    valid_others = [other for other in others if all([is_valid_field(o, rules) for o in other])]
    

I spent a while thinking about a recursive algorithm that would loop over each
rule and each index, and each time it found a rule that could apple to that
position, remove both of those from the list and call the function again. I
think this is possible, but it’s complicated.

I took a break and considered that it’s possible that there’s a rule for which
only one column is valid. And then there’s another rule for which only two
positions are valid, and one was the position from the first rule. And so on.
And if this is the case, then I can just find all the possible indexes for
each rule, sort by length, and then work through the list. This code checks
that:

    
    
    possibles = {}
    for name, bounds in rules.items():
        possibles[name] = [i for i in range(len(rules)) if all([is_valid_field(t[i], {name: bounds}) for t in valid_others])]
    

The result shows that what I had hoped is true:

    
    
    >>> sorted(possibles.items(), key=lambda x: len(x[1]))
    [('arrival platform', [11]), ('duration', [10, 11]), ('arrival station', [7, 10, 11]), ('wagon', [7, 10, 11, 12]), ('price', [7, 10, 11, 12, 18]), ('class', [4, 7, 10, 11, 12, 18]), ('departure time', [4, 7, 10, 11, 12, 16, 18]), ('departure date', [4, 6, 7, 10, 11, 12, 16, 18]), ('departure location', [4, 6, 7, 10, 11, 12, 16, 18, 19]), ('departure track', [2, 4, 6, 7, 10, 11, 12, 16, 18, 19]), ('departure platform', [2, 4, 6, 7, 10, 11, 12, 15, 16, 18, 19]), ('departure station', [2, 4, 6, 7, 10, 11, 12, 15, 16, 17, 18, 19]), ('train',
    [0, 2, 4, 6, 7, 10, 11, 12, 15, 16, 17, 18, 19]), ('row', [0, 2, 4, 6, 7, 8, 10, 11, 12, 15, 16, 17, 18, 19]), ('arrival location', [0, 1, 2, 4, 6, 7, 8, 10, 11, 12, 15, 16, 17, 18, 19]), ('zone', [0, 1, 2, 4, 6, 7, 8, 10, 11, 12, 14, 15, 16, 17, 18, 19]), ('arrival track', [0, 1, 2, 4, 5, 6, 7, 8, 10, 11, 12, 14, 15, 16, 17, 18, 19]), ('type', [0, 1, 2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 15, 16, 17, 18, 19]), ('seat', [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 15, 16, 17, 18, 19]), ('route', [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19])]
    

So I’ll use the loop above, and then loop over a sorted instance of it
creating a dictionary that goes from index to name:

    
    
    matched = {}
    
    for name, possibilities in sorted(possibles.items(), key=lambda x: len(x[1])):
        index = [i for i in possibilities if i not in matched]
        assert len(index) == 1
        matched[index[0]] = name
    

Now it’s just a matter of getting the size values from my ticket that have
‘departure’ in their name and finding the product (I’ve also created a helper
`product` function to make that more readable):

    
    
    dep_prod = product([x for i, x in enumerate(myticket) if "departure" in matched[i]])
    print(f"Part 2: {dep_prod}")
    

### Final Code

This is not computationally intensive, and runs instantly:

    
    
    $ time python3 day16.py 16-puz
    Part 1: 21996
    Part 2: 650080463519
    
    real    0m0.115s
    user    0m0.111s
    sys     0m0.004s
    
    
    
    #!/usr/bin/env python3
    
    import re
    import sys
    from functools import reduce
    
    
    def is_valid_field(i, rules):
        return any([v[0] <= i <= v[1] or v[2] <= i <= v[3] for v in rules.values()])
    
    
    def product(array):
        return reduce((lambda x, y: x * y), array)
    
    
    with open(sys.argv[1], "r") as f:
        puzin = f.read().strip()
    
    rules_raw, myticket_raw, others_raw = [x.split("\n") for x in puzin.split("\n\n")]
    
    rules = {}
    for rule in rules_raw:
        search = re.match(r"(.+): (\d+)-(\d+) or (\d+)-(\d+)", rule)
        name = search.group(1)
        nums = list(map(int, search.groups()[1:]))
        rules[name] = nums
    
    others = [list(map(int, o.split(","))) for o in others_raw[1:]]
    myticket = list(map(int, myticket_raw[1].split(",")))
    
    ticket_scanning_error_rate = sum([o for other in others for o in other if not is_valid_field(o, rules)])
    print(f"Part 1: {ticket_scanning_error_rate}")
    
    
    valid_others = [other for other in others if all([is_valid_field(o, rules) for o in other])]
    
    
    possibles = {}
    for name, bounds in rules.items():
        possibles[name] = [i for i in range(len(rules)) if all([is_valid_field(t[i], {name: bounds}) for t in valid_others])]
    
    matched = {}
    
    for name, possibilities in sorted(possibles.items(), key=lambda x: len(x[1])):
        index = [i for i in possibilities if i not in matched]
        assert len(index) == 1
        matched[index[0]] = name
    
    dep_prod = product([x for i, x in enumerate(myticket) if "departure" in matched[i]])
    print(f"Part 2: {dep_prod}")
    

[« Day15](/adventofcode2020/15)[Day17 »](/adventofcode2020/17)

[](/adventofcode2020/16)

