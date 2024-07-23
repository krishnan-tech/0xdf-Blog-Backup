# Holiday Hack 2019: KringleCon2

[ctf](/tags#ctf ) [sans-holiday-hack](/tags#sans-holiday-hack )  
  
Jan 14, 2020

![](https://0xdfimages.gitlab.io/img/hh19-cover.png)

The 2019 SANS Holiday Hack Challenge presented a twisted take on how a
villain, the Tooth Fairy, tried to take down Santa and ruin Christmas. It all
takes place at the second annual Kringle Con, where the worlds leading
security practitioners show up to hear talks and solve puzzles. Hosted at
Elf-U, this years conference included [14 talks from leaders in information
security](https://www.youtube.com/playlist?list=PLjLd1hNA7YVzyhhqBQaW-
tF45xnS6oHAP), as well as 11 terminals / in-game puzzles and 13 objectives to
figure out. In solving all of these, the Tooth Fairy’s plot was foiled, and
Santa was able to deliver presents on Christmas. As usual, the challenges were
interesting and set up in such a way that it was very beginner friendly, with
lots of hints and talks to ensure that you learned something while solving.
While last year really started the trend of defensive themed challenges, 2019
had a ton of interesting defensive challenges, with hands on with machine
learning as well as tools like Splunk and Graylog.

## 2019 SANS Holiday Hack - Two Turtle Doves

### Introduction

### Arrival

The conference starts as I’m dropped off in the train station. I’ll ignore
Bushy Evergreen and the Escape Ed terminal for the moment and talk to Santa,
who is there to greet me:

![image-20200110172556442](https://0xdfimages.gitlab.io/img/image-20200110172556442.png)

> Welcome to the North Pole and KringleCon 2!
>
> Last year, KringleCon hosted over 17,500 attendees and my castle got a
> little crowded.
>
> We moved the event to Elf University (Elf U for short), the North Pole’s
> largest venue.
>
> Please feel free to explore, watch talks, and enjoy the con!

As I leave the train station through the door at the top of the screen, I come
out onto the Elf U quad, where I find Santa again, this time holding an
umbrella:

![image-20200110212246714](https://0xdfimages.gitlab.io/img/image-20200110212246714.png)

> This is a little embarrassing, but I need your help.
>
> Our KringleCon _turtle dove_ mascots are missing!
>
> They probably just wandered off.
>
> Can you please help find them?
>
> To help you search for them and get acquainted with KringleCon, I’ve created
> some objectives for you. You can see them in your badge.
>
> Where’s your badge? Oh! It’s that big, circle emblem on your chest - give it
> a tap!
>
> We made them in two flavors - one for our new guests, and one for those
> who’ve attended both KringleCons.
>
> After you find the Turtle Doves and complete objectives 2-5, please come
> back and let me know.
>
> Not sure where to start? Try hopping around campus and talking to some
> elves.
>
> If you help my elves with some quicker problems, they’ll probably remember
> clues for the objectives.

Looking at my badge, I’ve just completed the first objective, “0) Talk to
Santa in the Quad”. There are twelve objectives remaining, though first time
players will only see the first five:

![](https://0xdfimages.gitlab.io/img/hhc19-initial_badge.png)

The completed badge shows all the objectives complete:

![](https://0xdfimages.gitlab.io/img/image-20200110214651768.png)

The solution to each of these objectives, with each associated terminal
challenge, are given on the pages that follow. Additionally, the appendix
provides information beyond the scope of the objectives, but potentially still
of interest.

## Table of Contents

  * [1) Find the Turtle Doves](/holidayhack2019/1)
  * [2) Unredact Threatening Document](/holidayhack2019/2)
  * [3) Evaluate Attack Outcome](/holidayhack2019/3)
  * [4) Determine Attacker Technique](/holidayhack2019/4)
  * [5) Determine Compromised System](/holidayhack2019/5)
  * [6) Splunk](/holidayhack2019/6)
  * [7) Get Access To The Steam Tunnels](/holidayhack2019/7)
  * [8) Bypassing the Frido Sleigh CAPTEHA](/holidayhack2019/8)
  * [9) Retrieve Scraps of Paper from Server](/holidayhack2019/9)
  * [10) Recover Cleartext Document](/holidayhack2019/10)
  * [11) Open the Sleigh Shop Door](/holidayhack2019/11)
  * [12) Filter Out Poisoned Sources of Weather Data](/holidayhack2019/12)
  * [Appendix A: Hide Others](/holidayhack2019/13)
  * [Appendix B: Open Locks](/holidayhack2019/14)
  * [Appendix C: Easter Eggs](/holidayhack2019/15)

## Elf University Map

Over the course of solving all the challenges, I developed the following map:

[![Map of Elf-U](https://0xdfimages.gitlab.io/img/hhc19-elfu-map.png)_Click
for full size image_](https://0xdfimages.gitlab.io/img/hhc19-elfu-map.png)

[1) Find the Turtle Doves »](/holidayhack2019/1)

[](/holidayhack2019/)

