# Cuckoo2Mist

Original description : The Malware Instruction Set (MIST) is a representation for monitored behavior of malicious software. The representation is optimized for effective and efficient analysis of behavior using data mining and machine learn- ing techniques. It can be obtained automatically during analysis of malware with a behavior monitoring tool or by converting existing behavior reports. The representation is not restricted to a particular monitoring tool and thus can also be used as a meta language to unify behavior reports of different sources.

## Goals

I'm using the awesome [https://cuckoosandbox.org/](Cuckoo Sandbox) and I wanted to be able to use [http://www.mlsec.org/malheur/](malheur) with it. 
Unfortunately, Cuckoo cannot produce the reports in mist as needed by malheur. I found no working and easy solution to convert the reports from Cuckoo to mist file that malheur could use. [https://sourceforge.net/u/trinius/profile/](Philipp Trinius) wrote Cuckoo2Mist that does just that, but sadly, this project is not maintained, does not work with the current Cuckoo reports nor Python 3.

This project aims to update Cuckoo2Mist so it is maintained and well documented.

Do not hesite to contribute !

## How to use

Just put all the reportsXX.json from Cuckoo in the reports folder.
Launch `python3 cuckoo2mist.py` and it should work !
Any review/comment/bug report is welcome !

## Todo :
- [x] Full python3 support
- [ ] Autogenerate config based on cuckoo report analysis
- [x] Add verbose functionnality
- [x] Fonctionnal Cuckoo2Mist (soon !)
- [x] Fully commented code
- [ ] Write complete documentation
