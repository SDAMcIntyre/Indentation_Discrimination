from psychopy import visual, core, gui, data, event
import time
import sys
import coordinator
import aurora_sequence_creator
import Motor
from expt_helpers import *

# time for aurora to apply force
WAIT_TIME_BETWEEN_MOTOR_MOVEMENTS_MS = 2500
HOW_MANY_POINTS_IN_EACH_SQUARE = 3
# distances in mm
DISTANCE_FROM_MIDLINE = 3
VERTICAL_DISTANCE_BETWEEN_POINTS = 1
AURORA_PROTOCOLS_PATH = 'C:\\Users\\oumth89\\Desktop\\Protocols'

# -- CREATE MOTOR OBJECT --
my_motor = Motor.Motor()
my_motor.calibrate_axis(my_motor.my_xaxis_id)
my_motor.calibrate_axis(my_motor.my_yaxis_id)
# --

# -- CREATE OBJECT THAT HANDLES POSITIONS --
coord = coordinator.Coordinator(total=HOW_MANY_POINTS_IN_EACH_SQUARE,
                                horizontal=DISTANCE_FROM_MIDLINE,vertical=VERTICAL_DISTANCE_BETWEEN_POINTS)

########################################################
# DEBUG CREATING SEQUENCE FOR AURORA
# # create test sequence
# stimList = coord.create_left_right_random_sequences(6,'A','B')
# foldername ='.\\' + 'data' + '\\'
# aurora_sequencer = aurora_sequence_creator.SequenceCreator(AURORA_PROTOCOLS_PATH,
#                                                             foldername,
#                                                             "ForceSequence.dsf",
#                                                             [2],
#                                                             [0.60,1.4,1.0,2.0,4.0,6.0,8.0],
#                                                             stimList,
#                                                             'A',
#                                                             'B')
# my_force_seq = aurora_sequencer.create_aurora_force_sequence()
# aurora_sequencer.create_sequence_file(my_force_seq)
############################################################


# -- MOVE MOTOR TO THE START POSITION (MIDDLE OF MIDLINE BETWEEN SQUARES) --
# disable trigger
my_motor.disable_ttl(my_motor.my_xaxis_id)
my_motor.disable_ttl(my_motor.my_yaxis_id)
# initial x and y position in mm
previous_motor_pos = (0,0)
# start position between squares
start_pos = coord.mid_point
previous_x = previous_motor_pos[0]
previous_y = previous_motor_pos[1]
next_x = start_pos[0]
next_y = start_pos[1]
x_distance = next_x - previous_x
y_distance = next_y - previous_y
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
    '00. Experiment Name': '',
    '01. Participant Code': 'test',
    '02. Standard stimulus': '2',
    '03. Comparison stimuli': '0.60,1.4,1.0,2.0,4.0,6.0,8.0',
    '04. Standard Area': 'A',
    '05. Comparison Area': 'B',
    '06. Number of repeats (even)': 6,
    '07. Folder for saving data': 'data',
    '08. Participant screen': 0,
    '09. Participant screen resolution': '600,400',
    '10. Path to Aurora Protocols': 'C:\\Users\\oumth89\\Desktop\\Protocols'
}
dlg = gui.DlgFromDict(exptSettings, title='Experiment details')
if dlg.OK:
    pass  # continue
else:
    core.quit()  # the user hit cancel so exit

# get screen resolution
participantScreenRes = [int(i) for i in exptSettings['09. Participant screen resolution'].split(',')]

# get stimulus values
standard = [float(i) for i in exptSettings['02. Standard stimulus'].split(',')]
comparison = [float(i) for i in exptSettings['03. Comparison stimuli'].split(',')]
# --

# -- CREATE SEQUENCE OF COORDINATES --
standard_area = exptSettings['04. Standard Area']
comparison_area = exptSettings['05. Comparison Area']
if not (standard_area == 'A' and comparison_area == 'B') or (standard_area == 'B' and comparison_area == 'A'):
    print("Standard and comparison areas have to be called A or B")
    sys.exit()
# create total of random sequences, Standard area, Comparison area
stimList = coord.create_left_right_random_sequences(int(exptSettings['06. Number of repeats (even)']),standard_area,comparison_area)
# --


# ADD EXPORT OF AURORA PROTOCOL & SEQUENCE FILES
foldername ='.\\' + exptSettings['07. Folder for saving data'] + '\\'
sequence_file_name = exptSettings['00. Experiment Name'] + '_' + data.getDateStr(format='%Y-%m-%d_%H-%M-%S') + '_P' + exptSettings[
        '01. Participant Code']+'_'+'ForceSequence.dsf'
# create sequencer object that formats sequence file and paths
aurora_sequencer = aurora_sequence_creator.SequenceCreator('C:\\Users\\oumth89\\Desktop\\Protocols',
                                                            foldername,
                                                            sequence_file_name,
                                                            standard,
                                                            comparison,
                                                            stimList,
                                                            standard_area,
                                                            comparison_area)
# create current sequence
my_force_seq = aurora_sequencer.create_aurora_force_sequence()
# save that sequence as a dsf file for aurora
aurora_sequencer.create_sequence_file(my_force_seq)

# ----


# -- MAKE FOLDER/FILES TO SAVE DATA --
outputFiles = DataFileCollection(
    foldername='./' + exptSettings['07. Folder for saving data'] + '/',
    filename=exptSettings['00. Experiment Name'] + '_' + data.getDateStr(format='%Y-%m-%d_%H-%M-%S') + '_P' + exptSettings[
        '01. Participant Code'],
    headers=['trial-number', 'standard', 'comparison', 'comparison.more.intense', 'presentation.order', 'response'],
    dlgInput=exptSettings
)

# ----

# -- SETUP VISUAL PROMPTS / DISPLAY --

participantWin = visual.Window(
    fullscr=False,
    allowGUI=False,
    screen=exptSettings['08. Participant screen'],
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
trialNo = 0
# for thisTrial in trials:
for thisTrial in stimList:
    trialNo += 1
    # get the stimulus for this trial
    if thisTrial['presentation order'] == 'standard first' : po = 0
    if thisTrial['presentation order'] == 'standard second' : po = 1
    stimPair = [thisTrial['standard'], thisTrial['comparison']]

    # update participant display
    participantMessage.text = displayText['interStimMessage']
    event.clearEvents()
    participantMouse.clickReset()
    participantWin.flip()
##########################################################################################################
    # present the stimuli
    # ILONA INSERT CODE HERE
    # GET THE ORDER FOR THE SKIN REGION FROM "po" (LINES 120-121, 133)
    outputFiles.logEvent(exptClock.getTime(), '{} then {}'.format(stimPair[po], stimPair[1 - po]))
    # calculate x and y distance in mm for the next motor move
    print("Current pos:",previous_motor_pos)
    previous_x = previous_motor_pos[0]
    previous_y = previous_motor_pos[1]
    next_x = stimPair[po][0]
    next_y = stimPair[po][1]
    x_distance = next_x - previous_x
    y_distance = next_y - previous_y
    print("move x",x_distance)
    print("move y",y_distance)
    # select which axis to enable ttl on stop (the one with longer distance)
    if abs(x_distance) >= abs(y_distance):
        my_motor.disable_ttl(my_motor.my_yaxis_id)
        my_motor.enable_ttl(my_motor.my_xaxis_id)
        my_motor.move(my_motor.my_yaxis_id,y_distance)
        my_motor.move(my_motor.my_xaxis_id,x_distance)
    else:
        my_motor.disable_ttl(my_motor.my_xaxis_id)
        my_motor.enable_ttl(my_motor.my_yaxis_id)
        my_motor.move(my_motor.my_xaxis_id,x_distance)
        my_motor.move(my_motor.my_yaxis_id,y_distance)
    # my_motor.move(my_motor.my_xaxis_id,x_distance)
    # my_motor.move(my_motor.my_yaxis_id,y_distance)
    previous_motor_pos = stimPair[po]
    time.sleep(WAIT_TIME_BETWEEN_MOTOR_MOVEMENTS_MS/1000)
    # calculate x and y distance in mm for the next motor move
    print("Current pos",previous_motor_pos)
    previous_x = previous_motor_pos[0]
    previous_y = previous_motor_pos[1]
    next_x = stimPair[1 - po][0]
    next_y = stimPair[1 - po][1]
    x_distance = next_x - previous_x
    y_distance = next_y - previous_y
    print("move x",x_distance)
    print("move y",y_distance)
    # select which axis to enable ttl on stop (the one with longer distance)
    if abs(x_distance) > abs(y_distance):
        my_motor.disable_ttl(my_motor.my_yaxis_id)
        my_motor.enable_ttl(my_motor.my_xaxis_id)
        time.sleep(0.5)
        my_motor.move(my_motor.my_yaxis_id,y_distance)
        my_motor.move(my_motor.my_xaxis_id,x_distance)
    else:
        my_motor.disable_ttl(my_motor.my_xaxis_id)
        my_motor.enable_ttl(my_motor.my_yaxis_id)
        time.sleep(0.5)
        my_motor.move(my_motor.my_xaxis_id,x_distance)
        my_motor.move(my_motor.my_yaxis_id,y_distance)
    # my_motor.move(my_motor.my_xaxis_id,x_distance)
    # my_motor.move(my_motor.my_yaxis_id,y_distance)
    previous_motor_pos = stimPair[1 - po]
    time.sleep(WAIT_TIME_BETWEEN_MOTOR_MOVEMENTS_MS/1000)
##########################################################################################################
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
        trialNo, #trials.thisN + 1,
        thisTrial['standard'],
        thisTrial['comparison'],
        comparisonMoreIntense,
        thisTrial['presentation order'],
        response
    ])

    # outputFiles.logEvent(exptClock.getTime(), '{} of {} complete'.format(trials.thisN + 1, trials.nTotal))
    outputFiles.logEvent(exptClock.getTime(), '{} of {} complete'.format(trialNo, int(exptSettings['06. Number of repeats (even)'])))

# ----

# -- END OF EXPERIMENT --

my_motor.close()
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
