# Advent of Code 2020: Day 23

[ctf](/tags#ctf ) [advent-of-code](/tags#advent-of-code )
[python](/tags#python )  
  
Dec 23, 2020

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
  * Day23
  * [Day24](/adventofcode2020/24)
  * [Day25](/adventofcode2020/25)

![](https://0xdfimages.gitlab.io/img/aoc2020-23-cover.png)

Today is another game. This time I’m given a list of numbers and asked to mix
it according to some given rules a certain number of times. Today is also the
first time this year where I wrote part one, and then completely started over
given part two.

## Challenge

The puzzle can be found [here](https://adventofcode.com/2020/day/23). I’m
given a list of numbers, which represent numbered cups in a circle, such that
the first comes after the last. The rules are simple. The active cup starts as
the first cup in the original list. The next three cups are removed from the
circle. The target is found to be cup with the value one less than the active
cup (and if that cup isn’t in the circle, decrement again until it is found in
the circle). The three cups are then inserted after the target cup, and the
active cup moves to the new cup that is after the previous active cup.

In part one, there are 100 rounds with the given list.

In part two, the rules are the same, but there are two differences. First,
while the input gives the order for cups 1-9, cups ten through one million are
then also joined into the circle in numerical order. Second, instead of 100
rounds, there will be ten million.

## Solution

### Part 1

The scope of the problem in part one made it that I could solve this with a
list of numbers, slicing and recombining to make the updated list:

    
    
    #!/usr/bin/env python3
    
    import sys
    
    game = [int(x) for x in sys.argv[1]]
    num_moves = int(sys.argv[2]) if len(sys.argv) > 2 else 100
    glen = len(game)
    
    for _ in range(num_moves):
        pick = game[1:4]
        game = game[0:1] + game[4:]
        sgame = sorted(game)
        dest = sgame[(sgame.index(game[0]) - 1) % (glen - 3)]
        dest_idx = game.index(dest) + 1
        game = game[1:dest_idx] + pick + game[dest_idx:] + game[0:1]
    
    idx1 = game.index(1)
    res = "".join([str(c) for c in game[idx1 + 1 :] + game[:idx1]])
    print(f'Part 1: {res}')
    

Rather than track the active cup, I just moved the list such that the active
cup was always at the front of the list. This made it easier so I didn’t have
to worry about slicing beyond the end of the list.

This runs in less than 0.1 second, and solves the challenge.

### Part 2

In theory, one might think I could just change the numbers and construct this
new list for part two, but my solution above will be _way_ too slow. slicing
and building lists is a very slow action in Python. I’ll change strategies so
that I keep a linked list. It will be a simple Python dictionary, where the
key is a cup, and the value is the next cup after it. So to find out which cup
comes after cup one, it’s kept in `cuplist[1]`. That also means to move a cup,
I only have to change the value for the cup that used to point to it, the new
cup that points to it, and the cup it points to.

I’ll create a function that takes a list of cups, the full padded length of
the game, and the number of moves. I’ll make sure this function works on both
part one and part two.

First, I’ll build the linked list. For part one, it’s as simple as looping
over the cups, and taking the cup number as the key, and the next cup number
as the value, and putting it into the dictionary. When I reach the last cup,
I’ll just set it to point to the value of the first cup.

    
    
        cuplist = {}
        for i in range(full_len):
            if i < len(cups) - 1:
                cuplist[cups[i]] = cups[i + 1]
            elif i == len(cups) - 1 and len(cups) == full_len:
                cuplist[cups[i]] = cups[0]
    

With the part two extension, I’ll start adding a count up after, and that will
take a few more conditions:

    
    
            elif i == len(cups) - 1 and len(cups) < full_len:
                cuplist[cups[i]] = max(cups) + 1
            elif i < full_len - 1:
                cuplist[i + 1] = i + 2
            elif i == full_len - 1:
                cuplist[i + 1] = cups[0]
    

Once the list is built, the game is played. To pull three cups out, I’ll
record their values, and set the pointer in the active cup to the cup four
down:

    
    
            # remove three cups
            c1 = cuplist[ptr]
            c2 = cuplist[c1]
            c3 = cuplist[c2]
            cuplist[ptr] = cuplist[c3]
    

To find the destination, I’ll use modular arithmetic. I really want to
subtract one and take the mod length. But that produce results in the zero to
length minus one range. So I’ll actually subtract two, take the mod, and then
add one, giving results in the one to length range. I’ll use a while loop to
make sure the cup isn’t in the removed cups:

    
    
            # find dest
            dest = ((ptr - 2) % full_len) + 1
            while dest in [c1, c2, c3]:
                dest = ((dest - 2) % full_len) + 1
    

Now I’ll just inset the cups by updating two pointers, and get the next active
cup:

    
    
            # reinsert cups after dest
            cuplist[c3] = cuplist[dest]
            cuplist[dest] = c1
    
            # move ptr forward
            ptr = cuplist[ptr]
    

I’ll do that all in a for loop over the number of iterations required, and
return that list.

### Final Code

Part one is quick, but part two runs for twenty seconds:

    
    
    $ time python3 day23.py 219748365 
    Part 1: 35827964
    Part 2: 5403610688
    
    real    0m22.701s
    user    0m22.601s
    sys     0m0.065s
    
    
    
    #!/usr/bin/env python3
    
    import sys
    
    
    def solve_game(cups, full_len, num_moves):
    
        # prep list
        cuplist = {}
        for i in range(full_len):
            if i < len(cups) - 1:
                cuplist[cups[i]] = cups[i + 1]
            elif i == len(cups) - 1 and len(cups) == full_len:
                cuplist[cups[i]] = cups[0]
            elif i == len(cups) - 1 and len(cups) < full_len:
                cuplist[cups[i]] = max(cups) + 1
            elif i < full_len - 1:
                cuplist[i + 1] = i + 2
            elif i == full_len - 1:
                cuplist[i + 1] = cups[0]
    
        ptr = cups[0]
        for _ in range(num_moves):
    
            # remove three cups
            c1 = cuplist[ptr]
            c2 = cuplist[c1]
            c3 = cuplist[c2]
            cuplist[ptr] = cuplist[c3]
    
            # find dest
            dest = ((ptr - 2) % full_len) + 1
            while dest in [c1, c2, c3]:
                dest = ((dest - 2) % full_len) + 1
    
            # reinsert cups after dest
            cuplist[c3] = cuplist[dest]
            cuplist[dest] = c1
    
            # move ptr forward
            ptr = cuplist[ptr]
    
        return cuplist
    
    
    cups = [int(x) for x in sys.argv[1]]
    
    solved = solve_game(cups, len(cups), 100)
    res = ""
    x = solved[1]
    while x != 1:
        res += str(x)
        x = solved[x]
    print(f"Part 1: {res}")
    
    solved = solve_game(cups, 1000000, 10000000)
    res = solved[1] * solved[solved[1]]
    print(f"Part 2: {res}")
    

[« Day22](/adventofcode2020/22)[Day24 »](/adventofcode2020/24)

[](/adventofcode2020/23)

