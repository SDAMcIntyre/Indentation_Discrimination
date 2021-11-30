import os

class DataFileCollection():
    def __init__(self, foldername, filename, headers, dlgInput):
        self.folder = './' + foldername + '/'
        if not os.path.exists(self.folder):
            os.makedirs(self.folder)
        self.fileprefix = self.folder + filename

        self.settingsFile = open(self.fileprefix + '_settings.csv', 'w')
        for k, v in dlgInput.items():
            self.settingsFile.write('"{}","{}"\n'.format(k, v))
        self.settingsFile.close()

        self.dataFile = open(self.fileprefix + '_data.csv', 'w')
        self.writeTrialData(headers)
        self.dataFile.close()

        self.logFile = open(self.fileprefix + '_log.csv', 'w')
        self.logFile.write('time,event\n')
        self.logFile.close()

    def logEvent(self, time, event):
        self.logFile = open(self.fileprefix + '_log.csv', 'a')
        self.logFile.write('{},"{}"\n'.format(time, event))
        self.logFile.close()
        print('LOG: {} {}'.format(time, event))

    def logAbort(self, time):
        self.logEvent(time, 'experiment aborted')

    def writeTrialData(self, trialData):
        lineFormatting = ','.join(['{}'] * len(trialData)) + '\n'
        self.dataFile = open(self.fileprefix + '_data.csv', 'a')
        self.dataFile.write(lineFormatting.format(*trialData))
        self.dataFile.close()
