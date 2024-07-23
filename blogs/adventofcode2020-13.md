# Advent of Code 2020: Day 13

[ctf](/tags#ctf ) [advent-of-code](/tags#advent-of-code )
[python](/tags#python ) [chinese-remainder-theorem](/tags#chinese-remainder-
theorem )  
  
Dec 13, 2020

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
  * Day13
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

![](https://0xdfimages.gitlab.io/img/aoc2020-13-cover.png)

Day 13 is looking at a series of buses that are running on their own time
cycles, and trying to find times where the buses arrive in certain patterns.
It brings in a somewhat obscure number theory concept called the Chinese
Remainder Theorem, which has to do with solving a series of modular linear
equations that all equal the same value.

## Challenge

The puzzle can be found [here](https://adventofcode.com/2020/day/13). The
puzzle input will have two lines, where the first represents the time at which
I can start, and the second is a list of buses. For example”

    
    
    939
    7,13,x,x,59,x,31,19
    

The buses will come through the station to pick up ever x minutes, where x is
the bus id. So bus 7 comes at 7, 14, 21, etc. In part one, I’m asked to look
at the first bus that will come through after the given start time.

In part two, I’m asked to look at the list of buses as an order of buses, and
find a time such that the first bus comes at that time, the next bus comes one
later, the next one later, etc. If there’s an x, it means it doesn’t matter if
any buses come at that offset.

## Solution

### Part 1

This was a pretty simple one. I’ll take the min time mod the bus id to get the
number of minutes after the most recent bus from that route the time is. That
means the next bus will be id minus that result.

    
    
    #!/usr/bin/env python3
    
    import sys
    
    
    with open(sys.argv[1], 'r') as f:
        start = int(f.readline())
        buses_raw = f.readline().strip().split(',')
    
    buses = [int(b) for b in buses_raw if b != 'x']
    waits = [(b,b - (start % b)) for b in buses]
    
    answer = min(waits, key=lambda x: x[1])
    
    print(f'Part 1: {answer[0] * answer[1]}')
    

I’ll use a list comprehension to calculate the waits from the start time for
each line, and then get the smallest one.

### Part 2

Now comes the number theory. It’s clear from the prompt that I can’t just
brute force through times, as the number will be huge. I got completely stuck
here, and had to get the hint to look at [Chinese Remainder
Theorum](https://en.wikipedia.org/wiki/Chinese_remainder_theorem).

For each bus, `b`, let `i` be the index in the list. Then I need to solve such
that for each bus:

    
    
    (t+i) mod b = 0
    

I’ll do some algebra to rearrange that:

    
    
    (t+i) ≡ 0 mod b
    t ≡ -i mod b
    t ≡ b-i mod b
    

This is the series of equations that CRT looks to solve (brilliant.org has a
[great explanation](https://brilliant.org/wiki/chinese-remainder-theorem/)
from here). My equations meet the form:

    
    
    x ≡ a[i] mod n[i]
    

Where the `a` will be (b-i) and the `n` will be b.

I cheated a bit here and found [this
implementation](https://rosettacode.org/wiki/Chinese_remainder_theorem#Python_3.6)
of CRT and stuck it into my code:

    
    
    from functools import reduce
    def chinese_remainder(n, a):
        sum = 0
        prod = reduce(lambda a, b: a*b, n)
        for n_i, a_i in zip(n, a):
            p = prod // n_i
            sum += a_i * mul_inv(p, n_i) * p
        return sum % prod
    
    
    def mul_inv(a, b):
        b0 = b
        x0, x1 = 0, 1
        if b == 1: return 1
        while a > 1:
            q = a // b
            a, b = b, a%b
            x0, x1 = x1 - q * x0, x0
        if x1 < 0: x1 += b0
        return x1
    
    
    offsets = [int(b) - i for i,b in enumerate(buses_raw) if b != 'x']
    print(f'Part 2: {chinese_remainder(buses, offsets)}')
    

### Final Code

Script runs instantly:

    
    
    $ time python3 day13.py 13-puzzle.txt
    Part 1: 410
    Part 2: 600691418730595
    
    real    0m0.049s
    user    0m0.041s
    sys     0m0.008s
    
    
    
    #!/usr/bin/env python3
    
    import sys
    from functools import reduce
    
    
    with open(sys.argv[1], "r") as f:
        start = int(f.readline())
        buses_raw = f.readline().strip().split(",")
    
    buses = [int(b) for b in buses_raw if b != "x"]
    waits = [(b, b - (start % b)) for b in buses]
    
    answer = min(waits, key=lambda x: x[1])
    
    print(f"Part 1: {answer[0] * answer[1]}")
    
    
    def chinese_remainder(n, a):
        sum = 0
        prod = reduce(lambda a, b: a * b, n)
        for n_i, a_i in zip(n, a):
            p = prod // n_i
            sum += a_i * mul_inv(p, n_i) * p
        return sum % prod
    
    
    def mul_inv(a, b):
        b0 = b
        x0, x1 = 0, 1
        if b == 1:
            return 1
        while a > 1:
            q = a // b
            a, b = b, a % b
            x1, x1 = x1 - q * x0, x0
        if x1 < 0:
            x1 += b0
        return x1
    
    
    offsets = [int(b) - i for i, b in enumerate(buses_raw) if b != "x"]
    print(f"Part 2: {chinese_remainder(buses, offsets)}")
    

[« Day12](/adventofcode2020/12)[Day14 »](/adventofcode2020/14)

[](/adventofcode2020/13)

