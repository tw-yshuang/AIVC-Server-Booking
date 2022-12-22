
#!/usr/bin/env bash

FILES=(.zshrc .zsh_history)

for key in ${!FILES[*]}; do
    echo "if [ -f '/root/Work/${FILES[$key]}' ]; then cp /root/Work/${FILES[$key]} ~/${FILES[$key]} ; fi" >> ~/.zlogin
    echo "cp ~/${FILES[$key]} /root/Work/${FILES[$key]}" >> ~/.zlogout
done