
import pygame
from psychopy import visual, core, gui, data, event
import time
import re # https://regexr.com/
import coordinator
import aurora_sequence_creator
import Motor
from expt_helpers import *

#######################################
# FLEXIBLE PARAMETERS
# time for aurora to apply force
WAIT_TIME_BETWEEN_MOTOR_MOVEMENTS_MS = 3600
# there will be created a few points within each square (A and B)
HOW_MANY_POINTS_IN_EACH_SQUARE = 5
# distances in mm
DISTANCE_FROM_MIDLINE = 3
VERTICAL_DISTANCE_BETWEEN_POINTS = 1
# path where aurora protocols are located
# to generate dsf sequence files that point to protocols
AURORA_PROTOCOLS_PATH = 'C:\\Emma protocols\\Protocols'
############################################


# -- CREATE MOTOR OBJECT --
my_motor = Motor.Motor()
my_motor.calibrate_axis(my_motor.my_xaxis_id)
my_motor.calibrate_axis(my_motor.my_yaxis_id)

# --

# -- CREATE OBJECT THAT HANDLES POSITIONS --
coord = coordinator.Coordinator(total=HOW_MANY_POINTS_IN_EACH_SQUARE,
                                horizontal=DISTANCE_FROM_MIDLINE,vertical=VERTICAL_DISTANCE_BETWEEN_POINTS)
# --

# -- MOVE MOTOR TO THE START POSITION (MIDDLE OF MIDLINE BETWEEN SQUARES) --
# disable trigger
my_motor.disable_ttl(my_motor.my_xaxis_id)
my_motor.disable_ttl(my_motor.my_yaxis_id)
# initial x and y position in mm
previous_motor_pos = (0,0)
# start position between squares
start_pos = coord.mid_point
[x_distance, y_distance] = get_motor_distances(previous_motor_pos,start_pos)
print("move x",x_distance)
print("move y",y_distance)
my_motor.move(my_motor.my_yaxis_id,y_distance)
my_motor.move(my_motor.my_xaxis_id,x_distance)
previous_motor_pos = start_pos

# --

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
    '00. Experiment Name': 'film-shaved-aurora',
    '01. Participant Code': '06',
    '02. Standard stimulus': '600.0',
    '03. Comparison stimuli': '250.0,400.0,600.0,800.0,900.0,1000.0, 1200.0',
    '04. Standard Area (A 1st, B 2nd)': 'A', #  (A 1st, B 2nd)
    '05. Comparison Area (A 1st, B 2nd)': 'B', #  (A 1st, B 2nd) # add line "Intervention Area:"
    '06. Intervention Area':'B',
    '07. Intervention (film/shaved)':'',
    '08. Number of repeats (even)': 7,
    '09. Folder for saving data': 'data',
    '10. Participant screen': 0,
    '11. Participant screen resolution': '600,400',
    '12. Path to Aurora Protocols': 'C:\\EXPERIMENTS\\Indentation_Discrimination\\Emma protocols\\Protocols'
}
dlg = gui.DlgFromDict(exptSettings, title='Experiment details')
if dlg.OK:
    pass  # continue
else:
    my_motor.close()
    core.quit()  # the user hit cancel so exit

# check standard and comparison areas are correct
standard_area = exptSettings['04. Standard Area (A 1st, B 2nd)']
comparison_area = exptSettings['05. Comparison Area (A 1st, B 2nd)']
if not (standard_area == 'A' and comparison_area == 'B') or (standard_area == 'B' and comparison_area == 'A'):
    print("Standard and comparison areas have to be called A or B")
    my_motor.close()
    core.quit()

# get screen resolution
participantScreenRes = [int(i) for i in exptSettings['11. Participant screen resolution'].split(',')]

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
            stimList.append({'standard_force': std,
                             'comparison_force': cmp,
                             'presentation order': pres})

# divide repeats by 2 because it gets doubled by presentation order
nRepeats = exptSettings['08. Number of repeats (even)'] / 2
init_trials = data.TrialHandler(stimList, nRepeats)

# add area coordinates to that
trials = coord.add_coordinates2forces(init_trials,standard_area,comparison_area)

# --

#file prefix to match aurora data files with python data files
expt_file_prefix = (
        exptSettings['00. Experiment Name'] +
        '_' + data.getDateStr(format='%Y-%m-%d_%H-%M-%S') +
        '_P' + exptSettings['01. Participant Code'] +
        '_' + exptSettings['07. Intervention (film/shaved)']
)

data_folder = exptSettings['09. Folder for saving data'] + '/' + exptSettings['01. Participant Code'] + '/'

# EXPORT OF AURORA SEQUENCE FILES
# create sequencer object that formats sequence file and paths
aurora_sequencer = aurora_sequence_creator.SequenceCreator(exptSettings['12. Path to Aurora Protocols'],
                                                            data_folder,
                                                            expt_file_prefix,
                                                            trials)
# create current sequence
my_force_seq = aurora_sequencer.create_aurora_force_sequence()
# save that sequence as a dsf file for aurora
aurora_sequencer.create_sequence_file(my_force_seq)

# ----


# -- MAKE FOLDER/FILES TO SAVE DATA --
outputFiles = DataFileCollection(
    foldername='./' + data_folder,
    filename=expt_file_prefix,
    headers=['trial-number', 'standard', 'comparison', 'comparison.more.intense', 'presentation.order', 'response'],
    dlgInput=exptSettings
)

# ----

# -- SETUP VISUAL PROMPTS / DISPLAY --

participantWin = visual.Window(
    fullscr=False,
    allowGUI=False,
    screen=exptSettings['10. Participant screen'],
    size=participantScreenRes,
    units='norm'
)
participantMouse = event.Mouse(win=participantWin)
participantMessage = visual.TextStim(participantWin, text=displayText['waitMessage'], units='norm')

# --

# -- SETUP AUDIO CUES --

pygame.mixer.pre_init()
pygame.mixer.init()
firstCue = pygame.mixer.Sound('./sounds/first.wav')
secondCue = pygame.mixer.Sound('./sounds/second.wav')

# --

# -- RUN THE EXPERIMENT --
exptClock = core.Clock()
exptClock.reset()

# wait for start trigger
print('Experimenter: '+displayText['startMessage']+' Press ESC to quit.')
participantMessage.text = displayText['waitMessage']
event.clearEvents()
participantMessage.autoDraw = True
participantWin.flip()
for (key, keyTime) in event.waitKeys(keyList=['space', 'escape'], timeStamped=exptClock):
    if key in ['escape']:
        outputFiles.logAbort(keyTime)
        my_motor.close()
        core.quit()
    if key in ['space']:
        exptClock.add(keyTime)
        outputFiles.logEvent(0, 'experiment started')

# experiment loop
trialNo = 0
nIndentationsExpected = 0
nIndentationsDelivered = 0
file_pattern = expt_file_prefix+'.*\.ddf'
for thisTrial in trials:
    trialNo += 1
    # get the stimulus for this trial
    if thisTrial['presentation order'] == 'standard first' : po = 0
    if thisTrial['presentation order'] == 'standard second' : po = 1
    stimStdComp = ['standard', 'comparison']
    stimPairPosition = [thisTrial['standard_position'], thisTrial['comparison_position']]
    stimPairForces = [thisTrial['standard_force'], thisTrial['comparison_force']]
    stimPairArea = [exptSettings['04. Standard Area (A 1st, B 2nd)'],exptSettings['05. Comparison Area (A 1st, B 2nd)']]
    # outputFiles.logEvent(exptClock.getTime(), '{} then {}'.format(stimPair[po], stimPair[1 - po]))
    outputFiles.logEvent(
        exptClock.getTime(),
        'Trial {}: First {} {}mN, area {}, position {}. Second {} {}mN, area {}, position {}'.format(
            trialNo,
            stimStdComp[po],
            stimPairForces[po],
            stimPairArea[po],
            stimPairPosition[po],
            stimStdComp[1-po],
            stimPairForces[1-po],
            stimPairArea[1-po],
            stimPairPosition[1-po]
        ))

    # update participant display
    participantMessage.text = displayText['interStimMessage']
    event.clearEvents()
    participantMouse.clickReset()
    participantWin.flip()
##########################################################################################################
    # present the stimuli
    # calculate x and y distance in mm for the next motor move
    outputFiles.logEvent(exptClock.getTime(), "Current pos: {}" .format(previous_motor_pos))
    [x_distance, y_distance] = get_motor_distances(previous_motor_pos, stimPairPosition[po])
    outputFiles.logEvent(exptClock.getTime(), "move x {}" .format(x_distance))
    outputFiles.logEvent(exptClock.getTime(), "move y {}" .format(y_distance))
    # select which axis to enable ttl on stop (the one with longer distance)
    
    my_motor.move_xy_ttl(x_distance, y_distance)
    previous_motor_pos = stimPairPosition[po]
    motorStartTime = exptClock.getTime()
    outputFiles.logEvent(exptClock.getTime(), 'motor started moving')
    while exptClock.getTime() < motorStartTime + (WAIT_TIME_BETWEEN_MOTOR_MOVEMENTS_MS/1000):
        for (key, keyTime) in event.getKeys(['escape'], timeStamped=exptClock):
            my_motor.close()
            outputFiles.logAbort(keyTime)
            core.quit()
    outputFiles.logEvent(exptClock.getTime(), 'finished waiting {} ms for motor' .format(WAIT_TIME_BETWEEN_MOTOR_MOVEMENTS_MS))
    # start first sound
    soundCh = firstCue.play()
    outputFiles.logEvent(exptClock.getTime(), 'first stim audio cue started playing')
    while soundCh.get_busy():
        for (key, keyTime) in event.getKeys(['escape'], timeStamped=exptClock):
            soundCh.stop()
            my_motor.close()
            outputFiles.logAbort(keyTime)
            core.quit()
    outputFiles.logEvent(exptClock.getTime(), 'first audio cue finished playing')
    # end sound
    nIndentationsExpected += 1
    file_pattern_firstIndentation = '--'+expt_file_prefix+'_{}_{}\d*_\d*\.ddf' .format(stimPairForces[po], nIndentationsExpected)
    
    # calculate x and y distance in mm for the next motor move
    outputFiles.logEvent(exptClock.getTime(), "Current pos {}" .format(previous_motor_pos))
    [x_distance, y_distance] = get_motor_distances(previous_motor_pos, stimPairPosition[1-po])
    outputFiles.logEvent(exptClock.getTime(), "move x {}" .format(x_distance))
    outputFiles.logEvent(exptClock.getTime(), "move y {}" .format(y_distance))
    # select which axis to enable ttl on stop (the one with longer distance)
    my_motor.move_xy_ttl(x_distance, y_distance)
    previous_motor_pos = stimPairPosition[1 - po]
    motorStartTime = exptClock.getTime()
    while exptClock.getTime() < motorStartTime + (WAIT_TIME_BETWEEN_MOTOR_MOVEMENTS_MS/1000):
        for (key, keyTime) in event.getKeys(['escape'], timeStamped=exptClock):
            my_motor.close()
            outputFiles.logAbort(keyTime)
            core.quit()
    outputFiles.logEvent(exptClock.getTime(), 'finished waiting {} ms for motor' .format(WAIT_TIME_BETWEEN_MOTOR_MOVEMENTS_MS))
    # play
    soundCh = secondCue.play()
    outputFiles.logEvent(exptClock.getTime(), 'second stim audio cue started playing')
    while soundCh.get_busy():
        for (key, keyTime) in event.getKeys(['escape'], timeStamped=exptClock):
            soundCh.stop()
            my_motor.close()
            outputFiles.logAbort(keyTime)
            core.quit()
    outputFiles.logEvent(exptClock.getTime(), 'second audio cue finished playing')
    # end of sound
    nIndentationsExpected += 1
    file_pattern_secondIndentation = '--'+expt_file_prefix+'_{}_{}\d*_\d*\.ddf' .format(stimPairForces[1-po], nIndentationsExpected)

##########################################################################################################
    # present question to participant
    participantResponded = False
    outputFiles.logEvent(exptClock.getTime(), 'Experimenter, '+displayText['waitMessage'])  # for experimenter
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
                my_motor.close()
                outputFiles.logAbort(keyTime)
                core.quit()

    # check response
    response = mouseResponse[2] + 1
    outputFiles.logEvent(responseTime, 'participant responded: {}'.format(response))
    comparisonMoreIntense = int(mouseResponse[0] == po)

    outputFiles.writeTrialData([
        trialNo, #trials.thisN + 1, /trialNo
        thisTrial['standard_force'],
        thisTrial['comparison_force'],
        comparisonMoreIntense,
        thisTrial['presentation order'],
        response
    ])
    
    # check if the stimulus really was delivered
    firstIndentationFile = [file for file in os.listdir(data_folder) if re.search(file_pattern_firstIndentation, file)]
    outputFiles.logEvent(exptClock.getTime(), "First indentation file detected: {}" .format(firstIndentationFile))

    secondIndentationFile = [file for file in os.listdir(data_folder) if re.search(file_pattern_secondIndentation, file)]
    outputFiles.logEvent(exptClock.getTime(), "Second indentation file detected: {}" .format(secondIndentationFile))

    nIndentationsDelivered = len([file for file in os.listdir(data_folder) if re.search(file_pattern, file)])
    outputFiles.logEvent(exptClock.getTime(), "# indentations expected = {}. # delivered = {}.".format(nIndentationsExpected,nIndentationsDelivered))

    outputFiles.logEvent(exptClock.getTime(), '{} of {} complete'.format(trialNo, len(trials)))

# ----

# -- END OF EXPERIMENT --

my_motor.close()
outputFiles.logEvent(exptClock.getTime(), 'experiment finished')
participantMessage.text = displayText['finishedMessage']
event.clearEvents()
participantMouse.clickReset()
participantWin.flip()
core.wait(2)
participantWin.close()
core.quit()

# ----