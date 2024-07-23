# You Need To Know jq

[ctf](/tags#ctf ) [sans-holiday-hack](/tags#sans-holiday-hack )
[hackthebox](/tags#hackthebox ) [jq](/tags#jq ) [htb-waldo](/tags#htb-waldo )
[ja3](/tags#ja3 ) [malware](/tags#malware )  
  
Dec 19, 2018

You Need To Know jq

![](https://0xdfimages.gitlab.io/img/jq-cover.png)jq is such a nifty tool that
not nealry enough people know about. If you’re working with json data, even
just small bits here and there, it’s worth knowing the basics to make some
simple data manipulations possible. And if you want to become a full on jq
wizard, all the better. In this post, I’ll walk through three examples of
varying levels of complexity to show off jq. I’ll detail what I did in Waldo,
show an example from the 2017 Sans Holiday Hack Challenge, and conclude with a
real-world example where I’m looking at SSL/TLS fingerprints.

## Overview

If you ever work with json data, you need to know how to use `jq`. It’s the
Swiss Army Knife of json data. On a Linux system, you should be able to `apt
install jq` to install (or whatever your package manager or choice is).

## json Refresher

There’s some cool charts on [json.org](https://www.json.org/), but the short
version is that json is made up of objects (of the format `{string: value}`),
arrays (of the format `[value1, value2, ...]`) and values (strings, numbers,
objects, arrays, booleans). [json.org](https://www.json.org) has some neat
wire diagrams too. For example:

![](https://0xdfimages.gitlab.io/img/jq-object.gif)

![](https://0xdfimages.gitlab.io/img/jq-array.gif)

For example, here’s the first 30 lines of some json data that I’ll use later,
with comments inserted by me:

    
    
    {
      "count": 999,                 <-- name / value pair
      "query": "date>1900-01-01",   <-- another name / value pair 
      "infractions": [              <-- the value in this one is an array
        {                           <-- the objects in the array are json objects
          "status": "pending",      <-- name / value pair
          "severity": 5,            <-- this time value is an int
          "title": "Throwing rocks (at people)",
          "coals": [                <-- "coals" has an array of ints
            1,
            1,
            1,
            1,
            1
          ],
          "date": "2017-06-25T09:55:04",
          "name": "Suzanne Hart"
        },
        {                           <-- second object in this "infractions" array
          "status": "closed",
          "severity": 4,
          "title": "Aggravated pulling of hair",
          "coals": [
            1,
            1,
            1,
            1
          ],
          "date": "2017-02-02T12:13:51",
          "name": "Nina Fitzgerald"
    

The nested nature of json data gives it the potential to get very messy. You
can certainly use something like python and `import json` to work with json
data, but there are times you just need to manipulate the data without writing
a script. `jq` to the rescue.

## Example from Waldo

### Background

In [Waldo from Hackthebox](/2018/12/15/htb-waldo.html), I had to abuse a path
vulnerability in a php app to read outside of webroot and fetch a private ssh
key. The data that comes back is in json. To get the private key in Waldo, I
can use curl (`-s` to suppress output, `-X POST` to post, `-d` for the data,
and the url of `fileRead.php`):

    
    
    root@kali# curl -s -X POST -d "file=....//....//....//home/nobody/.ssh/.monitor" http://10.10.10.87/fileRead.php
    {"file":"-----BEGIN RSA PRIVATE KEY-----\nMIIEogIBAAKCAQEAs7sytDE++NHaWB9e+NN3V5t1DP1TYHc+4o8D362l5Nwf6Cpl\nmR4JH6n4Nccdm1ZU+qB77li8ZOvymBtIEY4Fm07X4Pqt4zeNBfqKWkOcyV1TLW6f\n87s0FZBhYAizGrNNeLLhB1IZIjpDVJUbSXG6s2cxAle14cj+pnEiRTsyMiq1nJCS\ndGCc\/gNpW\/AANIN4vW9KslLqiAEDJfchY55sCJ5162Y9+I1xzqF8e9b12wVXirvN\no8PLGnFJVw6SHhmPJsue9vjAIeH+n+5Xkbc8\/6pceowqs9ujRkNzH9T1lJq4Fx1V\nvi93Daq3bZ3dhIIWaWafmqzg+jSThSWOIwR73wIDAQABAoIBADHwl\/wdmuPEW6kU\nvmzhRU3gcjuzwBET0TNejbL\/KxNWXr9B2I0dHWfg8Ijw1Lcu29nv8b+ehGp+bR\/6\npKHMFp66350xylNSQishHIRMOSpydgQvst4kbCp5vbTTdgC7RZF+EqzYEQfDrKW5\n8KUNptTmnWWLPYyJLsjMsrsN4bqyT3vrkTykJ9iGU2RrKGxrndCAC9exgruevj3q\n1h+7o8kGEpmKnEOgUgEJrN69hxYHfbeJ0Wlll8Wort9yummox\/05qoOBL4kQxUM7\nVxI2Ywu46+QTzTMeOKJoyLCGLyxDkg5ONdfDPBW3w8O6UlVfkv467M3ZB5ye8GeS\ndVa3yLECgYEA7jk51MvUGSIFF6GkXsNb\/w2cZGe9TiXBWUqWEEig0bmQQVx2ZWWO\nv0og0X\/iROXAcp6Z9WGpIc6FhVgJd\/4bNlTR+A\/lWQwFt1b6l03xdsyaIyIWi9xr\nxsb2sLNWP56A\/5TWTpOkfDbGCQrqHvukWSHlYFOzgQa0ZtMnV71ykH0CgYEAwSSY\nqFfdAWrvVZjp26Yf\/jnZavLCAC5hmho7eX5isCVcX86MHqpEYAFCecZN2dFFoPqI\nyzHzgb9N6Z01YUEKqrknO3tA6JYJ9ojaMF8GZWvUtPzN41ksnD4MwETBEd4bUaH1\n\/pAcw\/+\/oYsh4BwkKnVHkNw36c+WmNoaX1FWqIsCgYBYw\/IMnLa3drm3CIAa32iU\nLRotP4qGaAMXpncsMiPage6CrFVhiuoZ1SFNbv189q8zBm4PxQgklLOj8B33HDQ\/\nlnN2n1WyTIyEuGA\/qMdkoPB+TuFf1A5EzzZ0uR5WLlWa5nbEaLdNoYtBK1P5n4Kp\nw7uYnRex6DGobt2mD+10cQKBgGVQlyune20k9QsHvZTU3e9z1RL+6LlDmztFC3G9\n1HLmBkDTjjj\/xAJAZuiOF4Rs\/INnKJ6+QygKfApRxxCPF9NacLQJAZGAMxW50AqT\nrj1BhUCzZCUgQABtpC6vYj\/HLLlzpiC05AIEhDdvToPK\/0WuY64fds0VccAYmMDr\nX\/PlAoGAS6UhbCm5TWZhtL\/hdprOfar3QkXwZ5xvaykB90XgIps5CwUGCCsvwQf2\nDvVny8gKbM\/OenwHnTlwRTEj5qdeAM40oj\/mwCDc6kpV1lJXrW2R5mCH9zgbNFla\nW0iKCBUAm5xZgU\/YskMsCBMNmA8A5ndRWGFEFE+VGDVPaRie0ro=\n-----END RSA PRIVATE KEY-----\n"}
    

### jq Clean Up

So, what comes back is json. It’s an object, with one string/value pair.

If you ever just want to pretty print some json data, you can simply pipe it
into `jq .`. That’s the simplest form for `jq`, where it’s literally just
printing back the entire object. But looks what comes out:

![1544839901373](https://0xdfimages.gitlab.io/img/1544839901373.png)

When I find myself with a large, json blob of unknown structure, the first thing I’ll do is `| jq . | less` and see what it looks like.

Next, I really just want the value of the file key. If the `.` refers to the
top object, `.file` selects the file object:

    
    
    root@kali# curl -s -X POST -d "file=....//....//....//home/nobody/.ssh/.monitor" http://10.10.10.87/fileRead.php | jq .file
    "-----BEGIN RSA PRIVATE KEY-----\nMIIEogIBAAKCAQEAs7sytDE++NHaWB9e+NN3V5t1DP1TYHc+4o8D362l5Nwf6Cpl\nmR4JH6n4Nccdm1ZU+qB77li8ZOvymBtIEY4Fm07X4Pqt4zeNBfqKWkOcyV1TLW6f\n87s0FZBhYAizGrNNeLLhB1IZIjpDVJUbSXG6s2cxAle14cj+pnEiRTsyMiq1nJCS\ndGCc/gNpW/AANIN4vW9KslLqiAEDJfchY55sCJ5162Y9+I1xzqF8e9b12wVXirvN\no8PLGnFJVw6SHhmPJsue9vjAIeH+n+5Xkbc8/6pceowqs9ujRkNzH9T1lJq4Fx1V\nvi93Daq3bZ3dhIIWaWafmqzg+jSThSWOIwR73wIDAQABAoIBADHwl/wdmuPEW6kU\nvmzhRU3gcjuzwBET0TNejbL/KxNWXr9B2I0dHWfg8Ijw1Lcu29nv8b+ehGp+bR/6\npKHMFp66350xylNSQishHIRMOSpydgQvst4kbCp5vbTTdgC7RZF+EqzYEQfDrKW5\n8KUNptTmnWWLPYyJLsjMsrsN4bqyT3vrkTykJ9iGU2RrKGxrndCAC9exgruevj3q\n1h+7o8kGEpmKnEOgUgEJrN69hxYHfbeJ0Wlll8Wort9yummox/05qoOBL4kQxUM7\nVxI2Ywu46+QTzTMeOKJoyLCGLyxDkg5ONdfDPBW3w8O6UlVfkv467M3ZB5ye8GeS\ndVa3yLECgYEA7jk51MvUGSIFF6GkXsNb/w2cZGe9TiXBWUqWEEig0bmQQVx2ZWWO\nv0og0X/iROXAcp6Z9WGpIc6FhVgJd/4bNlTR+A/lWQwFt1b6l03xdsyaIyIWi9xr\nxsb2sLNWP56A/5TWTpOkfDbGCQrqHvukWSHlYFOzgQa0ZtMnV71ykH0CgYEAwSSY\nqFfdAWrvVZjp26Yf/jnZavLCAC5hmho7eX5isCVcX86MHqpEYAFCecZN2dFFoPqI\nyzHzgb9N6Z01YUEKqrknO3tA6JYJ9ojaMF8GZWvUtPzN41ksnD4MwETBEd4bUaH1\n/pAcw/+/oYsh4BwkKnVHkNw36c+WmNoaX1FWqIsCgYBYw/IMnLa3drm3CIAa32iU\nLRotP4qGaAMXpncsMiPage6CrFVhiuoZ1SFNbv189q8zBm4PxQgklLOj8B33HDQ/\nlnN2n1WyTIyEuGA/qMdkoPB+TuFf1A5EzzZ0uR5WLlWa5nbEaLdNoYtBK1P5n4Kp\nw7uYnRex6DGobt2mD+10cQKBgGVQlyune20k9QsHvZTU3e9z1RL+6LlDmztFC3G9\n1HLmBkDTjjj/xAJAZuiOF4Rs/INnKJ6+QygKfApRxxCPF9NacLQJAZGAMxW50AqT\nrj1BhUCzZCUgQABtpC6vYj/HLLlzpiC05AIEhDdvToPK/0WuY64fds0VccAYmMDr\nX/PlAoGAS6UhbCm5TWZhtL/hdprOfar3QkXwZ5xvaykB90XgIps5CwUGCCsvwQf2\nDvVny8gKbM/OenwHnTlwRTEj5qdeAM40oj/mwCDc6kpV1lJXrW2R5mCH9zgbNFla\nW0iKCBUAm5xZgU/YskMsCBMNmA8A5ndRWGFEFE+VGDVPaRie0ro=\n-----END RSA PRIVATE KEY-----\n"
    

### -r

That result still has all `\n` and other escaped characters. That’s where the
`-r` parameter comes in.

> With this option, if the filter’s result is a string then it will be written
> directly to standard output rather than being formatted as a JSON string
> with quotes. This can be useful for making jq filters talk to non-JSON-based
> systems.
    
    
    root@kali# curl -s -X POST -d "file=....//....//....//home/nobody/.ssh/.monitor" http://10.10.10.87/fileRead.php | jq -r .file
    -----BEGIN RSA PRIVATE KEY-----
    MIIEogIBAAKCAQEAs7sytDE++NHaWB9e+NN3V5t1DP1TYHc+4o8D362l5Nwf6Cpl
    mR4JH6n4Nccdm1ZU+qB77li8ZOvymBtIEY4Fm07X4Pqt4zeNBfqKWkOcyV1TLW6f
    87s0FZBhYAizGrNNeLLhB1IZIjpDVJUbSXG6s2cxAle14cj+pnEiRTsyMiq1nJCS
    dGCc/gNpW/AANIN4vW9KslLqiAEDJfchY55sCJ5162Y9+I1xzqF8e9b12wVXirvN
    o8PLGnFJVw6SHhmPJsue9vjAIeH+n+5Xkbc8/6pceowqs9ujRkNzH9T1lJq4Fx1V
    vi93Daq3bZ3dhIIWaWafmqzg+jSThSWOIwR73wIDAQABAoIBADHwl/wdmuPEW6kU
    vmzhRU3gcjuzwBET0TNejbL/KxNWXr9B2I0dHWfg8Ijw1Lcu29nv8b+ehGp+bR/6
    pKHMFp66350xylNSQishHIRMOSpydgQvst4kbCp5vbTTdgC7RZF+EqzYEQfDrKW5
    8KUNptTmnWWLPYyJLsjMsrsN4bqyT3vrkTykJ9iGU2RrKGxrndCAC9exgruevj3q
    1h+7o8kGEpmKnEOgUgEJrN69hxYHfbeJ0Wlll8Wort9yummox/05qoOBL4kQxUM7
    VxI2Ywu46+QTzTMeOKJoyLCGLyxDkg5ONdfDPBW3w8O6UlVfkv467M3ZB5ye8GeS
    dVa3yLECgYEA7jk51MvUGSIFF6GkXsNb/w2cZGe9TiXBWUqWEEig0bmQQVx2ZWWO
    v0og0X/iROXAcp6Z9WGpIc6FhVgJd/4bNlTR+A/lWQwFt1b6l03xdsyaIyIWi9xr
    xsb2sLNWP56A/5TWTpOkfDbGCQrqHvukWSHlYFOzgQa0ZtMnV71ykH0CgYEAwSSY
    qFfdAWrvVZjp26Yf/jnZavLCAC5hmho7eX5isCVcX86MHqpEYAFCecZN2dFFoPqI
    yzHzgb9N6Z01YUEKqrknO3tA6JYJ9ojaMF8GZWvUtPzN41ksnD4MwETBEd4bUaH1
    /pAcw/+/oYsh4BwkKnVHkNw36c+WmNoaX1FWqIsCgYBYw/IMnLa3drm3CIAa32iU
    LRotP4qGaAMXpncsMiPage6CrFVhiuoZ1SFNbv189q8zBm4PxQgklLOj8B33HDQ/
    lnN2n1WyTIyEuGA/qMdkoPB+TuFf1A5EzzZ0uR5WLlWa5nbEaLdNoYtBK1P5n4Kp
    w7uYnRex6DGobt2mD+10cQKBgGVQlyune20k9QsHvZTU3e9z1RL+6LlDmztFC3G9
    1HLmBkDTjjj/xAJAZuiOF4Rs/INnKJ6+QygKfApRxxCPF9NacLQJAZGAMxW50AqT
    rj1BhUCzZCUgQABtpC6vYj/HLLlzpiC05AIEhDdvToPK/0WuY64fds0VccAYmMDr
    X/PlAoGAS6UhbCm5TWZhtL/hdprOfar3QkXwZ5xvaykB90XgIps5CwUGCCsvwQf2
    DvVny8gKbM/OenwHnTlwRTEj5qdeAM40oj/mwCDc6kpV1lJXrW2R5mCH9zgbNFla
    W0iKCBUAm5xZgU/YskMsCBMNmA8A5ndRWGFEFE+VGDVPaRie0ro=
    -----END RSA PRIVATE KEY-----
    

So simple, yet it gives me exactly what I wanted back.

## Sans Holiday Hack 2017 - NPPD Data

### Background

In the [2017 Sans Holiday Hack
Challenge](https://holidayhackchallenge.com/2017/), at one point I was given a
large blob of json data called `infractions.json`. I was also told that there
were several moles in the data that I needed to identify. Finally, I was told
that Boq Questrian and Bini Aru were already identified as moles.

### Data Survey

The first thing I did was pipe it into jq to see what I was dealing with:

    
    
    root@kali# cat infractions.json | jq . | head -30
    {
      "count": 999,
      "query": "date>1900-01-01",
      "infractions": [
        {
          "status": "pending",
          "severity": 5,
          "title": "Throwing rocks (at people)",
          "coals": [
            1,
            1,
            1,
            1,
            1
          ],
          "date": "2017-06-25T09:55:04",
          "name": "Suzanne Hart"
        },
        {
          "status": "closed",
          "severity": 4,
          "title": "Aggravated pulling of hair",
          "coals": [
            1,
            1,
            1,
            1
          ],
          "date": "2017-02-02T12:13:51",
          "name": "Nina Fitzgerald"
    

Ok, so right there I have a good feeling for what the data looks like. The top
level has a value called “count”, a value called “query”, and an array called
“infractions”. I can get a feel for the names assigned to the infractions too
by selecting those:

    
    
    root@kali# cat infractions.json | jq -r '.infractions | .[] | .name' | head
    Suzanne Hart
    Nina Fitzgerald
    Jess Aziz
    Shaun Low
    Grace Cruz
    Iris Shaffer
    Paul Newton
    Tina Humphrey
    Bonnie Roberts
    Karl Burnett
    

In the above query, I select the infractions field, and then pipe the results,
which are an array. `.[]` goes into the array, almost like a `for each`. Then
for each item, I select only the `.name` field. I’ll output the result into
`head`, but that’s outside of `jq`. Cool, I’ve got names. Now I’ll use `sort`
and `uniq` to get infractions per name. I’ll demonstrate doing something like
this fully in `jq` in the last example, but here I’ll highlight one of my
favorite parts of `jq` \- how easily it works with other command line stuff:

    
    
    root@kali# cat infractions.json | jq -r '.infractions | .[] | .name' | sort | uniq -c | sort -nr | head
         10 Josephine Howard
          7 Jeffrey Oconnell
          6 Sara Mark
          6 Nina Fitzgerald
          6 Maggie Khan
          6 Lucas Daly
          6 Jeanette Tanner
          6 Felix Mclean
          5 Vijay Robbins
          5 Val Garner
    

### More Complex Query

Now to the fun stuff. I’m going to build a complex query to get a view of the
two known moles. In the end, my query will be:

    
    
    cat infractions.json | jq '.infractions | group_by(.name) | .[] | {"name": .[0].name, "severity": [.[].severity] | add, "num_infractions": .|length, "infractions": [.[].title]} | select((.name|contains("Boq")) or (.name|contains("Bini")))'
    

To do this, I don’t just type it all out, but build it bit by bit. I’ll start
with getting the infractions:

`cat infractions.json | jq '.infractions`

Next, I’ll add `| group_by(.name)`. In an earlier example I used `.name` to
select the name field. This time, I’m not selecting it, but rearranging the
data based on the name field. The output at this point looks like this:

    
    
    root@kali# cat infractions.json | jq -r '.infractions | group_by(.name)' | head -30
    [
      [
        {
          "status": "pending",
          "severity": 3,
          "title": "Throwing rocks (non-person target)",
          "coals": [
            1,
            1,
            1
          ],
          "date": "2017-03-09T10:19:28",
          "name": "Abdullah Lindsey"
        },
        {
          "status": "closed",
          "severity": 5,
          "title": "Naughty words",
          "coals": [
            1,
            1,
            1,
            1,
            1
          ],
          "date": "2017-06-28T12:04:04",
          "name": "Abdullah Lindsey"
        }
      ],          <--- end of Abdullah Lindsey array
      [           <--- start of Abigail Chavez array
    

I still have the outside array, but now that is an array of arrays, where each
inner array holds the json blobs for one name.

Now I’ll remove the outer array with a `| .[]`.

Next I’m going to build my own new json object, creating keys and values, and
using the input data to create those values by piping into `{ [stuff] }`. So,
what are the things I want to capture? I’ll start with name, total severity of
all infractions, the number of infractions, and the list of infraction
descriptions. I’ll be working in a `for each` loop over arrays for each name.
So, for the first iteration, I’ll be passing in this:

    
    
      [
        {
          "status": "pending",
          "severity": 3,
          "title": "Throwing rocks (non-person target)",
          "coals": [
            1,
            1,
            1
          ],
          "date": "2017-03-09T10:19:28",
          "name": "Abdullah Lindsey"
        },
        {
          "status": "closed",
          "severity": 5,
          "title": "Naughty words",
          "coals": [
            1,
            1,
            1,
            1,
            1
          ],
          "date": "2017-06-28T12:04:04",
          "name": "Abdullah Lindsey"
        }
      ],
    

Ok, name. Well, the name value will be the same in each blob in the array. So
I’ll just get it from the first one, using `.[0].name`.

    
    
    {"name": .[0].name}
    

To get total severity, I’ll first get the array of severities using
`[.[].severity]`, and I’ll pipe that into `add`.

    
    
    {"name": .[0].name, "severity": [.[].severity] | add}
    

To get the number of infractions, I just need the length of the array, so `. | length`:
    
    
    {"name": .[0].name, "severity": [.[].severity] | add, "num_infractions": .|length}
    

Finally, to get the list of infractions, I’ll create an array just like in
severity, but not try to reduce it, giving `[.[].title]`

    
    
    {"name": .[0].name, "severity": [.[].severity] | add, "num_infractions": .|length, "infractions": [.[].title]}
    

Putting that all together, I now have:

    
    
    root@kali# cat infractions.json | jq -r '.infractions | group_by(.name) | .[] | {"name": .[0].name, "severity": [.[].severity] | add, "num_infractions": .|length, "infractions": [.[].title]}' | head -15
    {
      "name": "Abdullah Lindsey",
      "severity": 8,
      "num_infractions": 2,
      "infractions": [
        "Throwing rocks (non-person target)",
        "Naughty words"
      ]
    }
    {
      "name": "Abigail Chavez",
      "severity": 3,
      "num_infractions": 1,
      "infractions": [
        "General sassing"
    

But I wanted to look specifically at two moles, Bini Aru and Boq Questrian.
I’ll use `jq` select by adding this to the end of the query: `|
select((.name|contains("Boq")) or (.name|contains("Bini")))`

That’s the final query, and it gives me this:

![1544843108489](https://0xdfimages.gitlab.io/img/1544843108489.png)

### -c

The `-c` option comes in super handy as well:

> By default, jq pretty-prints JSON output. Using this option will result in
> more compact output by instead putting each JSON object on a single line.

Why would you want this? For one, it makes your output grep-able. For example,
I’ll remove the `select` and grep out the lines I care about:

    
    
    root@kali# cat infractions.json | jq -c '.infractions | group_by(.name) | .[] | {"name": .[0].name, "severity": [.[].severity] | add, "num_infractions": .|length, "infractions": [.[].title]}' | grep -e Boq -e Bini
    {"name":"Bini Aru","severity":19,"num_infractions":4,"infractions":["Giving super atomic wedgies","Aggravated pulling of hair","Aggravated pulling of hair","Possession of unlicensed slingshot"]}
    {"name":"Boq Questrian","severity":18,"num_infractions":4,"infractions":["Playing with matches","Giving super atomic wedgies","Throwing rocks (at people)","Throwing rocks (at people)"]}
    

I can even go back into pretty print by piping the `grep` results back to`jq`:

    
    
    root@kali# cat infractions.json | jq -c '.infractions | group_by(.name) | .[] | {"name": .[0].name, "severity": [.[].severity] | add, "num_infractions": .|length, "infractions": [.[].title]}' | grep -e Boq -e Bini | jq .
    {
      "name": "Bini Aru",
      "severity": 19,
      "num_infractions": 4,
      "infractions": [
        "Giving super atomic wedgies",
        "Aggravated pulling of hair",
        "Aggravated pulling of hair",
        "Possession of unlicensed slingshot"
      ]
    }
    {
      "name": "Boq Questrian",
      "severity": 18,
      "num_infractions": 4,
      "infractions": [
        "Playing with matches",
        "Giving super atomic wedgies",
        "Throwing rocks (at people)",
        "Throwing rocks (at people)"
      ]
    }
    

Or, what if I want to easily count how many names there are from my last
query?

    
    
    root@kali# cat infractions.json | jq -c '.infractions | group_by(.name) | .[] | {"name": .[0].name, "severity": [.[].severity] | add, "num_infractions": .|length, "infractions": [.[].title]}' | wc -l
    527
    

### More Selects

Looking at my moles, I want to find five others with similar properties. I can
use `-c` with `wc -l` and different select statements to look for something
interesting.

Total severity greater than 17? Too many:

    
    
    root@kali# cat infractions.json | jq '.infractions | group_by(.name) | .[] | {"name": .[0].name, "severity": [.[].severity] | add, "num_infractions": .|length, "infractions": [.[].title]} | select(.severity > 17)' | wc -l
    268
    

What about “Giving Super Atomic Wedgies”, which is a shared infraction:

    
    
    root@kali# cat infractions.json | jq '.infractions | group_by(.name) | .[] | {"name": .[0].name, "severity": [.[].severity] | add, "num_infractions": .|length, "infractions": [.[].title]} | select(.infractions|contains(["Giving super atomic wedgies"]))' | wc -l
    178
    

Still too many. But what about wedgies and 4 or more infractions:

    
    
    root@kali# cat infractions.json | jq -r '.infractions | group_by(.name) | .[] | {"name": .[0].name, "severity": [.[].severity] | add, "num_infractions": .|length, "infractions": [.[].title]} | select((.infractions|contains(["Giving super atomic wedgies"])) and (.num_infractions >= 4)) | .name' 
    Bini Aru
    Boq Questrian
    Erin Tran
    Kirsty Evans
    Lance Montoya
    Nina Fitzgerald
    Tracey Rowe
    Wesley Morton
    

There we go. A list that includes our two known moles and five others.

## JA3 on ICEDID PCAP

### Background

I’ve been messing around with [JA3](https://github.com/salesforce/ja3) at work
a bit lately. JA3 is an attempt to give the defender some insight into SSL/TLS
connections by creating a hash based on the connection set up data, which
allows you to fingerprint different programs. It’s not a silver bullet, but it
seems pretty neat.

For the purposes of this example, there’s a [python
script](https://github.com/salesforce/ja3/blob/master/python/ja3.py) that
outputs json data (when you use `-j` or `--json`). For example, here’s a
[Emotet/ICEDID pcap from malware-traffic-analysis.net](https://www.malware-
traffic-analysis.net/2018/12/10/index2.html):

    
    
    $ ja3 --json pcaps/2018-12-10-Emotet-infection-with-IcedID.pcap
    [                                                                                        
        {                                                    
            "destination_ip": "178.21.8.42",                                                 
            "destination_port": 443,                         
            "ja3": "769,47-53-5-10-49171-49172-49161-49162-50-56-19-4,65281-0-10-11,23-24,0",
            "ja3_digest": "1d095e68489d3c535297cd8dffb06cb9",
            "source_ip": "10.12.10.102",  
            "source_port": 49313,                                                            
            "timestamp": 1544467801.411811                   
        },                                                                                   
        {                                                    
            "destination_ip": "178.21.8.42",                                                 
            "destination_port": 443,                         
            "ja3": "769,47-53-5-10-49171-49172-49161-49162-50-56-19-4,65281-0-10-11,23-24,0",
    ...[snip]...
    

### Analysis

The script will output an object for each client hello in the pcap. The first
question I wanted to know - how many are there? I’ll use jq and start with the
top element, and pipe that into the length function:

    
    
    $ ja3 --json pcaps/2018-12-10-Emotet-infection-with-IcedID.pcap | jq '. | length'
    32
    

Next, I might ask - how many different ja3_digests are in this pcap. Rather
than just show you the result, I’ll show you how I built this query.

First, I’ll just isolate the ja3_digest strings:

    
    
    $ ja3 --json pcaps/2018-12-10-Emotet-infection-with-IcedID.pcap | jq '.[].ja3_digest'
    "1d095e68489d3c535297cd8dffb06cb9"
    "1d095e68489d3c535297cd8dffb06cb9"
    "1d095e68489d3c535297cd8dffb06cb9"
    "1d095e68489d3c535297cd8dffb06cb9"
    ...[snip]...
    

Now, one simple option is to just leave `jq` at this point and go back to bash
(I’ll add in `-r` for raw to get rid of the quotes):

    
    
    $ ja3 --json pcaps/2018-12-10-Emotet-infection-with-IcedID.pcap | jq -r '.[].ja3_digest' | sort | uniq -c | sort -nr
         32 1d095e68489d3c535297cd8dffb06cb9
    

But I can also do it in `jq`. First, get my results into an array:

    
    
    $ ja3 --json pcaps/2018-12-10-Emotet-infection-with-IcedID.pcap | jq -r '[.[].ja3_digest]'
    [
      "1d095e68489d3c535297cd8dffb06cb9",
      "1d095e68489d3c535297cd8dffb06cb9",
      "1d095e68489d3c535297cd8dffb06cb9",
    ...[snip]...
      "1d095e68489d3c535297cd8dffb06cb9"
    ]
    

Then pipe that into unique:

    
    
    $ ja3 --json pcaps/2018-12-10-Emotet-infection-with-IcedID.pcap | jq -r '[.[].ja3_digest] | unique'
    [
      "1d095e68489d3c535297cd8dffb06cb9"
    ]
    

I can add `[]` or `| .[]` to the end to remove the array:

    
    
    $ ja3 --json pcaps/2018-12-10-Emotet-infection-with-IcedID.pcap | jq -r '[.[].ja3_digest] | unique[]'
    1d095e68489d3c535297cd8dffb06cb9
    

In this example, just bouncing out to bash seems like the easier path, but
there will be times when I may want to build another json object like I did in
the Holiday Hack example, and I’ll need a `jq` solution for that.

## Summary

`jq` is just handy tool to have in your toolbox. It comes in handy for little
things all the time, but it also can make analysis of large chunks of json so
much easier. I’d argue that anyone in infosec or anyone that does any kind of
technical analysis would benefit from knowing, at least the basics.

[](/2018/12/19/jq.html)

