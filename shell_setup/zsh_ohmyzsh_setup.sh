#!/usr/bin/env bash

# install zsh
apt-get install -y zsh 
chsh -s $(which zsh)

# oh-my-zsh package install, won't auto switch to the zsh.
sh -c "$(wget -qO- https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)" "" --unattended
