# Flare-On 2020: CodeIt

[flare-on](/tags#flare-on ) [ctf](/tags#ctf ) [flare-on-codeit](/tags#flare-
on-codeit ) [reverse-engineering](/tags#reverse-engineering )
[autoit](/tags#autoit ) [exe2aut](/tags#exe2aut ) [upx](/tags#upx )
[myauttoexe](/tags#myauttoexe ) [script-obfuscation](/tags#script-obfuscation
) [crypto](/tags#crypto )  
  
Oct 29, 2020

  * [[1] Fidler](/flare-on-2020/fidler)
  * [[2] garbage](/flare-on-2020/garbage)
  * [[3] wednesday](/flare-on-2020/wednesday)
  * [[4] report.xls](/flare-on-2020/report)
  * [[5] TKApp](/flare-on-2020/tkapp)
  * [6] CodeIt
  * [[7] RE Crowd](/flare-on-2020/recrowd)
  * [[8] Aardvark](/flare-on-2020/aardvark)
  * [[9] crackinstaller](/flare-on-2020/crackinstaller)
  * [[10] break](/flare-on-2020/break)

![codeit](https://0xdfimages.gitlab.io/img/flare2020-codeit-cover.png)

The sixth Flare-On7 challenge was tricky in a way that’s hard to put on the
page. It really was just a AutoIt script wrapped in a Windows exe. I’ll use a
tool to revert it back to a large, obfuscated script, and then get to work
deobfuscating it. Eventually I’ll see that it is looking for a specific
hostname, and on switching my hostname to match, I get a QRcode that contains
the flag.

## Challenge

> Reverse engineer this little compiled script to figure out what you need to
> do to make it give you the flag (as a QR code).

The file contains a Windows 32-bit executable, UPX packed:

    
    
    $ file codeit.exe 
    codeit.exe: PE32 executable (GUI) Intel 80386, for MS Windows, UPX compressed
    

## Running It

Running it pops a prompt with a text field, a button, and an image:

![image-20200922143542381](https://0xdfimages.gitlab.io/img/image-20200922143542381.png)

On entering some text and hitting the button, it replaces the image with a
QRcode:

![image-20200922144930694](https://0xdfimages.gitlab.io/img/image-20200922144930694.png)

The QR code decodes to the entered text.

## Get AutoIt Script

### Identify AutoIT

As it is UPX packed, I’ll unpack it:

    
    
    $ upx -d codeit.exe -o codeit-unpack.exe
                           Ultimate Packer for eXecutables
                              Copyright (C) 1996 - 2020
    UPX 3.96        Markus Oberhumer, Laszlo Molnar & John Reiser   Jan 23rd 2020
    
            File size         Ratio      Format      Name
       --------------------   ------   -----------   -----------
        963584 <-    481280   49.95%    win32/pe     codeit-unpack.exe
    
    Unpacked 1 file.
    

Looking at the strings, one jumps out:

    
    
    This is a third-party compiled AutoIt script.
    

This makes sense with the prompt which refers to this file as a “little
compiled script”. In googling about AutoIt complication and decompilation, I
learned that it’s common to UPX pack compiled AutoIt scripts.

[AutoIt](https://www.autoitscript.com/site/) is a:

> BASIC-like scripting language designed for automating the Windows GUI and
> general scripting. It uses a combination of simulated keystrokes, mouse
> movement and window/control manipulation in order to automate tasks in a way
> not possible or reliable with other languages (e.g. VBScript and SendKeys).
> AutoIt is also very small, self-contained and will run on all versions of
> Windows out-of-the-box with no annoying “runtimes” required!

Later in the description, it mentions compiling to exe:

> AutoIt has been designed to be as small as possible and stand-alone with no
> external .dll files or registry entries required making it safe to use on
> Servers. Scripts can be compiled into stand-alone executables with
> **Aut2Exe**.

### Decompile

I tried to use one AutoIt decompiler,
[Exe2Aut](http://domoticx.com/autoit3-decompiler-exe2aut/), but it failed:

![image-20200919211330873](https://0xdfimages.gitlab.io/img/image-20200919211330873.png)

This was actually a mistake on my part. I fed it the unpacked exe. On doing
this writeup, I noticed that giving it the original actually works (and that
`Exe2Aut.exe` is actually in the [Flare-VM](https://github.com/fireeye/flare-
vm) image, so that’s probably the intended tool):

![image-20201028070957566](https://0xdfimages.gitlab.io/img/image-20201028070957566.png)

Not knowing that at the time, I moved on to another one,
[myAutToExe](https://files.planet-dl.org/Cw2k/MyAutToExe/index.html), which
did work. It opened with a busy GUI. I entered the path to my unmodified
executable:

![image-20200922134633722](https://0xdfimages.gitlab.io/img/image-20200922134633722.png)

From the Scan File menu, I selected Automated:

![image-20200922134657148](https://0xdfimages.gitlab.io/img/image-20200922134657148.png)

It ran for about twenty seconds:

![image-20200922134913919](https://0xdfimages.gitlab.io/img/image-20200922134913919.png)

It also created a bunch of files:

![image-20200922135011284](https://0xdfimages.gitlab.io/img/image-20200922135011284.png)

Looking over the files, `codeit_restore.au3` is the AutoIt script.
`qr_encoder.dll` and `sprite.bmp` will be useful as well. The bitmap file is
the image that’s displayed when I run it:

![](https://0xdfimages.gitlab.io/img/flare7-codeit-sprite.bmp)

## RE

### Overview

#### Structure

What comes out is some obfuscated AutoIt code in `codeit_restore.au3`. At the
very top, I see a wrapper that indicates to use UPX on compilation:

    
    
    #Region
    #AutoIt3Wrapper_UseUpx=y
    #EndRegion
    

Looking over the rest of the file, everything falls into:

  * Defining globals
  * Defining functions
  * Some code that starts the program

#### Globals

A big part of the obfuscation relies on using variables for numbers. There are
25 lines that look like this:

    
    
    GLOBAL $FLWFCIOVPD=NUMBER(" 150 "),$FLBRBERYHA=NUMBER(" 128 "),$FLQXFKFBOD=NUMBER(" 28 "),$FLLKGHUYOO=NUMBER(" 25 "),$FLVOITVVCQ=NUMBER(" 150 "),$FLTWXZCOJL=NUMBER(" 151 "),$FLABFAKVAP=NUMBER(" 28 "),$FLDWMPGTSJ=NUMBER(" 152 "),$FLNCSALWDM=NUMBER(" 28 "),$FLXJEXJHWM=NUMBER(" 150 "),$FLMMQOCQPD=NUMBER(" 150 "),$FLCUYAGGUD=NUMBER(" 25 "),$FLXKQPKZXQ=NUMBER(" 28 "),$FLLFTZDHOA=NUMBER(" 153 "),$FLIQYVCBYG=NUMBER(" 28 "),$FLEUHCHVKD=NUMBER(" 28 "),$FLEYXMOFXU=NUMBER(" 150 "),$FLORZKPCIQ=NUMBER(" 28 "),$FLHIQHCYIO=NUMBER(" 28 "),$FLMMQJHZIV=NUMBER(" 154 "),$FLPDPBBQIG=NUMBER(" 25 "),$FLYUGCZHJH=NUMBER(" 26 "),$FLIIEMMOAO=NUMBER(" 155 "),$FLQBXXVJKP=NUMBER(" 28 "),$FLLCWTUUXW=NUMBER(" 39 ")
    

There is also a single uninitiated `GLOBAL`, defined, `$OS`, which will become
clear momentarily.

Finally, there are some variables that are defined in a non-obfuscated manner:

    
    
    GLOBAL CONST $STR_NOCASESENSE=0
    GLOBAL CONST $STR_CASESENSE=1
    GLOBAL CONST $STR_NOCASESENSEBASIC=2
    GLOBAL CONST $STR_STRIPLEADING=1
    GLOBAL CONST $STR_STRIPTRAILING=2
    GLOBAL CONST $STR_STRIPSPACES=4
    GLOBAL CONST $STR_STRIPALL=8
    GLOBAL CONST $STR_CHRSPLIT=0
    GLOBAL CONST $STR_ENTIRESPLIT=1
    GLOBAL CONST $STR_NOCOUNT=2
    GLOBAL CONST $STR_REGEXPMATCH=0
    GLOBAL CONST $STR_REGEXPARRAYMATCH=1
    GLOBAL CONST $STR_REGEXPARRAYFULLMATCH=2
    GLOBAL CONST $STR_REGEXPARRAYGLOBALMATCH=3
    GLOBAL CONST $STR_REGEXPARRAYGLOBALFULLMATCH=4
    GLOBAL CONST $STR_ENDISSTART=0
    GLOBAL CONST $STR_ENDNOTSTART=1
    GLOBAL CONST $SB_ANSI=1
    GLOBAL CONST $SB_UTF16LE=2
    GLOBAL CONST $SB_UTF16BE=3
    GLOBAL CONST $SB_UTF8=4
    GLOBAL CONST $SE_UTF16=0
    GLOBAL CONST $SE_ANSI=1
    GLOBAL CONST $SE_UTF8=2
    GLOBAL CONST $STR_UTF16=0
    GLOBAL CONST $STR_UCS2=1
    

#### Functions

There are eight utility functions that have names that match what they do like
`_HEXTOSTRING`, `_STRINGREPEAT`, and `_STRINGINSERT`. The rest of the
functions are named by strings starting with `ARE` and then eight random
uppercase characters, like `AREIALBHUYT`.

All of the variables in these functions seem to be similarly named, starting
with `$FL` and then eight random uppercase characters. Interestingly, there
are a few examples where an english word is appended to the variable, like
`$FLFNVBVVFI` and `$FLFNVBVVFIRAW`.

#### Code

The code that isn’t in a function or declaring a variable is limited:

    
    
    #Region
    #AutoIt3Wrapper_UseUpx=y
    #EndRegion
    #OnAutoItStartRegister "AREIHNVAPWN"
    GUICREATE(AREHDIDXRGK($OS[$FLFBEVULDL]),$FLWNRVOJHL,$FLLLVVITVL,-$FLWTSVPQCX,-$FLRRBXOGGL)
    AREIALBHUYT()
    GUIDELETE()
    

The `#OnAutoItStartRegister "AREIHNVAPWN"` will call that function before it
runs the rest of the program, and it’s an important one:

    
    
    FUNC AREIHNVAPWN()
    LOCAL $DLIT="7374727563743b75696e7420626653697a653b75696e7420626652657365727665643b75696e742062664f6666426974733b"
    $DLIT&="75696e7420626953697a653b696e7420626957696474683b696e742062694865696768743b7573686f7274206269506c616e"
    $DLIT&="65733b7573686f7274206269426974436f756e743b75696e74206269436f6d7072657373696f6e3b75696e7420626953697a"
    $DLIT&="65496d6167653b696e742062695850656c735065724d657465723b696e742062695950656c735065724d657465723b75696e"
    $DLIT&="74206269436c72557365643b75696e74206269436c72496d706f7274616e743b656e647374727563743b4FD5$626653697a6"
    $DLIT&="54FD5$626652657365727665644FD5$62664f6666426974734FD5$626953697a654FD5$626957696474684FD5$6269486569"
    $DLIT&="6768744FD5$6269506c616e65734FD5$6269426974436f756e744FD5$6269436f6d7072657373696f6e4FD5$626953697a65"
    ...[snip]...
    $DLIT&="3697a65"
    GLOBAL $OS=STRINGSPLIT($DLIT,"4FD5$",1)
    ENDFUNC
    FUNC AREHDIDXRGK($FLQLNXGXBP)
    

This function populates the the `$OS` variable by taking this long string and
breaking it on a delimiter into an array of hex strings.

Throughout the code, there are bits that match this pattern with different
`$FL` variables:

    
    
    AREHDIDXRGK($OS[$FLFBEVULDL])
    

Given what I know about how the global variables are set and how `$OS` is
populated, it looks like each of these is getting a hex string from `$OS` and
decoding it in `AREHDIDXRGK`, which is just a hex decode:

    
    
    FUNC AREHDIDXRGK($FLQLNXGXBP)
    	LOCAL $FLQLNXGXBP_
    	FOR $FLRCTQRYUB=1 TO STRINGLEN($FLQLNXGXBP)STEP 2
    		$FLQLNXGXBP_&=CHR(DEC(STRINGMID($FLQLNXGXBP,$FLRCTQRYUB,2)))
    	NEXT
    	RETURN $FLQLNXGXBP_
    ENDFUNC
    

I can rename the variables to make it more clear:

    
    
    FUNC hex2bytes($hex_string)
    	LOCAL $res
    	FOR $i=1 TO STRINGLEN($hex_string) STEP 2
    		$res&=CHR(DEC(STRINGMID($hex_string,$i,2)))
    	NEXT
    	RETURN $res
    ENDFUNC
    

After the obfuscated strings are ready, the program then calls `GUICREATE`,
`AREIALBHUYT` (which I’ll rename to `main`), and `GUIDELETE`.

### Deobfuscation

To deobfuscate this, I want a way to get the references I need from the
globals and from `$OS`. I copies large chunks of the code and used `vim`
macros to clean it up so that I had it in Python format:

    
    
    dlit = "7374727563743b75696e7420626653697a653b75696e7420626652657365727665643b75696e742062664f6666426974733b75696e7420626953697a653b696e7420626957696474683b696e742062694865696768743b7573686f7274206269506c616e65733b7573686f7274206269426974436f756e743b75696...[snip]...696c6553697a65"
    
    ints = {
    'FLAVEKOLCA': 0,
    'FLERQQJBMH': 1,
    'FLOWFRCKMW': 0,
    'FLMXUGFNDE': 0,
    'FLVJXCQXYN': 2,
    'FLDDXNMRKH': 0,
    'FLROSEEFLV': 1,
    'FLPGRGLPZM': 0,
    'FLVZRKQWYG': 0,
    'FLYVORMNQR': 0,
    'FLVTHBRBXY': 1,
    'FLXTTXKIKW': 0,
    'FLGJMYCRVW': 1,
    'FLCEUJXGSE': 0,
    'FLHPTOIJIN': 0,
    'FLRZPLGFOE': 0,
    ...[snip]...
    'FLXEZGJWBW': 30,
    'FLSGBZULNF': 23 }
    

Now, I can import the above code (`constants.py`) and write some code that
will clean up the stuff I already know about:

    
    
    #!/usr/bin/env python3
    
    import binascii
    import re
    from constants import *
    
    
    os = dlit.split('4FD5$')
    
    consts = [''] + [binascii.unhexlify(x).decode() for x in os]
    
    with open('codeit_restore.au3', 'r') as f:
        autoit_src = f.read()
    
    new_src = re.sub('AREHDIDXRGK\(\$OS\[\$([A-Z]{8,})\]\)', lambda m: f"'{consts[ints[m.group(1)]]}'", autoit_src)
    
    for k in ints:
        new_src = re.sub(f'\${k}', f'{ints[k]}', new_src)
    
    with open('codeit_restore_mod.au3', 'w') as f:
        f.write(new_src)
    

This code reads the AutoIt source and does two replacements. First, it will
find instances where a string from `$OS` is hex decoded and replace that with
the static string. Then, it will look over all the constant variables and
replace them with their value.

At this point, I’ll start working through the code starting at `main`,
renaming functions and the remaining variables to make the code make more
sense. It’s really useful to have the [AutoIt Function
documentation](https://www.autoitscript.com/autoit3/docs/functions/) handy for
this process.

### Main

`main` starts by creating the parts of the GUI:

    
    
    FUNC main()
    LOCAL $gui_input=GUICTRLCREATEINPUT('Enter text to encode',-1,5,300)
    LOCAL $gui_button=GUICTRLCREATEBUTTON('Can haz code?',-1,30,300)
    LOCAL $gui_pic=GUICTRLCREATEPIC('',-1,55,300,300)
    LOCAL $gui_menu=GUICTRLCREATEMENU('Help')
    LOCAL $gui_menu_item=GUICTRLCREATEMENUITEM('About CodeIt Plus!',$gui_menu)
    LOCAL $image_temp_filename=writeDllOrBmpToTemp(13)
    GUICTRLSETIMAGE($gui_pic,$image_temp_filename)
    deleteFile($image_temp_filename)
    GUISETSTATE(@SW_SHOW)
    

After that, it enters a `while 1` loop reading input from the GUI:

    
    
    WHILE 1
        SWITCH GUIGETMSG()
            CASE $gui_button
                ...[snip]...
            CASE $gui_menu_item
                ...[snip]...
            CASE -3
                EXITLOOP
            ENDSWITCH
    WEND
    

The `$gui_menu_item` case just prints the license / about page. The
interesting case is then the button is pushed.

First, it reads the input string into a variable. Then it calls a function
I’ve named `writeDllOrBmpToTemp`:

    
    
    LOCAL $input_string=GUICTRLREAD($gui_input)
    IF $input_string THEN
    	LOCAL $qrdll_temp_filename=writeDllOrBmpToTemp(26)
    

This function creates a random string, and creates a file in the local
`@SCRIPTDIR` with that name. If the input is between 10 and 15, it then writes
`sprite.bmp` to that file, and appends `.bmp` to the filename. If the input is
between 25 and 30, it writes `qr_encoder.dll` and appends `.dll` to the
filename. It then returns the filename.

Next, the code will create a struct to pass into a function using
[DLLSTRUCTCREATE](https://www.autoitscript.com/autoit3/docs/functions/DllStructCreate.htm).
This takes a string that defines the different parts of the struct to be
created. For example, the next line is:

    
    
    LOCAL $qr_struct=DLLSTRUCTCREATE('struct;dword;dword;byte[3918];endstruct')
        LOCAL $ret=DLLCALL($qrdll_temp_filename,'int:cdecl','justGenerateQRSymbol','struct*',$qr_struct,'str',$input_string)
    

This will create a struct with two `dwords` and a 3918-byte array. On the next
line, that struct is passed into the function from `qr_encoder.dll`,
`justGenerateQRSymbol`. The resulting data should be written into the struct.

Assuming that returned non-zero, it continues. The rest of main makes perfect
sense, except for one part:

    
    
    IF $ret[0]<>0 THEN
    switchToFlag($qr_struct)
    LOCAL $bitmap_struct=createBitmapStruct((DLLSTRUCTGETDATA($qr_struct,1)*DLLSTRUCTGETDATA($qr_struct,2)),(DLLSTRUCTGETDATA($qr_struct,1)*DLLSTRUCTGETDATA($qr_struct,2)),1024)
    $ret=DLLCALL($qrdll_temp_filename,'int:cdecl','justConvertQRSymbolToBitmapPixels','struct*',$qr_struct,'struct*',$bitmap_struct[1])
    IF $ret[0]<>0 THEN
    $image_temp_filename2=genRandomString(25,30)&'.bmp'
    writeImageToFile($bitmap_struct,$image_temp_filename2)
    ENDIF
    ENDIF
    deleteFile($qrdll_temp_filename)
    ELSE
    $image_temp_filename2=writeDllOrBmpToTemp(11)
    ENDIF
    GUICTRLSETIMAGE($gui_pic,$image_temp_filename2)
    deleteFile($image_temp_filename2)
    

After a function call, the `$qr_struct` is passed to another function that
generates another struct, which is passed into
`qr_encoded.dll:justConvertQRSymbolToBitmapPixels`. Then a random bitmap file
is created, the `$bitmap_struct` is used to write the QRcode image to a the
file, and then it’s loaded into the GUI using `GUICTRLSETIMAGE` and the file
is deleted.

### Flag Function

The thing that stuck out to me was the function call between the two DLL
calls. Surely the data from `justGenerateQRSymbol` would be compatible as
input to `justConvertQRSymbolToBitmapPixels` from the same DLL. What is the
program doing between the two that involves the return / input?

The first thing this function does is call another function, which I’ve named
`getComputerName`:

    
    
    FUNC getComputerName()
    	LOCAL $computer_name=-1
    	LOCAL $computer_nameRAW=DLLSTRUCTCREATE('struct;dword;char[1024];endstruct')
    	DLLSTRUCTSETDATA($computer_nameRAW,1,1024)
    	LOCAL $res=DLLCALL('kernel32.dll','int','GetComputerNameA','ptr',DLLSTRUCTGETPTR($computer_nameRAW,2),'ptr',DLLSTRUCTGETPTR($computer_nameRAW,1))
    	IF $res[0]<>0 THEN
    		$computer_name=BINARYMID(DLLSTRUCTGETDATA($computer_nameRAW,2),1,DLLSTRUCTGETDATA($computer_nameRAW,1))
    	ENDIF
    	RETURN $computer_name
    ENDFUNC
    

It creates a struct to hold the results and passes it to
`kernel32.dll:GetComputerNameA`.

    
    
    LOCAL $computer_name=getComputerName()
    IF $computer_name<>-1 THEN
    	$computer_name=BINARY(STRINGLOWER(BINARYTOSTRING($computer_name)))
    	LOCAL $computer_name_raw=DLLSTRUCTCREATE('struct;byte['&BINARYLEN($computer_name)&'];endstruct')
    	DLLSTRUCTSETDATA($computer_name_raw,1,$computer_name)
    	scrambleComputerName($computer_name_raw)
    

After getting the computer name, it converts it to binary, and then passes it
to a function I’m calling `scrambleComputerName`. I’ll come back to this one.

Now it’s going to create a hash, which takes several API calls from
`advapi32.dll` and structs to pass inputs / results:

    
    
    LOCAL $hash_struct=DLLSTRUCTCREATE('struct;ptr;ptr;dword;byte[32];endstruct')
    DLLSTRUCTSETDATA($hash_struct,3,32)
    LOCAL $ret=DLLCALL('advapi32.dll','int','CryptAcquireContextA','ptr',DLLSTRUCTGETPTR($hash_struct,1),'ptr',0,'ptr',0,'dword',24,'dword',4026531840)
    IF $ret[0]<>0 THEN
    	$ret=DLLCALL('advapi32.dll','int','CryptCreateHash','ptr',DLLSTRUCTGETDATA($hash_struct,1),'dword',32780,'dword',0,'dword',0,'ptr',DLLSTRUCTGETPTR($hash_struct,2))
    	IF $ret[0]<>0 THEN
    		$ret=DLLCALL('advapi32.dll','int','CryptHashData','ptr',DLLSTRUCTGETDATA($hash_struct,2),'struct*',$computer_name_raw,'dword',DLLSTRUCTGETSIZE($computer_name_raw),'dword',0)
    		IF $ret[0]<>0 THEN
    			$ret=DLLCALL('advapi32.dll','int','CryptGetHashParam','ptr',DLLSTRUCTGETDATA($hash_struct,2),'dword',2,'ptr',DLLSTRUCTGETPTR($hash_struct,4),'ptr',DLLSTRUCTGETPTR($hash_struct,3),'dword',0)
    

Now the result of that hash is put with some binary data into a variable.
There’s a long binary (created out of hex). Then there’s more calls to crypto
APIs from `advapi32.dll`: `CryptAcquireContextA`, `CryptImportKey`,
`CryptDecrypt`.

    
    
    LOCAL $modified_hash_result=BINARY('0x'&'08020'&'00010'&'66000'&'02000'&'0000')&DLLSTRUCTGETDATA($hash_struct,4)
    LOCAL $static_bytes=BINARY('0x'&'CD4B3'&'2C650'&'CF21B'&'DA184'&'D8913'&'E6F92'&'0A37A'&'4F396'&'3736C'&'042C4'&'59EA0'&'7B79E'&'A443F'&'FD189'&'8BAE4'&'9B115'&'F6CB1'&'E2A7C'&'1AB3C'&'4C256'&'12A51'&'9035F'&'18FB3'&'B1752'&'8B3AE'&'CAF3D'&'480E9'&'8BF8A'&'635DA'&'F974E'&'00135'&'35D23'&'1E4B7'&'5B2C3'&'8B804'&'C7AE4'&'D266A'&'37B36'&'F2C55'&'5BF3A'&'9EA6A'&'58BC8'&'F906C'&'C665E'&'AE2CE'&'60F2C'&'DE38F'&'D3026'&'9CC4C'&'E5BB0'&'90472'&'FF9BD'&'26F91'&'19B8C'&'484FE'&'69EB9'&'34F43'&'FEEDE'&'DCEBA'&'79146'&'0819F'&'B21F1'&'0F832'&'B2A5D'&'4D772'&'DB12C'&'3BED9'&'47F6F'&'706AE'&'4411A'&'52')
    LOCAL $crypt_stuff_struct=DLLSTRUCTCREATE('struct;ptr;ptr;dword;byte[8192];byte['&BINARYLEN($modified_hash_result)&'];dword;endstruct') ; [crypt_context, HCRYPTOKEY handle, len static bytes, static_bytes, mod hash == pbData, mod_hash len]
    DLLSTRUCTSETDATA($crypt_stuff_struct,3,BINARYLEN($static_bytes))
    DLLSTRUCTSETDATA($crypt_stuff_struct,4,$static_bytes)
    DLLSTRUCTSETDATA($crypt_stuff_struct,5,$modified_hash_result)
    DLLSTRUCTSETDATA($crypt_stuff_struct,6,BINARYLEN($modified_hash_result))
    LOCAL $ret=DLLCALL('advapi32.dll','int','CryptAcquireContextA','ptr',DLLSTRUCTGETPTR($crypt_stuff_struct,1),'ptr',0,'ptr',0,'dword',24,'dword',4026531840)
    IF $ret[0]<>0 THEN
    $ret=DLLCALL('advapi32.dll','int','CryptImportKey','ptr',DLLSTRUCTGETDATA($crypt_stuff_struct,1),'ptr',DLLSTRUCTGETPTR($crypt_stuff_struct,5),'dword',DLLSTRUCTGETDATA($crypt_stuff_struct,6),'dword',0,'dword',0,'ptr',DLLSTRUCTGETPTR($crypt_stuff_struct,2))
    IF $ret[0]<>0 THEN
    $ret=DLLCALL('advapi32.dll','int','CryptDecrypt','ptr',DLLSTRUCTGETDATA($crypt_stuff_struct,2),'dword',0,'dword',1,'dword',0,'ptr',DLLSTRUCTGETPTR($crypt_stuff_struct,4),'ptr',DLLSTRUCTGETPTR($crypt_stuff_struct,3))
    

In these calls, the key being imported is the buffer built from the hash of
the computer name. The ciphertext is the static binary string.

Now the program creates two markers, `FLARE` and `ERALF`, and looks at the
first five bytes of the decrypted content. If it starts with `FLARE` and ends
with `ERALF`, it uses the decrypted results to completely overwrite all three
elements in `$qrcode_struct`:

    
    
    LOCAL $decrypt_results=BINARYMID(DLLSTRUCTGETDATA($crypt_stuff_struct,4),1,DLLSTRUCTGETDATA($crypt_stuff_struct,3))
    $bytes_FLARE=BINARY('FLARE')
    $bytes_ERALF=BINARY('ERALF')
    $decrypt_start=BINARYMID($decrypt_results,1,BINARYLEN($bytes_FLARE))
    $decrypt_end=BINARYMID($decrypt_results,BINARYLEN($decrypt_results)-BINARYLEN($bytes_ERALF)+1,BINARYLEN($bytes_ERALF))
    IF $bytes_FLARE=$decrypt_start AND $bytes_ERALF=$decrypt_end THEN
    DLLSTRUCTSETDATA($qrcode_struct,1,BINARYMID($decrypt_results,6,4))
    DLLSTRUCTSETDATA($qrcode_struct,2,BINARYMID($decrypt_results,10,4))
    DLLSTRUCTSETDATA($qrcode_struct,3,BINARYMID($decrypt_results,14,BINARYLEN($decrypt_results)-18))
    

There’s then some cleanup of the Crypt stuff (`CryptoDestroyKey`,
`CryptReleaseContext`, `CryptDestroyhash`) and the function exits.

So I’ve found where the flag is. The hostname of the machine is scrambled,
then hashed. That hash is used to generate a key BLOB using
[CryptImportKey](https://docs.microsoft.com/en-
us/windows/win32/api/wincrypt/nf-wincrypt-cryptimportkey), which is then used
to decrypt some static bytes. If that decryption works, the contents are used
to replace the QRcode generated from the input string with presumably one with
the flag.

### Scramble

This felt a bit hopeless for a while. Even if I can reverse the scramble
function, how does that help me reverse the hash? Having no where else to go,
I dug into the scramble function. It’s not too long, so I’ll paste it here in
it’s entirety:

    
    
    FUNC scrambleComputerName(BYREF $computername_struct)
    	LOCAL $temp_image_file=writeDllOrBmpToTemp(14)
    	LOCAL $temp_image_file_handle=createFile1($temp_image_file)
    	IF $temp_image_file_handle<>-1 THEN
    		LOCAL $temp_image_file_size=getFileSize($temp_image_file_handle)
    		IF $temp_image_file_size<>-1 AND DLLSTRUCTGETSIZE($computername_struct)<$temp_image_file_size-54 THEN
    			LOCAL $file_content_bytes=DLLSTRUCTCREATE('struct;byte['&$temp_image_file_size&'];endstruct')
    			LOCAL $ret=readFile($temp_image_file_handle,$file_content_bytes)
    			IF $ret<>-1 THEN
    				LOCAL $file_content_bytes2=DLLSTRUCTCREATE('struct;byte[54];byte['&$temp_image_file_size-54&'];endstruct',DLLSTRUCTGETPTR($file_content_bytes))
    				LOCAL $ctr=1
    				LOCAL $output=''
    				FOR $i=1 TO DLLSTRUCTGETSIZE($computername_struct)
    				LOCAL $byte_as_int=NUMBER(DLLSTRUCTGETDATA($computername_struct,1,$i))
    					FOR $j=6 TO 0 STEP -1
    						$byte_as_int+=BITSHIFT(BITAND(NUMBER(DLLSTRUCTGETDATA($file_content_bytes2,2,$ctr)),1),-1*$j)
    						$ctr+=1
    					NEXT
    					$output&=CHR(BITSHIFT($byte_as_int,1)+BITSHIFT(BITAND($byte_as_int,1),-7))
    				NEXT
    				DLLSTRUCTSETDATA($computername_struct,1,$output)
    			ENDIF
    		ENDIF
    		closeHandle($temp_image_file_handle)
    	ENDIF
    	deleteFile($temp_image_file)
    ENDFUNC
    

It gets a copy of the sprite image, and gets a handle to it so it can read the
contents in. Using structs, it starts reading 54 bytes into the file, and it
enters a couple of loops. For each byte in `$computer_name`, it will loop over
the next seven bytes of the image file, taking the low bit from each and
effectively building a 7-bit word. For example, the first seven bytes
(starting at 54) are:

    
    
    >>> sprite[54:61]
    b'\xff\xff\xfe\xfe\xfe\xfe\xff'
    

I can get the low bit of each:

    
    
    >>> [b&1 for b in sprite[54:61]]
    [1, 1, 0, 0, 0, 0, 1]
    

And form that into a word:

    
    
    >>> int(''.join([str(b&1) for b in sprite[54:61]]),2)
    97
    

In the loop, that value is added to the first byte of the computer name. Then,
the bits are rotated right by one, with the low bit becoming the highbit.

I wrote the following Python, `scramble.py` to see it:

    
    
    #!/usr/bin/env python3
    
    import sys 
    
    
    name = sys.argv[1]
    
    with open('sprite.bmp', 'rb') as f:
        sprite = f.read()
    
    ctr = 0 
    out = ''
    
    for i,c in enumerate(name):
        x = ord(c)
        for j in range(6, -1, -1):
            x += (sprite[54+ctr] & 1) * pow(2,j)
            ctr += 1
        out += chr((x // 2) + ((x & 1) * pow(2,7)))
    
    print(out)
    

Guessing that the computer name would be less than 30 bytes, I calculated the
first 30 bytes of 7-bit words from the image (shown both as hex and as ASCII):

    
    
    $ python3 -i scramble.py test
    êmóR
    >>> for i in range(0, 7*30, 7):
    ...     print(f'{int("".join([str(x) for x in [sprite[x] & 1 for x in range(54,54+7*50)]][i:i+7]), 2):02x}', end='')
    ... 
    61757430317466616e313939397f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f7f
    
    >>> for i in range(0, 7*30, 7):
    ...     print(f'{chr(int("".join([str(x) for x in [sprite[x] & 1 for x in range(54,54+7*50)]][i:i+7]), 2))}', end='')
    ... 
    aut01tfan1999
    

“aut01tfan1999” is clearly a kind of key.

## Get Flag

Another interesting thing about the scramble algorithm. It is adding the two
characters together, and then effectively dividing by two if the result is
even, or dividing by two and then adding 128 if it’s odd. That means if the
hostname is “aut01tfan1999”, it won’t actually scramble because `(a + a) // 2
== a` for each character (whereas any other hostname will):

    
    
    $ python3 scramble.py aut01tfan1999
    aut01tfan1999
    $ python3 scramble.py 0xdfcomputer
    ÈölKJñéèñÒOÕ
    

This in no way means that it has to be the answer, but it’s worth a shot.
(After taking a snapshot of my VM), I renamed my host, rebooted, and opened
`codeit.exe`. No matter what I put in, the QRcode doesn’t change. That’s a
good sign:

![image-20200922133720255](https://0xdfimages.gitlab.io/img/image-20200922133720255.png)

That QRCode decodes to the flag.

**Flag: L00ks_L1k3_Y0u_D1dnt_Run_Aut0_Tim3_0n_Th1s_0ne!@flare-on.com**

[](/flare-on-2020/codeit)

