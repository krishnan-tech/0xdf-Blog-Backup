# Flare-On 2020: Aardvark

[flare-on](/tags#flare-on ) [ctf](/tags#ctf ) [flare-on-aardvark](/tags#flare-
on-aardvark ) [reverse-engineering](/tags#reverse-engineering )
[wsl](/tags#wsl ) [ghidra](/tags#ghidra ) [resource-hacker](/tags#resource-
hacker ) [process-hacker](/tags#process-hacker ) [gdb](/tags#gdb )
[peda](/tags#peda ) [pwndbg](/tags#pwndbg )  
  
Nov 1, 2020

  * [[1] Fidler](/flare-on-2020/fidler)
  * [[2] garbage](/flare-on-2020/garbage)
  * [[3] wednesday](/flare-on-2020/wednesday)
  * [[4] report.xls](/flare-on-2020/report)
  * [[5] TKApp](/flare-on-2020/tkapp)
  * [[6] CodeIt](/flare-on-2020/codeit)
  * [[7] RE Crowd](/flare-on-2020/recrowd)
  * [8] Aardvark
  * [[9] crackinstaller](/flare-on-2020/crackinstaller)
  * [[10] break](/flare-on-2020/break)

![aardvark](https://0xdfimages.gitlab.io/img/flare2020-aardvark-cover.png)

Aardvark was a game of tik-tac-toe where the computer always goes first, and
can’t lose. Instead of having the decision logic of the computer in the
program, it drops an ELF binary to act as the computer, and communicates with
it over a unix socket, all of which is possible on Windows with the Windows
Subsystem for Linux (WSL). Once I understand how the computer is playing, I’ll
modify the computers logic so that I can win, and get the flag. I’ll play with
different ways to patch the binary, starting manually with gdb, and moving to
patching the ELF resource a couple different ways.

## Challenge

> Expect difficulty running this one. I suggest investigating why each error
> is occuring. Or not, whatever. You do you.

The file is a 64-bit Windows exe:

    
    
    root@kali# file ttt2.exe 
    ttt2.exe: PE32+ executable (GUI) x86-64, for MS Windows
    

## Running It

### Errors

Given the prompt, I was a bit surprised when the binary ran without issue on
my VM. I happened to already have some of the necessary configurations in
place. I made a clean VM and run it, and got this error:

![image-20201029155944789](https://0xdfimages.gitlab.io/img/image-20201029155944789.png)

The [doc](https://docs.microsoft.com/en-us/windows/win32/api/combaseapi/nf-
combaseapi-cocreateinstance) don’t make the purpose of this function
immediately clear to me. It largely depends on the GUIDs passed into the call.
Firing up Ghidra, there are four calls to `CoCreateInstance`:

![image-20201029161339539](https://0xdfimages.gitlab.io/img/image-20201029161339539.png)

Each call is the same (except for the output buffer):

    
    
    CoCreateInstance((IID *)GUID_14001e008,(LPUNKNOWN)0x0,4,(IID *)GUID_14001e018,&local_288);
    

I tell Ghidra to treat the buffers at 0x14001e008 and 0x14001e018 as GUIDs and
get their values:

![image-20201029161608453](https://0xdfimages.gitlab.io/img/image-20201029161608453.png)

Googling for those GUIDs finds a couple links that don’t necessarily say
what’s going on, but that give hints:

  * [GitHub Issue about bash on Windows for Windows OpenSSH](https://github.com/PowerShell/Win32-OpenSSH/issues/289)
  * [GitHub Issue in the WSL repo](https://github.com/Microsoft/WSL/issues/2968)

The second has an error log that mentions the `LxssManager`, which is a part
of the Windows Subsystem for Linux (WSL).

I’ll go into “Enable Windows Features” and turn on WSL. After a reboot, the
error message is different:

![image-20201029162435215](https://0xdfimages.gitlab.io/img/image-20201029162435215.png)

I [downloaded a distribution](https://docs.microsoft.com/en-
us/windows/wsl/install-manual) and installed it:

    
    
    PS > IWR -Uri https://aka.ms/wslubuntu2004 -outfile ubuntu.appx -UseBasicParsing
    PS > Add-AppxPackage .\ubuntu.appx
    

Then I opened the ubuntu app, and it installed and set up a user. Now when I
run `ttt2.exe`, it works.

### Successfully

When the program runs, it displays a game of Tik-Tak-Toe:

![image-20200929072144295](https://0xdfimages.gitlab.io/img/image-20200929072144295.png)

I can play the game, but the computer always goes first, and at best I can get
a draw.

![image-20200929072232985](https://0xdfimages.gitlab.io/img/image-20200929072232985.png)

If I click on a space that’s already taken, another box pops up:

![image-20200929072259352](https://0xdfimages.gitlab.io/img/image-20200929072259352.png)

## RE ttt2.exe

### FUN_1400015a0 / main

#### Finding main

I started by looking for a known string, “Invalid Move”, and finding a single
reference to it, at 0x140001213, which is in `FUN_140001000` in Ghidra. Before
diving in on this function, I looked for references to it. Two of the
references that return are in the EXE headers, but the third is in a function:

![image-20200930134854714](https://0xdfimages.gitlab.io/img/image-20200930134854714.png)

Interestingly, that third isn’t the function being called, but rather
referenced. That function that loads the address of `FUN_140001000` is
`FUN_1400015a0`, which I’ll refer to as `main()`.

#### Four Parts of main

`main()` takes care of a few things for the program. It’s all a bit jumbled
together, but I’ll try to show it grouped:

1) Sets the current working directory to the running user’s
`%APPDATA%\local\temp` directory by calling `GetTempPathA` and then passing
the result to `SetCurrentDirectoryA`.

2) Creates the console using `AllocConsole`, and then `GetConsoleWindow` to
get handle. It then calls `ShowWindow` to make it visible, and eventually
`CreateDialogParamA` to create the board:

    
    
    hWnd = CreateDialogParamA((HINSTANCE)hInstance,"BOARD",(HWND)0x0,FUN_140001000,0);
    

[This function](https://docs.microsoft.com/en-us/windows/win32/api/winuser/nf-
winuser-createdialogparama) takes a template resource and a handle to a window
to create a “modeless dialog box”. `BOARD` is a reference to the resource
template that defines the dialog box. Resource Hacker shows a resource named
BOARD that has this template:

![image-20200930141345896](https://0xdfimages.gitlab.io/img/image-20200930141345896.png)

The fourth parameter is `DLGPROC lpDialogFunc`, which [the
docs](https://docs.microsoft.com/en-us/windows/win32/api/winuser/nc-winuser-
dlgproc) show take a handle to the box, a `message`, and then additional
message-specific information.

3) Creates a UNIX socket in the `temp` directory named `496b9b4b.ed5`. There’s
a call to `socket(1, 1, 0)`. The first input to socket is the family. Most
[Windows documentation](https://docs.microsoft.com/en-
us/windows/win32/api/winsock2/nf-winsock2-socket) of `socket` don’t mention
the value 1, because it’s a UNIX socket ( `AF_UNIX` or `AF_LOCAL`). But with
WSL, this works. It later calls `bind` on the filename, and then `listen` and
`accept`, storing the accepted socket in a global variable that will be read
from and written to in other functions.

4) Fetches an ELF file from the PE’s resources and saves it as a random name
in the same `temp` directory. This is all done in a call to `FUN_1400012b0`,
which I’ll look at more in depth.

### FUN_140001000

Looking at `FUN_140001000`, it’s doing different things based on `param2`,
which is the `DLGPROC lpDialogFunc` ([docs](https://docs.microsoft.com/en-
us/windows/win32/api/winuser/nc-winuser-dlgproc)). This must have something to
do with what was clicked in the GUI. I tried putting break point at the top of
the function, but it is hit a ton. Eventually by putting difference break
points inside different sections, I was able to determine that `param2 ==
0x111` was triggered when clicking on one of the boxes in board.

    
    
    if (param_2 == 0x111) {
        column = (uint)message & 0xf;
        row = (uint)(message >> 4) & 0xf;
        index = (ulonglong)row * 3 + (ulonglong)column;
        if ((&square_values)[index] == ' ') {
            coordinates[0] = (byte)row;
            coordinates[1] = (byte)column;
            (&square_values)[index] = 0x4f;
            send(s,(char *)coordinates,2,0);
            recv(sock,&square_values,10,0);
            update_board(param_1);
            if (winner != '\0') {
                recv(sock,msgbuf,0x40,0);
                MessageBoxA(param_1,msgbuf,"Game Over",0);
                clear_grid();
                update_board(param_1);
            }
        }
        else {
            MessageBoxA(param_1,"That space is already taken","Invalid Move",0);
        }
    }
    

That makes sense as a the “This space is already take” string is also in this
section.

I’ve renamed `param3` as `message`, and this seems to be the ID of the box
from the template shown above, which will look like:

256| 257| 258  
---|---|---  
272| 273| 274  
288| 289| 290  
  
This is convenient because in hex this looks like:

0x100| 0x101| 0x102  
---|---|---  
0x110| 0x111| 0x112  
0x120| 0x121| 0x122  
  
That means that the column number is the `message & 0xf`, and that the row
number is `(message >> 4) & 0xf`, which is what’s done above. It then creates
an index as `3*row + column`.

It then checks a data structure which is a ten character string, which I’ve
named `square_values` above. It uses `X`, `O`, and `[space]` to represent the
squares on the grid. The tenth value, initialized to null and pointed to by
the variable I’ve named `winner` above, is set when someone wins, or when
there’s a draw (set to 0xff).

If the clicked value is not space, it prints a message box and continues.
Otherwise, it writes an `O` (0x4f) into the right place in `squarevalues`, and
then writes two bytes to the UNIX socket initialized in `main`. The two bytes
are just the row and column. Then it reads 10 bytes out of that socket, and
writes it into `square_values`. This updated state contains the next move by
the computer, and any chances necessary to the game over byte. If the game
over byte is non-null, it calls `recv` again, and gets the body for the
message box to display. I suspect if I can win a game, I’ll get the flag back
over the socket here.

### FUN_1400012b0 and Children

#### Write ELF

Back in `main` there was a call to this function, and it is worth additional
scrutiny.

First it makes a call to `GetTempFileName`, which it passes to `CreateFileA`
to get a handle to a new random filename which is 1-4 hex characters `.tmp` in
the `temp` directory.

It then calls `FindResourceA`:

    
    
    hResInfo = FindResourceA((HMODULE)0x0,(LPCSTR)0x12c,(LPCSTR)0x100);
    

The [docs](https://docs.microsoft.com/en-us/windows/win32/api/winbase/nf-
winbase-findresourcea) show that the last parameter is the type, which can be
an integer id, and the second to last is the name, which can also be an
integer id. So this is looking for a resource of type 0x100 (256) and id 0x12c
(300). Resource Hacker shows not only that that resource exists, but also that
it’s an ELF:

![image-20200930150926355](https://0xdfimages.gitlab.io/img/image-20200930150926355.png)

The contents of the resource are loaded with `LoadResource` and then written
to the temp file using `WriteFile`.

I saved a copy with resource hacker, and looked at the temp file while
debugging, and they are the same:

    
    
    PS C:\Users\0xdf> Get-FileHash .\AppData\Local\Temp\A1.tmp
    
    Algorithm       Hash                                                                   Path
    ---------       ----                                                                   ----
    SHA256          06EE06846D1DE1897BA70315CCA3AB5181949DE1484CE31BC5F3A08610A2C509       C:\Users\0xdf\AppData\Local\T...
    
    
    PS C:\Users\0xdf> Get-FileHash F:\08-Aardvark\256300.elf
    
    Algorithm       Hash                                                                   Path
    ---------       ----                                                                   ----
    SHA256          06EE06846D1DE1897BA70315CCA3AB5181949DE1484CE31BC5F3A08610A2C509       F:\08-Aardvark\256300.elf
    

#### Run ELF

Finally, the function makes a call to `FUN_140001930`, which is a call to
`GetVersionExA`, and then a series of checks to figure out what OS is running.
If the OS Windows 10 1803 or later, it calls `FUN_1400021e0`.

`FUN_1400021e0` uses `CoCreateInstance` and series of other API calls to
create a COM object which is used to call into WSL to start the process.

    
    
      HVar2 = CoCreateInstance((IID *)&DAT_14001e008,(LPUNKNOWN)0x0,4,(IID *)&DAT_14001e018,&local_2d0);
      if (HVar2 == 0) {
        iVar3 = (**(code **)(*local_2d0 + 0x58))(local_2d0,&local_290);
        if (iVar3 == 0) {
          local_2d8[0] = 0;
          local_2c8 = (LPVOID)0x0;
          iVar3 = (**(code **)(*local_2d0 + 0x68))(local_2d0,local_2d8,&local_2c8);
          if (iVar3 == 0) {
            if (local_2d8[0] != 0) {
              do {
                lVar6 = uVar5 * 0x1c;
                if (((*(longlong *)(lVar6 + (longlong)local_2c8) == local_290) &&
                    (*(longlong *)(lVar6 + 8 + (longlong)local_2c8) == local_288)) &&
                   (*(int *)(lVar6 + 0x14 + (longlong)local_2c8) != 1)) {
                  MessageBoxA((HWND)0x0,"Default distribution must be WSL 1","Error",0x10);
                  goto LAB_14000246f;
                }
                uVar4 = (int)uVar5 + 1;
                uVar5 = (ulonglong)uVar4;
              } while (uVar4 < local_2d8[0]);
            }
            if (local_2c8 != (LPVOID)0x0) {
              CoTaskMemFree(local_2c8);
            }
    ...[snip]...
            uVar1 = *(undefined8 *)
                     (*(longlong *)(*(longlong *)(*(longlong *)(in_GS_OFFSET + 0x30) + 0x60) + 0x20) +
                     0x10);
            GetCurrentDirectoryW(0x105,local_248);
    ...[snip]...
            iVar3 = (**(code **)(*local_2d0 + 0x70))(local_2d0,&local_290,param_1,(ulonglong)param_2);
            if (iVar3 != 0) {
              MessageBoxA((HWND)0x0,"CreateLxProcess failed","Error",0x10);
            }
          }
          else {
            MessageBoxA((HWND)0x0,"EnumerateDistributions failed","Error",0x10);
          }
        }
        else {
          MessageBoxA((HWND)0x0,"GetDefaultDistribution failed","Error",0x10);
        }
      }
      else {
        MessageBoxA((HWND)0x0,"CoCreateInstance failed","Error",0x10);
      }
    

Just looking at the error messages at the bottom provides a good hint as to
what it’s trying to do. The creation of the process happens at this line:

    
    
    iVar3 = (**(code **)(*local_2d0 + 0x70))(local_2d0,&local_290,param_1,(ulonglong)param_2);
    

I stepped through this debugging with Process Hacker open, and on stepping,
two new processes were created under `svchost.exe`:

![image-20200929125510301](https://0xdfimages.gitlab.io/img/image-20200929125510301.png)

Looking at the details, it’s the temp file:

![image-20200929125550813](https://0xdfimages.gitlab.io/img/image-20200929125550813.png)

## RE ELF

### Loading Into Ghidra

For whatever reason, this program doesn’t load into Ghidra nicely. The
functions are all API calls stubs, and even `entry` calls `__libc_start_main`
which didn’t process:

![image-20200930172302342](https://0xdfimages.gitlab.io/img/image-20200930172302342.png)

I’ll select the `.text` section from the Program Trees window on the top left,
and see it’s treating that data as data, not code:

![image-20200930172524961](https://0xdfimages.gitlab.io/img/image-20200930172524961.png)

First I’ll right-click on the 00100ac0 address and select Disassemble [D], and
then right-click and select Create Function [F]. It will create the function,
as well as any other functions called by this function.

Interestingly, I was able to open it in IDA Pro Free, and it didn’t have any
issue with the file, and there’s a `main` function at that same 0xac0 offset:

![image-20200930172355348](https://0xdfimages.gitlab.io/img/image-20200930172355348.png)

### main

The main function starts with some setup, connecting to the unix socket,
creating the ten-byte squares structure. Then it enters a `do` loop, which
serves two functions:

  1. Call a function I named `checkForWin()` (0x001014b0). This function looks for rows that have three the same, then columns, then diagonals. If it finds any match, it returns that character. If it finds all the squares are full but no win, it returns -1. Otherwise, it returns 0.
  2. If the win flag is still null. 
    1. If not, it decodes a message depending on which game over condition (X wins, O wins, draw) and resets the state of the game to fresh.
    2. If so, it runs a series of checks to determine the next move for the computer, X. It updates the board, sends the updated game state back into the socket, and checks again for a win (if so jumping into the code from above).
  3. Then it waits to read the next move from the socket. It ignores the move is the user is trying to move to an already occupied space, and otherwise updates the game state with a new `O`, checks for a win, and then heads back to the start of the loop.

At this point, I had two options:

  1. Look at understanding the computer’s next move, with the hopes of finding a way to beat it; or
  2. Try to understand the flag decode.

The flag decode looked complicated. It is super long (even the decompiled
source in Ghidra), and involves reading from `/proc/modules` and `/proc/mount`
and processing the results). I decided to start with the next move.

This code starts at 0x100bc6. There are some global variables pointing to each
of the squares. I named then `sq1` \- `sq9` for readability, where 1, 2, 3 go
across the top row.

  * If `sq5` (center) is empty, choose it.
    
        if (sq5 == ' ') {
        next_col = 1;
        next_row = 1;
    }
    

  * Loop over the rows, and if any row has exactly two Os in it, pick the other square in that row.
    
        next_row = 0;
    squares2 = &squares;
    current_row = &squares;
    do {
        next_col = (uint)(current_row[2] == 'O') +
            (uint)(current_row[1] == 'O') + (uint)(*current_row == 'O');
        if (next_col == 2) {
            if (*current_row == ' ') goto LAB_00100cc8;   // select first column in current row
            if (current_row[1] == ' ') goto LAB_00100e40; // select second column in current row
            if (current_row[2] == ' ') goto LAB_00100cd0; // select third column in current row
        }
        next_row = next_row + 1;
        current_row = current_row + 3;
    } while (next_row != 3);
    

  * Loop over the columns, and if any column has exactly two Os, pick the other squre in that column.
    
        current_row = &squares;
    next_col = 0;
    do {
        next_row = (uint)(current_row[6] == 'O') +
            (uint)(current_row[3] == 'O') + (uint)(*current_row == 'O');
        if (next_row == 2) {
            if (*current_row == ' ') goto LAB_00100e15;
            if (current_row[3] == ' ') goto LAB_00100dcd;
            if (current_row[6] == ' ') goto LAB_00100cd0;
        }
        next_col = next_col + 1;
        current_row = current_row + 1;
    } while (next_col != 3);
    

  * If sq1 is open, pick it.

  * If sq3 is open, pick it.

  * If sq7 is open, pick it.

  * If sq9 is open, pick it.

  * This loop that will end up (of the remaining squares) picking a square in this order: sq2, sq4, sq6, then sq8.

I spent a few minutes evaluating that logic for flaws, but with X going first
and that gameplay, I don’t believe X can lose using this logic.

### Cheat

#### Setup

At this point, my options were to dive in on the flag decryption, or try to
cheat the computer.

I fired up a Bash window, ran `sudo su` to get a root shell. I updated the
machine (`apt update` and `apt upgrade`), and installed `gdb` (`apt install
gdb`). I installed [Peda](https://github.com/longld/peda), and it mostly
worked, but failed to show me the upcoming commands inside non-library code.
For example:

    
    
    [----------------------------------registers-----------------------------------]
    RAX: 0x2
    RBX: 0x7f84f4c020a0 ("    X    ")
    RCX: 0x0
    RDX: 0x2
    RSI: 0x7f84f4c020aa --> 0x201
    RDI: 0x3
    RBP: 0x7f84f4c020a0 ("    X    ")
    RSP: 0x7fffc9e967a0 --> 0x7fffc9e967d0 --> 0x0
    RIP: 0x7f84f4a00d24
    R8 : 0x0
    R9 : 0x0
    R10: 0x0
    R11: 0x0
    R12: 0x7f84f4c020aa --> 0x201
    R13: 0x7fffc9e96a10 --> 0x1
    R14: 0x0
    R15: 0x0
    EFLAGS: 0x203 (CARRY parity adjust zero sign trap INTERRUPT direction overflow)
    [-------------------------------------code-------------------------------------]
    Invalid $PC address: 0x7f84f4a00d24
    [------------------------------------stack-------------------------------------]
    0000| 0x7fffc9e967a0 --> 0x7fffc9e967d0 --> 0x0
    0008| 0x7fffc9e967a8 --> 0x7fffc9e967d8 --> 0x0
    0016| 0x7fffc9e967b0 --> 0x0
    0024| 0x7fffc9e967b8 --> 0x7fffc9e96850 --> 0x0
    0032| 0x7fffc9e967c0 --> 0x0
    0040| 0x7fffc9e967c8 --> 0x0
    0048| 0x7fffc9e967d0 --> 0x0
    0056| 0x7fffc9e967d8 --> 0x0
    [------------------------------------------------------------------------------]
    Legend: code, data, rodata, value
    
    Breakpoint 1, 0x00007f84f4a00d24 in ?? ()
    gdb-peda$
    

So I switched to [pwndbg](https://github.com/pwndbg/pwndbg), and it worked
better:

    
    
    ────────────────────────────────────────────────[ REGISTERS ]────────────────────────────────────────────────
    *RAX  0x2
     RBX  0x7f0df1c020a0 ◂— '    X    '
     RCX  0x0
     RDX  0x2
     RDI  0x3
     RSI  0x7f0df1c020aa ◂— 0x201
     R8   0x0
     R9   0x0
     R10  0x0
     R11  0x0
     R12  0x7f0df1c020aa ◂— 0x201
     R13  0x7ffff54f7300 ◂— 0x1
     R14  0x0
     R15  0x0
     RBP  0x7f0df1c020a0 ◂— '    X    '
    *RSP  0x7ffff54f7090 —▸ 0x7ffff54f70c0 ◂— 0x0
    *RIP  0x7f0df1a00d24 ◂— movsx  rdx, byte ptr [r12] /* 0xbe0f482414be0f49 */
    ─────────────────────────────────────────────────[ DISASM ]──────────────────────────────────────────────────
     ► 0x7f0df1a00d24    movsx  rdx, byte ptr [r12]
       0x7f0df1a00d29    movsx  rcx, byte ptr [rip + 0x20137a]
       0x7f0df1a00d31    lea    rax, [rdx + rdx*2]
       0x7f0df1a00d35    add    rax, rbx
       0x7f0df1a00d38    add    rax, rcx
       0x7f0df1a00d3b    cmp    byte ptr [rax], 0x20
       0x7f0df1a00d3e    jne    0x7f0df1a00bac <0x7f0df1a00bac>
    
       0x7f0df1a00d44    mov    byte ptr [rax], 0x4f
       0x7f0df1a00d47    call   0x7f0df1a014b0 <0x7f0df1a014b0>
    
       0x7f0df1a00d4c    test   al, al
       0x7f0df1a00d4e    mov    byte ptr [rip + 0x201355], al
    ──────────────────────────────────────────────────[ STACK ]──────────────────────────────────────────────────
    00:0000│ rsp  0x7ffff54f7090 —▸ 0x7ffff54f70c0 ◂— 0x0
    01:0008│      0x7ffff54f7098 —▸ 0x7ffff54f70c8 ◂— 0x0
    02:0010│      0x7ffff54f70a0 ◂— 0x0
    03:0018│      0x7ffff54f70a8 —▸ 0x7ffff54f7140 ◂— 0x0
    04:0020│      0x7ffff54f70b0 ◂— 0x0
    ... ↓
    ────────────────────────────────────────────────[ BACKTRACE ]────────────────────────────────────────────────
     ► f 0     7f0df1a00d24
       f 1     7f0df16d70b3 __libc_start_main+243
    ─────────────────────────────────────────────────────────────────────────────────────────────────────────────
    pwndbg>
    

#### Strategy

I decided to cheat just simply by adjusting the computers moves. Using the
logic I worked out above, I’m going to disable the second check, for a row
with exactly two `O` in it:

    
    
    next_row = 0;
    squares2 = &squares;
    current_row = &squares;
    do {
        num_os = (uint)(current_row[2] == 'O') +
            (uint)(current_row[1] == 'O') + (uint)(*current_row == 'O');
        if (num_os == 2) {
            if (*current_row == ' ') goto LAB_00100cc8;   // select first column in current row
            if (current_row[1] == ' ') goto LAB_00100e40; // select second column in current row
            if (current_row[2] == ' ') goto LAB_00100cd0; // select third column in current row
        }
        next_row = next_row + 1;
        current_row = current_row + 3;
    } while (next_row != 3);
    

Once that happens, the computer will ignore when I have two Os in a row.
Without that rule, it’s priority will be the top two corners, which will give
me enough time to get a tic-tac-toe across the bottom.

#### Win

I’ll disable the row check by changing the check looking for two `O` to
looking for four `O` (which will never happen). The assembly currently is:

    
    
            00100c07 83 fa 02        CMP        num_os,0x2
    

I’ll need to update that address for the ASLR, but I can do that by looking at
any instruction pointer inside this function and just changing the last three
nibbles. The `cmp` instruction above is `0x83fa02`. Without looking at the
docs I can guess that the third byte is what is being compared. I’ll change
it:

    
    
    pwndbg> set *(unsigned char*)0x7f0df1a00c09 = 0x04
    

Now I’ll tell `gdb` to `c` and play:

Move| Result  
---|---  
Initial Board| ![](../img/image-20201001070034832.png)  
Bottom Left| ![](../img/image-20201001070058272.png)  
Bottom Right| ![](../img/image-20201001070121549.png)  
Bottom Center| ![](../img/image-20201001070148539.png)  
  
There’s no X move after my last play because I’ve won, and the message box
provides the flag:

![image-20200930061058936](https://0xdfimages.gitlab.io/img/image-20200930061058936.png)

**Flag: c1ArF/P2CjiDXQIZ@flare-on.com**

This flag almost ruined the challenge here. It’s really poor form to have a
gibberish flag, when all the rest were leet speak. It made me think at first
that I didn’t have the right flag. It’s part of the challenge that would waste
people’s time without any benefit.

## Automating

### gdb

In playing with this, I thought it’d be interesting to write a single Bash
one-liner that started `gdb`, changed the byte I wanted changed, and then let
it run. I came up with this:

    
    
    pid=$(ps auxww | grep tmp | head -1 | awk '{print $2}'); base=$(cat /proc/$pid/maps | grep tmp | head -1 | cut -d- -f1 | rev | cut -c4- | rev); gdb -p $pid -ex "set *(unsigned char*)0x${base}c09 = 0x04" -ex c
    

That’s three commands. First, it gets the pid of the tmp process by running
`ps auxww` into `grep`, `head`, and `awk`.

    
    
    pid=$(ps auxww | grep tmp | head -1 | awk '{print $2}');
    

Next, it gets the base memory address by looking in `/proc/[pid]/maps`,
finding the start of the .text section, and dropping the last three bytes.

    
    
    base=$(cat /proc/$pid/maps | grep tmp | head -1 | cut -d- -f1 | rev | cut -c4- | rev);
    

Finally, it calls `gdb` to attach to that process, and run two commands on
start. First, the command to dork the compare breaking the “don’t let there be
three in a row” check using that `$base` to get the right address. Then `c`
for continue.

    
    
    gdb -p $pid -ex "set *(unsigned char*)0x${base}c09 = 0x04" -ex c
    

So now I can start `ttt2.exe`, run that line in Bash, and then click on bottom
left, bottom right, bottom center, and get flag.

### Modifying Resource

In writing the previous section, I thought, why even open `gdb`? What if I
just edit the dropped ELF to start with three Os in a win?

I found the instructions in the ELF where the state was initialized:

    
    
            00100b98 48 b8 20        MOV        RAX,0x2020202020202020
                     20 20 20 
                     20 20 20 20
            00100ba2 48 89 03        MOV        qword ptr [RBX]=>DAT_003020a0,RAX                = ??
            00100ba5 c6 05 fc        MOV        byte ptr [DAT_003020a8],0x20                     = ??
                     14 20 00 20
    

I opened up a hex editor, and changed that first line to `MOV RAX,
0x4F4F4F2020202020`, which should set the first row to all Os. I then used
Resource Hacker to replace the ELF resource with this modified version, and
ran it:

![image-20201001163315192](https://0xdfimages.gitlab.io/img/image-20201001163315192.png)

It looked good, so I clicked a square. I get a message box with a flag, but
it’s not the right flag, and the board is now all jacked:

![image-20201001163401675](https://0xdfimages.gitlab.io/img/image-20201001163401675.png)

However, I found if I set it so that I didn’t win at the start, but also
couldn’t lose, it would give the right flag. Modifying the resource like this
so that three `O` were on the starting board did work:

![image-20201029171556764](https://0xdfimages.gitlab.io/img/image-20201029171556764.png)

On replacing the ELF resource with the modified version, I start with an
advantage:

![image-20201029171750830](https://0xdfimages.gitlab.io/img/image-20201029171750830.png)

From there, I can just win:

![image-20201029171812775](https://0xdfimages.gitlab.io/img/image-20201029171812775.png)

### Patch Strategy

I was also able to make the same change I made above. I opened a copy of the
ELF in a hex editor and searched for `83 fa 02`, and changed the `02` to `04`.
Then I saved it. In Resource Hacker, I found the resource, went to Action –>
Replace Resource, and selected the modified ELF (it had to be named with a
`.bin` extension). After saving, I can run the modified version, and X won’t
try to stop my tic-tac-toe across the bottom just like above, this time
without `gdb`.

[](/flare-on-2020/aardvark)

