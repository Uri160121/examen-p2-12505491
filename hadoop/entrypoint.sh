#!/bin/bash
set -e
if [ ! -f /keys/id_ed25519 ]; then
  ssh-keygen -q -t ed25519 -N "" -f /keys/id_ed25519
fi
H=/home/hadoopuser/.ssh
install -d -m 700 -o hadoopuser -g hadoopuser $H
install -m 600 -o hadoopuser -g hadoopuser /keys/id_ed25519 $H/id_ed25519
install -m 644 -o hadoopuser -g hadoopuser /keys/id_ed25519.pub $H/id_ed25519.pub
install -m 600 -o hadoopuser -g hadoopuser /keys/id_ed25519.pub $H/authorized_keys
printf 'Host *\n  StrictHostKeyChecking no\n  UserKnownHostsFile /dev/null\n  LogLevel ERROR\n' > $H/config
chown hadoopuser:hadoopuser $H/config && chmod 600 $H/config
exec /usr/sbin/sshd -D -e
