# Flare-On 2021: credchecker

[flare-on](/tags#flare-on ) [ctf](/tags#ctf ) [flare-on-
credchecker](/tags#flare-on-credchecker ) [reverse-engineering](/tags#reverse-
engineering ) [html](/tags#html ) [javascript](/tags#javascript )
[python](/tags#python ) [youtube](/tags#youtube )  
  
Oct 22, 2021

  * [1] credchecker
  * [[2] known](/flare-on-2021/known)
  * [[3] antioch](/flare-on-2021/antioch)
  * [[4] myaquaticlife](/flare-on-2021/myaquaticlife)
  * [[5] FLARE Linux VM](/flare-on-2021/flarelinuxvm)
  * [[6] PetTheKitty](/flare-on-2021/petthekitty)
  * [[7] spel](/flare-on-2021/spel)
  * [[8] beelogin](/flare-on-2021/beelogin)
  * [9] evil - no writeup :(
  * [[10] wizardcult](/flare-on-2021/wizardcult)

![credchecker](https://0xdfimages.gitlab.io/img/flare2021-credchecker-
cover.png)

Flare-On 8 got off to an easy start with an HTML page and a login form. The
page has JavaScript to accept and check the password, and I’ll show two ways
to get the flag - pulling the password and then logging in, and decrypting the
flag buffer.

## Challenge

> Welcome to Flare-On 8! This challenge surves as your tutorial mission for
> the epic quest you are about to emark upon. Reverse engineer the Javascript
> code to determine the correct username and password the web page is looking
> for and it will show you the flag. Enter that flag here to advance to the
> next stage. All flags will be in the format of valid email addresses and all
> end with “@flare-on.com”.

The [archive](/files/flare2021-01_credchecker.7z) (password “flare”) contains
three files, an HTML page and two images:

    
    
    $ find . -type f 
    .../img/logo.png
    .../img/goldenticket.png
    ./admin.html
    

## Running It

Opening the page in Firefox presents a simple login form:

![image-20210911063224169](https://0xdfimages.gitlab.io/img/image-20210911063224169.png)

Just guessing a username and password returns a failure notification at the
bottom:

![image-20210911064333248](https://0xdfimages.gitlab.io/img/image-20210911064333248.png)

## RE

### Page Source

The page head has all the CSS inline, which isn’t interesting here. The body
has four `divs`:

    
    
    <div class="content" id="banner">
    <img id="logo" src="img/logo.png" alt="Flare-On 8">
    <h3>Administrator Verification Form</h3>
    <p">Enter your flare-on administrator credentials in this secure form to securely verify your security level. This is an official request and compliance is manditory.</p>
    </div>
    
    <div class="content" id="formdiv">
      <form id="credform">
        <label for="usrname">Username</label>
        <input type="text" id="usrname" name="usrname" onchange="dataEntered()">
        <label for="psw">Password</label>
        <input type="password" id="psw" name="psw" onkeydown="dataEntered()" onchange="dataEntered()">
      </form>
      	<button id="checkbtn" disabled="true" onclick="checkCreds()">Check Credentials</button>
    </div>
    
    <div class="content" id="message">
      <h3>Password must contain the following:</h3>
      <p class="invalid">The correct password</p>
      <p class="invalid">Not an incorrect password</p>
      <p>If you continue to fail, please ask your parents if it is too late to change your major</p>
    </div>
    
    <div class="content" id="winner">
    <img src="img/goldenticket.png" alt="A Golden Ticket">
    Welcome to Flare-On 8 here is your first flag:<br>
    <label id="final_flag">flag goes here</label>
    </div>
    

The first is the prompt, followed by the form. I’ll note that on any key press
into either of the input fields, it calls `dataEntered()`. On clicking the
button, it calls `checkCreds()`.

The other two divs with id `message` and `winner` display the response for a
bad password and the flag. They are both set to `display: none;` in CSS.

The JavaScript defines some variables (including `encoded_key`), and the two
functions noted above:

    
    
    <script>
    var form = document.getElementById("credform");
    var username = document.getElementById("usrname");
    var password = document.getElementById("psw");
    var info = document.getElementById("infolabel");
    var checkbtn = document.getElementById("checkbtn");
    var encoded_key = "P1xNFigYIh0BGAofD1o5RSlXeRU2JiQQSSgCRAJdOw=="
    
    function dataEntered() {
    	if (username.value.length > 0 && password.value.length > 0) {
    		checkbtn.disabled = false;
    	} else {
    		checkbtn.disabled = true;
    	}
    }
    
    function checkCreds() {
    	if (username.value == "Admin" && atob(password.value) == "goldenticket") 
    	{
    		var key = atob(encoded_key);
    		var flag = "";
    		for (let i = 0; i < key.length; i++)
    		{
    			flag += String.fromCharCode(key.charCodeAt(i) ^ password.value.charCodeAt(i % password.value.length))
    		}
    		document.getElementById("banner").style.display = "none";
    		document.getElementById("formdiv").style.display = "none";
    		document.getElementById("message").style.display = "none";
    		document.getElementById("final_flag").innerText = flag;
    		document.getElementById("winner").style.display = "block";
    	}
    	else
    	{
    		document.getElementById("message").style.display = "block";
    	}
    }
    </script>
    

`dataEntered()` just enables the submit button if both fields have data in
them. `checkCreds()` is what’s interesting.

### Solve With Password

The first line of `checkCreds()` is where it decides if it will show the flag
or the fail message:

    
    
    if (username.value == "Admin" && atob(password.value) == "goldenticket")
    

The username is “Admin” and the password when passed to `atob` will result in
the string “goldenticket”. `atob` is the JavaScript function for [base64
decode](https://developer.mozilla.org/en-US/docs/Web/API/atob). I’ll base64
encode the target string:

    
    
    $ echo -n goldenticket | base64
    Z29sZGVudGlja2V0
    

Entering that as the password with the known username provides the flag:

![image-20210911064408871](https://0xdfimages.gitlab.io/img/image-20210911064408871.png)

**Flag: enter_the_funhouse@flare-on.com**

### Solve By Decoding

The challenge can also be solved by ignoring the password, and looking at how
`encoded_key` is decoded to form the flag in this loop:

    
    
    		var key = atob(encoded_key);
    		var flag = "";
    		for (let i = 0; i < key.length; i++)
    		{
    			flag += String.fromCharCode(key.charCodeAt(i) ^ password.value.charCodeAt(i % password.value.length))
    		}
    

This is where I like to drop into a Python terminal (run `python3`). The first
thing the code does is base64 decode the `encoded_key` into `key`:

    
    
    >>> enc = "P1xNFigYIh0BGAofD1o5RSlXeRU2JiQQSSgCRAJdOw=="
    >>> import base64
    >>> base64.b64decode(enc)
    b'?\\M\x16(\x18"\x1d\x01\x18\n\x1f\x0fZ9E)Wy\x156&$\x10I(\x02D\x02];'
    >>> key = base64.b64decode(enc)
    

Here’s a short video on how I built this list comprehension to produce the
flag:

The result is:

    
    
    >>> ''.join([chr(x^ord(y)) for x,y in zip(key, cycle(password))])
    'enter_the_funhouse@flare-on.com'
    

[](/flare-on-2021/credchecker)

