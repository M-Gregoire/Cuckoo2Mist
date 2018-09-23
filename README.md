# Cuckoo2Mist [![Build Status](https://travis-ci.org/M-Gregoire/Cuckoo2Mist.svg?branch=master)](https://travis-ci.org/M-Gregoire/Cuckoo2Mist) [![Coverage Status](https://coveralls.io/repos/github/M-Gregoire/Cuckoo2Mist/badge.svg?branch=master)](https://coveralls.io/github/M-Gregoire/Cuckoo2Mist?branch=master)

Original description : The Malware Instruction Set (MIST) is a representation for monitored behavior of malicious software. The representation is optimized for effective and efficient analysis of behavior using data mining and machine learn- ing techniques. It can be obtained automatically during analysis of malware with a behavior monitoring tool or by converting existing behavior reports. The representation is not restricted to a particular monitoring tool and thus can also be used as a meta language to unify behavior reports of different sources.

## Goals

I'm using the awesome [Cuckoo Sandbox](https://cuckoosandbox.org) and I wanted to be able to use [malheur](http://www.mlsec.org/malheur) with it.  
Unfortunately, Cuckoo cannot produce the reports in mist as needed by malheur. I found no working and easy solution to convert the reports from Cuckoo to mist file that malheur could use. [Philipp Trinius](https://sourceforge.net/u/trinius/profile/) wrote Cuckoo2Mist that does just that, but sadly, this project is not maintained, does not work with the current Cuckoo reports nor Python 3.  

This project aims to update Cuckoo2Mist so it is maintained and well documented.  

Do not hesite to contribute !  

## Project

This project is composed of two folders :
- `Cuckoo2Mist` which contains the main script to convert JSON to MIST.
- `CuckooModule` which contains a Cuckoo module which automatically run the Cuckoo2Mist script after each analysis.

## Donation

This project helped you ? You can buy me a cup of coffee  
[![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg)](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=EWHGT3M9899J6)
