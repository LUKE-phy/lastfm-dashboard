# Lastfm-Dashboard

A small personal dashboard that visualizes Last.fm listening data.
Built as a weekend project to make music consumption more tangible again.

Uses the Last.fm API to display listening stats and recent tracks.
Designed to run on a Raspberry Pi with optional e-ink or small displays.

This project is intentionally simple and meant for personal use and experimentation.
It was optimized to run on an HDMI square screen, with 480x480px.

Adhjustments should be made, if your project should run on a 480x380 screen.
The script should be set in autostart, to enable opening upon bootup.

---

### Why this exists

This project started as a small weekend experiment.
I wanted to make music consumption feel more intentional again
and turn abstract listening data into something tangible.

It’s not meant to be perfect - just meaningful.

### Setup Instructions

1. Download Raspberry Pi OS (with Desktop) from the official website.
2. Flash the image to an SD card (I recommend using Raspberry Pi Imager).
3. Activating SSH is recommended, in order to start script remotely/make changes.
4. Boot your Raspberry Pi, set up your username/password, and connect it to the internet.

### Update the System

1. open the terminal and run:
   
   sudo apt update && sudo apt upgrade -y
   
This updates the package lists and installs all available updates.

### Install Phyton and pip

1. open the terminal again and run:

   sudo apt install python3 python3-pip -y

phyton = Phyton interpreter
pip = Phyton Package manager

Check if the installation has been done correctly by typingg:
python3 --version
pip3 --version

### Create a folder

1. open the terminal and type:

mkdir lastfm-display

Name is customizable. I chose lastfm-display,

### Install virtual envoirement (optional)

1. open the terminal and enter:

python3 -m venv ~/lastfm-venv
source ~/lastfm-venv/bin/activate

The last command, always gets you back on track into your virtual envoirement, in case you restart your pi.

### Install required python packages

1. open the terminal and enter:
   
pip install requests pygame pillow

2. verify the installation with:
   
   python3 -c "import pygame, requests, PIL; print('OK')"

   If OK appears, all packages are installed correctly.

### Enter api Key in lastfm.py file.

1. Open the following page: https://www.last.fm/api/authentication
2. Click on apply for a key.
3. Click on create and give the key a name.
4. Copy the key to your dashboard
5. Open lastfm.py and paste your key inbetween both " " .
6. Save the lastfm.py. Make sure to not change for formatting and save it as .py file.

   ##

It rotates every 30 seconds, with a smooth transition from: Top Albums (Last 7 Days) to - 
Top Tracks (Last 7 Days) and ends with Top Artists (Last 7 Days)

![644A86DA-7080-47AD-ABE1-6255CB3105FA_1_102_a](https://github.com/user-attachments/assets/a05deb58-370e-4b20-8645-7673ea4400a0)
![045A3B79-285F-4E71-9AB4-507E6581A862_1_102_a](https://github.com/user-attachments/assets/ca1a70e0-8ca6-4904-ab20-494799fc16b9)
![C6C77BB2-37FC-4B5B-BFCB-726B3BF946BD_4_5005_c](https://github.com/user-attachments/assets/f6dbe6f9-3cfc-41ed-9c51-3bb7d9c7418d)
##
