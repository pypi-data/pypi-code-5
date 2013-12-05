
import math, copy

from nesoni import config

from . import design, profile

@config.Float_flag('tweak_gapextra')
#@config.Float_flag('tweak_bulgediameter')
#@config.Float_flag('tweak_bulgepos1')
#@config.Float_flag('tweak_bulgepos2')
@config.Float_flag('tweak_boreless')
class Design_whistle(design.Instrument_designer_with_bore_scale):
    def get_whistle_maker(self):
        from . import make_whistle
        bore = self.inner_diameters[-1]
        outside = self.outer_diameters[-1]
        if self.outer_add: outside += bore
        return make_whistle.Make_whistle_head(
            bore = bore,
            outside = outside,
            )
        
    closed_top = False
    
    divisions = [ ]

    # For gap_width 0.5, gap_length 0.25, from soprano
    # tweak_gapextra = 0.37
    
    # From soprano recorder
    tweak_gapextra = 0.75 #0.71
    #tweak_bulgediameter = 1.0
    #tweak_bulgepos1 = 0.5
    #tweak_bulgepos2 = 0.9
    tweak_boreless = 0.65 #0.49
    
    def patch_instrument(self, inst):
        inst = copy.copy(inst)
        inst.true_length = inst.length
        inst.true_inner = inst.inner
        
        bore_diameter = inst.inner(inst.length)
        inst.length -= bore_diameter * self.tweak_boreless
        inst.inner = inst.inner.clipped(0.0,inst.length)

        #bulge_pos1 = self.tweak_bulgepos1 * inst.length
        #bulge_pos2 = self.tweak_bulgepos2 * inst.length
        #if bulge_pos1 > bulge_pos2:
        #    bulge_pos1, bulge_pos2 = bulge_pos2, bulge_pos1
        #bulge_amount = (self.tweak_bulgediameter-1.0) * bore_diameter
        #inst.inner = inst.inner + profile.Profile(
        #    [ bulge_pos1, bulge_pos2 ],
        #    [ 0.0, bulge_amount ],
        #    [ bulge_amount, 0.0 ],
        #    )
        
        maker = self.get_whistle_maker()
        diameter = maker.effective_gap_diameter()             
        length = maker.effective_gap_height() / 2.0
        #        ^ The gap is this high on one side and a blade on the other side
        #          split the difference.
        length += diameter * self.tweak_gapextra
        
        inst.inner = profile.Profile(
            inst.inner.pos + [ inst.length+length ],
            inst.inner.low + [ diameter ],
            inst.inner.high[:-1] + [ diameter, diameter ],
            )
        inst.length += length
        return inst


@config.help("""\
Design a whistle with pennywhistle fingering.
""")
class Design_folk_whistle(Design_whistle):    
    divisions = [
        [(5,0)],
        [(0,0),(5,0)],
        [(1,0),(5,0),(5,0.5)],
        ]
    
    initial_length = design.wavelength('D4') * 0.5
    
    min_hole_diameters = design.bore_scaler([ 3.0 ]*6)
    max_hole_diameters = design.bore_scaler([ 13.0 ]*6)
    
    horiz_angles = [ 0.0 ] * 6
    mid_cut = 3

    #balance = [ 0.05, 0.05, 0.05, 0.05 ]
    balance = [ 0.2 ]*4
    @property
    def min_hole_spacing(self):
        b = self.inner_diameters[-1]
        return [ b*1.15 ] * 5 #[ b,b,b*1.25,b,b ]

    inner_diameters = design.bore_scaler([ 24.0, 20.0, 20.0, 22.0, 20.0, 20.0 ])
    initial_inner_fractions = [ 0.2, 0.6,0.65,0.7 ]
    min_inner_fraction_sep = [ 0.02 ] * 5

#    outer_diameters = design.bore_scaler([ 38.0, 28.0, 28.0 ])    
#    initial_outer_fractions = [ 0.15 ]
#    min_outer_fraction_sep = [ 0.15, 0.8 ]

    outer_diameters = design.bore_scaler([ 40.0, 28.0, 28.0, 32.0, 32.0 ])    
    initial_outer_fractions = [ 0.15, 0.5, 0.85 ]
    min_outer_fraction_sep = [ 0.15, 0.3, 0.35, 0.15 ]
    
    #min_outer_fraction_sep = [ 0.01, 0.5 ]

    fingerings = [
        ('D4',   [1,1,1,1,1,1]),
        ('E4',   [0,1,1,1,1,1]),
        ('F#4',  [0,0,1,1,1,1]),
        ('G4',   [0,0,0,1,1,1]),
        ('A4',   [0,0,0,0,1,1]),
        ('B4',   [0,0,0,0,0,1]),
        ('C5',   [0,0,0,1,1,0]),
        ('C#5',  [0,0,0,0,0,0]),
        ('D5',   [1,1,1,1,1,0]),
        ('E5',   [0,1,1,1,1,1]),
        ('F#5',  [0,0,1,1,1,1]),
        ('G5',   [0,0,0,1,1,1]),
        ('A5',   [0,0,0,0,1,1]),
        ('B5',   [0,0,0,0,0,1]),
        #('C#6',  [1,1,1,0,0,0]),
        #('C#6',  [0,0,0,0,0,0]),
        ('D6',   [1,1,1,1,1,1]),
    ]


@config.help("""\
Design a recorder. \
This is like a penny-whistle, but with a complicated fingering system.
""")
class Design_recorder(Design_whistle):
    divisions = [
        [(7,0)],
        [(0,0),(7,0)],
        [(0,0),(3,0),(7,0)],
        [(0,0),(3,0),(7,0),(7,0.5)],
        [(0,0),(2,0),(4,0),(7,0),(7,0.5)],
        ]
    
    initial_length = design.wavelength('C4') * 0.5
    
    min_hole_diameters = design.bore_scaler([ 3.0 ]*8)
    max_hole_diameters = design.bore_scaler([ 12.0 ] + [ 14.0 ]*7)
    min_hole_spacing = design.sqrt_scaler([ 0.0 ]*6+[-50.0])

    horiz_angles = [ -15.0 ] + [ 0.0 ] * 6 + [ 180.0 ]
    hole_angles = [ -30, 30, -30, 30, 0, 0, 0, 0 ]

    balance = [ 0.1, 0.05, None, None, 0.05, None ]
    #balance = [ 0.2 ]*4
    #@property
    #def min_hole_spacing(self):
    #    b = self.inner_diameters[-1]
    #    return [ b*1.15 ] * 5 #[ b,b,b*1.25,b,b ]

#    inner_diameters = design.bore_scaler([ 17.0, 20.0, 20.0, 23.0, 20.0, 20.0 ])
    inner_diameters = design.bore_scaler([ 20.0, 20.0, 19.0, 23.0, 23.0, 20.0, 20.0 ])
    initial_inner_fractions = [ 0.6,0.65,0.7,0.75,0.8 ]
    min_inner_fraction_sep = [ 0.3,0.01,0.01,0.01,0.01,0.01 ]

    outer_diameters = design.bore_scaler([ 40.0, 28.0, 28.0, 32.0, 32.0 ])    
    initial_outer_fractions = [ 0.15, 0.6, 0.85 ]
    min_outer_fraction_sep = [ 0.15, 0.3, 0.35, 0.15 ]


    fingerings = [
        ('C4',   [1,1,1,1,1,1,1,1]),
        # Inter-register locking
        ('C5',   [1,1,1,1,1,1,1,1]),
        ('G5',   [1,1,1,1,1,1,1,1]),

        ('D4',   [0,1,1,1,1,1,1,1]),
        # Inter-register locking
        ('D5',   [0,1,1,1,1,1,1,1]),
        ('A5',   [0,1,1,1,1,1,1,1]),

        ('E4',   [0,0,1,1,1,1,1,1]),
        # Inter-register locking
        ('B5',   [0,0,1,1,1,1,1,1]),
        
        #Tendency to be sharp, due to inter register locking?
        ('F4',   [1,1,0,1,1,1,1,1]),
        ('F4',   [0,1,0,1,1,1,1,1]),
        
        ('F#4',  [0,1,1,0,1,1,1,1]),
        ('G4',   [0,0,0,0,1,1,1,1]),
        ('G#4',  [0,1,1,1,0,1,1,1]),
        ('A4',   [0,0,0,0,0,1,1,1]),
        ('Bb4',  [0,0,0,1,1,0,1,1]),
        ('B4',   [0,0,0,0,0,0,1,1]),
        ('C5',   [0,0,0,0,0,1,0,1]),
        ('C#5',  [0,0,0,0,0,1,1,0]),
        ('D5',   [0,0,0,0,0,1,0,0]),


        ('Eb5',  [0,1,1,1,1,1,0,0]),
        
        ('E5',   [0,0,1,1,1,1,1,0]),
        ('E5',   [0,0,1,1,1,1,1,1]),
        
        ('F5',   [0,1,0,1,1,1,1,0]),
        ('F5',   [0,1,0,1,1,1,1,1]),
        
        ('F#5',  [0,0,1,0,1,1,1,0]),
        ('F#5',  [0,0,1,0,1,1,1,1]),

        #('G5',   [0,0,0,0,1,1,1,0]),
        ('G5',   [0,0,0,0,1,1,1,1]),

        #('G#5',  [0,0,0,1,0,1,1,1]),
        ('A5',   [0,0,0,0,0,1,1,1]),
#        ('Bb5',  [0,1,1,1,0,1,1,1]),
#        ('B5',   [0,0,1,1,0,1,1,1]),
    ]
    

@config.help("""\
Design a three hole pipe, i.e. the pipe in pipe-and-tabor.
""")
class Design_three_hole_whistle(Design_whistle):
    bore_scale = 1.25
    
    divisions = [
        [],
        [(2,0.3)],
        [(2,0.05),(2,0.5)],
        [(2,0),(2,0.333),(2,0.666)],
        [(0,0),(2,0),(2,0.333),(2,0.666)],
        ]
    
    initial_length = design.wavelength('D3') * 0.5
    
    min_hole_diameters = design.bore_scaler([ 3.0 ]*3)
    max_hole_diameters = design.bore_scaler([ 14.0 ]*3)
    
    hole_angles = [ 0.0, 0.0, 0.0 ]
    horiz_angles = [ 0.0, 0.0, 180.0 ]
    mid_cut = 2
    
    #min_hole_spacing = [ -20.0, -20.0 ]
    
    initial_hole_fractions = [ 0.1,0.15,0.2 ]
    
    inner_diameters = design.bore_scaler([ 15.0, 15.0, 20.0, 20.0 ])
    initial_inner_fractions = [ 0.1, 0.75 ]
    
    outer_diameters = design.bore_scaler([ 23.0, 28.0, 32.0, 32.0 ])
    min_outer_fraction_sep = [ 0.55, 0.3, 0.1 ]
    initial_outer_fractions = [ 0.6, 0.9 ]
        
    min_inner_fraction_sep = [ 0.01 ] * 8

    fingerings = [
        ('D4', [1,1,1]),
        ('E4', [0,1,1]),
        ('F#4',[0,0,1]),
        ('G4', [0,0,0]),
        ('A4', [1,1,1]),
        ('B4', [0,1,1]),
        ('C#5',[0,0,1]),
        ('D5', [0,0,0]),
        ('D5', [1,1,1]),
        ('E5', [0,1,1]),
        ('F#5',[0,0,1]),
        ('G5', [0,0,0]),
    ]


