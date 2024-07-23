# Flare-On 2021: antioch

[flare-on](/tags#flare-on ) [ctf](/tags#ctf ) [flare-on-antioch](/tags#flare-
on-antioch ) [reverse-engineering](/tags#reverse-engineering )
[docker](/tags#docker ) [docker-tar](/tags#docker-tar ) [python](/tags#python
) [ghidra](/tags#ghidra ) [hackvent](/tags#hackvent )  
  
Oct 24, 2021

  * [[1] credchecker](/flare-on-2021/credchecker)
  * [[2] known](/flare-on-2021/known)
  * [3] antioch
  * [[4] myaquaticlife](/flare-on-2021/myaquaticlife)
  * [[5] FLARE Linux VM](/flare-on-2021/flarelinuxvm)
  * [[6] PetTheKitty](/flare-on-2021/petthekitty)
  * [[7] spel](/flare-on-2021/spel)
  * [[8] beelogin](/flare-on-2021/beelogin)
  * [9] evil - no writeup :(
  * [[10] wizardcult](/flare-on-2021/wizardcult)

![antioch](https://0xdfimages.gitlab.io/img/flare2021-antioch-cover.png)

antioch was a challenge based on the old movie, Monty Python and the Holy
Grail. I’m given a Tar archive, which is a Docker image, the output of a
command like `docker save`. It has a lot of layer data, but most the layers
are not referenced in the manifest. The image does have a single ELF
executable in it. Though reversing this binary, I’ll see how it expects input
matching the various authors from the metadata in the unused layers, and how
each author has an id associated with it. I’ll use the order of those IDs to
reconstruct the Docker image to include the files in the right order, and then
the new image will give the flag.

## Challenge

> To solve this challenge, you’ll need to …AAARGH

The [archive](/files/flare2021-03_antioch.7z) (password “flare”) contains a
TAR archive:

    
    
    $ file antioch.tar 
    antioch.tar: POSIX tar archive (GNU)
    

## Extract

### Binary

The `manifest.json` file shows a single layer as the latest:

    
    
    [
      {
        "Config": "a13ffcf46cf41480e7f15c7f3c6b862b799bbe61e7d5909150d8a43bd3b6c039.json",
        "RepoTags": [
          "antioch:latest"
        ],
        "Layers": [
          "7016b68f19aed3bb67ac4bf310defd3f7e0f7dd3ce544177c506d795f0b2acf3/layer.tar"
        ]
      }
    ]
    

In that layer, the `.tar` holds a single file which is an ELF:

    
    
    $ file AntiochOS 
    AntiochOS: ELF 64-bit LSB executable, x86-64, version 1 (SYSV), statically linked, stripped
    

It’s a bit weird that only one layer shows up in the `manifest.json`. When I
look at the tar, there are lots of layers present:

    
    
    $ tar tf antioch.tar
    09e6fff53d6496d170aaa9bc88bd39e17c8e5c13ee9066935b089ab0312635ef/
    09e6fff53d6496d170aaa9bc88bd39e17c8e5c13ee9066935b089ab0312635ef/VERSION
    09e6fff53d6496d170aaa9bc88bd39e17c8e5c13ee9066935b089ab0312635ef/layer.tar
    09e6fff53d6496d170aaa9bc88bd39e17c8e5c13ee9066935b089ab0312635ef/json     
    1c5d28d6564aed0316526e8bb2d79a436b45530d2493967c8083fea2b2e518ce/
    1c5d28d6564aed0316526e8bb2d79a436b45530d2493967c8083fea2b2e518ce/VERSION
    1c5d28d6564aed0316526e8bb2d79a436b45530d2493967c8083fea2b2e518ce/layer.tar
    1c5d28d6564aed0316526e8bb2d79a436b45530d2493967c8083fea2b2e518ce/json     
    25e171d6ac47c26159b26cd192a90d5d37e733eb16e68d3579df364908db30f2/
    25e171d6ac47c26159b26cd192a90d5d37e733eb16e68d3579df364908db30f2/VERSION
    25e171d6ac47c26159b26cd192a90d5d37e733eb16e68d3579df364908db30f2/layer.tar
    25e171d6ac47c26159b26cd192a90d5d37e733eb16e68d3579df364908db30f2/json     
    2b363180ec5d5862b2a348db3069b51d79d4e7a277d5cf5e4afe2a54fc04730e/
    ...[snip]...
    

In fact, there are 31 layers:

    
    
    $ tar tf antioch.tar | grep '/json' | wc -l
    31
    

Only the binary is included in the `manifest`. This will prove important.

### Authors (or Knights)

As I noted above, each later has three files, `json`, `layer.tar`, and
`VERSION`. Each `VERSION` is just “1.0”. Each `json` looks like:

    
    
    {
      "architecture": "amd64",
      "author": "Dragon of Angnor",
      "config": {
        "AttachStderr": false,
        "AttachStdin": false,
        "AttachStdout": false,
        "Cmd": null,
        "Domainname": "",
        "Entrypoint": null,
        "Env": [
          "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
        ],
        "Hostname": "",
        "Image": "",
        "Labels": null,
        "OnBuild": null,
        "OpenStdin": false,
        "StdinOnce": false,
        "Tty": false,
        "User": "",
        "Volumes": null,
        "WorkingDir": ""
      },
      "container_config": {
        "AttachStderr": false,
        "AttachStdin": false,
        "AttachStdout": false,
        "Cmd": [
          "/bin/sh",
          "-c",
          "#(nop) ADD multi:cac4629faae36e1a69040f3ca0fb3377ddd7eb285ac22bc701f064de1bf22f46 in / "
        ],
        "Domainname": "",
        "Entrypoint": null,
        "Env": [
          "PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
        ],
        "Hostname": "",
        "Image": "",
        "Labels": null,
        "OnBuild": null,
        "OpenStdin": false,
        "StdinOnce": false,
        "Tty": false,
        "User": "",
        "Volumes": null,
        "WorkingDir": ""
      },
      "created": "1975-04-03T12:00:00.000000000Z",
      "docker_version": "20.10.2",
      "id": "09e6fff53d6496d170aaa9bc88bd39e17c8e5c13ee9066935b089ab0312635ef",
      "os": "linux"
    }
    

The important part of each of these is the `Author`, which contains characters
from [Monty Python and the Holy
Grail](https://en.wikipedia.org/wiki/Monty_Python_and_the_Holy_Grail). I can
use `find` and `jq` to get a list of the characters and their layers:

    
    
    $ find . -name json -exec jq -c '[.author, .id]' {} \;
    ["Sir Gallahad","a2de31788db95838a986271665b958ac888d78559aa07e55d2a98fc3baecf6e6"]
    ["Roger the Shrubber","1c5d28d6564aed0316526e8bb2d79a436b45530d2493967c8083fea2b2e518ce"]
    ["Sir Bors","ea12384be264c32ec1db0986247a8d4b2231bf017742313c01b05a7e431d9c26"]
    ["Sir Gawain","58da659c7d1c5a0c3447cb97cd6ffb12027c734bfba32de8b9b362475fe92fae"]
    ["Black Knight","cfd7ddb31ce44bb24b373645876ac7ea372da1f3f31758f2321cc8f5b29884fb"]
    ["King Arthur","e6c2557dc0ff4173baee856cbc5641d5b19706ddb4368556fcdb046f36efd2e2"]
    ["Squire Concorde","81f28623cca429f9914e21790722d0351737f8ad3e823619a4f7019be72e2195"]
    ["Legendary Black Beast of Argh","9a31bad171ad7e8009fba41193d339271fc51f992b8d574c501cae1bfa6c3fe2"]
    ["A Famous Historian","49fb821d2bf6d6841ac7cf5005a6f18c4c76f417ac8a53d9e6b48154b5aa1e76"]
    ["Trojan Rabbit","6b4e128697aa0459a6caba2088f6f77efaaf29d407ec6b58939c9bc7814688ad"]
    ["Green Knight","76531a907cdecf03c8ac404d91cbcabd438a226161e621fab103a920600372a8"]
    ["Prince Herbert","e1a9333f9eccfeae42acec6ac459b9025fe6097c065ffeefe5210867e1e2317d"]
    ["Lady of the Lake","a435765bcd8745561460979b270878a3e7c729fae46d9e878f4c2d42e5096a44"]
    ["Rabbit of Caerbannog","cd27ad9a438a7eef05f5b5d99e2454225693e63aba29ce8553800fed23575040"]
    ["Dragon of Angnor","09e6fff53d6496d170aaa9bc88bd39e17c8e5c13ee9066935b089ab0312635ef"]
    ["Inspector End Of Film","fadf53f0ae11908b89dffc3123e662d31176b0bb047182bfec51845d1e81beb9"]
    ["Dennis the Peasant","2b363180ec5d5862b2a348db3069b51d79d4e7a277d5cf5e4afe2a54fc04730e"]
    ["Chicken of Bristol","bfefc1bdf8b980a525f58da1550b56daa67bae66b56e49b993fff139faa1472c"]
    ["Squire Patsy","f2ebdc667cbafc2725421d3c02babc957da2370fbd019a9e1993d8b0409f86dd"]
    ["Sir Ector","303dfd1f7447a80322cc8a8677941da7116fbf0cea56e7d36a4f563c6f22e867"]
    ["Sir Lancelot","fd8bf3c084c5dd42159f9654475f5861add943905d0ad1d3672f39e014757470"]
    ["Miss Islington","b75ea3e81881c5d36261f64d467c7eb87cd694c85dd15df946601330f36763a4"]
    ["Sir Bedevere","7d643931f34d73776e9169551798e1c4ca3b4c37b730143e88171292dbe99264"]
    [null,"7016b68f19aed3bb67ac4bf310defd3f7e0f7dd3ce544177c506d795f0b2acf3"]
    ["Bridge Keeper","f9621328166de01de73b4044edb9030b3ad3d5dbc61c0b79e26f177e9123d184"]
    ["Tim the Enchanter","4c33f90f25ea2ab1352efb77794ecc424883181cf8e6644946255738ac9f5dbd"]
    ["Sir Not-Appearing-in-this-Film","8e11477e79016a17e5cde00abc06523856a7db9104c0234803d30a81c50d2b71"]
    ["Zoot","b5f502d32c018d6b2ee6a61f30306f9b46dad823ba503eea5b403951209fd59b"]
    ["Brother Maynard","e5254dec4c7d10c15e16b41994ca3cf0c5e2b2a56c9d4dc2ef053eeff24333ff"]
    ["Dinky","25e171d6ac47c26159b26cd192a90d5d37e733eb16e68d3579df364908db30f2"]
    ["Sir Robin","754ee87063ee108c1f939cd3a28980a03b700f3c3967df8058831edad2743fd7"]
    

## Running It

### Docker

This archive format is the output of the `docker save` command. I looked at
this before in the [Twelve Steps of Christmas](/hackvent2020/leet#docker-
image) challenge in Hackvent 2020.

I can load this image and run it as is using `docker`:

    
    
    $ docker load --input antioch.tar
    Loaded image: antioch:latest
    $ docker image ls
    REPOSITORY          TAG                 IMAGE ID            CREATED             SIZE
    antioch             latest              a13ffcf46cf4        7 weeks ago         13kB
    

If I try to run `bash` or `sh`, it fails:

    
    
    $ docker run -it antioch bash
    docker: Error response from daemon: OCI runtime create failed: container_linux.go:370: starting container process caused: exec: "bash": executable file not found in $PATH: unknown.
    ERRO[0000] error waiting for container: context canceled 
    $ docker run -it antioch sh
    docker: Error response from daemon: OCI runtime create failed: container_linux.go:370: starting container process caused: exec: "sh": executable file not found in $PATH: unknown.
    ERRO[0000] error waiting for container: context canceled 
    $ docker run -it antioch /bin/sh
    docker: Error response from daemon: OCI runtime create failed: container_linux.go:370: starting container process caused: exec: "/bin/sh": stat /bin/sh: no such file or directory: unknown.
    ERRO[0000] error waiting for container: context canceled 
    

I can run `AntiochOS`:

    
    
    $ docker run -it antioch /AntiochOS
    AntiochOS, version 1.32 (build 1975)
    Type help for help
    > 
    

### ELF

This works the same as running the ELF:

    
    
    $ ./AntiochOS 
    AntiochOS, version 1.32 (build 1975)
    Type help for help
    > 
    

Running `help` isn’t too helpful:

    
    
    > help
    Available commands:
    help: print this help
    ...AAARGH
    
    > 
    

## RE

### Helper Functions

There were three types of functions that were quick to label once I understood
the formats. I’ll call these `load`, `loadxl`, and `syscall` functions.

#### load

There were nine functions that simply took a pointer to a buffer and set a
string value into it one byte at a time, like this:

![image-20210912063946266](https://0xdfimages.gitlab.io/img/image-20210912063946266.png)

By retyping `param_1` from `undefined *` to `char *`, it will quickly show the
value, and I’ll rename the function to describe it:

![image-20210912064224738](https://0xdfimages.gitlab.io/img/image-20210912064224738.png)

#### loadxl

There were five more functions that had a format like this:

![image-20210912133852387](https://0xdfimages.gitlab.io/img/image-20210912133852387.png)

In each case, it made sure that the first byte in some buffer was 0, and then
xored each byte in the buffer up to a hard-coded stop point with a value (each
was different, but 0xbe in this example). The buffer looked like:

![image-20210912133954012](https://0xdfimages.gitlab.io/img/image-20210912133954012.png)

After the xor, it returned the address of the second byte in the original
buffer (0x00404001 in the example above). I can select that buffer and right
click, “Copy Special…”, and copy the buffer as a Python Byte String. Then I
can paste it into my Python terminal and quickly decode it:

    
    
    >>> x = b'\xec\xd7\xd9\xd6\xca\x90\x9e\xf1\xd8\xd8\x9e\xc7\xd1\xcb\x9e\xd9\xd1\x90\x9e\x9d'
    >>> ''.join([chr(c ^ 0xbe) for c in x])
    'Right. Off you go. #'
    

#### syscall

The other group of functions each just made a call to `FUN_00401980`. That
function just makes a `syscall`:

    
    
    undefined  [16]
    syscall_execute(undefined8 syscall_number,undefined8 arg1,undefined8 arg2,undefined8 arg3)
    
    {
      syscall();
      return CONCAT88(arg3,syscall_number);
    }
    

The decompilation return is a bit weird, but otherwise it’s straight forward.
Knowing that, I can label these eight functions as `syscall_[call]`, for
example, `syscall_open`:

    
    
    undefined  [16] syscall_open(undefined8 filename)
    
    {
      undefined auVar1 [16];
      
      auVar1 = syscall_execute(2,filename,0,0);
      return auVar1;
    }
    

The first arg to `syscall_execute` is the syscall number, and in this case, [2
is
open](https://chromium.googlesource.com/chromiumos/docs/+/master/constants/syscalls.md#tables).

There were eight of these functions, providing `close`, `execute`, `exit`,
`open`, `read`, `select`, `stat`, and `write`.

### entry

The entry function is quite simple once the helpers are defined. It prints the
welcome message, then goes into a loop where it prints the prompt, reads
input, and compares it against X strings and takes action based on that
(function names are given by me):

Command | Action  
---|---  
`quit` | Breaks loop and exits  
`help` | Calls `print_help()`, starts of help menu but then “…AAARGH”  
`consult` | Calls `do_consult`  
`approach` | Calls `do_approach`  
  
### approach

Entering the `approach` command prompts for my name (just like in [the
movie](https://www.youtube.com/watch?v=0D7hFHfLEyk)):

    
    
    > approach
    Approach the Gorge of Eternal Peril!
    What is your name? 
    

Entering a name just replies “…AAARGH”. If I enter one of the authors from the
list above, it asks my quest (which the answer doesn’t matter), and then for a
favorite color:

    
    
    > approach
    Approach the Gorge of Eternal Peril!
    What is your name? Sir Ector
    What is your quest? find the grail
    What is your favorite color? Green
    ...AAARGH
    

There is an array of data which I’ve labeled `knights` at 0x00402000. There
are 30 blocks, each consisting of a CRC32 of the knight name, a CRC32 of the
knights favorite color, and a four byte int ranging from 1-30.

The code starts by printing and getting the name:

    
    
      res = loadxl_approach_the_gorge_str();
      syscall_write(1,res,0x25);
      syscall_select(1);
      load_what_is_your_name_str(message_strs);
      syscall_write(1,message_strs,0x13);
      res = syscall_read(0,read_buffer,0x80);
      name_crc = crc32(read_buffer,res);
      knight_ptr = knight_ARRAY_00402000;
      crc = -0x4a6c6a57;
      while (knight_ptr = knight_ptr + 1, crc != name_crc) {
        i2 = (int)i + 1;
        i = (ulong)i2;
        if (i2 == 0x1e) goto LAB_00401800;
        crc = knight_ptr->name_crc;
      }
    

It takes the input name, finds the CRC32, and then steps through the data
looking for a CRC32 that matches. I’ve actually defined a 12-byte struct in
Ghidra for each knight, which is why it only increments the pointer by 1.

![image-20210913061854489](https://0xdfimages.gitlab.io/img/image-20210913061854489.png)

If it finds the matching CRC32, it exits the while loop, of if it reaches the
end, it jumps to the end where it prints “…AAARGH” and exits.

The next code does a similar check against the favorite color:

    
    
      load_what_is_your_quest_str(message_strs);
      syscall_write(1,message_strs,0x14);
      name_len = syscall_read(0,read_buffer,0x80);
      if (1 < name_len) {
        load_what_is_your_favorite_color_str(message_strs);
        syscall_write(1,message_strs,0x1d);
        res = syscall_read(0,read_buffer,0x80);
        crc = crc32(read_buffer,res);
        if ((knight_ARRAY_00402000[i].color_crc == crc) && (0 < *(char *)&knight_ARRAY_00402000[i].id)) {
    

If the color matches the corresponding CRC32 for that knight, it continues,
otherwise it prints “…AAARGH” and exits.

On answering the questions correctly, it just prints “Right. Off you go.” and
a number, which is the third value from that knight struct:

    
    
    > approach
    Approach the Gorge of Eternal Peril!
    What is your name? Sir Lancelot
    What is your quest? grail
    What is your favorite color? Blue
    Right. Off you go. #18
    

I’ll write a Python script to find each character, their color, and their
number:

    
    
    #!/usr/bin/env python3    
        
    import struct    
    from zlib import crc32    
    
        
    knights = {}    
    knights_data = b'\xa9\x95\x93\xb5\x29\xab\xb5\x1b\x0e\x00\x00\x00\x4b\xd0\xfd\x5e\xc8\x68\x84\x3f\x12\x00\x00\x00\xd0\x85\xed\xec\x48\x3d\xd2\x82\x02\x00\x00\x00\x14\x92\x54\xd8\xe5\x2e\x47\x00\x1d\x00\x00\x00\x4d\x02\x2f\x2c\xaa\x60\xa0\xc9\x0c\x00\x00\x00\x32\x52\x8a\x01\x35\xd2\x24\x00\x0d\x00\x00\x00\x33\x8a\xb8\x72\x13\x66\x57\x81\x14\x00\x00\x00\xe2\x04\x44\x67\x29\xe1\x69\x51\x0b\x00\x00\x00\xb5\x73\x7a\x30\x3e\xe1\x60\xe5\x1c\x00\x00\x00\x04\x87\x46\x13\xa9\xe4\x58\x23\x15\x00\x00\x00\x1b\x47\xf6\x94\x53\x1a\x34\xd6\x05\x00\x00\x00\x75\xcf\xa1\xed\xe5\x91\xfa\xba\x18\x00\x00\x00\x4d\x12\xac\xbb\x1d\x64\x97\xa6\x19\x00\x00\x00\xc3\xe4\x07\xf7\x43\x56\x18\xef\x07\x00\x00\x00\x6f\x59\x02\xd7\x15\x89\xc2\x79\x0a\x00\x00\x00\x48\x08\xa1\x86\xdc\x8f\x10\x59\x01\x00\x00\x00\x1c\x53\x40\xd6\xe8\xe1\x3d\xef\x13\x00\x00\x00\xb3\x5d\x66\x7b\xb0\x03\xa9\xa3\x03\x00\x00\x00\xcc\x21\x13\xab\xd7\xea\xed\xee\x04\x00\x00\x00\xd8\x66\x60\x4f\x07\x3d\x8a\x9c\x11\x00\x00\x00\xca\x47\x60\x25\x9e\xbe\x85\x40\x09\x00\x00\x00\xd3\x1e\xc9\x3f\xc9\x49\x95\x37\x08\x00\x00\x00\xe4\xaf\x24\xa4\x47\x13\x87\xef\x1b\x00\x00\x00\xda\x01\x09\x55\x6b\xec\xfc\x01\x10\x00\x00\x00\x2d\x9e\xa2\x10\xaa\x56\x60\xe7\x16\x00\x00\x00\x5f\xc8\xcb\x56\x68\x1a\x6f\x35\x0f\x00\x00\x00\xa6\xe3\xdf\x80\x36\xb5\x0a\x9d\x1e\x00\x00\x00\xe1\xd4\x57\xe6\x30\xfd\xe9\xb4\x17\x00\x00\x00\xd4\xe1\xa1\x2b\x18\xd9\x66\xbe\x1a\x00\x00\x00\x9b\x08\x33\x7d\x85\xf5\xc1\x67\x06\x00\x00\x00'
        
        
    names = ['Sir Gallahad', 'Roger the Shrubber', 'Sir Bors', 'Sir Gawain', 'Black Knight', 'King Arthur', 'Squire Concorde', 'Legendary Black Beast of Argh', 'A Famous Historian', 'Trojan Rabbit', 'Green Knight', 'Prince Herbert', 'Lady of the Lake', 'Rabbit of Caerbannog', 'Dragon of Angnor', 'Inspector End Of Film', 'Dennis the Peasant', 'Chicken of Bristol', 'Squire Patsy', 'Sir Ector', 'Sir Lancelot', 'Miss Islington', 'Sir Bedevere', 'Bridge Keeper', 'Tim the Enchanter', 'Sir Not-Appearing-in-this-Film', 'Zoot', 'Brother Maynard', 'Dinky', 'Sir Robin']
        
    with open('colors.txt', 'r') as f:    
        colors = f.readlines()    
    
    crc_names = {crc32(f"{kn}\n".encode()): kn for kn in names}    
    crc_colors = {crc32(c.encode()): c for c in colors}    
    
    knights = {}    
    for i in range(0, len(knights_data), 12):    
            name_crc, color_crc, num = struct.unpack("<III", knights_data[i:i+12])
            name = crc_names[name_crc]
            try:
                color = crc_colors[color_crc].strip()
            except KeyError:
                color = "Not Identified"
                print(f"No color for {name}")
            knights[num] = {"name_crc": name_crc, "color_crc": color_crc, "name": name, "color": color}
    
    for i in sorted(knights):
        print(f"[{i:2d}] {knights[i]['name']:35} {knights[i]['color']}")             
    

`colors.txt` comes from [this list of CSS
colors](https://www.computerhope.com/htmcolor.htm). It finds colors for all
but one:

    
    
    $ python3 list_knights.py 
    No color for Sir Not-Appearing-in-this-Film
    [ 1] Miss Islington                      Brown
    [ 2] Sir Bors                            Coral
    [ 3] Tim the Enchanter                   Orange
    [ 4] Dragon of Angnor                    Khaki
    [ 5] Brother Maynard                     Crimson
    [ 6] Sir Bedevere                        Teal
    [ 7] Sir Robin                           Red
    [ 8] Zoot                                Tan
    [ 9] Squire Concorde                     Periwinkle
    [10] Green Knight                        Green
    [11] Trojan Rabbit                       Beige
    [12] Chicken of Bristol                  Mint
    [13] Roger the Shrubber                  Tomato
    [14] Bridge Keeper                       Indigo
    [15] Sir Gawain                          Azure
    [16] Legendary Black Beast of Argh       Silver
    [17] A Famous Historian                  Pink
    [18] Sir Lancelot                        Blue
    [19] Lady of the Lake                    Gold
    [20] Rabbit of Caerbannog                Salmon
    [21] Sir Not-Appearing-in-this-Film      Not Identified
    [22] Prince Herbert                      Wheat
    [23] King Arthur                         Purple
    [24] Inspector End Of Film               Gray
    [25] Sir Ector                           Bisque
    [26] Squire Patsy                        Chartreuse
    [27] Dennis the Peasant                  Orchid
    [28] Dinky                               Turquoise
    [29] Black Knight                        Black
    [30] Sir Gallahad                        Yellow
    

### consult

Running `consult` prints a message, hangs for a second, and then prints a ton
of lines of Vs:

    
    
    > consult         
    Consult the Book of Armaments!                                 
    VVVVVVVVVVVVVVV                     
    VVVVVVVVVVVVVVV
    ...[snip]...
    

The function `do_consult` starts by zeroing out a buffer and printing a
message:

    
    
      ptr_decoded_buf = decoded_buf;
      for (i = 0x200; i != 0; i = i + -1) {
        *ptr_decoded_buf = 0;
        ptr_decoded_buf = ptr_decoded_buf + 1;
      }
      puVar1 = loadxl_consult_the_book_string();
      syscall_write(1,puVar1,0x1f);
      syscall_select(2);
    

There are two variables defined at the top:

    
    
      c = 0x61;
      fn = 0x7461642e2e;
    

`c` is “a”, and `fn` is “..dat”.

The code then loops on `c` until it reaches 0x7b (“z”):

    
    
      do {
        while( true ) {
          fn = fn & 0xffffffffffffff00 | (ulong)c;
          res = syscall_open(&fn);
          if (res < 0) break;
          syscall_read(res,file_buf,0x1000);
          syscall_close(res);
          ptr_decoded_buf = decoded_buf;
          ptr_file_buf = file_buf;
          do {
            *(byte *)ptr_decoded_buf = *(byte *)ptr_decoded_buf ^ *ptr_file_buf;
            ptr_decoded_buf = (undefined8 *)((long)ptr_decoded_buf + 1);
            ptr_file_buf = ptr_file_buf + 1;
          } while (ptr_decoded_buf != (undefined8 *)&stack0xffffffffffffffd8);
          c = c + 1;
          if (c == 0x7b) goto LAB_00401544;
        }
        c = c + 1;
      } while (c != 0x7b);
    

On each loop, it replaces the first `.` in `..dat` with `c`, and opens that
file, reads it, and then loops over the buffer xoring each byte by the input.
So effectively it’s looking for the files a-z.dat and xoring them together.

Then it loads a string of characters used to make ascii art into 0x00404100
(the rest is filled with “.”):

    
    
    V\',`)(//\\\\\\||||||||||||_______________.
    

Now it loops through the buffer from above, using the value for a key into
that string above to get one of those characters except for every 16th
character, which it leaves as a newline:

    
    
      i = 0;
      do {
        value = '\n';
        if (((uint)i & 0xf) != 0xf) {
          value = (&DAT_00404100)[*(byte *)((long)decoded_buf + i)];
        }
        *(undefined *)((long)decoded_buf + i) = value;
        i = i + 1;
      } while (i != 0x1000);
      syscall_write(1,decoded_buf,0x1000);
    

When none of the files could be read, the buffer was just all null, so it
returned all V.

## Solve

### Find dats

The only place I can see where a flag could be would be in the ASCII art built
from the `.dat` files. There are no dat files yet, but I do have all these
layers that aren’t included. Checking a couple, I find them:

    
    
    $ tar tf 09e6fff53d6496d170aaa9bc88bd39e17c8e5c13ee9066935b089ab0312635ef/layer.tar 
    a.dat
    c.dat
    d.dat
    e.dat
    f.dat
    i.dat
    j.dat
    k.dat
    l.dat
    q.dat
    t.dat
    u.dat
    v.dat
    x.dat
    y.dat
    z.dat
    $ tar tf 1c5d28d6564aed0316526e8bb2d79a436b45530d2493967c8083fea2b2e518ce/layer.tar 
    a.dat
    e.dat
    g.dat
    h.dat
    i.dat
    k.dat
    l.dat
    m.dat
    n.dat
    o.dat
    p.dat
    q.dat
    s.dat
    t.dat
    w.dat
    x.dat
    y.dat
    z.dat
    

This is good because I have the files, but bad because each of the layers has
many dat files and there are repeats. I can get a histogram of all the files
in the different layers:

    
    
    $ find . -name layer.tar -exec tar tf {} \; | sort | uniq -c
         23 a.dat
          1 AntiochOS
         22 b.dat
         15 c.dat
         18 d.dat
         23 e.dat
         22 f.dat
         20 g.dat
         24 h.dat
         23 i.dat
         24 j.dat
         22 k.dat
         21 l.dat
         22 m.dat
         23 n.dat
         23 o.dat
         18 p.dat
         24 q.dat
         13 r.dat
         22 s.dat
         20 t.dat
         22 u.dat
         21 v.dat
         23 w.dat
         24 x.dat
         20 y.dat
         27 z.dat
    

This means the ordering of the layers is important. The last one added for
each letter will be the one that ends up in the image.

### Order Layers

The one thing I did manage to pull from the `approach` command is each
character and their number. And each layer has a character as an author. So I
can try ordering the layers in the order of the character numbers.

There are two files that need to be fixed in the `antioch.tar` file in order
to add the layers back in. First, the `manifest.json` will need to include the
layers in order. The default one is:

    
    
    [{"Config":"a13ffcf46cf41480e7f15c7f3c6b862b799bbe61e7d5909150d8a43bd3b6c039.json","RepoTags":["antioch:latest"],"Layers":["7016b68f19aed3bb67ac4bf310defd3f7e0f7dd3ce544177c506d795f0b2acf3/layer.tar"]}]
    

The other 30 layers will need to be added to the `Layes` array. The
`manifest.json` also references a `Config` file. In that file, it has a hash
for each of the layers at the end in the `rootfs.diff_ids` list.

    
    
    {"architecture":"amd64","config":{"Hostname":"","Domainname":"","User":"","AttachStdin":false,"AttachStdout":false,"AttachStderr":false,"Tty":false,"OpenStdin":false,"StdinOnce":false,"Env":["PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"],"Cmd":["/AntiochOS"],"Image":"sha256:72081c09b8504bda08787ba6ea0c5059e74464398cb92685b3c86a26230b8a1f","Volumes":null,"WorkingDir":"","Entrypoint":null,"OnBuild":null,"Labels":null},"container":"5a7d890eaf80df63166dedb6c0f0afaa26894ba10dd647671da887cfe2ce4349","container_config":{"Hostname":"5a7d890eaf80","Domainname":"","User":"","AttachStdin":false,"AttachStdout":false,"AttachStderr":false,"Tty":false,"OpenStdin":false,"StdinOnce":false,"Env":["PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"],"Cmd":["/bin/sh","-c","#(nop) ","CMD [\"/AntiochOS\"]"],"Image":"sha256:72081c09b8504bda08787ba6ea0c5059e74464398cb92685b3c86a26230b8a1f","Volumes":null,"WorkingDir":"","Entrypoint":null,"OnBuild":null,"Labels":{}},"created":"2021-07-23T03:21:55.959771124Z","docker_version":"20.10.2","history":[{"created":"2021-07-23T03:21:55.793483339Z","created_by":"/bin/sh -c #(nop) ADD file:fae1674275a5cc9b0c04ef177df65aebeaf796b0ba7c94ac2bd35120306411d4 in / "},{"created":"2021-07-23T03:21:55.959771124Z","created_by":"/bin/sh -c #(nop)  CMD [\"/AntiochOS\"]","empty_layer":true}],"os":"linux","rootfs":{"type":"layers","diff_ids":["sha256:d26c760acd6e75540d4ab7a33245a75a5506daa7998819f97918a39632a15497"]}}
    

The original version only shows one, which is the SHA256 of the `layer.tar`
containing `AntiochOS`:

    
    
    $ sha256sum 7016b68f19aed3bb67ac4bf310defd3f7e0f7dd3ce544177c506d795f0b2acf3/layer.tar 
    d26c760acd6e75540d4ab7a33245a75a5506daa7998819f97918a39632a15497  7016b68f19aed3bb67ac4bf310defd3f7e0f7dd3ce544177c506d795f0b2acf3/layer.tar
    $ tar tf 7016b68f19aed3bb67ac4bf310defd3f7e0f7dd3ce544177c506d795f0b2acf3/layer.tar
    AntiochOS
    

The order of the hashes must be in the same order as the layers.

### Script

This script will take the original `.tar` file, open it, and create `antioch-
new.tar` with a modified manifest and config such that the layers are added
back in the order of the characters/knights:

    
    
    #!/usr/bin/env python3
    
    import hashlib
    import json
    import os
    import struct
    import tarfile
    from io import StringIO, BytesIO
    from zlib import crc32
    
    
    knights = {}
    knights_data = b'\xa9\x95\x93\xb5\x29\xab\xb5\x1b\x0e\x00\x00\x00\x4b\xd0\xfd\x5e\xc8\x68\x84\x3f\x12\x00\x00\x00\xd0\x85\xed\xec\x48\x3d\xd2\x82\x02\x00\x00\x00\x14\x92\x54\xd8\xe5\x2e\x47\x00\x1d\x00\x00\x00\x4d\x02\x2f\x2c\xaa\x60\xa0\xc9\x0c\x00\x00\x00\x32\x52\x8a\x01\x35\xd2\x24\x00\x0d\x00\x00\x00\x33\x8a\xb8\x72\x13\x66\x57\x81\x14\x00\x00\x00\xe2\x04\x44\x67\x29\xe1\x69\x51\x0b\x00\x00\x00\xb5\x73\x7a\x30\x3e\xe1\x60\xe5\x1c\x00\x00\x00\x04\x87\x46\x13\xa9\xe4\x58\x23\x15\x00\x00\x00\x1b\x47\xf6\x94\x53\x1a\x34\xd6\x05\x00\x00\x00\x75\xcf\xa1\xed\xe5\x91\xfa\xba\x18\x00\x00\x00\x4d\x12\xac\xbb\x1d\x64\x97\xa6\x19\x00\x00\x00\xc3\xe4\x07\xf7\x43\x56\x18\xef\x07\x00\x00\x00\x6f\x59\x02\xd7\x15\x89\xc2\x79\x0a\x00\x00\x00\x48\x08\xa1\x86\xdc\x8f\x10\x59\x01\x00\x00\x00\x1c\x53\x40\xd6\xe8\xe1\x3d\xef\x13\x00\x00\x00\xb3\x5d\x66\x7b\xb0\x03\xa9\xa3\x03\x00\x00\x00\xcc\x21\x13\xab\xd7\xea\xed\xee\x04\x00\x00\x00\xd8\x66\x60\x4f\x07\x3d\x8a\x9c\x11\x00\x00\x00\xca\x47\x60\x25\x9e\xbe\x85\x40\x09\x00\x00\x00\xd3\x1e\xc9\x3f\xc9\x49\x95\x37\x08\x00\x00\x00\xe4\xaf\x24\xa4\x47\x13\x87\xef\x1b\x00\x00\x00\xda\x01\x09\x55\x6b\xec\xfc\x01\x10\x00\x00\x00\x2d\x9e\xa2\x10\xaa\x56\x60\xe7\x16\x00\x00\x00\x5f\xc8\xcb\x56\x68\x1a\x6f\x35\x0f\x00\x00\x00\xa6\xe3\xdf\x80\x36\xb5\x0a\x9d\x1e\x00\x00\x00\xe1\xd4\x57\xe6\x30\xfd\xe9\xb4\x17\x00\x00\x00\xd4\xe1\xa1\x2b\x18\xd9\x66\xbe\x1a\x00\x00\x00\x9b\x08\x33\x7d\x85\xf5\xc1\x67\x06\x00\x00\x00'
    manifest_fn = 'manifest.json'
    config_fn = 'a13ffcf46cf41480e7f15c7f3c6b862b799bbe61e7d5909150d8a43bd3b6c039.json'
    
    origtar = tarfile.open('./antioch.tar', 'r')
    newtar = tarfile.open('./antioch-new.tar', 'w')
    
    layers_to_hashes = {}
    knights_layers = {}
    
    # loop through tar creating new copy and getting info
    for f in origtar.getmembers():
        # skip manifest and config - will modified and add later
        if f.name in [manifest_fn, config_fn]:
            continue
        newtar.addfile(f, origtar.extractfile(f.name))
    
        # get map of layer to sha256
        if 'layer.tar' in f.name:
            layers_to_hashes[f.name.split('/')[0]] = hashlib.sha256(origtar.extractfile(f.name).read()).hexdigest()
        # get map of authors/knights to layer
        elif f.name.endswith('/json'):
            layer = json.loads(origtar.extractfile(f.name).read())
            if 'author' in layer:
                knights_layers[layer['author']] = f.name.split('/')[0]
    
    
    crc_names = {crc32(f"{kn}\n".encode()): kn for kn in knights_layers}
    
    for i in range(0, len(knights_data), 12):
            name_crc, color_crc, num = struct.unpack("<III", knights_data[i:i+12])
            name = crc_names[name_crc]
            layer = knights_layers[name]
            sha256 = layers_to_hashes[layer]
            knights[num] = {"name_crc": name_crc, "color_crc": color_crc, "name": name, "layer": layer, "sha256": sha256}
    
    # Create new manifest.json
    manifest = json.loads(origtar.extractfile(manifest_fn).read())
    manifest[0]['Layers'] = ["7016b68f19aed3bb67ac4bf310defd3f7e0f7dd3ce544177c506d795f0b2acf3/layer.tar"] + [f"{knights[i]['layer']}/layer.tar" for i in sorted(knights)]
    manifest_str = json.dumps(manifest)
    manifest_fobj = BytesIO(manifest_str.encode())
    info = tarfile.TarInfo(name=manifest_fn)
    info.size = len(manifest_str)
    newtar.addfile(tarinfo=info, fileobj=manifest_fobj)
    
    # Create new config
    config = json.loads(origtar.extractfile(config_fn).read())
    config['rootfs']['diff_ids'] = ['sha256:d26c760acd6e75540d4ab7a33245a75a5506daa7998819f97918a39632a15497'] + [f"sha256:{knights[i]['sha256']}" for i in sorted(knights)]
    config_str = json.dumps(config)
    config_fobj = BytesIO(config_str.encode())
    info = tarfile.TarInfo(name=config_fn)
    info.size = len(config_str)
    newtar.addfile(tarinfo=info, fileobj=config_fobj)
    
    origtar.close()
    newtar.close()  
    

On running this, it will create the new tar, which I can import:

    
    
    $ python3 knights.py 
    $ docker image rm -f antioch:latest 
    Untagged: antioch:latest
    Deleted: sha256:f9a1a435538a8f2fb4c0f15b85a5f46f90e3dde228506fabc70989cb4ea60a09
    $ docker image load --input antioch-new.tar 
    Loaded image: antioch:latest
    $ docker run -it antioch
    AntiochOS, version 1.32 (build 1975)
    Type help for help
    > 
    

From here, I’ll just run `consult`, and it prints it out as ASCII art:

![image-20211024140414309](https://0xdfimages.gitlab.io/img/image-20211024140414309.png)

**Flag: Five-Is-Right-Out@flare-on.com**

[](/flare-on-2021/antioch)

