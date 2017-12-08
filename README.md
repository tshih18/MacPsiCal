# MacPsiCal

## Mac Setup Instructions
### 1. Enable Internet Sharing
  - System Preferences -> Sharing -> [Check] Internet Sharing -> [Check] the allowed ports
### 2. Static IP Address
  - System Preferences -> Network -> [Select] (Thunderbolt)Ethernet
  - Configure IPv4: [Select] Manually
  - Example IP Address: 169.254.140.200 (Digits must be between 0-255)
  - Subnet Mask: 255.255.0.0 or 255.255.255.0 will work
  - When done editing -> Apply

## Pi Setup Instructions
### 1. Static IP Address
  - Open Terminal
  - Type: sudo nano /etc/dhcpcd.conf
  - At the very bottom type:
  interface eth0
  static ip_address=169.254.140.201/24
  static routers=169.254.140.1
  static domain_name_servers=8.8.8.8 8.8.4.4
  - ctl+x -> y -> enter
