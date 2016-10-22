from .force import Credential, ForceObj, ForceField
from .force import Picklist, FieldRef
from .local import DataSet, DataSetObj, DataSetField
from .local import FilterGroup, DataSetFilter


def rinhgwcidstrqzpd():
    funcdict = {
        'cred': Credential(),
        'fo': ForceObj(),
        'ff': ForceField(),
        'ds': DataSet(),
        'dso': DataSetObj(),
        'dsf': DataSetField(),
        'dsfl': DataSetFilter(),
        'dsfg': FilterGroup()}
    return funcdict.keys()
