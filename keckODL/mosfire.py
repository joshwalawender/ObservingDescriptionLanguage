#!python3

## Import General Tools
from pathlib import Path
import re
from warnings import warn
import yaml
from copy import deepcopy
from astropy import units as u


from .detector_config import IRDetectorConfig
from .instrument_config import InstrumentConfig
from .sequence import SequenceElement, Sequence
from .offset import SkyFrame, InstrumentFrame, TelescopeOffset, OffsetPattern
from .offset import Stare


##-------------------------------------------------------------------------
## MOSFIRE Frames
##-------------------------------------------------------------------------
detector = InstrumentFrame(name='MOSFIRE Detector',
                           scale=0.1798*u.arcsec/u.pixel,
                           offsetangle=+0.22*u.deg)
slit = InstrumentFrame(name='MOSFIRE Slit',
                       scale=0.1798*u.arcsec/u.pixel,
                       offsetangle=+4.0*u.deg)


##-------------------------------------------------------------------------
## MOSFIREDetectorConfig
##-------------------------------------------------------------------------
class MOSFIREDetectorConfig(IRDetectorConfig):
    '''An object to hold information about NIRES detector configuration.
    '''
    def __init__(self, exptime=None, readoutmode='CDS', coadds=1):
        super().__init__(instrument='MOSFIRE', exptime=exptime,
                         readoutmode=readoutmode, coadds=coadds)


    ##-------------------------------------------------------------------------
    ## Validate
    def validate(self):
        '''Check values and verify that they meet assumptions.
        
        Check:
        - readoutmode is either CDS or MCDSn where n is 1-32.
        
        Warn:
        '''
        parse_readoutmode = re.match('(M?)CDS(\d*)', self.readoutmode)
        if parse_readoutmode is None:
            raise DetectorConfigError(f'Readout Mode "{self.readoutmode}" '
                                      f'is not CDS or MCDSn')
        else:
            nreads = int(parse_readoutmode.group(2))
            if nreads > 32:
                raise DetectorConfigError(f'MCDS{nreads} not supported '
                                          f'(only 1-16 are supported)')


##-------------------------------------------------------------------------
## MOSFIREInstrumentConfig
##-------------------------------------------------------------------------
class MOSFIREConfig(InstrumentConfig):
    '''An object to hold information about MOSFIRE configuration.
    '''
    def __init__(self, mode='spectroscopy', filter='Y', mask='longslit_46x0.7'):
        super().__init__()
        self.instrument = 'MOSFIRE'
        self.mode = mode
        self.filter = filter
        self.mask = mask
        self.arclamp = None
        self.domeflatlamp = None
        self.name = f'{self.mask} {self.filter}-{self.mode}'
        if self.arclamp is not None:
            self.name += f' arclamp={self.arclamp}'
        if self.domeflatlamp is not None:
            self.name += f' domeflatlamp={self.domeflatlamp}'


    ##-------------------------------------------------------------------------
    ## Validate
    def validate(self):
        '''Check values and verify that they meet assumptions.
        
        Check:
        
        Warn:
        '''
        pass


    def to_dict(self):
        output = super().to_dict()
        output['filter'] = self.filter
        output['mode'] = self.mode
        output['mask'] = self.mask
        output['arclamp'] = self.arclamp
        output['domeflatlamp'] = self.domeflatlamp
        return output


    def arcs(self, lampname):
        '''
        '''
        arcs = deepcopy(self)
        arcs.arclamp = lampname
        arcs.name += f' arclamp={arcs.arclamp}'
        return arcs


    def domeflats(self, off=False):
        '''
        '''
        domeflats = deepcopy(self)
        domeflats.domeflatlamp = not off
        domeflats.name += f' domeflatlamp={domeflats.domeflatlamp}'
        return domeflats


    def cals(self):
        '''
        '''
        mosfire_1s = MOSFIREDetectorConfig(exptime=1, readoutmode='CDS')
        mosfire_11s = MOSFIREDetectorConfig(exptime=11, readoutmode='CDS')

        cals = Sequence()
        cals.append(SequenceElement(pattern=Stare(),
                                    detconfig=mosfire_11s,
                                    instconfig=self.domeflats(),
                                    repeat=7))
        if self.filter == 'K':
            cals.append(SequenceElement(pattern=Stare(),
                                        detconfig=mosfire_11s,
                                        instconfig=self.domeflats(off=True),
                                        repeat=7))
            cals.append(SequenceElement(pattern=Stare(),
                                        detconfig=mosfire_1s,
                                        instconfig=self.arcs('Ne'),
                                        repeat=2))
            cals.append(SequenceElement(pattern=Stare(),
                                        detconfig=mosfire_1s,
                                        instconfig=self.arcs('Ar'),
                                        repeat=2))
        return cals


##-------------------------------------------------------------------------
## Offset Patterns
##-------------------------------------------------------------------------
class ABBA(OffsetPattern):
    def __init__(self, offset=2, guide=True):
        super().__init__()
        self.name = f'ABBA ({offset:.1f})'
        self.data = [TelescopeOffset(dx=0, dy=+offset, posname="A", guide=guide, frame=slit),
                     TelescopeOffset(dx=0, dy=-offset, posname="B", guide=guide, frame=slit),
                     TelescopeOffset(dx=0, dy=-offset, posname="B", guide=guide, frame=slit),
                     TelescopeOffset(dx=0, dy=+offset, posname="A", guide=guide, frame=slit),
                     ]


class Long2pos(OffsetPattern):
    '''Note that the offset values here are not correct.
    '''
    def __init__(self, guide=True):
        super().__init__()
        self.name = f'long2pos'
        self.data = [TelescopeOffset(dx=+45, dy=-23, posname="A", guide=guide, frame=detector),
                     TelescopeOffset(dx=+45, dy=-9,  posname="B", guide=guide, frame=detector),
                     TelescopeOffset(dx=-45, dy=+9,  posname="A", guide=guide, frame=detector),
                     TelescopeOffset(dx=-45, dy=+23, posname="B", guide=guide, frame=detector),
                     ]
