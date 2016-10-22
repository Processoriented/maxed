from django.db import models
from .force import Credential, ForceObj, ForceField

OPERATORS = (
    ('=', 'Equals'),
    ('!=', 'Not equal'),
    ('<', 'Less Than'),
    ('<=', 'Less than or equal'),
    ('>=', 'Greater than or equal'),
    ('>', 'Greater than'),
    ('StartsWith', 'Starts With'),
    ('Contains', 'Contains'),
    ('EndsWith', 'Ends With'),
)
GOPERATORS = (('AND', 'AND'), ('OR', 'OR'),)


def opsList():
    r = []
    for t in OPERATORS:
        r.append(t[0])
    return r


class DataSet(models.Model):
    name = models.CharField(max_length=40)
    credential = models.ForeignKey(Credential, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    def primary_object(self):
        pdso = self.datasetobj_set.filter(rel_pos=0)
        if (len(pdso) > 0):
            return pdso[0].forceobj
        else:
            return False

    def availobjs(self):
        for dso in self.datasetobj_set.all():
            dso.update_in_use()
        return self.datasetobj_set.filter(in_use=True).order_by('rel_pos')

    def fgroups(self):
        return self.filtergroup_set.all()


class DataSetObj(models.Model):
    dataset = models.ForeignKey(DataSet, on_delete=models.CASCADE)
    forceobj = models.ForeignKey(ForceObj, on_delete=models.CASCADE)
    rel_pos = models.IntegerField(default=0, editable=False)
    in_use = models.BooleanField(default=False)

    def __str__(self):
        return self.dataset.name + "." + self.forceobj.label

    def save(self, *args, **kwargs):
        while not (self.forceobj.has_description()):
            self.forceobj.get_description()
        super(DataSetObj, self).save(*args, **kwargs)
        if self.rel_pos < 3:
            for ff in self.forceobj.forcefield_set.all():
                self.datasetfield_set.get_or_create(forcefield=ff)

    def main_filter_group(self):
        fgmt = self.filtergroup_set.get_or_create(parent=None)
        return fgmt[0]

    def allfields(self):
        return self.datasetfield_set.all().order_by(
            'forcefield__label',
            'forcefield__name')

    def update_in_use(self):
        ct_shown = len(self.datasetfield_set.filter(hidden=False))
        ct_fltrd = len(self.filtergroup_set.all())
        iu = (ct_shown + ct_fltrd > 0) or (self.rel_pos == 0)
        if (self.in_use != iu):
            self.in_use = iu
            self.save()

    def fqueryText(self):
        fnames = []
        for dsf in self.datasetfield_set.filter(hidden=False):
            fnames.append(dsf.forcefield.name)

        if (len(fnames) == 0):
            fnames.append('count()')

        mfg = self.main_filter_group()
        wc = mfg.fgText()

        qt = "SELECT+" + ",".join(fnames) + "+FROM+" + self.forceobj.name + wc
        return qt


class DataSetField(models.Model):
    datasetobj = models.ForeignKey(DataSetObj, on_delete=models.CASCADE)
    forcefield = models.ForeignKey(ForceField, on_delete=models.CASCADE)
    hidden = models.BooleanField(default=True)

    def __str__(self):
        d = [
            self.datasetobj.dataset.name,
            self.datasetobj.forceobj.label,
            self.forcefield.label]
        return ".".join(d)

    def save(self, *args, **kwargs):
        super(DataSetField, self).save(*args, **kwargs)
        roqs = self.forcefield.fieldref_set.all()
        for ro in roqs:
            rp = self.datasetobj.rel_pos + 1
            self.datasetobj.dataset.datasetobj_set.get_or_create(
                forceobj=ro.forceobj,
                rel_pos=rp)

    def hbtext(self):
        return 'Show' if self.hidden else 'Hide'


class FilterGroup(models.Model):
    datasetobj = models.ForeignKey(DataSetObj, on_delete=models.CASCADE)
    operator = models.CharField(
        max_length=10,
        choices=GOPERATORS,
        default='AND')
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True)

    def fgText(self):
        fltrs = []
        for f in self.datasetfilter_set.all():
            fltrs.append(f.ftext())

        for g in self.filtergroup_set.all():
            fltrs.append('(' + g.fgText() + ')')

        rtn = ''
        if (len(fltrs) > 0):
            sep = "+" + self.operator + "+"
            t = sep.join(fltrs)
            rtn = '+WHERE+' + t

        return rtn

    def fltrs(self):
        return self.datasetfilter_set.all()


class DataSetFilter(models.Model):
    group = models.ForeignKey(
        FilterGroup,
        on_delete=models.CASCADE,
        null=True,
        blank=True)
    field = models.ForeignKey(DataSetField, on_delete=models.CASCADE)
    operator = models.CharField(
        max_length=10,
        choices=OPERATORS)
    value = models.CharField(max_length=255)

    unquotedTypes = [
        'xsd:boolean', 'xsd:decimal', 'xsd:double',
        'xsd:duration', 'xsd:float', 'xsd:gDay', 'xsd:gMonth',
        'xsd:gMonthDay', 'xsd:gYear', 'xsd:gYearMonth', 'xsd:int',
        'xsd:integer', 'xsd:long', 'xsd:negativeInteger',
        'xsd:nonNegativeInteger', 'xsd:nonPositiveInteger',
        'xsd:positiveInteger', 'xsd:short', 'xsd:unsignedInt',
        'xsd:unsignedLong', 'xsd:unsignedShort'
    ]

    def ftext(self):
        qv = "'" + self.value + "'"
        ut = self.field.forcefield.soapType in self.unquotedTypes
        fv = self.value if ut else qv
        d = [self.field.forcefield.name, self.operator, fv]
        return " ".join(d)

    def __str__(self):
        return self.ftext()

    def save(self, *args, **kwargs):
        if self.group is None:
            self.group = self.field.datasetobj.main_filter_group()
        super(DataSetFilter, self).save(*args, **kwargs)
