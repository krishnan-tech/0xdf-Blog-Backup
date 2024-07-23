# Advent of Code 2020: Day 5

[ctf](/tags#ctf ) [advent-of-code](/tags#advent-of-code )
[python](/tags#python )  
  
Dec 5, 2020

  * [Day1](/adventofcode2020/1)
  * [Day2](/adventofcode2020/2)
  * [Day3](/adventofcode2020/3)
  * [Day4](/adventofcode2020/4)
  * Day5
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

![](https://0xdfimages.gitlab.io/img/aoc2020-5-cover.png)

Day 5 is wrapped in a story about plane ticket seat finding, but really it
boils down to a simple binary to integer conversion, and then finding the
difference of two sets and cleaning up what’s left based on some simple rules.

## Challenge

The puzzle can be found [here](https://adventofcode.com/2020/day/5). I’m given
seat numbers using a “binary space partitioning” strategy. The idea is that
the first character, B for back or F for front identifies if the seat is in
the back or front half of the plane. The second B or F identifies if the seat
is in the back or front half of that previously chosen half. There are exactly
128 rows, so seven Bs and/or Fs determine the row number. Then there are three
Ls and/or Rs to determine a column. To make a seat ID, just multiple the row
by eight and add the column. One example input would be `FBFBBFFRLR`, which
represents row 44, column 5, seat id 357.

## Solution

### Part 1

I’ve done enough CTFs working with binary data to immediately recognize this
for what it is - binary.

    
    
      FBFBBFFRLR
          |
          v
      0101100101
          |
          v
     0101100 101
        |     |
        v     v
        44    5
    

I can also notice that the seat id is just original string as binary:

    
    
    357 = 44 * 8 + 5
        = (44 << 3) | 5
        = (0101100 << 3) | 101
        = 0101100000 | 101
        = 0101100101 
    

This is the given ticket! This makes finding the seat id super easy. Replace
Fs and Ls with 0, Bs and Rs with 1s, and convert to an int.

    
    
    #!/usr/bin/env python3
    
    import sys
    
    
    with open(sys.argv[1], "r") as f:
        seats = (
            f.read()
            .strip()
            .replace("B", "1")
            .replace("F", "0")
            .replace("R", "1")
            .replace("L", "0")
            .split("\n")
        )
    
    print(f"Part 1: {max([int(s, 2) for s in seats])}")
    

For each seat, convert it to binary, and grab the max in the array.

### Part 2

In part two, I’m asked to go through all the seats, and find mine. There will
be 128 * 8 = 1024 seats on the plane, but my puzzle input has only 781 filled
seats:

    
    
    $ wc -l 05-puzzle_input.txt 
    781 05-puzzle_input.txt
    

It turns out there will be seats at the front and back of the plain that
aren’t filled. My seat will have someone in both the the id one higher and one
lower.

I’ll adjust the code from above to create a set of claimed seats, and then
create the set of all numbers 0-1023, and find the difference, leaving the
open seats.

This will produce a list like this:

    
    
    >>> openseats = allseats - claimed
    >>> len(openseats)
    243
    >>> openseats
    {0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 517, 833, 834, 835, 836, 837, 838, 839, 840, 841, 842, 843, 844, 845, 846, 847, 848, 849, 850, 851, 852, 853, 854, 855, 856, 857, 858, 859, 860, 861, 862, 863, 864, 865, 866, 867, 868, 869, 870, 871, 872, 873, 874, 875, 876, 877, 878, 879, 880, 881, 882, 883, 884, 885, 886, 887, 888, 889, 890, 891, 892, 893, 894, 895, 896, 897, 898, 899, 900, 901, 902, 903, 904, 905, 906, 907, 908, 909, 910, 911, 912, 913, 914, 915, 916, 917, 918, 919, 920, 921, 922, 923, 924, 925, 926, 927, 928, 929, 930, 931, 932, 933, 934, 935, 936, 937, 938, 939, 940, 941, 942, 943, 944, 945, 946, 947, 948, 949, 950, 951, 952, 953, 954, 955, 956, 957, 958, 959, 960, 961, 962, 963, 964, 965, 966, 967, 968, 969, 970, 971, 972, 973, 974, 975, 976, 977, 978, 979, 980, 981, 982, 983, 984, 985, 986, 987, 988, 989, 990, 991, 992, 993, 994, 995, 996, 997, 998, 999, 1000, 1001, 1002, 1003, 1004, 1005, 1006, 1007, 1008, 1009, 1010, 1011, 1012, 1013, 1014, 1015, 1016, 1017, 1018, 1019, 1020, 1021, 1022, 1023}
    

I could just look through that list and find the seat without it’s neighbors,
but completeness I’ll use a list comprehension and have it pull the one
number:

    
    
    #!/usr/bin/env python3
    
    import sys
    
    
    with open(sys.argv[1], "r") as f:
        seats = (
            f.read()
            .strip()
            .replace("B", "1")
            .replace("F", "0")
            .replace("R", "1")
            .replace("L", "0")
            .split("\n")
        )
    
    claimed = set([int(s, 2) for s in seats])
    print(f"Part 1: {max(claimed)}")
    
    allseats = set(range(128 * 8))
    openseats = allseats - claimed
    myseat = [
        seat
        for seat in openseats
        if seat + 1 not in openseats and seat - 1 not in openseats
    ]
    
    print(f"Part 2: {myseat[0]}")
    

Time is still not yet a factor this year, so this also solves instantly:

    
    
    $ time python3 day5.py 05-puzzle_input.txt 
    Part 1: 832
    Part 2: 517
    
    real    0m0.061s
    user    0m0.041s
    sys     0m0.016s
    

[« Day4](/adventofcode2020/4)[Day6 »](/adventofcode2020/6)

[](/adventofcode2020/5)

