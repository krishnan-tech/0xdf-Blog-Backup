# Advent of Code 2020: Day 14

[ctf](/tags#ctf ) [advent-of-code](/tags#advent-of-code )
[python](/tags#python )  
  
Dec 14, 2020

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
  * Day14
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

![](https://0xdfimages.gitlab.io/img/aoc2020-14-cover.png)

Part one of day 14 looked to be some basic binary masking and manipulation.
But in part two, it got trickier, as now I need to handle Xs in the mask as
both 0 and 1, meaning that there would be 2num X results. I used a recursive
function to generate the list of indexes there.

## Challenge

The puzzle can be found [here](https://adventofcode.com/2020/day/14). The
puzzle input will have two types of lines, either defining a mask, or setting
a memory address:

    
    
    mask = XXXXXXXXXXXXXXXXXXXXXXXXXXXXX1XXXX0X
    mem[8] = 11
    mem[7] = 101
    mem[8] = 0
    

The mask can be changed throughout the input as it’s processed line by line.

In part one, I’m asked to apply the current mask to the input value, where an
X leaves the value unchanged, but a 0 or 1 force that value in that bit
location.

In part two, the mask applies to the address in mem, and with different rules.
0 means no change on the input, 1 forces a 1, and X means to consider both 0
and 1 in that slot. That means if there are n Xs in the bitmask, I’ll write
the value into 2n addresses.

In each part, I’m to find the sum of all the values in memory at the end of
the program.

## Solution

### Part 1

Just like the previous few days, this one was relatively straight forward.
I’ll read the lines in, and iterate over them. If it starts with `mask`, I’ll
update the mask. Otherwise, I’ll get the index and the value, update the value
with the mask, and write it to the index.

The only trick is figuring out how to apply the mask. I’ll keep two masks,
`m_or` and `m_and`. The first will have replace all the `X` with `0`, leaving
only the `1` bits. By applying this mask logical or the input, it will turn on
those 1 bits. The second is replaces all the `X` with `1`, leaving only the
original `0` as `0`. By applying this logical and, it will force those
original `0` to be `0`.

    
    
    mem = {}
    
    for inst in insts:
        if inst.startswith("mask"):
            mask_in = inst.split(" ")[2]
            m_or = int(mask_in.replace("X", "0"), 2)
            m_and = int(mask_in.replace("X", "1"), 2)
        elif inst.startswith("mem"):
            idx = int(inst.split("[")[1].split("]")[0])
            val = int(inst.split(" ")[2])
            mem[idx] = (val & m_and) | m_or
    
    print(f"Part 1: {sum([v for k,v in mem.items()])}")
    

This works to solve part one.

### Part 2

This is where it gets a bit trickier. The challenge is now that each X
represents both values, so there are 2count(‘X’) addresses to write to.

I decided to use a recursive function to get a list of indexes:

    
    
    def get_indexes(mask):
        try:
            firstx = mask.index("X")
            return get_indexes(mask[:firstx] + "0" + mask[firstx + 1 :]) + \
                   get_indexes(mask[:firstx] + "1" + mask[firstx + 1 :])
        except ValueError:
            return [int(mask, 2)]
    

I’ll try to get the index of the first `X` in the mask. If it doesn’t find
any, this will cause a `ValueError`, which I’ll catch and return the value.
Otherwise, I’ll call `get_indexes` with that first `X` both ways, and return
the result.

Building the input mask is a bit harder this time since I can’t make use or
math / decimal numbers with certain bit holding an `X`. Still, I’ll just
create a 36-bit binary string representation of the input index, and loop over
that zipped with the mask to generate the masked index:

    
    
    mem = {}
    
    for inst in insts:
        if inst.startswith("mask"):
            mask = inst.split(" ")[2]
        elif inst.startswith("mem"):
            idx = int(inst.split("[")[1].split("]")[0])
            val = int(inst.split(" ")[2])
            idx_mask = ""
            for m, i in zip(mask, f"{idx:036b}"):
                if m == "0":
                    idx_mask += i
                elif m == "1" or m == "X":
                    idx_mask += m
                else:
                    assert False
            idxs = get_indexes(idx_mask)
            for idx in idxs:
                mem[idx] = val
    

Then I’ll call `get_indexes` and set each of those locations to the value.

### Final Code

Script runs pretty quickly:

    
    
    $ time python3 day14.py 14-puzzle.txt
    Part 1: 14925946402938
    Part 2: 3706820676200
    
    real    0m0.146s
    user    0m0.139s
    sys     0m0.008s
    
    
    
    #!/usr/bin/env python3
    
    import sys
    
    
    with open(sys.argv[1], "r") as f:
        insts = list(map(str.strip, f.readlines()))
    
    mem = {}
    
    for inst in insts:
        if inst.startswith("mask"):
            mask_in = inst.split(" ")[2]
            m_or = int(mask_in.replace("X", "0"), 2)
            m_and = int(mask_in.replace("X", "1"), 2)
        elif inst.startswith("mem"):
            idx = int(inst.split("[")[1].split("]")[0])
            val = int(inst.split(" ")[2])
            mem[idx] = (val & m_and) | m_or
    
    print(f"Part 1: {sum([v for k,v in mem.items()])}")
    
    
    def get_indexes(mask):
        try:
            firstx = mask.index("X")
            return get_indexes(mask[:firstx] + "0" + mask[firstx + 1 :]) + \
                   get_indexes(mask[:firstx] + "1" + mask[firstx + 1 :])
        except ValueError:
            return [int(mask, 2)]
    
    
    mem = {}
    
    for inst in insts:
        if inst.startswith("mask"):
            mask = inst.split(" ")[2]
        elif inst.startswith("mem"):
            idx = int(inst.split("[")[1].split("]")[0])
            val = int(inst.split(" ")[2])
            idx_mask = ""
            for m, i in zip(mask, f"{idx:036b}"):
                if m == "0":
                    idx_mask += i
                elif m == "1" or m == "X":
                    idx_mask += m
                else:
                    assert False
            idxs = get_indexes(idx_mask)
            for idx in idxs:
                mem[idx] = val
    
    print(f"Part 2: {sum([v for k,v in mem.items()])}")
    

[« Day13](/adventofcode2020/13)[Day15 »](/adventofcode2020/15)

[](/adventofcode2020/14)

