# Advent of Code 2020: Day 25

[ctf](/tags#ctf ) [advent-of-code](/tags#advent-of-code )
[python](/tags#python ) [modular-arithmetic](/tags#modular-arithmetic )  
  
Dec 26, 2020

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
  * [Day19](/adventofcode2020/19)
  * [Day20](/adventofcode2020/20)
  * [Day21](/adventofcode2020/21)
  * [Day22](/adventofcode2020/22)
  * [Day23](/adventofcode2020/23)
  * [Day24](/adventofcode2020/24)
  * Day25

![](https://0xdfimages.gitlab.io/img/aoc2020-25-cover.png)

Day 25 is an encryption problem using modular arithmetic. I’ve given two
public keys, both of which are of the form 7d mod 20201227 where d is unknown.
The challenge is to find each d.

## Challenge

The puzzle can be found [here](https://adventofcode.com/2020/day/25). I’m
given two public keys, each of which are some power of seven mod 20201227. I’m
asked to find each of the exponents, and then use those to find the private
key. This is similar to how some forms of asymmetric encryption work.

## Solution

To start, I need to find the exponent. There are many ways to attack this kind
of challenge, but I’ll start with a simple brute force since the number space
is small and I don’t expect AOC to think we all bring crypto expertise.

I can calculate ab mod c in Python as `pow(a, b, c)`. So I’ll find each loop
by looping until the result matches the given key:

    
    
    card_loop = 1
    while pow(7, card_loop, 20201227) != card_pub:
        card_loop += 1
    
    door_loop = 1
    while pow(7, door_loop, 20201227) != door_pub:
        door_loop += 1
    

Once I have those, I’m told the encryption key is either public key raised to
the other’s loop count. Starting from either public key should produce the
same result:

    
    
    priv_key = pow(card_pub, door_loop, 20201227)
    assert priv_key == pow(door_pub, card_loop, 20201227)
    

That’s the answer!

It solves the test input basically instantly, but takes almost two minutes to
solve the puzzle input:

    
    
    $ time python3 day25.py 25-test 
    Part 1: 14897079
    
    real    0m0.046s
    user    0m0.023s
    sys     0m0.011s
    
    $ time python3 day25.py 25-puz 
    Part 1: 3803729
    
    real    1m42.371s
    user    1m42.272s
    sys     0m0.024s
    

This is slow, and I suspect there are ways to speed this up rather than taking
the brute force approach. Maybe I’ll come back to that someday.

The full code is:

    
    
    #!/usr/bin/env python3
    
    import sys
    
    with open(sys.argv[1], 'r') as f:
        card_pub, door_pub = list(map(int, f.read().strip().split('\n')))
    
    card_loop = 1
    while pow(7, card_loop, 20201227) != card_pub:
        card_loop += 1
    
    door_loop = 1
    while pow(7, door_loop, 20201227) != door_pub:
        door_loop += 1
    
    priv_key = pow(card_pub, door_loop, 20201227)
    assert priv_key == pow(door_pub, card_loop, 20201227)
    
    print(f'Part 1: {priv_key}')
    

[« Day24](/adventofcode2020/24)

[](/adventofcode2020/25)

