# Advent of Code 2020: Day 4

[ctf](/tags#ctf ) [advent-of-code](/tags#advent-of-code )
[python](/tags#python ) [regex](/tags#regex )  
  
Dec 4, 2020

  * [Day1](/adventofcode2020/1)
  * [Day2](/adventofcode2020/2)
  * [Day3](/adventofcode2020/3)
  * Day4
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
  * [Day25](/adventofcode2020/25)

![](https://0xdfimages.gitlab.io/img/aoc2020-4-cover.png)

Day 4 presented another text parsing challenge. In the first part, I just
needed to validate if each section contained a specific seven strings, which
is easy enough to solve in Python. For part two, I need to now look at the
text following each of these strings, and apply some validation rules. At
first I thought I’d throw out my part 1 work and start processing all the data
into a Python dict. But then I realized I could just write a regex for each
validation, and use the same pattern.

## Challenge

The puzzle can be found [here](https://adventofcode.com/2020/day/4). I’m given
a bunch of text lines of “passport” data in key:value format, with eight
required keys. The example data is:

>
>     ecl:gry pid:860033327 eyr:2020 hcl:#fffffd
>     byr:1937 iyr:2017 cid:147 hgt:183cm
>  
>     iyr:2013 ecl:amb cid:350 eyr:2023 pid:028048884
>     hcl:#cfa07d byr:1929
>  
>     hcl:#ae17e1 iyr:2013
>     eyr:2024
>     ecl:brn pid:760753108 byr:1931
>     hgt:179cm
>  
>     hcl:#cfa07d eyr:2025 pid:166559648
>     iyr:2011 ecl:brn hgt:59in
>  

In the first part, I’m asked to validate passports by if they contain seven
(ignoring the eighth for the sake of the story) specific key values.

In the second part, I need to validate the data for each field.

In both cases, I’m asked to return the number of valid passports.

## Solution

### Part 1

On reading in the data, I’ll split on `\n\n` to get each passport into it’s
own string, newlines and all.

I created a list of the keys I was looking for, and use it in a nested list
comprehension. The inner list is a loop over all the keys, checking in a given
passport to see if they are in there:

    
    
    all([k in p for k in keys]
    

If all seven keys are there, this is true.

Now I’ll loop over the passports and count the numbers of true:

    
    
    num_keys_valid = sum([all([k in p for k in keys]) for p in passports])
    

Putting that into a script, it returns the answer:

    
    
    #!/usr/bin/env python3
    
    import sys
    
    
    keys = [
        "byr",  # (Birth Year)
        "iyr",  # (Issue Year)
        "eyr",  # (Expiration Year)
        "hgt",  # (Height)
        "hcl",  # (Hair Color)
        "ecl",  # (Eye Color)
        "pid",  # (Passport ID)
        # "cid", # (Country ID)
    ]
    
    with open(sys.argv[1], "r") as f:
        passports = f.read().split("\n\n")
    
    
    num_keys_valid = sum([all([k in p for k in keys]) for p in passports])
    print(f"Part 1: {num_keys_valid}")
    

### Part 2

At first I thought my part one skim of the data like this would have to
completely change structure for part two, reading each passport into a
dictionary and applying validity rules. However, as I started thinking about
it, each field’s rules could be expressed as a regex, and so I turned the keys
from part 1 into a dict with a regex string for each key, and did a similar
loop.

What got me really stuck for longer than I’m proud to admit was that I wasn’t
checking for the end of the string. The thing that was getting me was my
original regex for `pid`:

    
    
    r"pid:\s*\d{9}"
    

This found all the nine-digit pids, but it also found a 10 digit one, which
isn’t valid. I’ll add a `\b` to the end, which matches on any whitespace or a
newline, and that fixes it (I should have `\b` on most of these):

    
    
    #!/usr/bin/env python3
    
    import re
    import sys
    
    
    keys = {
        "byr": r"byr:\s*(19[2-9]\d|200[0-2])\b",  # (Birth Year) - four digits; at least 1920 and at most 2002.
        "iyr": r"iyr:\s*20(1\d|20)\b",  # (Issue Year) - four digits; at least 2010 and at most 2020.
        "eyr": r"eyr:\s*20(2\d|30)\b",  # (Expiration Year) - four digits; at least 2020 and at most 2030.
        "hgt": r"hgt:\s*(1([5-8]\d|9[0-3])cm|(59|6\d|7[0-6])in)",  # (Height) - a number followed by either cm or in:
        # "If cm, the number must be at least 150 and at most 193.
        # "If in, the number must be at least 59 and at most 76.
        "hcl": r"hcl:\s*#[0-9a-f]{6}\b",  # (Hair Color) - a # followed by exactly six characters 0-9 or a-f.
        "ecl": r"ecl:\s*(amb|blu|brn|gry|grn|hzl|oth)\b",  # (Eye Color) - exactly one of: amb blu brn gry grn hzl oth.
        "pid": r"pid:\s*\d{9}\b",  # (Passport ID) - a nine-digit number, including leading zeroes.
        # "cid", # (Country ID) - ignored, missing or not.
    }
    
    with open(sys.argv[1], "r") as f:
        passports = f.read().split("\n\n")
    
    num_keys_valid = sum([all([k in p for k in keys]) for p in passports])
    print(f"Part 1: {num_keys_valid}")
    
    num_data_valid = sum([all([re.search(keys[k], p) for k in keys]) for p in passports])
    print(f"Part 2: {num_data_valid}")
    

Running this gives both answers (still instantly):

    
    
    $ time python3 day4.py 04-puzzle_input.txt
    Part 1: 245
    Part 2: 133
    
    real    0m0.065s
    user    0m0.053s
    sys     0m0.008s
    

[« Day3](/adventofcode2020/3)[Day5 »](/adventofcode2020/5)

[](/adventofcode2020/4)

