# Advent of Code 2020: Day 22

[ctf](/tags#ctf ) [advent-of-code](/tags#advent-of-code )
[python](/tags#python )  
  
Dec 22, 2020

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
  * Day22
  * [Day23](/adventofcode2020/23)
  * [Day24](/adventofcode2020/24)
  * [Day25](/adventofcode2020/25)

![](https://0xdfimages.gitlab.io/img/aoc2020-22-cover.png)

I’m asked to play out a game between two players that in part one looks like
the classic card game of war, and in part two goes off in a different
direction of “recursive combat”. Both parts came together pretty quickly,
though part two had a few places where small mistakes made identifying
mistakes difficult.

## Challenge

The puzzle can be found [here](https://adventofcode.com/2020/day/22). I’m
given two decks and a set of rules very similar to the classic game of
[war](https://bicyclecards.com/how-to-play/war/) (though this game managed to
avoid two players ever having the same card). Each deck takes the top card,
and the higher card gets both back onto the bottom of that deck, with the
winning card first.

In part two, there’s an extra check. The top cards are checked. This time, if
each player has enough cards, they clone that many cards from the top of their
deck, and enter those decks into a new game. If either player doesn’t have
enough, the higher card wins. There is a check in here for infinite loops as
well.

## Solution

### Part 1

My program created both decks,and then loop over them while they both have
cards, comparing the top cards, and putting both onto the bottom of the
winner:

    
    
    with open(sys.argv[1], 'r') as f:
        raw_decks = f.read().strip().split('\n\n')
    
    decks = [list(map(int, deck.split('\n')[1:])) for deck in raw_decks]
    
    while all(decks):
        c0, c1 = [d.pop(0) for d in decks]
        if c1 > c0:
            decks[1] += [c1, c0]
        elif c0 > c1:
            decks[0] += [c0, c1]
        else:
            raise
    

When this loop exists, one of the decks will have no cards. I can get the
winning deck with `max`, and then use the score algorithm provided to find the
result:

    
    
    winner = max(decks)
    part1 = sum([f*c for f,c in zip(range(len(winner), 0, -1), winner)])
    print(f'Part 1: {part1}')
    

### Part 2

In part two I’ll make a recursive function to handle the game. It’s important
to think about what is being passed here. For example, originally I was
tracking rounds by having a list and adding the decks to it. But then as the
decks changed, so did the contents in rounds. I could use `deepcopy` here, but
I opted to just create a string from the current state and store that. When I
pass the subdecks into the new recursive game, because I’m slicing out of the
array, it is actually creating a new copy, so I don’t have to worry about
`deepcopy` there either.

    
    
    def rec_comb(decks):
        rounds = set()
        while all(decks):
            r = '-'.join([str(d) for d in decks])
            if r in rounds:
                return [decks[0], []]
            rounds.add(r)
            c0, c1 = [d.pop(0) for d in decks]
            if c0 <= len(decks[0]) and c1 <= len(decks[1]):
                result = rec_comb([decks[0][:c0], decks[1][:c1]])
                winner_is_1 = bool(result[1])
            else:
                winner_is_1 = c1 > c0
            if winner_is_1:
                decks[1].extend([c1, c0])
            else:
                decks[0].extend([c0, c1])
        return decks
    
    
    # Same starting decks
    decks = [list(map(int, deck.split('\n')[1:])) for deck in raw_decks]
    
    res = max(rec_comb(decks))
    part2 = sum([f*c for f,c in zip(range(len(res), 0, -1), res)])
    print(f'Part 2: {part2}')
    

### Final Code

Part one is quick, but part two runs for twenty seconds:

    
    
    $ time python3 day22.py 22-puz 
    Part 1: 33473
    Part 2: 31793
    
    real    0m20.376s
    user    0m20.097s
    sys     0m0.209s
    
    
    
    
    #!/usr/bin/env python3
    
    import sys
    
    
    with open(sys.argv[1], "r") as f:
        raw_decks = f.read().strip().split("\n\n")
    
    decks = [list(map(int, deck.split("\n")[1:])) for deck in raw_decks]
    
    while all(decks):
        c0, c1 = [d.pop(0) for d in decks]
        if c1 > c0:
            decks[1] += [c1, c0]
        elif c0 > c1:
            decks[0] += [c0, c1]
        else:
            raise
    
    winner = max(decks)
    part1 = sum([f * c for f, c in zip(range(len(winner), 0, -1), winner)])
    print(f"Part 1: {part1}")
    
    
    def rec_comb(decks):
        rounds = set()
        while all(decks):
            r = "-".join([str(d) for d in decks])
            if r in rounds:
                return [decks[0], []]
            rounds.add(r)
            c0, c1 = [d.pop(0) for d in decks]
            if c0 <= len(decks[0]) and c1 <= len(decks[1]):
                result = rec_comb([decks[0][:c0], decks[1][:c1]])
                winner_is_1 = bool(result[1])
            else:
                winner_is_1 = c1 > c0
            if winner_is_1:
                decks[1].extend([c1, c0])
            else:
                decks[0].extend([c0, c1])
        return decks
    
    
    # Same starting decks
    decks = [list(map(int, deck.split("\n")[1:])) for deck in raw_decks]
    
    res = max(rec_comb(decks))
    part2 = sum([f * c for f, c in zip(range(len(res), 0, -1), res)])
    print(f"Part 2: {part2}")
    

[« Day21](/adventofcode2020/21)[Day23 »](/adventofcode2020/23)

[](/adventofcode2020/22)

