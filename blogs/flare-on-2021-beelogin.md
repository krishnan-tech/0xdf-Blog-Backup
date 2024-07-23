# Flare-On 2021: beelogin

[flare-on](/tags#flare-on ) [ctf](/tags#ctf ) [flare-on-beelogin](/tags#flare-
on-beelogin ) [reverse-engineering](/tags#reverse-engineering )
[javascript](/tags#javascript ) [jsfuck](/tags#jsfuck ) [de4js](/tags#de4js )
[python](/tags#python ) [bruteforce](/tags#bruteforce )
[deobfuscation](/tags#deobfuscation )  
  
Oct 28, 2021

  * [[1] credchecker](/flare-on-2021/credchecker)
  * [[2] known](/flare-on-2021/known)
  * [[3] antioch](/flare-on-2021/antioch)
  * [[4] myaquaticlife](/flare-on-2021/myaquaticlife)
  * [[5] FLARE Linux VM](/flare-on-2021/flarelinuxvm)
  * [[6] PetTheKitty](/flare-on-2021/petthekitty)
  * [[7] spel](/flare-on-2021/spel)
  * [8] beelogin
  * [9] evil - no writeup :(
  * [[10] wizardcult](/flare-on-2021/wizardcult)

![beelogin](https://0xdfimages.gitlab.io/img/flare2021-beelogin-cover.png)

beelogin starts with a simple HTML page with five input fields. Diving into
the source, there’s almost sixty thousand lines of JavaScript. The vast
majority of that ends up being junk that isn’t run. I’ll trim it down to
around 30 lines. Then there’s some math to track where each of 64 bytes in the
key impact which bytes of the result. Once I have that, I can check for bytes
that produce valid JavaScript, and find the key. The result is some obfuscated
JavaScript that comes out to be doing the same thing again, on the second half
of the key. Once I have both halves, I can get the flag or put the key in and
get the page to give it to me.

## Challenge

> You’re nearly done champ, just a few more to go. we put all the hard ones at
> the beginning of the challenge this year so its smooth sailing from this
> point. Call your friends, tell ‘em you won. They probably don’t care. Flare-
> On is your only friend now.

The [download](/files/flare2021-08_beelogin.7z) (password “flare”) has an HTML
document:

    
    
    $ file beelogin.html 
    beelogin.html: HTML document, ASCII text, with very long lines, with CRLF, LF line terminators
    

The file is quite long, 59,090 lines, 271,350 words, and over three million
characters:

    
    
    $ wc beelogin.html
      59090  271350 3252550 beelogin.html
    

## Running It

Opening it in Firefox shows a background that looks like an advertisement for
Bee Movie, with five input fields and a Submit button:

[![image-20211004063221738](https://0xdfimages.gitlab.io/img/image-20211004063221738.png)_Click
for full size
image_](https://0xdfimages.gitlab.io/img/image-20211004063221738.png)

Pushing the submit button doesn’t seem to do anything regardless of any data
guessed in the various inputs.

## RE

### Overview

The top of the file is some static HTML

    
    
    <!DOCTYPE HTML>
    <html>
        <head>
            <title>beelogin</title>
        </head>
        <style>
            body {
    ...[snip]...
        </style>
        <body>
            <form onsubmit="Add(this)">  
            <input type="Password" name="LLfYTmPiahzA3WFXKcL5BczcG1s1" id="LLfYTmPiahzA3WFXKcL5BczcG1s1" placeholder="LLfYTmPiahzA3WFXKcL5BczcG1s1"><br><br>
            <input type="Password" name="qpZZCMxP2sDKX1PZU6sSMfBJA" id="qpZZCMxP2sDKX1PZU6sSMfBJA" placeholder="qpZZCMxP2sDKX1PZU6sSMfBJA"><br><br>
            <input type="Password" name="ZuAHehme2RWulqFbEWBW" id="ZuAHehme2RWulqFbEWBW" placeholder="ZuAHehme2RWulqFbEWBW"><br><br>
            <input type="Password" name="ZJqLM97qEThEw2Tgkd8VM5OWlcFN6hx4y2" id="ZJqLM97qEThEw2Tgkd8VM5OWlcFN6hx4y2" placeholder="ZJqLM97qEThEw2Tgkd8VM5OWlcFN6hx4y2"><br><br>
            <input type="Password" name="Xxb6fjAi1J1HqcZJIpFv16eS" id="Xxb6fjAi1J1HqcZJIpFv16eS" placeholder="Xxb6fjAi1J1HqcZJIpFv16eS"><br><br>
            <div><input id="submit" type="submit"></div>
            </form>
    ...[snip]...
    

The rest of the file falls between a `<script>` tag:

![image-20211004092145870](https://0xdfimages.gitlab.io/img/image-20211004092145870.png)

Where the close close for that is at the very end of the file:

![image-20211004092210442](https://0xdfimages.gitlab.io/img/image-20211004092210442.png)

In fact, the entire script is one function, `Add`, which is called by the
`<form>` tag `onsubmit` and passed the form itself. So in the script,
`xDyuf5ziRN1SvRgcaYDiFlXE3AwG` will be the form.

### Chaff

There’s a ton of stuff in this JavaScript that just isn’t ever used. Tons of
functions are defined and never called. There’s also a bunch of lines that
look like:

    
    
    BntQj9FBk=xDyuf5ziRN1SvRgcaYDiFlXE3AwG.LLfYTmPiahzA3WFXKcL5BczcG1s1.value.split(';')
    if('rFzmLyTiZ6AHlL1Q4xV7G8pW32'>=BntQj9FBk)eval(BntQj9FBk)
    vwXaWQUif35pQPp1HRk=xDyuf5ziRN1SvRgcaYDiFlXE3AwG.LLfYTmPiahzA3WFXKcL5BczcG1s1.value.split(';')
    

All but one of those are never used. The one that is used is actually based on
the forth input field:

    
    
    qguBomGfcTZ6L4lRxS0TWx1IwG=xDyuf5ziRN1SvRgcaYDiFlXE3AwG.ZJqLM97qEThEw2Tgkd8VM5OWlcFN6hx4y2.value.split(';')
    

There is a giant Base64 blob on line 4310:

![image-20211027205511932](https://0xdfimages.gitlab.io/img/image-20211027205511932.png)

This is the first line that actually runs, and putting a break point here
allows me to single step and see the next lines call, which is useful in
cleaning out all the garbage.

### Algorithm

By steping through and cleaning up, I end up with the following pseudocode
that repsents what the JavaScript is doing:

    
    
    pyk = "[big b64 blob]"
    gjr = "b2JDN2luc2tiYXhLOFZaUWRRWTlSeXdJbk9lVWxLcHlrMXJsRnk5NjJaWkQ4SHdGVjhyOENQeFE5dGxUaEd1dGJ5ZDNOYTEzRmZRN1V1emxkZUJQNTN0Umt6WkxjbDdEaU1KVWF1M29LWURzOGxUWFR2YjJqQW1HUmNEU2RRcXdFSERzM0d3emhOaGVIYlE3dm9aeVJTMHdLY2Vhb3YyVGQ4UnQ2SXUwdm1ZbGlVYjA4YVRES2xESnlXU3NtZENMN0J4MnBYdlZET3RUSmlhY2V6Y3B6eUM2Mm4yOWs=";
    l = 64
    qgu = ZJInput.split(';')
    npx = atob(pyk)
    pef = npx.length
    euf = atob(gjr)
    bnt = 'gflsdgfdjgflkdsfjg4980utjkfdskfglsldfgjJLmSDA49sdfgjlfdsjjqdgjfj'
    if(qgu[0].length==l){
        bnt=qgu[0]
    }
    for(i=0; i < euf.length; i++) {
        euf[i] = (euf[i] + bnt[i%l]) & 0xff
    }
    oz9 = npx
    for(i=0; i<pef; i++) {
        oz9[i] = (oz9[i] - euf[i%euf.length]) & 0xff
    }
    sej = ""
    for(i=0; i < npx.length; i++) {
        sej += oz9[i]
    }
    eval(sej);
    

There’s two blogs of base64 data, “big blob” (`pyk` above which decodes to
`npx`), and “little blob” (`gjr` above which decodes to `euf`). The input in
the forth input field is split on `;` and the first result is stored in `bnt`
if it’s exactly 64 characters in length.

Then there’s a loop over the smaller decoded blob, adding the corresponding
byte from the input (and looping to the start of the input when it reaches the
end). Then it loops over the big blob, subtracting the corresponding byte in
the small blob (and looped when it reaches the end).

## Key First Half

### Find Pattern

#### Theory

Let’s say I had two buffers that we 5 and 18 bytes long. In the example above,
the key would be 5 (instead of 64), and the small blob decoded would be 18
(instead of 221 bytes). So by messing with the first byte in the key, the
small blob would see changes at the green positions:

![image-20211028061605900](https://0xdfimages.gitlab.io/img/image-20211028061605900.png)

If that was then applied to a bigger buffer (say 60 bytes), the pattern would
look like:

![image-20211028061616210](https://0xdfimages.gitlab.io/img/image-20211028061616210.png)

It’s changing every fifth byte up to the length of 18, then it starts over.

Some character is impacted by the first byte in the key if:

\\[(pos\mod{18})\mod{5} = 0\\]

The second byte if that is 1, third if 2, etc.

So for example, position 23:

\\[(23\mod{18})\mod{5} = 5\mod{5} = 0\\]

It becomes 5 and then 0, which is why it’s green in the image, impacted by key
position 0. Looking at 30:

\\[(30\mod{18})\mod{5} = 12\mod{5} = 2\\]

So position 30 is impacted by the second byte of this five byte key.

#### Brute Forcing

To see it a different way, I wrote a simple program to look at the impact of
changing the key at one position:

    
    
    #!/usr/bin/env python3
    
    import sys
    from base64 import b64decode
    from itertools import cycle
    
    
    try:
        pos = int(sys.argv[1])
    except:
        pos = 0
    
    with open('PyKEvIqAmUkUVL0Anfn9FElFUN2dic3z.base64', 'r') as f:
        pyk = f.read()
    gjr =  "b2JDN2luc2tiYXhLOFZaUWRRWTlSeXdJbk9lVWxLcHlrMXJsRnk5NjJaWkQ4SHdGVjhyOENQeFE5dGxUaEd1dGJ5ZDNOYTEzRmZRN1V1emxkZUJQNTN0Umt6WkxjbDdEaU1KVWF1M29LWURzOGxUWFR2YjJqQW1HUmNEU2RRcXdFSERzM0d3emhOaGVIYlE3dm9aeVJTMHdLY2Vhb3YyVGQ4UnQ2SXUwdm1ZbGlVYjA4YVRES2xESnlXU3NtZENMN0J4MnBYdlZET3RUSmlhY2V6Y3B6eUM2Mm4yOWs=";
    
    npx = b64decode(pyk)
    pef = len(npx)
    euf = b64decode(gjr)
    
    key1 = b"a" * 64
    key2 = b"a" * pos + b"b" + b"a" * (63-pos)
    
    euf_key1 = [(x+y)&0xff for x,y in zip(euf, cycle(key1))]
    euf_key2 = [(x+y)&0xff for x,y in zip(euf, cycle(key2))]
    
    oz9_k1 = [(x-y)&0xff for x,y in zip(npx, cycle(euf_key1))]
    oz9_k2 = [(x-y)&0xff for x,y in zip(npx, cycle(euf_key2))]
    
    for i in range(5000):
        if oz9_k1[i] != oz9_k2[i]:
            print(f'{i}, ', end="")
    print()
    

It will read in the two buffers and decode them, and create two keys. The
first is all “a”. The second is all “a” except for one “b”. It then generates
the resulting buffers for each, and prints any characters in the first 5000
that are different. So changing the first character changes:

    
    
    $ python get_changes.py 0
    0, 64, 128, 192, 221, 285, 349, 413, 442, 506, 570, 634, 663, 727, 791, 855, 884, 948, 1012, 1076, 1105, 1169, 1233, 1297, 1326, 1390, 1454, 1518, 1547, 1611, 1675, 1739, 1768, 1832, 1896, 1960, 1989, 2053, 2117, 2181, 2210, 2274, 2338, 2402, 2431, 2495, 2559, 2623, 2652, 2716, 2780, 2844, 2873, 2937, 3001, 3065, 3094, 3158, 3222, 3286, 3315, 3379, 3443, 3507, 3536, 3600, 3664, 3728, 3757, 3821, 3885, 3949, 3978, 4042, 4106, 4170, 4199, 4263, 4327, 4391, 4420, 4484, 4548, 4612, 4641, 4705, 4769, 4833, 4862, 4926, 4990, 
    

The change impacts every 64 bytes until it reaches 221, where it starts over.
This fits the double mod equations shown above. Changing other bytes shows the
same behavior:

    
    
    $ python get_changes.py 1
    1, 65, 129, 193, 222, 286, 350, 414, 443, 507, 571, 635, 664, 728, 792, 856, 885, 949, 1013, 1077, 1106, 1170, 1234, 1298, 1327, 1391, 1455, 1519, 1548, 1612, 1676, 1740, 1769, 1833, 1897, 1961, 1990, 2054, 2118, 2182, 2211, 2275, 2339, 2403, 2432, 2496, 2560, 2624, 2653, 2717, 2781, 2845, 2874, 2938, 3002, 3066, 3095, 3159, 3223, 3287, 3316, 3380, 3444, 3508, 3537, 3601, 3665, 3729, 3758, 3822, 3886, 3950, 3979, 4043, 4107, 4171, 4200, 4264, 4328, 4392, 4421, 4485, 4549, 4613, 4642, 4706, 4770, 4834, 4863, 4927, 4991, 
    $ python get_changes.py 63
    63, 127, 191, 284, 348, 412, 505, 569, 633, 726, 790, 854, 947, 1011, 1075, 1168, 1232, 1296, 1389, 1453, 1517, 1610, 1674, 1738, 1831, 1895, 1959, 2052, 2116, 2180, 2273, 2337, 2401, 2494, 2558, 2622, 2715, 2779, 2843, 2936, 3000, 3064, 3157, 3221, 3285, 3378, 3442, 3506, 3599, 3663, 3727, 3820, 3884, 3948, 4041, 4105, 4169, 4262, 4326, 4390, 4483, 4547, 4611, 4704, 4768, 4832, 4925, 4989,
    

### Find First Key

#### Find Possible Keys

I wrote another Python program to brute force all possible key bytes that
produced valid JavaScript characters:

    
    
    #!/usr/bin/env python3
    
    import sys
    from base64 import b64decode
    from collections import defaultdict
    from itertools import cycle
    from string import printable, ascii_letters, digits
    
    
    with open('PyKEvIqAmUkUVL0Anfn9FElFUN2dic3z.base64', 'r') as f:
        pyk = f.read()
    gjr = "b2JDN2luc2tiYXhLOFZaUWRRWTlSeXdJbk9lVWxLcHlrMXJsRnk5NjJaWkQ4SHdGVjhyOENQeFE5dGxUaEd1dGJ5ZDNOYTEzRmZRN1V1emxkZUJQNTN0Umt6WkxjbDdEaU1KVWF1M29LWURzOGxUWFR2YjJqQW1HUmNEU2RRcXdFSERzM0d3emhOaGVIYlE3dm9aeVJTMHdLY2Vhb3YyVGQ4UnQ2SXUwdm1ZbGlVYjA4YVRES2xESnlXU3NtZENMN0J4MnBYdlZET3RUSmlhY2V6Y3B6eUM2Mm4yOWs=";
    
    npx = b64decode(pyk)
    pef = len(npx)
    euf = b64decode(gjr)
    leuf = len(euf)
    
    shifted = [(x-y) for x,y in zip(npx, cycle(euf))]
    key = ['a'] * 64
    for i in range(64):
        print(f"\n[{i:02d}] ", end="")
        res = [shifted[j] for j in range(pef) if (j % leuf) % 64 == i]
        #for c in printable[:-2]:
        for c in ascii_letters + digits:
            if all(chr((x-ord(c)) % 256) in printable[:-2] for x in res):
                print(c, end="")
                key[i] = c
                print(f'\n{"".join(key)}')
    

For each byte in the key, it calculates and collects the intermediate values
for all the characters that are impacted by that byte (that’s what `if (j %
leuf) % 64) == i` selects for).

Then it loops over letters and digits looking for any that make all valid
output.

The result looks like:

    
    
    oxdf@hacky[~/flare/08-beelogin]$ python brute.py 
    
    [00] C
    [01] cdefgh
    [02] V
    [03] C
    [04] SV
    [05] Y
    [06] wz
    [07] I
    [08] 1
    [09] ad
    [10] U
    [11] 9
    [12] c
    [13] V
    [14] g
    [15] 1
    [16] u
    [17] k
    [18] B
    [19] nq
    [20] O
    [21] 2
    [22] u
    [23] 4
    [24] RU
    ...[snip]...
    [57] m
    [58] K
    [59] B
    [60] CDEFGH
    [61] PQRSTU
    [62] RSTUVW
    [63] I
    ChVCVYzI1dU9cVg1ukBqO2u4UGr9aVCNWHpMUuYDLmDO22cdhXq3oqp8jmKBHUWI
    

It’s not completely unambiguous, but it’s close enough that I can give it a
look. I updated the script to allow me to pass in a key and see the results:

    
    
    #!/usr/bin/env python3
    
    import sys
    from base64 import b64decode
    from collections import defaultdict
    from itertools import cycle
    from string import printable, ascii_letters, digits
    
    
    with open('PyKEvIqAmUkUVL0Anfn9FElFUN2dic3z.base64', 'r') as f:
        pyk = f.read()
    gjr = "b2JDN2luc2tiYXhLOFZaUWRRWTlSeXdJbk9lVWxLcHlrMXJsRnk5NjJaWkQ4SHdGVjhyOENQeFE5dGxUaEd1dGJ5ZDNOYTEzRmZRN1V1emxkZUJQNTN0Umt6WkxjbDdEaU1KVWF1M29LWURzOGxUWFR2YjJqQW1HUmNEU2RRcXdFSERzM0d3emhOaGVIYlE3dm9aeVJTMHdLY2Vhb3YyVGQ4UnQ2SXUwdm1ZbGlVYjA4YVRES2xESnlXU3NtZENMN0J4MnBYdlZET3RUSmlhY2V6Y3B6eUM2Mm4yOWs=";
    
    npx = b64decode(pyk)
    pef = len(npx)
    euf = b64decode(gjr)
    leuf = len(euf)
    
    if len(sys.argv) == 1:
        shifted = [(x-y) for x,y in zip(npx, cycle(euf))]
        key = ['a'] * 64
        for i in range(64):
            print(f"\n[{i:02d}] ", end="")
            res = [shifted[j] for j in range(pef) if (j % leuf) % 64 == i]
            #for c in printable[:-2]:
            for c in ascii_letters + digits:
                if all(chr((x-ord(c)) % 256) in printable[:-2] for x in res):
                    print(c, end="")
                    key[i] = c
        print(f'\n{"".join(key)}')
    else:
        key = sys.argv[1].encode()
        mod_key = [x+y for x,y in zip(euf, cycle(key))]
        res = ''.join([chr((x-y) % 256) for x,y in zip(npx, cycle(mod_key))])
        print(res)
    

#### Find Key

I can start with the key from my script, which happens to be taking the last
possible key for each option. The idea was I can change each character to
other options in the list above as needed. But it turns out taking the last in
each option is the right answer, and the key above is correct:
ChVCVYzI1dU9cVg1ukBqO2u4UGr9aVCNWHpMUuYDLmDO22cdhXq3oqp8jmKBHUWI.

The resulting text is starts with a bunch of Bee Movie quotes commented out:

    
    
    //Yes, but who can deny the heart that is yearning?
    //Affirmative!
    //Uh-oh!
    //This.
    //At least you're out in the world. You must meet girls.
    //Why is yogurt night so difficult?!
    //I feel so fast and free!
    //Good idea! You can really see why he's considered one of the best lawyers...
    //One's bald, one's in a boat, they're both unconscious!
    //You know what a Cinnabon is?
    //Just one. I try not to use the competition.
    //Heads up! Here we go.
    //Whose side are you on?
    //Did you ever think, "I'm a kid from The Hive. I can't do this"?
    //Can I get help with the Sky Mall magazine? I'd like to order the talking inflatable nose and ear hair trimmer.
    //It's a close community.
    //Which one?
    ...[snip]...
    

Then comes obfuscated JS:

![image-20211027214342424](https://0xdfimages.gitlab.io/img/image-20211027214342424.png)

## Key Second Half

### De-JS-fuck

I saved that output to a file, and removed the comment lines. The result is
what is called [JSFuck](http://www.jsfuck.com/). According to it’s own page:

> JSFuck is an esoteric and educational programming style based on the atomic
> parts of JavaScript. It uses only six different characters to write and
> execute code.

It’s a complete language that is legit JavaScript using only 6 characters:
`()[]+!`. This is clearly that.

There are a lot of online JS deobfuscators that claim to deobfuscate JSFuck,
but most crashed when I gave them such a long program. But
[de4js](https://lelinhtinh.github.io/de4js/) handled it beautifuly. I’ll
upload the file here, and get the results:

[![image-20211005140626948](https://0xdfimages.gitlab.io/img/image-20211005140626948.png)_Click
for full size
image_](https://0xdfimages.gitlab.io/img/image-20211005140626948.png)

The resulting JavaScript is:

    
    
    (function (qguBomGfcTZ6L4lRxS0TWx1IwG) {
        sInNWkbompb8pOyDG5D = "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";
        SEN5lpjT4o1WcRyenF3c6EmlnjdnW = "N0l2N2l2RTVDYlNUdk5UNGkxR0lCbTExZmI4YnZ4Z0FpeEpia2NGN0xGYUh2N0dubWl2ZFpOWm15c0JMVDFWeHV3ZFpsd2JvdTVSTW1vZndYRGpYdnhrcGJFS0taRnZOMnNJU1haRXlMM2lIWEZtN0RSQThoMG8yYUhjNFZLTGtmOXBDOFR3OUpyT2RwUmFOOUdFck12bXd2dnBzOUVMWVpxRmpnc0ZHTFFtMGV4WW11Wmc1bWRpZWZ6U3FoZUNaOEJiMURCRDJTS1o3SFpNRzcwRndMZ0RCNFFEZWZsSWE4Vg==";
        pKxpcv7X8OO7AY4brDHDibSSlZx2F = atob(sInNWkbompb8pOyDG5D).split('');
        WLjv1KngPLuN8eezUIIj5tGR1ZZgqUZ = pKxpcv7X8OO7AY4brDHDibSSlZx2F.length;
        anFlFCVHqfi4WmTzNxmg = atob(SEN5lpjT4o1WcRyenF3c6EmlnjdnW).split('');
        NbgNroelQqxtLGx4xr2FzHuonetRtscR2 = '87gfds8f4h4dsahfdjhkDHKHF83hNNFDHHKFBDSAKFSfsd47lmkbfjghgdfgda34'.split('');
        if (qguBomGfcTZ6L4lRxS0TWx1IwG[1].length == 64) NbgNroelQqxtLGx4xr2FzHuonetRtscR2 = qguBomGfcTZ6L4lRxS0TWx1IwG[1].split('');
        for (i = 0; i < anFlFCVHqfi4WmTzNxmg.length; i++) {
            anFlFCVHqfi4WmTzNxmg[i] = (anFlFCVHqfi4WmTzNxmg[i].charCodeAt(0) + NbgNroelQqxtLGx4xr2FzHuonetRtscR2[i % 64].charCodeAt(0)) & 0xFF;
        };
        for (i = 0; i < WLjv1KngPLuN8eezUIIj5tGR1ZZgqUZ; i++) {
            pKxpcv7X8OO7AY4brDHDibSSlZx2F[i] = (pKxpcv7X8OO7AY4brDHDibSSlZx2F[i].charCodeAt(0) - anFlFCVHqfi4WmTzNxmg[i % anFlFCVHqfi4WmTzNxmg.length]) & 0xFF;
        };
        pKxpcv7X8OO7AY4brDHDibSSlZx2F = String.fromCharCode.apply(null, pKxpcv7X8OO7AY4brDHDibSSlZx2F);
        if ('rFzmLyTiZ6AHlL1Q4xV7G8pW32' >= Oz9nOiwWfRL6yjIwvM4OgaZMIt0B) eval(pKxpcv7X8OO7AY4brDHDibSSlZx2F);
    })(qguBomGfcTZ6L4lRxS0TWx1IwG);
    

### Dejavu

This code is doing the same thing as the first iteration, except this time it
is taking the second object from the input field split on `;`. I created a
copy of `brute.py` and updated to new buffers, so that it does the same thing
again:

    
    
    $ python3 brute2.py 
    [00] RU
    [01] LMNOPQ
    [02] 8
    [03] y
    [04] gj
    [05] klmnopq
    [06] rstuvw
    [07] A
    [08] k
    [09] o
    [10] V
    [11] DG
    [12] m
    [13] 7
    [14] V
    [15] AD
    [16] d
    [17] h
    [18] L
    [19] lo
    [20] D
    [21] hk
    [22] 0
    [23] Q
    ...[snip]...
    [58] x
    [59] J
    [60] P
    [61] dg
    [62] H
    [63] l
    UQ8yjqwAkoVGm7VDdhLoDk0Q75eKKhTfXXke36UFdtKAi0etRZ3DoHPz7NxJPgHl
    

With the correct key
(UQ8yjqwAkoVGm7VDdhLoDk0Q75eKKhTfXXke36UFdtKAi0etRZ3DoHPz7NxJPgHl), it
produced more commented movie quotes, and some more JSFuck:

    
    
    $ python3 brute2.py UQ8yjqwAkoVGm7VDdhLoDk0Q75eKKhTfXXke36UFdtKAi0etRZ3DoHPz7NxJPgHl | head
    //He's not bothering anybody.
    //Why would you question anything? We're bees.
    //But you've never been a police officer, have you?
    //Up on a float, surrounded by flowers, crowds cheering.
    //According to all known laws of aviation, there is no way a bee should be able to fly.
    //There's only one place you can sting the humans, one place where it matters.
    //I'm kidding. Yes, Your Honor, we're ready to proceed.
    //Can I get help with the Sky Mall magazine? I'd like to order the talking inflatable nose and ear hair trimmer.
    //Maybe I'll pierce my thorax. Shave my antennae. Shack up with a grasshopper. Get a gold tooth and call everybody "dawg"!
    //Did you bring your crazy straw?
    ...[snip]...
    

### Flag

Uploading this JSFuck to [de4js](https://lelinhtinh.github.io/de4js/) returned
a very simple line of JavaScript:

[![image-20211005140823418](https://0xdfimages.gitlab.io/img/image-20211005140823418.png)_Click
for full size
image_](https://0xdfimages.gitlab.io/img/image-20211005140823418.png)

That’s all I need to get the flag.

But also, I know have the key to the site. I can put this flag into the forth
input box:

    
    
    ChVCVYzI1dU9cVg1ukBqO2u4UGr9aVCNWHpMUuYDLmDO22cdhXq3oqp8jmKBHUWI;UQ8yjqwAkoVGm7VDdhLoDk0Q75eKKhTfXXke36UFdtKAi0etRZ3DoHPz7NxJPgHl
    

And on hitting submit:

![image-20211005134209875](https://0xdfimages.gitlab.io/img/image-20211005134209875.png)

**Flag: I_h4d_v1rtU411y_n0_r3h34rs4l_f0r_th4t@flare-on.com**

[](/flare-on-2021/beelogin)

