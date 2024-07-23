# PWK Notes: SMB Enumeration Checklist [Updated]

[oscp](/tags#oscp ) [pwk](/tags#pwk ) [enumeration](/tags#enumeration )
[smb](/tags#smb ) [nmblookup](/tags#nmblookup ) [smbclient](/tags#smbclient )
[rpcclient](/tags#rpcclient ) [nmap](/tags#nmap )
[enum4linux](/tags#enum4linux ) [smbmap](/tags#smbmap )  
  
Dec 2, 2018

PWK Notes: SMB Enumeration Checklist [Updated]

**🚨[Updated for 2024] Check out the latest version of this
post[here](/2024/03/21/smb-cheat-sheet.html).🚨**

[Update 2018-12-02] I just learned about smbmap, which is just great. Adding
it to the original post. Beyond the enumeration I show here, it will also help
enumerate shares that are readable, and can ever execute commands on writable
shares. [Original] As I’ve been working through PWK/OSCP for the last month,
one thing I’ve noticed is that enumeration of SMB is tricky, and different
tools fail / succeed on different hosts. With some input from the NetSecFocus
group, I’m building out an SMB enumeration check list here. I’ll include
examples, but where I use [PWK labs](https://www.offensive-
security.com/information-security-training/penetration-testing-training-kali-
linux/), I’ll anonymize the data per their rules. If I’m missing something,
leave a comment.

## Checklist

  * Enumerate Hostname - `nmblookup -A [ip]`
  * List Shares 
    * `smbmap -H [ip/hostname]`
    * `echo exit | smbclient -L \\\\[ip]`
    * `nmap --script smb-enum-shares -p 139,445 [ip]`
  * Check Null Sessions 
    * `smbmap -H [ip/hostname]`
    * `rpcclient -U "" -N [ip]`
    * `smbclient \\\\[ip]\\[share name]`
  * Check for Vulnerabilities - `nmap --script smb-vuln* -p 139,445 [ip]`
  * Overall Scan - `enum4linux -a [ip]`
  * Manual Inspection 
    * `smbver.sh [IP] (port)` [Samba]
    * check pcap

## Tools

  * `nmblookup` \- collects NetBIOS over TCP/IP client used to lookup NetBIOS names.
  * `smbclient` \- an ftp-like client to access SMB shares
  * `nmap` \- general scanner, with scripts
  * `rpcclient` \- tool to execute client side MS-RPC functions
  * `enum4linux` \- enumerates various smb functions
  * `wireshark`

## Details

### Enumerate Hostname

#### nmblookup

`nmblookup -A [IP]`

  * `-A` \- look up by IP address

Example:

    
    
    root@kali:~# nmblookup -A [ip]
    Looking up status of [ip]
            [hostname]      <00> -         M <ACTIVE>
            [hostname]      <20> -         M <ACTIVE>
            WORKGROUP       <00> - <GROUP> M <ACTIVE>
            WORKGROUP       <1e> - <GROUP> M <ACTIVE>
                            <03> -         M <ACTIVE>
            INet~Services   <1c> - <GROUP> M <ACTIVE>
            IS~[hostname]   <00> -         M <ACTIVE>
    
            MAC Address = 00-50-56-XX-XX-XX
    

### List Shares

#### smbmap

`smbmap -H [ip/hostname]`

This command will show you the shares on the host, as well as your access to
them.

Example:

    
    
    root@kali:/# smbmap -H [ip]
    [+] Finding open SMB ports....
    [+] User SMB session established on [ip]...
    [+] IP: [ip]:445        Name: [ip]                                      
            Disk                                                    Permissions
            ----                                                    -----------
            ADMIN$                                                  NO ACCESS
            C$                                                      NO ACCESS
            IPC$                                                    NO ACCESS
            NETLOGON                                                NO ACCESS
            Replication                                             READ ONLY
            SYSVOL                                                  NO ACCESS
    

If you get credentials, you can re-run to show new access:

    
    
    root@kali:/# smbmap -H [ip] -d [domain] -u [user] -p [password]
    [+] Finding open SMB ports....
    [+] User SMB session established on [ip]...
    [+] IP: [ip]:445        Name: [ip]                                      
            Disk                                                    Permissions
            ----                                                    -----------
            ADMIN$                                                  NO ACCESS
            C$                                                      NO ACCESS
            IPC$                                                    NO ACCESS
            NETLOGON                                                READ ONLY
            Replication                                             READ ONLY
            SYSVOL                                                  READ ONLY
    

#### smbclient

`echo exit | smbclient -L \\\\[ip]`

  * exit takes care of any password request that might pop up, since we’re checking for null login
  * `-L` \- get a list of shares for the given host

Example:

    
    
    root@kali:~# smbclient -L \\[ip]
    Enter WORKGROUP\root's password:
    
            Sharename       Type      Comment
            ---------       ----      -------
            IPC$            IPC       Remote IPC
            share           Disk
            wwwroot         Disk
            ADMIN$          Disk      Remote Admin
            C$              Disk      Default share
    Reconnecting with SMB1 for workgroup listing.
    
            Server               Comment
            ---------            -------
    
            Workgroup            Master
            ---------            -------
    

#### nmap

`nmap --script smb-enum-shares -p 139,445 [ip]`

  * `--script smb-enum-shares` \- specific smb enumeration script
  * `-p 139,445` \- specify smb ports

Example:

    
    
    root@kali:~# nmap --script smb-enum-shares -p 139,445 [ip]
    Starting Nmap 7.70 ( https://nmap.org ) at 2018-09-27 16:25 EDT
    Nmap scan report for [ip]
    Host is up (0.037s latency).
    
    PORT    STATE SERVICE
    139/tcp open  netbios-ssn
    445/tcp open  microsoft-ds
    MAC Address: 00:50:56:XX:XX:XX (VMware)
    
    Host script results:
    | smb-enum-shares:
    |   account_used: guest
    |   \\[ip]\ADMIN$:
    |     Type: STYPE_DISKTREE_HIDDEN
    |     Comment: Remote Admin
    |     Anonymous access: <none>
    |     Current user access: <none>
    |   \\[ip]\C$:
    |     Type: STYPE_DISKTREE_HIDDEN
    |     Comment: Default share
    |     Anonymous access: <none>
    |     Current user access: <none>
    |   \\[ip]\IPC$:
    |     Type: STYPE_IPC_HIDDEN
    |     Comment: Remote IPC
    |     Anonymous access: READ
    |     Current user access: READ/WRITE
    |   \\[ip]\share:
    |     Type: STYPE_DISKTREE
    |     Comment:
    |     Anonymous access: <none>
    |     Current user access: READ/WRITE
    |   \\[ip]\wwwroot:
    |     Type: STYPE_DISKTREE
    |     Comment:
    |     Anonymous access: <none>
    |_    Current user access: READ
    
    Nmap done: 1 IP address (1 host up) scanned in 10.93 seconds
    

### Check Null Sessions

#### smbmap

`smbmap -H [ip/hostname]` will show what you can do with given credentials (or
null session if no credentials). See examples in the previous section.

#### rpcclient

`rpcclient -U "" -N [ip]`

  * `-U ""` \- null session
  * `-N` \- no password

Example:

    
    
    root@kali:~# rpcclient -U "" -N [ip]
    rpcclient $>
    

From there, you can run rpc commands.

#### smbclient

`smbclient \\\\[ip]\\[share name]`

This will attempt to connect to the share. Can try without a password (or
sending a blank password) and still potentially connect.

Example:

    
    
    root@kali:~/pwk/lab/public# smbclient \\\\[ip]\\share
    Enter WORKGROUP\root's password:
    Try "help" to get a list of possible commands.
    smb: \> ls
      .                                   D        0  Thu Sep 27 16:26:00 2018
      ..                                  D        0  Thu Sep 27 16:26:00 2018
      New Folder (9)                      D        0  Sun Dec 13 05:26:59 2015
      New Folder - 6                      D        0  Sun Dec 13 06:55:42 2015
      Shortcut to New Folder (2).lnk      A      420  Sun Dec 13 05:24:51 2015
    
                    1690825 blocks of size 2048. 794699 blocks available
    

### Check for Vulnerabilities

#### nmap

`nmap --script smb-vuln* -p 139,445 [ip]`

  * `--script smb-vuln*` \- will run all smb vulnerability scan scripts
  * `-p 139,445` \- smb ports

Example:

    
    
    root@kali:~# nmap --script smb-vuln* -p 139,445 [ip]
    Starting Nmap 7.70 ( https://nmap.org ) at 2018-09-27 16:37 EDT
    Nmap scan report for [ip]
    Host is up (0.030s latency).
    
    PORT    STATE SERVICE
    139/tcp open  netbios-ssn
    445/tcp open  microsoft-ds
    MAC Address: 00:50:56:XX:XX:XX (VMware)
    
    Host script results:
    | smb-vuln-ms06-025:
    |   VULNERABLE:
    |   RRAS Memory Corruption vulnerability (MS06-025)
    |     State: VULNERABLE
    |     IDs:  CVE:CVE-2006-2370
    |           A buffer overflow vulnerability in the Routing and Remote Access service (RRAS) in Microsoft Windows 2000 SP4, XP SP1
    |           and SP2, and Server 2003 SP1 and earlier allows remote unauthenticated or authenticated attackers to
    |           execute arbitrary code via certain crafted "RPC related requests" aka the "RRAS Memory Corruption Vulnerability."
    |
    |     Disclosure date: 2006-6-27
    |     References:
    |       https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2006-2370
    |_      https://technet.microsoft.com/en-us/library/security/ms06-025.aspx
    |_smb-vuln-ms10-054: false
    |_smb-vuln-ms10-061: false
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
    |       https://technet.microsoft.com/en-us/library/security/ms17-010.aspx
    |       https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2017-0143
    |_      https://blogs.technet.microsoft.com/msrc/2017/05/12/customer-guidance-for-wannacrypt-attacks/
    |_smb-vuln-regsvc-dos: ERROR: Script execution failed (use -d to debug)
    
    Nmap done: 1 IP address (1 host up) scanned in 5.58 seconds
    

### Overall Scan

#### enum4linux

`enum4linux -a [ip]`

  * `-a` \- all enumeration

Example output is long, but some highlights to look for:

  * output similar to nmblookup
  * check for null session
  * listing of shares
  * domain info
  * password policy
  * RID cycling output

### Manual Inspection

### Samba

`ngrep` is a neat tool to grep on network data. Running something like `ngrep -i -d tap0 's.?a.?m.?b.?a.*[[:digit:]]' port 139` in one terminal and then `echo exit | smbclient -L [IP]` in another will dump out a bunch of info including the version.

rewardone in the PWK forums posted a neat script to easily get Samba versions:

    
    
    #!/bin/sh
    #Author: rewardone
    #Description:
    # Requires root or enough permissions to use tcpdump
    # Will listen for the first 7 packets of a null login
    # and grab the SMB Version
    #Notes:
    # Will sometimes not capture or will print multiple
    # lines. May need to run a second time for success.
    if [ -z $1 ]; then echo "Usage: ./smbver.sh RHOST {RPORT}" && exit; else rhost=$1; fi
    if [ ! -z $2 ]; then rport=$2; else rport=139; fi
    tcpdump -s0 -n -i tap0 src $rhost and port $rport -A -c 7 2>/dev/null | grep -i "samba\|s.a.m" | tr -d '.' | grep -oP 'UnixSamba.*[0-9a-z]' | tr -d '\n' & echo -n "$rhost: " &
    echo "exit" | smbclient -L $rhost 1>/dev/null 2>/dev/null
    sleep 0.5 && echo ""
    

When you run this on a box running Samba, you get results:

    
    
    root@kali:~/pwk/lab/public# ./smbver.sh [IP]
    [IP]: UnixSamba 227a
    

When in doubt, we can check the smb version in PCAP. Here’s an example Unix
Samba 2.2.3a: ![](https://0xdfimages.gitlab.io/img/1535861610117.png)

#### Windows

Windows SMB is more complex than just a version, but looking in `wireshark`
will give a bunch of information about the connection. We can filter on
`ntlmssp.ntlmv2_response` to see NTLMv2 traffic, for example.

[](/2018/12/02/pwk-notes-smb-enumeration-checklist-update1.html)

