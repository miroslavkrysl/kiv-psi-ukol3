# KIV/PSI - úkol 3

Author: Miroslav Krýsl

## Description

Simple International Space Station (ISS) location tool.
It sends requests to *Open Notify - ISS Location Now* online service to get information about ISS
and to *Sunrise Sunset* online service to get times of sunrise and sunset on current ISS location.
Received data is used to determine observation conditions on the current ISS location.

In addition, to correctly calculate whether it is day or night, it is also necessary to fetch the sunset
time from yesterday and sunrise time from tomorrow. The computation returns wrong
results in some cases otherwise.

**Open Notify - ISS Location Now**: http://open-notify.org/Open-Notify-API/ISS-Location-Now/

**Sunset Sunrise**: https://sunrise-sunset.org/api

## Install, run

It is written in Python 3 which needs to be installed.

`requests` Python library (https://docs.python-requests.org/en/master/) is used for http requests.
It needs to be installed locally:

```
pip install requests
```

And to run the program:

```
python main.py
```

Alternatively you could use the Pipenv virtual environment.

To install Pipenv:

```
pip install pipenv
```

And then to run the program (in project root):

```
pipenv shell
python main.py
```