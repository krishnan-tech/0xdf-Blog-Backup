# Flare-On 2020: report.xls

[flare-on](/tags#flare-on ) [ctf](/tags#ctf ) [flare-on-report](/tags#flare-
on-report ) [reverse-engineering](/tags#reverse-engineering ) [xls](/tags#xls
) [vba](/tags#vba ) [olevba](/tags#olevba ) [evil-clippy](/tags#evil-clippy )
[pcode](/tags#pcode ) [vba-stomp](/tags#vba-stomp ) [python](/tags#python )
[pcodedmp](/tags#pcodedmp ) [pcode2code](/tags#pcode2code ) [script-
obfuscation](/tags#script-obfuscation )  
  
Oct 27, 2020

  * [[1] Fidler](/flare-on-2020/fidler)
  * [[2] garbage](/flare-on-2020/garbage)
  * [[3] wednesday](/flare-on-2020/wednesday)
  * [4] report.xls
  * [[5] TKApp](/flare-on-2020/tkapp)
  * [[6] CodeIt](/flare-on-2020/codeit)
  * [[7] RE Crowd](/flare-on-2020/recrowd)
  * [[8] Aardvark](/flare-on-2020/aardvark)
  * [[9] crackinstaller](/flare-on-2020/crackinstaller)
  * [[10] break](/flare-on-2020/break)

![report](https://0xdfimages.gitlab.io/img/flare2020-report-cover.png)

report.xls was my kind of challenge. It’s an Excel book with an macro with
some relatively standard obfuscation and sandbox evasion. In analyzing the
VBA, I see more and more hints that something odd is going on. Eventually I’ll
extract an mp3 file with several more hints that the VBA has been stomped,
replacing the p-code with something different from the VBA. When I dump the
p-code and analyze it, I’ll find an image with the flag.

## Challenge

> Nobody likes analysing infected documents, but it pays the bills. Reverse
> this macro thrill-ride to discover how to get it to show you the key.

The file contains a single Excel workbook:

    
    
    root@kali# file report.xls 
    report.xls: Composite Document File V2 Document, Little Endian, Os: Windows, Version 10.0, Code page: 1252, 0x17: 1048576CDFV2 Microsoft Excel
    

Also, the prompt is flat out wrong - I love analyzing infected documents.

## Running It

When I open the document, it’s got a classic image suggesting that I’ve got
the wrong version (of Word?) and I need to enable macros. But also, a message
box pops up with an error: “Invalid procedure call or argument”:

[![image-20200917174113379](https://0xdfimages.gitlab.io/img/image-20200917174113379.png)_Click
for full size
image_](https://0xdfimages.gitlab.io/img/image-20200917174113379.png)

## RE - VBA

### General Layout

There are macros in both “ThisWorkbook” and “Sheet1”, and there’s a form:

![image-20200917174640025](https://0xdfimages.gitlab.io/img/image-20200917174640025.png)

ThisWorkbook has two functions to try to run when the workbook is opened,
`Workbook_Open()` and `Auto_Open()`, and both run `Sheet1.folderol`:

    
    
    Sub Workbook_Open()
    Sheet1.folderol
    End Sub
    
    Sub Auto_Open()
    Sheet1.folderol
    End Sub
    

Sheet1 contains four custom functions (which I’ll get much more in-depth into)
- `GetInternetConnectedState()`, `rigmarole()`, `folderol()`, and
`canoodle()`. It also imports three functions from Windows Libraries,
`InternetGetConnectedState`, `mciSendString`, and `GetShortPathName`:

    
    
    Private Declare Function InternetGetConnectedState Lib "wininet.dll" _
    (ByRef dwflags As Long, ByVal dwReserved As Long) As Long
    
    Private Declare PtrSafe Function mciSendString Lib "winmm.dll" Alias _
       "mciSendStringA" (ByVal lpstrCommand As String, ByVal _
       lpstrReturnString As Any, ByVal uReturnLength As Long, ByVal _
       hwndCallback As Long) As Long
    
    Private Declare Function GetShortPathName Lib "kernel32" Alias "GetShortPathNameA" _
        (ByVal lpszLongPath As String, ByVal lpszShortPath As String, ByVal lBuffer As Long) As Long
    

### Debugging

One approach to this (and other macro challenges / phishing docs) is to use
`olevba` to dump the VBA and statically analyze. For more challenging
documents, it’s nice to have the ability to debug, either in the document
itself, in the immediate window, or in another empty document.

No macro in this workbook will run. Any time I try to start, that message box
pops up. To get around this, I’ll do a combination of writing my own similar
code in Python, and create a new `.xls` file and then drag the form into it as
a copy in the macro editor. This allows me access to the form and the data it
holds, and I can start to drop parts of the macros that I want to test into
this new workbook as well.

### rigamarole

I’ll start in `folderol`, as it’s the function called by the `auto_open()`,
but it quickly becomes clear that I’ll need to understand `rigamarole` to
understand `folderol`, so I’ll go there first.

One thing I’ll notice pretty quickly is that the static strings are encoded
and stored in the form. The first instruction is

    
    
    onzo = Split(F.L, ".")
    

From my new workbook, I can run `print F.L` in the Immediate window to see the
data:

    
    
    print F.L
    9655B040B64667238524D15D6201.B95D4E01C55CC562C7557405A532D768C55FA12DD074DC697A06E172992CAF3F8A5C7306B7476B38.C555AC40A7469C234424.853FA85C470699477D3851249A4B9C4E.A855AF40B84695239D24895D2101D05CCA62BE5578055232D568C05F902DDC74D2697406D7724C2CA83FCF5C2606B547A73898246B4BC14E941F9121D464D263B947EB77D36E7F1B8254.853FA85C470699477D3851249A4B9C4E.9A55B240B84692239624.CC55A940B44690238B24CA5D7501CF5C9C62B15561056032C468D15F9C2DE374DD696206B572752C8C3FB25C3806.A8558540924668236724B15D2101AA5CC362C2556A055232AE68B15F7C2DC17489695D06DB729A2C723F8E5C65069747AA389324AE4BB34E921F9421.CB55A240B5469B23.AC559340A94695238D24CD5D75018A5CB062BA557905A932D768D15F982D.D074B6696F06D5729E2CAE3FCF5C7506AD47AC388024C14B7C4E8F1F8F21CB64
    

Given the split on `.`, this looks like it creates an array of hex strings.
Each time one of these is referenced, it’s done so as `rigamarole(onzo(#))`.
So to understand `folderol`, I need to decode these strings first.

`rigmarole` is fairly simple:

    
    
    Function rigmarole(es As String) As String
        Dim furphy As String
        Dim c As Integer
        Dim s As String
        Dim cc As Integer
        furphy = ""
        For i = 1 To Len(es) Step 4
            c = CDec("&H" & Mid(es, i, 2))
            s = CDec("&H" & Mid(es, i + 2, 2))
            cc = c - s
            furphy = furphy + Chr(cc)
        Next i
        rigmarole = furphy
    End Function
    

It takes a hex string four characters at a time, breaking them into two pairs,
and converting each to an int. Then it subtracts the second from the first to
generate a character. It does this down the input to generate a string.

I wrote a short Python script to do that based on the code in `rigmarole`:

    
    
    #!/usr/bin/env python3
      
    
    def rigmarole(hexstr):
    
        res = ""
        for i in range(0, len(hexstr), 4):
            res += chr(int(hexstr[i:i+2],16) - int(hexstr[i+2:i+4],16))
        return res
    
    
    fl = "9655B040B64667238524D15D6201.B95D4E01C55CC562C7557405A532D768C55FA12DD074DC697A06E172992CAF3F8A5C7306B7476B38.C555AC40A7469C234424.853FA85C470699477D3851249A4B9C4E.A855AF40B84695239D24895D2101D05CCA62BE5578055232D568C05F902DDC74D2697406D7724C2CA83FCF5C2606B547A73898246B4BC14E941F9121D464D263B947EB77D36E7F1B8254.853FA85C470699477D3851249A4B9C4E.9A55B240B84692239624.CC55A940B44690238B24CA5D7501CF5C9C62B15561056032C468D15F9C2DE374DD696206B572752C8C3FB25C3806.A8558540924668236724B15D2101AA5CC362C2556A055232AE68B15F7C2DC17489695D06DB729A2C723F8E5C65069747AA389324AE4BB34E921F9421.CB55A240B5469B23.AC559340A94695238D24CD5D75018A5CB062BA557905A932D768D15F982D.D074B6696F06D5729E2CAE3FCF5C7506AD47AC388024C14B7C4E8F1F8F21CB64"
    
    onzo = fl.split('.')
    
    for i,x in enumerate(onzo):
        print(f'[{i:02d}] {rigmarole(x)}')
    

It prints a list of the decoded strings:

    
    
    root@kali# ./decode.py
    [00] AppData
    [01] \Microsoft\stomp.mp3
    [02] play
    [03] FLARE-ON
    [04] Sorry, this machine is not supported.
    [05] FLARE-ON
    [06] Error
    [07] winmgmts:\\.\root\CIMV2
    [08] SELECT Name FROM Win32_Process
    [09] vbox
    [10] WScript.Network
    [11] \Microsoft\v.png  
    

### folderol

With those strings, I can more easily understand `folderol`. There’s two
sections that remain.

#### Anti-VM Measures

The first is some attempts to look for certain conditions on the machine that
might look like a sandbox. This is really common in phishing documents, that
don’t want to take malicious actions in sandboxes. This code has two checks:

    
    
        If GetInternetConnectedState = False Then
            MsgBox "Cannot establish Internet connection.", vbCritical, "Error"
            End
        End If
    
        Set fudgel = GetObject(rigmarole(onzo(7)))
        Set twattling = fudgel.ExecQuery(rigmarole(onzo(8)), , 48)
        For Each p In twattling
            Dim pos As Integer
            pos = InStr(LCase(p.Name), "vmw") + InStr(LCase(p.Name), "vmt") + InStr(LCase(p.Name), rigmarole(onzo(9)))
            If pos > 0 Then
                MsgBox rigmarole(onzo(4)), vbCritical, rigmarole(onzo(6))
                End
            End If
        Next
    

The first calls `GetInternetConnectedState` (which is just a wrapper around a
call to the `wininet.dll` [function](https://docs.microsoft.com/en-
us/windows/win32/api/wininet/nf-wininet-internetgetconnectedstate)
`InternetGetConnectedState(0&, 0&)`), and throws an error message box if not
connected to the internet, and then calls `End` to exit.

The second block is checking processes. Here’s how it looks with the strings
substituted in:

    
    
    Set fudgel = GetObject("winmgmts:\\.\root\CIMV2")
      Set twattling = fudgel.ExecQuery("SELECT Name FROM Win32_Process", , 48)
      For Each p In twattling
        Dim pos As Integer
        pos = InStr(LCase(p.Name), "vmw") + InStr(LCase(p.Name), "vmt") + InStr(LCase(p.Name), "vbox")
          If pos > 0 Then
            MsgBox "Sorry, this machine is not supported.", vbCritical, "Error"
            End
    	End If
    Next
    

It uses a WMI object to query for the list of processes. Then it loops over
them, for each checking (case insensitively) if the strings “vmw”, “vmt”, or
“vbox” are present, and if it finds anything, pops a message box and exits.

#### Create and Run File

The rest of the code creates and runs a file. Here it is (with deobfuscated
strings substituted in):

    
    
    xertz = Array(&H11, &H22, &H33, &H44, &H55, &H66, &H77, &H88, &H99, &HAA, &HBB, &HCC, &HDD, &HEE)
    
    wabbit = canoodle(F.T.Text, 0, 168667, xertz)
    mf = Environ("AppData") & "\Microsoft\stomp.mp3"
    Open mf For Binary Lock Read Write As #fn
    Put #fn, , wabbit
    Close #fn
    
    mucolerd = mciSendString("play " & mf, 0&, 0, 0)
    

`xertz` is a short array of numbers. Without looking at `canoodle`, I can
guess that it takes the obfuscated string at `F.T.Text` and decodes it. I’m
guessing that `xertz` is some kind of key. The result is written to the
current users `AppData\Microsoft` directory as `stomp.mp3`. Finally, it plays
the mp3 audio file using the `mciSendString`
[function](https://docs.microsoft.com/en-us/windows/win32/multimedia/playing-
a-device).

### Decode File (canoodle)

`canoodle` does decode a hex string using a passed in array of xor values:

    
    
    Function canoodle(panjandrum As String, ardylo As Integer, s As Long, bibble As Variant) As Byte()
        Dim quean As Long
        Dim cattywampus As Long
        Dim kerfuffle() As Byte
        ReDim kerfuffle(s)
        quean = 0
        For cattywampus = 1 To Len(panjandrum) Step 4
            kerfuffle(quean) = CByte("&H" & Mid(panjandrum, cattywampus + ardylo, 2)) Xor bibble(quean Mod (UBound(bibble) + 1))
            quean = quean + 1
            If quean = UBound(kerfuffle) Then
                Exit For
            End If
        Next cattywampus
        canoodle = kerfuffle
    End Function
    

It loops over the string four characters at a time. It takes two of those
characters, creates a hex value, and then xors against a value from the input
key, `bibble`.

The second arg, `ardylo` is weird, as it’s 0 and unnecessary. This is
something to think about moving forward. Why did they write this such that it
grabs only the first two of four characters and decodes them. There’s another
half of the hex string that’s being ignored, and there’s a way to call it
(with `adrylo` as 2) to access those instead.

Additionally, the third arg, `s` is basically a length check. Why is this
needed if `canoodle` is only called once and it starts by looping over the
length of the hex encoded input?

Leaving the questions aside for now, I’ll show two ways to decode this. First,
in my workbook that isn’t broken, I’ll just copy a modified `folderol` and an
unmodified `canoodle` into a module and run `folderol`:

    
    
    Function canoodle(panjandrum As String, ardylo As Integer, s As Long, bibble As Variant) As Byte()
        Dim quean As Long
        Dim cattywampus As Long
        Dim kerfuffle() As Byte
        ReDim kerfuffle(s)
        quean = 0
        For cattywampus = 1 To Len(panjandrum) Step 4
            kerfuffle(quean) = CByte("&H" & Mid(panjandrum, cattywampus + ardylo, 2)) Xor bibble(quean Mod (UBound(bibble) + 1))
            quean = quean + 1
            If quean = UBound(kerfuffle) Then
                Exit For
            End If
        Next cattywampus
        canoodle = kerfuffle
    End Function
    
    Function folderol()
        Dim wabbit() As Byte
        Dim fn As Integer: fn = FreeFile
        Dim onzo() As String
        Dim mf As String
        Dim xertz As Variant
    
        xertz = Array(&H11, &H22, &H33, &H44, &H55, &H66, &H77, &H88, &H99, &HAA, &HBB, &HCC, &HDD, &HEE)
    
        wabbit = canoodle(F.T.Text, 0, 168667, xertz)
        mf = "F:\04-report\stomp.mp3"
        Open mf For Binary Lock Read Write As #fn
          Put #fn, , wabbit
        Close #fn
    
    End Function
    

Alternatively, I could throw together some Python that does the same thing:

    
    
    #!/usr/bin/env python3
    
    from itertools import cycle
    
    with open('ft-olevba.txt', 'r') as f:
        encoded = f.read().strip()
    
    key = [i*0x11 for i in range(1, 15)]
    out = b''
    for i in range(0, len(encoded), 4):
        out += bytes([int(encoded[i:i+2], 16) ^ key[(i//4) % len(key)]])
        if i > 168667:
            break
    
    with open('stomp.mp3', 'wb') as f:
        f.write(out)
    

To get the hex string, I ran `olevba` against the notebook and directed all
the output to a file. Then I went in and deleted all the lines around the long
hex string to get just that line.

Either way, I get an `mp3` file:

    
    
    root@kali# file stomp.mp3 
    stomp.mp3: Audio file with ID3 version 2.3.0, contains:MPEG ADTS, layer III, v1, 160 kbps, 44.1 kHz, JntStereo
    

The song just plays a beat. But there’s a bunch of hints here. The file name
is “stomp”. Looking at the information about the track, the “Title” and “Band”
are also hints:

    
    
    root@kali# exiftool stomp.mp3 
    ...[snip]...
    ID3 Size                        : 4096
    Publisher                       : FLARE
    Year                            : 2020
    Title                           : This is not what you should be looking at...
    Band                            : P. Code
    Date/Time Original              : 2020
    Duration                        : 8.23 s (approx)
    

“This is not what you should be looking at…” is a good hint, as is the Band,
“P. Code”.

When you edit a VBA macro, the source is kept in the document, but it’s also
compiled into what is called p-code, which is what is actually run. There’s a
technique in VBA documents called VBA stomping, which replaces the source code
for the VBA (what shows in the editor) with something different than what the
compiled p-code does. Because the p-code is os / architecture specific, this
will break the document so that it will only run on machines that match the
one it was written on. That actually could explain why I’m getting errors no
matter what in this file.

[Evil Clippy](https://github.com/outflanknl/EvilClippy) is one tool that can
be used to stomp VBA code.

## RE - p-code

### pcodedmp

To understand how p-code works,
[pcodedmp](https://github.com/bontchev/pcodedmp) is a good tool to view the
raw code. In addition to other things, it will show the raw pcode in each
sheet / module. For example, here’s the p-code related to the `rigmarole`
function in `report.xls` (with comments added by me):

    
    
    Line #10:
            FuncDefn (Function rigmarole(es As String, id_FFFE As String) As String)
    Line #11:
            Dim
            VarDefn furphy (As String)
    Line #12:
            Dim                                                        
            VarDefn c (As Integer)                                     
    Line #13:                                                                     
            Dim                                                                   
            VarDefn s (As String)                                                 
    Line #14:                                                                     
            Dim                                                                   
            VarDefn cc (As Integer)                                               
    Line #15:                                                                     
            LitStr 0x0000 ""                                                      
            St furphy                                                             
    Line #16:              // for loop in lines 16-21                                                       
            StartForVariable    // identify variable as i                                                  
            Ld i                                                                  
            EndForVariable                                                        
            LitDI2 0x0001                                                         
            Ld es                                                                 
            FnLen                                                                 
            LitDI2 0x0004                                                         
            ForStep             // sets for loop with three args, (1, Len(es), 4)
    Line #17:                                                                     
            LitStr 0x0002 "&H"                                                    
            Ld es                                                                 
            Ld i                                                                  
            LitDI2 0x0002                                                         
            ArgsLd Mid 0x0003   // Mid(es, i, 2)                                                  
            Concat                                                                
            ArgsLd CDec 0x0001  // CDes("&H" & result of Mid)                                                  
            St c                // store as c                                                 
    Line #18:                                                                     
            LitStr 0x0002 "&H"                                                    
            Ld es                                                                 
            Ld i                                                                  
            LitDI2 0x0002                                                         
            Add                 // Add(i, 2)                                                  
            LitDI2 0x0002                                                         
            ArgsLd Mid 0x0003   // Mid(es, i + 2, 2)                                                  
            Concat                                                                
            ArgsLd CDec 0x0001  // CDes("&H" & result of Mid)                                                  
            St s                // store as s                                                  
    Line #19:                                                                     
            Ld c                                                                  
            Ld s                                                                  
            Sub                                                                   
            St cc              // cc = c - s                                                   
    Line #20:                                                                     
            Ld furphy                                                             
            Ld cc                                                                 
            ArgsLd Chr 0x0001                                                     
            Add                                                                   
            St furphy          // furphy = furphy + Chr(cc)                                                   
    Line #21:                                                                     
            StartForVariable                                                      
            Ld i                                                                  
            EndForVariable                                                        
            NextVar                                                               
    Line #22:                                                                     
            Ld furphy                                                             
            St rigmarole                                                          
    Line #23:                                                                     
            EndFunc
    

I can compare this to the VBA to get a feel for how it works. Arguments are
pushed into a stack, and then function pull from the start and return values
to that stack.

Looking through the code, I noticed some differences at line 31:

    
    
    Line #31:
            Dim
            LitDI2 0x0000
            LitDI2 0x0007
            VarDefn buff (As Byte)  
    

That’s a new array of bytes being defined, `buff`, which isn’t in the VBA.
Later at line 53, there’s more:

    
    
    Line #53:
            SetStmt
            LitDI2 0x000A
            ArgsLd onzo 0x0001
            ArgsLd rigmarole 0x0001
            ArgsLd CreateObject 0x0001
            Set groke         // groke = CreateObject(rigmarole(onzo(0xA)))
            
    Line #54:
            Ld groke
            MemLd UserDomain
            St firkin        // firkin = groke.UserDomain
    

This code has definitely been stompped.

### pcode2code

In Googling around for p-code references, I found
[pcode2code](https://github.com/Big5-sec/pcode2code). It will try to convert
p-code back into VBA and display it. When I ran it against `report.xls`, there
was a new section that replaced what where the MP3 was decoded, written to
disk, and played (with `rigmarole` encoded strings replaced):

    
    
    Set groke = CreateObject("WScript.Network")
    firkin = groke.UserDomain
    If firkin <> "FLARE-ON" Then
    MsgBox "Sorry, this machine is not supported.", vbCritical, "Error" 
    End
    End If
    
    n = Len(firkin)
    For i = 1 To n
    buff(n - i) = Asc(Mid$(firkin, i, 1))
    Next
    
    wabbit = canoodle(F.T.Text, 2, 285729, buff)
    mf = Environ("AppData") & "\Microsoft\v.png"
    Open mf For Binary Lock Read Write As #fn
    ' a generic exception occurred at line 68: can only concatenate str (not "NoneType") to str
    '       # Ld fn
    '       # Sharp
    '       # LitDefault
    '       # Ld wabbit
    '       # PutRec
    Close #fn
    
    Set panuding = Sheet1.Shapes.AddPicture(mf, False, True, 12, 22, 600, 310)
    

It’s slightly broken at the file write, but the general idea is clear. It
first creates a `WScript.Network` object and gets the `UserDomain` attribute.
If that is not “FLARE-ON”, it pops a message box and exits. Then it creates
the key which is “NO-ERALF” (FLARE-ON backwards). The offset is two, so it is
getting the bytes that were ignored in the previous decode. This time it saves
as `AppData\Microsoft\v.png`.

### Decode Image

Just like before, I can do this in the macro editor, making a function to
write the file:

    
    
    Function dumpimage()
        Dim buff(0 To 7) As Byte
        Dim fn As Integer: fn = FreeFile
        Dim mf As String
    
        firkin = "FLARE-ON"
        n = Len(firkin)
        For i = 1 To n
          buff(n - i) = Asc(Mid$(firkin, i, 1))
        Next
        
        wabbit = canoodle(F.T.Text, 2, 285729, buff)
        mf = "F:\04-report\av.png"
        Open mf For Binary Lock Read Write As #fn
          Put #fn, , wabbit
        Close #fn
    
    End Function
    

Or I can create a new Python script with slight mods to the previous:

    
    
    #!/usr/bin/env python3
    
    from itertools import cycle
    
    with open('ft-olevba.txt', 'r') as f:
        encoded = f.read().strip()
    
    key = b'FLARE-ON'[::-1]
    out = b''
    for i in range(0, len(encoded), 4):
        out += bytes([int(encoded[i+2:i+4], 16) ^ key[(i//4) % len(key)]])
        if i//4 > 285729:
            break
    
    with open('v.png', 'wb') as f:
        f.write(out)
    

Either way, I get an image with the flag:

![](https://0xdfimages.gitlab.io/img/flareon-report-v.png)

**Flag: thi5_cou1d_h4v3_b33n_b4d@flare-on.com@flare-on.com**

[](/flare-on-2020/report)

