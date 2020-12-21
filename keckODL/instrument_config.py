#!python3

## Import General Tools
import re
from pathlib import Path
from astropy import units as u
import yaml


class InstrumentConfigError(Exception): pass


class InstrumentConfigWarning(UserWarning): pass


##-------------------------------------------------------------------------
## InstrumentConfig
##-------------------------------------------------------------------------
class InstrumentConfig():
    '''An object to hold information about an instrument configuration.
    '''
    def __init__(self, name='GenericInstrumentConfig'):
        self.name = name
        # Determine instrument from class name.  This is needed so the class
        # name and the instrument property have a predictable relationship
        namesearch = re.search("<class 'keckODL.(\w+).config.(\w+)Config'>",
                               str(self.__class__))
        self.package = namesearch.group(1)
        self.instrument = namesearch.group(2)


    def validate(self):
        pass


    def to_dict(self):
        return {'InstrumentConfigs': [{'name': self.name,
                                       'instrument': self.instrument,
                                       }]}


    def to_YAML(self):
        '''Return string corresponding to a Detector Config Description
        Language (DCDL) YAML entry.
        '''
        return yaml.dump(self.to_dict())


    def write(self, file):
        self.validate()
        p = Path(file).expanduser().absolute()
        if p.exists(): p.unlink()
        with open(p, 'w') as FO:
            FO.write(yaml.dump([self.to_dict()]))


    def arcs(self, lampname):
        '''This method should be overridden on each instrument to be the arcs
        configuration for the science config described.
        '''
        pass


    def domeflats(self, off=False):
        '''This method should be overridden on each instrument to be the dome
        flat configuration for the science config described.
        '''
        pass


    def __str__(self):
        return f'{self.name}'


    def __repr__(self):
        return f'{self.name}'


