# Commando VM: Looking Around

[home-lab](/tags#home-lab ) [commando](/tags#commando )
[fireeye](/tags#fireeye ) [openvpn](/tags#openvpn ) [burp](/tags#burp )
[7z](/tags#7z ) [winrar](/tags#winrar ) [cmder](/tags#cmder )
[greenshot](/tags#greenshot ) [windump](/tags#windump )
[payloadsallthethings](/tags#payloadsallthethings ) [seclists](/tags#seclists
) [fuzzdb](/tags#fuzzdb ) [foxyproxy](/tags#foxyproxy ) [x64dbg](/tags#x64dbg
) [dnspy](/tags#dnspy ) [ida](/tags#ida ) [ghidra](/tags#ghidra )
[gobuster](/tags#gobuster ) [wfuzz](/tags#wfuzz )  
  
Apr 10, 2019

  * [Installation](/2019/04/09/commando-vm-installation.html)
  * Looking Around
  * [Lessons Learned](/2019/04/15/commando-vm-lessons.html)

![](https://0xdfimages.gitlab.io/img/commando-overview-cover.png)Having built
my CommandoVM in a [previous post](/2019/04/09/commando-vm-installation.html),
now I am going to look at what’s installed, and what else I might want to add
to the distribution. I’ll start with some tweaks I made to get the box into
shape, check out what tools are present, and add some that I notice missing.
After this, in I’ll use the VM to work a HTB target, and report back on in a
future post.

## Accounts

I probably should have addressed this in the opening post. Since I’m using
this machine exclusively to work on [HackTheBox](https://www.hackthebox.eu)
and other CTF challenges, I’m going to take a similar approach as I did with
Kali where I run as root, and run a single user in the Administrators group.
If I were a PenTester dealing with customer or other sensitive data, I would
look into running as a non-privileged user and increasing my operational
security.

## Getting Connected - OpenVPN

I’ll needed to connect to the HackTheBox vpn. In Kali, I’d simple run `openvpn
[my config file]` in a terminal window. In Windows, it’s different.

First, I enabled the OpenVPN service. I hit windows key and then typed
services, and opened it. Then I scrolled down to OpenVPNService, right
clicked, and hit run. I did the same with the OpenVPN Interactive Service. I
then double clicked on both, and changed their startup type to Automatic:

![1554834610613](https://0xdfimages.gitlab.io/img/1554834610613.png)

Then I opened OpenVPN from the start menu. It’s important to run this as an
Administer, as only an admin can add the interfaces necessary to complete the
connection. The first thing I got was a popup saying that there were no config
files found:

![1554834665674](https://0xdfimages.gitlab.io/img/1554834665674.png)

I also noticed the OpenVPN icon appears in the notification icons:

![1554834726264](https://0xdfimages.gitlab.io/img/1554834726264.png)

I right clicked on it, and selected “Import file…”. I found `0xdf.ovpn`, and
it imported successfully. Now I can right click on the status icon and say
“Connect”. The status window pops up, and after a minute, goes away. The icon
is now green:

![1554834844651](https://0xdfimages.gitlab.io/img/1554834844651.png)

And I can `ping` htb hosts:

    
    
    C:\Users\0xdf>\Windows\System32\PING.EXE 10.10.10.113
    
    Pinging 10.10.10.113 with 32 bytes of data:
    Reply from 10.10.10.113: bytes=32 time=18ms TTL=63
    Reply from 10.10.10.113: bytes=32 time=18ms TTL=63
    Reply from 10.10.10.113: bytes=32 time=17ms TTL=63
    Reply from 10.10.10.113: bytes=32 time=20ms TTL=63
    
    Ping statistics for 10.10.10.113:
        Packets: Sent = 4, Received = 4, Lost = 0 (0% los." | relative_url }}),
    Approximate round trip times in milli-seconds:
        Minimum = 17ms, Maximum = 20ms, Average = 18ms
    

## Configurations

### Path

When I opened `cmd` and tried to ping something to check my VPN connection, I
got a strange result:

    
    
    C:\Users\0xdf>ping 10.10.10.109
    Use: C:\Python27\Scripts\ping.py <src ip> <dst ip>
    

If I try `ping.exe`, it works as expected:

    
    
    C:\Users\0xdf>ping.exe 10.10.10.109
    
    Pinging 10.10.10.109 with 32 bytes of data:
    Reply from 10.10.10.109: bytes=32 time=20ms TTL=63
    Reply from 10.10.10.109: bytes=32 time=21ms TTL=63
    Reply from 10.10.10.109: bytes=32 time=18ms TTL=63
    Reply from 10.10.10.109: bytes=32 time=19ms TTL=63
    
    Ping statistics for 10.10.10.109:
        Packets: Sent = 4, Received = 4, Lost = 0 (0% los." | relative_url }}),
    Approximate round trip times in milli-seconds:
        Minimum = 18ms, Maximum = 21ms, Average = 19ms
    

Looking at the path shows me why:

    
    
    C:\Users\0xdf>echo %PATH%
    C:\Python37\Scripts\;C:\Python37\;C:\Python27\;C:\Python27\Scripts;C:\Program Files (x8." | relative_url }})\Common Files\Oracle\Java\javapath;C:\ProgramData\Boxstarter;C:\Windows\system32;C:\Windows;C:\Windows\System32\Wbem;C:\Windows\System32\WindowsPowerShell\v1.0\;C:\Windows\System32\OpenSSH\;C:\ProgramData\chocolatey\bin;C:\Program Files\Git\cmd;C:\Program Files\Microsoft VS Code\bin;C:\Go\bin;C:\Program Files\TortoiseSVN\bin;C:\Program Files\Java\jdk1.8.0_201\bin;C:\Program Files\Microsoft SQL Server\Client SDK\ODBC\130\Tools\Binn\;C:\metasploit-framework\bin\;C:\Program Files\dotnet\;C:\Program Files\Microsoft SQL Server\130\Tools\Binn\;C:\Program Files (x86)\GNU\GnuPG\pub;C:\Users\0xdf\AppData\Local\Microsoft\WindowsApps;C:\tools\Cmder;C:\Users\0xdf\go\bin;C:\Program Files (x86)\Nmap;C:\Users\0xdf\AppData\Local\Programs\Fiddler;C:\Tools\ADOffline;C:\Tools\CredNinja;C:\Tools\demiguise;C:\Tools\Get-ReconInfo;C:\Tools\Grouper2;C:\Tools\Inveigh;C:\Tools\Invoke-CradleCrafter;C:\Tools\Invoke-DCOM;C:\Tools\Invoke-Obfuscation;C:\Tools\KeeThief;C:\Tools\mimikittenz;C:\Tools\PoshC2;C:\Tools\PowerLessShell;C:\Tools\PowerPriv;C:\Tools\PowerSploit;C:\Tools\PrivExchange;C:\Tools\PSAttack;C:\Tools\PSReflect;C:\Tools\ruler;C:\Tools\SpoolerScanner;C:\Tools\vssown;C:\Tools\WMImplant;C:\Tools\zBang;C:\Users\0xdf\.dotnet\tools;C:\Tools\Covenant\Covenant;C:\Tools\Elite\Elite
    

I’m sure it makes sense to have all those things in the path, but I’d like to
have system32 at the front of that list. I’ll hit Windows key, and type “This
PC”, then right click and select “Properties”. –> “Advanced System Settings”
–> Environment Variables”. I’ll find “Path” in System Variables (the bottom
window) and click edit:

![1554907562356](https://0xdfimages.gitlab.io/img/1554907562356.png)

I’ll select `C:\Windows\System32` and click “Move Up” until it’s at the top.
Then hit ok, and `ping` works again.

### Burp

I almost always want Burp open when I’m using this VM, but for some reason,
Windows doesn’t like pinning shortcuts to jar files to the taskbar. I overcame
this by creating a copy of the shortcut onto my desktop. Then I edited the
“Target” from `C:\ProgramData\chocolatey\lib\burp-suite-free-
edition\tools\app\burpsuite.jar` to `%SystemRoot%\System32\cmd.exe /C
"C:\ProgramData\chocolatey\lib\burp-suite-free-
edition\tools\app\burpsuite.jar"`. I could right click on that shortcut,
select “Pin to taskbar”, and now I had it handy. I can also delete the
shortcut on the desktop and the pinned shortcut still works.

![1554903659290](https://0xdfimages.gitlab.io/img/1554903659290.png)

But that shortcut launches a cmd window that just waits for Burp to close.
That’s annoying:

![1554903706332](https://0xdfimages.gitlab.io/img/1554903706332.png)

I’ll change the target again to `%SystemRoot%\System32\cmd.exe /C "start ^"^"
^"C:\ProgramData\chocolatey\lib\burp-suite-free-
edition\tools\app\burpsuite.jar^"`. Now it starts Burp and then cmd window
pops for a flash, but then goes away.

### 7zip > WinRar

All archive formats are set to open in WinRar by default. I don’t love WinRar,
and much prefer 7zip, so I want to change 7zip to be the default. I’ll open
7zip by hitting Windows key and starting to type it out. When I see it, I’ll
run it as admin (necessary to change default extension handling). Under
“Tools” –> “Options…” the first thing to pop up is the “System” tab, which has
a list of types to associate 7zip with. I’ll click on each until it is how I
want it:

![1554907916275](https://0xdfimages.gitlab.io/img/1554907916275.png)

## Interesting Tools

### General Tools

On the desktop there’s a shortcut called “Tools”. It points to
`C:\ProgramData\Microsoft\Windows\Start Menu\Programs\Tool List`. In it is an
organized folder structure of tools:

![1554943531987](https://0xdfimages.gitlab.io/img/1554943531987.png)

This directory is worth exploring to get a feel for what’s there.

### cmder

The recommended shell in CommandoVM is cmder. It can run `cmd`, `powershell`,
or `bash` in panes and tabs. Here’s an example with bash on top and cmd on
bottom:

![1554943675461](https://0xdfimages.gitlab.io/img/1554943675461.png)

I’ve played around with it a bit. I can Ctrl+t to create a new tab, and
Ctrl+Tab to switch between tabs. When I create a tab, a pop up asks me what it
should be, and I can choose various shell types:

![1554917944899](https://0xdfimages.gitlab.io/img/1554917944899.png)

I can also give a directory to start in, the user to run as, if it should be a
new tab or split window:

![1554917979650](https://0xdfimages.gitlab.io/img/1554917979650.png)

I can also tell it to create a new window, and then I can Alt+Tab between
them.

There’s not enough keyboard shortcut support built in for my liking off the
bat, but I might be able to get used it it, and it looks like there’s a
powerful macro language that might allow me to define tmux-like shortcuts.

### GreenShot

GreenShot is pinned in the taskbar by Commando-VM, and is a pretty slick
screen capture tool that I was previously unfamiliar with.

When I click it, no windows open, but rather a Greenshot icon shows up in the
System Tray:
![1554908025326](https://0xdfimages.gitlab.io/img/1554908025326.png)

Once it’s running, I can use the PrintScreen button to get a crosshairs. I can
then click and drag out the area to capture. When I let go, it prompts me as
to what to do to.

![](https://0xdfimages.gitlab.io/img/commando-greenshot.gif)

### WinDump

I use `tcpdump` all the time on Kali, and it seems that `WinDump.exe` will do
basically the same thing. There’s also Wireshark on the box, but I like to
work command line. `WinDump` takes basically the same arguments as `tcpdump`,
so if I want to watch for pings, I can do something like this and see the
pings:

    
    
    λ windump.exe -i3 -n icmp
    C:\ProgramData\chocolatey\lib\windump.fireeye\tools\windump.exe: listening on \Device\NPF_{FA0211FF-7A30-48BA-954A-3B4D4C14D909}
    01:36:02.716853 IP 10.10.14.14 > 10.10.10.109: ICMP echo reply, id 9443, seq 1, length 64
    01:36:03.719388 IP 10.10.14.14 > 10.10.10.109: ICMP echo reply, id 9443, seq 2, length 64
    

I did have to adjust my windows Firewall to allow the pings in bound by
enabling these rules:

![1554943069187](https://0xdfimages.gitlab.io/img/1554943069187.png)

That’s a state I’ll want anyway, so that if I’m trying to test for RCE by
pinging myself, I can see the pings.

### Wordlists

[PayloadsAllTheThings](https://github.com/swisskyrepo/PayloadsAllTheThings),
[SecLists](https://github.com/danielmiessler/SecLists), and
[FuzzDB](https://github.com/fuzzdb-project/fuzzdb) all install by default.
SecLists was actually failing to install when I originally built this VM, but
[that has been fixed](https://github.com/fireeye/commando-vm/issues/38). You
can find shortcuts starting from the `Tools` shortcut on the desktop, in
`Tools\Wordlists`.

### Others

The full list of tools is on the [Commando-VM GitHub
Page](https://github.com/fireeye/commando-vm). So others that I found worth
mentioning were Subline Text as an editor, both Visual Studio Code and Visual
Studio development environments and Wireshark. SysInternals, a handful of C2
frameworks and obfuscation frameworks, and other interesting PowerShell
scripts can be found just surfing through the Tools List directory. There’s a
stand-alone copy of CyberChef, HxD, and KeepPass. Like I said earlier, once
you install, it’s worth taking a minute to look through the tool-set.

## Additional Tools

### FoxyProxy

FoxyProxy is indispensable for me as I send most of my web traffic to target
through Burp, but don’t want my Google searches to go there. I’ll head to the
[FoxyProxy website](https://addons.mozilla.org/en-US/firefox/addon/foxyproxy-
standard) and click “+ Add to Firefox” and after a few clicks it’s installed.
I see it in the top right of Firefox:

![1554904140553](https://0xdfimages.gitlab.io/img/1554904140553.png)

Now I’ll set up Burp. I’ll click on the FoxyProxy icon shown above, and select
“Options”. In the page that comes up, I’ll select “Add”. I’ll set the Type to
HTTP, call it Burp, and point it to localhost:8080:

![1554904221667](https://0xdfimages.gitlab.io/img/1554904221667.png)

Now I’ll hit “Save & Edit Patterns”. I’m going to set it up so that traffic to
hackthebox targets goes through Burp, and the rest does not. I’ll start by
using the ![1554904371319](https://0xdfimages.gitlab.io/img/1554904371319.png)
to delete all the rules that are already there. Then I’ll hit “New White” and
create my first rule. I’ll name it htb, and the pattern will be `*10.10.10.*`.
This should direct all traffic going to a 10.10.10.0/24 address to Burp. I’ll
hit new-rule again and add one with pattern `*.htb*` to get domain traffic as
well.

![1554904513781](https://0xdfimages.gitlab.io/img/1554904513781.png)

Now I can hit save and close that page. I’ll click on the Foxy icon again, and
select “Use Enabled Proxies by Patterns and Priority”:

![1554905024533](https://0xdfimages.gitlab.io/img/1554905024533.png)

Now, I can visit `http:10.10.10.109` and get the Vault page through Burp (and
see the green Burp on the FP icon):

![1554905168586](https://0xdfimages.gitlab.io/img/1554905168586.png)

And without changing the settings, open another tab and go to `google.com` and
it doesn’t go through burp:

![1554905201308](https://0xdfimages.gitlab.io/img/1554905201308.png)

### RE

The distribution already has `x64dbg` (and `x32dbg`) for Windows debugging and
`dnSpy` for dotNET reversing and debugging. Those are both tools I would add
if they weren’t there.

I want to add [IDA](https://www.hex-
rays.com/products/ida/support/download_freeware.shtml) and
[Ghidra](https://www.ghidra-sre.org/). I’ll grab each from their sites. IDA
installs by running the installer.

For Ghidra, I’ll open the archive and drop the `ghidra_9.0.2` folder into
`C:\Program Files`, and drop a shortcut to `ghidrarun.bat` somewhere useful,
like in the tools directory with all the shortcuts. I’ll also need to get the
[latest JDK
installer](https://www.oracle.com/technetwork/java/javase/downloads/jdk12-downloads-5295953.html)
and run it.

### Dirbuster Lists

I regularly use the [dirbuster wordlists](https://github.com/daviddias/node-
dirbuster/tree/master/lists) for web enumeration. I created a directory in
`\tools\` and used `wget` to get them:

    
    
    C:\Tools\dirbuster-lists>wget https://raw.githubusercontent.com/daviddias/node-dirbuster/master/lists/directory-list-2.3-medium.txt
    --16:51:22--  https://raw.githubusercontent.com/daviddias/node-dirbuster/master/lists/directory-list-2.3-medium.txt
               => `directory-list-2.3-medium.txt'
    Resolving raw.githubusercontent.com... 151.101.248.133
    Connecting to raw.githubusercontent.com[151.101.248.133]:443... connected.
    HTTP request sent, awaiting response... 200 OK
    Length: 2,200,599 [text/plain]
    
    100%[====================================>] 2,200,599     --.--K/s
    
    16:51:22 (27.26 MB/s) - `directory-list-2.3-medium.txt' saved [2200599/2200599]
    
    
    C:\Tools\dirbuster-lists>wget https://raw.githubusercontent.com/daviddias/node-dirbuster/master/lists/directory-list-2.3-small.txt
    --16:51:30--  https://raw.githubusercontent.com/daviddias/node-dirbuster/master/lists/directory-list-2.3-small.txt
               => `directory-list-2.3-small.txt'
    Resolving raw.githubusercontent.com... 151.101.248.133
    Connecting to raw.githubusercontent.com[151.101.248.133]:443... connected.
    HTTP request sent, awaiting response... 200 OK
    Length: 813,102 [text/plain]
    
    100%[====================================>] 813,102       --.--K/s
    
    16:51:30 (25.85 MB/s) - `directory-list-2.3-small.txt' saved [813102/813102]
    
    
    C:\Tools\dirbuster-lists>wget https://raw.githubusercontent.com/daviddias/node-dirbuster/master/lists/directory-list-lowercase-2.3-small.txt
    --16:51:47--  https://raw.githubusercontent.com/daviddias/node-dirbuster/master/lists/directory-list-lowercase-2.3-small.txt
               => `directory-list-lowercase-2.3-small.txt'
    Resolving raw.githubusercontent.com... 151.101.248.133
    Connecting to raw.githubusercontent.com[151.101.248.133]:443... connected.
    HTTP request sent, awaiting response... 200 OK
    Length: 758,408 [text/plain]
    
    100%[====================================>] 758,408       --.--K/s
    
    16:51:47 (15.72 MB/s) - `directory-list-lowercase-2.3-small.txt' saved [758408/758408]
    
    
    C:\Tools\dirbuster-lists>wget https://raw.githubusercontent.com/daviddias/node-dirbuster/master/lists/directory-list-lowercase-2.3-medium.txt
    --16:51:54--  https://raw.githubusercontent.com/daviddias/node-dirbuster/master/lists/directory-list-lowercase-2.3-medium.txt
               => `directory-list-lowercase-2.3-medium.txt'
    Resolving raw.githubusercontent.com... 151.101.248.133
    Connecting to raw.githubusercontent.com[151.101.248.133]:443... connected.
    HTTP request sent, awaiting response... 200 OK
    Length: 2,057,312 [text/plain]
    
    100%[====================================>] 2,057,312     --.--K/s
    
    16:51:54 (31.65 MB/s) - `directory-list-lowercase-2.3-medium.txt' saved [2057312/2057312]
    

### Gobuster

I prefer `gobuster` for website path enumerations (and more). I grabbed the
latest install from the [releases
page](https://github.com/OJ/gobuster/releases) and dropped it at
`C:\Tools\gobuster\gobuster.exe`. Then I added that directory to my path. I
tested it on vault:

    
    
    C:\Users\0xdf>gobuster -u http://10.10.10.109/sparklays/ -w \Tools\dirbuster-lists\directory-list-2.3-small.txt -t 50
    
    =====================================================
    Gobuster v2.0.1              OJ Reeves (@TheColonial)
    =====================================================
    [+] Mode         : dir
    [+] Url/Domain   : http://10.10.10.109/sparklays/
    [+] Threads      : 50
    [+] Wordlist     : \Tools\dirbuster-lists\directory-list-2.3-small.txt
    [+] Status codes : 200,204,301,302,307,403
    [+] Timeout      : 10s
    =====================================================
    2019/04/10 17:29:45 Starting gobuster
    =====================================================
    /design (Status: 301) (0.53%)
    =====================================================
    2019/04/10 17:30:50 Finished
    =====================================================
    

This version seems to work fine, though I did submit a [feature
request](https://github.com/fireeye/commando-vm/issues/39) to get it installed
by default.

### WFuzz

Installing `wfuzz` _should_ be as simple as `pip install wfuzz`. However,
there is a curveball. On Linux, `python` and `python3` are typically different
binaries. On windows, both are named `python`, and both are in my path:

    
    
    C:\Users\0xdf>where python
    C:\Python37\python.exe
    C:\Python27\python.exe
    

And the one that runs is `python3`:

    
    
    C:\Users\0xdf>python --version
    Python 3.7.3
    
    C:\Users\0xdf>pip --version
    pip 19.0.3 from c:\python37\lib\site-packages\pip (python 3.7)
    

I had a hard time getting pycurl to install using python3’s `pip`, but when I
switched to python2’s `pip`, it worked instantly:

    
    
    C:\Users\0xdf>\Python27\python.exe -m pip install wfuzz
    DEPRECATION: Python 2.7 will reach the end of its life on January 1st, 2020. Please upgrade your Python as Python 2.7 won't be maintained after that date. A future version of pip will drop support for Python 2.7.
    Collecting wfuzz
      Downloading https://files.pythonhosted.org/packages/1a/72/05b7a91322092a2b99edfab8e1fb4bcbd2c957e6cb8ec1304adab6563028/wfuzz-2.3.4.tar.gz (81kB)
        100% |UUUUUUUUUUUUUUUUUUUUUUUUUUUUUUUU| 81kB ...
    Requirement already satisfied: pycurl in c:\python27\lib\site-packages (from wfuzz) (7.43.0.2)
    Requirement already satisfied: pyparsing in c:\python27\lib\site-packages (from wfuzz) (2.4.0)
    Requirement already satisfied: future in c:\python27\lib\site-packages (from wfuzz) (0.17.1)
    Requirement already satisfied: six in c:\python27\lib\site-packages (from wfuzz) (1.12.0)
    Collecting configparser (from wfuzz)
      Using cached https://files.pythonhosted.org/packages/ba/05/6c96328e92e625fc31445d24d75a2c92ef9ba34fc5b037fe69693c362a0d/configparser-3.7.4-py2.py3-none-any.whl
    Requirement already satisfied: chardet in c:\python27\lib\site-packages (from wfuzz) (3.0.4)
    Collecting colorama (from wfuzz)
      Downloading https://files.pythonhosted.org/packages/4f/a6/728666f39bfff1719fc94c481890b2106837da9318031f71a8424b662e12/colorama-0.4.1-py2.py3-none-any.whl
    Installing collected packages: configparser, colorama, wfuzz
      Running setup.py install for wfuzz ... done
    Successfully installed colorama-0.4.1 configparser-3.7.4 wfuzz-2.3.4
    

It runs… poorly. It won’t run beyond a crawl in cmd or powershell. It prints
each line, and then removes it if hidden very slowly. But I got it to run in
cmder. The text updating is clearly optimized for Linux. And it seems to run a
little slow. That said, it still works:

    
    
    λ wfuzz -w \Tools\dirbuster-lists\directory-list-2.3-small.txt -u http://10.10.10.109/sparklays/FUZZ --hw 32 -t 50
    ********************************************************
    * Wfuzz 2.3.4 - The Web Fuzzer                         *
    ********************************************************
    
    Target: http://10.10.10.109/sparklays/FUZZ
    Total requests: 87664
    
    ==================================================================
    ID   Response   Lines      Word         Chars          Payload
    ==================================================================
    
    000370:  C=301      9 L       28 W          323 Ch        "design"
    000680:  C=404
    Finishing pending requests...
    ^C
    

I [put in a feature request](https://github.com/fireeye/commando-vm/issues/40)
to see if they can get it working better and bring it by default, and they
said it has been added to the roadmap.

## Conclusion

That’s all for my initial overview. There’s a ton I didn’t cover. Leave a
comment with your favorite thing I didn’t talk about that people should know
about, or what you changed or would change in your VM.

Up next, I’m going to try to do a box through this VM, and report back on what
worked and what I struggled with.

[« Installation](/2019/04/09/commando-vm-installation.html)[Lessons Learned
»](/2019/04/15/commando-vm-lessons.html)

[](/2019/04/10/commando-vm-overview.html)

