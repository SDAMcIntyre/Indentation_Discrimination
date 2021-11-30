from psychopy import visual, core, gui, data, event
from expt_helpers import *

# -- DISPLAY TEXT --

displayText = {'waitMessage': 'Please wait.',
               'interStimMessage': '...',
               'finishedMessage': 'Session finished.',
               'stimQuestion': 'Which was most intense, 1st or 2nd?',
               'startMessage': 'Press space to start.',
               'stimMessage': 'Next stimulus:',
               'continueMessage': 'Press space for the touch cue.',
               'touchMessage': 'Follow the audio cue.'}
# --

# -- GET INPUT FROM THE EXPERIMENTER --

exptSettings = {
    '00. Experiment Name': '',
    '01. Participant Code': 'test',
    '02. Standard stimulus': '2',
    '03. Comparison stimuli': '0.60,1.4,1.0,2.0,4.0,6.0,8.0',
    '04. Number of repeats (even)': 10,
    '05. Folder for saving data': 'data',
    '06. Participant screen': 0,
    '07. Participant screen resolution': '600,400'
}
dlg = gui.DlgFromDict(exptSettings, title='Experiment details')
if dlg.OK:
    pass  # continue
else:
    core.quit()  # the user hit cancel so exit

# get screen resolution
participantScreenRes = [int(i) for i in exptSettings['07. Participant screen resolution'].split(',')]

# get stimulus values
standard = [float(i) for i in exptSettings['02. Standard stimulus'].split(',')]
comparison = [float(i) for i in exptSettings['03. Comparison stimuli'].split(',')]

# --


# -- SETUP STIMULUS RANDOMISATION AND CONTROL --
presentationOrder = ['standard first', 'standard second']
stimList = []
for std in standard:
    for cmp in comparison:
        for pres in presentationOrder:
            stimList.append({'standard': std,
                             'comparison': cmp,
                             'presentation order': pres})

# divide repeats by 2 because it gets doubled by presentation order
nRepeats = exptSettings['04. Number of repeats (even)'] / 2
trials = data.TrialHandler(stimList, nRepeats)

## SARAH ADD EXPORT OF AURORA PROTOCOL & SEQUENCE FILES

# ----


# -- MAKE FOLDER/FILES TO SAVE DATA --
outputFiles = DataFileCollection(
    foldername='./' + exptSettings['05. Folder for saving data'] + '/',
    filename=exptSettings['Experiment name'] + '_' + data.getDateStr(format='%Y-%m-%d_%H-%M-%S') + '_P' + exptSettings[
        'Participant Code'],
    headers=['trial-number', 'standard', 'comparison', 'comparison.more.intense', 'presentation.order', 'response'],
    dlgInput=exptSettings
)

# ----

# -- SETUP VISUAL PROMPTS / DISPLAY --

participantWin = visual.Window(
    fullscr=False,
    allowGUI=False,
    screen=exptSettings['06. Participant screen'],
    size=participantScreenRes,
    units='norm'
)
participantMouse = event.Mouse(win=participantWin)
participantMessage = visual.TextStim(participantWin, text=displayText['waitMessage'], units='norm')

# --


# -- RUN THE EXPERIMENT --
exptClock = core.Clock()
exptClock.reset()

# wait for start trigger
print(displayText['startMessage'])
participantMessage.text = displayText['waitMessage']
event.clearEvents()
participantMessage.autoDraw = True
participantWin.flip()
for (key, keyTime) in event.waitKeys(keyList=['space', 'escape'], timeStamped=exptClock):
    if key in ['escape']:
        outputFiles.logAbort(keyTime)
        core.quit()
    if key in ['space']:
        exptClock.add(keyTime)
        outputFiles.logEvent(0, 'experiment started')

# experiment loop
for thisTrial in trials:

    # get the stimulus for this trial
    if thisTrial['presentation order'] == 'standard first' : po = 0
    if thisTrial['presentation order'] == 'standard second' : po = 1
    stimPair = [thisTrial['standard'], thisTrial['comparison']]

    # update participant display
    participantMessage.text = displayText['interStimMessage']
    event.clearEvents()
    participantMouse.clickReset()
    participantWin.flip()

    # present the stimuli
    # ILONA INSERT CODE HERE
    # GET THE ORDER FOR THE SKIN REGION FROM "po" (LINES 120-121, 133)
    outputFiles.logEvent(exptClock.getTime(), '{} then {}'.format(stimPair[po], stimPair[1 - po]))

    # present question to participant
    participantResponded = False
    print(displayText['waitMessage'])  # for experimenter
    event.clearEvents()
    participantMessage.text = displayText['stimQuestion']
    while not participantResponded:
        participantWin.flip()
        mouseResponse = participantMouse.getPressed()
        if mouseResponse[0] or mouseResponse[2]:
            responseTime = exptClock.getTime()
            participantResponded = True
        for (key, keyTime) in event.getKeys(['escape'], timeStamped=exptClock):
            if key in ['escape']:
                outputFiles.logAbort(keyTime)
                core.quit()

    # check response
    response = mouseResponse[2] + 1
    outputFiles.logEvent(responseTime, 'participant responded: {}'.format(response))
    comparisonMoreIntense = int(mouseResponse[0] == po)

    outputFiles.writeTrialData([
        trials.thisN + 1,
        thisTrial['standard'],
        thisTrial['comparison'],
        comparisonMoreIntense,
        thisTrial['presentation order'],
        response
    ])

    outputFiles.logEvent(exptClock.getTime(), '{} of {} complete'.format(trials.thisN + 1, trials.nTotal))

# ----

# -- END OF EXPERIMENT --

outputFiles.logEvent(exptClock.getTime(), 'experiment finished')
print(displayText['finishedMessage'])
participantMessage.text = displayText['finishedMessage']
event.clearEvents()
participantMouse.clickReset()
participantWin.flip()
core.wait(2)
participantWin.close()
core.quit()

# ----
