import numpy as np
import numpy.polynomial.legendre as L

from abc import ABC, abstractmethod

import mcdc.mpi

from mcdc.misc     import binary_search
from mcdc.constant import EPSILON


# =============================================================================
# Filter base abstract classes
# =============================================================================

class Filter(ABC):
    @property
    @abstractmethod
    def grid(self):
        pass

    @property
    @abstractmethod
    def N_bin(self):
        pass
    
    @abstractmethod
    def __init__(self, grid):
        pass

    @abstractmethod
    def __call__(self, P):
        pass

class FilterSpatial(Filter):
    @property
    @abstractmethod
    def N_face(self):
        pass

# =============================================================================
# Energy filters     
# =============================================================================

class FilterEnergyGroup(Filter):
    grid  = None
    N_bin = None
    
    def __init__(self, grid):
        self.grid  = grid
        self.N_bin = len(grid)
        
    def __call__(self, P):
        return binary_search(P.g_old, self.grid) + 1

# =============================================================================
# Angular filters
# =============================================================================

class FilterPolarCosine(Filter):
    grid  = None
    N_bin = None
    
    def __init__(self, grid):
        self.grid  = grid
        self.N_bin = len(grid) - 1
            
    def __call__(self, P):
        return binary_search(P.dir_old.x, self.grid)

#===============================================================================
# Time Filter
#   Outputs:
#     (1) bins crossed
#     (2) track-length scored in each bin
#     (3) edges hit
#     (4) weight scored at each edge
#     (5) track-length-rate scored at each edge
#===============================================================================

class FilterTime(Filter):
    grid  = None
    N_bin = None
    
    def __init__(self, grid):
        self.grid  = grid
        self.N_bin = len(grid) - 1
        
    def __call__(self, P):
        # Get particle states
        k     = binary_search(P.time, self.grid)
        k_old = max(0,binary_search(P.time_old, self.grid))
        speed = P.speed
        wgt_init  = P.wgt_old
        wgt_final = P.wgt
                
        # Determine bins crossed
        bins  = np.arange(k_old, k+1)
        t_min = P.time_old
        t_max = P.time

        # Only one bin crossed?
        if len(bins) == 1:
            if bins[0] == -1 or bins == self.N_bin:
                return [], [], [], [], []
            else:
                wgt = wgt_init
                return bins, [wgt*P.distance], [], [], []

        # Edges hit
        edges = bins[1:] - 1

        # Distance traveled in each bin
        distance = np.zeros(len(bins))
        
        # Partial first bin
        distance[0] = (self.grid[bins[0]+1]-t_min)*speed
            
        # Partial last bin
        distance[-1] = (t_max-self.grid[bins[-1]])*speed

        # Full middle bins
        for i in range(1, len(bins)-1):
            distance[i] = (self.grid[bins[i]+1] - self.grid[bins[i]])*speed       

        # Weight at each grid and weight average at each bin
        wgt     = np.ones(len(edges))*wgt_init
        wgt_avg = np.ones(len(bins))*wgt_init

        # Track-length-rate scored at each grid
        TLR = wgt*speed
        
        # Track-length scored in each bin
        TL = distance*wgt_avg        

        # Cut outsiders
        if bins[0] == -1:
            bins = bins[1:]
            TL = TL[1:]
        if bins[-1] == self.N_bin:
            bins = bins[:-1]
            TL = TL[:-1]

        return bins, TL, edges, wgt, TLR
    
# =============================================================================
# Spatial Filter        
#   Outputs:
#     (1) bins crossed
#     (2) track-length scored in each bin
#     (3) faces hit (and sense)
#     (4) weight scored at each face
#     (5) track-length-rate scored at each face
# =============================================================================
    
class FilterSurface(FilterSpatial):
    grid   = None
    N_bin  = None
    N_face = None
    
    def __init__(self, surfaces):
        self.grid   = [x.id for x in surfaces]
        self.N_bin  = 0
        self.N_face = len(surfaces)
        
        self.grid.sort()
            
    def __call__(self, P):
        if P.surface and P.surface.id in self.grid:
            # Get sense
            sense = 0
            if P.surface.evaluate(P.pos) > 0:
                sense = 1
            faces = [np.array([binary_search(P.surface.id, self.grid) + 1,
                              sense])]
            wgt = [P.wgt]
            TLR = [P.wgt/abs(P.surface.normal(P.pos,P.dir_old))]
            return [0], [0.0], faces, wgt, TLR
        else:
            return [], [], [], [], []

class FilterCell(FilterSpatial):
    grid   = None
    N_bin  = None
    N_face = None
    
    def __init__(self, grid):
        self.grid   = grid
        self.N_bin  = len(grid)
        self.N_face = 0
            
    def __call__(self, P):
        wgt  = p.wgt_old
        bins = [binary_search(P.cell_old.id, self.grid) + 1]
        TL   = [wgt*P.distance]
        return bins, TL, [], [], []

class FilterPlaneX(FilterSpatial):
    grid   = None
    N_bin  = None
    N_face = None
    
    def __init__(self, grid):
        self.grid   = grid
        self.N_bin  = len(grid) - 1
        self.N_face = len(grid)
            
    def __call__(self, P):
        # Get particle states
        j     = binary_search(P.pos.x, self.grid)
        j_old = binary_search(P.pos_old.x, self.grid)
        dir   = P.dir_old.x
        wgt_init  = P.wgt_old
        wgt_final = P.wgt
        
        # Go to positive direction?
        go_plus = dir > 0.0        
        
        # Determine bins crossed
        if go_plus:
            bins  = np.arange(j_old, j+1)
            x_min = P.pos_old.x
            x_max = P.pos.x
        else:
            bins  = np.arange(j, j_old+1)
            x_min = P.pos.x
            x_max = P.pos_old.x
            
        # Only one bin crossed?
        if len(bins) == 1:
            wgt = wgt_init
            return bins, [wgt*P.distance], [], [], []

        # Faces hit (and sense)
        faces = np.zeros([len(bins)-1,2],dtype=int)
        faces[:,0] = bins[1:]
        if go_plus:
            faces[:,1] = 1
            
        # Distance traveled in each bin
        distance = np.zeros(len(bins))
        
        # Partial first bin
        distance[0]  = abs((self.grid[bins[0]+1] - x_min)/dir)
            
        # Partial last bin
        distance[-1] = abs((x_max - self.grid[bins[-1]])/dir)

        # Full middle bins
        for i in range(1, len(bins)-1):
            distance[i]  = abs((self.grid[bins[i]+1] - self.grid[bins[i]])/dir)

        # Weight at each grid and weight average at each bin
        wgt     = np.ones(len(faces))*wgt_init
        wgt_avg = np.ones(len(bins))*wgt_init
        
        # Track-length-rate scored at each face
        TLR = wgt/abs(dir)
                
        # Track-length scored in each bin
        TL = distance*wgt_avg        

        # Cut outsider
        if bins[0] == -1:
            bins = bins[1:]
            TL = TL[1:]
        if bins[-1] == self.N_bin:
            bins = bins[:-1]
            TL = TL[:-1]
            
        # Flip order if going left
        if not go_plus:
            bins  = np.flip(bins)
            TL    = np.flip(TL)
            faces = np.flip(faces,axis=0)
            wgt   = np.flip(wgt)
            TLR   = np.flip(TLR)
        return bins, TL, faces, wgt, TLR
    
# =============================================================================
# Tally
# =============================================================================

class Tally:
    def __init__(self, name, scores, 
                 time_filter=None, angular_filter=None,
                 energy_filter=None, spatial_filter=None):
        
        self.name        = name
        self.score_names = scores
        self.scores      = []
        self.filter_flag_time    = False
        self.filter_flag_angular = False
        self.filter_flag_energy  = False
        self.filter_flag_spatial = False

        # =====================================================================
        # Set filters
        # =====================================================================
        
        # Time filter
        if time_filter:
            self.filter_time = time_filter
            self.filter_flag_time    = True
        else:
            self.filter_time = FilterTime(np.array([0.0, np.inf]))                
        
        # Angular filter
        if angular_filter:
            self.filter_angular = angular_filter
            self.filter_flag_angular = True
        else:
            self.filter_angular = FilterPolarCosine(np.array([-1.0, 1.0]))

        # Energy filter
        if energy_filter:
            self.filter_energy = energy_filter
            self.filter_flag_energy  = True
        else:
            self.filter_energy = FilterEnergyGroup(np.array([np.inf]))
            
        # Spatial filter
        if spatial_filter:
            self.filter_spatial = spatial_filter
            self.filter_flag_spatial = True
        else:
            self.filter_spatial = FilterPlaneX(np.array([-np.inf, np.inf]))    

    def setup_bins(self, N_iter):
        self.scores = []

        # Shapes
        N_time         = self.filter_time.N_bin
        N_energy       = self.filter_energy.N_bin
        N_angular      = self.filter_angular.N_bin
        N_spatial_bin  = self.filter_spatial.N_bin
        N_spatial_face = self.filter_spatial.N_face

        for score in self.score_names:
            score_name = score.split('-')[0]
            if len(score.split('-')) > 1:
                score_mode = score.split('-')[1]
            else:
                score_mode = ''
                
            # Determine tally shape
            if score_mode in ['face']:
                N_spatial = N_spatial_face
            elif score_mode in ['edge', '']:
                N_spatial = N_spatial_bin

            if score_name in ['flux', 'absorption']:
                shape = [N_time, N_energy, N_angular, N_spatial]
            elif score_name in ['current']:
                shape = [N_time, N_energy, N_spatial, 3]
            elif score_name in ['eddington']:
                shape = [N_time, N_energy, N_spatial, 6]
            elif score_name in ['total_crossing', 'net_crossing']:
                shape = [N_time, N_energy, N_spatial_face]
            elif score_name in ['partial_crossing']:
                shape = [N_time, N_energy, N_spatial_face, 2]
            elif score_name in ['fet']:
                shape = [N_time, N_energy, N_spatial, 20]
            
            # Iteration dimension
            shape = [N_iter] + shape
            
            # Set score
            if score_name == 'flux':
                S = ScoreFlux(score, shape)
            elif score_name == 'absorption_rate':
                S = ScoreAbsorption(score, shape)
            elif score_name == 'current':
                S = ScoreCurrent(score, shape)
            elif score_name == 'eddington':
                S = ScoreEddington(score, shape)
            elif score_name == 'total_crossing':
                S = ScoreCrossingTotal(score, shape)
            elif score_name == 'net_crossing':
                S = ScoreCrossingNet(score, shape)
            elif score_name == 'partial_crossing':
                S = ScoreCrossingPartial(score, shape)
            elif score_name == 'fet':
                S = ScoreFET(score, shape)

            # Set modifiers
            if score_mode == 'face':
                S.face_cross = True
            elif score_mode  == 'edge':
                S.time_edge = True
            elif score_name in ['total_crossing', 'net_crossing', 
                                'partial_crossing']:
                S.face_cross = True
            
            self.scores.append(S)
                    
                    
    def score(self, P):
        # Get spatial and time bin indices
        spatial_bins, spatial_TL, spatial_faces, spatial_wgt, spatial_TLR \
            = self.filter_spatial(P)
        time_bins, time_TL, time_edges, time_wgt, time_TLR \
            = self.filter_time(P)

        track_length_bins   = []
        track_length_scores = []
        face_cross_bins   = []
        face_cross_scores = []
        time_edge_bins   = []
        time_edge_scores = []
                
        if len(time_TL) > 0 and len(spatial_TL) > 0:
            filter_score = True
            k = 0
            j = 0
            sum_time    = time_TL[0]
            sum_spatial = spatial_TL[0]
            low         = 0.0
        else:
            filter_score = False
            
        while filter_score:
            # TL score
            track_length_bins.append([time_bins[k],spatial_bins[j]])

            # Hit time edge or spatial face or both?
            hit_time    = False
            hit_spatial = False
            diff = sum_time - sum_spatial
            if abs(diff) < EPSILON:
                hit_time    = True
                hit_spatial = True
            elif diff < 0.0:
                hit_time = True
            else:
                hit_spatial = True
            
            # Assign scores
            if hit_time:
                score = sum_time-low
                if k < len(time_edges):
                    time_edge_bins.append([time_edges[k],spatial_bins[j]])
                    time_edge_scores.append([time_TLR[k]])
            if hit_spatial:
                score = sum_spatial-low
                if j < len(spatial_faces):
                    face_cross_bins.append([time_bins[k],spatial_faces[j][0],spatial_faces[j][1]])
                    face_cross_scores.append([spatial_TLR[j], spatial_wgt[j]])
            track_length_scores.append([score])

            # Increment
            if hit_time:
                k += 1
                if k < len(time_bins):
                    sum_time += time_TL[k]
                else:
                    break
            if hit_spatial:
                j += 1
                if j < len(spatial_bins):
                    sum_spatial += spatial_TL[j]
                else:
                    break
            low += score

        # Get energy group and angular bin indices
        g = self.filter_energy(P)
        n = self.filter_angular(P)

        for S in self.scores:
            bin_idx   = track_length_bins
            bin_score = track_length_scores
            if S.time_edge:
                bin_idx   = time_edge_bins
                bin_score = time_edge_scores
            elif S.face_cross:
                bin_idx   = face_cross_bins
                bin_score = face_cross_scores
            S(P, g, n, bin_idx, bin_score)
            
    def closeout_history(self):
        for S in self.scores:
            # Accumulate
            S.sum    += S.bin
            S.sq_sum += np.square(S.bin)
        
            # Reset bin
            S.bin.fill(0.0)
        
    def closeout(self, N_hist, i_iter):
        for S in self.scores:
            # MPI Reduce
            mcdc.mpi.reduce_master(S.sum, S.sum_buff)
            mcdc.mpi.reduce_master(S.sq_sum, S.sq_sum_buff)
            S.sum[:]    = S.sum_buff[:]
            S.sq_sum[:] = S.sq_sum_buff[:]
            
            if mcdc.mpi.master:
                S.mean[i_iter,:] = S.sum/N_hist
                S.sdev[i_iter,:] = np.sqrt((S.sq_sum/N_hist - np.square(S.mean[i_iter]))/(N_hist-1))
            
            # Reset accumulator
            S.sum.fill(0.0)
            S.sq_sum.fill(0.0)
            
# =============================================================================
# Scores
# =============================================================================
    
class Score(ABC):
    def __init__(self, name, shape):
        self.name       = name
        self.time_edge  = False
        self.face_cross = False
        
        self.bin = np.zeros(shape[1:])
        # Accumulators
        self.sum    = np.zeros_like(self.bin)
        self.sq_sum = np.zeros_like(self.bin)
        # MPI buffers
        self.sum_buff    = np.zeros_like(self.bin)
        self.sq_sum_buff = np.zeros_like(self.bin)
        # Results
        if mcdc.mpi.master:
            self.mean = np.zeros(shape)
            self.sdev = np.zeros_like(self.mean)
            
    @abstractmethod
    def __call__(self, P, g, n, bin_idx, bin_score):
        pass

class ScoreFlux(Score):
    def __init__(self, name, shape):
        Score.__init__(self, name, shape)
    def __call__(self, P, g, n, bin_idx, bin_score):
        for i in range(len(bin_idx)):
            k = bin_idx[i][0]
            j = bin_idx[i][1]
            flux = bin_score[i][0]
            self.bin[k,g,n,j] += flux

class ScoreFET(Score):
    def __init__(self, name, shape):
        Score.__init__(self, name, shape)
    def __call__(self, P, g, n, bin_idx, bin_score):
        for i in range(len(bin_idx)):
            k = bin_idx[i][0]
            j = bin_idx[i][1]
            flux = bin_score[i][0]
            # fet, 20 terms
            for l in range(20):
                self.bin[k,g,j,l] += flux * L.Legendre.basis(l)(j/60 * 2 - 1)
            
class ScoreCurrent(Score):
    def __init__(self, name, shape):
        Score.__init__(self, name, shape)
    def __call__(self, P, g, n, bin_idx, bin_score):
        for i in range(len(bin_idx)):
            k = bin_idx[i][0]
            j = bin_idx[i][1]
            flux = bin_score[i][0]
            # x
            self.bin[k,g,j,0] += flux*P.dir_old.x
            # y
            self.bin[k,g,j,1] += flux*P.dir_old.y
            # z
            self.bin[k,g,j,2] += flux*P.dir_old.z
            
class ScoreEddington(Score):
    def __init__(self, name, shape):
        Score.__init__(self, name, shape)
    def __call__(self, P, g, n, bin_idx, bin_score):
        for i in range(len(bin_idx)):
            k = bin_idx[i][0]
            j = bin_idx[i][1]
            flux = bin_score[i][0]
            # xx
            self.bin[k,g,j,0] += flux*P.dir_old.x*P.dir_old.x
            # xy
            self.bin[k,g,j,1] += flux*P.dir_old.x*P.dir_old.y
            # xz
            self.bin[k,g,j,2] += flux*P.dir_old.x*P.dir_old.z
            # yy
            self.bin[k,g,j,3] += flux*P.dir_old.y*P.dir_old.y
            # yz
            self.bin[k,g,j,4] += flux*P.dir_old.y*P.dir_old.z
            # zz
            self.bin[k,g,j,5] += flux*P.dir_old.z*P.dir_old.z

class ScoreCrossingPartial(Score):
    def __init__(self, name, shape):
        Score.__init__(self, name, shape)
    def __call__(self, P, g, n, bin_idx, bin_score):
        for i in range(len(bin_idx)):
            k     = bin_idx[i][0]
            j     = bin_idx[i][1]
            sense = bin_idx[i][2]
            wgt   = bin_score[i][1]
            self.bin[k,g,j,sense] += wgt
            
class ScoreCrossingTotal(Score):
    def __init__(self, name, shape):
        Score.__init__(self, name, shape)
    def __call__(self, P, g, n, bin_idx, bin_score):
        for i in range(len(bin_idx)):
            k     = bin_idx[i][0]
            j     = bin_idx[i][1]
            wgt   = bin_score[i][1]
            self.bin[k,g,j] += wgt
            #print("score ",g,wgt)
            #input()
            
class ScoreCrossingNet(Score):
    def __init__(self, name, shape):
        Score.__init__(self, name, shape)
    def __call__(self, P, g, n, bin_idx, bin_score):
        for i in range(len(bin_idx)):
            k     = bin_idx[i][0]
            j     = bin_idx[i][1]
            sense = bin_idx[i][2]
            wgt   = bin_score[i][1]
            if sense == 0:
                self.bin[k,g,j] -= wgt
            else:
                self.bin[k,g,j] += wgt
