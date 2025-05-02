from datetime import datetime

from django.db import models
from sfm.models import FinancialYear

FINYEAR_CHOICES = (
    ("2011/12", "2011/12"),
    ("2012/13", "2012/13"),
    ("2013/14", "2013/14"),
    ("2014/15", "2014/15"),
    ("2015/16", "2015/16"),
    ("2016/17", "2016/17"),
    ("2017/18", "2017/18"),
    ("2018/19", "2018/19"),
    ("2019/20", "2019/20"),
    ("2020/21", "2020/21"),
)


class IBMData(models.Model):
    """IBM data table stores IBMS related data that is being input through IBMS budget templates, Code Update templates
    and Data Amendment templates by end users.
    """

    ibmIdentifier = models.CharField(max_length=100, verbose_name="IBM identifer")

    fy = models.ForeignKey(FinancialYear, on_delete=models.PROTECT, verbose_name="financial year")
    costCentre = models.CharField(max_length=4, null=True, blank=True, db_index=True, verbose_name="cost centre")
    # regionBranch
    service = models.IntegerField(null=True, blank=True, db_index=True)
    project = models.CharField(max_length=6, null=True, blank=True)
    job = models.CharField(max_length=6, null=True, blank=True)
    budgetArea = models.CharField(max_length=100, db_index=True, verbose_name="budget area")
    projectSponsor = models.CharField(max_length=100, db_index=True, verbose_name="project sponsor")

    activity = models.CharField(max_length=4, null=True, blank=True)
    account = models.IntegerField(null=True, blank=True)
    regionalSpecificInfo = models.TextField(verbose_name="regional specific info")
    servicePriorityID = models.CharField(max_length=100, verbose_name="service priority ID")
    annualWPInfo = models.TextField(verbose_name="annual WP info")
    priorityActionNo = models.TextField(null=True, verbose_name="priority action no")
    priorityLevel = models.TextField(null=True, verbose_name="priority level")
    marineKPI = models.TextField(null=True, verbose_name="marine KPI")
    regionProject = models.TextField(null=True, verbose_name="region project")
    regionDescription = models.TextField(null=True, verbose_name="region description")

    def __str__(self):
        return f"{self.fy} {self.ibmIdentifier}"

    class Meta:
        # Financial year and ibmIdentifier should make a natural key for this model.
        unique_together = [("ibmIdentifier", "fy")]
        verbose_name = "IBM data"
        verbose_name_plural = "IBM data"

    def get_glpivdownload(self):
        """Returns a single matched GLPivDownload object, if it exists."""
        return GLPivDownload.objects.filter(codeID=self.ibmIdentifier).first() or None


class GLPivDownload(models.Model):
    """GLPivDownload source is from WebReporting data (Finance Service Branch).
    The link between IBMData to GLPivDownload is the codeID column ie. concatenate of CC-Account-Service-Activity-Project-Job.
    There are instances where a line transaction (IBM ID) in IBM data does not have a match with IBM ID in GLPivotDownload
    (as there isn't any transaction yet (no YTD actual/FY budget). It will come through later in the financial year.
    """

    fy = models.ForeignKey(
        FinancialYear, on_delete=models.PROTECT, blank=True, null=True, verbose_name="financial year"
    )
    costCentre = models.CharField(max_length=4, db_index=True, verbose_name="cost centre")
    regionBranch = models.CharField(max_length=100, db_index=True, verbose_name="region branch")
    service = models.IntegerField(db_index=True)
    project = models.CharField(max_length=6)
    job = models.CharField(max_length=6)

    download_period = models.DateField(blank=True, null=True)
    downloadPeriod = models.CharField(max_length=10)
    account = models.IntegerField(db_index=True)
    activity = models.CharField(max_length=4, db_index=True)
    resource = models.IntegerField(db_index=True)
    shortCode = models.CharField(max_length=20, verbose_name="short code")
    shortCodeName = models.CharField(max_length=200, verbose_name="short code name")
    gLCode = models.CharField(max_length=30, verbose_name="GL code")
    ptdActual = models.DecimalField(max_digits=14, decimal_places=2)
    ptdBudget = models.DecimalField(max_digits=14, decimal_places=2)
    ytdActual = models.DecimalField(max_digits=14, decimal_places=2)
    ytdBudget = models.DecimalField(max_digits=14, decimal_places=2)
    fybudget = models.DecimalField(max_digits=14, decimal_places=2)
    ytdVariance = models.DecimalField(max_digits=14, decimal_places=2)
    ccName = models.CharField(max_length=100, verbose_name="CC name")
    serviceName = models.CharField(max_length=100, verbose_name="service name")
    activityName = models.CharField(max_length=100, verbose_name="activity name")
    resourceName = models.CharField(max_length=100, verbose_name="resource name")
    projectName = models.CharField(max_length=100, verbose_name="project name")
    jobName = models.CharField(max_length=100, verbose_name="job name")
    codeID = models.CharField(
        max_length=30,
        db_index=True,
        verbose_name="code ID",
        help_text="This should match an IBMData object's IBMIdentifier field.",
    )
    resNameNo = models.CharField(max_length=100)
    actNameNo = models.CharField(max_length=100)
    projNameNo = models.CharField(max_length=100)
    division = models.CharField(max_length=100, db_index=True)
    resourceCategory = models.CharField(max_length=100, verbose_name="resource category")
    wildfire = models.CharField(max_length=30)
    expenseRevenue = models.CharField(max_length=7, verbose_name="expense revenue")
    fireActivities = models.CharField(max_length=50, verbose_name="fire activities")
    mPRACategory = models.CharField(max_length=100)

    ibmdata = models.ForeignKey(
        IBMData,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="glpivdownload",
    )

    class Meta:
        unique_together = [("gLCode", "fy")]
        verbose_name = "GL pivot download"
        verbose_name_plural = "GL pivot downloads"

    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        """Overide save() to parse string date to a Python date."""
        if self.downloadPeriod:
            self.download_period = datetime.strptime(self.downloadPeriod, "%d/%m/%Y")
        # Set a linked IBMData object, if present.
        if not self.ibmdata:
            self.ibmdata = self.get_ibmdata()
        super().save(force_insert, force_update)

    def get_ibmdata(self):
        """Returns a single matched IBMData object, if it exists."""
        return IBMData.objects.filter(ibmIdentifier=self.codeID).first() or None


class CorporateStrategy(models.Model):
    fy = models.ForeignKey(
        FinancialYear, on_delete=models.PROTECT, blank=True, null=True, verbose_name="financial year"
    )
    corporateStrategyNo = models.CharField(max_length=100, verbose_name="corporate strategy no")
    description1 = models.TextField(null=True)
    description2 = models.TextField(null=True)

    def __str__(self):
        # Truncate description text longer than 100 characters.
        if len(self.description1) <= 100:
            return self.description1
        else:
            desc_trunc = " ".join(self.description1[:101].split(" ")[0:-1])
            return "{} (...more...)".format(desc_trunc)

    class Meta:
        unique_together = [("corporateStrategyNo", "fy")]
        verbose_name_plural = "corporate strategies"


class ServicePriority(models.Model):
    """
    Abstract base class.
    """

    fy = models.ForeignKey(
        FinancialYear, on_delete=models.PROTECT, blank=True, null=True, verbose_name="financial year"
    )
    categoryID = models.CharField(max_length=100, null=True, blank=True, db_index=True, verbose_name="category ID")
    servicePriorityNo = models.CharField(
        max_length=100, null=False, default="-1", db_index=True, verbose_name="service priority no"
    )
    strategicPlanNo = models.CharField(max_length=100, null=True, blank=True, verbose_name="strategic plan no")
    corporateStrategyNo = models.CharField(max_length=100, null=True, blank=True, verbose_name="corporate strategy no")
    description = models.TextField(null=True)
    pvsExampleAnnWP = models.TextField()
    pvsExampleActNo = models.TextField()

    def __str__(self):
        return "{}: {}".format(self.pk, self.servicePriorityNo)

    class Meta:
        abstract = True
        unique_together = [("servicePriorityNo", "fy")]


class GeneralServicePriority(ServicePriority):
    description2 = models.TextField(null=True)

    class Meta:
        verbose_name_plural = "general service priorities"


class NCServicePriority(ServicePriority):
    assetNo = models.CharField(max_length=5, verbose_name="asset no")
    asset = models.TextField()
    targetNo = models.CharField(max_length=30, verbose_name="target no")
    target = models.TextField()
    actionNo = models.CharField(max_length=30, verbose_name="action no")
    action = models.TextField()
    mileNo = models.CharField(max_length=30, verbose_name="mile no")
    milestone = models.TextField()

    class Meta:
        unique_together = [("servicePriorityNo", "fy")]
        verbose_name = "NC service priority"
        verbose_name_plural = "NC service priorities"


class PVSServicePriority(ServicePriority):
    servicePriority1 = models.TextField(verbose_name="service priority 1")

    class Meta:
        verbose_name = "PVS service priority"
        verbose_name_plural = "PVS service priorities"


class SFMServicePriority(ServicePriority):
    regionBranch = models.CharField(max_length=20, verbose_name="region branch")
    description2 = models.TextField()

    class Meta:
        verbose_name = "SFM service priority"
        verbose_name_plural = "SFM service priorities"


class ERServicePriority(ServicePriority):
    classification = models.TextField()

    class Meta:
        verbose_name = "ER service priority"
        verbose_name_plural = "ER service priorities"


class NCStrategicPlan(models.Model):
    fy = models.ForeignKey(
        FinancialYear, on_delete=models.PROTECT, blank=True, null=True, verbose_name="financial year"
    )
    strategicPlanNo = models.CharField(max_length=100, verbose_name="strategic plan no")
    directionNo = models.CharField(max_length=100, verbose_name="direction no")
    direction = models.TextField()
    aimNo = models.CharField(max_length=100, verbose_name="aim no")
    aim1 = models.TextField()
    aim2 = models.TextField()
    actionNo = models.TextField(verbose_name="action no")
    action = models.TextField()

    class Meta:
        unique_together = [("strategicPlanNo", "fy")]
        verbose_name = "NC strategic plan"
        verbose_name_plural = "NC strategic plans"


class Outcomes(models.Model):
    fy = models.ForeignKey(
        FinancialYear, on_delete=models.PROTECT, blank=True, null=True, verbose_name="financial year"
    )
    q1Input = models.TextField()
    q2Input = models.TextField(blank=True)
    q3Input = models.TextField(blank=True)
    q4Input = models.TextField(blank=True)

    def __str__(self):
        return self.fy

    class Meta:
        verbose_name_plural = "outcomes"


class ServicePriorityMappings(models.Model):
    fy = models.ForeignKey(
        FinancialYear, on_delete=models.PROTECT, blank=True, null=True, verbose_name="financial year"
    )
    costCentreNo = models.CharField(max_length=4, verbose_name="cost centre no")
    wildlifeManagement = models.CharField(max_length=100, verbose_name="wildlife management")
    parksManagement = models.CharField(max_length=100, verbose_name="parks management")
    forestManagement = models.CharField(max_length=100, verbose_name="forest management")

    def __str__(self):
        return self.costCentreNo

    class Meta:
        verbose_name_plural = "Service Priority Mappings"
