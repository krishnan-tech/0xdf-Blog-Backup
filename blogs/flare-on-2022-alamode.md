# Flare-On 2022: à la mode

[flare-on](/tags#flare-on ) [ctf](/tags#ctf ) [flare-on-a-la-
mode](/tags#flare-on-a-la-mode ) [reverse-engineering](/tags#reverse-
engineering ) [youtube](/tags#youtube ) [dotnet](/tags#dotnet )
[dll](/tags#dll ) [dnspy](/tags#dnspy ) [polyglot](/tags#polyglot )
[ghidra](/tags#ghidra ) [ida](/tags#ida ) [x32dbg](/tags#x32dbg )
[rc4](/tags#rc4 ) [cyberchef](/tags#cyberchef ) [peb](/tags#peb )
[tib](/tags#tib )  
  
Nov 11, 2022

  * [[1] Flaredle](/flare-on-2022/flaredle)
  * [[2] Pixel Poker](/flare-on-2022/pixel_poker)
  * [[3] Magic 8 Ball](/flare-on-2022/magic_8_ball)
  * [[4] darn_mice](/flare-on-2022/darn_mice)
  * [[5] T8](/flare-on-2022/t8)
  * [6] à la mode
  * [[7] anode](/flare-on-2022/anode)
  * [[8] backdoor](/flare-on-2022/backdoor)
  * [[9] encryptor](/flare-on-2022/encryptor)
  * [[10] Nur geträumt](/flare-on-2022/nur_getraumt)
  * [[11] The challenge that shall not be named](/flare-on-2022/challenge_that_shall_not_be_named)

![a la mode](https://0xdfimages.gitlab.io/img/flare2022-alamode-cover.png)

à la mode is a polyglot file, part .NET binary, part standard binary. The .NET
part of the file shows a named pipe client that gets the flag over a
connection. The standard binary loads functions dynamically by getting
kernelbase.dll’s address from the process environment block, and getting
offsets by deobfuscated string function names. Then it uses those functions to
stand up a named pipe server. I’ll get the flag dynamically, and then go to
show how it is using RC4, and decrypt it.

## Challenge

> FLARE FACT #824: Disregard flare fact #823 if you are a .NET Reverser too.
>
> We will now reward your fantastic effort with a small binary challenge.
> You’ve earned it kid!

The download contains a 32-bit Windows .NET library file:

    
    
    oxdf@hacky$ file HowDoesThisWork.dll 
    HowDoesThisWork.dll: PE32 executable (DLL) (GUI) Intel 80386 Mono/.Net assembly, for MS Windows
    

There’s also a text file, `IR chat log.txt`:

> [FLARE Team] Hey IR Team, it looks like this sample has some other binary
> that might interact with it, do you have any other files that might be of
> help.
>
> [IR Team] Nope, sorry this is all we got from the client, let us know what
> you got.

## Video Solution

I’ve solved this one in a YouTube
[video](https://www.youtube.com/watch?v=QfbFKD7ebQM) as well as a written
solution:

## Run It

As a DLL, this binary doesn’t run on it’s own. It’s meant to offer functions
that can be imported into an EXE.

`rundll32.exe` is a program that’s designed to test DLLs by calling their
functions directly. It takes a dll, then comma, then a function name or
[ordinal
number](https://knowledge.ni.com/KnowledgeArticleDetails?id=kA00Z000000kHBmSAM).
I’ll try a couple, but each time a pop-up flashes on the screen for a fraction
of a second and then disappears:

![image-20221005204528695](https://0xdfimages.gitlab.io/img/image-20221005204528695.png)

## RE

### .NET

Given this is (at least claiming to be) a .NET binary, I’ll open it in DNSpy.

[![image-20221006125044580](https://0xdfimages.gitlab.io/img/image-20221006125044580.png)_Click
for full size
image_](https://0xdfimages.gitlab.io/img/image-20221006125044580.png)

There’s not much there besides two functions in the `Flag` namespace, `Flag()`
and `GetFlag(string)`.

`Flag()` is empty:

[![image-20221006125109855](https://0xdfimages.gitlab.io/img/image-20221006125109855.png)_Click
for full size
image_](https://0xdfimages.gitlab.io/img/image-20221006125109855.png)

`GetFlag(string)` is more interesting:

[![image-20221006125138185](https://0xdfimages.gitlab.io/img/image-20221006125138185.png)_Click
for full size
image_](https://0xdfimages.gitlab.io/img/image-20221006125138185.png)

This function takes a password, then connects to a named pipe named `FlareOn`.
It writes the password into the pipe, and then reads up to 64 bytes, converts
those to characters, and returns the string.

With the hints about parts missing, I suspect somewhere else in this binary
that it’s going to create that named pipe and listen for a password, and
return the flag.

### Dll Load Thread

#### Loading for Analysis

Given that there must be more to the binary, I’ll take a look in Ghidra. The
file exports two functions:

![image-20221006125800158](https://0xdfimages.gitlab.io/img/image-20221006125800158.png)

IDA gives the choice to open as .NET (which is the default) or a regular exe.
If you open as .NET, it will show the same two functions as above. Under exe,
it’s better, but it still doesn’t recognize DllMain as a function, let alone
an export:

![image-20221006131049442](https://0xdfimages.gitlab.io/img/image-20221006131049442.png)

I’m very rusty at Ida (prefer Ghidra now by a long shot comparing free
versions), so perhaps there’s a way to configure so that this doesn’t happen.

#### entry

The `entry` function is quite simple:

    
    
    void entry(void)
    
    {
                        /* WARNING: Could not recover jumptable at 0x1000d16c. Too many branches */
                        /* WARNING: Treating indirect jump as call */
      _CorDllMain();
      return;
    }
    

`_CorDllMain()` doesn’t exist at this point:

![image-20221006131247692](https://0xdfimages.gitlab.io/img/image-20221006131247692.png)

#### DllMain

This is a [standard Microsoft function](https://learn.microsoft.com/en-
us/windows/win32/dlls/dllmain) for Dlls, and it typically does what’s in the
linked example, doing different actions based on the `fdwReason`, the reason
this is invoked. In this case, it just calls `dllmain_dispatch` with all three
parameters:

    
    
    BOOL __DllMainCRTStartup@12(HINSTANCE__ *hinstDLL,DWORD fdwReason,LPVOID lpvReserved)
    
    {
      int iVar1;
      
      if (fdwReason == 1) {
        ___security_init_cookie();
      }
      iVar1 = dllmain_dispatch(hinstDLL,fdwReason,lpvReserved);
      return iVar1;
    }
    

`dllmain_dispatch` does the same kind of thing, with some branching based on
the second parameter:

    
    
    int __cdecl dllmain_dispatch(HINSTANCE__ *hinstDLL,unsigned_long fdwReason,void *lpvReserved)
    
    {
      int res;
      undefined4 *in_FS_OFFSET;
      undefined4 local_14;
      
      if ((fdwReason == DLL_PROCESS_DETACH) && (DAT_10015a90 < 1)) {
        res = 0;
      }
      else if (((fdwReason != DLL_PROCESS_ATTACH) && (fdwReason != DLL_THREAD_ATTACH)) ||
              ((res = dllmain_raw(hinstDLL,fdwReason,lpvReserved), res != 0 &&
               (res = dllmain_crt_dispatch(hinstDLL,fdwReason,lpvReserved), res != 0)))) {
        res = FUN_10001163(hinstDLL,fdwReason);
        if ((fdwReason == DLL_PROCESS_ATTACH) && (res == 0)) {
          FUN_10001163(hinstDLL,0);
          dllmain_crt_process_detach(lpvReserved != (void *)0x0);
          dllmain_raw(hinstDLL,0,lpvReserved);
        }
        if (((fdwReason == DLL_PROCESS_DETACH) || (fdwReason == DLL_THREAD_DETACH)) &&
           (res = dllmain_crt_dispatch(hinstDLL,fdwReason,lpvReserved), res != 0)) {
          res = dllmain_raw(hinstDLL,fdwReason,lpvReserved);
        }
      }
      *in_FS_OFFSET = local_14;
      return res;
    }
    

My quick review of this show that it either calls `FUN_10001163` or it
doesn’t. It looks like it does call it on `DLL_PROCESS_ATTACH`.

### Initialization

#### FUN_10001163

The function at 0x10001163 is very short:

    
    
    undefined4 FUN_10001163(undefined4 param_1,int param_2)
    
    {
      if (param_2 == 1) {
        FUN_100012f1();
        (*DAT_10015a30)(0,0,FUN_10001094,0,0,0);
      }
      return 1;
    }
    

It only seems to do anything in the first call above, not the second, but I’ll
continue to see what it’s doing. If `param2` is one, it calls two functions.
The first is at 0x100012f1. The second is a global variable that must be
initialized elsewhere.

#### FUN_100012f1

This function has three parts. First, it sets a couple globals:

    
    
      _DAT_10015a18 = FUN_10001426;
      DAT_10015a1c = &LAB_10001451;
      DAT_10015a20 = &LAB_10001493;
    

`FUN_10001426` is basically a safe call to `memset`, verifying that the target
buffer exists. The other two show up as not functions, but they are, as
doubleclicking shows:

[![image-20221006134125419](https://0xdfimages.gitlab.io/img/image-20221006134125419.png)_Click
for full size
image_](https://0xdfimages.gitlab.io/img/image-20221006134125419.png)

I’ll right click in the Listing view and create a function for each.

Next, it calls `FUN_100012db`, and saves a result that will be used throughout
the third part:

    
    
    iVar1 = FUN_100012db();
    

Finally, there’s 11 pairs of function calls, first passing in two globals into
`FUN_100014ae` to get a result, and then passing that along with the result
from `FUN_100012db` into `FUN_1000125c` and storing that result in another
global. For example, the first one is:

    
    
    iVar2 = FUN_100014ae(&DAT_10015060,(int)&DAT_10015a50);
    DAT_10015a24 = FUN_1000125c(iVar1,iVar2);
    

## Debug

### Background

A this point, I’ll switch to debugging. I’ll still work along in Ghidra, but
using x32dbg to understand and validate what’s happening.

At first I thought I would have to debug `rundll32.exe`, and set the command
line to load this DLL, but I learned that x32dbg (and presumably x64dbg) has a
feature where if you tell it to run a DLL, it will create a copy of a file
`DLLLoader32_????.exe` in the same directory, and run that which loads the
given file. Once execution completes, that EXE file is removed.

### Initialization

#### Get kernelbase.dll Address

Curious to pick up where I left off, I’ll put a break point at 0x100012f1, the
start of the function with three parts discussed above. The first part is just
setting globals.

If I just step over `FUN_100012db`, I’ll notice that it returns 766c000. This
looks like a memory address, and in the Memory Map tab, I’ll see it’s the
address at which `kernelbase.dll` is loaded:

[![image-20221006135123852](https://0xdfimages.gitlab.io/img/image-20221006135123852.png)_Click
for full size
image_](https://0xdfimages.gitlab.io/img/image-20221006135123852.png)

Looking at the function, it loads `fs:[0x30]` into EAX, which is the address
of the Process Environment Block (PEB) in the [Thread Information Block
(TIB)](https://en.wikipedia.org/wiki/Win32_Thread_Information_Block#Accessing_the_TIB).

![image-20221006071030449](https://0xdfimages.gitlab.io/img/image-20221006071030449.png)

Next it goes 0xc bytes into that, [which
contains](https://www.aldeid.com/wiki/PEB-Process-Environment-Block) the
address of the `PEB_LDR_DATA`. 0x14 bytes into that is the
`InMemoryOrderModuleList`, a linked list of all the loaded Dlls in the current
process, in memory placement order. The next few lines are walking the list,
getting the pointer at the top of the structure and moving to the next entry.
Once it settles on one, it jumps 0x10 bytes in, which is the address of the
module as it’s loaded. Along the way it visits the `LIST_ENTRY` block for
`ntdll.dll` and `kernel32.dll`, before returning the address of
`kernelbase.dll`.

#### Load Function Addresses

Now it comes to these pairs of calls. The first takes two globals. Stepping
over one, I’ll see it returns a string describing a function name:

[![image-20221006140047774](https://0xdfimages.gitlab.io/img/image-20221006140047774.png)_Click
for full size
image_](https://0xdfimages.gitlab.io/img/image-20221006140047774.png)

I’ll note that the second parameter starts as a clean null buffer, and gets
updated to the result of the call. It seems that the binary is decoding based
on the previous string. The decode function it self confirms:

    
    
    int __cdecl decode_string(byte *param_1,int param_2)
    
    {
      byte bVar1;
      int i;
      int iVar2;
      
      i = 0;
      bVar1 = *param_1;
      if (bVar1 != 0) {
        iVar2 = param_2 - (int)param_1;
        do {
          i = i + 1;
          param_1[iVar2] = bVar1 ^ 0x17;
          param_1 = param_1 + 1;
          bVar1 = *param_1;
        } while (bVar1 != 0);
      }
      *(undefined *)(i + param_2) = 0;
      return param_2;
    }
    

I’m not sure that decompile is 100% on, but I get enough of the gist to get
the debugging.

The second function takes in this address of `kernelbase.dll` and the function
name, and it returns an address, which is saved in the global variable.
Sometimes it fails and returns null. I didn’t figure out why.

The `load_function_addresses` function looks like this:

    
    
    void load_function_addresses(void)
    
    {
      int kernelbase_addr;
      int decoded_name;
      
      _safe_memset = safe_memset;
      FUN_1451addr = FUN_10001451;
      FUN_1493addr = FUN_10001493;
      kernelbase_addr = get_kernelbase_addr();
      decoded_name = decode_string(&CloseHandle_enc,(int)&string_decode_buffer);
      CloseHandle_addr = get_function_address(kernelbase_addr,decoded_name);
      decoded_name = decode_string((byte *)ConnectNamedPipe_enc,(int)&string_decode_buffer);
      ConnectNamedPipe_addr = get_function_address(kernelbase_addr,decoded_name);
      decoded_name = decode_string((byte *)CreateNamedPipe_enc,(int)&string_decode_buffer);
      CreateNamedPipeA = get_function_address(kernelbase_addr,decoded_name);
      decoded_name = decode_string(&CreateThread_enc,(int)&string_decode_buffer);
      CreateThread_addr = get_function_address(kernelbase_addr,decoded_name);
      decoded_name = decode_string((byte *)DisconnectNamedPipe_enc,(int)&string_decode_buffer);
      DisconnectNamedPipe_addr = get_function_address(kernelbase_addr,decoded_name);
      decoded_name = decode_string(&FlushFileBuffers_enc,(int)&string_decode_buffer);
      FlushFileBuffers = get_function_address(kernelbase_addr,decoded_name);
      decoded_name = decode_string((byte *)GetLastError_enc,(int)&string_decode_buffer);
      GetLastError_addr = get_function_address(kernelbase_addr,decoded_name);
      decoded_name = decode_string((byte *)GetProcessHeap_enc,(int)&string_decode_buffer);
      GetProcessHeap_addr = get_function_address(kernelbase_addr,decoded_name);
      decoded_name = decode_string((byte *)lstrcmpA_enc,(int)&string_decode_buffer);
      lstrcmpA_addr = get_function_address(kernelbase_addr,decoded_name);
      decoded_name = decode_string((byte *)ReadFile_enc,(int)&string_decode_buffer);
      ReadFile_addr = get_function_address(kernelbase_addr,decoded_name);
      decoded_name = decode_string((byte *)WriteFile_enc,(int)&string_decode_buffer);
      WriteFile_addr = get_function_address(kernelbase_addr,decoded_name);
      return;
    }
    

Now the parent function shows what it’s doing as well:

    
    
    undefined4 FUN_10001163(undefined4 param_1,int param_2)
    
    {
      if (param_2 == 1) {
        load_function_addresses();
        (*CreateThread_addr)(0,0,FUN_10001094,0,0,0);
      }
      return 1;
    }
    

It’s going to create a thread with `FUN_10001094`.

### Thread

#### Named Pipe Server

I don’t have a natural way to reach this code, so I’ll start looking at it
statically.

`FUN_10001094` looks a lot like it pairs with the .NET code from before.
First, it creates a named pipe:

    
    
      _memset(password,0,0x40);
      (*GetProcessHeap_addr)();
                        /* SecureityAttributes - Null */
      uVar7 = 0;
                        /* nDefaultTimeout - 0 == 50 ms */
      uVar6 = 0;
                        /* nInBufferSize */
      uVar5 = 0x40;
                        /* nOutBufferSize */
      uVar4 = 0x40;
                        /* nMaxInstances */
      uVar3 = 255;
                        /* PIPE_TYPE_MESSAGE|PIPE_READMODE_MESSAGE */
      uVar2 = 6;
      uVar1 = PIPE_ACCESS_DUPLEX;
      res = decode_string((byte *)\\\\.\\pipe\\FlareOn_enc,(int)&DAT_100159d8);
      hPipe = (HANDLE)(*CreateNamedPipeA)(res,uVar1,uVar2,uVar3,uVar4,uVar5,uVar6,uVar7);
    

It first creates a named pipe, passing a name that is encoded using the same
technique as with the function names. To decrypt this, I’ll run to a call of
`decode_string` (say, 0x10001323), and edit the stack to pass in the globals
here instead of the ones used naturally.

I’ll do this by right clicking on the parameter in the Stack view, Binary >
Edit. There I can update the hex:

[![image-20221006142155331](https://0xdfimages.gitlab.io/img/image-20221006142155331.png)_Click
for full size
image_](https://0xdfimages.gitlab.io/img/image-20221006142155331.png)

[![image-20221006142228944](https://0xdfimages.gitlab.io/img/image-20221006142228944.png)_Click
for full size
image_](https://0xdfimages.gitlab.io/img/image-20221006142228944.png)

This will fail if the second parameter buffer is supposed to have been used
elsewhere first, but it works. On stepping over the call, the new string is in
EAX:

![image-20221006142252847](https://0xdfimages.gitlab.io/img/image-20221006142252847.png)

Assuming that worked, it connects to the pipe, reads the password from it, and
then flushes the buffer. It makes sure the read bytes are null terminated, and
passes it to `FUN_10001000`, along with a buffer to store the result:

    
    
      if (hPipe != (HANDLE)0xffffffff) {
        res = (*ConnectNamedPipe_addr)(hPipe,0);
        if (res == 0) {
          (*GetLastError_addr)();
        }
        res = (*ReadFile_addr)(hPipe,password,0x40,&bytesRead,0);
        if ((res == 0) || (bytesRead == 0)) {
          (*GetLastError_addr)();
        }
        else {
          (*FlushFileBuffers)(hPipe);
          password[bytesRead] = 0;
          FUN_10001000(password,&local_c);
          (*WriteFile_addr)(hPipe,password,local_c,local_10,0);
        }
        (*FlushFileBuffers)(hPipe);
        (*DisconnectNamedPipe_addr)(hPipe);
        (*CloseHandle_addr)(hPipe);
      }
      return 0;
    }
    

Then it writes back into the pipe, and closes things out.

#### Process Password

In this function at 0x10001000, it takes the password and compares it to
something generated by a couple functions. It actually turns out this is RC4,
just like the previous challenge. I’ll look at that more at the end, but I
didn’t need to now that.

    
    
    bool __cdecl FUN_10001000(undefined4 password,undefined4 *result_code)
    
    {
      int res;
      undefined *puVar1;
      uint S [258];
      
      RC4_KSA(S,(int)&DAT_10015000,8);
      RC4_PRGA(S,(int)&decrypted_password,9);
      res = (*lstrcmpA_addr)(&decrypted_password,password);
      if (res == 0) {
        puVar1 = &flag;
        RC4_PRGA(S,(int)&flag,0x1f);
        *result_code = 0x1f;
      }
      else {
        *result_code = 0x15;
        puVar1 = (undefined *)decode_string(&DAT_10015034,(int)&DAT_100159d8);
      }
      (*FUN_1493addr)(password,puVar1);
      return res == 0;
    }
    

The function runs a couple functions, and then compares a string to the input
password. If the result is 0 (the strings are the same), then it decrypts
something else.

### Get Flag

#### Get Password

I want to see what is decrypted if the strings match, but I still have the
issue of not being able to reach this code. I’ll remove the break points and
run to `entry`. There I’ll change EIP to 0x10001000. Stepping forward to
0x10001039 where it does the `lstrcmpA` call, the second argument is garbage
(because I didn’t get here right, where it should be the user sent password),
but the decrypted password looks good, “MyV0ic3!”:

[![image-20221006143938150](https://0xdfimages.gitlab.io/img/image-20221006143938150.png)_Click
for full size
image_](https://0xdfimages.gitlab.io/img/image-20221006143938150.png)

Trying to step through the compare throws an error.

#### Get Flag

I’ll reset, and do the same thing, getting to the start of 0x10001000. Before
stepping, I’ll select the call to `lstrcmp` and change it to `xor eax, eax`,
effectively making EAX 0 instead of doing the compare:

[![image-20221006144145450](https://0xdfimages.gitlab.io/img/image-20221006144145450.png)_Click
for full size
image_](https://0xdfimages.gitlab.io/img/image-20221006144145450.png)

Stepping down to 0x10001074 where it calls the RC4 decrypt again, this time
it’s passing in the buffer at 0x10015008. After stepping over, I can see the
flag in either the dump or in the preview by ESI:

[![image-20221006144423907](https://0xdfimages.gitlab.io/img/image-20221006144423907.png)_Click
for full size
image_](https://0xdfimages.gitlab.io/img/image-20221006144423907.png)

**Flag: M1x3d_M0dE_4_l1f3@flare-on.com**

## Beyond Flag - RC4

### Decrypt Password

To confirm this is RC4, I’ll run to 0x10001019, where it calls the KSA
function, and look at the parameters:

[![image-20221006145300421](https://0xdfimages.gitlab.io/img/image-20221006145300421.png)_Click
for full size
image_](https://0xdfimages.gitlab.io/img/image-20221006145300421.png)

It wants 8 bytes from 10015000.

Stepping forward to 0x1000102d where it calls RC4 decrypt, this time it wants
9 bytes from 0x10015028:

[![image-20221006145412172](https://0xdfimages.gitlab.io/img/image-20221006145412172.png)_Click
for full size
image_](https://0xdfimages.gitlab.io/img/image-20221006145412172.png)

Dropping all this into CyberChef yields the decrpyted password:

![image-20221006145444323](https://0xdfimages.gitlab.io/img/image-20221006145444323.png)

### Decrypt Flag

To get the flag, I’ll run to the next call to use the RC4 at 0x10001074. It
wants 0x1f bytes from 0x10015008:

[![image-20221006145705312](https://0xdfimages.gitlab.io/img/image-20221006145705312.png)_Click
for full size
image_](https://0xdfimages.gitlab.io/img/image-20221006145705312.png)

I can’t just replace the previous input with this, or it won’t work:

[![image-20221006145843431](https://0xdfimages.gitlab.io/img/image-20221006145843431.png)_Click
for full size
image_](https://0xdfimages.gitlab.io/img/image-20221006145843431.png)

The state of the stream hasn’t been reset, so at this point I need to add it
to the end of the previous decrypt:

[![image-20221006145903336](https://0xdfimages.gitlab.io/img/image-20221006145903336.png)_Click
for full size
image_](https://0xdfimages.gitlab.io/img/image-20221006145903336.png)

[](/flare-on-2022/alamode)

