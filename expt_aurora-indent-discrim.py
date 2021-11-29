from psychopy import visual, core, gui, data, event
import numpy, random, os, pygame
from math import *

def logEvent(time,event,logFile):
    logFile.write('{},{}\n' .format(time,event))
    print('LOG: {} {}' .format(time, event))


# -- DISPLAY TEXT --

displayText = {'waitMessage':'Please wait.',
                'interStimMessage':'...',
                'finishedMessage':'Session finished.',
                'painQuestion':'Which was most intense, 1st or 2nd?',
                'startMessage':'Press space to start.',
                'stimMessage':'Next stimulus:',
                'continueMessage':'Press space for the touch cue.',
                'touchMessage' : 'Follow the audio cue.'}
# --


# -- GET INPUT FROM THE EXPERIMENTER --

exptInfo = {'01. Participant Code':'test', 
            '02. Standard monofilaments':'2', 
            '03. Comparison monofilaments':'0.60,1.4,1.0,2.0,4.0,6.0,8.0',
            '04. Number of repeats (even)':10, 
            '05. Folder for saving data':'data',
            '06. Participant screen':1,
            '07. Participant screen resolution':'600,400',
            '08. Experimenter screen':0,
            '09. Experimenter screen resolution':'600,400'}


dlg = gui.DlgFromDict(exptInfo, title='Experiment details')
if dlg.OK:
    dateTime = data.getDateStr(format='%Y-%m-%d_%H-%M-%S')
else:
    core.quit() ## the user hit cancel so exit

## get screen resolution
participantScreenRes = [int(i) for i in exptInfo['07. Participant screen resolution'].split(',')]
experimenterScreenRes = [int(i) for i in exptInfo['09. Experimenter screen resolution'].split(',')]

## get stimulus values
standard = [float(i) for i in exptInfo['02. Standard monofilaments'].split(',')]
comparison = [float(i) for i in exptInfo['03. Comparison monofilaments'].split(',')]


# --


# -- SETUP STIMULUS RANDOMISATION AND CONTROL --
presentationOrder = ['standard first', 'standard second']
stimList = []
for std in standard:
    for cmp in comparison: 
        for ord in presentationOrder:
            stimList.append({'standard':std,
                            'comparison':cmp,
                            'presentation order':ord}) 
##divide repeats by 2 because it gets doubled by presentation order
nRepeats = exptInfo['04. Number of repeats (even)']/2
trials = data.TrialHandler(stimList, nRepeats)

# ----


# -- MAKE FOLDER/FILES TO SAVE DATA --

dataFolder = './'+exptInfo['05. Folder for saving data']+'/'
if not os.path.exists(dataFolder):
    os.makedirs(dataFolder)

fileName = dataFolder + 'PainDiscrimination_' + dateTime + '_' + exptInfo['01. Participant Code']

infoFile = open(fileName+'_info.csv', 'w') 
for k,v in exptInfo.iteritems(): 
    infoFile.write(k + ',' + str(v) + '\n')
infoFile.close()

logFile = open(fileName+'_log.csv', 'w')
logFile.write('time,event\n')

dataFile = open(fileName+'_data.csv', 'w')
dataFile.write('trial-number,standard,comparison,comparison.more.painful,presentation.order,response\n')

# ----


# -- SETUP EXPERIMENTER AUDIO CUE --

pygame.mixer.pre_init() 
pygame.mixer.init()
stimAudioCue = pygame.mixer.Sound('./sounds/1st-2nd.wav')
# ----


# -- SETUP VISUAL ANALOG SCALES AND VISUAL PROMPTS --

participantWin = visual.Window(fullscr = False, 
                            allowGUI = False, 
                            screen = exptInfo['06. Participant screen'],
                            size = participantScreenRes,
                            units='norm') 
participantMouse = event.Mouse(win = participantWin)
participantMessage = visual.TextStim(participantWin, text=displayText['waitMessage'], units='norm')
barMarker = visual.TextStim(participantWin, text='|', units='norm')

experimenterWin = visual.Window(fullscr = False,
                                allowGUI = False,
                                screen = exptInfo['08. Experimenter screen'],
                                size = experimenterScreenRes,
                                units = 'norm')
experimenterMessage = visual.TextStim(experimenterWin, text=displayText['startMessage'], units='norm')


# --


# -- RUN THE EXPERIMENT --
exptClock=core.Clock()
exptClock.reset()

# wait for start trigger
experimenterMessage.text = displayText['startMessage']
participantMessage.text = displayText['waitMessage']
event.clearEvents()
experimenterMessage.autoDraw = True
participantMessage.autoDraw = True
experimenterWin.flip()
participantWin.flip()
startTriggerReceived = False
while not startTriggerReceived:
    experimenterWin.flip()
    for (key,keyTime) in event.getKeys(['space','escape'], timeStamped=exptClock):
        if key in ['escape']:
            logEvent(keyTime,'experiment aborted',logFile)
            dataFile.close(); logFile.close(); core.quit()
        if key in ['space']:
            exptClock.add(keyTime)
            logEvent(0,'experiment started',logFile)
            startTriggerReceived = True

# experiment loop
for thisTrial in trials:
    
    ## get the stimulus for this trial
    if thisTrial['presentation order'] == 'standard first': po = 0
    if thisTrial['presentation order'] == 'standard second': po = 1
    stimPair = [thisTrial['standard'], thisTrial['comparison']]
    
    cueText = '{} g then {} g' .format(stimPair[po], stimPair[1-po])
    
    ## display stim message
    continuePressed = False
    experimenterMessage.text = '{}\n{}\n\n{}' .format(displayText['stimMessage'], cueText, displayText['continueMessage'])
    participantMessage.text = displayText['waitMessage']
    event.clearEvents()
    participantMouse.clickReset()
    logEvent(exptClock.getTime(), 'experimenter shown: {}' .format(cueText), logFile)
    participantWin.flip()
    while not continuePressed:
        experimenterWin.flip()
        for (key,keyTime) in event.getKeys(['space','escape'], timeStamped=exptClock):
            if key in ['escape']:
                logEvent(keyTime,'experiment aborted',logFile)
                dataFile.close(); logFile.close(); core.quit()
            if key in ['space']:
                logEvent(keyTime,'experimenter pressed for cue',logFile)
                continuePressed = True
    
    ## cue experimenter to perform touch
    experimenterMessage.text = '\n{}\n\n{}' .format(cueText, displayText['touchMessage'])
    participantMessage.text = displayText['interStimMessage']
    event.clearEvents()
    experimenterWin.flip()
    participantWin.flip()
    core.wait(1)
    audioStartTime = exptClock.getTime()
    soundCh = stimAudioCue.play()
    logEvent(audioStartTime,'audio cue started playing',logFile)
    while soundCh.get_busy():
        for (key,keyTime) in event.getKeys(['escape'], timeStamped=exptClock):
            soundCh.stop()
            logEvent(keyTime,'experiment aborted',logFile)
            dataFile.close(); logFile.close(); core.quit()
    logEvent(exptClock.getTime(),'audio cue finished playing',logFile)
    
    ## present question to participant
    participantResponded = False
    experimenterMessage.text = displayText['waitMessage']
    event.clearEvents()
    experimenterWin.flip()
    participantMessage.text = displayText['painQuestion']
    while not participantResponded:
        participantWin.flip()
        mouseResponse = participantMouse.getPressed()
        if mouseResponse[0] or mouseResponse[2]:
            responseTime = exptClock.getTime()
            participantResponded = True
        for (key,keyTime) in event.getKeys(['space','escape'], timeStamped=exptClock):
            if key in ['escape']:
                logEvent(keyTime,'experiment aborted',logFile)
                dataFile.close(); logFile.close(); core.quit()
            if key in ['space']:
                logEvent(keyTime,'experimenter pressed for cue',logFile)
                continuePressed = True
    
    ## check response
    response = mouseResponse[2] + 1
    logEvent(responseTime, 'participant responded: {}' .format(response), logFile)
    comparisonMorePainful = int(mouseResponse[0] == po)
    
    dataFile.write('{},{},{},{},{},{}\n' .format(trials.thisN+1, 
                                            thisTrial['standard'], 
                                            thisTrial['comparison'], 
                                            comparisonMorePainful,
                                            thisTrial['presentation order'], 
                                            response))
    logEvent(exptClock.getTime(),'{} of {} complete' .format(trials.thisN+1, trials.nTotal),logFile)
    
# ----

# -- END OF EXPERIMENT --

logEvent(exptClock.getTime(),'experiment finished',logFile)
experimenterMessage.text = displayText['finishedMessage']
participantMessage.text = displayText['finishedMessage']
event.clearEvents()
participantMouse.clickReset()
experimenterWin.flip()
participantWin.flip()
core.wait(2)
dataFile.close(); logFile.close()
experimenterWin.close()
participantWin.close()
core.quit()

# ----
