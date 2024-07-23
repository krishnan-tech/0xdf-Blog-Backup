# Flare-On 2021: wizardcult

[flare-on](/tags#flare-on ) [ctf](/tags#ctf ) [flare-on-
wizardcult](/tags#flare-on-wizardcult ) [reverse-engineering](/tags#reverse-
engineering ) [go](/tags#go ) [python](/tags#python ) [youtube](/tags#youtube
) [crypto](/tags#crypto ) [ghidra](/tags#ghidra ) [irc](/tags#irc )
[inspircd](/tags#inspircd ) [c2](/tags#c2 )  
  
Oct 22, 2021

  * [[1] credchecker](/flare-on-2021/credchecker)
  * [[2] known](/flare-on-2021/known)
  * [[3] antioch](/flare-on-2021/antioch)
  * [[4] myaquaticlife](/flare-on-2021/myaquaticlife)
  * [[5] FLARE Linux VM](/flare-on-2021/flarelinuxvm)
  * [[6] PetTheKitty](/flare-on-2021/petthekitty)
  * [[7] spel](/flare-on-2021/spel)
  * [[8] beelogin](/flare-on-2021/beelogin)
  * [9] evil - no writeup :(
  * [10] wizardcult

![wizardcult](https://0xdfimages.gitlab.io/img/flare2021-wizardcult-cover.png)

The last challenge in Flare-On 8 was probably not harder than the ninth one,
but it might have been the one I had the most fun attacking. In a mad rush to
finish on time, I didn’t take great notes, so instead, I went back and solved
it start to finish on YouTube.

## Challenge

> We have one final task for you. We captured some traffic of a malicious
> cyber-space computer hacker interacting with our web server. Honestly, I
> padded my resume a bunch to get this job and don’t even know what a pcap
> file does, maybe you can figure out what’s going on.

The
[archive](https://drive.google.com/u/1/uc?id=1rZNyh4R03T6lOgtKKMnSzCiJn0tPr7TW&export=download)
(password “flare”) contains a PCAP file:

    
    
    $ file wizardcult.pcap
    wizardcult.pcap: pcap capture file, microsecond ts (little-endian) - version 2.4 (Ethernet, capture length 262144)
    

## Solving It

Full solution is on YouTube:

**Flag: wh0_n33ds_sw0rds_wh3n_you_h4ve_m4ge_h4nd@flare-on.com**

[](/flare-on-2021/wizardcult)

