# mandl’s constraint toolbox 

*lazy marker constraint : send to story : easy character color* 

------

### **setting up**

add script to asset browser in motionbuilder using **"add favourite path"** and browse to where this script is located

### **usage**

drag and drop script into the python editor to check if the path to UI is correct
drag the script from the asset browser into the viewport, and select **"add to scene and execute"**
you'll be presented with this window : 

**marker constraint tool**
**a** : creates a random colored marker based on selected look from the dropdown menu.
**b** : creates a parent-child constraint based on selection, child-object first, then parent-object, and then click create constraint. 
​	**offset** : enable this to maintain positions of the parent-object and child-object when activating constraint.
**c** : reset scene. you'd want to be careful with this one. 

**story tool** 
**a** : creates a story track, adds the selected character into the story track, inserts current take
**b** : creates a story track for all the characters in the scene, adds all the characters into the story track, inserts current take, shift all clips to frame 0 
​	**plot** : if enabled, plots existing take to skeleton and control rig before performing the above two functions
​	**export** : work in progress

**color tool** 
**a** : select the from the list of characters in the scene
**b** : choose a color
**c** : hit apply to change color 

------

### to-do

**optimisation** :
​	check for existing materials by name, if exists, create new ones
**features** : 
​	upon creation, animators would have the option to already have markers aligned to current selection
​	export option already works, but i want to allow users to specify where to save to

------

**credits**
daniel tjondropuro, michelle wong, xu xiao, francois dallaire and cyrus 























