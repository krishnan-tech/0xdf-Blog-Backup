# Flare-On 2022: Pixel Poker

[flare-on](/tags#flare-on ) [ctf](/tags#ctf ) [flare-on-pixel-
poker](/tags#flare-on-pixel-poker ) [reverse-engineering](/tags#reverse-
engineering ) [direct-x](/tags#direct-x ) [ghidra](/tags#ghidra )
[x32dbg](/tags#x32dbg )  
  
Nov 11, 2022

  * [[1] Flaredle](/flare-on-2022/flaredle)
  * [2] Pixel Poker
  * [[3] Magic 8 Ball](/flare-on-2022/magic_8_ball)
  * [[4] darn_mice](/flare-on-2022/darn_mice)
  * [[5] T8](/flare-on-2022/t8)
  * [[6] à la mode](/flare-on-2022/alamode)
  * [[7] anode](/flare-on-2022/anode)
  * [[8] backdoor](/flare-on-2022/backdoor)
  * [[9] encryptor](/flare-on-2022/encryptor)
  * [[10] Nur geträumt](/flare-on-2022/nur_getraumt)
  * [[11] The challenge that shall not be named](/flare-on-2022/challenge_that_shall_not_be_named)

![pixel poker](https://0xdfimages.gitlab.io/img/flare2022-pixelpoker-
cover.png)

In Pixel Poker, I’ll reverse engineer a Windows Direct-X 11 application using
both Ghidra and x32dbg to find the correct pixel to click on. On clicking, it
returns a meme and the flag.

## Challenge

> I said you wouldn’t win that last one. I lied. The last challenge was
> basically a captcha. Now the real work begins. Shall we play another game?

The download contains a 32-bit Windows exe file:

    
    
    $ file PixelPoker.exe 
    PixelPoker.exe: PE32 executable (GUI) Intel 80386, for MS Windows
    

## Run It

In a Windows VM, I’ll run it, and it opens a window with a title bar, a menu
bar, and a main canvas with a bunch of pixels:

![image-20220930205857479](https://0xdfimages.gitlab.io/img/image-20220930205857479.png)

Under File, there’s an option of “I Give Up”, which exits the game. Under
Help, there’s “How To …” which opens a pop up:

![image-20220930205951339](https://0xdfimages.gitlab.io/img/image-20220930205951339.png)

Moving the mouse around the canvas, the pixel location is updated as
`(horizontal position, vertical position)`. Each time I click in the canvas,
the counter at the top advances:

![image-20220930210403587](https://0xdfimages.gitlab.io/img/image-20220930210403587.png)

If I click after it gets to 10/10, it pops a message:

![image-20220930210424373](https://0xdfimages.gitlab.io/img/image-20220930210424373.png)

Clicking OK exits the game.

## RE

### Identify Directx 11

I’ll start by finding the “Womp womp” string, which actually shows up in two
functions:

![image-20221003072203335](https://0xdfimages.gitlab.io/img/image-20221003072203335.png)

Stepping up the call tree, the second is actually two calls down from the
first. A few calls up, I’ll find this function at 0x401120:

    
    
    void __cdecl initWinClass(HINSTANCE param_1)
    
    {
      WNDCLASSEXW winClass;
      
      winClass.cbSize = 0x30;
      winClass.style = 3;
      winClass.lpfnWndProc = WndProc;
      winClass.cbClsExtra = 0;
      winClass.cbWndExtra = 0;
      winClass.hInstance = param_1;
      winClass.hIcon = LoadIconW(param_1,(LPCWSTR)0x6b);
      winClass.hCursor = LoadCursorW((HINSTANCE)0x0,(LPCWSTR)0x7f00);
      winClass.hbrBackground = (HBRUSH)0x6;
      winClass.lpszMenuName = (LPCWSTR)0x6d;
      winClass.lpszClassName = (LPCWSTR)&lpBuffer_004131b0;
      winClass.hIconSm = LoadIconW(winClass.hInstance,(LPCWSTR)0x6c);
      RegisterClassExW(&winClass);
      return;
    }
    

I’ve renamed the function and the `winClass` object, `WndProc`, and the
function itself, but the rest is already named.

In a strange case of beneficial typos, I googled “WINDCLASSEXW” (with an extra
“I” in “WIND”), and got [this article](https://blog.devgenius.io/using-
directx-11-for-games-part1-65a51fb91fe2) (that makes the same typo) titled
“Using DirectX11 for games: Part 1”. It was a very lucky find, because it
walks through the structure of a DirectX11 application, which is what this
game is.

For example, from the post:

![image-20221003074622176](https://0xdfimages.gitlab.io/img/image-20221003074622176.png)

This looks very much like what I have above.

### CreateWindow

After the `initWinClass` call, the `hInstance` object is passed to a function
I named `CreateWindow` (0x401040). This function gets a buffer the size of
size `DAT_00413284 * DAT_00413280 * 4`. Given that colors can be stored in
4-bytes per pixel, and I know we’re looking at a grid of pixels, it makes
sense to think these are the `MAX_X` and `MAX_Y` values.

### WndProc

In that initWinClass function, it sets the `winClass.lpfnWndProc` to the
address of a function at 0x4012c0 that I’ll rename to `WinProc` to match
what’s in the post above.

From the post:

> We’re also passing a pointer to a function called _WndProc_ seen in the line
> _winClass.lpfnWndProc = &WndProc;_

![img](https://0xdfimages.gitlab.io/img/1GQYxyZyhX94j_x9re0d2Kw.png)

> WndProc Callback handles out input events
>
> This is the callback that handles events sent to our app like resizing,
> keyboard input, and exiting our program. We have to define it ourselves, so
> we’ll do that above our main function.

The example in the post shows this function taking four parameters, and then
doing a `switch` on `msg` to handle different kinds of events:

    
    
    LRESULT CALLBACK WndProc(HWND hwnd, UINT msg, WPARAM wparam, LPARAM lparam)
    {
        LRESULT result = 0;
        switch(msg) {
            case WM_KEYDOWN: {
                if(wparam == VK_ESCAPE)
                    PostQuitMessage(0);
                break;
            }
            case WM_DESTROY: {
                PostQuitMessage(0);
            } break;
            default:
                result = DefWindowProcW(hwnd, msg, wparam, lparam);
        }
        return result;
    }
    

The `WndProc` in `PixelPoker.exe` looks similar. I’ll rename/retype the
variables to match. This one doesn’t decompile to a `switch`, but a bunch of
`if` / `else`. I’ll use Equates in Ghidra to set the constants to names, and
towards the bottom I’ll find the code for `msg == WM_LBUTTONDOWN` (for left
button down):

    
    
        if (msg == WM_LBUTTONDOWN) {
          xcoord = (uint)(short)lparam;
          ycoord = (uint)(short)((uint)lparam >> 0x10);
          if (CLICK_COUNTER == 10) {
            MessageBoxA((HWND)0x0,"Womp womp... :(","Please play again!",0);
            DestroyWindow(hwnd);
          }
          else {
            CLICK_COUNTER = CLICK_COUNTER + 1;
            if ((xcoord == s_FLARE-On_00412004._0_4_ % (uint)MAX_X) &&
               (ycoord == s_FLARE-On_00412004._4_4_ % (uint)MAX_Y)) {
              if (0 < MAX_Y) {
                CVar5 = 0;
                iVar3 = MAX_X;
                iVar4 = MAX_Y;
                do {
                  ycoord = 0;
                  if (0 < iVar3) {
                    do {
                      FUN_004015d0(ycoord,CVar5);
                      ycoord = ycoord + 1;
                      iVar3 = MAX_X;
                      iVar4 = MAX_Y;
                    } while ((int)ycoord < MAX_X);
                  }
                  CVar5 = CVar5 + 1;
                } while ((int)CVar5 < iVar4);
              }
            }
            else if ((xcoord < (uint)MAX_X) && (ycoord < (uint)MAX_Y)) {
              FUN_004015d0(xcoord,ycoord);
            }
          }
    

The [docs](https://learn.microsoft.com/en-us/windows/win32/inputdev/wm-
lbuttondown) on `WM_LBUTTONDOWN` show that this is getting the x and y
coordinate from the `lparam`, and checking if the global I’ve named
`CLICK_COUNTER` is equal to 10 (if so, print “Womp womp” and `DestroyWindow`).
Otherwise, it increments `CLICK_COUNTER` and then checks if x and y are some
specific values:

![image-20220930215955438](https://0xdfimages.gitlab.io/img/image-20220930215955438.png)

`s_FLARE-On_00412004` is a global, named by Ghidra, that’s initialized to
“FLARE-On”. If I can figure out what `MAX_X` and `MAX_Y` are, I’ll know the
pixel to click.

### Debug

I’ll open `x32dbg` and set a breakpoint at 0x401477, where it is loading
“FLAR” into EAX to compare. I’ll run until the program is running, and then
click somewhere in the pixels. The breakpoint is hit:

[![image-20221003084103345](https://0xdfimages.gitlab.io/img/image-20221003084103345.png)_Click
for full size
image_](https://0xdfimages.gitlab.io/img/image-20221003084103345.png)

Stepping forward two to 0x401482, it’s loaded 0x52414C46 (“RALF”) into EAX,
and 0x2e5 into ESI. 0x2e5 = 741 must be `MAX_X`, which makes sense as when I
move my cursor to the far left hand side of the image, the title bar goes up
to 740 as the first coordinate:

![image-20221003084343151](https://0xdfimages.gitlab.io/img/image-20221003084343151.png)

Stepping once more, the `div` instruction stores the result of the division in
EAX, with the remainder in EDX, which is what I need. That reads 0x5F, or 95.

Because I just clicked on a random pixel, this check fails. I’ll click again,
this time making sure the x coordinate is 95.

This time the jump is not taken, and I get to where “nO-E” is loaded into EAX,
and divided by 0x281, or 641. The remainder this time is 0x139, or 313.

When I click on pixel 95, 313, the flag is shown:

![image-20220930220040448](https://0xdfimages.gitlab.io/img/image-20220930220040448.png)

**Flag: w1nN3r_W!NneR_cHick3n_d1nNer@flare-on.com**

[](/flare-on-2022/pixel_poker)

