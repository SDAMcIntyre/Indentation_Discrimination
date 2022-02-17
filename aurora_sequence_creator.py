import os
import random

class SequenceCreator():
    '''
        Parameters:
        protocol_path(str) - path where aurora protocol files are stored
        path2saveseq(str) - path where to folder where to save generated sequence dsf file (i.e. data subfolder with other logs)
        seq_file_name(str) - the name of the generated sequence file
        sequence (list of dictionaries that have keys: 'presentation order') 
    
    '''
    def __init__(self,protocol_path,path2saveseq,file_name_prefix,sequence):
        self.file_name_prefix = file_name_prefix

        self.headers = 'DMCv5 Sequence File \nBase File:  \nProtocol File\tTimed?\tTimeToWait\tFileMarker\tRepeat\n'
        self.user_path = protocol_path
        self.forceLineText = self.user_path + '\\Emma{}.dpf\tManual\t0.000\t{}_{}_{}\t0\t\n'
        self.path2save = path2saveseq
        # list of dictionaries
        self.sequence_dict = sequence

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
        forceFile = open((self.path2save+self.file_name_prefix+'_ForceSequence.dsf'), 'w')
        forceFile.write(self.headers)
        for n,value in enumerate(sequence):
            forceFile.write(self.forceLineText .format(value, self.file_name_prefix, value, n+1))
        forceFile.close()