import os
import random

class SequenceCreator():
    '''
        Parameters:
        protocol_path(str) - path where aurora protocol files are stored
        path2saveseq(str) - path where to folder where to save generated sequence dsf file (i.e. data subfolder with other logs)
        seq_file_name(str) - the name of the generated sequence file
        standard_force(list of floats) - list of all standard forces (will be randomly shuffled). If there is more trials than forces, it will be wrapped around
        comparison_force (list of floats) - list of all comparison forces (will be randomly shuffled). If there is more trials than forces, it will be wrapped around
        sequence (list of dictionaries that have keys: 'presentation order') 
        standard_area ('A' or 'B') - which area was selected as a standard
        comparison_area ('A' or 'B') - which area was selected as comparison
    
    '''
    def __init__(self,protocol_path,path2saveseq,seq_file_name,sequence,standard_area,comparison_area):
        self.forceFileName = seq_file_name 

        self.headers = 'DMCv5 Sequence File \nBase File:  \nProtocol File\tTimed?\tTimeToWait\tFileMarker\tRepeat\n'
        self.user_path = protocol_path
        self.forceLineText = self.user_path + '\\Emma{}.dpf\tManual\t0.000\t{}\t0\t\n'
        self.path2save = path2saveseq
        # list of dictionaries
        self.sequence_dict = sequence
        self.standard_area = standard_area
        self.comparison_area = comparison_area

    def create_aurora_force_sequence(self):
        force_sequence = []
        for dictionary in self.sequence_dict:
            if dictionary['presentation order'] == 'standard first':
                force_sequence.append(dictionary['standard_force'])
                force_sequence.append(dictionary['comparison_force'])
            else:
                force_sequence.append(dictionary['comparison_force'])
                force_sequence.append(dictionary['standard_force'])
        # print("Force sequence",force_sequence)
        return force_sequence

    def create_sequence_file(self,sequence):
        if not os.path.exists(self.path2save):
            os.mkdir(self.path2save)
        forceFile = open(self.path2save + self.forceFileName, 'w')
        forceFile.write(self.headers)
        for n,value in enumerate(sequence):
            forceFile.write(self.forceLineText .format(value,n+1))
        forceFile.close()
