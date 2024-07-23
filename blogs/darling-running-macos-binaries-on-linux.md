# Darling: Running MacOS Binaries on Linux

[tools](/tags#tools ) [bsides-london](/tags#bsides-london ) [ctf](/tags#ctf )
[darling](/tags#darling ) [python](/tags#python ) [mach-o](/tags#mach-o )
[macos](/tags#macos )  
  
Jul 1, 2019

Darling: Running MacOS Binaries on Linux

`![](https://0xdfimages.gitlab.io/img/darling-cover.png)I attended BSides
London almost a month ago now, and of course took a look at the CTF. There
were a handful of reversing challenges, but multiple of them were MacOS
(Mach-O) binaries. As I looked down at my Windows laptop and my Kali VM, I
felt at a bit of a disadvantage. While I was able to solve one of the
challenges just with IDA, I went looking for a way to run Mac binaries on a
Linux OS. And I found Darwin. It took basically the rest of the day to
install, so I didn’t get to any of the additional challenges, but I am happy
to be semi-equiped the next time the need comes up.

## Darling

### Background

[Darling](http://www.darlinghq.org/) is a translation layer allowing you to
run macOS software on Linux. It is just like how Wine lets you run Windows
exes on Linux.

### Installation

Installation isn’t hard, but it take a long time. The install instructions
were straight forward, but I did have to adjust one thing for Kali. I used the
Ubuntu `apt install` line for dependencies, but `linux-headers-generic` didn’t
exist. I just removed that item, and the installed worked. I already had some
headers installed, so if just removing it doesn’t work for you, try to install
these, likely the `common` one:

    
    
    root@kali# apt list --installed linux-headers-*
    Listing... Done
    linux-headers-4.18.0-kali1-amd64/now 4.18.6-1kali1 amd64 [installed,local]
    linux-headers-4.18.0-kali1-common/now 4.18.6-1kali1 all [installed,local]
    linux-headers-4.19.0-kali1-amd64/now 4.19.13-1kali1 amd64 [installed,local]
    linux-headers-4.19.0-kali1-common/now 4.19.13-1kali1 all [installed,local]
    linux-headers-4.19.0-kali4-amd64/now 4.19.28-2kali1 amd64 [installed,local]
    linux-headers-4.19.0-kali4-common/now 4.19.28-2kali1 all [installed,local]
    linux-headers-amd64/now 4.19+104+kali1 amd64 [installed,upgradable to: 4.19+105+kali1]
    

Then it was just a matter of `git clone`, followed by `build`/`cmake`/`make`.
The build process took about 6 hours on my machine.

### Testing

Now I can run the test that is the top of the Darling website:

    
    
    root@kali# uname
    Linux
    root@kali# darling shell
    Darling [/root/bsides-london-2019]# uname
    Darwin
    

### Next Steps

I won’t get to it today, but there’s a project on GitHub that provides [gdb
for Darling](https://github.com/darlinghq/darling-gdb). I’d like to install
this and play around with it. That could be a future post. If it is, I’ll join
it to this one.

## BSides London CTF: coffee

### Challenge

I originally solved this with just ida, but it’s nice to see the program run.
I’m given a file, `coffee`:

    
    
    root@kali# file coffee
    coffee: Mach-O 64-bit x86_64 executable, flags:<NOUNDEFS|DYLDLINK|TWOLEVEL|PIE>
    

When I run it, I get a sad face with a usage telling me I need to give it a
key:

![1561961987780](https://0xdfimages.gitlab.io/img/1561961987780.png)

### Testing

If I run it with some incorrect input, it puts out a message, but that message
is garbled:

    
    
    Darling [~/bsides-london-2019]# ./coffee 0xdf
           a$$$$$$$$$$a
         a$$$$$$$$$$$$$$a
       a$$$$$$$$$$$$$$$$$$a
      a$$$$$$$$$$$$$$$$$$$$a
     a$$$$$   $$$$$$   $$$$$a
    a$$$$$     $$$$     $$$$$a
    a$$$$$$$ $$$$$$$$$$$$$$$$a
    a$$$$$$$ $$$$$$$$$$$$$$$$a
    a$$$$$$$$$$$$$$$$$$$$$$$$a
     a$$$$$$          $$$$$$a
      a$$$$  $$$$$$$$  $$$$a
       a$$ $$$$$$$$$$$$ $$a
         a$$$$$$$$$$$$$$a
           a$$$$$$$$$$a
            I <3 Java
    
    Mr Sadface is sad, can you unlock his happiness by giving him the right key?
    
    If you know, you know -> |9<d`oyccqEkYkPAfFcyP^gOPzCkAo[UXc[bPBfMgULzZUzYnmJw
    

Putting in numbers seems to get the output changing:

    
    
    Darling [~/bsides-london-2019]# for i in {1..5}; do ./coffee $i | grep 'If you know'; done
    If you know, you know -> }8=eanxbbpDjXjQ@gGbxQ_fNQ{Bj@nZTYbZcQCgLfTM{[T{XolKv
    If you know, you know -> ~;>fbm{aasGi[iRCdDa{R\eMRxAiCmYWZaY`R@dOeWNxXWx[loHu
    If you know, you know -> :?gclz``rFhZhSBeE`zS]dLSy@hBlXV[`XaSAeNdVOyYVyZmnIt
    If you know, you know -> x=8`dk}gguAo]oTEbBg}TZcKT~GoEk_Q\g_fTFbIcQH~^Q~]jiNs
    If you know, you know -> y<9aej|fft@n\nUDcCf|U[bJUFnDj^P]f^gUGcHbPI_P\khOr
    

### Reversing

I’ll open this in IDA and take a look. There’s only two real functions,
`_main` and `_coffee_sadface`. The latter just prints the sadface message I’ve
seen a couple times now.

`_main` is just a couple of branches, with one loop:

![1561962312091](https://0xdfimages.gitlab.io/img/1561962312091.png)

Looking at the bottom right area where the loop is, I can see a couple things:

![1561962403536](https://0xdfimages.gitlab.io/img/1561962403536.png)

  1. A string that’s very similar to what I saw in the output is loaded and passed to `memcpy`, putting it into what I’ve named `buffer`.
  2. A variable I’ve named `counter` will start at 0, and then the loop will run until the counter hits 53, then it will jump out.
  3. When it jumps out, it will call `printf` with the “If you know” string and `buffer`.
  4. In the loop, it reads the next byte, xors it with the input number, and writes it back to the buffer.

At this point, I can jump over to python. I know the flags take the format
`S33n0eViL{}` (or it might have been `S3en0eViL`…I don’t quite remember, and
you’ll see why I can’t prove it in a minute). So I can just `xor` the first
byte in the seed with `S` and get the key:

    
    
    root@kali# python3
    Python 3.7.3rc1 (default, Mar 13 2019, 11:01:15) 
    [GCC 8.3.0] on linux
    Type "help", "copyright", "credits" or "license" for more information.
    >>> seed = '|9<d`oyccqEkYkPAfFcyP^gOPzCkAo[UXc[bPBfMgULzZUzYnmJw'
    >>> ord(seed[0])^ord('S')
    47
    >>> ''.join([chr(47^ord(x)) for x in seed])
    'S\x16\x13KO@VLL^jDvD\x7fnIiLV\x7fqH`\x7fUlDn@tzwLtM\x7fmIbHzcUuzUvABeX'
    

Well… that’s not exactly what I was hoping for. Could it be a multi-byte xor?
What if I look for the second byte:

    
    
    >>> ord(seed[1])^ord('3')
    10
    >>> ''.join([chr(10^ord(x)) for x in seed])
    'v36njesii{OaSaZKlLisZTmEZpIaKeQ_RiQhZHlGm_FpP_pSdg@}'
    

That actually looks really good, including the `{}` in the right spots. I can
try this to get the full flag:

    
    
    >>> ''.join([chr(10^ord(x)) if i % 2 else chr(47^ord(x)) for i,x in enumerate(seed)])
    'S3\x13nOeViL{java\x7fKILLs\x7fTHE\x7fplanet_with\x7fHIGH_cpu_USAge}'
    

I can’t quite explain what the 5 non-ascii bytes are. But with a couple
guesses, I can fill them in by hand, and get a flag that is accepted:

`S33nOeViL{java_KILLs_THE_planet_with_HIGH_cpu_USAge}`

[](/2019/07/01/darling-running-macos-binaries-on-linux.html)

