#!/usr/bin/env bash

fl_font=('3D-ASCII' '3-D' '3d' 'Broadway' 'Electronic' 'Isometric1' 'ANSI Regular' 'ANSI Shadow' 'Big Money-ne' 'Big Money-nw' 'Delta Corps Priest 1' 'DOS Rebel')
echo
figlet -f ${fl_font[$((${RANDOM} % ${#fl_font[*]} + 1))]} "A I V C" | lolcat -f
echo