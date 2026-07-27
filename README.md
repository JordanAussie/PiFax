# PiFax
A simple python based program that allows you to send print jobs to Raspberry Pi's connected to a printer, like an old school fax machine except now you can connect to them wirelessly!

## How To Install
To quickly and easily be able to install this package, I have included an installer. To install the PiFax system you want to go to the root folder of this repository by running `cd PiFax` and then go to the `src` folder by running `cd src`. To start the installer run:
```terminal
sudo python installer.py
```
Or if that doesn't work then run
```terminal
sudo python3 installer.py
```
Next you will be prompted with some questions regaurding the setup and install of the PiFax system. I recomend typing `y` for every field, but I will go into an explanation of what each question is asking.

<div align="center">
    <img src="assets/installer.png" alt="Installer Image" width="300">
</div>

## Installer Questions
The different questions in the installer do separate things based on how you want the system to be setup and I will explain each question here:

`Do you wish to start the installer? Y|N`
This question will just make sure that you are apsolutly sure that you want to run the installer and it will install cups and make the necesary folders on you machine.

`Would you like to create a systemd file for fax_checker.py? Y|N`
This question will make a systemd file that controls the fax_checker.py file, so that you can start/stop it and enable/disable it for startup.

`Would you like to enable this service at startup? Y|N`
This question will only show if you answered the last question as Y, it will then set the service to start on startup. Alternativly, you can also type:
```terminal
sudo systemctl enable pifax.service
```

`Would you like to start this service now? Y|N`
This question will also only show if you answered Y to the second question and it will start the service now so that when done with the installer it is started. Alternativly, you can also type:
```terminal
sudo systemctl start pifax.service
```

`Would you like to make any custom commands? Y|N`
This question simply just asks you if you want to make custom commands, so that if you don't, then it will save time in the installer.

`Would yopu like to make a PiFax command? Y|N`
This question will only show if you answered the last question with Y and it will make a custom command that runs the client.py, the custom command is `PiFax`.

`Would you like to make an add-printer command? Y|N`
This question will only show if you answered the fifth question with Y and it will make a custom command that opens up the cups admin pannel in chromium so that you can add a printer, the custom command is `add-printer`. SIDE NOTE: This custom command only works in a graphical desktop.

`Would you like to enable CUPS? Y|N`
This question is asking if you want to enable the cups web interface on startup so that you can add and manage printers. Alternativly, you can also type:
```terminal
sudo systemctl enable cups
```

`Would you like to start CUPS? Y|N`
This question is asking if you want to start the cups web interface now so that you can add and manage printers. Alternativly, you can alos type:
```terminal
sudo systemctl start cups
```

## How to use PiFax
Throughout the setup, it might seem like a lot, but it isn't to difficult to run and use PiFax. The first thing you should do is startup the PiFax client, the installer automatically moved the client to `/pifax-python/`, so you will need to run:
```terminal
python /pifax-python/client.py
```
Or if you said Y to making a PiFax command:
```terminal
PiFax
```
Now you will see a screen that looks like this:
<div align="center">
    <img src="assets/client.png" alt="Client Image" width="300">
</div>
You will see in the top left corner is your ID, it is kind of like the phone number for a fax machine, it is the number people will send faxes to. You will also see a brief description about the PiFax system and an input that lets you input a filename. This input is asking what file you would like to send. It is very important that you include the full path of the file that is being sent. Once you type in the file to send, you will see an option to tell the system what ID to send it to. Simply, just type in the ID number of the client to send to and it will send the file to that client. SIDE NOTE: You must include the dashes as part of the ID, they are in this format XXX-XXXX-XXX.

<br>

If you want to listen for faxes you should run the fax_checker, like the client this has also been moved to `/pifax-python/`, so you will need to run:
```terminal
python /pifax-python/fax_checker.py
```
Or if you said Y to making a fax_checker systemd file:
```terminal
sudo systemctl start pifax.service
```
