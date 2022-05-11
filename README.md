# Tangram pentagons generator
![intro](Readme%2026a8368e4ba041768a5bbd16cd8735f3/meme.jpg)
+ This is the group project of undergraduate course Artificial Intelligence 2022 @ Macau University of Science and Technology 
+ Copyright (c) 2022, Liu YanQing, Zhu Zengliang, Yi RuiYu. All rights reserved. 

This file will teach you how to install and use our program.

First we got two different version applications, one is for windows and the other is for mac. You can also choose to run from source code, which is compatible on both devices.

## Install:
Download the release package in the "release page" on the right.
### For Mac

To run the program, just click main.app

### For Windows

1. Unzip the AI_project.zip
2. Click exe file.

### Run from source code
1. install python environment on your computer. Please refer to this tutorial: https://www.runoob.com/python3/python3-install.html?msclkid=94cc2130d03f11ecbcffeca88e71caf4
2. clone our repo with "git clone https://github.com/bchuh/AI_project.git"
   + Or, download the codes as a zip file.
3. go to the codes' folder, make sure a "requirement.txt" is in the folder
4. open a terminal(cmd) in the folder
5. type "pip install -r requirement.txt" and press "enter"
6. after installing all the packages, type "python main.py" and press "enter"

## Usage:


![截屏2022-05-09 下午8.29.44.png](Readme%2026a8368e4ba041768a5bbd16cd8735f3/%E6%88%AA%E5%B1%8F2022-05-09_%E4%B8%8B%E5%8D%888.29.44.png)

![截屏2022-05-09 下午9.41.48.png](Readme%2026a8368e4ba041768a5bbd16cd8735f3/%E6%88%AA%E5%B1%8F2022-05-09_%E4%B8%8B%E5%8D%889.41.48.png)

![截屏2022-05-09 下午9.42.04.png](Readme%2026a8368e4ba041768a5bbd16cd8735f3/%E6%88%AA%E5%B1%8F2022-05-09_%E4%B8%8B%E5%8D%889.42.04.png)

![截屏2022-05-09 下午9.42.14.png](Readme%2026a8368e4ba041768a5bbd16cd8735f3/%E6%88%AA%E5%B1%8F2022-05-09_%E4%B8%8B%E5%8D%889.42.14.png)

![截屏2022-05-09 下午9.42.32.png](Readme%2026a8368e4ba041768a5bbd16cd8735f3/%E6%88%AA%E5%B1%8F2022-05-09_%E4%B8%8B%E5%8D%889.42.32.jpg)

# referential steps
+ make sure the menu is set as "NONE" mode
+ click "show", and you will see the records run by us before
+ click one image to check all possible ways to form its corresponding pentagon.
+ Once finished checking the record, click "cancel" to return to home page.
## Now you will learn about how the program runs.
+ Take DFS for example, First, choose the ‘DFS’ 
+ uncheck "run DFS with muliprocess"
+ Turn on the 'Run with graphics', 'Run by steps'
+ Then click ‘ok’ to start searching 
### The main view will show the searching results. click ‘slow’ to slow down search progress, and click ‘resume’ back to the normal speed.<br>
## Finish watching the cool animations? Now lets try run the whole search with multi-process, which should take around 1 hour
+ Click "Quit current AL", wait for "cancelled!" to appear in the message box.
+ choose the ‘DFS’
+ check "run DFS with muliprocess"
+ uncheck 'Run with graphics', 'Run by steps'
+ Then click ‘ok’ to start searching 
### When the application is searching, you can’t change the algorithm, the progress bar and remaining hours will let you know the time costs and search progress.<br>
+ Once the search is over, text edit will show how many combinations we have found and arrange nodes automatically. Then click ‘show’ to see those results.
## Tip:
If use DFS algorithm with multiple processes, then the ‘Run with Graphics’ and "run by step"  will be unusable during the search.  For all informed algorithm the ‘slow’ and ‘resume’ will be unusable. <br>




IF use mac version, you may need change your security setting.

![26331652113855_.pic.jpg](Readme%2026a8368e4ba041768a5bbd16cd8735f3/26331652113855_.pic.jpg)