# Hackvent 2019 - leet

[ctf](/tags#ctf ) [hackvent](/tags#hackvent ) [arduino](/tags#arduino ) [hex-
file](/tags#hex-file ) [avr-simulator](/tags#avr-simulator )
[binascii](/tags#binascii ) [python](/tags#python ) [burp](/tags#burp )
[php](/tags#php ) [john](/tags#john ) [ghidra](/tags#ghidra ) [arm](/tags#arm
) [ioctl](/tags#ioctl ) [reverse-engineering](/tags#reverse-engineering )  
  
Jan 1, 2020

  * [Hackvent 2019  
easy](/hackvent2019/easy)

  * [medium](/hackvent2019/medium)
  * [hard](/hackvent2019/hard)
  * leet

![](https://0xdfimages.gitlab.io/img/hackvent2019-leet-cover.png)

There were only three leet challenges, but they were not trivial, and IOT
focused. First, I’ll reverse a Arduino binary from hexcode. Then, there’s a
web hacking challenge that quickly morphs into a crypto challenge, which I can
solve by reimplementing the leaked PRNG from Ida Pro to generate a valid
password. Finally, there’s a firmware for a Broadcom wireless chip that I’ll
need to find the hooked ioctl function and pull the flag from it.

## Day 22

### Challenge

![hv19-ball22](https://0xdfimages.gitlab.io/img/hv19-ball22.png) | HV19.22 The command ... is lost  
---|---  
Categories: |  ![fun](../img/hv-cat-fun.png)FUN  
![reverse engineering](../img/hv-cat-reverse_engineering.png)REVERSE
ENGINEERING  
Level: | leet  
Author: |  inik   
  
> Santa bought this gadget when it was released in 2010. He did his own DYI
> project to control his sledge by serial communication over IR. Unfortunately
> Santa lost the source code for it and doesn’t remember the command needed to
> send to the sledge. The only thing left is this file:
> [thecommand7.data](/files/hv19-thecommand7.data)
>
> Santa likes to start a new DYI project with more commands in January, but
> first he needs to know the old command. So, now it’s on you to help out
> Santa.

I’m given a data file that contains what looks like a formatted hexdump:

    
    
    :100000000C9435000C945D000C945D000C945D0024
    :100010000C945D000C945D000C945D000C945D00EC
    :100020000C945D000C945D000C945D000C945D00DC
    :100030000C945D000C945D000C945D000C945D00CC
    :100040000C94EA010C945D000C945A020C94340256
    :100050000C945D000C945D000C945D000C945D00AC
    :100060000C945D000C945D00A60311241FBECFEF1D
    :10007000D8E0DEBFCDBF11E0A0E0B1E0EEE9F8E0EE
    :1000800002C005900D92A835B107D9F721E0A8E587
    :10009000B1E001C01D92AE3FB207E1F710E0C5E349
    ...[snip]...
    

[thecommand7.data](/files/hv19-thecommand7.data)

### Solution

My first step was to try to figure out what kind of file this is. I took the
first line and Googled it:

![image-20191222205212772](https://0xdfimages.gitlab.io/img/image-20191222205212772.png)

The first line shows that it matches `.hex` files, and that these are related
to [Arduino](https://www.arduino.cc/). The `.hex` file is an [Intel Hex
file](https://en.wikipedia.org/wiki/Intel_HEX), a file format that conveys
binary program information in a text format.

Googling a few more of the lines of the file, I notice another trend -
reference to the ATmega128:

![image-20191222214257536](https://0xdfimages.gitlab.io/img/image-20191222214257536.png)
![image-20191222214636224](https://0xdfimages.gitlab.io/img/image-20191222214636224.png)

I downloaded a _ton_ of disassemblers, IDEs, decompilers, etc. Eventually, I
found [AVR Simulator IDE](https://www.oshonsoft.com/avr.html). It’s a Windows
software, so I switched to a Windows VM. After running the installer for the
evaluation copy, I opened it, loaded the given file and set the
microcontroller to ATmega128:

![image-20191222215154786](https://0xdfimages.gitlab.io/img/image-20191222215154786.png)

When I go to Simulation –> Start, the steps start counting. I used the Rate
menu to increase the speed. Around Instruction Counter 2500, I noticed the
memory starting at $117, following a null at $116, switched to 48, 56, 31, 39.
I immediately recognized 31 39 as `19`, and 48 = `H` and 56 = `V`.

![image-20191222220009998](https://0xdfimages.gitlab.io/img/image-20191222220009998.png)

I wrote down the entire string, to the next null:

    
    
    485631397b4833795f536c336467335f6d3333745f6d335f61745f7468335f6e3378745f6330726e33727d
    

I dropped into a Python shell and converted that to ASCII, revealing the flag:

    
    
    >>> import binascii
    >>> s = "485631397b4833795f536c336467335f6d3333745f6d335f61745f7468335f6e3378745f6330726e33727d"
    >>> binascii.unhexlify(s)
    b'HV19{H3y_Sl3dg3_m33t_m3_at_th3_n3xt_c0rn3r}'
    

**Flag: HV19{H3y_Sl3dg3_m33t_m3_at_th3_n3xt_c0rn3r}**

## Day 23

### Challenge

![hv19-ball23](https://0xdfimages.gitlab.io/img/hv19-ball23.png) | HV19.23 Internet Data Archive  
---|---  
Categories: |  ![fun](../img/hv-cat-fun.png)FUN   
Level: | leet  
Author: |  M.   
  
> Today’s flag is available in the Internet Data Archive (IDA).

I’m given a url, http://whale.hacking-lab.com:23023/.

### Solution

#### Page Recon

The page is a form to pull older challenges from the “Internet Data Archive”:

![image-20191223155555275](https://0xdfimages.gitlab.io/img/image-20191223155555275.png)

When I enter a username (0xdf) select a challenge, and submit, I get:

![image-20191223155736068](https://0xdfimages.gitlab.io/img/image-20191223155736068.png)

The link to download my archive is `http://whale.hacking-
lab.com:23023/tmp/0xdf-data.zip`

The POST request to generate the zip looked like:

    
    
    POST /archive.php HTTP/1.1
    Host: whale.hacking-lab.com:23023
    User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:60.0) Gecko/20100101 Firefox/60.0
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
    Accept-Language: en-US,en;q=0.5
    Accept-Encoding: gzip, deflate
    Referer: http://whale.hacking-lab.com:23023/
    Content-Type: application/x-www-form-urlencoded
    Content-Length: 50
    Connection: close
    Upgrade-Insecure-Requests: 1
    
    username=0xdf&req%5B%5D=candle&req%5B%5D=blindball
    

`%5B%5D` url decodes to `[]`. In PHP, this is how an array is passed. It is
likely the site is running a for each loop over `$_POST['req']`. I can see in
the source the that disabled checkbox has the value `flag`:

    
    
    <input type="checkbox" class="custom-control-input" disabled id="req-flag" name="req[]" value="flag">
    

Unfortunately, adding `&req%5B%5D=flag` to the POST data results in:

    
    
    HTTP/1.1 200 OK
    Date: Mon, 23 Dec 2019 16:01:39 GMT
    Server: Apache/2.4.38 (Debian)
    X-Powered-By: PHP/7.4.1
    Content-Length: 15
    Connection: close
    Content-Type: text/html; charset=UTF-8
    
    Illegal Request
    

Similarly, when I try to enter a username of `santa`, I get `Illegal Request`
as well.

In poking around, I notice that `/tmp` has directory listing enabled, so I can
see all the generated zips:

![image-20191223160656141](https://0xdfimages.gitlab.io/img/image-20191223160656141.png)

There’s two interesting files in this directory:

  * `phpinfo.php` \- this is a standard `phpinfo` file, giving info about the instance
  * `Santa-data.zip` \- You can’t submit the username Santa, so this is quite interesting.

#### Zip Password

My hypothesis at this point is that the flag is in `Santa-data.zip`. But I
need the password.

I looked at the passwords given to me, and they were always 12 characters
long, upper, lower, and digits:

    
    
    $ time for i in {1..10}; do curl -s -X POST --data-binary $'username=qqqq&req[]=ball15' http://whale.hacking-lab.com:23023/archive.php | grep -E "<strong>.*</strong>"; done 
    <p>Your one-time Password is: <strong>M78hbzJEV32L</strong></p>
    <p>Your one-time Password is: <strong>XjBig3zaKg2Z</strong></p>
    <p>Your one-time Password is: <strong>rdhyhepbyadZ</strong></p>
    <p>Your one-time Password is: <strong>quXV8dXTAY5x</strong></p>
    <p>Your one-time Password is: <strong>E2vYaVG2REAx</strong></p>
    <p>Your one-time Password is: <strong>Jp3CtBxLsCXk</strong></p>
    <p>Your one-time Password is: <strong>K3YDGcMpEKyd</strong></p>
    <p>Your one-time Password is: <strong>2PUbfr8XG3vV</strong></p>
    <p>Your one-time Password is: <strong>5ZrbcaZP5Xcs</strong></p>
    <p>Your one-time Password is: <strong>aYdAiZss4XaK</strong></p>
    
    real    0m3.100s
    user    0m0.122s
    sys     0m0.177s
    

And, even if the request is exactly the same, the password changes, even
within the same second.

At this point the challenge name which hints at IDA PRO comes in. [This
article](https://devco.re/blog/2019/06/21/operation-crack-hacking-IDA-Pro-
installer-PRNG-from-an-unusual-way-en/) talks about how they managed to break
the registration password for IDA Pro by figuring out thepseudo-random number
generation (PRNG) algorithm. While reading that, the leaked passwords they
shows jumped out at me:

![image-20191223162940198](https://0xdfimages.gitlab.io/img/image-20191223162940198.png)

Those look just like the passwords from the site.

Now I’m thinking that if I can use this algorithm to generate passwords, maybe
one of them will work for `Santa-data.zip`. I originally tried by modifying
the Perl script in the post, but when it didn’t work, decided to try
implementing the same algorithm in PHP (making sure to have a similar version
to what’s on the challenge, which I can see in the phpinfo page).

I used `zip2john` to get the password into a format `john` can understand:

    
    
    $ /opt/john/run/zip2john Santa-data.zip > Santa-data.zip.john 
    

Now, I’ll write a script that will generate passwords:

    
    
    <?php
    
    $chars = "abcdefghijkmpqrstuvwxyzABCDEFGHJKLMPQRSTUVWXYZ23456789";
    
    for($j=1;$j<0x100000000;++$j) {
        srand($j);
        $pw="";
    
        for($i=0;$i<12;++$i) {
            $key = rand(0, 53);
            $pw = $pw . $chars[$key];
        }
        print "$pw\n";
    }
    ?>
    

For each seed, I’ll set the seed, and then create the password, just like in
the article. Note, that how random seeding is done is different in Perl, so
using the Perl script from the blog post will not generate the correct
password.

I can run this, and pipe it into `john`, and it cracks in less than two
minutes (on a vm, without much power):

    
    
    $ php ida_crack.php | /opt/john/run/john --stdin Santa-data.zip.john
    Using default input encoding: UTF-8
    Loaded 1 password hash (ZIP, WinZip [PBKDF2-SHA1 256/256 AVX2 8x])
    Will run 3 OpenMP threads
    Press Ctrl-C to abort, or send SIGUSR1 to john process for status
    Kwmq3Sqmc5sA     (Santa-data.zip)
    1g 0:00:01:55  0.008669g/s 37604p/s 37604c/s 37604C/s iJDctaJ29CKW..2CREsJAx7rLb
    Use the "--show" option to display all of the cracked passwords reliably
    Session completed     
    

Now I can extract `Santa-data.zip` and get the flag:

    
    
    $ 7z x Santa-data.zip
    
    7-Zip [64] 16.02 : Copyright (c) 1999-2016 Igor Pavlov : 2016-05-21
    p7zip Version 16.02 (locale=en_US.UTF-8,Utf16=on,HugeFiles=on,64 bits,3 CPUs Intel(R) Core(TM) i7-8750H CPU @ 2.20GHz (906EA),ASM,AES-NI)                                                                                  
    
    Scanning the drive for archives:
    1 file, 349592 bytes (342 KiB)
    
    Extracting archive: Santa-data.zip                                                                                                                                                                                         
    --
    Path = Santa-data.zip
    Type = zip
    Physical Size = 349592
    
    
    Enter password (will not be echoed):
    Everything is Ok
    
    Files: 6
    Size:       354474
    Compressed: 349592
                 
    $ cat flag.txt
    HV19{Cr4ckin_Passw0rdz_like_IDA_Pr0}   
    

**Flag: HV19{Cr4ckin_Passw0rdz_like_IDA_Pr0}**

## Day 24

### Challenge

![hv19-ball24](https://0xdfimages.gitlab.io/img/hv19-ball24.png) | HV19.24 ham radio  
---|---  
Categories: |  ![fun](../img/hv-cat-fun.png)FUN  
![reverse engineering](../img/hv-cat-reverse_engineering.png)REVERSE
ENGINEERING  
Level: | leet  
Author: |  DrSchottky   
  
> Elves built for santa a special radio to help him coordinating today’s
> presents delivery.

I’m given a zip, which contains a binary file, `brcmfmac43430-sdio.bin`.

[HV19-ham_radio.zip](/files/HV19-ham_radio.zip)

### Solution

First thing I needed to do is figure out what kind of file this is. I started
by Googling “brcmfmac”, and found that it’s a driver for a Broadcom wireless
hardware. I found the [original file](https://github.com/seemoo-
lab/nexmon/blob/master/firmwares/bcm43430a1/7_45_41_46/brcmfmac43430-sdio.bin).
I saved it as `brcmfmac43430-stio-orig.bin`.

I took a look at the difference in the two files using `binwalk -W -i
brcmfmac43430-sdio.bin brcmfmac43430-sdio-orig.bin`. I could see where the
puzzle file was modified. There’sa bunch of places, but I’ll use this as a map
as I poke around the program in Ghidra.

I’ll load the file into Ghidra next. After a bit of guessing, I used little
endian 32-bit arm (v6-8 all seemed to work fine).

There’s a ton of functions, and I did a lot of poking around before I landed
on something interesting, `FUN_00058dd8`. First of all, it is in the memory
space that was modified from the original (in the `binwalk` output). But more
interestingly, there’s a loop xoring two buffers, a very common pattern in CTF
binaries.

Here’s the disassembly from Ghidra, with only some minor type changes:

    
    
    FUN_00058dd8(undefined4 param_1,undefined *param_2,undefined4 param_3,undefined4 param_4,
                undefined4 param_5)
    {
      undefined4 uVar1;
      byte *pbVar2;
      byte *pbVar3;
      char local_39;
      char local_38 [24];
      
      FUN_00058d9c(param_3,param_4);
      local_38._0_4_ = *s__00058e84;
      local_38._4_4_ = s__00058e84[1];
      local_38._8_4_ = s__00058e84[2];
      local_38._12_4_ = s__00058e84[3];
      local_38._16_4_ = s__00058e84[4];
      local_38._20_4_ = s__00058e84[5];
      if (param_2 == &DAT_0000cafe) {
        func_0x00803cd4(param_3,_DAT_00058e90,param_4);
        return 0;
      }
      if (param_2 != (undefined *)0xd00d) {
        if (param_2 != &DAT_00001337) {
          uVar1 = func_0x0081a2d4(param_1,param_2,param_3,param_4,param_5);
          return uVar1;
        }
        pbVar3 = (byte *)&local_39;
        pbVar2 = _DAT_00058e88;
        do {
          pbVar3 = pbVar3 + 1;
          pbVar2 = pbVar2 + 1;
          *pbVar3 = *pbVar2 ^ *pbVar3;
        } while (pbVar3 != (byte *)(local_38 + 0x16));
        func_0x00803cd4(param_3,local_38,param_4);
        return 0;
      }
      FUN_00002390(_DAT_00058e8c,(undefined4 *)0x800000,0x17);
      return 0;
    }
    

I started by looking for where this function is called, but that proved more
challenging than I expected. Eventually, I started looking at the function
itself. There are four distinct paths based on `param_2`. I started with the
first one in the code, which is 0xcafe:

    
    
      if (param_2 == &DAT_0000cafe) {
        func_0x00803cd4(param_3,PTR_s_Um9zZXMgYXJlIHJlZCwgVmlvbGV0cyBh_00058e90,param_4);
        return 0;
      }
    

Unfortunately, the memory address 0x8033cd4 isn’t in this loaded memory. I
needed to find the ROM associated with this device. Some googling around led
me to it [here](https://github.com/seemoo-
lab/bcm_misc/tree/master/bcm43430a1). I opened it in Ghidra, and immediately
noticed that the base address was 0x800000. I checked at 0x803cd4, and found a
function there. This was feeling right. I then went to File -> “Add to
program” and selected the modified firmware, and loaded it at base address
0x00. Now I had both parts in the same Ghidra window (I did have to tell it to
re-analyze).

After a few minutes of looking at 0x803cd4, it was clear to me it was
`strncpy`. So while I don’t know the length passed in, I can take a look at
the string at the address in the second parameter:

    
    
    Um9zZXMgYXJlIHJlZCwgVmlvbGV0cyBhcmUgYmx1ZSwgRHJTY2hvdHRreSBsb3ZlcyBob29raW5nIGlvY3Rscywgd2h5IHNob3VsZG4ndCB5b3U/
    

That looked like base64, so I decodeded it:

    
    
    $ echo "Um9zZXMgYXJlIHJlZCwgVmlvbGV0cyBhcmUgYmx1ZSwgRHJTY2hvdHRreSBsb3ZlcyBob29raW5nIGlvY3Rscywgd2h5IHNob3VsZG4ndCB5b3U/" | base64 -d                                                            
    Roses are red, Violets are blue, DrSchottky loves hooking ioctls, why shouldn't you?
    

All of a sudden this started to click for me. This function I’m in right now
is a hooked for the ioctl call. I can quickly take a look at what is called if
`param_2` is anything other than 0xcafe, 0xd00d, or 0x1337:

    
    
      if (param_2 != (undefined *)0xd00d) {
        if (param_2 != &DAT_00001337) {
          uVar1 = func_0x0081a2d4(param_1,param_2,param_3,param_4,param_5);
          return uVar1;
        }
    

That explains why there are four specific words it’s looking for to take some
action, otherwise it just calls the real `ioctl` with the same parameters
passed into it, returning the return value from that function.

Knowing that 0xcafe just `strncpy` the poem, and the base case is the call to
`ioctl`, I need to look at the next two. I’ll start with 0xd00d, which jumps
all the way to the bottom of the code:

    
    
      FUN_00002390(PTR_DAT_00058e8c,0x800000,0x17);
      return 0;
    

It took me a while, but eventually I realized that `FUN_00002390` was just
`memcpy`. So it’s copying the first 23 bytes of the rom image to the address
stored at 0x58e8c. I check that address, and find 0x58eac.

Now I’ll check 0x1337:

    
    
        pbVar3 = (byte *)&local_39;
        pbVar2 = DAT_00058e88;
        do {
          pbVar3 = pbVar3 + 1;
          pbVar2 = pbVar2 + 1;
          *pbVar3 = *pbVar2 ^ *pbVar3;
        } while (pbVar3 != (byte *)(local_38 + 0x16));
        func_0x00803cd4(param_3,local_38,param_4);
        return 0;
    

The hardest part for me was getting my head around the two pointers, `pbVar3`
and `pbVar2`. `pbVar2` is set to the value at 0x58e88, which is 0x58eab, one
byte less than where the buffer was copied in 0xd00d. `pbVar3` is 39 bytes
onto the stack (stack pointer - 0x39), just one byte less than where a bunch
of stuff was copied into the stack at the start of the function:

    
    
      stack_buf[0] = *(undefined **)PTR_s__1:h_rG_~_J_o_.tP_x_>_00058e84;
      stack_buf[1] = *(undefined **)(PTR_s__1:h_rG_~_J_o_.tP_x_>_00058e84 + 4);
      stack_buf[2] = *(undefined **)(PTR_s__1:h_rG_~_J_o_.tP_x_>_00058e84 + 8);
      stack_buf[3] = *(undefined **)(PTR_s__1:h_rG_~_J_o_.tP_x_>_00058e84 + 0xc);
      stack_buf[4] = *(undefined **)(PTR_s__1:h_rG_~_J_o_.tP_x_>_00058e84 + 0x10);
      stack_buf[5] = *(undefined **)(PTR_s__1:h_rG_~_J_o_.tP_x_>_00058e84 + 0x14);
    

Then it increments both pointers, and xors a byte, writing it back to
`pbVar3`.

I think I know what’s going on here. Here’s my labeled code:

    
    
    hooked_ioctl(undefined4 param_1,int param_2,undefined4 param_3,undefined4 param_4,undefined4 param_5
                )
    
    {
      undefined4 out;
      byte *data_buf_ptr;
      byte *stack_buf_ptr;
      char stack_buf_+1;
      char stack_buf [24];
      
      FUN_00058d9c(param_3,param_4);
      stack_buf._0_4_ = *(undefined4 *)PTR_s__1:h_rG_~_J_o_.tP_x_>_00058e84;
      stack_buf._4_4_ = *(undefined4 *)(PTR_s__1:h_rG_~_J_o_.tP_x_>_00058e84 + 4);
      stack_buf._8_4_ = *(undefined4 *)(PTR_s__1:h_rG_~_J_o_.tP_x_>_00058e84 + 8);
      stack_buf._12_4_ = *(undefined4 *)(PTR_s__1:h_rG_~_J_o_.tP_x_>_00058e84 + 0xc);
      stack_buf._16_4_ = *(undefined4 *)(PTR_s__1:h_rG_~_J_o_.tP_x_>_00058e84 + 0x10);
      stack_buf._20_4_ = *(undefined4 *)(PTR_s__1:h_rG_~_J_o_.tP_x_>_00058e84 + 0x14);
      if (param_2 == 0xcafe) {
        strncpy(param_3,PTR_s_Um9zZXMgYXJlIHJlZCwgVmlvbGV0cyBh_00058e90,param_4);
        return 0;
      }
      if (param_2 != 0xd00d) {
        if (param_2 != 0x1337) {
          out = ioctl(param_1,param_2,param_3,param_4,param_5);
          return out;
        }
        stack_buf_ptr = (byte *)&stack_buf_+1;
        data_buf_ptr = DAT_00058e88;
        do {
          stack_buf_ptr = stack_buf_ptr + 1;
          data_buf_ptr = data_buf_ptr + 1;
          *stack_buf_ptr = *data_buf_ptr ^ *stack_buf_ptr;
        } while (stack_buf_ptr != (byte *)(stack_buf + 0x16));
        strncpy(param_3,stack_buf,param_4);
        return 0;
      }
      memcpy(PTR_DAT_00058e8c,0x800000,0x17);
      return 0;
    }
    

Now I just need to grab the two buffers and xor them. I’ll assume this
function is called at least twice, 0xd00d first, then 0x1337. In Ghidra, I can
select a buffer and copy special as byte string no spaces, which copies nicely
into Python, and I can use `binascii` to convert the hex strings to bytes:

    
    
    >>> import binascii
    >>> bstr1 = "09bc313a681aab7247867ee64a1d6f042e74500d78063e"
    >>> bstr2 = "41ea000313439b0730b510d10c680368634013604c6843"
    >>> b1 = binascii.unhexlify(bstr1)
    >>> b2 = binascii.unhexlify(bstr2)
    

Now I just xor those buffers and create a string to get the flag:

    
    
    >>> ''.join([chr(x ^ y) for x,y in zip(b1, b2)])
    'HV19{Y0uw3n7FullM4Cm4n}'
    

**Flag: HV19{Y0uw3n7FullM4Cm4n}**

[](/hackvent2019/leet)

