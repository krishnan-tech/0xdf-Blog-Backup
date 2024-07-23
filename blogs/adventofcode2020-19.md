# Advent of Code 2020: Day 19

[ctf](/tags#ctf ) [advent-of-code](/tags#advent-of-code )
[python](/tags#python )  
  
Dec 19, 2020

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
  * [Day16](/adventofcode2020/16)
  * [Day17](/adventofcode2020/17)
  * [Day18](/adventofcode2020/18)
  * Day19
  * [Day20](/adventofcode2020/20)
  * [Day21](/adventofcode2020/21)
  * [Day22](/adventofcode2020/22)
  * [Day23](/adventofcode2020/23)
  * [Day24](/adventofcode2020/24)
  * [Day25](/adventofcode2020/25)

![](https://0xdfimages.gitlab.io/img/aoc2020-19-cover.png)

Another day with a section of convoluted validation rules and a series of
items to be validated. Today’s rules apply to a string, and I’ll actually use
a recursive algorithm to generate a single regex string that can then be
applied to each input to check validity. It gets slightly more difficult in
the second part, where loops are introduced into the rules. In order to work
around this, I’ll guess at a depth at which I can start to ignore further
loops.

## Challenge

The puzzle can be found [here](https://adventofcode.com/2020/day/19). The
first part of the input are rules representing the order of characters in a
valid string. The example input they give is:

    
    
    0: 1 2
    1: "a"
    2: 1 3 | 3 1
    3: "b"
    

So to match rule 0, the string must start with something that matches rule 1
and then rule 2. Rule 1 is an “a”, so the string must start with an “a”. Rule
two is rule 1 and then rule 3 OR rule 3 and then rule 1, or “ab” or “ba”. So
rule 0 matches on “aab” and “aba”.

The second part of the input is a series of strings of “a” and “b” to check.
The solution is the number of strings that match.

In part one, there are no loops. In part two, two rules update to add loops.
Because the loops are in an OR arrangement, they can loop anywhere from zero
to infinite times.

## Solution

### Part 1

First I parsed the rules into a dictionary

    
    
    with open(sys.argv[1], "r") as f:
        rules_raw, msgs = f.read().split("\n\n")
    
    rules = {}
    for rule in rules_raw.split("\n"):
        num, r = rule.split(": ")
        rules[num] = [s.split() for s in r.split(" | ")]
    

This will produce a dictionary that has an array for each number, and given
the nature of the rules, that array will have one or two values. The values
are also array, either of a character (`"a"`) or of ints (`["42", "16"]`).

Next I’ll make a function to recursively walk the rules object starting with
“0” and build a regex from it:

    
    
    #!/usr/bin/env python3
    
    import re
    import sys
    
    
    def gen_regex(r="0"):
        if depth == 0:
            return ""
        if rules[r][0][0].startswith('"'):
            return rules[r][0][0].strip('"')
        return "(" + "|".join(["".join([gen_regex(sub) for sub in subrule]) for subrule in rules[r]]) + ")"
    

The output will look something like:

    
    
    >>> gen_regex('5')
    '((aa)b|((a|b)b|ba)a)'
    

With that in place, now I can compile the reges and then loop over each input,
counting the matches:

    
    
    r1 = re.compile(gen_regex())
    res = [r1.fullmatch(msg) for msg in msgs.split("\n")]
    print(f"Part 1: {len([x for x in res if x])}")
    

### Part 2

In part two, I’m given two rules with loops in them:

    
    
    8: 42 | 42 8
    11: 42 31 | 42 11 31
    

I was tempted to just add updates for these two rules into the `get_regex`
function. With “8”, it’s actually pretty easy. This is one or more “42”s,
which in regex is written `(42)+`. (where 42 is actually a string).

The challenge comes with “11”. If 42 is just “a” and 31 is just “b”, then
“ab”, “aabb”, “aaabbb”, would all match. There’s no good way to do this with
basic regex. Instead, I made another observation - as the regex string grows,
the minimum length of a string it could match also grows.

The longest message in the puzzle input is 96 characters:

    
    
    >>> max([len(x) for x in msgs.strip().split('\n')])
    96
    

There is some length at which it will no longer match anything. I could start
doing some math to figure out where the depth starts to make it no longer
useful, but I’ll just guess that 25 is enough, and add that as a parameters to
the `get_regex` function:

    
    
    def gen_regex(r="0", depth=25):
        if depth == 0:
            return ""
        if rules[r][0][0].startswith('"'):
            return rules[r][0][0].strip('"')
        return "(" + "|".join(["".join([gen_regex(sub, depth - 1) for sub in subrule]) for subrule in rules[r]]) + ")"
    

When the loop gets too long, it just quits and returns the empty string.

Now I just need to update the rule set with these new looping rules and the
rest looks the same:

    
    
    rules["8"] = [["42"], ["42", "8"]]
    rules["11"] = [["42", "31"], ["42", "11", "31"]]
    
    r2 = re.compile(gen_regex())
    res = [r2.fullmatch(msg) for msg in msgs.split("\n")]
    print(f"Part 2: {len([x for x in res if x])}")
    

### Final Code

This is all relatively fast:

    
    
    $ time python3 day19.py 19-puz
    Part 1: 139
    Part 2: 289
    
    real    0m0.407s
    user    0m0.362s
    sys     0m0.044s
    

This works. I did some experimenting with different starting depths in a loop,
and found that 15 is enough to get the correct solution for my puzzle input.
And it cuts the overall time in half:

    
    
    $ time python3 day19.py 19-puz
    Part 1: 139
    Part 2: 289
    
    real    0m0.198s
    user    0m0.186s
    sys     0m0.012s
    
    
    
    #!/usr/bin/env python3
    
    import re
    import sys
    
    
    def gen_regex(r="0", depth=15):
        if depth == 0:
            return ""
        if rules[r][0][0].startswith('"'):
            return rules[r][0][0].strip('"')
        return "(" + "|".join(["".join([gen_regex(sub, depth - 1) for sub in subrule]) for subrule in rules[r]]) + ")"
    
    
    with open(sys.argv[1], "r") as f:
        rules_raw, msgs = f.read().split("\n\n")
    
    rules = {}
    for rule in rules_raw.split("\n"):
        num, r = rule.split(": ")
        rules[num] = [s.split() for s in r.split(" | ")]
    
    r1 = re.compile(gen_regex())
    res = [r1.fullmatch(msg) for msg in msgs.split("\n")]
    print(f"Part 1: {len([x for x in res if x])}")
    
    rules["8"] = [["42"], ["42", "8"]]
    rules["11"] = [["42", "31"], ["42", "11", "31"]]
    
    r2 = re.compile(gen_regex())
    res = [r2.fullmatch(msg) for msg in msgs.split("\n")]
    print(f"Part 2: {len([x for x in res if x])}")
    

[« Day18](/adventofcode2020/18)[Day20 »](/adventofcode2020/20)

[](/adventofcode2020/19)

