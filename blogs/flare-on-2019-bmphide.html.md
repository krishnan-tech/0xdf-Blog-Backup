# Flare-On 2019: bmphide

[flare-on](/tags#flare-on ) [ctf](/tags#ctf ) [flare-on-bmphide](/tags#flare-
on-bmphide ) [dnspy](/tags#dnspy ) [dotnet](/tags#dotnet ) [anti-
debug](/tags#anti-debug ) [steganography](/tags#steganography ) [reverse-
engineering](/tags#reverse-engineering )  
  
Oct 9, 2019

  * [[1] Memecat Battlestation](/flare-on-2019/memecat-battlestation.html)
  * [[2] Overlong](/flare-on-2019/overlong.html)
  * [[3] Flarebear](/flare-on-2019/flarebear.html)
  * [[4] DNS Chess](/flare-on-2019/dnschess.html)
  * [[5] demo](/flare-on-2019/demo.html)
  * [6] bmphide
  * [[7] wopr](/flare-on-2019/wopr.html)

![](https://0xdfimages.gitlab.io/img/flare2019-6-cover.png)

bmphide was my favorite challenge this year (that I got to). It was
challenging, yet doable and interesting. I’m given a bitmap image and a
Windows .NET executable. That executable is used to hide information in the
low bits of the image. I’ll have to reverse the exe to understand how to
extract the data. I’ll also have to work around some anti-debug.

## Challenge

> Tyler Dean hiked up Mt. Elbert (Colorado’s tallest mountain) at 2am to
> capture this picture at the perfect time. Never skip leg day. We found this
> picture and executable on a thumb drive he left at the trail head. Can he be
> trusted?

I’m given a 32-bit Windows .NET executable and a `.bmp` bitmap image file:

    
    
    $ file bmphide.exe image.bmp
    bmphide.exe: PE32 executable (console) Intel 80386 Mono/.Net assembly, for MS Windows
    image.bmp:   PC bitmap, Windows 3.x format, 1664 x 1248 x 24
    

The image is of a mountain:

![](https://0xdfimages.gitlab.io/img/image.bmp)

## Running It

Just running it throws an error about the arguments:

    
    
    C:\Users\0xdf\Desktop\flare6>bmphide.exe
    
    Unhandled Exception: System.IndexOutOfRangeException: Index was outside the bounds of the array.
       at BMPHIDE.Program.Main(String[] args)
    

Looks like I’ll need to reverse it to figure out what it’s looking for.

## Initial RE

### Static

Given this is a dotnet application, I opened it in `dnspy`, and located the
main function:

![1568231829318](https://0xdfimages.gitlab.io/img/1568231829318.png)

It is simple enough, taking three args, which I can guess are an image to put
the message into, the data to embed, and the output filename:

    
    
    private static void Main(string[] args)
    {
    	Program.Init();
    	Program.yy += 18;
    	string filename = args[2];
    	string fullPath = Path.GetFullPath(args[0]);
    	string fullPath2 = Path.GetFullPath(args[1]);
    	byte[] data = File.ReadAllBytes(fullPath2);
    	Bitmap bitmap = new Bitmap(fullPath);
    	byte[] data2 = Program.h(data);
    	Program.i(bitmap, data2);
    	bitmap.Save(filename);
    }
    

It reads the first arg file into a `Bitmap`, and the second arg file into
`data`. It passes `data` into `Program.h()`, and stores the result as `data2`.
Then `bitmap` and `data2` are passed into `Program.i()`, and then `bitmap` is
saved to the filename from the third arg.

Given the exe name, the challenge prompt, I suspect this program is designed
to perform stegonagraphy, hiding some data inside an image. Based on this, I
can guess that `h()` encodes/encrypts the data somehow, and `i()` combines the
data into the image. If I can understand what goes on in `h` and `i`, and
reverse it, I can get the original data back out.

### Running It

At this point, I wanted to try to run it again. And I got it roughly working,
as the following returns without error:

    
    
    C:\Users\0xdf\Desktop\flare6>bmphide.exe image.bmp bmphide.exe exe.bmp
    

My theory is that it just took the `bmphide.exe` file, and encoded it and
stored it in the low bits of `exe.bmp`. Looking at them, `exe.bmp` looks the
same as `image.bmp`. But if I look in a hex editor, I can confirm that the low
bits are different:

    
    
    $ xxd image.bmp | head
    00000000: 424d 3610 5f00 0000 0000 3600 0000 2800  BM6._.....6...(.
    00000010: 0000 8006 0000 e004 0000 0100 1800 0000  ................
    00000020: 0000 0000 0000 c40e 0000 c40e 0000 0000  ................
    00000030: 0000 0000 0000 3d60 7055 7a8c 2a54 6717  ......=`pUz.*Tg.
    00000040: 3c4c 224e 5e18 4655 2c58 686a 9ea5 588a  <L"N^.FU,Xhj..X.
    00000050: 9a2c 666e 184a 5929 5c6d 2956 664c 7485  .,fn.JY)\m)VfLt.
    00000060: 3352 6227 4055 5574 8242 5e6d 3950 623a  3Rb'@UUt.B^m9Pb:
    00000070: 5265 314e 5a20 384e 2444 511d 384e 415e  Re1NZ 8N$DQ.8NA^
    00000080: 6861 8095 4e68 7a2f 4a5d 2744 572d 4e5e  ha..Nhz/J]'DW-N^
    00000090: 3f58 6931 586d 6794 a03c 708e 0c42 5240  ?Xi1Xmg..<p..BR@
    
    $ xxd exe.bmp | head
    00000000: 424d 3610 5f00 0000 0000 3600 0000 2800  BM6._.....6...(.
    00000010: 0000 8006 0000 e004 0000 0100 1800 0000  ................
    00000020: 0000 0000 0000 c40e 0000 c40e 0000 0000  ................
    00000030: 0000 0000 0000 3c61 7454 7b8c 2851 6414  ......<atT{.(Qd.
    00000040: 3b4c 2049 5c18 4354 2e59 6e6a 9da4 5a8d  ;L I\.CT.Ynj..Z.
    00000050: 9d2e 636e 194b 5c2a 596c 2855 614c 7782  ..cn.K\*Yl(UaLw.
    00000060: 3357 6225 4154 5471 8440 5b6c 3851 6438  3Wb%ATTq.@[l8Qd8
    00000070: 5364 3049 5c20 3b4c 2441 541c 3b4c 4059  Sd0I\ ;L$AT.;L@Y
    00000080: 6c60 8394 4c69 7c2c 4b5c 2441 542c 4b5c  l`..Li|,K\$AT,K\
    00000090: 3c59 6c30 5b6c 6794 a03c 708e 0c42 5240  <Yl0[lg..<p..BR@
    

Once I get past the header, at 0x36 I start to see the low bits changing.

### h()

The two functions I need to look at now are `h()` and `i()`. Since `h()`
encodes the data, I’ll take a look at that first:

    
    
    public static byte[] h(byte[] data)
    {
    	byte[] array = new byte[data.Length];
    	int num = 0;
    	for (int i = 0; i < data.Length; i++)
    	{
    		int num2 = (int)Program.f(num++);
    		int num3 = (int)data[i];
    		num3 = (int)Program.e((byte)num3, (byte)num2);
    		num3 = (int)Program.a((byte)num3, 7);
    		int num4 = (int)Program.f(num++);
    		num3 = (int)Program.e((byte)num3, (byte)num4);
    		num3 = (int)Program.c((byte)num3, 3);
    		array[i] = (byte)num3;
    	}
    	return array;
    }
    

Pretty simple. There’s a series of functions, a counter (`num`), and a loop
over `data`, writing results to `array`.

## Anti Debug

I took a quick glance into `f`, `e`, `a`, and `c`, and they look like complex
mixing functions. I want to try to debug the binary so I can watch data pass
through these. I’ll select “Debug -> Start Debugging…”, and enter the same
command line I just successfully ran from `cmd`:

![1568994918870](https://0xdfimages.gitlab.io/img/1568994918870.png)

On clicking “OK”, I reach my break point at the entry point:

![1568995022991](https://0xdfimages.gitlab.io/img/1568995022991.png)

When I try to step over `Program.Init()`, it throws an error:

![1568995096542](https://0xdfimages.gitlab.io/img/1568995096542.png)

To try to get around this, I’ll take a new strategy of starting the program
from the command line, and then trying to (very) quickly attach `dnspy` to the
running process. My hypothesis here is that if I attach after
`Program.Init()`, perhaps I’ll have bypassed the anti-debug.

It takes a couple tries, but I get it attached while the program is still in
`h`. It’s there I notice something else weird. When I’m at the start of the
loop, and I step into the call for `f.(num++)`, I don’t go to `f`, but `g`:

![](https://0xdfimages.gitlab.io/img/bmphide-disassembly.gif)

In that gif, I’ll open up the disassembly, and see it’s been changed. My new
theory is that `Program.Init()` does two things - changes the function calls,
and crashes if a debugger is attached. I spent some time checking out the
rest, and the only thing that seems to change is the functions called. Instead
of calling `f`, `e`, `a`, `f`, `e`, `c` like shown above, it calls `g`, `e`,
`b`, `g`, `e`, `d`.

## Functions in h()

### e()

It’s not the first function called, but `e()` is actually called in other
functions, so I’ll break it down first.

    
    
    public static byte e(byte b, byte k)
    {
    	for (int i = 0; i < 8; i++)
    	{
    		bool flag = (b >> i & 1) == (k >> i & 1);
    		if (flag)
    		{
    			b = (byte)((int)b & ~(1 << i) & 255);
    		}
    		else
    		{
    			b = (byte)((int)b | (1 << i & 255));
    		}
    	}
    	return b;
    }
    

The function takes two bytes. It then walks each bit. `flag` is true if the
ith bit for b and k is the same. If `flag`, then that bit is turned to a 0 in
`b`, else that bit is turned to a 1 in `b`. This is just `xor`.

### g()

`g()` is just some math:

    
    
    public static byte g(int idx)
    {
    	byte b = (byte)((long)(idx + 1) * (long)((ulong)-306674912));
    	byte k = (byte)((idx + 2) * 1669101435);
    	return Program.e(b, k);
    }
    

I actually think the disassembly for setting `b` (and perhaps `k`) might be
clearer:

    
    
    ;     byte b = (byte)((long)(idx + 1) * (long)((ulong)-306674912));
    01063399 90                   nop
    
    0106339A 8B45FC               mov     eax,[ebp-4]
    0106339D 40                   inc     eax
    0106339E BAC56F6B12           mov     edx,126B6FC5h
    010633A3 33C9                 xor     ecx,ecx
    010633A5 0FAFC2               imul    eax,edx
    010633A8 25FF000000           and     eax,0FFh
    010633AD 8945F8               mov     [ebp-8],eax
    
    ;     byte k = (byte)((idx + 2) * 1669101435);
    010633B0 8B45FC               mov     eax,[ebp-4]
    010633B3 40                   inc     eax
    010633B4 40                   inc     eax
    010633B5 69C07DC9820C         imul    eax,0C82C97Dh
    010633BB 25FF000000           and     eax,0FFh
    010633C0 8945F4               mov     [ebp-0Ch],eax
    

So, `b = ((idx + 1) * 0x126B6FC5) & 0xFF`, and `k = ((idx+2) * 0xC82C97D)
0xFF`, and then those two bytes are xored and the result is returned.

I started a file called `funcs.py`, and created `g()`:

    
    
    def g(idx):
        b = ((idx + 1) * 0x126B6FC5) & 255
        k = ((idx + 2) * 0xC82C97D) & 255
        return b ^ k
    

### b()

I’ll do the same thing with `b()`:

    
    
    public static byte b(byte b, int r)
    {
    	for (int i = 0; i < r; i++)
    	{
    		byte b2 = (b & 128) / 128;
    		b = (b * 2 & byte.MaxValue) + b2;
    	}
    	return b;
    }
    

This is definitely some scrambling. Rather then break down the algorithm, I
created my python function:

    
    
    def b(b_, r):
        for i in range(r):
            b2 = (b_ & 128) // 128
            b_ = ((b_ * 2) & 255) + b2
        return b_
    

I also noticed that this is only called with a static `r` value of 7. I’ll
take a look at the values that come out:

    
    
    df@df:~/flareon/6 - bmphide$ python3
    Python 3.6.8 (default, Aug 20 2019, 17:12:48)
    [GCC 8.3.0] on linux
    Type "help", "copyright", "credits" or "license" for more information.
    >>> from funcs import *
    >>> for i in range(10):
    ...     b(i, 7)
    ...
    0
    128
    1
    129
    2
    130
    3
    131
    4
    132
    

It seems `b(i, 7) == i/2 + (127.5 * (i mod 2))`. For even numbers, that’s
`i/2`. For odd, that’s `i/2 + 127.5`. I checked 0 through 255, and it holds
up.

### d()

`d()` is similar to be, in that it takes two args, but is only ever called
with the second arg of 3:

    
    
    public static byte d(byte b, int r)
    {
    	for (int i = 0; i < r; i++)
    	{
    		byte b2 = (b & 1) * 128;
    		b = (b / 2 & byte.MaxValue) + b2;
    	}
    	return b;
    }
    

I’ll do the same thing and create a `python` version:

    
    
    def d(b, r):
        for i in range(r):
            b2 = (b & 1) * 128
            b = ((b // 2) & 255) + b2
        return b
    

And again, running it shows a pattern:

    
    
    >>> for i in range(10):
    ...     d(i, 3)
    ... 
    0
    32
    64
    96
    128
    160
    192
    224
    1
    33
    

This one works out to `d(i, 3) == 32 * (i mod 8) + i//8` (where `//`
represents integer division).

### h() in python

Given my understanding of these functions, I wrote `h()` in python, but rather
than looping over all data, it takes an `i` and a byte and outputs what
`array[i]` will be:

    
    
    def h_one(byte, i):
        num2 = g(2*i)
        num3 = byte
        num3 = num3 ^ num2
        num3 = b(num3, 7)
        num4 = g(2*i + 1)
        num3 = num3 ^ num4
        num3 = d(num3, 3)
        return num3
    

I can test this by breaking at the start of the loop in my debugger, observing
the `i` and `data[i]`. I can run my code to see what the output will be, and
then check that the output matches what is eventually stored in `array`.

## Invert h()

Now I want to be able to find the inverse of `h()`. This would start with `i`
and `array[i]`, and output `data[i]`. Given the code above, I can work
backwards and invert some of the functions. Since `i` is the same working
backwards and forwards, so are functions that only rely on `i`, like `g()`. On
the other hand, I’ll need to invert `e()`, `b()`, and `d()`, though the
inverse of `e()` is just `e()` (since `e()` is `xor`).

Since `b()` and `d()` are only called with specific second arguments, I’m only
going to worry about inverting them for those arguments.

I end up with:

    
    
    def h_inv_one(byte, i):
        num3 = byte
        num3 = d_inv_3(num3)
        num4 = g(2*i + 1)
        num3 = num3 ^ num4
        num3 = b_inv_7(num3)
        num2 = g(2*i)
        num3 = num3 ^ num2
        return num3
    
    def b_inv_7(b_):
        if b_ > 127:
            return ((2*b_) - 255)
        else:
            return 2*b_
    
    def d_inv_3(b):
        return (b//32) + 8*(b%32)    
    

I can test this by showing that for a random `byte` (0-255) and a random `i`
(0-10000, and while `i` could go higher, no reason to think it’d work
differently), that `h_inv(h(byte, i), i) == byte`. For example:

    
    
    >>> h_inv_one(h_one(223, 1034), 1034) == 223
    True
    

Or if I wanted to test with 300,000 randomly generated `byte` and `i`:

    
    
    >>> random_byte_and_i = [(random.randint(0,255), random.randint(0,10000)) for x in range(300000)]
    >>> all([(h_inv_one(h_one(byte, i), i) == byte) for byte,i in random_byte_and_i])
    True
    

I feel good now that I have python that can reverse the encoding.

## i()

Now I need to look at `i()` to see how the encoded data is written into the
image:

    
    
    public static void i(Bitmap bm, byte[] data)
    {
    	int num = Program.j(103);
    	for (int i = Program.j(103); i < bm.Width; i++)
    	{
    		for (int j = Program.j(103); j < bm.Height; j++)
    		{
    			bool flag = num > data.Length - Program.j(231);
    			if (flag)
    			{
    				break;
    			}
    			Color pixel = bm.GetPixel(i, j);
    			int red = ((int)pixel.R & Program.j(27)) | ((int)data[num] & Program.j(228));
    			int green = ((int)pixel.G & Program.j(27)) | (data[num] >> Program.j(230) & Program.j(228));
    			int blue = ((int)pixel.B & Program.j(25)) | (data[num] >> Program.j(100) & Program.j(230));
    			Color color = Color.FromArgb(Program.j(103), red, green, blue);
    			bm.SetPixel(i, j, color);
    			num += Program.j(231);
    		}
    	}
    }
    

At first, this looks a bit daunting, especially when I look at the mess that
is `j()`. However, I’ll notice that `j()` is being called on static ints only.
There’s no reason I can’t replace calls to `j()` with the values they return.
I’ll walk through with the debugger and record the output of `j()` for each
input it receives:

x | j(x)  
---|---  
103 | 0  
231 | 1  
27 | 0xf8 (1111 1000)  
228 | 7  
230 | 3  
25 | 0xfc (1111 1100)  
100 | 6  
  
Knowing that, I can re-write `i`:

    
    
    public static void i(Bitmap bm, byte[] data)
    {
    	int num = 0;
    	for (int i = 0; i < bm.Width; i++)
    	{
    		for (int j = 0; j < bm.Height; j++)
    		{
    			bool flag = num > data.Length - 1;
    			if (flag)
    			{
    				break;
    			}
    			Color pixel = bm.GetPixel(i, j);
    			int red = ((int)pixel.R & 0xf8) | ((int)data[num] & 7);
    			int green = ((int)pixel.G & 0xf8) | (data[num] >> 3 & 7);
    			int blue = ((int)pixel.B & 0xfc) | (data[num] >> 6 & 3);
    			Color color = Color.FromArgb(0, red, green, blue);
    			bm.SetPixel(i, j, color);
    			num += 1;
    		}
    	}
    }
    

Now it’s much easier to read. It reads a pixel. Then it overwrites the low
three bits of red with the low three bits of the byte, the low three bits of
green with the next three bits, and the low two bits of blue with the high two
bits of the byte. Then it writes the pixel.

## Inverting i()

I want to do the opposite of this. So I’ll read a pixel, get the RGB values,
and get the low three (for red and green) or two (for blue) bits, and use them
to form the byte. It will look like:

    
    
    for x in range(width):
        for y in range(height):
            rp, gp, bp = im.getpixel((x,y))
    
            value = (rp & 7) | ((gp & 7) << 3) | ((bp & 3) << 6)
            i = y + (x*height)
    
            cipher.append(value)
            plaintext = h_inv_one(value, i)
    
            data.append(plaintext)
    

## Extracting a Message

All of that comes together into a python script that will take an image and
output the hidden data:

    
    
    #!/usr/bin/env python3
    
    import sys
    from PIL import Image
    
    
    def g(idx):
        b = ((idx + 1) * 0x126B6FC5) & 255
        k = ((idx + 2) * 0xC82C97D) & 255
        return b ^ k
    
    
    def d_inv_3(b):
        return (b//32) + 8*(b%32)
    
    
    def b_inv_7(b_):
        if b_ > 127:
            return ((2*b_) - 255)
        else:
            return 2*b_
    
    
    def h_inv_one(byte, i):
        num3 = byte
        num3 = d_inv_3(num3)
        num4 = g(2*i + 1)
        num3 = num3 ^ num4
        num3 = b_inv_7(num3)
        num2 = g(2*i)
        num3 = num3 ^ num2
        return num3
    
    
    if __name__ == "__main__":
    
        data = bytearray()
        cipher = []
    
        im = Image.open(sys.argv[1])
        width, height = im.size
    
        for x in range(width):
            for y in range(height):
                rp, gp, bp = im.getpixel((x,y))
    
                value = (rp & 7) | ((gp & 7) << 3) | ((bp & 3) << 6)
                i = y + (x*height)
    
                cipher.append(value)
                plaintext = h_inv_one(value, i)
    
                data.append(plaintext)
    
        with open(sys.argv[2], 'wb') as f:
            f.write(data)
    

I can run this on the given image and get output:

    
    
    $ ./extract.py image.bmp extracted
    $ file extracted 
    extracted: PC bitmap, Windows 3.x format, 832 x 624 x 24
    

Surprising that the output is another bmp. It is a valid image:

![](https://0xdfimages.gitlab.io/img/bmphide-extracted.bmp)

I’ll extract on it again:

    
    
    $ ./extract.py extracted extracted2
    

And get another `.bmp`:

    
    
    $ file extracted2 
    extracted2: PC bitmap, Windows 3.x format, 234 x 312 x 24
    

This one has a flag in it:

![](https://0xdfimages.gitlab.io/img/bmphide-extracted2.bmp)

**Flag: d0nT_tRu$t_vEr1fy@flare-on.com**

[](/flare-on-2019/bmphide.html)

