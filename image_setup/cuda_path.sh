#!/usr/bin/env bash

cuda_Keyword='
# cuda setting
export PATH=/usr/local/cuda/bin:$PATH
export LD_LIBRARY_PATH=/usr/local/cuda/lib64:$LD_LIBRARY_PATH
'

case $SHELL in
    *zsh )
    shell=zsh
    profile=~/.zshrc
    login_profile=~/.zprofile
    ;;
    *bash )
    shell=bash
    profile=~/.bashrc
    login_profile=~/.bash_profile
    ;;
    *ksh )
    shell=ksh
    profile=~/.profile
    ;;
    * )
    Echo_Color r "Unknow shell, need to manually add pyenv config on your shell profile!!"
    ;;
esac

echo "$cuda_Keyword" >> $profile

exec $shell