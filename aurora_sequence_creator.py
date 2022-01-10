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
    def __init__(self,protocol_path,path2saveseq,seq_file_name,standard_force,comparison_force,sequence,standard_area,comparison_area):
        self.forceFileName = seq_file_name 

        self.headers = 'DMCv5 Sequence File \nBase File:  \nProtocol File\tTimed?\tTimeToWait\tFileMarker\tRepeat\n'
        self.user_path = protocol_path
        self.forceLineText = self.user_path + '\\Emma ex force{}.dpf\tManual\t0.000\t{}\t0\t\n' 
        self.path2save = path2saveseq
        self.standard = standard_force
        self.comparison = comparison_force
        # list of dictionaries
        self.sequence_dict = sequence
        self.standard_area = standard_area
        self.comparison_area = comparison_area

    def create_aurora_force_sequence(self):
        # shuffle the list of comparison forces
        random.shuffle(self.comparison)
        print("New comparison order",self.comparison)
        # shuffle standard forces
        random.shuffle(self.standard)
        print("New standard order",self.standard)
        force_sequence = []
        standard_iterator = 0
        comparison_iterator = 0
        for i in range(len(self.sequence_dict)):
            if self.sequence_dict[i]['presentation order'] == 'standard first':
                force_sequence.append(self.standard[standard_iterator])
                # wrap around if indexes out of range
                if standard_iterator == len(self.standard)-1:
                    standard_iterator = 0
                else:
                    standard_iterator +=1
                force_sequence.append(self.comparison[comparison_iterator])
                if comparison_iterator == len(self.comparison)-1:
                    comparison_iterator = 0
                else:
                    comparison_iterator +=1
            else:
                force_sequence.append(self.comparison[comparison_iterator])
                if comparison_iterator == len(self.comparison)-1:
                    comparison_iterator = 0
                else:
                    comparison_iterator +=1
                force_sequence.append(self.standard[standard_iterator])
                if standard_iterator == len(self.standard)-1:
                    standard_iterator = 0
                else:
                    standard_iterator +=1
        print("Force sequence",force_sequence)
        return force_sequence

    def create_sequence_file(self,sequence):
        if not os.path.exists(self.path2save):
            os.mkdir(self.path2save)
        forceFile = open(self.path2save + self.forceFileName, 'w')
        forceFile.write(self.headers)
        for n,value in enumerate(sequence):
            forceFile.write(self.forceLineText .format(value,n+1))
        forceFile.close()
