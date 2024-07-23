# SANS SEC599 Review

[training](/tags#training ) [review](/tags#review ) [purple-
team](/tags#purple-team )  
  
Jul 24, 2018

SANS SEC599 Review

I had the chance to take [SANS SEC599](https://www.sans.org/course/defeating-
advanced-adversaries-kill-chain-defenses), “Defeating Advanced Adversaries -
Purple Team Tactics & Kill Chain Defenses” last week at SANSFIRE. The class is
one of the newer SANS offerings, and so I suspect it will be changing and
updating rapidly. There are some things I would change about the class, but
overall, I enjoyed the class, definitely learned things that I didn’t know
before, and got to meet some really smart people.

## Course structure

### My Mistaken Impression Coming In

When I look at the title of the class, what got me really excited about it was
the “Purple Team Tactics” part. When I think of purple teaming, I think of red
and blue working together to start pushing the boundaries of current
detection/prevention. When you come to a point where blue can’t detect/prevent
the activity, you can then work to configure the environment to bring addition
data to the SIEM, generate new alerts / rules, and configure systems to
increase logging and close vulnerabilities. And that is what the class taught
as well.

Coming in, I had overlooked the second half of the title, “Kill Chain
Defenses”. This isn’t necessarily a bad thing, but it led to some confused
expectations. Where I had read the class as “Purple Teaming”, it really should
have been seen as “Advanced Defence, Achieved Through Both Purple Teaming AND
Other Kill Chain Defenses”.

### Structure

The class structure was set up to spend a block of time walking through each
step in the cyber kill chain.

### Day 1

The first day, “Knowing the Adversary, Knowing Yourself” was a bit of a mixed
bag. There was general overview stuff, a discussion how to set up your space
to be defensible, and some information about scanning and open source
intelligence gathering, which aligns to step one in the kill chain,
reconnaissance.

To be honest, this day was a bit of a disappointment, like every other SANS
first day I’ve experienced (except SEC660). There was a fair amount of
overview material, and it was a little unfocused. There was a lab where we
built a phishing document, and used it to gain access to the target
environment, and then stole credentials to a file server and exfilled the
secret plans. It wasn’t clear why it was there, other than to make sure
everyone could use Kali/Metasploit. Another lab we ran Nessus against an
environment to check for vulnerabilities. It’s not that this content isn’t
interesting, it’s just that I’ve had it in SEC560, and I’m sure other parts
are covered in some of the defensive classes I haven’t taken. By the end of
day 1, there was no real purple teaming, other than some discussion of what it
was.

### Day 2

Day 2 was titled “Averting Payload Delivery”, where we talked about not only
phishing, but removable media, and even delivery for lateral movement with
attacks like SMB relay using Responder. This day was mostly focused on Kill
Chain step 2 and 3, Weaponization and Delivery, though (due to the
imperfections in the kill chain, some of the lateral movement stuff could be
considered Actions on Objectives).

The labs were all around good. The first lab, using Responder, and then
configuring GPOs at the domain controller to enable SMB signing and turn off
LLMNR, and then trying again and seeing that the attack is now unsuccessful
was exactly what I was hoping to get out of the class. Other labs were good,
though not really purple activities. Still, I enjoyed the lab where we used
Suricata, Cuckoo, and YARA to build (really, finish building, as most of the
work was already done) a sandbox environment for email attachments. In
another, we got to set up ELK to detect exploit kit activity.

### Day 3

Day 3 was titled “Preventing Exploitation”, and was focused on kill chain step
4, exploitation. We looked at hardening using AD and GPO to restrict
scripting, putting whitelisting in place, and setting up logging with Sysmon.
We built out queries and visualizations in our ELK SIEM to help see and
understand the data. We looked at various protections that EMET can enable.
Throughout the day we used purple teaming strategies to identify problems, and
then fix them and show that they were fixed. I really enjoyed this day, as it
gave me a lot of insight into an area that I was weak in (Windows hardening
and configuration, and active directory), and provided the purple team mindset
to show the problem, and then show how it was fixed.

### Day 4

“Avoiding Installation, Foiling Command and Control, and Thwarting Lateral
Movement” aimed to tackle the last three kill chain stages - Installation, C2,
and Actions on Objectives. We looked at persistence and autoruns, OSquery,
privesc, C2, and lateral movement. It was a lot, and frankly, I think this
could have easily been 2 or more days to cover each of these better. A real
discussion of detecting and stopping lateral movement could take a full day on
it’s own.

In the labs, we got hands on with Autoruns, OSquery, Suricata, Bro. We also
did more GPO creation to make lateral movement more difficult.

### Day 5

Day 5 continues Actions on Objectives with with “Thwarting Exfiltration, Cyber
Deception, and Incident Response”. I thought the exfiltration section was
good, but a bit rushed. Then we moved into Cyber Deception. I found this
interesting, and I learned from it. However, it also didn’t totally fit into
the class, and I might suggest dropping it to do a better job on some of the
other sections. Finally, there was a section on IR which was pretty much a
waste. IR is something much better handled in the other SANS classes devoted
to it, such as [FOR508](https://www.sans.org/course/advanced-incident-
response-threat-hunting-training).

### Structure Summary

I think the structure of this class was imperfect at best, at least for my
needs. It tries to be a little bit of everything, and then ends up rushing
through some really interesting parts that could use more coverage.

## Labs

### Technical Setup

The labs were all run through a browser with remote desktop access to various
machines. The setup was actually quite slick. For each lab, you’d hit a button
to start the lab environment, and a new browser window would open, and it
would take 1-2 minutes to load the environment. When the screen would load,
there was a virtual machine in the main center window. On the bottom was a
bar, with the current instructions for the lab, and a next button to move to
the next step. On the right, was a sidebar with each of the machines used in
the lab, and the ability to switch to bring them into the main view, as well
as shortcuts for ctrl+alt+del, and ways to paste into the vms.

One downside of this configuration is that you don’t get the VMs for the
Windows AD environment to take home with you.

### Content

Overall, most of the lab content was really good. The course authors did a
good job of getting some of the really heavy lifting done beforehand. For
example, getting Cuckoo set up is a giant pain. But they took care of all of
that for us, and just had us set up the connections between Suricata on the
mail server and Cuckoo, and then we loaded Yara rules into the Cuckoo setup.
It showed off what we could do, and having us go through all of the pain in
class wouldn’t really have helped anyone.

There were about half the labs that were great examples of purple teaming, and
I particularly enjoyed those. The other half typically demonstrated some
useful defensive capabilities, some of which I will use in my day job.

## Instructor

In my offering, the instruction was one of the course co-authors, Eric Van
Buggenhout. He was awesome. He was skilled both technically and as a
presenter. He did a good job going through complex material, and mixed in a
ton of _really_ corny jokes to keep it light.

His time management was pretty good, though most days we ended the course
content with a final lab to go around 5, so plan on an extra 20-30 minutes if
you want to do the last lab.

## CTF

The final CTF consisted of two parts running at the same time. First, there
was a jeopardy-style board with questions worth points. At the same time, you
had a small network to defend against waves of attacks, and stopping various
attacks was worth points. I didn’t catch a rationale behind having two
unrelated tasks, but my guess is that it’s to similar the real world, where
you are doing your day job and hardening and dealing with attacks all at the
same time.

The jeopardy style part really wasn’t even that related to the class material.
It had some malware re, some pcap analysis, some trivia, etc. The questions
were definitely infosec focused, but not really anything from this class.

I wish I had spent more time thinking out a strategy for defending our network
at the start instead of just diving into the questions. Were it up to me, I’d
probably cut the jeopardy part entirely. I understand the desire to replicate
the real world, but I ended up spending a lot of time on it, and missed out on
a chance to use my newly developed skills in the final day.

## Conclusion

Overall, I for the most part enjoyed my time in SEC599, and it was worth my
time. As with every other SANS class I’ve taken, it was really solid training,
by experts in the field, and I walked away with things I can use in my day
job.

I do think there are structural flaws in the class, and that it would benefit
from some restructure, and perhaps even breaking it into multiple classes.
That said, once I got over my expectation that everything be purple team
focused, it was really a solid course.

[](/2018/07/24/sans-sec599-review.html)

