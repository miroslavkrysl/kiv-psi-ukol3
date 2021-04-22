# KIV/PSI - úkol 3

Author: Miroslav Krýsl

## Description

Simple International Space Station (ISS) location tool.
It sends requests to *Open Notify - ISS Location Now* service server to get information about ISS
and to *Sunrise Sunset* service to get times of sunrise and sunset on current ISS location.
Received data is used to determine observation conditions on the current ISS location.

**Open Notify - ISS Location Now**: http://open-notify.org/Open-Notify-API/ISS-Location-Now/

**Sunset Sunrise**: https://sunrise-sunset.org/api

## Install, run

It is written in Python 3 which needs to be installed.

`requests` Python library (https://docs.python-requests.org/en/master/) is used for http requests.
It needs to be installed locally:

```
pip install requests
```

Alternatively you could use the Pipenv virtual environment.

To install Pipenv:

```
pip install pipenv
```

And then to run the program:

```
pipenv shell
python main.py
```