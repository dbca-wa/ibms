from datetime import datetime
from django.conf import settings
from django.db import models
from sfm.models import FinancialYear


FINYEAR_CHOICES = (
    ('2011/12', '2011/12'),
    ('2012/13', '2012/13'),
    ('2013/14', '2013/14'),
    ('2014/15', '2014/15'),
    ('2015/16', '2015/16'),
    ('2016/17', '2016/17'),
    ('2017/18', '2017/18'),
    ('2018/19', '2018/19'),
    ('2019/20', '2019/20'),
    ('2020/21', '2020/21'),
)


class IBMData(models.Model):
    fy = models.ForeignKey(FinancialYear, on_delete=models.PROTECT, blank=True, null=True)
    ibmIdentifier = models.CharField(
        max_length=100,
        verbose_name='IBMId',
        help_text='IBM Identifier')
    budgetArea = models.CharField(max_length=100, db_index=True)
    projectSponsor = models.CharField(max_length=100, db_index=True)
    corporatePlanNo = models.CharField(max_length=100, db_index=True)
    strategicPlanNo = models.CharField(max_length=100, db_index=True)
    regionalSpecificInfo = models.TextField()
    servicePriorityID = models.CharField(max_length=100)
    annualWPInfo = models.TextField()
    costCentre = models.CharField(max_length=4, null=True, blank=True, db_index=True)
    account = models.IntegerField(null=True, blank=True)
    service = models.IntegerField(null=True, blank=True, db_index=True)
    activity = models.CharField(max_length=4, null=True, blank=True)
    project = models.CharField(max_length=6, null=True, blank=True)
    job = models.CharField(max_length=6, null=True, blank=True)

    def __str__(self):
        return self.ibmIdentifier

    class Meta:
        unique_together = [('ibmIdentifier', 'fy')]
        verbose_name = 'IBM data'
        verbose_name_plural = 'IBM data'


class GLPivDownload(models.Model):
    fy = models.ForeignKey(FinancialYear, on_delete=models.PROTECT, blank=True, null=True)
    download_period = models.DateField(blank=True, null=True)
    downloadPeriod = models.CharField(max_length=10)
    costCentre = models.CharField(max_length=4, db_index=True)
    account = models.IntegerField(db_index=True)
    service = models.IntegerField(db_index=True)
    activity = models.CharField(max_length=4, db_index=True)
    resource = models.IntegerField(db_index=True)
    project = models.CharField(max_length=6)
    job = models.CharField(max_length=6)
    shortCode = models.CharField(max_length=20)
    shortCodeName = models.CharField(max_length=200)
    gLCode = models.CharField(max_length=30)
    ptdActual = models.DecimalField(max_digits=10, decimal_places=2)
    ptdBudget = models.DecimalField(max_digits=10, decimal_places=2)
    ytdActual = models.DecimalField(max_digits=10, decimal_places=2)
    ytdBudget = models.DecimalField(max_digits=10, decimal_places=2)
    fybudget = models.DecimalField(max_digits=12, decimal_places=2)
    ytdVariance = models.DecimalField(max_digits=10, decimal_places=2)
    ccName = models.CharField(max_length=100)
    serviceName = models.CharField(max_length=100)
    activityName = models.CharField(max_length=100)
    resourceName = models.CharField(max_length=100)
    projectName = models.CharField(max_length=100)
    jobName = models.CharField(max_length=100)
    codeID = models.CharField(
        max_length=30, db_index=True,
        help_text="This should match an IBMData object's IBMIdentifier field.")
    resNameNo = models.CharField(max_length=100)
    actNameNo = models.CharField(max_length=100)
    projNameNo = models.CharField(max_length=100)
    regionBranch = models.CharField(max_length=100, db_index=True)
    division = models.CharField(max_length=100, db_index=True)
    resourceCategory = models.CharField(max_length=100)
    wildfire = models.CharField(max_length=30)
    expenseRevenue = models.CharField(max_length=7)
    fireActivities = models.CharField(max_length=50)
    mPRACategory = models.CharField(max_length=100)

    class Meta:
        unique_together = [('gLCode', 'fy')]
        verbose_name = 'GL pivot download'
        verbose_name_plural = 'GL pivot downloads'

    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        """Overide save() to parse string date to a Python date.
        """
        if self.downloadPeriod:
            self.download_period = datetime.strptime(self.downloadPeriod, "%d/%m/%Y")
        super().save(force_insert, force_update)


class CorporateStrategy(models.Model):
    fy = models.ForeignKey(FinancialYear, on_delete=models.PROTECT, blank=True, null=True)
    corporateStrategyNo = models.CharField(max_length=100)
    description1 = models.TextField(null=True)
    description2 = models.TextField(null=True)

    def __str__(self):
        # Truncate description text longer than 100 characters.
        if len(self.description1) <= 100:
            return self.description1
        else:
            desc_trunc = ' '.join(self.description1[:101].split(' ')[0:-1])
            return '{0} (...more...)'.format(desc_trunc)

    class Meta:
        unique_together = [('corporateStrategyNo', 'fy')]
        verbose_name_plural = 'corporate strategies'


class ServicePriority(models.Model):
    """
    Abstract base class.
    """
    fy = models.ForeignKey(FinancialYear, on_delete=models.PROTECT, blank=True, null=True)
    categoryID = models.CharField(max_length=100, null=True, blank=True, db_index=True)
    servicePriorityNo = models.CharField(max_length=100, null=False, default='-1', db_index=True)
    strategicPlanNo = models.CharField(max_length=100, null=True, blank=True)
    corporateStrategyNo = models.CharField(
        max_length=100,
        null=True,
        blank=True)
    description = models.TextField(null=True)
    pvsExampleAnnWP = models.TextField()
    pvsExampleActNo = models.TextField()

    def __str__(self):
        return '{0}: {1}'.format(self.pk, self.servicePriorityNo)

    class Meta:
        abstract = True
        unique_together = [('servicePriorityNo', 'fy')]


class GeneralServicePriority(ServicePriority):
    description2 = models.TextField(null=True)

    class Meta:
        verbose_name_plural = 'general service priorities'


class NCServicePriority(ServicePriority):
    assetNo = models.CharField(max_length=5)
    asset = models.TextField()
    targetNo = models.CharField(max_length=30)
    target = models.TextField()
    actionNo = models.CharField(max_length=30)
    action = models.TextField()
    mileNo = models.CharField(max_length=30)
    milestone = models.TextField()

    class Meta:
        unique_together = [('servicePriorityNo', 'fy')]
        verbose_name = 'NC service priority'
        verbose_name_plural = 'NC service priorities'


class PVSServicePriority(ServicePriority):
    servicePriority1 = models.TextField()

    class Meta:
        verbose_name = 'PVS service priority'
        verbose_name_plural = 'PVS service priorities'


class SFMServicePriority(ServicePriority):
    regionBranch = models.CharField(max_length=20)
    description2 = models.TextField()

    class Meta:
        verbose_name = 'SFM service priority'
        verbose_name_plural = 'SFM service priorities'


class ERServicePriority(ServicePriority):
    classification = models.TextField()

    class Meta:
        verbose_name = 'ER service priority'
        verbose_name_plural = 'ER service priorities'


class NCStrategicPlan(models.Model):
    fy = models.ForeignKey(FinancialYear, on_delete=models.PROTECT, blank=True, null=True)
    strategicPlanNo = models.CharField(max_length=100)
    directionNo = models.CharField(max_length=100)
    direction = models.TextField()
    AimNo = models.CharField(max_length=100)
    Aim1 = models.TextField()
    Aim2 = models.TextField()
    ActionNo = models.TextField()
    Action = models.TextField()

    class Meta:
        unique_together = [('strategicPlanNo', 'fy')]
        verbose_name = 'NC strategic plan'
        verbose_name_plural = 'NC strategic plans'


class Outcomes(models.Model):
    fy = models.ForeignKey(FinancialYear, on_delete=models.PROTECT, blank=True, null=True)
    q1Input = models.TextField()
    q2Input = models.TextField(blank=True)
    q3Input = models.TextField(blank=True)
    q4Input = models.TextField(blank=True)

    def __str__(self):
        return self.fy

    class Meta:
        verbose_name_plural = 'outcomes'

class ServicePriorityMappings(models.Model):
    fy = models.ForeignKey(FinancialYear, on_delete=models.PROTECT, blank=True, null=True)
    costCentreNo = models.CharField(max_length=4)
    wildlifeManagement = models.CharField(max_length=100)
    parksManagement = models.CharField(max_length=100)
    forestManagement = models.CharField(max_length=100)

    def __str__(self):
        return self.costCentreNo

    class Meta:
        verbose_name_plural = 'Service Priority Mappings'
