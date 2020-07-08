sudo systemctl stop switch_actions.service
sudo cp switch_actions.py /usr/local/bin
sudo cp switch_actions.service /etc/systemd/system
sudo cp *.wav /usr/local/bin
sudo systemctl enable switch_actions.service
sudo systemctl start switch_actions.service
