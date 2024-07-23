# Advent of Code 2019: Day 4

[ctf](/tags#ctf ) [advent-of-code](/tags#advent-of-code )
[python](/tags#python )  
  
Dec 3, 2019

  * [Day1](/adventofcode2019/1)
  * [Day2](/adventofcode2019/2)
  * [Day3](/adventofcode2019/3)
  * Day4
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

![](https://0xdfimages.gitlab.io/img/aoc2019-4-cover.png)

I solved day 4 much faster than day 3, probably because it moved away from
spatial reasoning and just into input validation. I’m given a range of 6-digit
numbers, and asked to pick ones that meet certain criteria.

## Challenge

The puzzle can be found [here](https://adventofcode.com/2019/day/4). I’m given
a starting and ending point, both 6-digit numbers. For part 1, I need to count
the number of numbers in that range that have only increasing (or staying the
same) digits left to right, and contain two matching digits at some point in
the password. For part 2, I add the complication that a grouping of 3
repeating digits doesn’t count towards the pair requirement.

## Solution

### Part 1

There are so many ways to approach this. I considered recurrsively building
the password rather than looping over a range because I could avoid even
checking many of the number. For example, for `5678`, I’d only have to check
`567888`, `567889`, `567899`, and not the other 97 possible two digit
combinations.

But then I decided to try first just looping over the entire range, and while
it isn’t instant, it still took less than a second.

For part one my code is:

    
    
    #!/usr/bin/env python3
    
    import re
    import sys
    
    
    count = 0
    for passwd_int in range(int(sys.argv[1]), int(sys.argv[2]) + 1):
        passwd = f"{passwd_int}"
        if re.search(r"(\d)\1", passwd) and all(
            int(i) <= int(j) for i, j in zip(passwd, passwd[1:])
        ):
            count += 1
    
    print(f"Part 1: {count}")
    

This loops over the numbers in the given range, and checks first if there’s a
repeating digit using `re.search`, and then if for each character in the
password, the next one is greater than or equal. `zip` is smart enough to take
the six characters in `passwd` and the five characters in `passwd[1:]` and
return five tuples.

This runs in less than a second, and returns the right answer:

    
    
    $ time ./day4.py 231832 767346
    Part 1: 1330
    
    real    0m0.848s
    user    0m0.840s
    sys     0m0.008s
    

### Part 2

In part two, when checking for consecutive characters, there must be a group
of only two for it to be valid. This is tricky because while `123444` is no
longer valid, `111122` still is, because while the four 1s don’t count, the
pair of 2s do.

I decided to add a check after incrementing `count` to look for this. I’m
going to do a `findall` on the consecutive characters and then look for ones
that are two in length.

This gets a bit tricky with the `\1` capture group reference. I started with
something like this:

    
    
    >>> re.findall(r'(\d)\1+', '111122')
    ['1', '2']
    

It’s finding what I want it to find, but only returning what’s in `()`. I
tried changing it to:

    
    
    >>> re.findall(r'((\d)\1+)', '111122')
    

But that crashes, because the `\1` is referencing a capture group that isn’t
yet closed.

The trick then is to use `\2`, since the `(\d)` is now the second capture
group. This worked:

    
    
    >>> re.findall(r'((\d)\2+)', '111122')
    [('1111', '1'), ('22', '2')]
    

I can use a list comprehension to get just the part I care about:

    
    
    >>> [x[0] for x in re.findall(r'((\d)\2+)', '111122')]
    ['1111', '22']
    

Now I can change that into a check for length:

    
    
    >>> [len(x[0]) == 2 for x in re.findall(r'((\d)\2+)', '111122')]
    [False, True]
    

I’ll add this to my code, and when I run this, it solves both in less than a
second:

    
    
    $ time ./day4.py 231832 767346
    Part 1: 1330
    Part 2: 876
    
    real    0m0.644s
    user    0m0.644s
    sys     0m0.000s
    

## Final Code

    
    
    #!/usr/bin/env python3
    
    import re
    import sys
    
    
    count = 0
    count2 = 0
    for passwd_int in range(int(sys.argv[1]), int(sys.argv[2]) + 1):
        passwd = f"{passwd_int}"
        if re.search(r"(\d)\1", passwd) and all(
            int(i) <= int(j) for i, j in zip(passwd, passwd[1:])
        ):
            count += 1
            if any([len(x[0]) == 2 for x in re.findall(r"((\d)\2+)", passwd)]):
                count2 += 2
    
    print(f"Part 1: {count}")
    print(f"Part 2: {count2}")
    

[« Day3](/adventofcode2019/3)[Day5 »](/adventofcode2019/5)

[](/adventofcode2019/4)

