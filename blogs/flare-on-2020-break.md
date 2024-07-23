# Flare-On 2020: break

[flare-on](/tags#flare-on ) [ctf](/tags#ctf ) [flare-on-break](/tags#flare-on-
break ) [reverse-engineering](/tags#reverse-engineering )
[ghidra](/tags#ghidra ) [ptrace](/tags#ptrace ) [hook](/tags#hook )
[ldpreload](/tags#ldpreload ) [pre-main](/tags#pre-main ) [gdb](/tags#gdb )
[crypto](/tags#crypto ) [feistel-cipher](/tags#feistel-cipher )
[unpack](/tags#unpack ) [modinv](/tags#modinv ) [python](/tags#python ) [htb-
mischief](/tags#htb-mischief ) [htb-obscurity](/tags#htb-obscurity ) [htb-
teacher](/tags#htb-teacher ) [htb-popcorn](/tags#htb-popcorn ) [htb-
lightweight](/tags#htb-lightweight ) [htb-sunday](/tags#htb-sunday )  
  
Nov 2, 2020

  * [[1] Fidler](/flare-on-2020/fidler)
  * [[2] garbage](/flare-on-2020/garbage)
  * [[3] wednesday](/flare-on-2020/wednesday)
  * [[4] report.xls](/flare-on-2020/report)
  * [[5] TKApp](/flare-on-2020/tkapp)
  * [[6] CodeIt](/flare-on-2020/codeit)
  * [[7] RE Crowd](/flare-on-2020/recrowd)
  * [[8] Aardvark](/flare-on-2020/aardvark)
  * [[9] crackinstaller](/flare-on-2020/crackinstaller)
  * [10] break

![break](https://0xdfimages.gitlab.io/img/flare2020-break-cover.png)

break was an amazing challenge. Just looking at main, it looks like a simple
comparison against a static flag. But there’s an init function that runs
first, forking a child process that then attaches a debugger to the parent,
hooking all of it’s system calls and crashes. The child itself forks a second
child, which attaches to the first child, handling several intentional crash
points in the first child’s code. The effectively prevents my debugging the
parent for first child, as only one debugger can attach at a time. I’ll use
two different approaches - hooking library calls and patching the second
child’s functionality directly into the first child, allowing me to debug the
first child. Using these techniques, I’ll wind through three parts of the
flag, each successively more difficult to break out.

## Challenge

> As a reward for making it this far in Flare-On, we’ve decided to give you a
> break. Welcome to the land of sunshine and rainbows!

The file is a Linux ELF executable:

    
    
    $ file break 
    break: ELF 32-bit LSB executable, Intel 80386, version 1 (SYSV), dynamically linked, interpreter /lib/ld-linux.so.2, for GNU/Linux 2.6.32, BuildID[sha1]=1793c43108b544ef35f9814b0caafcf76210631c, stripped
    

## Running It (Weirdness)

Right away it’s clear that things aren’t as simple as they appear. Something
is “stealing” my input:

    
    
    root@kali# ./break
    welcome to the land of sunshine and rainbows!
    as a reward for getting this far in FLARE-ON, we've decided to make this one soooper easy
    
    please enter a password friend :) password
    sorry, but 'sorry i stole your input :)' is not correct
    

It’s also catching my attempts to interrupt with Ctrl-C:

    
    
    root@kali# ./break
    welcome to the land of sunshine and rainbows!
    as a reward for getting this far in FLARE-ON, we've decided to make this one soooper easy
    
    please enter a password friend :) ^CI HAVE THE CONCH DONT INTERRUPT ME
    

Finally, running it once starts three processes:

    
    
    root@kali# pidof break
    9427 9426 9201
    

## Orienting / General Structure

### main

In Ghidra, `main` is super simple:

    
    
    void main(void)
    
    {
      ssize_t len_input;
      int result;
      undefined input_buffer [261];
      undefined *puStack12;
      
      puStack12 = &stack0x00000004;
      puts("welcome to the land of sunshine and rainbows!");
      puts("as a reward for getting this far in FLARE-ON, we\'ve decided to make this one soooper easy");
      putchar(10);
      printf("please enter a password friend :) ");
      len_input = read(0,input_buffer + 1,0xff);
      auStack273[len_input] = 0;
      result = main_compare(input_buffer + 1);
      if (result == 0) {
        printf("sorry, but \'%s\' is not correct\n",input_buffer + 1);
      }
      else {
        printf("hooray! the flag is: %s\n",input_buffer + 1);
      }
                        /* WARNING: Subroutine does not return */
      exit(0);
    }
    

`main_compare` is simpler:

    
    
    uint main1_compare(char *input)
    
    {
      int result;
      
      result = strcmp(input,"sunsh1n3_4nd_r41nb0ws@flare-on.com");
      return (uint)(result == 0);
    }
    

Obviously there’s something deeper going on.

### elf start

Going back to how an ELF starts, there’s an Entry Point given in the headers
that points to a starting function. This function typically gets things
started, pushes arguments, and calls `__libc_start_main`
([ref](https://refspecs.linuxbase.org/LSB_3.1.0/LSB-generic/LSB-
generic/baselib---libc-start-main-.html)):

    
    
    public start
    start proc near
    xor     ebp, ebp
    pop     esi
    mov     ecx, esp
    and     esp, 0FFFFFFF0h
    push    eax
    push    esp             ; stack_end
    push    edx             ; rtld_fini
    push    offset fini     ; fini
    push    offset init     ; init
    push    ecx             ; ubp_av
    push    esi             ; argc
    push    offset main     ; main
    call    ___libc_start_main
    hlt
    start endp
    

The `init` function calls `_init_proc` (typical) and then loops over the array
of function pointers passed to it above. For `break`, there are two The first
(08048cb0) isn’t super interesting, but the second (08048fc5, I’ll call
`_INIT_1`) is.

### _INIT_1 [08048fc5]

This function is also relatively straight forward:

  * Calls `setvbuf` ([docs](http://www.cplusplus.com/reference/cstdio/setvbuf/)) on both `stdin` and `stdout` setting them to null, effectively killing any input or output to this process.
  * It gets it’s own process ID (pid) with `getpid`.
  * `fork`, which creates a copy of the current process. The child process calls what I’m labeling as `main2` (080490c4).
  * Calls `prctl` with `PR_SET_PTRACER` and the child’s pid - now the child process has permission to trace / debug this process.
  * Sleeps.
  * Lowers it’s priority with `nice`.
  * Prints a message into nothing, which will cause a `SIGSEGV`, and returns (which leads to main above).

### main2 [080490c4]

The first child process (will refer to as child1 or first child) lives almost
entirely in this function, debugging the parent process. There’s a helper
function, `call_ptrace` [0804bae6] that loads `ptrace` from `libc.so.6` using
`dlopen` and `dlsym`.

    
    
    long call_ptrace(undefined4 request,pid_t pid,undefined4 addr,undefined4 data)
    
    {
      undefined4 hLibc;
      code *ptrace;
      long ret;
      
      hLibc = dlopen("libc.so.6",1);
      ptrace = (code *)dlsym(hLibc,"ptrace");
      ret = (*ptrace)(request,pid,addr,data);
      return ret;
    }
    

This avoids putting `ptrace` in the imports.

`main2` uses this helper to first send a `PTRACE_ATTACH` request to the
parent. On success, it:

  * Calls `waitpid` to wait for the parent to return, which it does [when the parent SIGSEGV?].
  * Uses `ptrace` to overwrite the first command of the `main_compare` function with 0xb0f, which is not a valid command. This means that when the parent process reaches this point, it will crash.
  * Gets its own PID, and passes that to `secondFork` [0804a0b4].
  * Calls `ptrace` with `PTRACE_CONT | PTRACE_SYSCALL` to tell the parent to run until a signal, which includes raising a `SIGTRAP` on syscall (without executing the syscall).

The rest of this function is a big loop on `while waitpid(parent_pid, status,
0) != -1`. These
[macros](https://code.woboq.org/gcc/include/bits/waitstatus.h.html) show how
to read the status. First it checks the low byte to see if it is 0x7f, which
means the process came back on a signal. The signal number is the next byte,
so it checks that and compares to various signals it has handlers for
(`SIGTRAP`, `SIGSEGV`, and others). `SIGTRAP` is the most interesting, as that
is thrown whenever the parent makes a syscall. In that case, it uses `ptrace`
to get the registers and grab `$eax`, the syscall number, which is used to
generate a key that directs what code is run instead of the legit syscall.
There are handlers for the following syscalls:

[Syscall](https://chromium.googlesource.com/chromiumos/docs/+/master/constants/syscalls.md#x86-32_bit) | Key | Handler Action  
---|---|---  
`exit` \- 1 [0x01] | b82d3c24 | Actually exits  
`read` \- 3 [0x03] | 91bda628 | Reads user input; pokes “stole your input” string into parent, but also actual input to different buffer; sets `$eax` to len of “store your input” string  
`write` \- 4 [0x04] | 7e85db2a | Prints message and sets `$eax` to len of message  
`execve` \- 11 [0x0b] | f7ff4e38 | Gets string from first arg from parent, replaces trailing `\n` with `\0`, and pokes it back into parent  
`chmod` \- 15 [0x0f] | ab202240 | Encryption related - See below  
`nice` \- 34 [0x22] | 3dfc1166 | Not actually called; `nice` instead calls `getpriority`, `setpriority`, and `getpriority`  
`ioctl` \- 54 [0x36] | 2499954e | Not actually called  
`truncate` \- 92 [0x5c] | 4a51739a | See below  
`getpriority` \- 96 [0x60] | 9678e7e2 | Before `setpriority`, sets `$eax` to 0x14; After`setpriority`, sets `$eax` to -0x81a52a0  
`setpriority` \- 97 [0x61] | 83411ce4 | Gets string based on `$edx` and pokes it into parent at 0x81a52a0.  
`uname` \- 122 [0x7a] | 09c7a9d6 | Userd in crypto; sets parent memory at `$ebx` and `$ebx+4` to constant values.  
`mlockall` \- 152 [0x98] | c93de012 | Used in crypto  
`pivot_root` \- 217 [0xd9] | e8135594 | Used in crypto; swaps values at parents `$ebx` and `$ecx`  
  
### main3 [08049c9c]

This function running in child2 attaches to child1 (its parent) using
`ptrace`, and then enters a similar `waitpid` loop. This loop just sends
`PTRACE_CONT`, so it isn’t breaking on syscalls, but just signals. It reads
the registers and the first four values from the stack from child1. The main
handler is for the `SIGSEGV`, which typically sets `$eax` (the function return
value), fixes the stack and sets `$eip` to the the next instruction (which is
on the stack from the function call).

Looking back through `main2`, there are several places where a `SIGSEGV` is
thrown by trying to call the function at 0:

    
    
    uVar1 = (*(code *)0x0)(0x91bda628,(int)(char)init_str[i * 2],(int)(char)init_str[i * 2 + 1]);
    

In each case, the first argument is a hex key value, which `main3` uses to
determine what to do next, which typically involves setting `$eax` to
something, setting `$eip` to the return value on the stack, and fixing the
stack.

This function also has a handler for `SIGINT`, which puts a stack string, “I
HAVE THE CONCH DONT INTERRUPT ME” and continues.

## Flag Part 1 - Hooking

### memcmp

Because `ptrace` is already attached to the parent and first child processes,
I can’t attach a debugger to them, leaving me needing some visibility into
what’s going on with them. My first attempt was to write a shared library to
hook libc functions as they are called to print information about what’s going
on. Looking at the list of imports, `memcmp` jumped out as interesting.

The following code will print the two buffers being compared with `memcmp` and
call the real one:

    
    
    #define _GNU_SOURCE
    
    #include <stdio.h>
    #include <dlfcn.h>
    #include <inttypes.h>
    #include <sys/types.h>
    
    typedef int (*memcmp_t)(const void *str1, const void *str2, size_t n);
    memcmp_t real_memcmp;
    
    int memcmp(const void *str1, const void *str2, size_t n) {
      fprintf(stderr, "memcmp: %s\n        %s\n", str1, str2);
      if (!real_memcmp) {
        real_memcmp = dlsym(RTLD_NEXT, "memcmp");
      }
    
      return real_memcmp(str1, str2, n);
    }
    
    __attribute__((constructor)) static void setup(void) {
      fprintf(stderr, "Hooked process...\n");
    }
    

Compile it:

    
    
    root@kali# gcc -shared -fPIC -ldl hooks.c -o hooks.so -m32
    

And run `break` with `LD_PRELOAD`:

    
    
    root@kali# LD_PRELOAD=hooks/hooks.so ./break
    Hooked process...
    welcome to the land of sunshine and rainbows!
    as a reward for getting this far in FLARE-ON, we've decided to make this one soooper easy
    
    please enter a password friend :) 0xdf-password
    memcmp: 0xdf-password
            w3lc0mE_t0_Th3_l
    sorry, but 'sorry i stole your input :)' is not correct
    

Just like that, I have the first part of the flag, `w3lc0mE_t0_Th3_l`. If I
submit a password that doesn’t start with that string, it returns failure
immediately. If I send a password that starts with that string, it will hang
for a couple minutes, and then returns the failure message.

Clearly there’s something else going on here.

### ptrace

I tried a couple other imports without finding anything interesting. Then I
decided to target `ptrace`. Because (as mentioned above) `ptrace` isn’t
imported via the standard mechanism but rather is loaded with `dlsym`, I can’t
hook it with `LD_PRELOAD`. Instead, I’ll create another shared object named
`pt.so`, and then find the string in the file used by this line:

    
    
    hLibc = dlopen("libc.so.6",1);
    

I’ll replace “libc.so.6” with “./pt.so\x00” so that it loads my library
instead.

    
    
    #define _GNU_SOURCE
    
    #include <stdio.h>
    #include <dlfcn.h>
    #include <inttypes.h>
    #include <sys/types.h>
    #include <unistd.h>
    
    
    char* procName(pid_t pid);
    const char *ptrace_types[] = { "0", "1", "PEEKDATA", "3", "4", "POKEDATA", "6", "CONT",
                                   "8", "9", "10", "11", "GETREGS", "SETREGS", "14", "15",
                                   "ATTACH", "17", "18", "19", "20", "21", "22", "23", "24",
                                   "25", "26", "27", "28", "29", "30", "CONT|SYSCALL" };
    const char *regs[] = { "ebx", "ecx", "edx", "esi", "edi", "ebp", "eax", "xds", "xes",
                           "xfs", "xgs", "orig_eax", "eip", "xcs", "eflags", "esp", "xss" };
    
    pid_t p1, p2, p3;
    int prev_getregs[17];
    char c;
    
    char* procName(pid_t pid) {
    
        if (pid == p1) {
            return "p1";
        } else if (pid == p2) {
            return "p2";
        } else if (pid == p3) {
            return "p3";
        } else {
            fprintf(stderr, "oops\n");
            return "oops";
        }
    }
    
    
    long ptrace(int request, pid_t pid, void *addr, void *data) {
      
        void *hLibc;
        int res, new_reg, orig_reg;
        int (*real_ptrace)(int request, pid_t pid, void *addr, void *data);
        hLibc = dlopen("libc.so.6",1);
        *(void**)(&real_ptrace) = dlsym(hLibc, "ptrace");
      
        pid_t cur_pid = getpid();
        if (ptrace_types[request] == "ATTACH") {
            if (!p2) {
                p1 = pid;
                p2 = cur_pid;
            } else if (!p3) {
                p3 = cur_pid;
            }
        }
      
        res = real_ptrace(request, pid, addr, data);
     
        //fprintf(stderr, "%s --> %s %-10s", procName(cur_pid), procName(pid), ptrace_types[request]);
        if (request == 2) {         // peekdata
        } else if (request == 5) {  //poke data
            fprintf(stderr, "%s --> %s %-10s", procName(cur_pid), procName(pid), ptrace_types[request]);
            fprintf(stderr, "  0x%08x =  0x%08x  ", addr, data);
            for (int i=0; i<4; i++) {
                int c = ((int)data << (3-i)*(8)) >> 24;
                if (c < 32 || c > 126) {
                    c = 46;
                }
                fprintf(stderr, "%c", (char)c);
            }
            fprintf(stderr, "\n");
        } else if (request == 12) { // getregs
            for (int i=0; i<17; i++) {
                prev_getregs[i] = *((int*)(data)+i);
            }
        } else if (request == 13) { // setregs
            fprintf(stderr, "%s --> %s %-10s", procName(cur_pid), procName(pid), ptrace_types[request]);
            for (int i=0; i < 17; i++) {
                new_reg = *((int*)(data) + i);
                orig_reg = prev_getregs[i];
                if (new_reg != orig_reg) {
                    fprintf(stderr, "  [%s] %08x --> %08x", regs[i], orig_reg, new_reg);
                }
            }
            fprintf(stderr, "\n");
        }
        return res; 
    }
    

The basic idea is that it catches a `prtrace` call, makes the call, and then
prints status based on the results. Originally I implemented printing for all
calls, but it was too much. I reduced it to only show when it changed things
in its parent process, either registers or data. For registers, it keeps the
previous data from `GETREGS` and looks for changes, only printing those. Any
time it `POKES` data, I print that as well. I also found it useful to get the
PIDs for the three processes, and refer to them as `p1`, `p2`, and `p3`, for
easy tracking.

Now the start of the process looks like:

    
    
    root@kali# ./break
    w3lc0mE_t0_Th3_l-0xdf@flare-on.com                  
    p2 --> p1 POKEDATA    0x08048cdb =  0x00000b0f  ....
    p2 --> p1 SETREGS     [eax] ffffffda --> 00000014
    p2 --> p1 POKEDATA    0x081a52a0 =  0x00000000  ....   
    p2 --> p1 SETREGS     [eax] ffffffda --> 00000000
    p2 --> p1 SETREGS     [eax] ffffffda --> f7e5ad60
    welcome to the land of sunshine and rainbows!p2 --> p1 SETREGS     [eax] ffffffda --> 0000002d
    
    p2 --> p1 SETREGS     [eax] ffffffda --> 00000001
    as a reward for getting this far in FLARE-ON, we've decided to make this one soooper easyp2 --> p1 SETREGS     [eax] ffffffda --> 00000059
    
    p2 --> p1 SETREGS     [eax] ffffffda --> 00000001
    
    p2 --> p1 SETREGS     [eax] ffffffda --> 00000001
    please enter a password friend :) p2 --> p1 SETREGS     [eax] ffffffda --> 00000022
    

I can see the first `POKEDATA` that breaks the comparison function. There’s
something changing `$eax` a few times.

On entering a password, I see first “sorry i stole your input :).” and then
the entered password `POKED` into different places in the main process:

    
    
    AAAABBBBCCCCDDDDEEEEFFFF
    p2 --> p1 POKEDATA    0xffdeb920 =  0x72726f73  sorr
    p2 --> p1 POKEDATA    0xffdeb924 =  0x20692079  y i 
    p2 --> p1 POKEDATA    0xffdeb928 =  0x6c6f7473  stol
    p2 --> p1 POKEDATA    0xffdeb92c =  0x6f792065  e yo
    p2 --> p1 POKEDATA    0xffdeb930 =  0x69207275  ur i
    p2 --> p1 POKEDATA    0xffdeb934 =  0x7475706e  nput
    p2 --> p1 POKEDATA    0xffdeb938 =  0xf7293a20   :).
    p2 --> p1 SETREGS     [eax] ffffffda --> 0000001c
    p2 --> p1 POKEDATA    0x081a56c0 =  0x41414141  AAAA
    p2 --> p1 POKEDATA    0x081a56c4 =  0x42424242  BBBB
    p2 --> p1 POKEDATA    0x081a56c8 =  0x43434343  CCCC
    p2 --> p1 POKEDATA    0x081a56cc =  0x44444444  DDDD
    p2 --> p1 POKEDATA    0x081a56d0 =  0x45454545  EEEE
    p2 --> p1 POKEDATA    0x081a56d4 =  0x46464646  FFFF
    p2 --> p1 POKEDATA    0x081a56d8 =  0x0000000a  ....
    p2 --> p1 POKEDATA    0xffdeb910 =  0x081a56c0  .V..
    p2 --> p1 SETREGS     [eip] 08048cdb --> 08048dcb
    p2 --> p1 POKEDATA    0x081a56d8 =  0x00000000  ....
    

Immediately following that, `$eip` is set to 08048dcb.

Unfortunately, while this is useful for tracking how information is passed
between the different processes, it still wasn’t enough to make clear what was
going on. If I enter something starting with “w3lc0mE_t0_Th3_l”, there’s a ton
of activity, but nothing that reveals a flag.

## Flag Part 2 - Patching

### gdb Init File

The thing preventing me from debugging the first child process is the second
child. At this point I moved to remove that process from the flow. I created a
gdb init file that would break in the first child process in `main2` before it
entered the while loop where it calls the function to `fork` the next child:

    
    
    secondFork(waitpid_ret);
    

At this breakpoint, I simply set `$eip` to the next command and continue:

    
    
    # don't start p3
    b *0x08049152
    commands
    set $eip=0x8049157
    c
    end
    

Now running in `gdb` I’m able to stay with the first child, but I start
hitting `SIGSEGV` signals that were previously handled by the second child.
For example, it hits this loop in a function I labeled `getmessage`:

    
    
        while (i < (int)init_str_len / 2) {
          uVar1 = (*(code *)0x0)(0x91bda628,(int)(char)init_str[i * 2],(int)(char)init_str[i * 2 + 1]);
          *(undefined *)(i + (int)__dest) = uVar1;
          i = i + 1;
        }
    

Calling address 0x00 results in a `SIGSEGV`, which the second child would
catch at `waitpid`. Then it reads the registers and the top four stack values:

    
    
    if (sig == SIGSEGV) {
        call_ptrace(PTRACE_GETREGS,parentPid,0,&regs);
        stack1 = call_ptrace(PTRACE_PEEKDATA,parentPid,regs.esp,0);
        stack2 = call_ptrace(PTRACE_PEEKDATA,parentPid,regs.esp + 4,0);
        stack3 = call_ptrace(PTRACE_PEEKDATA,parentPid,regs.esp + 8,0);
        stack4 = call_ptrace(PTRACE_PEEKDATA,parentPid,regs.esp + 0xc,0);
    

At the `SIGSEGV`, the top four stack values are:

Stack | Value  
---|---  
`stack1` | return address / next instruction after bad call  
`stack2` | first arg, the four byte hex value used as a key  
`stack3` | second arg  
`stack4` | third arg  
  
The second child process then enters a series of `if` / `else` based on the
key. So for this call, 0x91bda628, it sets `$eax` in the reg structure from
the first child to a combination of the next two args:

    
    
    else {
        if (stack2 == -0x6e4259d8) {
            regs.eax = stack4 - 1 & 0xf | (stack3 - 1) * 0x10;
        }
    }
    

Looking at each of the handlers, I added the following to the gdb init script
to handle each crash and continue:

    
    
    catch signal SIGSEGV
    commands
    silent
    if *((int*)($esp+0x4)) == 0x91bda628
        set $eax=((*((int*)($esp+0xc)) - 1) & 0xf) + ((*((int*)($esp+0x8)) - 1) * 0x10)
        set $eip=(*((int*)($esp)))
        set $esp=$esp+4
        c
        end
    if *((int*)($esp+0x4)) == 0xb82d3c24
        set $eax=(*((int*)($esp+0x8)) + 1)
        set $eip=(*((int*)($esp)))
        set $esp=$esp+4
        c
        end
    if *((int*)($esp+0x4)) == 0x7e85db2a
        set $eax=0x9e3779b9
        set $eip=(*((int*)($esp)))
        set $esp=$esp+4
        c
        end
    if *((int*)($esp+0x4)) == 0x6b4e102c
        set $eax=*((int*)($esp+0xc)) + *((int*)($esp+0x8))
        set $eip=(*((int*)($esp)))
        set $esp=$esp+4
        c
        end
    if *((int*)($esp+0x4)) == 0x5816452e
        set $eax=*((int*)($esp+0xc)) & 0x1f
        set $eax=((*((unsigned int*)($esp+0x8)) >> $eax) | (*((unsigned int*)($esp+0x8)) << ((-1*$eax) & 0x1f)))
        set $eip=(*((int*)($esp)))
        set $esp=$esp+4
        c
        end
    if *((int*)($esp+0x4)) == 0x44de7a30
        set $eax=*((int*)($esp+0xc)) ^ *((int*)($esp+0x8))
        set $eip=(*((int*)($esp)))
        set $esp=$esp+4
        c
        end
    end
    

With this in place (starting `gdb` with `-x [init_file]`), I can now debug in
the first child to get a sense for what’s going on. It does run much slower
than the original binary. It took close to 20 minutes to run to the end, so I
eventually did create a fully patched binary. Each of these operations in
second child were simple enough that I could just find machine instructions
for the bad call in a hex editor (including pushing the arguments), and
overwrite them with the instructions to do what the handler would do. This ran
much faster. The patches were:

    
    
    root@kali# diff <( xxd break-orig ) <( xxd break-mod)
    278c278
    < 00001150: 0c50 e85d 0f00 0083 c410 c745 cca0 521a  .P.].......E..R.
    ---
    > 00001150: 0c50 9090 9090 9083 c410 c745 cca0 521a  .P.........E..R.
    375,376c375,376
    < 00001760: 31d2 89c2 8b45 e483 ec04 5250 6824 3c2d  1....E....RPh$<-
    < 00001770: b88b 45d8 ffd0 83c4 1089 45e4 8b85 a8c0  ..E.......E.....
    ---
    > 00001760: 31d2 89c2 8b45 e483 c001 9090 9090 9090  1....E..........
    > 00001770: 9090 9090 9090 9090 9089 45e4 8b85 a8c0  ..........E.....
    395,397c395,397
    < 000018a0: 50ff 7508 6a05 e83b 2200 0083 c410 83ec  P.u.j..;".......
    < 000018b0: 0468 feca 0000 6837 1300 0068 2adb 857e  .h....h7...h*..~
    < 000018c0: 8b45 d8ff d083 c410 89c2 8b85 34ff ffff  .E..........4...
    ---
    > 000018a0: 50ff 7508 6a05 e83b 2200 0083 c410 9090  P.u.j..;".......
    > 000018b0: 9090 b8b9 7937 9e90 9090 9090 9090 9090  ....y7..........
    > 000018c0: 9090 9090 9090 9090 89c2 8b85 34ff ffff  ............4...
    1052,1057c1052,1057
    < 000041b0: 4508 8b40 1c89 c28b 45f4 83ec 0452 5068  E..@....E....RPh
    < 000041c0: 2c10 4e6b 8b45 f0ff d083 c410 8945 f48b  ,.Nk.E.......E..
    < 000041d0: 4508 8b80 a400 0000 89c2 8b45 f483 ec04  E..........E....
    < 000041e0: 5250 682e 4516 588b 45f0 ffd0 83c4 1089  RPh.E.X.E.......
    < 000041f0: 45f4 8b45 088b 404c 89c2 8b45 f483 ec04  E..E..@L...E....
    < 00004200: 5250 6830 7ade 448b 45f0 ffd0 83c4 1089  RPh0z.D.E.......
    ---
    > 000041b0: 4508 8b40 1c89 c28b 45f4 9001 c28b 4d08  E..@....E.....M.
    > 000041c0: 8b89 a400 0000 83e1 1f89 d0d3 e8f7 d983  ................
    > 000041d0: e11f d3e2 09c2 8b45 088b 404c 31d0 9090  .......E..@L1...
    > 000041e0: 9090 9090 9090 9090 9090 9090 9090 9090  ................
    > 000041f0: 9090 9090 9090 9090 9090 9090 9090 9090  ................
    > 00004200: 9090 9090 9090 9090 9090 9090 9090 9089  ................
    1116,1117c1116,1117
    < 000045b0: 83ec 0452 5068 28a6 bd91 8b85 2cff ffff  ...RPh(.....,...
    < 000045c0: ffd0 83c4 1088 8523 ffff ff8b 9528 ffff  .......#.....(..
    ---
    > 000045b0: 83e8 01c1 e004 83ea 0183 e20f 09d0 9090  ................
    > 000045c0: 9090 9090 9088 8523 ffff ff8b 9528 ffff  .......#.....(..
    3733,3734c3733,3734
    < 0000e940: 8d01 0204 0810 2040 801b 366c 6962 632e  ...... @..6libc.
    < 0000e950: 736f 2e36 0070 7472 6163 6500 7200 0000  so.6.ptrace.r...
    ---
    > 0000e940: 8d01 0204 0810 2040 801b 362e 2f70 742e  ...... @..6./pt.
    > 0000e950: 736f 0000 0070 7472 6163 6500 7200 0000  so...ptrace.r...
    

One other thing to note - I made the `gdb` init file by running until I
reached a `SIGSEGV`, then looking up the appropriate response, and adding it
to the file. You’ll note that the crash for first arg 0xa4f57126 isn’t in
there. That turned out to be a lucky mistake. My patched binary was generated
using my init file as a check list, so again, this one didn’t get patched,
again, a lucky choice for me, as I’ll explain later.

### Tracing Parent

#### _INIT_1 and main

Now I can look at the status from each `waitpid` return in the first child and
follow along in the main program. Each time, if it’s a `SIGTRAP`, it will get
the syscall number from the registry, generate a key value from that, and then
navigate to code that handles that key.

This was a helpful add to the `gdb` init file to print the syscall number on
each loop:

    
    
    # get syscall from p1
    b *0x804926b
    commands
    printf "SYSCALL: %d [0x%x]\n", $eax, $eax
    end
    

Now I can step through watching the different syscalls from the parent process
(using [this
table](https://chromium.googlesource.com/chromiumos/docs/+/master/constants/syscalls.md#x86-32_bit)
to get the name from number), and follow along in the code as the parent
finishes `_INIT_1` and goes to `main`.

SysCall| Function Called| Location  
---|---|---  
0 - restart_syscall| N/A| On child attach  
267 - clock_nanosleep| nanosleep((timespec *)PTR_DAT_081a50e8,(timespec
*)0x0);| _INIT_1  
96 - getpriority| iVar1 = nice(0xaa);  
97 - setpriority  
96 - getpriority  
4 - write (several)| Each of the puts or printf calls in main| main  
3 - read| sVar1 = read(0,auStack273 + 1,0xff);  
  
The handling code for the write system calls fetches a message that matches
what’s being printed and prints it from the first child. The read system call
gets the data with `fgets`, and then pokes the “sorry i stole your input”
string back into the parent:

    
    
    if (eax_key == -0x6e4259d8) {
        fgets(&user_input,0xff,stdin);
        sorrystoleinput_str = (char *)getmessage(0xb8);
        _DAT_081a57c0 = trace_regs.ecx;
        input_length = strlen(sorrystoleinput_str);
        poke_input_into_p1(parent_pid,trace_regs.ecx,sorrystoleinput_str,
                           input_length);
        input_length = strlen(sorrystoleinput_str);
        trace_regs.eax = input_length + 1;
        call_ptrace(PTRACE_SETREGS,parent_pid,0,&trace_regs);
    }
    

I can see this with the hooks:

    
    
    Testinput     <--- my input
    p2 --> p1 POKEDATA    0xffffd090 =  0x72726f73  sorr
    p2 --> p1 POKEDATA    0xffffd094 =  0x20692079  y i 
    p2 --> p1 POKEDATA    0xffffd098 =  0x6c6f7473  stol
    p2 --> p1 POKEDATA    0xffffd09c =  0x6f792065  e yo
    p2 --> p1 POKEDATA    0xffffd0a0 =  0x69207275  ur i
    p2 --> p1 POKEDATA    0xffffd0a4 =  0x7475706e  nput
    p2 --> p1 POKEDATA    0xffffd0a8 =  0xf7293a20   :).
    p2 --> p1 SETREGS     [eax] ffffffda --> 0000001c
    

It does save the real input into a buffer in the child process.

#### Redirection

At this point `main` calls the comparison function. However, as I noted above,
the first instruction has been overwritten leading to a `SIGILL` (Illegal
instruction). When this happens, the handler in first child goes here:

    
    
    if ((int)(waitpid_status1 & 0xff00) >> 8 == SIGILL) {
        input_length = strlen(&user_input);
        poke_input_into_p1(parent_pid,&user_input,&user_input,input_length);
        call_ptrace(PTRACE_GETREGS,parent_pid,0,&trace_regs);
        retval = call_ptrace(PTRACE_POKEDATA,parent_pid,trace_regs.esp + 4,&user_input);
        if (retval == -1) {
            /* WARNING: Subroutine does not return */
            exit(0);
        }
        trace_regs.eip = main1b;
        call_ptrace(PTRACE_SETREGS,parent_pid,0,&trace_regs);
    }
    

It pokes the real user input into the same global variable in the parent
process, and then overwrites the first argument (where `$esp` holds the return
address) with the address of that variable. It then sets `$eip` to a function
I’ve named `main1b` [08048dcb], and lets the parent run again. This
effectively creates a call to `main1b([user_input])`.

#### main1b [08048dcb]

This function isn’t too complex, and I’ll look at it in 3 parts. First, it
uses the user input to make a scary `execve` call:

    
    
      in_len = strlen(param_1);
      rm_str = "rm";
      rf_str = &rf_str;
      nopreserveroot_str = "--no-preserve-root";
      slash_str = &slash_str;
      local_18 = 0;
      execve(param_1,&rm_str,(char **)0x0);
      in_len = in_len - 1;
    

This ends up being `execve([input], [rm -rf --no-preserve-root /], 0x0)`, but
it isn’t run because the first child catches the syscall and runs its handler
instead. The handler for the `execve` syscall does run, and it replaces a `\n`
on the end of my input with a `\x00`, and returns.

The second part is where `nice` is called (which generates three syscalls)
with the result being passed to another function that initializes some
encryption stuff, and then another function which uses that to decrypt the
string that is the correct first 0x10 bytes of the flag:

    
    
    local_14 = nice(0xa5);
    local_14 = -local_14;
    loadBuffer(local_d8,local_14);
    loadFlagStart(local_d8,&DAT_081a50ec);
    loadFlagStart(local_d8,&DAT_081a50f0);
    loadFlagStart(local_d8,&DAT_081a50f4);
    loadFlagStart(local_d8,&DAT_081a50f8);
    

After this, `DAT_081a50ec` holds the string “w3lc0mE_t0_Th3_l”.

The third part is a call to `memcmp` (as observed from the hook), and it the
first 0x10 bytes of input match that string, it passes the rest of the input
(skipping the first 0x10 bytes) into `main1c`. If the `memcmp` does not return
a match, it sets the return value to 0 and exits.

    
    
      memcmp_return = memcmp(param_1,&DAT_081a50ec,0x10);
      if (memcmp_return == 0) {
        memset(&DAT_081a50ec,0,0x10);
        return = main1c(param_1 + 0x10);
      }
      else {
        memset(&DAT_081a50ec,0,0x10);
        return = 0;
      }
      return return;
    }
    

As this function will be returning to the original `main`, I want this to
return non-zero for success. Obviously then I need the flag to start with the
string I identified earlier, and then to dig into `main1c` to figure out what
happens there to get it to return non-zero.

#### main1c [08048f05]

This code running in the parent process continues using the syscalls to run
different code as dictated by the first child.

    
    
      inv_no_purpose_string = nice(0xa4);
      len_str_has_no_purpose = strlen((char *)-inv_no_purpose_string);
      key = keygen(0,0,(char *)-inv_no_purpose_string,len_str_has_no_purpose,0);
      max_40000 = 40000;
      memcpy(&DAT_0804c640,user_input_remain,0x20);
      i = 0;
      while (i < max_40000) {
        encryptBlock(&DAT_0804c640 + i,key,local_fa0);
        i = i + 8;
      }
      result = truncate(&DAT_0804c640,0x20);
      return (result == 0x20);
    

The code above calls `nice` (which runs three syscalls, 0x60, 0x61, 0x60),
which pokes the following string into memory with the 0x61 call (as seen from
my hook):

    
    
    p2 --> p1 POKEDATA    0x081a52a0 =  0x73696854  This
    p2 --> p1 POKEDATA    0x081a52a4 =  0x72747320   str
    p2 --> p1 POKEDATA    0x081a52a8 =  0x20676e69  ing 
    p2 --> p1 POKEDATA    0x081a52ac =  0x20736168  has 
    p2 --> p1 POKEDATA    0x081a52b0 =  0x70206f6e  no p
    p2 --> p1 POKEDATA    0x081a52b4 =  0x6f707275  urpo
    p2 --> p1 POKEDATA    0x081a52b8 =  0x61206573  se a
    p2 --> p1 POKEDATA    0x081a52bc =  0x6920646e  nd i
    p2 --> p1 POKEDATA    0x081a52c0 =  0x656d2073  s me
    p2 --> p1 POKEDATA    0x081a52c4 =  0x796c6572  rely
    p2 --> p1 POKEDATA    0x081a52c8 =  0x72656820   her
    p2 --> p1 POKEDATA    0x081a52cc =  0x6f742065  e to
    p2 --> p1 POKEDATA    0x081a52d0 =  0x73617720   was
    p2 --> p1 POKEDATA    0x081a52d4 =  0x79206574  te y
    p2 --> p1 POKEDATA    0x081a52d8 =  0x2072756f  our 
    p2 --> p1 POKEDATA    0x081a52dc =  0x656d6974  time
    p2 --> p1 POKEDATA    0x081a52e0 =  0x0000002e  ....
    

Then the second 0x60 syscall sets `$eax` to 0xf7e5ad60, which will be the
return value for `nice`. That value is negated and used as a pointer in the
rest of the function, which I can do in the built in Ubuntu calculator to see
that’s 0x081A52A0, the address of the string:

![image-20201025142601875](https://0xdfimages.gitlab.io/img/image-20201025142601875.png)

I didn’t dig into the function I named `keygen` much, as the output is the
same every time, regardless of my input. It then copies the remaining input
(first 0x10 bytes stripped before passing to `main1c`), copies it into a
global buffer that’s already populated with random looking data, and then
looks over it in blocks. Without even looking at the function called on each
block, I can guess this is an encryption/decryption routine for a block
cipher. The results are passed to `truncate` (which has its own code defined
in `main2`), and if that returns 0x20, it returns True which is non-zero.

### Crypto

#### Victory Conditions

This loop is what takes a while to run, as it encrypts 0x40000 / 8 = 0x8000
blocks. I can put a break on the `truncate` handler and let it run, or let it
run for a bit and then Ctrl-c to break it, and look at the buffer it’s working
on:

    
    
    gdb-peda$ hexdump 0x804c640 200
    0x0804c640 : fe c5 f8 1d 80 2d 6b ba 59 83 26 ac 5a bc ef 11   .....-k.Y.&.Z...
    0x0804c650 : 9a e3 00 54 16 24 b4 51 60 61 7a af ef a8 8d 6d   ...T.$.Q`az....m
    0x0804c660 : 41 63 63 6f 72 64 69 6e 67 20 74 6f 20 61 6c 6c   According to all
    0x0804c670 : 20 6b 6e 6f 77 6e 20 6c 61 77 73 20 6f 66 20 61    known laws of a
    0x0804c680 : 76 69 61 74 69 6f 6e 2c 20 74 68 65 72 65 20 69   viation, there i
    0x0804c690 : 73 20 6e 6f 20 77 61 79 20 74 68 61 74 20 61 20   s no way that a 
    0x0804c6a0 : 62 65 65 20 73 68 6f 75 6c 64 20 62 65 20 61 62   bee should be ab
    0x0804c6b0 : 6c 65 20 74 6f 20 66 6c 79 2e 20 49 74 73 20 77   le to fly. Its w
    0x0804c6c0 : 69 6e 67 73 20 61 72 65 20 74 6f 6f 20 73 6d 61   ings are too sma
    0x0804c6d0 : 6c 6c 20 74 6f 20 67 65 74 20 69 74 73 20 66 61   ll to get its fa
    0x0804c6e0 : 74 20 6c 69 74 74 6c 65 20 62 6f 64 79 20 6f 66   t little body of
    0x0804c6f0 : 66 20 74 68 65 20 67 72 6f 75 6e 64 2e 20 54 68   f the ground. Th
    0x0804c700 : 65 20 62 65 65 2c 20 6f                           e bee, o
    

The first two blocks (0x20 bytes) are an encrypted version of my input. Beyond
that, it appears to be a script from the movie [Bee
Movie](https://web.njit.edu/~cm395/theBeeMovieScript/). It’s actually a bit
more than that, but I’ll come back to it later.

Before diving into the encryption or the rest of the buffer, I’d better take a
look at what the program wants. After all the blocks are encrypted (it’s a bit
weird that the output of the encryption is the plaintext movie script, but the
encryption / decryption schemes are kind of mirror, and my input it going the
opposite direction as the script, so I’ll stick with encryption for this
direction), the buffer is passed into `truncate`:

    
    
      result = truncate(&DAT_0804c640,0x20);
      return (result == 0x20);
    

The handler for this syscall looks simple enough:

    
    
    if (eax_key == 0x4a51739a) {
        /* truncate */
        getDataFromParent(parent_pid,trace_regs.ebx,&DAT_0804c640,40000);
        i = 0;
        while ((i < 40000 && ((&DAT_0804c640)[i] != '\0'))) {
            local_3f50[i] = (&DAT_0804c640)[i];
            if ((returnval == -1) && (local_3f50[i] != (&DAT_081a5100)[i])) {
                returnval = i;
            }
            i = i + 1;
        }
        /* "returns" returnval */
        trace_regs.eax = (*null)(0xa4f57126,&user_input,returnval);
        returnval = trace_regs.eax;
        /* Need to set EAX to 0x20 */
        call_ptrace(PTRACE_SETREGS,parent_pid,0,&trace_regs);
    

It gets the full encrypted buffer from the parent process, and loops over the
entire thing one byte at a time, copying each byte into a local buffer. If the
return value has not been set (it’s initialized to -1 earlier), and the
current byte doesn’t match the corresponding byte in a static global, it sets
the return value to `i`, and continues. This effectively is a inefficient way
to compare these two buffers and return the first time they don’t match. Since
I’m looking for a value of 0x20 for the return, that tells me I want the next
0x20 bytes of my input to match the decrypted value of `DAT_081a5100`. So if I
can figure out the encryption and decrypt the buffer, I’ll have success.

#### encryptBlock [0804c369]

This function is pretty straight forward crypto once I get the functions
labeled:

    
    
    void encryptBlock(uint *block,undefined4 key0-3,undefined4 key4-7,char *CryptArray)
    
    {
      uint mixed_second;
      int in_GS_OFFSET;
      undefined4 i;
      code *null;
      uint firsthalf;
      __mode_t secondhalf;
      __mode_t temp;
      uint local_14;
      int canary;
      
      canary = *(int *)(in_GS_OFFSET + 0x14);
      null = (code *)0x0;
      GenerateArrayFromKey(key0-3,key4-7,0x10,CryptArray);
      firsthalf = *block;
      secondhalf = block[1];
      i = 0;
      temp = secondhalf;
      mixed_second = chmod(CryptArray,secondhalf);
      secondhalf = mixed_second ^ firsthalf;
      firsthalf = temp;
      local_14 = secondhalf;
      (*null)(0x804c3c4,&i);
      *block = secondhalf;
      block[1] = firsthalf;
      if (canary != *(int *)(in_GS_OFFSET + 0x14)) {
                        /* WARNING: Subroutine does not return */
        __stack_chk_fail();
      }
      return;
    }
    

It uses the key value passed in to generate an array that’s used in the mixing
function, `chmod`. It takes the two halves of the block, mixes the second,
xors the result with the first half and sets that to the new second half. The
new first half is the original second half.

Then there’s a call to `(*null)(0x804c3c4,&i);`, which causes a `SIGSEGV`
that’s handled by the first child. When it gets to the child, the top of the
stack will be the next instruction, the value 0x804c3c4, and the value `i`.
The handler reads these values from the stack, increments `i`, and checks it
against 0x10. If it’s less than, it sets `$eip` to the second stack value
(0x804c3c4) and pokes the incremented `i` back into the parent. Once it’s run
16 times, it sets `$eip` to the next address. So this single line is basically
a for loop over 16 times.

This is all an implementation of a [Feistel
cipher](https://en.wikipedia.org/wiki/Feistel_cipher). To decrypt, I just need
to implement the same mixing function and swap the half order:

![Feistel cipher diagram en.svg](https://0xdfimages.gitlab.io/img/511px-
Feistel_cipher_diagram_en.svg.png)

#### Python Implementation

I didn’t have to dig into the `CryptArray` generation, but rather, because
it’s passed into `chmod`, I was able to get the static values from there using
`gdb`. In `chmod`, the `CryptArray` and input are passed into a function that
uses handlers in the second child to do the crypt operations:

    
    
    undefined4 FUN_0804c19c(int cryptStruct,undefined4 input)
    
    {
      undefined4 result;
                        /* Add input plus first struct val together */
      result = (*(code *)0x0)(0x6b4e102c,input,*(undefined4 *)(cryptStruct + 0x1c));
                        /* shift and reorder 1 based on 2 (which is 3rd arg in struct) */
      result = (*(code *)0x0)(0x5816452e,uVar1,*(undefined4 *)(cryptStruct + 0xa4));
                        /* xor two args (result and 2nd obj in struct) */
      result = (*(code *)0x0)(0x44de7a30,uVar1,*(undefined4 *)(cryptStruct + 0x4c));
      return result;
    }
    

The rest was walking through the `chmod` handler to determine the mixing
algorithm, which I could debug since it’s in the first child, making it not
too difficult.

    
    
    #!/usr/bin/env python3
    
    import binascii
    from pwn import *
    
    
    # generated in 804c217
    crypt_array = [[0x4b695809, 0x674a1dea , 0x0000000f],
    [0xe35b9b24, 0xad92774c , 0x00000011],
    [0x71adcd92, 0x56c93ba6 , 0x00000011],
    [0x38d6e6c9, 0x2b649dd3 , 0x00000011],
    [0x5a844444, 0x8b853750 , 0x0000000c],
    [0x2d422222, 0x45c29ba8 , 0x0000000c],
    [0x16a11111, 0x22e14dd4 , 0x0000000c],
    [0xcdbfbfa8, 0x8f47df53 , 0x00000015],
    [0xe6dfdfd4, 0x47a3efa9 , 0x00000015],
    [0xf36fefea, 0x23d1f7d4 , 0x00000015],
    [0x79b7f7f5, 0x11e8fbea , 0x00000015],
    [0xfa34ccda, 0x96c3044c , 0x0000000f],
    [0x7d1a666d, 0x4b618226 , 0x0000000f],
    [0xf8620416, 0xbb87b8aa , 0x0000000f],
    [0x7c31020b, 0x5dc3dc55 , 0x0000000f],
    [0x78f7b625, 0xb0d69793 , 0x00000012]]
    
    
    def chmod(crypt, word):
        shift = crypt[2] & 0x1f
        step1 = (crypt[0] + word) & 0xffffffff
        step2 = (step1 >> shift) | (step1 << ((-shift) & 0x1f)) & 0xffffffff
        return crypt[1] ^ step2
    
    
    def encrypt8bytes(b):
    
        L, R = u32(b[:4]), u32(b[4:])
        for i in range(16):
            temp = R
            R = chmod(crypt_array[i], R) ^ L
            L = temp
        return p64((L << 32) + R)
    
    
    def decrypt8bytes(b):
        R, L = u32(b[:4]), u32(b[4:])
        for i in range(16):
            temp = L
            L = chmod(crypt_array[15-i], L) ^ R
            R = temp
        return p64((R << 32) + L)
    
    
    test_string = encrypt8bytes("AAAABBBB")
    print(f'{test_string}')
    
    plaintext = decrypt8bytes(test_string)
    print(plaintext)
    
    enc_flag = binascii.unhexlify("64a06002ea8a877d 6ce97ce4823f2d0c 8cb7b5ebcf354f42 4fad2b4920287ce0".replace(' ',''))
    
    flag = b''
    for i in range(len(enc_flag)//8):
        flag += decrypt8bytes(enc_flag[(8*i):(8*i)+8])
    
    print(flag)
    

When I run this, I can see it encrypts and decrypts a test block ok, and then
shows me the next part of the flag:

    
    
    root@kali# ./crypto.py 
    b'x(5\x0fGp\xfcD'
    AAAABBBB
    4nD_0f_De4th_4nd_d3strUct1oN_4nd
    

## Flag Part 3 - New Code

### Identify New Part

At this point, I figured I had the correct flag. I tried both
`4nD_0f_De4th_4nd_d3strUct1oN_4nd` and
`4nD_0f_De4th_4nd_d3strUct1oN_4nd@flare-on.com`, but no luck on the Flare site
or in the program. I was confused. The loop in `truncate` would run, and set
the return value to 0x20, the first place where the input didn’t match the
start of Bee Movie, and then the return value should be right to print the
success message.

Looking at `truncate` again:

    
    
    if (eax_key == 0x4a51739a) {
        /* truncate */
        getDataFromParent(parent_pid,trace_regs.ebx,&DAT_0804c640,40000);
        i = 0;
        while ((i < 40000 && ((&DAT_0804c640)[i] != '\0'))) {
            local_3f50[i] = (&DAT_0804c640)[i];
            if ((returnval == -1) && (local_3f50[i] != (&DAT_081a5100)[i])) {
                returnval = i;
            }
            i = i + 1;
        }
        /* "returns" returnval */
        trace_regs.eax = (*null)(0xa4f57126,&user_input,returnval);
        returnval = trace_regs.eax;
        /* Need to set EAX to 0x20 */
        call_ptrace(PTRACE_SETREGS,parent_pid,0,&trace_regs);
    

There is this null call that is handled by the second child:

    
    
    if (stack2 == -0x5b0a8eda) {
        regs.eax = stack4;
        if (stack4 != 0xffffffff) {
            getDataFromParent(parentPid,stack3,&user_input,0x3e);
            iVar3 = strncmp(&DAT_081a56f0,"@no-flare.com",0xd);
            if (iVar3 != 0) {
                regs.eax = -1;
            }
        }
    }
    

It sets `$eax` to `stack4` (the return value, 0x20), and then checks that 0x30
bytes into the input is “@no-flare.com”, setting `$eax` to -1 if they don’t
match. I did try `4nD_0f_De4th_4nd_d3strUct1oN_4nd@no-flare.com`, but it
didn’t take either.

I ran the unmodified binary with a break point in this code, but it never hit
(which is consistent with the fact that I never patched it in the modified
binary and it still never crashed.) Given that, and the fact that the flag
looks incomplete (ending in “and”), led me back into `truncate`.

It turns out there is a buffer overflow in the copy `local_3f50[i] =
(&DAT_0804c640)[i];`. `local_3f50` is defined by Ghidra as `char local_3f50
[16000];`. But the copy will loop until the first null. If I dump the full
buffer to a file in `gdb` (`dump binary memory buffer.bin 0x804c6400
0x804c640+0x40000`), and look at the `hexdump -C` in less, the first “ 00 “
comes at offset 3f28 (or 16168):

    
    
    00003f20  20 6d 79 2e 70 3b 05 08  00 20 57 68 61 74 e2 80  | my.p;... What..|
    

This overflow happens to overwrite the variable I named `null` because it just
held a 0 and then was called in `truncate` (I thought to generate a `SIGSEGV`
to the second child). `local_3f50` is at `$EBP-0x3f4c`, and `null` is at
​`$EBP-0x28`. So what overwrites `null` is 0x3f24 bytes into the input/movie
script:

    
    
    gdb-peda$ p 0x3f4c-0x28
    $35 = 0x3f24
    gdb-peda$ x/xw 0x0804c640+0x3f24
    0x8050564:      0x08053b70
    

Which leads to this at `trace_regs.eax =
(*null)(0xa4f57126,&user_input,returnval);`, where `$eax` isn’t null, but an
address:

    
    
    [----------------------------------registers-----------------------------------]
    EAX: 0x8053b70 --> 0x75ffec8b 
    EBX: 0x1                                                              
    ECX: 0xffff91fc --> 0x260a064                                         
    EDX: 0xffffd123 --> 0x3f2808 
    ESI: 0x0
    EDI: 0xffff91f4 --> 0x0
    EBP: 0xffffd148 --> 0xffffd178 --> 0x1 
    ESP: 0xffff90e0 --> 0xa4f57126                                        
    EIP: 0x8049869 --> 0xc483d0ff                                         
    EFLAGS: 0x292 (carry parity ADJUST zero SIGN trap INTERRUPT direction overflow)
    [-------------------------------------code-------------------------------------]
       0x8049860:   push   eax                                            
       0x8049861:   push   0xa4f57126
       0x8049866:   mov    eax,DWORD PTR [ebp-0x28]
    => 0x8049869:   call   eax     
       0x804986b:   add    esp,0x10
       0x804986e:   mov    DWORD PTR [ebp-0x20],eax
       0x8049871:   mov    eax,DWORD PTR [ebp-0x20]
       0x8049874:   mov    DWORD PTR [ebp-0xb4],eax            
    Guessed arguments:                                                                                                                           
    arg[0]: 0xa4f57126               
    arg[1]: 0x81a56c0 ("w3lc0mE_t0_Th3_l4nD_0f_De4th_4nd_d3strUct1oN_4ndAAAABBBBCCCCDDDD@flare-on.com\n")
    arg[2]: 0x20 (' ')                                                                                                                           
    [------------------------------------stack-------------------------------------]
    0000| 0xffff90e0 --> 0xa4f57126 
    0004| 0xffff90e4 --> 0x81a56c0 ("w3lc0mE_t0_Th3_l4nD_0f_De4th_4nd_d3strUct1oN_4ndAAAABBBBCCCCDDDD@flare-on.com\n")
    0008| 0xffff90e8 --> 0x20 (' ')
    0012| 0xffff90ec --> 0x9c40 
    0016| 0xffff90f0 --> 0x0 
    0020| 0xffff90f4 --> 0x2 
    0024| 0xffff90f8 --> 0xf7fcb700 --> 0x8048697 ("GLIBC_2.0")
    0028| 0xffff90fc --> 0x1 
    [------------------------------------------------------------------------------]
    Legend: code, data, rodata, value
    
    Thread 3.1 "break-mod" hit Breakpoint 3, 0x08049869 in ?? ()
    

It’s calling

So what’s at 0x8053b70? Well, it’s 0x7530 (or 30000) bytes into the buffer
with the input/movie script, which happens to be where the buffer goes from
Bee Movies script to binary stuff:

![image-20201026133208868](https://0xdfimages.gitlab.io/img/image-20201026133208868.png)

The script seems to pick up later:

![image-20201026133333505](https://0xdfimages.gitlab.io/img/image-20201026133333505.png)

I dumped from 0x7530 to 0x8816 into a new file I could open in Ghidra and
analyze as a new file.

### Unpacked main [0805492e]

The top of the code, 08053b70, just moves three parameters passed in back to
the top of the stack, and calls 0805492e. This function serves are the main
for this section.

At the very bottom, there’s some confusing loops:

    
    
      i = bufcmp((int)match1a,(int)match1b);
                        /* need i==0 */
      if (i == 0) goto LAB_08054c40;
      do {
        parent_regs.eax = -1;
        callPtrace(PTRACE_SETREGS,ppid,(ulong)&parent_regs,0);
        callPtrace(PTRACE_DETACH,ppid,(ulong)&parent_regs,0);
        exit();
    LAB_08054c40:
        i = bufcmp((int)match2a,(int)match2b);
                        /* This is a win! */
        if (i == 0) {
          *(undefined *)(input + 0x48) = 0;
          FUN_08054c75(0x49,_DAT_081a57c0,ppid,(char *)input);
          parent_regs.eax = 0x20;
          callPtrace(PTRACE_SETREGS,ppid,(ulong)&parent_regs,0);
          callPtrace(PTRACE_DETACH,ppid,(ulong)&parent_regs,0);
          exit();
        }
      } while( true );
    

This really simplifies to pseudocode:

    
    
    if bufcmp(match1a == match1b) and bufcmp(match2a == match2b):
        parent.eax = 0x20
    else:
        parent.eax = -1
    detach
    

`bufcmp` is a my given name. There’s a structure used in this code that
represents large numbers that expand across up to 32 4 byte words. Several of
the functions deal with what ends up being mathematical operations on these
numbers. This function, `bufcmp` checks if two numbers are equal by comparing
each word.

So what’s in these buffers? Two of them, `match1a` and `match2a` are both
generated at the top by a function I named `decodeString`, which takes a
static buffer and decodes to into a new constant buffer. These are the same
regardless of my input.

I did some debugging to look at `match1b`, it ends up being a static copy of
`match1a` each time, independent of my input. That leaves just `match2b`.

There is a bunch of static in this code that just doesn’t matter. For example,
there’s a read from `/dev/urandom`, but it turns out that input is later
overwritten by all nulls before it’s used elsewhere. Some debugging and code
analysis showed that the `input` –> `match2b` occurs on these two lines:

    
    
    FUN_080546e1(input_remain,(int)local_708,(int)local_508);
    FUN_080543ca((int)local_508,(int)local_908,(int)local_488,(int)match2b);
    

Beyond that, `local_708` and `local_908` are static values, and `local_488` is
always all nulls. So input goes into `FUN_080546e1`, writing into `local_508`.
Then `local_508` goes into `FUN_080543ca`, writing to `match2b`.

### Math Functions

The first function, 800546e1, is largely two nested for loops:

    
    
    void __regparm3 FUN_080546e1(int in1,int in2,int out)
    
    {
      longlong lVar1;
      int j;
      int i;
      undefined outer [128];
      uint inner [33];
      undefined4 local_30;
      undefined4 local_28;
      uint local_24;
      int in1_local;
      int in2_local;
      int out_local;
      
      in1_local = in1;
      in2_local = in2;
      out_local = out;
      zero0x20words(out);
      i = 0;
      while (i < 0x20) {
        zero0x20words((int)outer);
        j = 0;
        while (j < 0x20) {
          if (i + j < 0x20) {
            zero0x20words((int)inner);
            local_30 = 0;
            local_24 = *(uint *)(in2_local + j * 4);
            local_28 = 0;
            lVar1 = (ulonglong)*(uint *)(in1_local + i * 4) * (ulonglong)local_24;
            swap_low_high(inner,(uint)lVar1,(uint)((ulonglong)lVar1 >> 0x20));
            shifter((int)inner,i + j);
            adder((int)inner,(int)outer,(int)outer);
          }
          j = j + 1;
        }
        adder(out_local,(int)outer,out_local);
        i = i + 1;
      }
      return;
    }
    

I implemented this in Python to see how it was working. After playing with it
a bit, it’s clear that this is just a multiplication of the large numbers with
carry, in the buffer format. There are other functions for add, subtract, and
divide. Once I had a Python POC that could take my input and produce the same
buffer I would see in debugging, I started simplifying and renaming functions,
until it looked like:

    
    
    #!/usr/bin/env python3
    
    import binascii
    from pwn import *
    
    inputstr = b"AAAABBBBCCC@flare-on.com\x00\x00\x00\x00\x00\x00\x00\x00".ljust(128, b"\x00")
    user_input = []
    temp708 = binascii.unhexlify("31 dd 41 ea 5a 98 45 8f 8d 0c 00 43 71 a5 e7 39 60 15 2d 3a f0 5b 4a ef f1 a2 3f a5 c7 57 03 c1".replace(' ', '')).ljust(128, b"\x00")
    buf708 = []
    temp908 = binascii.unhexlify("4f d8 a9 eb 2a 5f 71 c3 13 ea 68 15 6b b1 fa b1 0d 77 a8 ae fa 92 ae ad e6 e1 a9 d5 47 34 cc d1".replace(' ', '')).ljust(128, b"\x00")
    buf908 = []
    temp_goal = binascii.unhexlify("eb 97 46 c0 48 6f 14 e4 51 3d 8e b1 eb 40 28 76 48 7a 08 4e ad fb ef fc 3a a2 ed e7 d4 c5 36 d0".replace(' ', '')).ljust(128, b"\x00")
    goal = []
    for i in range(8):
        buf708 += [u32(temp708[i*4:(i*4)+4])]
        buf908 += [u32(temp908[i*4:(i*4)+4])]
        user_input += [u32(inputstr[i*4:(i*4)+4])]
        goal += [u32(temp_goal[i*4:(i*4)+4])]
    buf708 += [0] * 120
    buf908 += [0] * 120
    user_input += [0] * 120
    
    
    def shiftupword(p1, p2):
    
        res = [0] * 0x20
        res[p2] = p1[0]
        if p2 < 0x1f:
            res[p2+1] = p1[1]
        return res
    
    
    def addbufs(p1, p2):
    
        flag = 0
        res = [0] * 0x20
    
        for i in range(0x20):
          res[i] = (p1[i] + p2[i] + flag)
          flag = res[i] >> 32
          res[i] = res[i] & 0xffffffff
    
        return res
        
    
    def multbufs(user_in, static):
    
        result = [0] * 0x20
    
        for i in range(0x20):
            outer = [0] * 0x20
            for j in range(0x20):
                inner = [0] * 0x20
                if i + j < 0x20:
                    word708 = static[j]
                    wordin = user_in[i]
                    prod = word708 * wordin
                    inner[0] = prod % 0x100000000
                    inner[1] = (prod >> 0x20) & 0xffffffff
                    inner = shiftupword(inner, i+j)
                    outer = addbufs(inner, outer)
    
            result = addbufs(result, outer)
    
        return result
    
    
    def encrypt(userinput, static1, static2):
        buf508 = multbufs(userinput, static1)
        temp1 = divbufs(buf508, static2)
        temp2 = multbufs(temp1, static2)
        return subbufs(buf508, temp2)
    
    
    def bufcmp(b1, b2):
    
        for i in range(min(len(b1), len(b2)) - 1, -1, -1):
            if b2[i] < b1[i]:
                return 1
            if b1[i] < b2[i]:
                return -1
        return 0
    
    def divbufs(buf1, buf2):
    
        mask = [1] + [0] * 0x1f
        copy2 = [x for x in buf2]
        while bufcmp(copy2, buf1) != 1:
            mask = shift_up(mask)
            buf2 = shift_up(copy2)
        out = [0] * 0x20
        shift_down(mask)
        shift_down(copy2)
        while any(x != 0 for x in mask):
            if bufcmp(buf1, copy2) != -1:
                buf1 = subbufs(buf1, copy2)
                out = [x|y for x,y in zip(mask, out)]
            mask = shift_down(mask)
            buf2 = shift_down(copy2)
        return out
    
    
    def subbufs(b1, b2):
    
        cf = 0
        out = [0] * 0x20
    
        for i in range(0x20):
            if b2[i] + cf > b1[i]:
                out[i] = b1[i] + 0x100000000 - b2[i] - cf
                cf = 1
            else:
                out[i] = b1[i] - b2[i] - cf
                cf = 0
        return out
    
    
    def shift_up(buf):
    
        for i in range(0x1f, 0, -1):
            buf[i] = ((buf[i] << 1) | (buf[i-1] >> 0x1f)) & 0xffffffff
        buf[0] = (buf[0] << 1) & 0xffffffff
        return buf
    
    
    def shift_down(buf):
    
        for i in range(0x1f):
            buf[i] = buf[i] >> 1 | ((buf[i+1] << 0x1f) & 0xffffffff)
        buf[0x1f] = buf[0x1f] >> 1
        return buf
        
    
    # print buffer as hex string
    def pp(buf, label=''):
        hexstr = binascii.hexlify(b''.join([p32(x) for x in buf]))
        print(f'{label} {hexstr.decode()}')
    
    
    # return buffer as int
    def buf2int(buf):
    
        return sum([x*pow(2,i*32) for i,x in enumerate(buf[:0x20])])
        
    
    res = encrypt(user_input, buf708, buf908)
    

I could start this and run with `python3 -i crypto2.py` so that I got a prompt
at the end and could play with things.

The key part here is this:

    
    
    def encrypt(userinput, static1, static2):
        buf508 = multbufs(userinput, static1)
        temp1 = divbufs(buf508, static2)
        temp2 = multbufs(temp1, static2)
        return subbufs(buf508, temp2)
    

The last three operations are to take some `x`, divide by `static2`, then
multiply by `static2`, and then subtract that from `x`.

\\[x - (\frac{x}{static2}*static2)\\]

This is actually the same as \\(x\mod static2\\)

So this entire encryption is \\(output\equiv (input * static1)\mod static2\\).

### Reverse

To reverse this, I just need to find the mod inverse:

    
    
    #!/usr/bin/env python3
    
    import binascii
    from pwn import *
    
    inputstr = b"AAAABBBBCCC@flare-on.com\x00\x00\x00\x00\x00\x00\x00\x00".ljust(128, b"\x00")
    user_input = []
    temp708 = binascii.unhexlify("31 dd 41 ea 5a 98 45 8f 8d 0c 00 43 71 a5 e7 39 60 15 2d 3a f0 5b 4a ef f1 a2 3f a5 c7 57 03 c1".replace(' ', '')).ljust(128, b"\x00")
    buf708 = []
    temp908 = binascii.unhexlify("4f d8 a9 eb 2a 5f 71 c3 13 ea 68 15 6b b1 fa b1 0d 77 a8 ae fa 92 ae ad e6 e1 a9 d5 47 34 cc d1".replace(' ', '')).ljust(128, b"\x00")
    buf908 = []
    temp_goal = binascii.unhexlify("eb 97 46 c0 48 6f 14 e4 51 3d 8e b1 eb 40 28 76 48 7a 08 4e ad fb ef fc 3a a2 ed e7 d4 c5 36 d0".replace(' ', '')).ljust(128, b"\x00")
    goal = []
    for i in range(8):
        buf708 += [u32(temp708[i*4:(i*4)+4])]
        buf908 += [u32(temp908[i*4:(i*4)+4])]
        user_input += [u32(inputstr[i*4:(i*4)+4])]
        goal += [u32(temp_goal[i*4:(i*4)+4])]
    buf708 += [0] * 120
    buf908 += [0] * 120
    user_input += [0] * 120
    
    def egcd(a, b):
        if a == 0:
            return (b, 0, 1)
        else:
            g, y, x = egcd(b % a, a)
            return (g, x - (b // a) * y, y)
    
    
    def modinv(a, m):
        g, x, y = egcd(a, m)
        if g != 1:
            raise Exception('modular inverse does not exist')
        else:
            return x % m
    
    mod_inv = modinv(buf2int(buf708), buf2int(buf908))
    solution_int = (mod_inv * buf2int(goal)) % buf2int(buf908)
    solution_hex = f'{solution_int:x}'
    solution = binascii.unhexlify(solution_hex)[::-1].decode()
    print(f'w3lc0mE_t0_Th3_l4nD_0f_De4th_4nd_d3strUct1oN_4nd{solution}')
    

This works, and reveals the flag:

    
    
    david@meeks:~/Dropbox/CTFs/flareon-2020/10-break$ python3 solve.py
    w3lc0mE_t0_Th3_l4nD_0f_De4th_4nd_d3strUct1oN_4nd_n0_puppi3s@flare-on.com
    

Running this as input to the original file does return success:

    
    
    david@meeks:~/Dropbox/CTFs/flareon-2020/10-break$ ./break-orig w3lc0mE_t0_Th3_l4nD_0f_De4th_4nd_d3strUct1oN_4nd_n0_puppi3s@flare-on.com
    welcome to the land of sunshine and rainbows!
    as a reward for getting this far in FLARE-ON, we've decided to make this one soooper easy
    
    please enter a password friend :) w3lc0mE_t0_Th3_l4nD_0f_De4th_4nd_d3strUct1oN_4nd_n0_puppi3s@flare-on.com
    hooray! the flag is: w3lc0mE_t0_Th3_l4nD_0f_De4th_4nd_d3strUct1oN_4nd_n0_puppi3s@flare-on.com
    

**Flag: w3lc0mE_t0_Th3_l4nD_0f_De4th_4nd_d3strUct1oN_4nd_n0_puppi3s@flare-
on.com**

[](/flare-on-2020/break)

