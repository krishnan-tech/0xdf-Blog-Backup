# Flare-On 2021: myaquaticlife

[flare-on](/tags#flare-on ) [ctf](/tags#ctf ) [flare-on-
myaquaticlife](/tags#flare-on-myaquaticlife ) [reverse-
engineering](/tags#reverse-engineering ) [upx](/tags#upx ) [multimedia-
builder](/tags#multimedia-builder ) [mmunbuilder](/tags#mmunbuilder )
[x64dbg](/tags#x64dbg ) [ghidra](/tags#ghidra ) [python](/tags#python )
[bruteforce](/tags#bruteforce )  
  
Oct 29, 2021

  * [[1] credchecker](/flare-on-2021/credchecker)
  * [[2] known](/flare-on-2021/known)
  * [[3] antioch](/flare-on-2021/antioch)
  * [4] myaquaticlife
  * [[5] FLARE Linux VM](/flare-on-2021/flarelinuxvm)
  * [[6] PetTheKitty](/flare-on-2021/petthekitty)
  * [[7] spel](/flare-on-2021/spel)
  * [[8] beelogin](/flare-on-2021/beelogin)
  * [9] evil - no writeup :(
  * [[10] wizardcult](/flare-on-2021/wizardcult)

![myaquaticlife](https://0xdfimages.gitlab.io/img/flare2021-myaquaticlife-
cover.png)

myaquaticlife was a Windows exe built on a really old multimedia framework,
Multimedia Builder. I’ll use a project on Github to decompile it back to the
framework file, and look at it in the original software. There’s a DLL used as
a plugin that tracks the order of clicks on fish, and I can figure out the
order to click and get the flag.

## Challenge

> What would Flare-On do without a healthy amount of nostalgia for the
> abraisive simplicity of 1990’s UI design? Probably do more actual work and
> less writing fun challenges like this.

The [file](/files/flare2021-04_myaquaticlife.7z) (password “flare”) is a
32-bit Windows executable that is UPX packed:

    
    
    $ file myaquaticlife.exe 
    myaquaticlife.exe: PE32 executable (GUI) Intel 80386, for MS Windows, UPX compressed
    

## Running It

Running it pops open a GUI with a bunch of animals:

![flare2021-myaquaticlife-
cover](https://0xdfimages.gitlab.io/img/flare2021-myaquaticlife-cover.png)

The icon at the top right is a cube with the letters MMB.

I can click on the fish, and it may do something, but then if I click on the
text in the center, a new panel loads:

![image-20210916142312159](https://0xdfimages.gitlab.io/img/image-20210916142312159.png)

## RE

### MMB Project

#### UPX - Fail

Because the binary is UPX packed (see the output of the `file` command above),
I started by decompressing it with `upx` and looking at the result in Ghidra.
This turned out to be a really bad approach. As I eventually figured out, this
binary is built with a framework, and by unpacking it, I found myself reverse
engineering the framework code, not the stuff specific to this binary.

I will actually come back to reversing the unpacked binary later, but with
additional context as to what I’m looking for to get oriented.

#### Decompile

t’s always good to check `strings`, and there’s a really interesting clule at
the very bottom:

    
    
    oxdf@parrot$ strings myaquaticlife.exe
    ...[snip]...
    2n0R
    b3s:
    ]Yek'
    T&)0k
    U rl
    !wYn
            email.gif
    eguxxjihvsV
    MyApp
    1.0.0.01Created with Multimedia Builder, version 4.9.8.13
    STANDALONE
    

[Multimedia Builder](https://www.mediachance.com/mmb/) is old software
designed to create multimedia apps and games with a drap and drop GUI editor
and limited code. The download from their website is disabled (apparently too
much malware was using the framework), but I found a downloadable version
[here](https://www.windows10download.com/multimedia-builder/).

There’s also a project on GitHub,
[MMUnbuilder](https://github.com/qprotex/MMUnbuilder), which will decompile
MMBuilder applications into their project files. The links for additional
information are not working, but I can give the tool a try. It’s six years old
and Python2 only:

    
    
    oxdf@parrot$ python2 /opt/MMUnbuilder/MMUnbuilder.py -u myaquaticlife.exe
          
    MMUnbuilder - v0.1
    Programmed by Miguel Febres - http://www.q-protex.com
                                               
    [+] Opening myaquaticlife.exe
    [+] Checking size...
    [+] Overlay data found in the end of PE file!
    [+] Checking if overlay data is from Multimedia Builder...
    [+] Multimedia Builder format version 30 found!
    [+] Checking if data is compiled with security layer...
    [+] Security Layer not found!
    [+] Saving project...
    [+] Work done!
    

It outputs `myaquaticlife.mbd`:

    
    
    oxdf@parrot$ file myaquaticlife.mbd
    myaquaticlife.mbd: data
    

Unpacking the project wasn’t strictly necessary. It would be totally possible
to just solve this challenge using the files stored in `%TEMP%` (see below).

#### Analysis

I’ll install the MMBuilder application in a Windows VM (snapshotted so I can
revert afterwards since it’s a random download from the internet), and open
the `.mbd`:

![image-20210916142151046](https://0xdfimages.gitlab.io/img/image-20210916142151046.png)

The objects bar on the right has 19 objects - 17 scripts, one browser, and one
plugin.

Double clicking on an object loads a window about it. The browser object shows
a reference to an `index.html`:

![image-20210916142534066](https://0xdfimages.gitlab.io/img/image-20210916142534066.png)

The script objects each have a bit of code. 16 of them are very simple,
looking like:

![image-20210916142615649](https://0xdfimages.gitlab.io/img/image-20210916142615649.png)

Here’s each of the scripts:

Script | Variable | Value | PluginSet  
---|---|---|---  
1 | part1$ | derelict:MZZWP | part1$  
2 | part2$ | lagan:BAJkR | part2$  
3 | part2$ | flotsam:DFWEyEW | part2$  
4 | part1$ | flotsam:PXopvM | part1$  
5 | part2$ | derelict:LDNCVYU | part2$  
6 | part3$ | derelict:yXQsGB | part3$  
7 | part2$ | jetsam:newaui | part2$  
8 | part3$ | lagan:QICMX | part3$  
9 | part1$ | lagan:rOPFG | part1$  
10 | part3$ | jetsam:HwdwAZ | part3$  
11 | part1$ | jetsam:SLdkv | part1$  
12 | part2$ | derelict:LSZvYSFHW | part2$  
13 | part3$ | flotsam:BGgsuhn | part3$  
14 | part4$ | lagan:GTYAKlwER | part2$  
15 | part4$ | derelict:RTYXAc | part4$  
16 | part2$ | lagan:GTXI | part2$  
  
Script17 has a bunch more code:

    
    
    PluginRun("PlugIn","PluginFunc19")
    PluginGet("PlugIn","var1$")
    NextPage()
    LoadVariable("visitors","count")
    count = count + 1
    SaveVariable("visitors","count")
    vc$='Visitor Counter: ' + CHAR(count)
    CreateText("mytext","visitlabel$,1050,580,yippy")
    LoadText("visitlabel$","vc$")
    colr$='TEXTCOLOR=255,0,0'
    SetObjectParam("outlabel$","colr$")
    SetObjectParam("outlabel$","FONTNAME=Comic Sans MS")
    SetObjectParam("outlabel$","FONTSIZE=24")
    colors$[1] = '255,0,0'
    colors$[2] = '0,255,0'
    colors$[3] = '0,0,255'
    colors$[4] = '255,0,0'
    colors$[5] = '0,255,0'
    colors$[6] = '0,0,255'
    colors$[7] = '255,0,0'
    colors$[8] = '0,255,0'
    colors$[9] = '0,0,255'
    colors$[10] = '255,0,0'
    colors$[11] = '0,255,0'
    colors$[12] = '0,0,255'
    colors$[13] = '255,0,0'
    colors$[14] = '0,255,0'
    colors$[15] = '0,0,255'
    For Loop= 1 To 1000
      For Counter= 1 To 15
        CreateText("mytext","outlabel$,20,100 + 50 * Counter,yippy")
        LoadText("outlabel$","var1$")
        colr$='TEXTCOLOR='+colors$[Counter]
        SetObjectParam("outlabel$","colr$")
        SetObjectParam("outlabel$","FONTNAME=Comic Sans MS")
        SetObjectParam("outlabel$","FONTSIZE=48")
        Pause("1000")
        DeleteObject("outlabel$")
      Next Counter
    Next Loop
    

The plugin has a reference to `fathom.dll`:

![image-20210916142658850](https://0xdfimages.gitlab.io/img/image-20210916142658850.png)

#### Files

Knowing that for `fathom.dll` to work, it would have to come with the binary,
I ran it again, and did a search in `c:\users\0xdf\appdata\` for `fathom.dll`,
and found it in `AppData\Local\Temp\MMBPlayer`, along with all the images and
two html pages:

![image-20210916142847632](https://0xdfimages.gitlab.io/img/image-20210916142847632.png)

### Click On Animal

#### Dynamic Analysis

The original file is `upx` packed, so it’s helpful for reversing to have an
unpacked version. `upx -d myaquaticlife.exe` works great. `upx` overwrites the
original file with the unpacked one, but I prefer to move that to
`myaquaticlife-unpacked.exe` so I have a copy of both.

I’ll open the unpacked version in x32dbg. In the Symbols tab, I can filter to
get `fathom.dll`, and put break points at interesting functions:

![image-20210916162732515](https://0xdfimages.gitlab.io/img/image-20210916162732515.png)

I want to understand how clicking on an animal sends data into the plugin.
I’ll start the program from the beginning, and run until it’s waiting for
input. Then I’ll click on the top left swordfish. x32Dbg breaks at `SetFile`,
and I can see the value “derelict:MZZWP” has been passed in:

![image-20210916162929923](https://0xdfimages.gitlab.io/img/image-20210916162929923.png)
![image-20210916162936463](https://0xdfimages.gitlab.io/img/image-20210916162936463.png)

With some clicking around, I can determine a few things:

  * The Script numbers above apply to the animals starting from the top left, working to the right, and then wrapping to the next row, like:
    
         1  2  3  4
     5  6  7  8
    [  text   ]
     9 10 11 12
    13 14 15 16
    

  * Each script sets a variable, and then that variable is passed in, except Script 14. 14 submits whatever was last set as part2$, which matches what’s in the code:
    
        part4$='lagan:GTYAKlwER'
    PluginSet("PlugIn","part2$")
    

#### Ghidra

Still in `SetFile`, I’m trying to figure out how it’s saving data. The string
`"floatsam"` catches my eye:

![image-20210916170356011](https://0xdfimages.gitlab.io/img/image-20210916170356011.png)

I don’t go this code in too much detail, but it’s looping over `local_8` to
check byte for byte if it matches “floatsam”, and if so, it sets `this` to a
global I’ve named `floatsam_buffer`. Otherwise, it continues and does similar
loops for the other three strings seen before the `:` above.

At the end of this function, there’s a call to a function that passes in
`this` and a string.

#### Conclusions

I ran a bunch more tests in x32Dbg to see what was going on. It was especially
helpful to have a breakpoint at that final function, 0x31c1. `this` will be in
ECX, as it typically for
[ThisCall](https://en.wikipedia.org/wiki/X86_calling_conventions#thiscall).
The other variable will be on the top of the stack. Debugging shows that this
is the data after the `:` each time. Looking at the buffer when it reaches
this last function, it starts out empty, but on each successive call, it’s got
the previous data appended to the end.

It seems clear from debugging that this function is appending data (what comes
after `:`) to the end of the one of four buffers, based on what is before the
`:`. In my debugging, it didn’t seem like there was a limit to the length of
these buffers.

### PluginFunc19

`PluginFunc19` is what is called when I click on the text, and what typically
returns the message that I choose poorly. Now that I understand how the four
buffers are set, I suspect here is where I’ll see how they are used.

Right at the top, a buffer of 31 bytes is initialized:

![image-20210916211128855](https://0xdfimages.gitlab.io/img/image-20210916211128855.png)

Then there’s some checks to ensure that `floatsam` and `jetsam` buffers have
length greater than zero (I’m not sure where the address - 0x0c gets the
length, but debugging shows it does).

![image-20210916211028937](https://0xdfimages.gitlab.io/img/image-20210916211028937.png)

Then there’s this loop. Inside the loop, it gets the length of `floatsam`, and
then loops through the `flag_buffer` (my name) and `floatsam` xoring byte by
byte, and looping to the start of `floatsam` if it exceeds the length.
Immediately after, the `i mod 0x11` byte of `jetsam` is subtracted from the
byte.

![image-20210916211343770](https://0xdfimages.gitlab.io/img/image-20210916211343770.png)

The contents of the resulting buffer are copied into another buffer, and
passed into a function, `FUN_10002bc0`. Just by looking at the API calls, it
looks like it’s taking a hash:

![image-20210916211454778](https://0xdfimages.gitlab.io/img/image-20210916211454778.png)

It returns a 32-byte result, so it’s likely an MD5.

The result is compared byte by byte against a hash:

![image-20210916212357074](https://0xdfimages.gitlab.io/img/image-20210916212357074.png)

That’s enough for me to take a try here at solving this.

### Solve Script

The follow script will solve the challenge:

    
    
    #!/usr/bin/env python3
    
    import hashlib
    from itertools import cycle, product
    
    
    floatsam = ['DFWEyEW', 'PXopvM', 'BGgsuhn']
    floatsam_idx = [3, 4, 13]
    jetsam = ['newaui', 'HwdwAZ', 'SLdkv']
    jetsam_idx = [7, 10, 11]
    target_md5 = '6c5215b12a10e936f8de1e42083ba184'
    
    float_strs = []
    for i in range(1,7):
        float_strs += [''.join(x) for x in product(floatsam, repeat=i)]
    
    jet_strs = [''.join(x) for x in product(jetsam, repeat=3) if len(''.join(x)) == 0x11]
    
    
    def check_pattern(floatsam, jetsam):
        buf_init = bytearray(b"\x96\x25\xA4\xA9\xA3\x96\x9A\x90\x9F\xAF\xE5\x38\xF9\x81\x9E\x16\xF9\xCB\xE4\xA4\x87\x8F\x8F\xBA\xD2\x9D\xA7\xD1\xFC\xA3\xA8")
        res = [((init ^ ord(fs)) - ord(js)) & 0xff for init, fs, js in zip(buf_init, cycle(floatsam), cycle(jetsam))]                                                                                                  
        if hashlib.md5(bytearray(res)).hexdigest() == target_md5:
            print(f"flag: {''.join(chr(x) for x in res)}")
            return True
        return False
    
    
    for fs in float_strs:
        for js in jet_strs:
            if check_pattern(fs, js):
                print(f'floatsam: {fs}')
                print(f'jetsam:   {js}')
                fs_order, js_order = fs, js
                for i in range(3):
                    fs_order = fs_order.replace(floatsam[i], f'{floatsam_idx[i]} ')
                    js_order = js_order.replace(jetsam[i], f'{jetsam_idx[i]} ')
                print(f'click order: {fs_order}{js_order}\n')  
    

The first thing the script does it generate the possible strings in the
floatsam and jetsam buffers. Since I have no information about the length of
floatsam, other than the only the first up to 31 characters will be used, I’ll
use between one and six clicks. The shortest string in six characters, so six
of those will cover the full 31 bytes. For jetsam, I know the length is 0x11
== 17 characters. That means there can only be three clicks (two of length
six, and one of length five).

Next is `check_pattern`. It creates the initial value from the code, xors it
by floatsam, and then subtracts jetsam. The result is converted to a bytearray
and hashes, and if the hash matches, it prints the result, and returns true.

With all the strings and the function to check for the right combination, I’ll
loop over all the combinations, for each checking if it solves, and if so,
after printing the flag, also printing the order to click on the animals to
get the flag via the application.

Running it prints the flag, and actually finds two combinations of clicks that
arrive at it:

    
    
    oxdf@parrot$ python solve.py
    flag: s1gn_my_gu357_b00k@flare-on.com
    floatsam: PXopvMDFWEyEWBGgsuhn
    jetsam:   SLdkvnewauiHwdwAZ
    click order: 4 3 13 11 7 10 
    
    flag: s1gn_my_gu357_b00k@flare-on.com
    floatsam: PXopvMDFWEyEWBGgsuhnPXopvMDFWEyEW
    jetsam:   SLdkvnewauiHwdwAZ
    click order: 4 3 13 4 3 11 7 10
    

Opening the application, clicking on the animals in this order, and then the
text gives the flag as well:

![image-20210916221558544](https://0xdfimages.gitlab.io/img/image-20210916221558544.png)

**Flag: s1gn_my_gu357_b00k@flare-on.com**

[](/flare-on-2021/myaquaticlife)

