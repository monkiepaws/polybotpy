#!/bin/sh

# leave in ops folder

systemctl stop polybot_discord.service
yum -y update
/usr/sbin/reboot --reboot
