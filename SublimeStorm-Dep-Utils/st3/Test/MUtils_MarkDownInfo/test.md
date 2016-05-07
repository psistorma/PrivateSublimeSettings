# Config multiple account for github in one pc

## 1. [Generate ssh key](https://help.github.com/articles/generating-an-ssh-key/).

open **Git Bash** in **Adminstrator** mode:

```bash
$ ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
$ eval "$(ssh-agent -s)"
$ ssh-add ~/.ssh/id_rsa
$ clip < ~/.ssh/id_rsa.pub
```

## 2. [Setup multiple ssh account](http://code.tutsplus.com/tutorials/quick-tip-how-to-work-with-github-and-multiple-accounts--net-22574)

**file**: `C:\Users\Administrator\.ssh\config`:

```ini
#psistorma
Host github.com
  HostName github.com
  User git
  IdentityFile ~/.ssh/id_rsa

#iamstorm
Host github-iamstorm
  HostName github.com
  User git
  IdentityFile ~/.ssh/id_rsa_iamstorm
```
