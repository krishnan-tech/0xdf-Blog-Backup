# Advent of Code 2020: Day 20

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
  * Day20
  * [Day21](/adventofcode2020/21)
  * [Day22](/adventofcode2020/22)
  * [Day23](/adventofcode2020/23)
  * [Day24](/adventofcode2020/24)
  * [Day25](/adventofcode2020/25)

![](https://0xdfimages.gitlab.io/img/aoc2020-20-cover.png)

Day 20 was almost the end of my 2020 Advent of Code. I managed to solve part
one in 15 minutes, but then part two got me for days. I finally solved it, but
I can’t promise pretty code.

## Challenge

The puzzle can be found [here](https://adventofcode.com/2020/day/20). I’m
given a series of tiles, each of which is ten by ten with either `.` or `#`
like:

    
    
    Tile 2311:
    ..##.#..#.
    ##..#.....
    #...##..#.
    ####.#...#
    ##.##.###.
    ##...#.###
    .#.#.#..##
    ..#....#..
    ###...#.#.
    ..###..###
    

I’ll need to find a way to arrange the given tiles such that the any two tiles
sharing a border have the same pattern on that border like these three:

    
    
    #...##.#..  ..###..###  #.#.#####.
    ..#.#..#.#  ###...#.#.  .#..######
    .###....#.  ..#....#..  ..#.......
    ###.##.##.  .#.#.#..##  ######....
    .###.#####  ##...#.###  ####.#..#.
    .##.#....#  ##.##.###.  .#...#.##.
    #...######  ####.#...#  #.#####.##
    .....#..##  #...##..#.  ..#.###...
    #.####...#  ##..#.....  ..#.......
    #.##...##.  ..##.#..#.  ..#.###...
    

The tiles can be rotated and flipped to get there.

The solution to part one is to find that layout and return the product of the
four ids of the corners of the resulting map.

In part two, I’m asked to remove the edges (they are just used for
orientation), and then look for sea monsters in the resulting image, again,
with rotations and flips:

    
    
                      # 
    #    ##    ##    ###
     #  #  #  #  #  #   
    

For each sea monster, I can change those to `O` and then count the remaining
`#`.

## Solution

### Part 1

I’ll read in the tile list, breaking on double newline. I’ll keep a dictionary
of `tiles`, where the key is the id, and the rest holds information about the
tile. I’ll loop over the raw tiles, pulling the id from the first line, and
then the grid from the rest. I’ll also record the sides (both forward and
backwards) . Then I’ll loop over the tiles that are already recorded and look
for any shared sides. If they are found, I’ll record them as `neighbors`:

    
    
    with open(sys.argv[1], 'r') as f:
        tiles_raw = f.read().strip().split('\n\n')
    
    tiles = {}
    
    for raw_tile in tiles_raw:
        lines = raw_tile.strip('\n').split('\n')
        idn = int(lines[0].split()[1].strip(':'))
        grid = lines[1:]
        sides = [grid[0], grid[-1], ''.join([g[0] for g in grid]), ''.join([g[-1] for g in grid])]
        sides += [s[::-1] for s in sides]
        tiles[idn] = {"grid": grid, "sides": sides, 'neighbors': {}}
    
        for i, tile in tiles.items():
            if i == idn:
                continue
            shared = [s for s in tile['sides'] if s in sides]
            for s in shared:
                tiles[idn]['neighbors'][i] = s
                tiles[i]['neighbors'][idn] = s
    

With that information, finding the corners is just finding the tiles with only
two neighbors:

    
    
    corners = list(map(int, [t for t in tiles if len(tiles[t]['neighbors']) == 2]))
    res = 1
    for c in corners:
        res *= c
    
    print(f'Part 1: {res}')
    

### Part 2

This is where it gets crazy. First, I need to lay all the tiles together into
a big grid. I’ll pick a corner arbitrarily, and then start working through
it’s neighbors looking for one that matches the right side. I created a few
helper functions:

    
    
    def get_side(tile, side):
        if side == "top":
            return tile[0]
        if side == "bottom":
            return tile[-1][::-1]
        if side == "right":
            return "".join([t[-1] for t in tile])
        if side == "left":
            return "".join([t[0] for t in tile])[::-1]
        raise ValueError
    
    
    def get_sides(tile):
        return [get_side(tile, "top"), get_side(tile, "right"), get_side(tile, "bottom"), get_side(tile, "left")]
    
    
    def rotate(tile):
        R = len(tile)
        C = len(tile[0])
        new = [["x" for _ in range(C)] for _ in range(R)]
        for r in range(R):
            for c in range(C):
                new[r][c] = tile[C - c - 1][r]
        return ["".join(r) for r in new]
    
    
    def flip(tile):
        return tile[::-1]
    
    

I’m going to store the combined image in an array of strings, so I created
another helper to add a tile to the array, either to the end of the current
row, or to the start of a new row of tiles:

    
    
    def add_fullpic(tile, newline=False):
        global fullpic
        if fullpic == []:
            fullpic = deepcopy(tile)
        elif newline:
            for r in tile:
                fullpic.append(r)
        else:
            R = len(fullpic) - len(tile)
            for r in range(len(tile)):
                fullpic[r + R] += tile[r]
    

Now I’ll create a loop while there are tiles that are not yet added. At a high
level, it looks like:

    
    
    r, c = 0, 0
    gridmap = {}
    fullpic = []
    
    while not len(gridmap) == len(tiles):
        if r == 0 and c == 0:
            #add corner to fullpic
            ...[snip]...
            c += 1
        elif c == 0:
            # add new tile based on first tile in previous row's bottom
            ...[snip]...
            c += 1
        else:
            # look for next in row
            ...[snip]...
            if find next:
                # add to row
                ...[snip]...
                c += 1
            else:
                r, c = r + 1, 0
    

This is where the code gets a bit ugly and I can’t stand to spend time
cleaning it up. For the first tile, I’ll add it, and rotate it until the
bottom and right sides match the sides listed as neighbors:

    
    
        if r == 0 and c == 0:
            idn = corners[0]
            tile = tiles[idn]["grid"]
            neighbors = list(tiles[idn]["neighbors"].values())
            neighbors += [n[::-1] for n in neighbors]
            while True:
                bottom, right = get_side(tile, "bottom"), get_side(tile, "right")
                if bottom in neighbors and right in neighbors:
                    break
                tile = rotate(tile)
            gridmap[(r, c)] = idn
            tiles[idn]["grid"] = tile
            add_fullpic(tile)
            c += 1
    

For other first tiles in a row, I’ll get the tile from the above tile’s
neighbor list, and rotate / flip until it matches the bottom:

    
    
        elif c == 0:
            p_idn = gridmap[(r - 1, c)]
            p_tile = tiles[p_idn]["grid"]
            side_options = [get_side(p_tile, "bottom"), get_side(p_tile, "bottom")[::-1]]
            idn = [i for i, s in tiles[p_idn]["neighbors"].items() if s in side_options][0]
            tile = tiles[idn]["grid"]
            n_side = get_side(tiles[p_idn]["grid"], "bottom")
            found = False
            for i in range(8):
                if i == 4:
                    tile = flip(tile)
                if get_side(tile, "top") == n_side[::-1]:
                    found = True
                    break
                tile = rotate(tile)
            if not found:
                raise
            gridmap[(r, c)] = idn
            tiles[idn]["grid"] = tile
            add_fullpic(tile, newline=True)
            c += 1
    

It’s important to note that there are only eight orientations for each tile.
Four rotations, flip on either edge, and then four more rotations.

Finally, when looking to grow an existing row, I’ll look to see if there are
any neighbors that match the right side of the last tile. If there’s one, I’ll
rotate/flip it until it matches, and add it. If there are none, I’ll go to the
next row:

    
    
        else:
            p_idn = idn
            p_tile = tiles[p_idn]["grid"]
            side_options = [get_side(p_tile, "right"), get_side(p_tile, "right")[::-1]]
            idn = [i for i, s in tiles[p_idn]["neighbors"].items() if s in side_options]
            if len(idn) == 1:
                idn = idn[0]
                tile = tiles[idn]["grid"]
                n_side = get_side(tiles[p_idn]["grid"], "right")
                found = False
                for i in range(8):
                    if i == 4:
                        tile = flip(tile)
                    if get_side(tile, "left") == n_side[::-1]:
                        found = True
                        break
                    tile = rotate(tile)
                if not found:
                    raise
                gridmap[(r, c)] = idn
                tiles[idn]["grid"] = tile
                add_fullpic(tile)
                c += 1
    
    

At this point, I have the assembled image. Now I need to remove the edges.

    
    
    G = []
    for i in range(len(fullpic) // 10):
        G.extend(fullpic[(10 * i) + 1 : (10 * i) + 9])
    G = ["".join([r[(10 * c) + 1 : (10 * c) + 9] for c in range(len(r) // 10)]) for r in G]
    

The first loop removes the extra rows, and the second the extra columns.

Next is the monster. I’ll define the monster as a series of offsets to some
point:

    
    
    monster = [(0, 1), (1, 2), (4, 2), (5, 1), (6, 1), (7, 2), (10, 2), (11, 1),
               (12, 1), (13, 2), (16, 2), (17, 1), (18, 0), (18, 1), (19, 1)]
    

I’ll loop over the grid for each orientation checking if the point is the
start of the monster, and if so, add all the monster points to a set. If there
were overlapping monsters, this would account for that (there aren’t, so I
could have just counted that and multiplied by the size of the monster at the
end).

    
    
    mon = set()
    for i in range(8):
        if i == 4:
            G = flip(G)
        for r in range(len(G) - 2):
            for c in range(len(G[0]) - 20):
                if all([G[r + dr][c + dc] == "#" for dc, dr in monster]):
                    for dc, dr in monster:
                        mon.add((r + dr, c + dc))
        G = rotate(G)
    
    part2 = len([c for r in G for c in r if c == "#"]) - len(mon)
    print(f"Part 2: {part2}")
    

### Final Code

This is all relatively fast, in around half a second:

    
    
    $ time python3 day20-clean.py 20-puz 
    Part 1: 12519494280967
    Part 2: 2442
    
    real    0m0.486s
    user    0m0.472s
    sys     0m0.005s
    

This code is pretty ugly, but it works:

    
    
    #!/usr/bin/env python3
    
    import sys
    from copy import deepcopy
    
    
    def get_side(tile, side):
        if side == "top":
            return tile[0]
        if side == "bottom":
            return tile[-1][::-1]
        if side == "right":
            return "".join([t[-1] for t in tile])
        if side == "left":
            return "".join([t[0] for t in tile])[::-1]
        raise ValueError
    
    
    def get_sides(tile):
        return [get_side(tile, "top"), get_side(tile, "right"), get_side(tile, "bottom"), get_side(tile, "left")]
    
    
    def rotate(tile):
        R = len(tile)
        C = len(tile[0])
        new = [["x" for _ in range(C)] for _ in range(R)]
        for r in range(R):
            for c in range(C):
                new[r][c] = tile[C - c - 1][r]
        return ["".join(r) for r in new]
    
    
    def flip(tile):
        return tile[::-1]
    
    
    def add_fullpic(tile, newline=False):
        global fullpic
        if fullpic == []:
            fullpic = deepcopy(tile)
        elif newline:
            for r in tile:
                fullpic.append(r)
        else:
            R = len(fullpic) - len(tile)
            for r in range(len(tile)):
                fullpic[r + R] += tile[r]
    
    
    with open(sys.argv[1], "r") as f:
        tiles_raw = f.read().strip().split("\n\n")
    
    tiles = {}
    
    for raw_tile in tiles_raw:
        lines = raw_tile.strip("\n").split("\n")
        idn = int(lines[0].split()[1].strip(":"))
        grid = lines[1:]
        sides = get_sides(grid)
        sides += [s[::-1] for s in sides]
        tiles[idn] = {"grid": grid, "sides": sides, "neighbors": {}}
    
        for i, tile in tiles.items():
            if i == idn:
                continue
            shared = [s for s in tile["sides"] if s in sides[:4]]
            for s in shared:
                tiles[idn]["neighbors"][i] = s
                tiles[i]["neighbors"][idn] = s
    
    corners = list(map(int, [t for t in tiles if len(tiles[t]["neighbors"]) == 2]))
    res = 1
    for c in corners:
        res *= c
    
    print(f"Part 1: {res}")
    
    r, c = 0, 0
    gridmap = {}
    fullpic = []
    
    while not len(gridmap) == len(tiles):
        if r == 0 and c == 0:
            idn = corners[0]
            tile = tiles[idn]["grid"]
            neighbors = list(tiles[idn]["neighbors"].values())
            neighbors += [n[::-1] for n in neighbors]
            while True:
                bottom, right = get_side(tile, "bottom"), get_side(tile, "right")
                if bottom in neighbors and right in neighbors:
                    break
                tile = rotate(tile)
            gridmap[(r, c)] = idn
            tiles[idn]["grid"] = tile
            add_fullpic(tile)
            c += 1
        elif c == 0:
            p_idn = gridmap[(r - 1, c)]
            p_tile = tiles[p_idn]["grid"]
            side_options = [get_side(p_tile, "bottom"), get_side(p_tile, "bottom")[::-1]]
            idn = [i for i, s in tiles[p_idn]["neighbors"].items() if s in side_options][0]
            tile = tiles[idn]["grid"]
            n_side = get_side(tiles[p_idn]["grid"], "bottom")
            found = False
            for i in range(8):
                if i == 4:
                    tile = flip(tile)
                if get_side(tile, "top") == n_side[::-1]:
                    found = True
                    break
                tile = rotate(tile)
            if not found:
                raise
            gridmap[(r, c)] = idn
            tiles[idn]["grid"] = tile
            add_fullpic(tile, newline=True)
            c += 1
        else:
            p_idn = idn
            p_tile = tiles[p_idn]["grid"]
            side_options = [get_side(p_tile, "right"), get_side(p_tile, "right")[::-1]]
            idn = [i for i, s in tiles[p_idn]["neighbors"].items() if s in side_options]
            if len(idn) == 1:
                idn = idn[0]
                tile = tiles[idn]["grid"]
                n_side = get_side(tiles[p_idn]["grid"], "right")
                found = False
                for i in range(8):
                    if i == 4:
                        tile = flip(tile)
                    if get_side(tile, "left") == n_side[::-1]:
                        found = True
                        break
                    tile = rotate(tile)
                if not found:
                    raise
                gridmap[(r, c)] = idn
                tiles[idn]["grid"] = tile
                add_fullpic(tile)
                c += 1
            elif len(idn) == 0:
                r, c = r + 1, 0
            else:
                raise Exception
    
    G = []
    for i in range(len(fullpic) // 10):
        G.extend(fullpic[(10 * i) + 1 : (10 * i) + 9])
    G = ["".join([r[(10 * c) + 1 : (10 * c) + 9] for c in range(len(r) // 10)]) for r in G]
    
    monster = [(0, 1), (1, 2), (4, 2), (5, 1), (6, 1), (7, 2), (10, 2), (11, 1),
               (12, 1), (13, 2), (16, 2), (17, 1), (18, 0), (18, 1), (19, 1)]
    
    mon = set()
    for i in range(8):
        if i == 4:
            G = flip(G)
        for r in range(len(G) - 2):
            for c in range(len(G[0]) - 20):
                if all([G[r + dr][c + dc] == "#" for dc, dr in monster]):
                    for dc, dr in monster:
                        mon.add((r + dr, c + dc))
        G = rotate(G)
    
    part2 = len([c for r in G for c in r if c == "#"]) - len(mon)
    print(f"Part 2: {part2}")
    
    

[« Day19](/adventofcode2020/19)[Day21 »](/adventofcode2020/21)

[](/adventofcode2020/20)

