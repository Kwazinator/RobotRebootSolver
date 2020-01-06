# RobotRebootSolver
program that can automatically solve the robot reboot challenge at robotreboot.com using a depth first search algorithmn.
All credit to the Algorithmn goes to Micheal Fogelman @ https://github.com/fogleman/Ricochet

This project is the implementation of it to autosolve at robotreboot.com

***************INSTALLATION***************************
requires:
gcc
chromedriver
python3

for Ubuntu:
sudo apt-get update
sudo apt-get install -y unzip xvfb libxi6 libgconf-2-4
sudo curl -sS -o - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add
sudo echo "deb [arch=amd64]  http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list
sudo apt-get -y update
sudo apt-get -y install google-chrome-stable
wget https://chromedriver.storage.googleapis.com/2.41/chromedriver_linux64.zip
unzip chromedriver_linux64.zip
sudo mv chromedriver /usr/bin/chromedriver
sudo chown root:root /usr/bin/chromedriver
sudo chmod +x /usr/bin/chromedriver

#then install requirements.txt from the repository

pip install -r requirements.txt

allow build_ricochet to be executable to generate the C binaries

chmod +x build_ricochet
./build_ricochet

then you can run with
python3 RobotSolverExtract.py
*******************************************************************
general output is as follows:

<color>_<direction> example: y_U means yellow up and b_D means Blue down.
*********************************************************************
arguements:
--post will prompt for a username that will automatically post it to the website when solved.


