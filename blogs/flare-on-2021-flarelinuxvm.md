# Flare-On 2021: flarelinuxvm

[flare-on](/tags#flare-on ) [ctf](/tags#ctf ) [flare-on-
flarelinuxvm](/tags#flare-on-flarelinuxvm ) [reverse-
engineering](/tags#reverse-engineering ) [vm](/tags#vm )
[cyberchef](/tags#cyberchef ) [encoding](/tags#encoding )
[crypto](/tags#crypto ) [ghidra](/tags#ghidra ) [ransomware](/tags#ransomware
) [youtube](/tags#youtube )  
  
Oct 27, 2021

  * [[1] credchecker](/flare-on-2021/credchecker)
  * [[2] known](/flare-on-2021/known)
  * [[3] antioch](/flare-on-2021/antioch)
  * [[4] myaquaticlife](/flare-on-2021/myaquaticlife)
  * [5] FLARE Linux VM
  * [[6] PetTheKitty](/flare-on-2021/petthekitty)
  * [[7] spel](/flare-on-2021/spel)
  * [[8] beelogin](/flare-on-2021/beelogin)
  * [9] evil - no writeup :(
  * [[10] wizardcult](/flare-on-2021/wizardcult)

![flarelinuxvm](https://0xdfimages.gitlab.io/img/flare2021-flarelinuxvm-
cover.png)

Flare Linux VM starts with a VM and some ransomware encrypted files. I’ll have
to triage, find the malware, and reverse it to understand that it’s using a
static key stream to encrypted the files. With that stream, I can decrypt and
get the files, which provide a series of CTF puzzles to get a password which I
can give to the binary and get the final flag.

## Challenge

> Because of your superior performance throughout the FLARE-ON 8 Challenge,
> the FLARE team has invited you to their office to hand you a special prize!
> Ooh – a special prize from FLARE ? What could it be? You are led by a strong
> bald man with a strange sense of humor into a very nice conference room with
> very thick LED dimming glass. As you overhear him mumbling about a party and
> its shopping list you notice a sleek surveillance camera. The door locks
> shut!
>
> Excited, you are now waiting in a conference room with an old and odd
> looking computer on the table. The door is closed with a digital lock with a
> full keyboard on it.
>
> Now you realise… The prize was a trap! They love escape rooms and have
> locked you up in the office to make you test out their latest and greatest
> escape room technology. The only way out is the door – but it locked and it
> appears you have to enter a special code to get out. You notice the glyph
> for U+2691 on it. You turn you attention to the Linux computer - it seems to
> have been infected by some sort of malware that has encrypted everything in
> the documents directory, including any potential clues.
>
> Escape the FLARE Linux VM to get the flag - hopefully it will be enough to
> find your way out.
>
> Hints:
>
>   * You can import “FLARE Linux VM.ovf” with both VMWare and VirtualBox.
>   * Log in as ‘root’ using the password ‘flare’
>   * If you use VirtualBox and want to use ssh, you may need to enable port
> forwarding. The following link explains how to do it:
> https://nsrc.org/workshops/2014/btnog/raw-attachment/wiki/Track2Agenda/ex-
> virtualbox-portforward-ssh.htm
>

The
[download](https://drive.google.com/file/d/18Hx83FG3T9AJckxQF0oPCjrps-C0a_TT/view?usp=sharing)
contains the files needed for a virtual machine (as well as `intro.txt`, which
just contains the text from the prompt):

    
    
    $ ls
    FLARE_Linux_VM-disk1.vmdk  'FLARE Linux VM.mf'  'FLARE Linux VM.ovf'   intro.txt
    

## Set Up

### Import

I’m running VirtualBox, so I’ll go to File -> Import Appliance, find the
`.ova` file, and import it. I changed the name from `vm` to `flareon-2021-05`,
and it imports:

![image-20210917130818327](https://0xdfimages.gitlab.io/img/image-20210917130818327.png)

I’ll take a snapshot here so I have a clean version handy.

### Boot

On booting the VM, it shows it’s openSUSE version 152 splash screen before
auto booting:

![image-20210917131432712](https://0xdfimages.gitlab.io/img/image-20210917131432712.png)

I’ll log in as the root user with the password and I’m at a termina:

![image-20210917130955384](https://0xdfimages.gitlab.io/img/image-20210917130955384.png)

### SSH

Working at this terminal is a big pain. No copy and paste for notes, and it
captures my host mouse cursor. I could install Guest Additions, but I’m going
to avoid installing things for now. Instead, I’ll take the hint from the
prompt and SSH in. Rather than setting up port forwarding, I’ll just change
the NIC to bridged mode, so it gets an IP on the same network as my host:

    
    
    $ sshpass -p flare ssh root@10.1.1.193
    Warning: Permanently added '10.1.1.193' (ECDSA) to the list of known hosts.
    Last login: Fri Sep 17 17:14:49 2021
    Welcome to the FLARE Linux VM. :)
    Have a lot of fun...
    localhost:~ # 
    

This is another good place for a snapshot.

## Enumeration

### Documents

There are 28 files in the `Documents` folder, all exactly 1MB in size, and
each with a `.broken` extension:

    
    
    localhost:~/Documents # ls -la
    total 112
    drwxr-xr-x 1 root root 1102 Aug 26 17:37 .
    drwx------ 1 root root  118 Aug 26 15:04 ..
    -rw-r--r-- 1 root root 1024 Aug 26 15:05 backberries.txt.broken
    -rw-r--r-- 1 root root 1024 Aug 26 15:05 banana_chips.txt.broken
    -rw-r--r-- 1 root root 1024 Aug 26 15:05 blue_cheese.txt.broken
    -rw-r--r-- 1 root root 1024 Aug 26 15:05 .daiquiris.txt.broken
    -rw-r--r-- 1 root root 1024 Aug 26 15:05 donuts.txt.broken
    -rw-r--r-- 1 root root 1024 Aug 26 15:05 dumplings.txt.broken
    -rw-r--r-- 1 root root 1024 Aug 26 15:05 ice_cream.txt.broken
    -rw-r--r-- 1 root root 1024 Aug 26 15:05 iced_coffee.txt.broken
    -rw-r--r-- 1 root root 1024 Aug 26 15:05 instant_noodles.txt.broken
    -rw-r--r-- 1 root root 1024 Aug 26 15:05 nachos.txt.broken
    -rw-r--r-- 1 root root 1024 Aug 26 15:05 natillas.txt.broken
    -rw-r--r-- 1 root root 1024 Aug 26 15:05 nutella.txt.broken
    -rw-r--r-- 1 root root 1024 Aug 26 15:05 oats.txt.broken
    -rw-r--r-- 1 root root 1024 Aug 26 15:05 omelettes.txt.broken
    -rw-r--r-- 1 root root 1024 Aug 26 15:05 oranges.txt.broken
    -rw-r--r-- 1 root root 1024 Aug 26 15:05 raisins.txt.broken
    -rw-r--r-- 1 root root 1024 Aug 26 15:05 rasberries.txt.broken
    -rw-r--r-- 1 root root 1024 Aug 26 15:05 reeses.txt.broken
    -rw-r--r-- 1 root root 1024 Aug 26 15:05 sausages.txt.broken
    -rw-r--r-- 1 root root 1024 Aug 26 15:05 shopping_list.txt.broken
    -rw-r--r-- 1 root root 1024 Aug 26 15:05 spaghetti.txt.broken
    -rw-r--r-- 1 root root 1024 Aug 26 15:05 strawberries.txt.broken
    -rw-r--r-- 1 root root 1024 Aug 26 17:37 tacos.txt.broken
    -rw-r--r-- 1 root root 1024 Aug 26 17:37 tiramisu.txt.broken
    -rw-r--r-- 1 root root 1024 Aug 26 17:37 tomatoes.txt.broken
    -rw-r--r-- 1 root root 1024 Aug 26 15:05 udon_noddles.txt.broken
    -rw-r--r-- 1 root root 1024 Aug 26 15:05 ugali.txt.broken
    -rw-r--r-- 1 root root 1024 Aug 26 15:05 unagi.txt.broken
    

Looking at the start of each file, I don’t see any pattern like a header:

    
    
    localhost:~/Documents # xxd backberries.txt.broken | head -1
    00000000: 7a22 0a13 1345 9d3d ed7e a7f8 8d1c 6609  z"...E.=.~....f.
    localhost:~/Documents # xxd banana_chips.txt.broken | head -1
    00000000: 7236 4f4a 055f c87c f874 e8f2 c209 324e  r6OJ._.|.t....2N
    localhost:~/Documents # xxd blue_cheese.txt.broken | head -1
    00000000: 672c 4f4a 4844 d57c fd62 f3f3 c207 204e  g,OJHD.|.b.... N
    localhost:~/Documents # xxd .daiquiris.txt.broken | head -1
    00000000: 3040 2c39 2e6e bd2e 921d 8496 e563 652b  0@,9.n.......ce+
    

### Home Directory

The `bash_history` file shows four commands. First it checks the IP address
information. Then it runs `zypper refresh`. This is similar to a `apt update`
on Debian-based Linux machines. Next `openssh` is installed using `zypper`.
And then the box is shut down.

    
    
    localhost:~ # cat .bash_history
    #1622565496
    ip a
    #1623075831
    zypper refresh
    #1623075992
    zypper in --no-confirm openssh
    #1629999465
    poweroff
    

The `.bash_profile` file doesn’t have the normal stuff, but rather just sets
three ENV variables:

    
    
    export NUMBER1=2
    export NUMBER2=3
    export NUMBER3=37
    

I’ll need these later.

The `.bashrc` file also is unusually small, just setting one `alias`:

    
    
    alias FLARE="echo 'The 13th byte of the password is 0x35'"
    

This will make more sense later as well.

### zyppe

The root crontab file shows one that runs every minute:

    
    
    localhost:~ # crontab -l
    * * * * * /usr/lib/zyppe
    

Just running it, I don’t see any output or activity. I’ll pull back a copy of
the binary:

    
    
    $ sshpass -p flare scp root@10.1.1.193:/usr/lib/zyppe .
    

Running `strings` does show some interesting stuff:

    
    
    $ strings zyppe
    ...[snip]...
    readdir
    closedir
    __cxa_atexit
    remove
    opendir
    getenv
    ...[snip]...
    A secretH
     is no lH
    onger a H
    secret oH
    nce someH
    one knowH
    s it
    AWAVI
    AUATL
    []A\A]A^A_
    HOME
    /Documents
    broken
    .broken
     is now a secret
    ...[snip]...
    

That first group is showing commands related to reading files in a directory.
In the middle of the second group are references to `HOME` and `/Documents`,
as well as `.broken`. This binary seems related to the encrypted documents.

One quick test I thought to try at this point. I wrote a file into
`/Documents`:

    
    
    localhost:~/Documents # echo "hello" > 0xdf.txt
    localhost:~/Documents # ls
    0xdf.txt                 .daiquiris.txt.broken  iced_coffee.txt.broken      nutella.txt.broken    raisins.txt.broken     shopping_list.txt.broken  tiramisu.txt.broken      unagi.txt.broken
    backberries.txt.broken   donuts.txt.broken      instant_noodles.txt.broken  oats.txt.broken       rasberries.txt.broken  spaghetti.txt.broken      tomatoes.txt.broken
    banana_chips.txt.broken  dumplings.txt.broken   nachos.txt.broken           omelettes.txt.broken  reeses.txt.broken      strawberries.txt.broken   udon_noddles.txt.broken
    blue_cheese.txt.broken   ice_cream.txt.broken   natillas.txt.broken         oranges.txt.broken    sausages.txt.broken    tacos.txt.broken          ugali.txt.broken
    

Now I’ll run `zyppe`, and my file is encrypted:

    
    
    localhost:~/Documents # /usr/lib/zyppe
    0xdf.txt is now a secret
    localhost:~/Documents # ls -l 0xdf.txt.broken 
    -rw-r--r-- 1 root root 1024 Sep 17 17:35 0xdf.txt.broken
    localhost:~/Documents # cat 0xdf.txt.broken | xxd | head -1
    00000000: 0944 2375 761d ce0e fa7e f4f3 c51b 140b  .D#uv....~......
    

## zyppe

### RE

The program was rather quick to triage and get a high level feel for what was
going on. It builds the string `$HOME/Documents`, and passes that to
`opendir`. It then loops over files that don’t end in `.broken`, reads the
first kilobyte (0x400 == 1024 bytes), and passes it to the `encrypt` function:

![image-20210917210042971](https://0xdfimages.gitlab.io/img/image-20210917210042971.png)

And:

![image-20210917210206125](https://0xdfimages.gitlab.io/img/image-20210917210206125.png)

In `encrypt`, there’s a lot of shuffling data to make a cipher stream, but the
key thing I’ll notice is that the file contents are only used at the very end,
XORed by two values:

![image-20210917210743391](https://0xdfimages.gitlab.io/img/image-20210917210743391.png)

The Ghidra decompliation is a bit off here. The disassembly shows it’s not
actually the same value twice, but two different ones:

![image-20210917210840566](https://0xdfimages.gitlab.io/img/image-20210917210840566.png)

This video goes through it in a bit more detail:

### Capture Stream

Because the key stream doesn’t appear to depend on the input at all, but
rather is just created and then XORed against the input, if I can capture that
key stream, then I can XOR any encrypted file byte by byte with that stream
and decrypt it.

To capture the stream I’ll create a file with 1024 null bytes and encrypt it:

    
    
    $ python2 -c 'print "\x00"* 1024' > ~/Documents/null.txt
    $ ./zyppe 
    null.txt is now a secret
    

The contents of the encrypted nulls matches what I was seeing in the video
when I was manually pulling the stream:

    
    
    $ xxd ~/Documents/null.txt.broken
    00000000: 6121 4f19 1917 ce0e fa7e f4f3 c51b 140b  a!O......~......
    ...[snip]...
    

### Decrypt Script

With that, I’ll save that as `key`, and write a script that uses it to decrypt
any file:

    
    
    #!/usr/bin/env python3
    
    import sys
    
    
    with open('key', 'rb') as f:
        key = f.read()
    
    with open(sys.argv[1], 'rb') as f:
        enc = f.read()
    
    print(''.join([chr(i^j) for i,j in zip(key,enc) if i^j]))
    

It works:

    
    
    $ echo "This is a test" > ~/Documents/0xdf.txt
    $ ./zyppe 
    0xdf.txt is now a secret
    $ python3 decrypt.py ~/Documents/0xdf.txt.broken 
    This is a test
    

### Easier Decrypt

Because the program is just using a stream of random numbers and XORing the
data by that, the decryption is the same as the encryption, just XORing it
again. I can also then just rename all the files with `.broken` extension to
not have them, and encrypt them again, resulting in the plaintext files:

    
    
    localhost:~/Documents # find . -type f -name '*.broken' | while read fn; do mv $fn ${fn%.broken}; done
    

That will loop over the each file and move it from it’s current name to the
same name without `.broken`. The only tricky part in this loop is
`${fn%.broken}`. [This page](https://tldp.org/LDP/abs/html/string-
manipulation.html) is a great reference for manipulating Bash variables.

>
>     ${string%substring}
>  
>
> Deletes shortest match of `$substring` from back of `$string`.

So in this case, it’s removing `.broken`.

I can do this in the VM, and then SCP them back to my workstation for analysis
(not forgetting that one of the files starts with `.` and will need to be
SCPed independently).

## File Analysis

### General

There are 28 files now decrypted:

    
    
    $ ls -a
    .                banana_chips.txt  donuts.txt     iced_coffee.txt      natillas.txt  omelettes.txt  rasberries.txt  shopping_list.txt  tacos.txt     udon_noddles.txt
    ..               blue_cheese.txt   dumplings.txt  instant_noodles.txt  nutella.txt   oranges.txt    reeses.txt      spaghetti.txt      tiramisu.txt  ugali.txt
    backberries.txt  .daiquiris.txt    ice_cream.txt  nachos.txt           oats.txt      raisins.txt    sausages.txt    strawberries.txt   tomatoes.txt  unagi.txt
    

If I group them by first letter, there are three of each group, except for `s`
which has four:

    
    
    $ ls -a | grep -v '\.$' | cut -c1 | uniq -c
          3 b
          1 .   // actually a 'd', from `.daiquiris.txt`
          2 d
          3 i
          3 n
          3 o
          3 r
          4 s
          3 t
          3 u
    

’s’ has `shopping_list.txt` which is not a food like the rest.

### shopping_list.txt

`shopping_list.txt` has a list of foods with an obvious hint:

    
    
    $ cat shopping_list.txt 
    /
    [U]don noodles
    [S]trawberries
    [R]eese's
    /
    [B]anana chips
    [I]ce Cream
    [N]atillas
    /
    [D]onuts
    [O]melettes
    [T]acos
    

`/usr/bin/dot` \- running that prompts for a password:

    
    
    localhost:~ # /usr/bin/dot
    Password: password
    Wrong password!
    Password (ASCII):notpassword
    Wrong password!
    Password (ASCII):asdasd
    Wrong password!
    Password (ASCII):asd
    Wrong password!
    Password (ASCII):^C
    

On failing, it reminds me that the password is ASCII until I quit. I’ll need
this password.

I didn’t notice this until after solving, but the items in the list also give
an order to approach the clusters of three foods (start with `udon_noodles`,
then move to `strawberries`, `reese's`, etc).

### u files

The U foods confirm the point about grouping foods by their first letter:

    
    
    $ cat udon_noddles.txt 
    "ugali", "unagi" and "udon noodles" are delicious. What a coincidence that all of them start by "u"!
    $ cat ugali.txt 
    Ugali with Sausages or Spaghetti is tasty. It doesn’t matter if you rotate it left or right, it is still tasty! You should try to come up with a great recipe using CyberChef.
    $ cat unagi.txt 
    The 1st byte of the password is 0x45
    

They also give the first byte of the password, 0x45 or “E”.

### s files

The notes above mentioned the S works, as well as rotation and CyberChef. I’ll
load these three files into CyberChef and play with the “Rotate left” and
“Rotate Right” operations. On Rotate left with an Amount of 1, it pops into
ASCII text:

[![image-20210917214304132](https://0xdfimages.gitlab.io/img/image-20210917214304132.png)_Click
for full size
image_](https://0xdfimages.gitlab.io/img/image-20210917214304132.png)

Each file decodes to a message:

Filename | Decoded  
---|---  
`spaghetti.txt` | In the FLARE language “spaghetti” is “c3BhZ2hldHRp”.  
`sausages.txt` | The 2nd byte of the password is 0x34  
`strawberries.txt` | In the FLARE team we like to speak in code. You should learn our language, otherwise you want be able to speak with us when you escape (if you manage to escape!). For example, instead of “strawberries” we say “c3RyYXdiZXJyaWVz”.  
  
I’ve got the second character of the password, 0x34 or “4”, as well as another
hint. This time, it’s using Base64 to encode the words:

    
    
    $ echo c3BhZ2hldHRp | base64 -d
    spaghetti
    $ echo c3RyYXdiZXJyaWVz | base64 -d
    strawberries
    

### r files

The r files look like they have Base64 in them, so I’ll go there next:

    
    
    $ cat raisins.txt 
    VGhlIDNyZCBieXRlIG9mIHRoZSBwYXNzd29yZCBpcy4uIGl0IGlzIGEgam9rZSwgd2UgZG9uJ3QgbGlrZSByYWlzaW5zIQo=
    $ cat rasberries.txt 
    VGhlIDNyZCBieXRlIG9mIHRoZSBwYXNzd29yZCBpczogMHg1MQo=
    $ cat reeses.txt 
    V2UgTE9WRSAiUmVlc2UncyIsIHRoZXkgYXJlIGdyZWF0IGZvciBldmVyeXRoaW5nISBUaGV5IGFyZSBhbWF6aW5nIGluIGljZS1jcmVhbSBhbmQgdGhleSBldmVuIHdvcmsgYXMgYSBrZXkgZm9yIFhPUiBlbmNvZGluZy4K
    

Each file decodes to:

Filename | Decoded  
---|---  
`raisins.txt` | The 3rd byte of the password is.. it is a joke, we don’t like raisins!  
`rasberries.txt` | The 3rd byte of the password is: 0x51  
`reeces.txt` | We LOVE “Reese’s”, they are great for everything! They are amazing in ice-cream and they even work as a key for XOR encoding.  
  
0x51 is “Q”. The password is now “E4Q”, and another hint about an XOR key,
“Reese’s”

### b files

With the hint of the XOR key, I set up the recipe in CyberChef to execute
that:

![image-20210917215506447](https://0xdfimages.gitlab.io/img/image-20210917215506447.png)

Then I went looking for binary files to test. When I opened `backberries.txt`,
a message popped out in the Output:

[![image-20210917215539170](https://0xdfimages.gitlab.io/img/image-20210917215539170.png)_Click
for full size
image_](https://0xdfimages.gitlab.io/img/image-20210917215539170.png)

Each of the three files decodes:

Filename | Decoded  
---|---  
`backberries.txt` | If you are not good in maths, the only thing that can save you is to be a bash expert. Otherwise you will be locked here forever HA HA HA!  
`banana_chips.txt` | Are you good at maths? We love maths at FLARE! We use this formula a lot to decode bytes: “ENCODED_BYTE + 27 + NUMBER1 * NUMBER2 - NUMBER3”  
`blue_cheese.txt` | The 4th byte of the password is: 0x35  
  
0x35 is the “5” character, so the password is now “E4Q5”, and a hint about
decoding by doing math in Bash.

### i files

I’ve got the three environment variables from the `.bash_profile` above. I’ll
combine them as described in the hint to get -4:

    
    
    localhost:~ # expr 27 + $NUMBER1 \* $NUMBER2 - $NUMBER3
    -4
    

At first I didn’t think the i files one would be next because it was full of
`$` characters that I wasn’t sure what to do with but thought maybe they would
be complex Bash variables or something. The light clicked when I realized what
`$` \- 4 was - space.

I didn’t know how to do this one in CyberChef, but Python works:

    
    
    >>> with open('ice_cream.txt', 'rb') as f:
    ...     enc = f.read()
    ... 
    >>> print(''.join([chr(x-4) for x in enc if x > 0]))
    If this challenge is too difficult and you want to give up or just in case you got hungry, what about baking some muffins? Try this recipe:
    0 - Cinnamon
    1 - Butter 150gr
    2 - Lemon 1/2
    3 - Eggs 3
    4 - Sugar 150gr
    5 - Flour 250gr
    6 - Milk 30gr
    7 - Icing sugar 10gr
    8 - Apple 100gr
    9 - Raspberries 100gr
    
    Mix 0 to 9 and bake for 30 minutes at 180Â°C.
    

The three files decode to:

Filename | Decoded  
---|---  
`ice_cream.txt` | [Recipe above]  
`iced_coffee.txt` | The only problem with RC4 is that you need a key. The FLARE team normally uses this number: “SREFBE” (as an UTF-8 string). If you have no idea what that means, you should give up and bake some muffins.  
`instant_noodles.txt` | The 5th byte of the password is: 0xMS  
  
Obviously `MS` are not hex characters… but I have this recipe above, where
Milk is the “6” and Sugar is “4”. If I take that as 0x64, that’s a “d”, I now
have “E4Q5d”.

### n files

Given the hint about RC4 and the key, I first created a recipe in CyberChef
that looked like:

![image-20210917222604195](https://0xdfimages.gitlab.io/img/image-20210917222604195.png)

I tried on each of the remaining files, but none produced anything
interesting.

It says it “uses this number”. But “SFERBE” isn’t a number, unless I use the
recipe again to convert it to “493513”. When I change the passphrase, the n
files decrypt:

Filename | Decoded  
---|---  
`nachos.txt` | In the FLARE team we really like Felix Delastelle algorithms, specially the one which combines the Polybius square with transposition, and uses fractionation to achieve diffusion.  
`natillas.txt` | Do you know natillas? In Spain, this term refers to a custard dish made with milk and KEYWORD, similar to other European creams as crème anglaise. In Colombia, the delicacy does not include KEYWORD, and is called natilla.  
`instant_noodles.txt` | The 6th byte of the password is: 0x36  
  
Adding 0x36 as “6”, the password now has a 6th character, “E4Q5d6”.

### d files

First I need to find the cipher. Some googling of that name and the terms in
the hint leads to the [Wikipedia page for Bifid
cipher](https://en.wikipedia.org/wiki/Bifid_cipher):

> In classical [cryptography](https://en.wikipedia.org/wiki/Cryptography), the
> **bifid cipher** is a cipher which combines the [Polybius
> square](https://en.wikipedia.org/wiki/Polybius_square) with
> [transposition](https://en.wikipedia.org/wiki/Transposition_cipher), and
> uses
> [fractionation](https://en.wikipedia.org/wiki/Transposition_cipher#Fractionation)
> to achieve
> [diffusion](https://en.wikipedia.org/wiki/Confusion_and_diffusion). It was
> invented around 1901 by [Felix
> Delastelle](https://en.wikipedia.org/wiki/Felix_Delastelle).

Pulling that up in CyberChef, it needs a keyword. The second clue above leads
to research on “natillas”. The [Wikipedia
page](https://en.wikipedia.org/wiki/Natillas) describes how it’s made in
various locations, and comparing Spain and Colombia, Columbia is missing
vinilla and eggs. With “eggs” as the keyword, the d files decode:

Filename | Decoded  
---|---  
`.daiquiris.txt` | The 7th byte of the password is: 0x66  
`donuts.txt` | Did you know that Giovan Battista Bellaso loved microwaves?  
`instant_noodles.txt` | Are you missing something? You should search for it better! It’s hidden, but not really.  
  
The third clue is just a hint to look for the hidden `.daiquiris` file. 0x66
is “f”. The password now has a 7th character, “E4Q5d6f”.

### o files

[Giovan Battista
Bellaso](https://en.wikipedia.org/wiki/Giovan_Battista_Bellaso) invented the
Vigenère cipher. It’s a keyed cipher, and the clue suggests the key is
“microwaves”, and plugging that into CyberChef again works on the o files:

Filename | Decoded  
---|---  
`oats.txt` | You should follow the FLARE team in Twitter. They post a bunch of interesting stuff and have great conversation on Twitter!  
https://twitter.com/anamma_06  
https://twitter.com/MalwareMechanic  
`omelette.txt` | You should follow the FLARE team in Twitter. Otherwise they may get angry and not let you leave even if you get the flag.  
https://twitter.com/anamma_06  
https://twitter.com/osardar1  
https://twitter.com/MalwareMechanic  
`oranges.txt` | The 8th byte of the password is: 0x60  
  
The third clue is just a hint to look for the hidden `.daiquiris` file. With
0x60 as backtick, The password now has a 8 characters, “E4Q5d6f`”.

### t files

Some looking around on Twitter leads to [this
conversation](https://twitter.com/anamma_06/status/1414583864865996803):

![image-20210917232151830](https://0xdfimages.gitlab.io/img/image-20210917232151830.png)

From this I get:

  * AES, CBC mode
  * Key is “Sheep should sleep in a shed” + version of the OS of Flare VM. The Flare VM is SuSE 15.2.
  * IV is [@osardar1](https://twitter.com/osardar1)’s favorite food, and his profile says “PIZZA”.

All of that creates this operation:

![image-20210917234112208](https://0xdfimages.gitlab.io/img/image-20210917234112208.png)

The IV is slightly off, as the start of the decryted buffer is weird, but I
can get the main points:

Filename | Decoded  
---|---  
`tacos.txt` | WOOW..yD.CUU]C.Iou are very very close to get the flag! Be careful when converting decimal and hexadecimal values to ASCII and hurry up before we run out of tacos!  
`tiramisu.txt` | The 9DX.RIDU._V.the password is the atomic number of the element moscovium  
The 10th byte of the password is the bell number preceding 203  
The 12th byte of the password is the largest known number to be the sum of two
primes in exactly two different ways  
The 14th (and last byte) of the password is the sum of the number of
participants from Spain, Singapore and Indonesia that finished the FLARE-ON 7,
FLARE-ON 6 or FLARE-ON 5  
`tomatoes.txt` | It seU]C.I_E.QBU close to escape… We are preparing the tomatoes to throw at you when you open the door! It is only a joke…  
The 11th byte of the password is the number of unique words in
/etc/Quijote.txt  
The 13th byte of the password is revealed by the FLARE alias  
  
This gives clues for characters 9-14.

Position | Clue | Result  
---|---|---  
9 | atomic number of [moscovium](https://en.wikipedia.org/wiki/Moscovium) | 115 = “s”  
10 | [bell number](https://en.wikipedia.org/wiki/Bell_number) preceding 203 | 52 = “4”  
11 | number of unique words in `/etc/Quijote.txt` | 108 = “l”  
12 | [largest known number to be the sum of two primes in exactly two different ways](https://en.wikipedia.org/wiki/68_\(number\)) | 68 = “D”  
13 | revealed by the FLARE alias - noted from `.bashrc` earlier | 0x35 = “5”  
14 | sum of the number of participants from Spain, Singapore and Indonesia that finished the FLARE-ON 7, FLARE-ON 6 or FLARE-ON 5 |   
  
For 11, I used [this grep
trick](https://stackoverflow.com/questions/16489317/how-to-generate-list-of-
unique-words-from-text-file-in-ubuntu):

    
    
    localhost:~ # cat /etc/Quijote.txt | grep -o -E '\w+' | sort -u -f | wc -l
    108
    

For 14, there were three sites to check:

Year | Spain + Singapore + Indonesia  
---|---  
[Flare-On-7](https://www.fireeye.com/blog/threat-research/2020/10/flare-on-7-challenge-solutions.html) | 9 + 19 + 0 = 28  
[Flare-On-6](https://www.fireeye.com/blog/threat-research/2019/09/2019-flare-on-challenge-solutions.html) | 7 + 25 + 2 = 34  
[Flare-On-5](https://www.fireeye.com/blog/threat-research/2018/10/2018-flare-on-challenge-solutions.html) | 4 + 6 + 1 = 11  
Total | 28 + 34 + 11 = 73 = “I”  
  
So the password is: “E4Q5d6f`s4lD5I”

## Flag

I’ll run `dot` and enter the password to get the flag:

    
    
    localhost:~ # /usr/bin/dot
    Password: E4Q5d6f`s4lD5I
    Correct password!
    Flag: H4Ck3r_e5c4P3D@flare-on.com
    

**Flag: H4Ck3r_e5c4P3D@flare-on.com**

[](/flare-on-2021/flarelinuxvm)

