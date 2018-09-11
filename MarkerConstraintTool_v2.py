#========================================================================================#
# Script : makeMarker.py
# Author : Mandl Cho
#
# Updated : 24th July 2018 
#
# Usage : Drag and drop script into scene and execute. 
#
# Description :                                                                                                                                                                                                                                                                                                                                
# This tool is to automatically create a random-colored marker within the scene
# and constraint two selected objects, first selected object being the child, and the  
# latter being the source. 
#
#========================================================================================#
import sys
import os

import pyfbsdk as fb
import pyfbsdk_additions as fba
from pyfbsdk import FBMessageBox

import re
import random as rand
from functools import partial
from time import gmtime, strftime

from PySide import QtCore, QtGui, QtUiTools
from PySide.QtCore import Signal

mobuApp = fb.FBApplication()
mobuSys = fb.FBSystem()
mobuGrp = fb.FBSystem().Scene.Groups
mobuMat = fb.FBSystem().Scene.Materials
colorMat = []


def clearSelection():
    for i in fb.FBSystem().Scene.Components:
        i.Selected = False

def clearMaterialSelection():
    for i in fb.FBSystem().Scene.Materials:
        i.Selected = False

class CustomListitem(QtGui.QListWidgetItem):
    def __init__(self, parent, model):
        QtGui.QListWidgetItem.__init__(self, parent)
        self.model = model

class Main(QtGui.QWidget):
    def __init__(self,parent):

        QtGui.QWidget.__init__(self,parent)
        loader = QtUiTools.QUiLoader()
        self.ui = loader.load(r'D:\Dropbox (Personal)\Python\01_MotionBuilder\b_MarkerConstraintTool\ui\markerConstraintTool.ui', self)
        self.ui.show()

        self.ui.charLst.clear()
        p = re.compile('.+:Mesh')
        self.lGroupList = fb.FBSystem().Scene.Groups 
        for i in self.lGroupList:
            matched = p.match(i.LongName)
            if matched:
                # sorting RTAs by Mesh layer in Groups (this is for Ubisoft pipeline)
                # this entierly depends on existing pipeline, if the pipeine is sorted by namespace, then use namespace.
                item = CustomListitem(i.LongName, i)
                self.ui.charLst.addItem(item)


        # Marker Constraint Tool Tab =================================================#
        self.ui.btnCreateMarker.clicked.connect( self.btnCallBackCreateMarker)
        self.ui.btnCreateConstraint.clicked.connect( self.btnCallBackCreateConstraint )
        self.ui.btnResetScene.clicked.connect( self.btnCallBackResetScene )

        # Set Tool Hint ==============================================================#
        self.ui.btnCreateMarker.setToolTip("Creates a random-colored marker based on selection.")
        self.ui.btnCreateConstraint.setToolTip("Creates a Parent-Child Constraint, Please Select Child First")
        self.ui.btnResetScene.setToolTip("Resets Scene !! Use with Care")

        # Story Tool Tab =============================================================#
        # Characters Buttons
        
        self.ui.btnSendSelChar.clicked.connect( self.btnCallBackSendSelToStory )
        self.ui.btnSendAllChar.clicked.connect( self.btnCallBackSendAllToStory )

        # Set Tool Hint ==============================================================#
        # Character Buttons's Tooltips
        self.ui.btnSendSelChar.setToolTip("Sends Selected Character to Story Track with Current Take")
        self.ui.btnSendAllChar.setToolTip("Sends All Characterss to Story Track with Current Take and Move Clip to Start from 0")
        self.ui.chkboxCharPlotOrNot.setToolTip("If enabled, plots take to ControlRig and Skeleton")

        # Color Tool Tab =============================================================# 
        ''' the below is to populate list of characters within the scene. 
        '''
        self.ui.charLst.itemClicked.connect(self.onItemClicked)
        self.ui.btnApplyCol.clicked.connect(self.btnCallBackApplySelectedColor)
       
        # creating all the materials we need # 
        material = fb.FBMaterial('Mat_Gray')
        material.Diffuse = fb.FBColor(0.8, 0.8, 0.8)

        material = fb.FBMaterial('Mat_Red')
        material.Diffuse = fb.FBColor(0.59, 0.03, 0.01)

        material = fb.FBMaterial('Mat_Green')
        material.Diffuse = fb.FBColor(0.50, 0.60, 0)

        material = fb.FBMaterial('Mat_Blue')
        material.Diffuse = fb.FBColor(0.31, 0.59, 1.00)

        for i in mobuMat:
            if i.Name == "Mat_Gray":
                colorMat.append(i)
            if i.Name == "Mat_Red":
                colorMat.append(i)
            if i.Name == "Mat_Green":
                colorMat.append(i)
            if i.Name == "Mat_Blue":
                colorMat.append(i)
        
        print len(colorMat)

        for i in colorMat:
            print i.Name

    def btnCallBackApplySelectedColor(self):
        material = None
        if self.ui.cboxGray.isChecked() == True:
            material = colorMat[0]
            clearMaterialSelection()
            material.Selected = True

        elif self.ui.cboxRed.isChecked() == True:
            material = colorMat[1]
            clearMaterialSelection()
            material.Selected = True

        elif self.ui.cboxGreen.isChecked() == True:
            material = colorMat[2]
            clearMaterialSelection()
            material.Selected = True

        elif self.ui.cboxBlue.isChecked() == True:
            material = colorMat[3]
            clearMaterialSelection()
            material.Selected = True

        if material != None:
            # means some check box is checked
            lstCount = self.ui.charLst.count()
            for i in range(lstCount): 
                item = self.ui.charLst.item(i)
                if item.isSelected():
                    for j in item.model.Items:
                        for jItem in j.Children:
                            material.Parent = jItem
                            jItem.Materials.removeAll()
                            jItem.Materials.append(material)
                            jItem.Geometry.SetMaterialIndexArray([len(jItem.Materials)])
    
    def onItemClicked(self):
        clearSelection()
        lstCount = self.ui.charLst.count()
        for i in range(lstCount): 
            item = self.ui.charLst.item(i)
            if item.isSelected():
                item.model.Select(True)


    # Button CallBacks ALWAYS PUT IN MAIN ================================================#

    def btnCallBackCreateMarker(self):
        if self.ui.cmboxMarkerLook.currentText() == "Hard Cross":
            makeMarker("MDTools::Mrkr:Marker1", 1, 500)
        if self.ui.cmboxMarkerLook.currentText() =="Light Cross":
            makeMarker("MDTools::Mrkr:Marker1", 2, 500)
        if self.ui.cmboxMarkerLook.currentText() == "Cube":
            makeMarker("MDTools::Mrkr:Marker1", 0, 500)
        if self.ui.cmboxMarkerLook.currentText() == "Circle":
            makeMarker("MDTools::Mrkr:Marker1", 7, 500)

    def btnCallBackCreateConstraint(self):
        if self.ui.btnSnapCheckBox.isChecked() == True: 
            createConstraintBySelection(True, 5, True, True)
        else:
            createConstraintBySelection(True, 5, False, True)

    def btnCallBackResetScene(self):
        resetScene()

    def btnCallBackSendSelToStory(self):
        if self.ui.chkboxCharPlotOrNot.isChecked() == True:
            plotSelectedDecision("skeleton")
            plotSelectedDecision("ctrlRig")
            SendSelectedToStory()
        if self.ui.chkboxSaveAnim.isChecked() == True:
            plotSelectedDecision("skeleton")
            plotSelectedDecision("ctrlRig")
            saveAnimation()
        else:
            SendSelectedToStory()

    def btnCallBackSendAllToStory(self):
        SendAllCharactersToStory()

    def make_connection(self, CustomColorCheckBox):
        CustomColorCheckBox.selectedColor.connect(self.btnApplyCol)


    
    # =====================================================================================#


# ALL CONSTRAINT TOOL FUNCTIONS [FUNCTIONS] ===============================================#

def createConstraintBySelection(pActive, pType, pSnap, pLock):
    '''
    To allow users to query what is their existing selection
    and base the constraint nature as Maya's Child-first, Parent-later. 

    pActive : True = Constraint On, False = Not On
    pType : Constraint Type
    pLock : True = Locked, False = Not Locked
    '''
    lModels = fb.FBModelList()
    fb.FBGetSelectedModels(lModels, None, True, True)
    for s in lModels:
        print s.Name
    # Here we are doing a check if there are 2 objects in selection, or if != 2, then throw an error window
    lSelectedObj = [fb.FBFindObjectByFullName(model.FullName) for model in lModels]
    # If two objects are selected, create the constraint
    if len(lSelectedObj) == 2:
            Con = fb.FBConstraintManager().TypeCreateConstraint(pType)
            Con.Name = "Child-"+str([lModels[0].Name])+"_to_Parent-"+str([lModels[1].Name])+"-mToolbox"
            Con.ReferenceAdd(0, lModels[0])
            Con.ReferenceAdd(1, lModels[1])
            if pSnap == True:
                Con.Snap()
            Con.Active = pActive
            Con.Lock = pLock
    # If selection is not 2, error message. 
    elif len(lSelectedObj) != 2:
        fb.FBMessageBox("Error", "Can't create constraint, Please select only two objects","OK")

def makeMarkerGrp(pName):
    mkGrp = fb.FBGroup(pName)
    mkGrp.Show = True
    mkGrp.Pickable = True
    mkGrp.Transformable = True

def makeMarker(pName, pLook, pSize):
    '''
    pName: name given to marker during marker creation
    pLook: defines the look of marker
    pSize: size given to marker during marker creation
    '''
    # Randomly generate R, G, B float values for our random color
    global mkGrp

    cR = rand.random() 
    cG = rand.random()
    cB = rand.random()

    # Creating our marker and assigning it to a variable 
    oMarker = fb.FBModelMarker(pName)

    # Modify marker property (MarkerScale)
    oMarker.Size = pSize

    # Modify marker property (LookUI) 
    oMarker.PropertyList.Find('LookUi').Data = pLook

    # Modify marker property (FBColor) 
    oMarker.Color = fb.FBColor(cR, cG, cB)

    # Set the Marker to Show
    oMarker.Show = True

    print oMarker.Name
    print cR , cG , cB 
    print 'Marker Created!'

def ObjCountCheck():
    lSelectedModels = fb.FBModelList()
    fb.FBGetSelectedModels(lSelectedModels, None, True, True)
    lSelectedObj = [fb.FBFindObjectByFullName(model.FullName) for model in lSelectedModels]
    if len(lSelectedObj) == 2:
        createConstraintBySelection()
    elif len(lSelectedObj) != 2:
        # Error: just a OK button.
        fb.FBMessageBox( "Error: Wrong Number of Objects Selected", "Please select two objects", "OK" )
        return

def resetScene():
    mobuApp.FileNew()

# ========================================================================================#

# ALL STORY TOOL FUNCTIONS [STORY] =======================================================#

def plotSelectedDecision(pPlotWhere):
    # Defining our Characater as the currnetly selected one
    lCharacter = fb.FBApplication().CurrentCharacter
    # Defining the Plot option that will be used        
    PlotCtrlRigTakeOptions = fb.FBPlotOptions()
    # To use Constant Key Reduction on the plot (True or False) 
    PlotCtrlRigTakeOptions.ConstantKeyReducerKeepOneKey = False
    # To go through all takes in the scene and plot the data (True or False) 
    PlotCtrlRigTakeOptions.PlotAllTakes = False
    # Do you wish to plot onto frames (True or False) 
    PlotCtrlRigTakeOptions.PlotOnFrame = True
    # Set the plot period 
    PlotCtrlRigTakeOptions.PlotPeriod = fb.FBTime( 0, 0, 0, 1 )
    PlotCtrlRigTakeOptions.PlotTranslationOnRootOnly = False
    PlotCtrlRigTakeOptions.PreciseTimeDiscontinuities = False
    # What filter to use on the plot (Unroll, GimabalKill or None)
    PlotCtrlRigTakeOptions.RotationFilterToApply = fb.FBRotationFilter.kFBRotationFilterUnroll
    # Use Constant Kye Reduction (True or False)
    PlotCtrlRigTakeOptions.UseConstantKeyReducer = False
    if pPlotWhere == "skeleton":
        lCharacter.PlotAnimation (fb.FBCharacterPlotWhere.kFBCharacterPlotOnControlRig,PlotCtrlRigTakeOptions )
    elif pPlotWhere == "ctrlrig":
        lCharacter.PlotAnimation (fb.FBCharacterPlotWhere.kFBCharacterPlotOnSkeleton,PlotCtrlRigTakeOptions )

def SendSelectedToStory():
    lfoldername = fb.FBSystem().CurrentTake.Name
    lFolder = fb.FBStoryFolder()
    lFolder.Label = lfoldername
    ## Character Track
    lCharTrack = fb.FBStoryTrack(fb.FBStoryTrackType.kFBStoryTrackCharacter, lFolder)
    # Assign our CurrentCharacter to the track
    lCharTrack.Details.append(fb.FBApplication().CurrentCharacter)
    # Set Character Track name to Current Character Name
    lCharTrack.Label = fb.FBApplication().CurrentCharacter.LongName
    # Insert current take in the newly created track
    lCharTrack.CopyTakeIntoTrack(fb.FBSystem().CurrentTake.LocalTimeSpan, fb.FBSystem().CurrentTake)

def SendAllCharactersToStory():
    charIndex = 1
    lClipList = []
    lMyStartTime = 0
    # Find all characters in the scene. Add them to story track
    for lChar in fb.FBSystem().Scene.Characters:
        # Create Track for one character
        lTrack = fb.FBStoryTrack(fb.FBStoryTrackType.kFBStoryTrackCharacter)
        # Specify the index of the character which is one
        lTrack.CharacterIndex = charIndex
        # Creating the track names based on character names and adding a 'Track' behind. 
        lTrack.LongName = lChar.LongName +" Track"
        #lTrack.Ghost = self.ui.RBEnableGhost.isChecked()
        # Insert current take
        lClip = lTrack.CopyTakeIntoTrack(fb.FBSystem().CurrentTake.LocalTimeSpan, fb.FBSystem().CurrentTake)
        # Shift clip to start time at 0 
        lClip.Start = fb.FBTime(0,0,0,lMyStartTime)
        # adding one to the index so that it will repeat for the next character in the scene. 
        charIndex = charIndex + 1
        # insert current take. 
        lClipList.append(lClip)

def saveAnimation():
    lSaveCharCurrent = mobuApp.CurrentCharacter
    lSaveCharCurrentName = lSaveCharCurrent.LongName
    lSaveCurrentTakeName = mobuSys.CurrentTake.Name
    lSaveFBXFileName = mobuApp.FBXFileName

    # Indicating the directory that you want the clips to be saved at. 
    lSaveDirRoot = r"C:\AnimationClipExports"

    # Variables for the subfolder and the scene name
    lSaveDirSub = os.path.splitext(os.path.basename(lSaveFBXFileName))[0]
    lSaveSceneName = os.path.splitext(os.path.basename(lSaveFBXFileName))[0]

    # variables for paths
    lSavePath = lSaveDirRoot + "\\" + lSaveDirSub + "\\"

    # variable for file name
    lSaveFileName = lSaveSceneName + " - " + lSaveCharCurrentName

    # variable for the full path "Root\Subfoilder\Filename"
    lSaveCharAnim = lSavePath + lSaveFileName

    # Directory setup to save in, also, doing a check to see if its there, if not, make it
    if not os.path.exists(lSavePath):
        os.makedirs(lSavePath)
    # Save animation options
    lSaveOptions = fb.FBFbxOptions (False) # False = will not save options
    lSaveOptions.SaveCharacter = True
    lSaveOptions.SaveControlSet = True
    lSaveOptions.SaveCharacterExtension = True
    lSaveOptions.ShowFileDialog = False
    lSaveOptions.ShowOptionslDialog = False
    # saving out the animation
    mobuApp.SaveCharacterRigAndAnimation(lSaveCharAnim, lSaveCharCurrent, lSaveOptions)


# ========================================================================================#

# ========================================================================================#

#App = QtGui.QApplication(sys.argv)
parent = QtGui.QApplication.activeWindow()  # it will Parent to Motionbuilder window
myUI = Main(parent)


#=========================================================================================================
