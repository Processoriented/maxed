from django.db import models
from django.utils import timezone
import requests


class Credential(models.Model):
    user_id = models.EmailField(max_length=80)
    password = models.CharField(max_length=80)
    user_token = models.CharField(max_length=80)
    consumer_key = models.CharField(max_length=120)
    consumer_secret = models.CharField(max_length=120)
    request_token_url = models.CharField(
        max_length=255,
        default='https://login.salesforce.com/services/oauth2/token')
    access_token_url = models.CharField(
        max_length=255,
        default='https://login.salesforce.com/services/oauth2/token')
    # http://PITC-Zscaler-US-MilwaukeeZ.proxy.corporate.ge.com:9400
    http_proxy = models.CharField(
        max_length=255,
        null=True,
        blank=True)
    # https://PITC-Zscaler-US-MilwaukeeZ.proxy.corporate.ge.com:9400
    https_proxy = models.CharField(
        max_length=255,
        null=True,
        blank=True)
    object_refresh_date = models.DateTimeField(
        'objects refreshed',
        null=True,
        editable=False)
    conn = None

    def __str__(self):
        return self.user_id

    def proxies(self):
        d = {}
        if self.http_proxy:
            d['http'] = self.http_proxy
        if self.https_proxy:
            d['https'] = self.https_proxy
        return d

    def create_connection(self):
        data = {
            'grant_type': 'password',
            'client_id': self.consumer_key,
            'client_secret': self.consumer_secret,
            'username': self.user_id,
            'password': self.password
        }
        headers = {
            'content-type': 'application/x-www-form-urlencoded'
        }
        req = requests.post(
            self.access_token_url,
            data=data,
            headers=headers,
            proxies=self.proxies())
        self.conn = req.json()
        return req.json()

    def test_connection(self):
        if self.conn:
            tstHdr = {
                'Authorization': 'Bearer ' + self.conn['access_token']
            }
            tstUrl = self.conn['instance_url']
            tstUrl = tstUrl + '/services/data/v37.0/sobjects'
            tst = requests.get(tstUrl, headers=tstHdr, proxies=self.proxies())
            return (tst.status_code == 200)

        return False

    def get_connection(self):
        if not self.test_connection():
            return self.create_connection()
        else:
            return self.conn

    def get_data(self, apiFunction):
        c = self.get_connection()
        hdr = {
            'Authorization': 'Bearer ' + c['access_token']
        }
        url = c['instance_url'] + '/services/data/v37.0/' + apiFunction
        r = requests.get(url, headers=hdr, proxies=self.proxies())
        return r.json()

    def get_objects(self, reset=False):
        d = self.get_data('sobjects')
        for so in d['sobjects']:
            ins = (so['queryable'] is True)
            ins = ins and (len(self.forceobj_set.filter(name=so['name'])) == 0)
            if (ins or reset):
                self.forceobj_set.update_or_create(
                    activateable=so['activateable'],
                    createable=so['createable'],
                    custom=so['custom'],
                    customSetting=so['customSetting'],
                    deletable=so['deletable'],
                    deprecatedAndHidden=so['deprecatedAndHidden'],
                    feedEnabled=so['feedEnabled'],
                    keyPrefix=so['keyPrefix'],
                    label=so['label'],
                    labelPlural=so['labelPlural'],
                    layoutable=so['layoutable'],
                    mergeable=so['mergeable'],
                    mruEnabled=so['mruEnabled'],
                    name=so['name'],
                    queryable=so['queryable'],
                    replicateable=so['replicateable'],
                    retrieveable=so['retrieveable'],
                    searchable=so['searchable'],
                    triggerable=so['triggerable'],
                    undeletable=so['undeletable'],
                    updateable=so['updateable']
                    )
                self.object_refresh_date = timezone.now()

    def has_objects(self):
        return (len(self.forceobj_set.all()) > 0)
    has_objects.admin_order_field = 'object_refresh_date'
    has_objects.boolean = True
    has_objects.short_description = 'Objects Populated?'


class ForceObj(models.Model):
    name = models.CharField(max_length=80, unique=True)
    label = models.CharField(max_length=80)
    credential = models.ForeignKey(Credential, on_delete=models.CASCADE)
    activateable = models.BooleanField(default=False)
    createable = models.BooleanField(default=False)
    custom = models.BooleanField(default=False)
    customSetting = models.BooleanField(default=False)
    deletable = models.BooleanField(default=False)
    deprecatedAndHidden = models.BooleanField(default=False)
    feedEnabled = models.BooleanField(default=False)
    keyPrefix = models.CharField(max_length=20, null=True, blank=True)
    labelPlural = models.CharField(max_length=80, null=True, blank=True)
    layoutable = models.BooleanField(default=False)
    mergeable = models.BooleanField(default=False)
    mruEnabled = models.BooleanField(default=False)
    queryable = models.BooleanField(default=False)
    replicateable = models.BooleanField(default=False)
    retrieveable = models.BooleanField(default=False)
    searchable = models.BooleanField(default=False)
    triggerable = models.BooleanField(default=False)
    undeletable = models.BooleanField(default=False)
    updateable = models.BooleanField(default=False)
    commonly_used = models.BooleanField(default=False)
    description_refresh_date = models.DateTimeField(
        'description refreshed',
        null=True,
        editable=False)

    def __str__(self):
        return self.label

    def get_description(self):
        d = self.credential.get_data('sobjects/' + self.name + '/describe')
        for f in d['fields']:
            fft = self.forcefield_set.update_or_create(
                aggregatable=f['aggregatable'],
                autoNumber=f['autoNumber'],
                byteLength=f['byteLength'],
                calculated=f['calculated'],
                calculatedFormula=f['calculatedFormula'],
                cascadeDelete=f['cascadeDelete'],
                caseSensitive=f['caseSensitive'],
                controllerName=f['controllerName'],
                createable=f['createable'],
                custom=f['custom'],
                defaultValue=f['defaultValue'],
                defaultValueFormula=f['defaultValueFormula'],
                defaultedOnCreate=f['defaultedOnCreate'],
                dependentPicklist=f['dependentPicklist'],
                deprecatedAndHidden=f['deprecatedAndHidden'],
                digits=f['digits'],
                displayLocationInDecimal=f['displayLocationInDecimal'],
                encrypted=f['encrypted'],
                externalId=f['externalId'],
                extraTypeInfo=f['extraTypeInfo'],
                filterable=f['filterable'],
                filteredLookupInfo=f['filteredLookupInfo'],
                groupable=f['groupable'],
                highScaleNumber=f['highScaleNumber'],
                htmlFormatted=f['htmlFormatted'],
                idLookup=f['idLookup'],
                inlineHelpText=f['inlineHelpText'],
                label=f['label'],
                length=f['length'],
                mask=f['mask'],
                maskType=f['maskType'],
                name=f['name'],
                nameField=f['nameField'],
                namePointing=f['namePointing'],
                nillable=f['nillable'],
                permissionable=f['permissionable'],
                precision=f['precision'],
                queryByDistance=f['queryByDistance'],
                referenceTargetField=f['referenceTargetField'],
                relationshipName=f['relationshipName'],
                relationshipOrder=f['relationshipOrder'],
                restrictedDelete=f['restrictedDelete'],
                restrictedPicklist=f['restrictedPicklist'],
                scale=f['scale'],
                soapType=f['soapType'],
                sortable=f['sortable'],
                fftype=f['type'],
                unique=f['unique'],
                updateable=f['updateable'],
                writeRequiresMasterRead=f['writeRequiresMasterRead'])
            self.description_refresh_date = timezone.now()
            ff = fft[0]
            for p in f['picklistValues']:
                ff.picklist_set.update_or_create(
                    active=p['active'],
                    defaultValue=p['defaultValue'],
                    label=p['label'],
                    validFor=p['validFor'],
                    value=p['value'])
            for r in f['referenceTo']:
                ro = ForceObj.objects.filter(name=r)
                if (len(ro) > 0):
                    robj = ro[0]
                    ff.fieldref_set.update_or_create(forceobj=robj)

    def has_description(self):
        return (len(self.forcefield_set.all()) != 0)
    has_description.boolean = True
    has_description.short_description = 'Description Populated?'


class ForceField(models.Model):
    aggregatable = models.BooleanField(default=False)
    autoNumber = models.BooleanField(default=False)
    byteLength = models.IntegerField(null=True, blank=True)
    calculated = models.BooleanField(default=False)
    calculatedFormula = models.CharField(null=True, blank=True, max_length=255)
    cascadeDelete = models.BooleanField(default=False)
    caseSensitive = models.BooleanField(default=False)
    controllerName = models.CharField(null=True, blank=True, max_length=40)
    createable = models.BooleanField(default=False)
    custom = models.BooleanField(default=False)
    defaultValue = models.CharField(null=True, blank=True, max_length=40)
    defaultValueFormula = models.CharField(
        null=True,
        blank=True,
        max_length=40)
    defaultedOnCreate = models.BooleanField(default=False)
    dependentPicklist = models.BooleanField(default=False)
    deprecatedAndHidden = models.BooleanField(default=False)
    digits = models.IntegerField(null=True, blank=True)
    displayLocationInDecimal = models.BooleanField(default=False)
    encrypted = models.BooleanField(default=False)
    externalId = models.BooleanField(default=False)
    extraTypeInfo = models.CharField(null=True, blank=True, max_length=40)
    filterable = models.BooleanField(default=False)
    filteredLookupInfo = models.CharField(null=True, blank=True, max_length=40)
    groupable = models.BooleanField(default=False)
    highScaleNumber = models.BooleanField(default=False)
    htmlFormatted = models.BooleanField(default=False)
    idLookup = models.BooleanField(default=False)
    inlineHelpText = models.CharField(null=True, blank=True, max_length=255)
    label = models.CharField(max_length=40)
    length = models.IntegerField(null=True, blank=True)
    mask = models.CharField(null=True, blank=True, max_length=40)
    maskType = models.CharField(null=True, blank=True, max_length=40)
    name = models.CharField(max_length=40)
    nameField = models.BooleanField(default=False)
    namePointing = models.BooleanField(default=False)
    nillable = models.BooleanField(default=False)
    permissionable = models.BooleanField(default=False)
    precision = models.IntegerField(null=True, blank=True)
    queryByDistance = models.BooleanField(default=False)
    referenceTargetField = models.CharField(
        null=True,
        blank=True,
        max_length=40)
    relationshipName = models.CharField(null=True, blank=True, max_length=40)
    relationshipOrder = models.CharField(null=True, blank=True, max_length=40)
    restrictedDelete = models.BooleanField(default=False)
    restrictedPicklist = models.BooleanField(default=False)
    scale = models.IntegerField(null=True, blank=True)
    soapType = models.CharField(max_length=40)
    sortable = models.BooleanField(default=False)
    fftype = models.CharField(max_length=40)
    unique = models.BooleanField(default=False)
    updateable = models.BooleanField(default=False)
    writeRequiresMasterRead = models.BooleanField(default=False)
    forceobj = models.ForeignKey(ForceObj, on_delete=models.CASCADE)
    commonly_used = models.BooleanField(default=False)

    def __str__(self):
        return self.label


class Picklist(models.Model):
    active = models.BooleanField(default=False)
    defaultValue = models.BooleanField(default=False)
    label = models.CharField(max_length=40)
    validFor = models.CharField(max_length=40, null=True, blank=True)
    value = models.CharField(max_length=40)
    field = models.ForeignKey(ForceField, on_delete=models.CASCADE)

    def __str__(self):
        return self.label


class FieldRef(models.Model):
    field = models.ForeignKey(ForceField, on_delete=models.CASCADE)
    forceobj = models.ForeignKey(ForceObj, on_delete=models.CASCADE)

    def __str__(self):
        return self.forceobj.label


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
        return self.datasetobj_set.all().order_by('rel_pos')


class DataSetObj(models.Model):
    dataset = models.ForeignKey(DataSet, on_delete=models.CASCADE)
    forceobj = models.ForeignKey(ForceObj, on_delete=models.CASCADE)
    rel_pos = models.IntegerField(default=0, editable=False)

    def __str__(self):
        return self.dataset.name + "." + self.forceobj.label


class DataSetField(models.Model):
    datasetobj = models.ForeignKey(DataSetObj, on_delete=models.CASCADE)
    forcefield = models.ForeignKey(ForceField, on_delete=models.CASCADE)
    hidden = models.BooleanField(default=False)

    def __str__(self):
        d = [
            self.datasetobj.dataset.name,
            self.datasetobj.forceobj.label,
            self.forcefield.label]
        return ".".join(d)

    def save(self, *args, **kwargs):
        super(DataSetField, self).save(*args, **kwargs)
        roqs = self.fieldref_set.all()
        for ro in roqs:
            rp = self.datasetobj.rel_pos + 1
            self.datasetobj.dataset.datasetobj_set.get_or_create(
                forceobj=ro.forceobj,
                rel_pos=rp)


class FilterGroup(models.Model):
    OPERATORS = (('AND', 'AND'), ('OR', 'OR'),)
    datasetobj = models.ForeignKey(DataSetObj, on_delete=models.CASCADE)
    operator = models.CharField(max_length=10, choices=OPERATORS)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True)


class DataSetFilter(models.Model):
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
    group = models.ForeignKey(FilterGroup, on_delete=models.CASCADE)
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

    def __str__(self):
        qv = "'" + self.value + "'"
        ut = self.field.forcefield.soapType in self.unquotedTypes
        fv = self.value if ut else qv
        d = [self.field.forcefield.name, self.operator, fv]
        return " ".join(d)
