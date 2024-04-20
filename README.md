# logki: Log Analysis Toolkit

[![build status](https://github.com/Perfexionists/logki/actions/workflows/ubuntu.yml/badge.svg)](https://github.com/Perfexionists/logki/actions)
[![codecov](https://codecov.io/gh/Perfexionists/logki/graph/badge.svg?token=3x4Luodr84)](https://codecov.io/gh/Perfexionists/logki)
[![Codacy Badge](https://app.codacy.com/project/badge/Grade/a704486b4679442cb2a53173475f79ca)](https://app.codacy.com/gh/Perfexionists/logki/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_grade)
[![GitHub tag](https://img.shields.io/github/tag/Perfexionists/logki.svg)](https://github.com/Perfexionists/logki)


<p align="center">
  <img src="https://raw.githubusercontent.com/Perfexionists/logki/devel/figs/logo.png">
</p>

Logki is a log analysis toolkit: a prompt application for on-the-fly analysis of big logs.

## Installation

Note that we are no longer maintaining support for Python 3.8, nor do we support Python 3.12
(this is due to some of its dependencies). Logki may work, but we strongly advise to upgrade your 
Python to one of the supported version between Python 3.9 and Python 3.11.

You can install logki from pip as follows:

    pip3 instal logki 

Alternatively you can install logki from the source code as follows:

    git clone https://github.com/Perfexionists/logki.git
    cd logki
    make install

These commands install logki to your system as a runnable python package. You can then run logki
safely from the command line using the `logki` command. 

It is advised to verify that logki is running correctly in your environment as follows:

    # You can run this only once: it will initialize the requirements necessary for testing
    make init-test
    # Runs all tests using pytest
    make test

or alternatively using Tox if you wish to test for more Python versions 
(see the [developing section](#developing)).

## Developing

In order to commit changes to the logki, you have to install logki in development mode:

    git clone https://github.com/Perfexionists/logki.git
    cd logki
    make dev

This method of installation allows you to make a changes to the code, which will be then reflected
by the installation.

If you are interested in contributing to logki project, please refer to
[contributing](CONTRIBUTING) section. If you think your results could help others, please [send us
PR](https://github.com/Perfexionists/logki/pull/new/develop), we will review the code and in case it is
suitable for wider audience, we will include it in our [upstream](https://github.com/Perfexionists/logki).

But, please be understanding, we cannot fix and merge everything immediately.

## Getting Started

Simply run the following command:

    logki [LOGFILE]

Contributing
------------

If you'd like to contribute, please first fork our repository and create a dedicated feature branch. Pull requests are
warmly welcome. We will review the contribution (possibly request some changes).

In case you run into some unexpected behaviour, error or anything suspicious, either contact us
directly through mail or [create a new Issue](https://github.com/Perfexionists/logki/issues/new).

If you are interested in contributing to logki project, please first refer to
[contributing](Contributing.md) section. If you think your custom module could help others, please
[send us PR](https://github.com/Perfexionists/logki/pull/new/develop), we will review the code and in case
it is suitable for wider audience, we will include it in our
[upstream](https://github.com/Perfexionists/logki).

But, please be understanding, we cannot fix and merge everything.

Links
-----

-   GitHub repository : [https://github.com/Perfexionists/logki](https://github.com/Perfexionists/logki)
-   Issue tracker: [https://github.com/Perfexionists/logki/issues](https://github.com/Perfexionists/logki/issues)
    -   In case of sensitive bugs like security vulnerabilities, please
        contact [Tomas Fiedor](mailto:TomasFiedor@gmail.com) directly
        instead of using issue tracker. We value your effort to improve the security and privacy of our project!

Unrelated links:

-   Check out our research group focusing on program analysis, static and dynamic analysis, formal methods, verification
    and many more: [VeriFIT](http://www.fit.vutbr.cz/research/groups/verifit/index.php.en)

Licensing
---------

The code in this project is licensed under [GNU GPLv3 license](https://github.com/Perfexionists/logki/blob/devel/LICENSE).