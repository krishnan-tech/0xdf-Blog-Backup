# Flare-On 2022: Flaredle

[flare-on](/tags#flare-on ) [ctf](/tags#ctf ) [flare-on-flaredle](/tags#flare-
on-flaredle ) [reverse-engineering](/tags#reverse-engineering )
[javascript](/tags#javascript )  
  
Nov 11, 2022

  * [1] Flaredle
  * [[2] Pixel Poker](/flare-on-2022/pixel_poker)
  * [[3] Magic 8 Ball](/flare-on-2022/magic_8_ball)
  * [[4] darn_mice](/flare-on-2022/darn_mice)
  * [[5] T8](/flare-on-2022/t8)
  * [[6] à la mode](/flare-on-2022/alamode)
  * [[7] anode](/flare-on-2022/anode)
  * [[8] backdoor](/flare-on-2022/backdoor)
  * [[9] encryptor](/flare-on-2022/encryptor)
  * [[10] Nur geträumt](/flare-on-2022/nur_getraumt)
  * [[11] The challenge that shall not be named](/flare-on-2022/challenge_that_shall_not_be_named)

![flaredle](https://0xdfimages.gitlab.io/img/flare2022-flaredle-cover.png)

Flaredle is a take off on the popular word game, Wordle. In Wordle, you guess
letters in a five letter word. In Flaredle, it’s a 21 character work. I’ll
look at the JavaScript to find the winning word, and use it to get the flag.

## Challenge

> Welcome to Flare-On 9!
>
> You probably won’t win. Maybe you’re like us and spent the year playing
> Wordle. We made our own version that is too hard to beat without cheating.
>
> Play it live at: <http://flare-on.com/flaredle/>

## Live Game

Opening the link in a browser gives a giant
[Wordle](https://www.nytimes.com/games/wordle/index.html) board (check out my
video on [hacking wordle](https://www.youtube.com/watch?v=or1AKX5kTZA)):

![image-20220930205057221](https://0xdfimages.gitlab.io/img/image-20220930205057221.png)

The words are 21 characters long instead of the typical five!

## RE

Opening the debug tools, `script.js` has the solution right at the top:

    
    
    import { WORDS } from "./words.js";
    
    const NUMBER_OF_GUESSES = 6;
    const WORD_LENGTH = 21;
    const CORRECT_GUESS = 57;
    let guessesRemaining = NUMBER_OF_GUESSES;
    let currentGuess = [];
    let nextLetter = 0;
    let rightGuessString = WORDS[CORRECT_GUESS];
    ...[snip]...
    

Later down, there’s a check for `rightGuessString` against the input guess:

    
    
        if (guessString === rightGuessString) {
    		let flag = rightGuessString + '@flare-on.com';
    		toastr.options.timeOut = 0;
    		toastr.options.onclick = function() {alert(flag);}
            toastr.success('You guessed right! The flag is ' + flag);
    
            guessesRemaining = 0
            return
    

If they match, it will show that string plus the email address to make a flag.

I can put a break point at that `if`, enter a valid guess from `words.js`, and
then hover over it to see the flag:

![image-20220930205434918](https://0xdfimages.gitlab.io/img/image-20220930205434918.png)

If they match, it creates the flag by combining that word plus “@flare-
on.com”.

Entering the word solves the challenge, and a popup at the top right gives the
flag:

![image-20221107151117062](https://0xdfimages.gitlab.io/img/image-20221107151117062.png)

**Flag: flareonisallaboutcats@flare-on.com**

[](/flare-on-2022/flaredle)

