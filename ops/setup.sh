# 1. Make sure other files in this folder have been placed where directed.
# 2. Assumes a user called polybot

POLYBOT_SERVICE_NAME="polybot_discord.service"
POLYBOT_PATCH_NAME="polybot_patch.timer"

sudo systemctl daemon-reload
sudo systemctl start $POLYBOT_SERVICE_NAME
sudo systemctl enable $POLYBOT_SERVICE_NAME
sudo systemctl start $POLYBOT_PATCH_NAME
sudo systemctl enable $POLYBOT_PATCH_NAME
