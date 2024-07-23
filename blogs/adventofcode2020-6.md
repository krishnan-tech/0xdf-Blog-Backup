# Advent of Code 2020: Day 6

[ctf](/tags#ctf ) [advent-of-code](/tags#advent-of-code )
[python](/tags#python )  
  
Dec 6, 2020

  * [Day1](/adventofcode2020/1)
  * [Day2](/adventofcode2020/2)
  * [Day3](/adventofcode2020/3)
  * [Day4](/adventofcode2020/4)
  * [Day5](/adventofcode2020/5)
  * Day6
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
  * [Day19](/adventofcode2020/19)
  * [Day20](/adventofcode2020/20)
  * [Day21](/adventofcode2020/21)
  * [Day22](/adventofcode2020/22)
  * [Day23](/adventofcode2020/23)
  * [Day24](/adventofcode2020/24)
  * [Day25](/adventofcode2020/25)

![](https://0xdfimages.gitlab.io/img/aoc2020-6-cover.png)

Day 6 was another text parsing challenge, breaking the input into groups and
then counting across the users within each group. Both parts were similar,
with the first counting if any user said yes to a given question, and the
latter if every user said yes to a given question. Python makes this a breeze
either way.

## Challenge

The puzzle can be found [here](https://adventofcode.com/2020/day/6). I’m given
text again representing answers to 26 questions from people. Each person’s
answers are on one line, and each group of people is separated by an empty
line. In part one, I’m asked to look at each group and count the number of
questions that were included by any one member, and sum that count across all
groups. In part two, I’m asked to count a question only if every member said
yes.

## Solution

### Part 1

This is another one where Python makes it too easy. Once I break the text into
groups (using `split('\n\n')`), I just need to remove the newlines and then
get the set (list of unique items) of characters that remain. The length of
that set is the count for the group. So loop over all groups getting that
length, and then sum it to get the total:

    
    
    #!/usr/bin/env python3
    
    import sys
    
    
    with open(sys.argv[1], "r") as f:
        answers = f.read().strip().split("\n\n")
    
    part1 = sum([len(set(ans.replace("\n", ""))) for ans in answers])
    print(f"Part 1: {part1}")
    

### Part 2

For part two, I need to look at each member of the group to ensure they
included the answer before counting it. I’ll loop through the characters a-z,
and check that that character is in all the members for the group, and if so,
count it. I’ll just use one count across all groups, as I don’t need to track
the per group total:

    
    
    #!/usr/bin/env python3
    
    import string
    import sys
    
    
    with open(sys.argv[1], "r") as f:
        answers = f.read().strip().split("\n\n")
    
    part1 = sum([len(set(ans.replace("\n", ""))) for ans in answers])
    print(f"Part 1: {part1}")
    
    count = 0
    for ans in answers:
        ind_ans = ans.split("\n")
        for c in string.ascii_lowercase:
            count += all([c in a for a in ind_ans])
    
    print(f"Part 2: {count}")
    

These both solve instantly:

    
    
    $ time python3 day6.py 06-puzzle_input.txt 
    Part 1: 6534
    Part 2: 3402
    
    real    0m0.061s
    user    0m0.049s
    sys     0m0.012s
    

[« Day5](/adventofcode2020/5)[Day7 »](/adventofcode2020/7)

[](/adventofcode2020/6)

