# Flare-On 2022: anode

[flare-on](/tags#flare-on ) [ctf](/tags#ctf ) [flare-on-anode](/tags#flare-on-
anode ) [reverse-engineering](/tags#reverse-engineering ) [nexe](/tags#nexe )
[javascript](/tags#javascript ) [nodejs](/tags#nodejs ) [nexe-
unpacker](/tags#nexe-unpacker ) [ghidra](/tags#ghidra ) [random-
numbers](/tags#random-numbers ) [patch](/tags#patch ) [python](/tags#python )  
  
Nov 11, 2022

  * [[1] Flaredle](/flare-on-2022/flaredle)
  * [[2] Pixel Poker](/flare-on-2022/pixel_poker)
  * [[3] Magic 8 Ball](/flare-on-2022/magic_8_ball)
  * [[4] darn_mice](/flare-on-2022/darn_mice)
  * [[5] T8](/flare-on-2022/t8)
  * [[6] à la mode](/flare-on-2022/alamode)
  * [7] anode
  * [[8] backdoor](/flare-on-2022/backdoor)
  * [[9] encryptor](/flare-on-2022/encryptor)
  * [[10] Nur geträumt](/flare-on-2022/nur_getraumt)
  * [[11] The challenge that shall not be named](/flare-on-2022/challenge_that_shall_not_be_named)

![anode](https://0xdfimages.gitlab.io/img/flare2022-anode-cover.png)

anode is a JavaScript application packed into an EXE with NEXE. The challenge
would be straight forward, but the instance of Node that’s packed in the
executable with the JavaScript is dorked such that BigInts don’t evaluate as
booleans correctly and the random numbers are seeded the same way each time.
I’ll patch the JavaScript in the executable (carefully to maintain the length)
to print out all 1024 steps that it takes changing the input into an encoded
value, and write a Python script to reverse that and recover the flag.

## Challenge

> You’ve made it so far! I can’t believe it! And so many people are ahead of
> you!

The download contains a 64-bit Windows executable:

    
    
    oxdf@hacky$ file anode.exe 
    anode.exe: PE32+ executable (console) x86-64, for MS Windows
    

## Run It

Double-clicking the application pops a console with a prompt:

![image-20221007141522856](https://0xdfimages.gitlab.io/img/image-20221007141522856.png)

If I enter something, it prints “Try again” and disappears. That’s more easily
seen running it from a terminal:

![image-20221007141608192](https://0xdfimages.gitlab.io/img/image-20221007141608192.png)

Hovering over the exe shows some additional details:

![image-20221007141642356](https://0xdfimages.gitlab.io/img/image-20221007141642356.png)

## JS Source

### Identify Framework

Looking at the `strings` in the binary, there are a ton that include `nexe`:

    
    
    oxdf@hacky$ strings anode.exe | grep nexe | wc -l
    2047
    oxdf@hacky$ strings anode.exe | grep nexe                        
    c:\users\vssadministrator\.nexe\14.15.3\src\inspector\node_string.h:98              
    c:\users\vssadministrator\.nexe\14.15.3\out\release\obj\global_intermediate\src\node\inspector\pro
    tocol\protocol.cpp:664
      const __nexe_patches = (process.nexe = { patches: {} }).patches
      const __nexe_noop_patch = function (original) {
      const __nexe_patch = function (obj, method, patch) {                               
        __nexe_patches[method] = patch                                                                      return __nexe_patches[method].apply(this, args)
      __nexe_patch((process).binding('fs'), 'internalModuleReadFile', __nexe_noop_patch)                __nexe_patch((process).binding('fs'), 'internalModuleReadJSON', __nexe_noop_patch) 
      __nexe_patch((process).binding('fs'), 'internalModuleStat', __nexe_noop_patch)                  const footerPosition = tailWindow.indexOf('<nexe~~sentinel>');
    Object.defineProperty(process, '__nexe', (function () {                              
        let nexeHeader = null;
                return nexeHeader;
                if (nexeHeader) {
                nexeHeader = Object.assign({}, value, {                                  
                Object.freeze(nexeHeader);                                                            c:\users\vssadministrator\.nexe\14.15.3\src\tls_wrap.cc
    c:\users\vssadministrator\.nexe\14.15.3\src\env-inl.h:250                             
    c:\users\vssadministrator\.nexe\14.15.3\src\base_object-inl.h:77  
    ...[snip]...
    c:\users\vssadministrator\.nexe\14.15.3\deps\v8\src\compiler\verifier.cc:1928
    c:\users\vssadministrator\.nexe\14.15.3\out\release\obj\global_intermediate\node_code_cache.cc:742
    C:\Users\VssAdministrator\.nexe\14.15.3\out\Release\node.pdb
    !(function () {process.__nexe = {"resources":{"./anode.js":[0,321847]}};
        if ((process.env.DEBUG || '').toLowerCase().includes('nexe:require')) {
                    process.stderr.write('[nexe] - MANIFEST' + JSON.stringify(manifest, null, 4) + '\n');
                    process.stderr.write('[nexe] - DIRECTORIES' + JSON.stringify(directories, null, 4) + '\n');
                return process.stderr.write('[nexe] - ' + text + '\n');
        const patches = process.nexe.patches || {};
        delete process.nexe;
    shimFs(process.__nexe)
    <nexe~~sentinel>
    

[Nexe](https://github.com/nexe/nexe) is a tool for packaging a NodeJS
application into an executable file. It actually brings along a full `node`
interpreter and any used JS libraries, and uses that to run JavaScript that’s
also embedded in the application.

### Extract

#### Manual Unpack

Looking at the end of the binary, there are about 10,000 lines of JavaScript
code:

    
    
    oxdf@hacky$ tail -n 10 anode.exe 
      }
    
      var target = [106, 196, 106, 178, 174, 102, 31, 91, 66, 255, 86, 196, 74, 139, 219, 166, 106, 4, 211, 68, 227, 72, 156, 38, 239, 153, 223, 225, 73, 171, 51, 4, 234, 50, 207, 82, 18, 111, 180, 212, 81, 189, 73, 76];
      if (b.every((x,i) => x === target[i])) {
        console.log('Congrats!');
      } else {
        console.log('Try again.');
      }
    });
    <nexe~~sentinel>@ܤA
    

There are several patches of JavaScript in the binary, first at line 37,144.
At the end of line 284,993, Nexe JS starts:

    
    
    !(function () {process.__nexe = {"resources":{"./anode.js":[0,321847]}};
    

A few hundred lines later on line 285392, the custom code for this application
starts (marked with a comment added by me):

    
    
    ...[snip]...
    shimFs(process.__nexe)
    })();!(function () {
        if (process.argv[1] && process.env.NODE_UNIQUE_ID) {
          const cluster = require('cluster')
          cluster._setupWorker()
          delete process.env.NODE_UNIQUE_ID
        }
      })();!(function () {
          if (!process.send) {
            const path = require('path')
            const entry = path.resolve(path.dirname(process.execPath),"./anode.js")
            process.argv.splice(1,0, entry)
          }
        })();;const readline = require('readline').createInterface({  // <-- here
      input: process.stdin,
      output: process.stdout,
    });
    
    readline.question(`Enter flag: `, flag => {
      readline.close();
      if (flag.length !== 44) {
        console.log("Try again.");
        process.exit(0);
      }
      var b = [];
      for (var i = 0; i < flag.length; i++) {
        b.push(flag.charCodeAt(i));
      }
    ...[snip]...
    

I can cut out the interesting JavaScript into a file and proceed to analysis
from there.

#### NEXE UNPACKER

[NEXE UNPACKER](https://www.npmjs.com/package/nexe_unpacker) is a NodeJS
script to unpack NExe applications. It’s as simple as running:

    
    
    oxdf@hacky$ nexe_unpacker anode.exe --out .
    

This command creates a `anode.js`:

    
    
    const readline = require('readline').createInterface({
      input: process.stdin,
      output: process.stdout,
    });
    
    readline.question(`Enter flag: `, flag => {
      readline.close();
      if (flag.length !== 44) {
        console.log("Try again.");
        process.exit(0);
    ...[snip]...
    

### Source Analysis

#### Read Flag

The script starts out by reading the flag, making sure it’s exactly 44
characters long, and then creating an array of ints named `b` which
initializes to the numerical value of each character in the input flag.

    
    
    const readline = require('readline').createInterface({
      input: process.stdin,
      output: process.stdout,
    });
    
    readline.question(`Enter flag: `, flag => {
      readline.close();
      if (flag.length !== 44) {
        console.log("Try again.");
        process.exit(0);
      }
      var b = [];
      for (var i = 0; i < flag.length; i++) {
        b.push(flag.charCodeAt(i));
      }
    

#### Oddness

Next there’s an odd bit that doesn’t make much sense (as the comment the Flare
team included points out):

    
    
      // something strange is happening...
      if (1n) {
        console.log("uh-oh, math is too correct...");
        process.exit(0);
      }
    

In theory, this should always exit. `1n` is a
[BigInt](https://developer.mozilla.org/en-
US/docs/Web/JavaScript/Reference/Global_Objects/BigInt) object, with the value
1, and therefore should be true. And yet, running the binary doesn’t exit
here.

In fact, running the extracted source does fail this way:

    
    
    oxdf@hacky$ node anode.js
    Enter flag: AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
    uh-oh, math is too correct...
    

I’ll come back to this.

#### State Machine

Next there is a giant loop working as a state machine:

    
    
      var state = 1337;
      while (true) {
        state ^= Math.floor(Math.random() * (2**30));
        switch (state) {
          case 306211:
            if (Math.random() < 0.5) {
              b[30] -= b[34] + b[23] + b[5] + b[37] + b[33] + b[12] + Math.floor(Math.random() * 256);
              b[30] &= 0xFF;
            } else {
              b[26] -= b[24] + b[41] + b[13] + b[43] + b[6] + b[30] + 225;
              b[26] &= 0xFF;
            }
            state = 868071080;
            continue;
          case 311489:
            if (Math.random() < 0.5) {
              b[10] -= b[32] + b[1] + b[20] + b[30] + b[23] + b[9] + 115;
              b[10] &= 0xFF;
            } else {
              b[7] ^= (b[18] + b[14] + b[11] + b[25] + b[31] + b[21] + 19) & 0xFF;
            }
            state = 22167546;
            continue;
          case 755154:
            if (93909087n) {
              b[4] -= b[42] + b[6] + b[26] + b[39] + b[35] + b[16] + 80;
              b[4] &= 0xFF;
            } else {
              b[16] += b[36] + b[2] + b[29] + b[10] + b[12] + b[18] + 202;
              b[16] &= 0xFF;
            }
            state = 857247560;
            continue;
          case 832320:
    

There are 1025 possible cases in the switch statement:

    
    
    oxdf@hacky$ grep case anode.js | wc -l
    1025
    

One of them does break the loop:

    
    
          case 185078700:
            break;
    

Each of the rest seem to branch based on a random number or a BigInt, and then
change one byte in `b`.

The fact that I expect the flag to be the same every run also shows more
oddness of the same type as experienced above.

#### Check Flag

At the bottom after the loop, the code checks `b` against a static array of
ints, and prints either “Congrats!” or “Try again.”:

    
    
      var target = [106, 196, 106, 178, 174, 102, 31, 91, 66, 255, 86, 196, 74, 139, 219, 166, 106, 4, 211, 68, 227, 72, 156, 38, 239, 153, 223, 225, 73, 171, 51, 4, 234, 50, 207, 82, 18, 111, 180, 212, 81, 189, 73, 76];
      if (b.every((x,i) => x === target[i])) {
        console.log('Congrats!');
      } else {
        console.log('Try again.');
      }
    

## Static Analysis

### Strategy

At this point it’s clear that something is dorked in the JavaScript
environment that’s running this code. Specifically, the random numbers
generated are not random, and the BigInts are not evaluating as booleans
correctly.

As to how I ended up solving this challenge, I didn’t end up using this
analysis at all - this section can be completely skipped. But it is
interesting, so I wanted to include it.

### Random

Opening `anode.exe` in Ghidra showed just how much there was in this binary.
It took several minutes to process, and there are a _ton_ of functions. Once
it completes, I’ll go into the Symbol Tree section, and go to Classes, and
find `RandomNumberGenerator`:

![image-20221010105637374](https://0xdfimages.gitlab.io/img/image-20221010105637374.png)

Poking around in these a bit, I’ll notice that `SetSeed` seems interesting:

![image-20221010105714759](https://0xdfimages.gitlab.io/img/image-20221010105714759.png)

To get a feel for what this should look like, I’ll open another Ghidra window
and load (after a long time) my local copy of `node`. This is a Linux copy, vs
the Windows part from the EXE, and I’m not sure if they are the same version,
but it’s close enough to get an idea what’s different. There, `SetSeed` looks
like this:

![image-20221010105817350](https://0xdfimages.gitlab.io/img/image-20221010105817350.png)

Without going too deep into how random numbers work in JavaScript ([this video
from PwnFunction](https://www.youtube.com/watch?v=-h_rj2-HP2E) is a really
neat watch for more details), it keeps two state values and each time a random
number is created, it returns one, and then mixes both together to replace the
one sent off.

The fact that the seed function in `anode.exe` is just setting two static
values is a good clue as to why the random numbers come back the same each
time. If the seeds are always the same, the random stream resulting from those
seeds will be as well.

I did even go down the rabbit hole of writing a Python script to generate
numbers based from these seeds:

    
    
    #!/usr/bin/env python3
    
    import struct
    import z3
    
    state0 = 0x60c43c4809ad2d74
    state1 = 0xce6a1a53db4c5403
    
    for _ in range(100):
        s0 = state1
        s1 = ((state0 << 0x17) & 0xffffffffffffffff) ^ state0
        state0 = s0
        s1 = (s0 >> 9 ^ s1) >> 0x11 ^ s0 ^ s1
        state1 = s1
    
        u_long_long_64 = (state0 >> 12) | 0x3FF0000000000000
        float_64 = struct.pack("<Q", u_long_long_64)
        next_seq = struct.unpack("d", float_64)[0]
        next_seq -= 1
    
        print(next_seq)
    

Though, as mentioned above, I don’t actually use this to solve the challenge.

### BigInt

I had less success identifying what was going on with `BinInt`. I can find it
in Ghidra as well (there are two there, I’m not sure why):

![image-20221010104146651](https://0xdfimages.gitlab.io/img/image-20221010104146651.png)

Clicking around on a few of these functions, one subtle thing jumps out as
potentially interesting. For example, the `UInt64Value` function:

![image-20221010104338621](https://0xdfimages.gitlab.io/img/image-20221010104338621.png)

There’s a call to `FUN_14082b390`. That’s a local function that’s not a part
of the class (or any other class).

This looks similar to what’s in `node`, thought it’s weird to not be using the
`v8::internal::BigInt` class in the `anode.exe` version:

![image-20221010104557709](https://0xdfimages.gitlab.io/img/image-20221010104557709.png)

Something is definitely up with this class.

## Patching Binary

### POC

Given that the JavaScript that’s run is all in plaintext in the binary, an
interesting thought is to check and see if I can edit that JavaScript and have
the changes take effect. I’ll copy `anode.exe` to `anode-mod.exe` and edit
that, keeping a good copy so I can start over when I mess up the binary.

I’ll use `notepad++` on Windows or `vim` on Linux because I know they are good
about keeping all the non-ascii characters the same. To start simple, I’ll try
adding some text to the message that prints if the flag is not the right
length:

![image-20221010120228593](https://0xdfimages.gitlab.io/img/image-20221010120228593.png)

Making sure to hit Save, now I’ll run that, and it fails:

![image-20221010120323680](https://0xdfimages.gitlab.io/img/image-20221010120323680.png)

Spacing is often important in binaries. I’ll try again, but this time, instead
of adding text, I’ll replace it:

![image-20221010120610985](https://0xdfimages.gitlab.io/img/image-20221010120610985.png)

It works:

![image-20221010120629093](https://0xdfimages.gitlab.io/img/image-20221010120629093.png)

### Observe States

It would be potentially useful to know the order of the various states that
are visited, and to confirm that they are the same each time. I’ll add a print
statement just after the state updates to show that:

![image-20221010121011555](https://0xdfimages.gitlab.io/img/image-20221010121011555.png)

The input print statement adds 22 characters to the JavaScript, so I’ll need
to remove 22 characters. An easy place to take from is the messages printed to
the screen, as shown above.

Running this results in the states printing:

    
    
    PS > .\anode-mod.exe
    Enter flag: AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
    1010356043
    497278214
    181384715
    957436102
    605458814
    429116243
    304625349
    ...[snip]...
    443632296
    1048216731
    210975861
    185078700
    Try again.
    

I can run a couple times and verify that the states are the same each time.
Saving the results to a file and counting lines confirms 1025 unique states,
so each is visited once.

### Observer Actions

#### POC #1

In theory, now I can visit the states in order and track their actions. The
challenge is that every state starts with an `if` / `else` based on either a
BigInt or a random number, and keeping track of that, while possible, would be
a ton of work.

Instead, I’d like to just record each of the operations that occur. I’ll start
with a fresh copy of the binary, and change one of the states so that it
prints the values rather than doing them:

![image-20221010121921898](https://0xdfimages.gitlab.io/img/image-20221010121921898.png)

I’ll add 15 characters in two sports (in red), and remove from strings and
comments to make up for it (blue).

This runs and prints the operation, but then fails:

    
    
    PS > .\anode-mod.exe
    Enter flag: AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
    b[30] -= b[34] + b[23] + b[5] + b[37] + b[33] + b[12] + Math.floor(Math.random() * 256)
    uh-oh, math.random() is too random...
    

The failure is because I printed `Math.random` instead of calling it, and
therefore on the next loop it’s out of sync, and ends up in an state that’s
not intended.

#### POC #2

I’ll edit this so that `Math.random` is called, and the result is printed:

![image-20221010122221360](https://0xdfimages.gitlab.io/img/image-20221010122221360.png)

This time, it runs to completion:

    
    
    PS > .\anode-mod.exe
    Enter flag: AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
    b[30] -= b[34] + b[23] + b[5] + b[37] + b[33] + b[12] + 60
    Try again.
    

#### Script

I really want to add this printing to 1024 cases (excluding the one that just
breaks), and not knowing which way the `if` will resolve, that’s 2048 edits to
make. I’m not going to do that manually.

I’ll use a Python script to create a modified binary:

    
    
    #!/usr/bin/env python3
    
    import re
    import sys
    
    
    with open(sys.argv[1], 'rb') as f:
        exe = f.read()
    
    js_start = exe.index(b'})();;') + 6
    js_end = exe.index(b'\n});\n<nexe')
    
    js = exe[js_start:js_end]
    print(f"[*] Extracted JS [{len(js)} bytes]")
    
    new_js = re.sub(b'(b\[\d+\] .= .{10,});', b'console.log("\\1");', js)
    print(f"[*] Wrapped lines in console.log [{len(new_js)} bytes]")
    new_js = re.sub(b'Math.floor\(Math\.random\(\) \* 256\)', b'" + Math.floor(Math.random() * 256) + "', new_js)
    print(f"[*] Moved Math.random() calls outside the logging to get values and keep in sync [{len(new_js)} bytes]")
    new_js = re.sub(b'\n +', b'\n', new_js)
    print(f"[*] Removing leading spaces [{len(new_js)} bytes]")
    
    size_diff = len(js) - len(new_js)
    new_js += b" " * size_diff
    print(f"[*] Added {size_diff} spaces to the end to keep size [{len(new_js)} bytes]")
    
    new_exe = exe[:js_start] + new_js + exe[js_end:]
    
    fn_bits = sys.argv[1].split('.')
    new_fn = '.'.join(fn_bits[:-1]) + "-mod." + fn_bits[-1]
    with open(new_fn, 'wb') as f:
        f.write(new_exe)
        
    print(f"[+] Modified binary written to {new_fn}")
    

First I’ll read the binary into a variable named `exe`. I’ll use `vim` to get
the start and end offsets to the JavaScript I’m going to mess with, and pull
that code into a variable named `js`.

Now there’s a series of substitutions using regex.

The first will find `b[digits] ?= {10 or more characters}`, and replace it by
wrapping `console.log` around it. I require 10 or more characters so I skip
the lines that are just `& 0xFF`. I’ll make sure to note that the values in
`b` are always 0-255.

The next finds calls to `Math.floor(Math.random() * 256)` and removes them
from the `console.log`. I am able to verify with some `grep` that these only
occur in the lines that I’m wrapping with `console.log`.

Finally, the third regex will find every instance of a line that starts with
spaces, and remove those spaces. That is a quick way to create a ton of extra
space.

Now I’ll calculate the size difference between the original JS and the
modified version, and add spaces at the end of make them the same.

The rest is just writing the result to a new file.

It generates a file:

    
    
    oxdf@hacky$ python patch.py anode.exe 
    [*] Extracted JS [321842 bytes]
    [*] Wrapped lines in console.log [352562 bytes]
    [*] Moved Math.random() calls outside the logging to get values and keep in sync [356090 bytes]
    [*] Removing leading spaces [274810 bytes]
    [*] Added 47032 spaces to the end to keep size [321842 bytes]
    [+] Modified binary written to anode-mod.exe
    

It works:

    
    
    PS > .\anode-mod.exe
    Enter flag: AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
    b[29] -= b[37] + b[23] + b[22] + b[24] + b[26] + b[10] + 7
    b[39] += b[34] + b[2] + b[1] + b[43] + b[20] + b[9] + 79
    b[19] ^= (b[26] + b[0] + b[40] + b[37] + b[23] + b[32] + 255) & 0xFF
    b[28] ^= (b[1] + b[23] + b[37] + b[31] + b[43] + b[42] + 245) & 0xFF
    b[39] += b[42] + b[10] + b[3] + b[41] + b[14] + b[26] + 177
    b[9] -= b[20] + b[19] + b[22] + b[5] + b[32] + b[35] + 151
    b[14] -= b[4] + b[5] + b[31] + b[15] + b[36] + b[40] + 67
    ...[snip]...
    b[21] += b[39] + b[6] + b[0] + b[33] + b[8] + b[40] + 179
    b[34] += b[35] + b[40] + b[13] + b[41] + b[23] + b[25] + 14
    b[22] += b[16] + b[18] + b[7] + b[23] + b[1] + b[27] + 50
    b[39] += b[18] + b[16] + b[8] + b[19] + b[5] + b[23] + 36
    Try again.
    

I can do a quick check against my printed states to verify that it’s following
the same course.

## Solve

### Strategy

With the full list of operations performed, I can now work backwards from the
correct result to get the right input.

For example, if I had a much simpler challenge where there was only one byte,
x, and the operations were:

    
    
    x += 5
    x ^= 7
    x -= 3
    if (x == 5):
    	print ("yay")
    

I would start with 5, and work backwards undoing the operations:

  * add 3 to get 8
  * xor with 7 to get 15
  * subtract 5 to get 10

### Script

I’ll write a Python script to handle this as well:

    
    
    #!/usr/bin/env python3
    
    import re
    
    
    b = [106, 196, 106, 178, 174, 102, 31, 91, 66, 255, 86, 196, 74, 139, 219, 166, 106, 4, 211, 68, 227, 72, 156, 38, 239, 153, 223, 225, 73, 171, 51, 4, 234, 50, 207, 82, 18, 111, 180, 212, 81, 189, 73, 76]
    
    with open('ops.txt', 'r') as f:
        ops = f.readlines()[::-1]
    
    for line in ops:
        target, op, eq = line.split(' ', 2)
        target_num = int(re.findall('\d+', target)[0])
        if op == '+=':
            b[target_num] = (b[target_num] - eval(eq)) & 0xff
        elif op == '-=':
            b[target_num] = (b[target_num] + eval(eq)) & 0xff
        elif op == '^=':
            b[target_num] = b[target_num] ^ eval(eq)
        else:
            assert(False)
    
    
    print(''.join([chr(x) for x in b]))
    

This will create `b` from the `target` in the JS. Then it will read in the
operations, reversing the order (`[::-1]`). Now I loop over the lines, for
each splitting out the target register, the operation, and the rest of the
equation.

I’ll switch based on the `op`. If it’s plus, I need to subtract, and vice-
versa. It’s good to throw an error if I get an unexpected `op` . For each
`op`, I will `eval(eq)` to get a value, and then apply it to the number, mask
it with `0xff` to get a byte, and store it back in the same register.

At the end, I’ll print the flag, and it works:

    
    
    oxdf@hacky$ python3 solve.py 
    n0t_ju5t_A_j4vaSCriP7_ch4l1eng3@flare-on.com
    

**Flag: n0t_ju5t_A_j4vaSCriP7_ch4l1eng3@flare-on.com**

[](/flare-on-2022/anode)

