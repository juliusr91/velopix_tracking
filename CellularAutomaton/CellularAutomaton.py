# import stuff
from utils.visualizer import CaVisualizer
import event_model
import time
import sys
import copy
from sklearn.decomposition import PCA


class CellularAutomaton(object):

    def __init__(self, max_slopes=(0.7, 0.7), max_tolerance=(0.4, 0.4), max_scatter=0.4, allowed_skip_sensors=1):
        self.__max_slopes = max_slopes
        self.__max_tolerance = max_tolerance
        self.__max_scatter = max_scatter
        self.__allowed_skip_sensors = allowed_skip_sensors
        self.doublets = []

    def are_compatible_in_x(self, hit_0, hit_1):
        """Checks if two hits are compatible according
        to the configured max_slope in x.
        From Daniel
        """
        hit_distance = abs(hit_1[2] - hit_0[2])
        dxmax = self.__max_slopes[0] * hit_distance
        return abs(hit_1[0] - hit_0[0]) < dxmax

    def are_compatible_in_y(self, hit_0, hit_1):
        """Checks if two hits are compatible according
        to the configured max_slope in y.
        From Daniel
        """
        hit_distance = abs(hit_1[2] - hit_0[2])
        dymax = self.__max_slopes[1] * hit_distance
        return abs(hit_1[1] - hit_0[1]) < dymax

    def are_compatible(self, hit_0, hit_1):
        """Checks if two hits are compatible according to
        the configured max_slope.
        From Daniel
        """
        return self.are_compatible_in_x(hit_0, hit_1) and self.are_compatible_in_y(hit_0, hit_1)

    def check_tolerance(self, hit_0, hit_1, hit_2):
        """Checks if three hits are compatible by
        extrapolating the segment conformed by the
        first two hits (hit_0, hit_1) and comparing
        it to the third hit.

        The parameters that control this tolerance are
        max_tolerance and max_scatter.
        From Daniel
        """
        td = 1.0 / (hit_1.z - hit_0.z)
        txn = hit_1.x - hit_0.x
        tyn = hit_1.y - hit_0.y
        tx = txn * td
        ty = tyn * td

        dz = hit_2.z - hit_0.z
        x_prediction = hit_0.x + tx * dz
        dx = abs(x_prediction - hit_2.x)
        tolx_condition = dx < self.__max_tolerance[0]

        y_prediction = hit_0.y + ty * dz
        dy = abs(y_prediction - hit_2.y)
        toly_condition = dy < self.__max_tolerance[1]

        scatter_num = (dx * dx) + (dy * dy)
        scatter_denom = 1.0 / (hit_2.z - hit_1.z)
        scatter = scatter_num * scatter_denom * scatter_denom

        scatter_condition = scatter < self.__max_scatter
        return tolx_condition and toly_condition and scatter_condition

    def calculate_chi2(self, hit_0, hit_1, hit_2):
        """
        Calculate Chi2 for three hits, by extrapolating the line between the first two.
        Used for deciding which tracks are kept and which are discarded.
        """
        td = 1.0 / (hit_1.z - hit_0.z)
        txn = hit_1.x - hit_0.x
        tyn = hit_1.y - hit_0.y
        tx = txn * td
        ty = tyn * td

        dz = hit_2.z - hit_0.z
        x_prediction = hit_0.x + tx * dz
        dx = abs(x_prediction - hit_2.x)

        y_prediction = hit_0.y + ty * dz
        dy = abs(y_prediction - hit_2.y)

        scatter_num = (dx * dx) + (dy * dy)
        scatter_denom = 1.0 / (hit_2.z - hit_1.z)
        scatter = scatter_num * scatter_denom * scatter_denom

        return scatter

    def make_doublets(self, event):
        """
        makes all doublets between all sensors, given that the two hits are compatible, depending on the angle with respect to z
        also makes all doublets when a sensor is skipped.
        """
        self.doublets = []

        for index, sensor in enumerate(event.sensors[:-2]): #for each sensor
            sensor_doublets = []

            #normal sensors
            for index2, next_hit in enumerate(event.sensors[index + 2]): #for each right neighbour
                hit_doublets = []
                for hit in sensor:  # for each hit in each sensor
                    if self.are_compatible(hit, next_hit):
                        doublet = event_model.doublets(hit, next_hit)
                        hit_doublets.append(doublet)
                sensor_doublets.append(hit_doublets)

            #skipped sensors
            if index < len(event.sensors) - 4:
                for index3, next_hit in enumerate(event.sensors[index + 4]): #for each next right neighbour
                    hit_doublets = []
                    for hit in sensor:  # for each hit in each sensor
                        if self.are_compatible(hit, next_hit):
                            doublet = event_model.doublets(hit, next_hit)
                            hit_doublets.append(doublet)
                    sensor_doublets.append(hit_doublets)
            self.doublets.append(sensor_doublets)

    def calculate_shared_point(self, doublet, left_doublet):
        """
        checks if two doublets have a shared point
        """
        return (left_doublet.ending_point.x == doublet.starting_point.x and
                left_doublet.ending_point.y == doublet.starting_point.y and
                left_doublet.ending_point.z == doublet.starting_point.z)

    def find_left_neighbours(self, doublet, index):
        """
        for a given doublet find all left neighbours and append the index to the neighbours list in the doublet object
        """
        for hit_index, left_doublets in enumerate(self.doublets[index - 2]):
            for doublet_index, left_doublet in enumerate(left_doublets):

                if self.calculate_shared_point(doublet, left_doublet):
                    if self.check_tolerance(left_doublet.starting_point, left_doublet.ending_point, doublet.ending_point):
                        doublet.left_neighbours.append([hit_index, doublet_index])
                else:
                    break

    def make_left_neighbours(self):
        """
        loop over all doublets and find all left neighbours
        """
        for index, sensor in enumerate(self.doublets[2:], 2):
            for doublets in sensor:
                for doublet in doublets:
                    self.find_left_neighbours(doublet, index)

    def check_neighbour(self, doublet, index):
        """
        check if any left neighbour has the same state as the current doublet
        """
        for index2, neighbour in enumerate(doublet.left_neighbours):
            state_equality = int(self.doublets[index - 2][neighbour[0]][neighbour[1]].state == doublet.state)
            doublet.new_state += state_equality
            if state_equality:
                return state_equality

        return 0

    def Ca(self):
        """
        does the actual cellular automaton calculation, looping over all doublets, check the neighbours and update the status
        then copies the new state over to the state
        """
        while True:
            changes = int(0)
            for index, sensor in enumerate(self.doublets[2:], 2):
                for doublets in sensor:
                    for doublet in doublets:
                        changes += self.check_neighbour(doublet, index)
            print(changes, file=sys.stderr)

            for index, sensor in enumerate(self.doublets[2:]):
                for doublets in sensor:
                    for doublet in doublets:
                        doublet.state = doublet.new_state

            if changes == 0:
                break

    def extract_next_segment(self, right_doublet, index, track):
        """
        extract the next segment of the track.
        1. loops over the previous doublets and checks if they are neighbours
        2. checks if they are within the tolerance
        3. appends it to the list of neighbours
        4. loops over all the neighbours, checks if the state is smaller
        5. calculates the chi2 for the extension, and adds the segment to the track
        6. recursively until all possible tracks have been created and can be returned
        """
        local_track = copy.deepcopy(track)
        local_tracks = []
        in_loop = False

        index = index - 2
        n_doublets = []
        for previous_doublets in self.doublets[index]:
            for doublet in previous_doublets:
                if self.calculate_shared_point(right_doublet, doublet):
                    try:
                        if self.check_tolerance(doublet.starting_point, doublet.ending_point,
                                                right_doublet.ending_point):
                            n_doublets.append(doublet)
                    except:
                        print(doublet.ending_point, right_doublet.starting_point, right_doublet.ending_point)


        #only goes to the second doublet and not the first
        for n_doublet in n_doublets:
            if n_doublet.state < right_doublet.state and not n_doublet.used:
                in_loop = True
                chi2 = self.calculate_chi2(n_doublet.starting_point, n_doublet.ending_point, right_doublet.ending_point)
                local_track.add_hit(n_doublet.starting_point, chi2)
                local_tracks += self.extract_next_segment(n_doublet, index, local_track)

        if in_loop:
            return local_tracks
        else:
            return [local_track]

    def extract_tracks(self):
        """
        extract the tracks from the Cellular automaton doublets
        1. starts at the most right doublet and creates all possible tracks for all starting doublets
        2. chooses the doublet with the lowest chi2 and appends it to the list of tracks
        3. moves one layer to the left and makes all possible tracks with those starting segments
        """
        self.collected_tracks = []
        for index, sensor in reversed(list(enumerate(self.doublets[2:],2))):
            for doublets in sensor:
                # sorted_doublets = sorted(doublets, key=lambda x: x.state) #probably only finds one track per sensor
                for doublet in doublets:
                    if doublet.state > 1 and not doublet.used:
                        hits=[]
                        hits.append(doublet.ending_point)
                        hits.append(doublet.starting_point)
                        track = event_model.track(hits, len(hits))

                        track = self.extract_next_segment(doublet, index, track)
                        track = sorted(track, key=lambda x: x.new_x, reverse=True)

                        self.collected_tracks.append(track[0])

    def remove_shorttracks(self, length):
        """
        removes all tracks that are shorter than the length indicates
        """
        self.long_tracks = []
        for tracks in self.collected_tracks:
            if len(tracks.hits) > length:
                self.long_tracks.append(tracks)

    def remove_ghosts_clones(self):
        """
        removes possible ghosts and clones
        sorts the created tracks by length and chi2;
        where longer tracks are first and smoother tracks (smaller chi2) are first
        then it starts with the longest tracks and adds it to the list of final tracks
        all hits used in that track are added to a list; if a track consists off more than 30% used tracks its not added

        thus we pick the longest and smoothest tracks first

        instead of the sorting i also tried to combine the length and chi2 in a PCA. worked quite well
        """


        #PCA trial
        # x=[]
        # for track in self.long_tracks:
        #     x.append([track.length, track.chi2])
        #
        # pca = PCA(n_components=1)
        # x_new = pca.fit_transform(x)
        #
        # for index, track in enumerate(self.long_tracks):
        #     track.new_x = x_new[index]
        # self.all_collected_tracks = sorted(self.long_tracks, key=lambda x: x.new_x, reverse=True)

        #normal sorting
        self.all_collected_tracks = sorted(self.long_tracks, key=lambda x: (x.length, 1/x.chi2), reverse=True)
        self.long_tracks = []
        self.used_hits = []

        for index, track in enumerate(self.all_collected_tracks):
            counter = 0
            for hits in track:
                if hits.id in self.used_hits:
                    counter += 1
            if counter/track.length < 0.3:
                for hits in track:
                    self.used_hits.append(hits.id)
                self.long_tracks.append(track)

    def solve(self, event):

        """
        main function

        1. Creates all possible and applicable doublets

        2. searches for all the left neighbours of these doublets

        3. Runs the Cellular Automaton (CA)

        4. Extract all possible tracks of the CA

        5. remove short tracks

        6. Removes Clones and Ghost Tracks
        """

        # 1. Creates all possible and applicable doublets
        start = time.clock()
        self.make_doublets(event)
        print("making doublets took: ", time.clock()-start)

        #2. searches for all the left neighbours of these doublets
        start = time.clock()
        self.make_left_neighbours()
        print("making neighbours took: ", time.clock() - start)

        #3. Runs the Cellular Automaton (CA)
        start = time.clock()
        self.Ca()
        print("ca took: ", time.clock() - start)

        #4. Extract all possible tracks of the CA
        start = time.clock()
        self.extract_tracks()
        # print(self.collected_tracks)
        print("extracting took: ", time.clock() - start)

        # 5. remove short tracks
        start = time.clock()
        self.remove_shorttracks(2) #keeps everything longer than 2
        print("removing shorttracks took: ", time.clock() - start)

        #6. Removes Clones and Ghost Tracks
        start = time.clock()
        self.remove_ghosts_clones()  # keeps everything longer than 2
        print("removing ghost_clones took: ", time.clock() - start)


        #Possible visualisation of the segments and the tracks found
        # vis = CaVisualizer(self.doublets, self.long_tracks)
        # vis.visualize_segments()
        # vis.visualize_found_tracks()
        return (self.long_tracks)