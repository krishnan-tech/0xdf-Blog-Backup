# Advent of Code 2020: Day 21

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
  * Day21
  * [Day22](/adventofcode2020/22)
  * [Day23](/adventofcode2020/23)
  * [Day24](/adventofcode2020/24)
  * [Day25](/adventofcode2020/25)

![](https://0xdfimages.gitlab.io/img/aoc2020-21-cover.png)

Day 21 was welcome relief after day 20. In this one, I’ll parse a list of
foods, each with an ingredients list and a listing of some (not necessarily
all) of the allergies. I’ll use that list to pair up allergens to ingredients.

## Challenge

The puzzle can be found [here](https://adventofcode.com/2020/day/21). I’m
given list, where each line is the list of ingredients in the food and at
least some of the allergens the food may contain (absence of a label doesn’t
mean that food doesn’t contain that allergen). An example list of four foods
is:

    
    
    mxmxvkd kfcds sqjhc nhms (contains dairy, fish)
    trh fvjkl sbzzf mxmxvkd (contains dairy)
    sqjhc fvjkl (contains soy)
    sqjhc mxmxvkd sbzzf (contains fish)
    

In part one, I’m asked to find all the ingredients that can’t contain be an
allergen.

In part two, I solve the system and find which ingredient contains each
allergen.

## Solution

### Part 1

I’ll keep a list of all the ingredients (originally I used a set, but the
challenge for part one is to count the number of times the safe ingredients
appear, not the number of ingredients) and a dictionary by allergen. I’ll
parse the input saving the ingredients to the big list, and keeping track of
which ingredients could be associated with each allergen.

    
    
    all_ingredients = []
    all_allergens = {}
    
    for line in data:
        ilist, alist = line.strip('\n)').split(' (contains ')
        ilist = ilist.split(' ')
        alist = alist.split(', ')
        all_ingredients += ilist
        for allergen in alist:
            if allergen in all_allergens:
                all_allergens[allergen] &= set(ilist)
            else:
                all_allergens[allergen] = set(ilist)
    

If an allergen is already in the dictionary, then the potential ingredients
that could contain that allergen are ingredients that are in both sets, or the
intersection of the two sets, which is defined in Python as `&`. If the
allergen isn’t already in the dictionary, then the potential ingredients are
the list of ingredients in this food.

Once that’s processed, to find the list of safe ingredients, I’ll get a list
of all the foods in the allergens list, and then get the ingredients list
without the foods in that list:

    
    
    allergen_foods = set([i for v in all_allergens.values() for i in v])
    safe_foods = [i for i in all_ingredients if i not in allergen_foods]
    print(f'Part 1: {len(safe_foods)}')
    

### Part 2

Now I just need to run through the allergens dict looking for any with only
one potential ingredient. I’ll save that pair, and then remove the allergen
from the dict and the ingredient from all of the other allergens’ lists.

    
    
    canonical = {}
    while all_allergens:
        known = [(k,list(v)[0]) for k,v in all_allergens.items() if len(v) == 1]
        for k,v in known:
            canonical[k] = v
            del all_allergens[k]
            for a in all_allergens:
                if v in all_allergens[a]:
                    all_allergens[a].remove(v)
    

When that’s done, the sorted list from `canonical` is used to make the string:

    
    
    can_str = ','.join([v for k,v in sorted(canonical.items())])
    print(f'Part 2: {can_str}')
    

### Final Code

This one is basically instant:

    
    
    $ time python3 day21.py 21-puz.txt 
    Part 1: 2573
    Part 2: bjpkhx,nsnqf,snhph,zmfqpn,qrbnjtj,dbhfd,thn,sthnsg
    
    real    0m0.037s
    user    0m0.032s
    sys     0m0.000s
    
    

This code is pretty ugly, but it works:

    
    
    #!/usr/bin/env python3
    
    import sys
    
    
    with open(sys.argv[1], "r") as f:
        data = f.readlines()
    
    all_ingredients = []
    all_allergens = {}
    
    for line in data:
        ilist, alist = line.strip("\n)").split(" (contains ")
        ilist = ilist.split(" ")
        alist = alist.split(", ")
        all_ingredients += ilist
        for allergen in alist:
            if allergen in all_allergens:
                all_allergens[allergen] &= set(ilist)
            else:
                all_allergens[allergen] = set(ilist)
    
    allergen_foods = set([i for v in all_allergens.values() for i in v])
    safe_foods = [i for i in all_ingredients if i not in allergen_foods]
    print(f"Part 1: {len(safe_foods)}")
    
    canonical = {}
    while all_allergens:
        known = [(k, list(v)[0]) for k, v in all_allergens.items() if len(v) == 1]
        for k, v in known:
            canonical[k] = v
            del all_allergens[k]
            for a in all_allergens:
                if v in all_allergens[a]:
                    all_allergens[a].remove(v)
    
    can_str = ",".join([v for k, v in sorted(canonical.items())])
    print(f"Part 2: {can_str}")
    

[« Day20](/adventofcode2020/20)[Day22 »](/adventofcode2020/22)

[](/adventofcode2020/21)

