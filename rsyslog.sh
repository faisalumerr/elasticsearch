
# =====================================
#   rsyslog installation script
# =====================================
# Setup rsyslog as a UDP syslog server on <server-ip>:514

#!/bin/bash
set -e

echo "[*] Installing rsyslog..."
sudo apt-get update -y
sudo apt-get install -y rsyslog

echo "[*] Enabling UDP syslog reception..."
sudo sed -i 's/#module(load="imudp")/module(load="imudp")/' /etc/rsyslog.conf
sudo sed -i 's/#input(type="imudp" port="514")/input(type="imudp" port="514")/' /etc/rsyslog.conf

echo "[*] Creating log directory..."
sudo mkdir -p /var/log/remote

echo "[*] Adding rule to log all remote syslog messages..."
sudo bash -c 'cat >> /etc/rsyslog.d/remote.conf <<EOF
if (\$fromhost-ip != "127.0.0.1") then {
    action(type="omfile" file="/var/log/remote/remote.log")
    stop
}
EOF'

echo "[*] Restarting rsyslog service..."
sudo systemctl restart rsyslog
sudo systemctl enable rsyslog

echo "[*] Opening firewall for UDP 514..."
sudo iptables -A INPUT -p udp --dport 514 -s 0.0.0.0/0 -j ACCEPT

echo "[*] Syslog server setup complete."
echo "[*] Listening on UDP <server-ip>:514"

# =====================================
# Optional: Uninstall rsyslog script
# =====================================


# #!/bin/bash

# echo "Stopping rsyslog service..."
# sudo systemctl stop rsyslog

# echo "Disabling rsyslog from startup..."
# sudo systemctl disable rsyslog

# echo "Removing rsyslog package..."
# sudo apt-get purge -y rsyslog

# echo "Removing residual configuration files..."
# sudo apt-get autoremove --purge -y
# sudo apt-get clean

# echo "Checking if rsyslog is still installed..."
# if dpkg -l | grep -q rsyslog; then
#     echo "❌ rsyslog removal failed!"
# else
#     echo "✅ rsyslog successfully uninstalled."
# fi
