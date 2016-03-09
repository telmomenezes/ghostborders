class Partition:
    def __init__(self, path):
        self.comms = {}
        
        lines = [line.rstrip('\n') for line in open(path)]
        del lines[0]

        # read communities from csv
        for line in lines:
            cols = line.split(',')
            self.comms[int(cols[0])] = int(cols[1])

    def comm(self, loc):
        if loc in self.comms:
            return self.comms[loc]
        else:
            return -1
            
    def loc_dist(self, part, loc1, loc2):
        comm1a = self.comm(loc1)
        comm2a = self.comm(loc2)
        comm1b = part.comm(loc1)
        comm2b = part.comm(loc2)
        if (comm1a == comm2a) == (comm1b == comm2b):
            return 0.
        else:
            return 1.

    # compute Rand index
    # https://en.wikipedia.org/wiki/Rand_index
    def distance(self, part):
        locs = set([loc for loc in self.comms] + [loc for loc in part.comms])
        count = 0.
        dist = 0.
        for loc1 in locs:
            for loc2 in locs:
                if loc2 > loc1:
                    count += 1.
                    dist += self.loc_dist(part, loc1, loc2)
        return dist / count
