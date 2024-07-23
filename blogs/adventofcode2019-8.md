# Advent of Code 2019: Day 8

[ctf](/tags#ctf ) [advent-of-code](/tags#advent-of-code )
[python](/tags#python )  
  
Dec 8, 2019

  * [Day1](/adventofcode2019/1)
  * [Day2](/adventofcode2019/2)
  * [Day3](/adventofcode2019/3)
  * [Day4](/adventofcode2019/4)
  * [Day5](/adventofcode2019/5)
  * [Day6](/adventofcode2019/6)
  * [Day7](/adventofcode2019/7)
  * Day8
  * [Day9](/adventofcode2019/9)
  * [Day10](/adventofcode2019/10)
  * [Day11](/adventofcode2019/11)
  * [Day12](/adventofcode2019/12)
  * [Day13](/adventofcode2019/13)
  * [Day14](/adventofcode2019/14)

![](https://0xdfimages.gitlab.io/img/aoc2019-8-cover.png)

After spending hours on day 7, I finished day 8 in about 15 minutes. It was
simply reading in a series of numbers which represented pixels in various
layers in an email. In part one I’ll break the pixels into layers, and
evaluate each one. In part two, I’ll actually create the image.

## Challenge

The puzzle can be found [here](https://adventofcode.com/2019/day/8). I’m given
a string of 0s, 1s, and 2s. The string is 15000 characters long, which I must
break into layers that are 25 wide by 6 tall. In part one, I’ll find the layer
with the fewest 0s, and then return the number of 1s in that layer times the
number of 2s.

In part two, I’ll understand that 2 is transparent, 1 is black, and 0 is
white. Looking down from the top layer, I’ll draw the picture.

## Solution

### Part 1

Python makes this so simple. I’ll read in the input, and then break it into
layers. Then I can use the `min` command, passing it a lambda function as
`key`. The lambda just tells it to count the number of `0`.

    
    
    #!/usr/bin/env python3
    
    import sys
    
    
    w, h = 25, 6
    with open(sys.argv[1], "r") as f:
        pixels = f.read().strip()
    
    layers = [pixels[i : i + w * h] for i in range(0, len(pixels), w * h)]
    
    fewest_0 = min(layers, key=lambda x: x.count("0"))
    print(f"Part 1: {fewest_0.count('1')*fewest_0.count('2')}")
    

It runs and immediately returns the answer:

    
    
    $ time python3 day8.py 08-puzzle_input.txt 
    Part 1: 1330
    
    real    0m0.028s
    user    0m0.020s
    sys     0m0.008s
    

### Part 2

I now just need to write something that will loop over the pixels, and then
starting at layer 0, find the first layer with a non-2 at that pixel.

    
    
    #!/usr/bin/env python3
    
    import sys
    
    
    w, h = 25, 6
    with open(sys.argv[1], "r") as f:
        pixels = f.read().strip()
    
    layers = [pixels[i : i + w * h] for i in range(0, len(pixels), w * h)]
    
    fewest_0 = min(layers, key=lambda x: x.count("0"))
    print(f"Part 1: {fewest_0.count('1')*fewest_0.count('2')}")
    
    print(f"Part 2:")
    for y in range(h):
        line = ""
        for x in range(w):
            l = 0
            while layers[l][x + (y * w)] == "2":
                l += 1
            line += layers[l][x + (y * w)]
        print(line)
    

This prints an image, but it’s hard to read:

    
    
    $ time python3 day8.py 08-puzzle_input.txt 
    Part 1: 1330
    Part 2:
    1111001100100101111011110
    1000010010100101000010000
    1110010010111101110011100
    1000011110100101000010000
    1000010010100101000010000
    1000010010100101111010000
    
    real    0m0.046s
    user    0m0.043s
    sys     0m0.004s
    

I’ll replace the 0s with a unicode block character, and the 1s with a space:

    
    
    print(line.replace("0", chr(9608)).replace("1", " "))
    

Now I get an image:

    
    
    $ time python3 day8.py 08-puzzle_input.txt 
    Part 1: 1330
    Part 2:
        ██  ██ ██ █    █    █
     ████ ██ █ ██ █ ████ ████
       ██ ██ █    █   ██   ██
     ████    █ ██ █ ████ ████
     ████ ██ █ ██ █ ████ ████
     ████ ██ █ ██ █    █ ████
    
    real    0m0.032s
    user    0m0.028s
    sys     0m0.004s
    

That’s getting better. It’s actually easier to read if I invest the image,
switching 0 and 1:

    
    
    $ time python3 day8.py 08-puzzle_input.txt 
    Part 1: 1330
    Part 2:
    ████  ██  █  █ ████ ████ 
    █    █  █ █  █ █    █    
    ███  █  █ ████ ███  ███  
    █    ████ █  █ █    █    
    █    █  █ █  █ █    █    
    █    █  █ █  █ ████ █    
    
    real    0m0.048s
    user    0m0.044s
    sys     0m0.004s
    

Here’s an image from my terminal in case the text doesn’t format right:

![image-20191212062113719](https://0xdfimages.gitlab.io/img/image-20191212062113719.png)

## Final Code

    
    
    #!/usr/bin/env python3
    
    import sys
    
    
    w, h = 25, 6
    with open(sys.argv[1], "r") as f:
        pixels = f.read().strip()
    
    layers = [pixels[i : i + w * h] for i in range(0, len(pixels), w * h)]
    
    fewest_0 = min(layers, key=lambda x: x.count("0"))
    print(f"Part 1: {fewest_0.count('1')*fewest_0.count('2')}")
    
    print(f"Part 2:")
    for y in range(h):
        line = ""
        for x in range(w):
            l = 0
            while layers[l][x + (y * w)] == "2":
                l += 1
            line += layers[l][x + (y * w)]
        print(line.replace("1", chr(9608)).replace("0", " "))
    

[« Day7](/adventofcode2019/7)[Day9 »](/adventofcode2019/9)

[](/adventofcode2019/8)

