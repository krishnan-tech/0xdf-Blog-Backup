# Flare-On 2021: spel

[flare-on](/tags#flare-on ) [ctf](/tags#ctf ) [flare-on-spel](/tags#flare-on-
spel ) [reverse-engineering](/tags#reverse-engineering ) [ghidra](/tags#ghidra
) [unpack](/tags#unpack ) [shellcode](/tags#shellcode ) [dll](/tags#dll )
[x64dbg](/tags#x64dbg ) [anti-debug](/tags#anti-debug )  
  
Oct 25, 2021

  * [[1] credchecker](/flare-on-2021/credchecker)
  * [[2] known](/flare-on-2021/known)
  * [[3] antioch](/flare-on-2021/antioch)
  * [[4] myaquaticlife](/flare-on-2021/myaquaticlife)
  * [[5] FLARE Linux VM](/flare-on-2021/flarelinuxvm)
  * [[6] PetTheKitty](/flare-on-2021/petthekitty)
  * [7] spel
  * [[8] beelogin](/flare-on-2021/beelogin)
  * [9] evil - no writeup :(
  * [[10] wizardcult](/flare-on-2021/wizardcult)

![spel](https://0xdfimages.gitlab.io/img/flare2021-spel-cover.png)

spel was a Russian nesting doll of binaries. It starts with a giant function
that has thousands move instructions setting a single byte at a time into a
buffer and then calling it. That buffer is shellcode that loads and calls a
DLL. That DLL loads and calls a function from a second DLL. In that DLL, there
are a series of checks that cause the program to exit (different file name,
network connection), before the flag bytes are eventually decoded from a PNG
resource in the original binary, and then scrambled into an order only
observable in debug.

## Challenge

> Pro-tip: start disassembling this one then take a nice long break, you’ve
> earned it kid.

The [download](/files/flare2021-07_spel.7z) (password “flare”) has a single
Windows x64 executable:

    
    
    $ file spel.exe 
    spel.exe: PE32+ executable (GUI) x86-64, for MS Windows
    

## Running It

Running the application pops a box with what looks like an error:

![image-20210923153142148](https://0xdfimages.gitlab.io/img/image-20210923153142148.png)

I happened to have Process Hacker open, and I noticed that when I close
`spel.exe`, it doesn’t exit:

![image-20210923153319480](https://0xdfimages.gitlab.io/img/image-20210923153319480.png)

I killed that process, and started Procmon to see what might be going on. When
I clicked close, the first thing that happen is two Thread Create operations.
Two more are created 18 seconds later. The threads complete, with all seven of
eight threads exiting, three 30 seconds later, two more 75 seconds after that,
and the last two a minute after that. Then, almost three minutes later, two
new threads start. A minute later, exactly six minutes after closing the
window, all three remaining threads exit and the process exits.

![image-20210923154056719](https://0xdfimages.gitlab.io/img/image-20210923154056719.png)

## RE

### Resources

The application has a good number of resources (as shown in Resource Hacker):

![image-20210923160109670](https://0xdfimages.gitlab.io/img/image-20210923160109670.png)

`AFX_DIALOG_LAYOUT` didn’t have any thing interesting. `Cursor` has 16
different cursor images. `Bitmap` has two other images. `Icon` has 16x16 and
32x32 versions of the icon that shows at the top left. `Cursor Group` has 15
groups of the icons. `Icon Group` has a resource with the two icons. `Version
Info` and `Manifest` don’t contain much interesting beyond what they say they
are.

`PNG` contains a single resource, but it doesn’t load as an image, but it’s
corrupted:

![image-20210923160542096](https://0xdfimages.gitlab.io/img/image-20210923160542096.png)

I tried downloading the file and confirmed it doesn’t load. It does have the
PNG file signature though:

    
    
    $ file PNG128.png
    PNG128.png: PNG image data, 100 x 100, 8-bit/color RGBA, non-interlaced
    $ xxd PNG128.png 
    00000000: 8950 4e47 0d0a 1a0a 0000 000d 4948 4452  .PNG........IHDR
    00000010: 0000 0064 0000 0064 0806 0000 0070 e295  ...d...d.....p..
    00000020: 5400 0000 0662 4b47 4400 ff00 ff00 ffa0  T....bKGD.......
    00000030: bda7 9300 0000 0970 4859 7300 002e 2300  .......pHYs...#.
    00000040: 002e 2301 78a5 3f76 0000 0007 7449 4d45  ..#.x.?v....tIME
    00000050: 07e5 0717 0003 175d 4d45 a300 0000 19d7  .......]ME......
    00000060: fb7e 628d ab87 65cd 7185 ce53 0f5a 8c2d  .~b...e.q..S.Z.-
    00000070: 8a45 3712 4b79 1d40 da76 8626 d3d3 7217  .E7.Ky.@.v.&..r.
    00000080: 0000 003e 4944 4154 78da edc1 3101 0000  ...>IDATx...1...
    00000090: 00c2 a0f5 4f6d 0b2f a000 0000 0000 0000  ....Om./........
    000000a0: 0000 0000 0000 0000 0000 0000 0000 0000  ................
    000000b0: 0000 0000 0000 0000 0000 0000 0000 0080  ................
    000000c0: a701 9ca4 0001 d87b 1c5e 0000 0000 4945  .......{.^....IE
    000000d0: 4e44 ae42 6082                           ND.B`.
    

The other interesting set of resources is `Dialog`:

![image-20210923160720931](https://0xdfimages.gitlab.io/img/image-20210923160720931.png)

Each contains a GUI view:

![image-20210923160741242](https://0xdfimages.gitlab.io/img/image-20210923160741242.png)
![image-20210923160753598](https://0xdfimages.gitlab.io/img/image-20210923160753598.png)
![image-20210923160813093](https://0xdfimages.gitlab.io/img/image-20210923160813093.png)
![image-20210923160830233](https://0xdfimages.gitlab.io/img/image-20210923160830233.png)
![image-20210923160843496](https://0xdfimages.gitlab.io/img/image-20210923160843496.png)
![image-20210923160857694](https://0xdfimages.gitlab.io/img/image-20210923160857694.png)

102 seems to be the one used to display the error messages.

### Unpack

Loading this into Ghidra takes a while to analyze, which isn’t surprising
given the challenge text. By my quick count, there are 4918 functions in this
executable.

#### Find Buffer

Just poking around I stumbled on the function at 0x2cb0. It’s not hard to do
because it is _huge_. Ghidra can’t decompile it:

![image-20210924113752704](https://0xdfimages.gitlab.io/img/image-20210924113752704.png)

The vast majority of the file is just single byte move instructions like this:

![image-20210924113855973](https://0xdfimages.gitlab.io/img/image-20210924113855973.png)

It’s moving single bytes onto the stack. I did notice the last five bytes,
after a lot of nulls, are “flare”.

It turned out not to be necessary, but I was able to rebuild the buffer in
Python. I’ll read the in binary:

    
    
    >>> with open('spel.exe', 'rb') as f:
    ...     exe = f.read()
    ... 
    

The first `MOV` is at 0x2d77 with the bytes 0xc684 being the start of the
command:

    
    
    >>> exe[0x2d67:0x2d69]
    b'\xc6\x84'
    

Now I’ll just loop over the program until I find a different instruction:

    
    
    >>> res = b''
    >>> idx = 0x2d67
    >>> while exe[idx:idx+2] == b'\xc6\x84':
    ...     res += bytes([exe[idx+7]])
    ...     idx += 8
    ... 
    >>> len(res)
    191407
    

The end is still “flare”:

    
    
    >>> res[-5:]
    b'flare'
    

#### Extract Unpacked Code

Just after the buffer is loaded and a bit more setting various values, the
program allocs 0x2ed2d bytes of space on the heap, and then passes the buffer
and that buffer to another function:

[![](https://0xdfimages.gitlab.io/img/buffer-decode.png)_Click for full size
image_](https://0xdfimages.gitlab.io/img/buffer-decode.png)

I’ve tried to color-code the notes in that image to match the boxes around the
disassembly.

I can run up to 0x17972f with a breakpoint and dump the contents of buffer to
a file by finding the bytes I want in the Dump, selecting them, right
clicking, Binary -> Save to File.

The resulting file is 191,789 bytes (or 0x2ed2d).

    
    
    $ ls -l unpacked.bin 
    -rwxrwx--- 1 root vboxsf 191789 Sep 24 15:52 unpacked.bin
    $ md5sum unpacked.bin 
    552c5755912014bad17fd1db22cf78db  unpacked.bin
    

### Unpacked Code

#### Debugging

To understand what’s going on, I’m going to work on the unpacked code in
Ghidra and debug the main binary in `x64dbg`. To get into the unpacked code,
I’ll need to set a break point where it calls the buffer, here:

![image-20211001205301677](https://0xdfimages.gitlab.io/img/image-20211001205301677.png)

Then I’ll start the program, run until it opens, close it, and it hits the
break point. Then by stepping into that, I’ll be in the unpacked code.
Unfortunately, any breakpoints I set in that code won’t live between runs, as
the addresses will change, so I’ll get good at finding the next offsets to
break on to step in.

#### Load into Ghidra

On loading this, it won’t recognize the architecture, so I’ll have to tell
Ghidra it is x86-x64 little endian:

![image-20210924155614484](https://0xdfimages.gitlab.io/img/image-20210924155614484.png)

It takes a bunch of cleaning up, as the functions aren’t as easy for Ghidra to
recognize without an entry point or other metadata typically included in an
EXE. I’ll do a lot of deleting and creating functions.

#### Entry

The top of the shellcode is a call to five bytes later. This is a common
technique of going to the next instruction, but now with the address of that
instruction on top of the stack.

![image-20210924170001719](https://0xdfimages.gitlab.io/img/image-20210924170001719.png)

The next instruction is POP RCX, so RCX now holds the address five bytes into
the top of the buffer. This allows the program to reference static objects at
given offsets into this buffer without knowing where in memory it will load.

The function at 0x5 does just that, calling `FUN_00000040` with two such
references:

    
    
    void FUN_00000005(void)
    
    {
      longlong reference_point;  // from the previous call
      
      FUN_00000040(reference_point + 0xb23,0x45a75caa,reference_point + 0x2ed23,5,0);
      return;
    }
    

At 0xb28 there’s a Windows MZ executable:

![image-20210924170241978](https://0xdfimages.gitlab.io/img/image-20210924170241978.png)

0x2ed28 is just before the end of the buffer, where I saw “flare”:

![image-20210924170320068](https://0xdfimages.gitlab.io/img/image-20210924170320068.png)

#### FUN_00000040

I could just try to carve out the EXE now, but given those other variables
passed in, I’ll want to look at what’s happening.

There’s a function I’ve named `ImportFuncByHash` (at 0xa1c). This is a common
technique used throughout this binary and it’s children. In this function,
loops through the [PEB](https://docs.microsoft.com/en-
us/windows/win32/api/winternl/ns-winternl-peb) looking for loaded DLLs, and
then gets the address of the exports it needs from it (kind of like
[this](http://www.rohitab.com/discuss/topic/45310-obtain-dll-addresses-from-
the-peb-of-a-64-bit-process/)).

It loads `LdrLoadDll` and `LdrGetProcedureAddress` using this function, and
then uses those to get more:

![image-20211001205807055](https://0xdfimages.gitlab.io/img/image-20211001205807055.png)

It uses these functions to load the DLL into memory, and calls into it at
0x952 into the buffer:

![image-20211001210334263](https://0xdfimages.gitlab.io/img/image-20211001210334263.png)

### DLL #1

#### Verifying Location

By stepping into that `call rax` above, it jumps to a new section of code that
starts:

![image-20211001210619189](https://0xdfimages.gitlab.io/img/image-20211001210619189.png)

After dumping the DLL from the shellcode to disk and opening it in Ghidra, it
has one Export, `entry`, which starts:

![image-20211001210717511](https://0xdfimages.gitlab.io/img/image-20211001210717511.png)

#### DLLMain

The is the [DllMain](https://docs.microsoft.com/en-
us/windows/win32/dlls/dllmain) function for the DLL, so it takes a well known
set of parameters.

    
    
    bool entry(HINSTANCE hinstDLL,dword fwdReason,LPVOID lpReserved)
    
    {
      int res;
      
      if (fwdReason == DLL_PROCESS_ATTACH) {
        __security_init_cookie();
      }
      if ((fwdReason == DLL_PROCESS_DETACH) && (DAT_18002e330 < 1)) {
        return false;
      }
      if ((1 < fwdReason - 1) ||
         ((res = dllmain_raw(hinstDLL,fwdReason,lpReserved), res != 0 &&
          (res = dllmain_crt_dispatch(hinstDLL,fwdReason,lpReserved), res != 0)))) {
        res = LoadDLLandRun();
        if ((fwdReason == DLL_PROCESS_ATTACH) && (res == 0)) {
          LoadDLLandRun();
          dllmain_crt_dispatch(hinstDLL,0,lpReserved);
          dllmain_raw(hinstDLL,0,lpReserved);
        }
        if (((fwdReason == 0) || (fwdReason == 3)) &&
           (res = dllmain_crt_dispatch(hinstDLL,fwdReason,lpReserved), res != 0)) {
          res = dllmain_raw(hinstDLL,fwdReason,lpReserved);
        }
      }
      return (bool)(char)res;
    }
    

There are a couple functions that take the same args and do some prep, but the
interesting function starts at 0x180001000 and I’ve named `LoadDLLandRun`:

    
    
    void LoadDLLandRun(void)
    
    {
      longlong *plVar1;
      code *pcVar2;
      
      plVar1 = (longlong *)FUN_180001fd0((short *)&DAT_1800168f0,0x17a00);
      pcVar2 = (code *)FUN_1800027d0(plVar1,s_Start_1800168e0);
      (*pcVar2)();
                        /* WARNING: Subroutine does not return */
      ExitProcess(0);
    }
    

Without diving into the two functions here, I’ll look at the parameters. The
first takes a global buffer, which looking at it, is a second Windows
executable:

![image-20211002071004334](https://0xdfimages.gitlab.io/img/image-20211002071004334.png)

I can guess that 0x17a00 is a length. 0x1800168f0 + 0x17a00 = 0x18002E2F0,
which does look like a change in Ghidra:

![image-20211002071411983](https://0xdfimages.gitlab.io/img/image-20211002071411983.png)

The second function takes the output of the first and the string “Start”. Then
it calls the result of the second. Just from looking at that, I can make a
guess that the first is loading the DLL into memory, and the second is getting
the address of the `Start` function, and the third is calling that.

In the debugger, running to these functions, the return value of
`FUN_180001fd0` is an address that holds an address that points to the PE
header inside the loaded MZ:

![image-20211002112109167](https://0xdfimages.gitlab.io/img/image-20211002112109167.png)

If I take the result of the second function and right click and select “Follow
in Disassembler”, it’s a very short function:

![image-20211002140413931](https://0xdfimages.gitlab.io/img/image-20211002140413931.png)

### DLL #2

#### Verifying Location

I’ll dump the MZ from the debugger and see if I am where I think I am. Two
exports, and one is named `Start`:

![image-20211002140232893](https://0xdfimages.gitlab.io/img/image-20211002140232893.png)

Clicking on it, it matches perfectly to what I saw in the debugger:

![image-20211002140441565](https://0xdfimages.gitlab.io/img/image-20211002140441565.png)

#### Start_main

This function just calls one I named `Start_main`. That function isn’t too
long:

    
    
    void Start_main(void)
    
    {
      int flag;
      code *loaded_function;
      longlong buffer;
      undefined8 seconds;
      int flag2;
      
      DAT8af0-set();
                        /* pVirtualAlloc */
      loaded_function = (code *)load_by_hash((char *)0x0,1,0x697a6afe);
      buffer = (*loaded_function)(0,0x1e0,0x3000,4);
      FUN_180001a40(buffer,1);
      flag = FUN_180002e60(buffer);
      flag2 = 8;
      if (flag != 0) {
        flag2 = *(int *)(buffer + 0x24);
      }
      _DAT_1800178e0 = 6;
      seconds = 360000;
      if (flag2 == 0x40) {
        seconds = 300000;
      }
                        /* sleep */
      loaded_function = (code *)load_by_hash((char *)0x0,1,0x5cbd6d9e);
      (*loaded_function)(seconds);
      FUN_180001a40(buffer,flag2);
      return;
    }
    

Throughout this binary, it uses a function I named `load_by_hash`, where it
gets the address of a Windows API function by some hash value. I didn’t spend
a bunch of time looking at it, but rather stepped over it and saw RAX
contained a pointer to a function (which x64dbg is nice enough to label). I
did google a few of the values passed as parameter three and noticed they were
in [this script](https://github.com/pan-
unit42/public_tools/blob/master/teslacrypt/deobfuscate_api_calls.py) for
deobfuscating the same kind of functions from the TeslaCrypt ransomware, so
they likely use the same algorithm.

#### Avoiding Sleep

Before calling the last function in this function, it loads and calls `sleep`.
It looks like it could be for either 300000 or 360000, but I never saw it have
any argument besides 360000, which is 360 seconds or 6 minutes. I found that
`call rax` at an address ending in 0x1a1e and replaced it with two nops to
just skip over it.

![image-20211002151415711](https://0xdfimages.gitlab.io/img/image-20211002151415711.png)

#### Filename

When debugging, I noticed I was always dying in `FUN_180001a40`, and that it
was always passing in 8 as a second parameter. In that function, there’s this
(where I named the second parameter `flag`):

    
    
        if (flag == 8) {
                        /* FatalExit */
          loadedFunction = (code *)load_by_hash((char *)0x0,1,0x95902b19);
          (*loadedFunction)();
        }
    

That explains the exit. That flag is set based on the result of
`FUN_180002e60`, which is passed the output of `FUN_180001a40`. With
debugging, I can see that buffer looks like:

![image-20211002142229365](https://0xdfimages.gitlab.io/img/image-20211002142229365.png)

It’s got the date in a wide ASCII string, some other stuff, and at offset 0x28
the full path to the current running binary.

That buffer is passed to `FUN_180002e60`:

    
    
    int FUN_180002e60(longlong param_1)
    
    {
      byte bVar1;
      byte bVar2;
      int exe_name_len;
      char *exe_name;
      code *strnlen;
      ulonglong i;
      ulonglong j;
      undefined auStack344 [32];
      undefined local_138;
      uint required_filename [3];
      byte local_128 [272];
      ulonglong local_18;
      
      local_18 = DAT_180017000 ^ (ulonglong)auStack344;
      exe_name = strrchr((char *)(param_1 + 0x28),L'\\');
      strncpy_s((char *)local_128,0x104,exe_name + 1,0x105);
      strnlen = (code *)load_by_hash((char *)0x0,1,0x2d40b8e6);
      exe_name_len = (*strnlen)();
      local_138 = 0;
      i = 0;
      required_filename[0] = 0x80ed0aa;
      required_filename[1] = 0x3c2e8e95;
      required_filename[2] = 0x646ba0bc;
      j = i;
      do {
        required_filename[j] = required_filename[j] ^ 0x646ba0f9;
        j = j + 1;
      } while (j < 3);
      if (exe_name_len != 0) {
        do {
          bVar1 = local_128[i];
          bVar2 = *(byte *)((longlong)required_filename + i);
          if ((bVar1 < bVar2) || (bVar1 >= bVar2 && bVar1 != bVar2)) break;
          i = i + 1;
        } while (i < (ulonglong)(longlong)exe_name_len);
      }
      exe_name_len = stackcheck?(local_18 ^ (ulonglong)auStack344);
      return exe_name_len;
    }
    

It takes the buffer + 0x28 and passes it to `strrchr` with `\` to get the rest
of the string after the last `\`, which is just the executable name and
extension.

Then there’s a loop that loads some static bytes and XORs each word to get the
required filename. Then it compares each by with the EXE name for the running
exe. Running to just after this loop (where it checks if the `exe_name_len` is
not null), I can see the result by dropping that address in the dump:

![image-20211002142937115](https://0xdfimages.gitlab.io/img/image-20211002142937115.png)

My file is named `spel.exe`, but it’s checking it against `Spell.EXE`. The
return values in Ghidra’s decomplication aren’t quite right. But it seems to
return 0 if the match isn’t right, and 1 if it does match.

That causes `flag2` to be set to 0x24 bytes into the buffer, which was always
2 in my debugging.

#### FUN_180001a40

This function has an `if` / `else` that basically does three things based on
the input of `flag`. If it’s 8 it just exits (as I noted above). If it’s one,
it does some stuff (including another decoding of a stack string like
`Spell.EXE` above), but I’ll ignore this for now, since I’m always passing 2.
That code starts:

    
    
      else {
        if (flag == 2) {
                        /* VirtualAlloc */
          loadedFunction = (code *)load_by_hash((char *)0x0,1,0x697a6afe);
          new_buffer = (*loadedFunction)(0,0x20,0x3000,PAGE_READWRITE);
          *(undefined8 *)(buffer + 0x188) = new_buffer;
          zero = 0;
          local_88 = 0;
          decoded1[0] = 0x24745716;
          decoded1[1] = 0x387a1615;
          decoded1[2] = 0x3b7a585e;
          decoded1[3] = 0x56153b70;
          i = zero;
          do {
            decoded1[i] = decoded1[i] ^ 0x56153b70;
            i = i + 1;
          } while (i < 4);
            /* flare-on.com */
          flareoncom_string = *(undefined **)(buffer + 0x188);
          j = 0xd;
          if (flareoncom_string != (undefined *)0x0) {
            lVar4 = (longlong)decoded1 - (longlong)flareoncom_string;
            do {
              *flareoncom_string = flareoncom_string[lVar4];
              flareoncom_string = flareoncom_string + 1;
              j = j + -1;
            } while (j != 0);
          }
    

It sneakily loaded `VirtualAlloc` and creates a 0x20 byte buffer, and puts the
address 0x188 bytes into the buffer with the date and filename.

The it decodes the string `flare-on.com`, which smells like the end of a flag
potentially? That is copied into the new 0x20 byte buffer.

The section of code continues:

    
    
          j = init_c2(buffer);
          if ((char)j != '\0') {
            puVar5 = (undefined8 *)&xored_buf;
            lVar4 = *(longlong *)(buffer + 0x188);
            xored_buf = 0x15891d8a;
            uStack68 = 0x1dc19f14;
            uStack64 = 0x1b8a7e99;
            uStack60 = 0;
            local_38 = ZEXT816(0);
            i = zero;
            while( true ) {
              twelve = zero;
              if (*(char **)(buffer + 0x188) != (char *)0x0) {
                twelve = strnlen(*(char **)(buffer + 0x188),0x20);
              }
              if (twelve < (ulonglong)(longlong)(int)i) break;
              i = (ulonglong)((int)i + 1);
              *(byte *)puVar5 =
                   *(byte *)puVar5 ^ *(byte *)((lVar4 - (longlong)&xored_buf) + (longlong)puVar5);
              puVar5 = (undefined8 *)((longlong)puVar5 + 1);
            }
            local_90 = 0;
            hex31 = 0x31;
                        /* strlen */
            loadedFunction = (code *)load_by_hash((char *)0x0,1,0x2d40b8e6);
            j = (*loadedFunction)(&xored_buf);
            set_regkey(buffer,(undefined8 *)&xored_buf,j + 1,&hex31);
            cVar1 = decrypt_flag_sortof(buffer,*(longlong *)(buffer + 0x18) + 0x5f);
            if (cVar1 == '\0') {
              loadedFunction = (code *)load_by_hash((char *)0x0,1,0x95902b19);
              (*loadedFunction)();
            }
            descramble_flag?(buffer);
          }
          goto LAB_180001e38;
    

There’s a call to what I named `init_c2`. More to come on that later. The
important part here is that putting the right thing into C2 will return 1,
which allows it to enter that big stretch.

I skipped through the next bit, down to where it calls `set_regkey`. This
actually creates the reg key `HKCU:\SOFTWARE\Microsoft\Spell` if it doesn’t
exist.

I’ll come back to `decrypt_flag_sortof` and `descramble_flag?` as well.

#### C2

The `init_c2` function (at 0x1f80) calls `WSAStartup` and then calls a
function I named `c2` (at 0x2070). This function creates a TCP socket (with
`socket`) and then builds the string `inactive.flare-on.com`:

    
    
        format_string_sdots[0] = 0x38b2f282;
        format_string_sdots[1] = 0x1d9c81d4;
        j = 0;
        i = j;
        do {
          format_string_sdots[i] = format_string_sdots[i] ^ 0x1d9c81a7;
          i = i + 1;
        } while (i < 2);
        sprintf(inactive,format_string_sdots,(longlong)&param_1[0x25].y + 1,param_1[0x31])
    

Next it resolves and connects to that domain on TCP 888:

    
    
                        /* gethostbyname */
        loaded_function = (code *)load_by_hash((char *)0x0,4,0xf44318c6);
        hostent = (hostent *)(*loaded_function)();
        if (hostent != (hostent *)0x0) {
          getiplist(ip,(undefined8 *)*hostent->h_addr_list,(longlong)hostent->h_length);
                        /* htons */
          loaded_function = (code *)load_by_hash((char *)0x0,4,0x8e9bf775);
          port_network = (*loaded_function)();
                        /* connect */
          loaded_function = (code *)load_by_hash((char *)0x0,4,0xedd8fe8a);
          res = (*loaded_function)(sockd,&local_80,0x10);
    

I’ll add the domain to `C:\windows\system32\drivers\etc\hosts` to resolve to
127.0.0.1 so it connects to me. I’ll also start `nc.exe` listening on 888.

If it connects, it sends a `@`:

    
    
            local_c8 = 0;
            local_c4 = L'@';
                        /* lstrlen */
            loaded_function = (code *)load_by_hash((char *)0x0,1,0x2d40b8e6);
            len_str = (*loaded_function)();
            local_c0 = 0;
            local_bc = L'@';
                        /* send */
            loaded_function = (code *)load_by_hash((char *)0x0,4,0xe797764);
            res = (*loaded_function)(sockd,&local_bc,len_str,0);
    

Which then arrives at `nc`:

    
    
    PS > nc -lnvp 888
    Ncat: Version 7.31 ( https://nmap.org/ncat )
    Ncat: Listening on :::888
    Ncat: Listening on 0.0.0.0:888
    Ncat: Connection from 127.0.0.1.
    Ncat: Connection from 127.0.0.1:1025.
    @
    

It `recv` up to 0x20 bytes into a buffer, and there are three loops decoding
stack strings and comparing it. I didn’t dive too deep into `run` and `exe`,
but the third is `flare-on.com`, which causes it to return the right values
such that 1 is returned into the function above, which is what I needed.

#### Decrypt String

With the non-zero return values from `init_c2` it continues. The reg key is
created if it doesn’t exist, and execution reaches `decrypt_flag_sortof`.

Debugging shows this is passed two arguments:

  * The buffer with the date and filename (that has also been a scratch pad for the application to store locations) and the `flare-on.com` string.
  * The address that is 0x5f bytes into the “PNG” resource:

![image-20211003062335601](https://0xdfimages.gitlab.io/img/image-20211003062335601.png)

With a handful of stack string decodes (just like above), and loading
functions by hash, the function effective makes the following calls to the
BCrypt provider calls:

  * `BCryptoOpenAlgorithmProvider(&phAlgorithm, "AES", 0, 0)`
  * `BCryptGetProperty(phAlgorithm, len(hObject), outbuf, size out=4, place to write size out, out_buf, flags)`
  * `BCryptoSetProperty(phAlgorithm, "ChainingMode", W"ChaningModeCBC", out_buf, len(out_buf), flags)`
  * `BCryptGenerateSymmetricKey(phAlgorithm, &phkey, key_buffer, len(key_buffer), secret = "d41d8cd98f00b204e9800998ecf8427e", len(secret))`
  * `BCryptDecrypt(phkey, inPNG_buf, len(inPNG_buf) = 0x20, null, iv = 16*0x80, len(iv) = 16, outbuffer, len(outbuffer) = 0x20, outlenres, flags)`
  * `BCryptCloseAlgorithmProvider(phAlgorithm, 0)`
  * `BCryptDestroyKey(phkey)`

The resulting decrypted buffer is disappointingly not the flag, but it is
written into the scratchpad buffer at an offset of 0x1a8:

![image-20211003063633133](https://0xdfimages.gitlab.io/img/image-20211003063633133.png)

But it does return 1, which allows the calling code to avoid a call to
`FatalExit`.

#### Descramble Flag?

The last function called is what I named `descramble_flag?`, which:

  * Sets a bunch of static stack values;
  * Loops over a a switch statement 0x17 times, with each case doing some XORing of one of the values from the decrypted buffer above.

![image-20211003064550253](https://0xdfimages.gitlab.io/img/image-20211003064550253.png)

  * The resulting buffer is passed to the `set_regkey` function which actually writes the value this time:

![image-20211003064655401](https://0xdfimages.gitlab.io/img/image-20211003064655401.png)

I wasn’t a fan of this part of the challenge. To get the flag, you have to
notice the order in which the bytes are being called up to be shuffled / xored
in the switch statement. If you look at it in x64dbg, it will jump out
eventually:

[![image-20211001204954426](https://0xdfimages.gitlab.io/img/image-20211001204954426.png)_Click
for full size
image_](https://0xdfimages.gitlab.io/img/image-20211001204954426.png)

**Flag: b3s7_sp3llcheck3r_ev3r@flare-on.com**

[](/flare-on-2021/spel)

