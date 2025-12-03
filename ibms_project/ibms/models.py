from datetime import datetime

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.urls import reverse
from sfm.models import FinancialYear

from ibms_project.middleware import get_current_user

User = get_user_model()


class IBMData(models.Model):
    """IBM data table stores IBMS related data that is being input through IBMS budget templates, Code Update templates
    and Data Amendment templates by end users.
    """

    ibmIdentifier = models.CharField(max_length=100, verbose_name="IBM identifier", db_index=True)

    fy = models.ForeignKey(FinancialYear, on_delete=models.PROTECT, verbose_name="financial year")
    costCentre = models.CharField(max_length=4, null=True, blank=True, db_index=True, verbose_name="cost centre")

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

    # Audit fields
    modifier = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        blank=True,
        null=True,
        related_name="ibms_ibmdata_modifier",
        editable=False,
        verbose_name="last modified by",
    )
    modified = models.DateTimeField(null=True, blank=True, auto_now=True, editable=False, verbose_name="last modified")

    # Generic relationship to Service Priority model classes.
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True, editable=False)
    object_id = models.PositiveBigIntegerField(null=True, blank=True, editable=False)
    service_priority = GenericForeignKey("content_type", "object_id")

    class Meta:
        unique_together = [("ibmIdentifier", "fy")]
        verbose_name = "IBM data"
        verbose_name_plural = "IBM data"
        indexes = [models.Index(fields=["content_type", "object_id"])]

    def __str__(self):
        return f"{self.fy} {self.ibmIdentifier}"

    def save(self, *args, **kwargs):
        user = get_current_user()
        if user:
            self.modifier = user

        if self.pk and not self.service_priority:
            sp = self.get_service_priority()
            if sp:
                self.content_type = ContentType.objects.get_for_model(sp._meta.model)
                self.object_id = sp.pk
            else:
                self.content_type = None
                self.object_id = None

        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("ibms:data_amendment_update", kwargs={"pk": self.pk})

    def get_service_priority(self):
        """Return any matching SP object among the subclasses of ServicePriority."""
        if GeneralServicePriority.objects.filter(fy=self.fy, servicePriorityNo=self.servicePriorityID).exists():
            return GeneralServicePriority.objects.get(fy=self.fy, servicePriorityNo=self.servicePriorityID)
        elif NCServicePriority.objects.filter(fy=self.fy, servicePriorityNo=self.servicePriorityID).exists():
            return NCServicePriority.objects.get(fy=self.fy, servicePriorityNo=self.servicePriorityID)
        elif PVSServicePriority.objects.filter(fy=self.fy, servicePriorityNo=self.servicePriorityID).exists():
            return PVSServicePriority.objects.get(fy=self.fy, servicePriorityNo=self.servicePriorityID)
        elif SFMServicePriority.objects.filter(fy=self.fy, servicePriorityNo=self.servicePriorityID).exists():
            return SFMServicePriority.objects.get(fy=self.fy, servicePriorityNo=self.servicePriorityID)
        elif ERServicePriority.objects.filter(fy=self.fy, servicePriorityNo=self.servicePriorityID).exists():
            return ERServicePriority.objects.get(fy=self.fy, servicePriorityNo=self.servicePriorityID)

        return None

    def get_account_display(self) -> str:
        """The account display value should be returned as a string (integer, left-padded with zeros)."""
        if self.account:
            return str(self.account).zfill(2)
        else:
            return ""

    def get_service_display(self) -> str:
        """The service display value should be returned as a string (integer, left-padded with zeros)."""
        if self.service:
            return str(self.service).zfill(2)
        else:
            return ""

    def get_project_display(self) -> str:
        """The project display value should be returned as a string (integer, left-padded with zeros)."""
        if self.project:
            return str(self.project).zfill(4)
        else:
            return ""

    def get_region_branch(self) -> str:
        """This value belongs to linked GLPivDownload objects."""
        if self.glpivdownload.exists():
            return str(self.glpivdownload.first().regionBranch)
        else:
            return ""


class DepartmentProgram(models.Model):
    fy = models.ForeignKey(FinancialYear, on_delete=models.PROTECT, verbose_name="financial year")
    ibmIdentifier = models.CharField(max_length=100, verbose_name="IBM identifer", db_index=True)
    dept_program1 = models.CharField(max_length=500, verbose_name="department program 1", null=True, blank=True)
    dept_program2 = models.CharField(max_length=500, verbose_name="department program 2", null=True, blank=True)
    dept_program3 = models.CharField(max_length=500, verbose_name="department program 3", null=True, blank=True)

    class Meta:
        unique_together = [("ibmIdentifier", "fy")]

    def __str__(self):
        return f"{self.fy} {self.dept_program1}"


class GLPivDownload(models.Model):
    """GLPivDownload source is from WebReporting data (Finance Service Branch).
    The link between IBMData to GLPivDownload is the codeID column ie. concatenate of CC-Account-Service-Activity-Project-Job.
    There are instances where a line transaction (IBM ID) in IBM data does not have a match with IBM ID in GLPivotDownload
    (as there isn't any transaction yet (no YTD actual/FY budget). It will come through later in the financial year.

    NOTE: data in this model is not intended to be user-editable, but will always be sourced externally.
    """

    fy = models.ForeignKey(FinancialYear, on_delete=models.PROTECT, verbose_name="financial year", editable=False)
    costCentre = models.CharField(max_length=4, db_index=True, verbose_name="cost centre", editable=False)
    regionBranch = models.CharField(max_length=100, db_index=True, verbose_name="region branch", editable=False)
    service = models.IntegerField(db_index=True, editable=False)
    project = models.CharField(max_length=6, editable=False)
    job = models.CharField(max_length=6, editable=False)

    download_period = models.DateField(blank=True, null=True, editable=False)
    downloadPeriod = models.CharField(max_length=10, editable=False)
    account = models.IntegerField(db_index=True, editable=False)
    activity = models.CharField(max_length=4, db_index=True, editable=False)
    resource = models.IntegerField(db_index=True, editable=False)
    shortCode = models.CharField(max_length=20, verbose_name="short code", editable=False)
    shortCodeName = models.CharField(max_length=200, verbose_name="short code name", editable=False)
    gLCode = models.CharField(max_length=30, verbose_name="GL code", editable=False)
    ptdActual = models.DecimalField(max_digits=14, decimal_places=2, editable=False)
    ptdBudget = models.DecimalField(max_digits=14, decimal_places=2, editable=False)
    ytdActual = models.DecimalField(max_digits=14, decimal_places=2, editable=False)
    ytdBudget = models.DecimalField(max_digits=14, decimal_places=2, editable=False)
    fybudget = models.DecimalField(max_digits=14, decimal_places=2, editable=False)
    ytdVariance = models.DecimalField(max_digits=14, decimal_places=2, editable=False)
    ccName = models.CharField(max_length=100, verbose_name="CC name", editable=False)
    serviceName = models.CharField(max_length=100, verbose_name="service name", editable=False)
    activityName = models.CharField(max_length=100, verbose_name="activity name", editable=False)
    resourceName = models.CharField(max_length=100, verbose_name="resource name", editable=False)
    projectName = models.CharField(max_length=100, verbose_name="project name", editable=False)
    jobName = models.CharField(max_length=100, verbose_name="job name", editable=False)
    codeID = models.CharField(
        max_length=30,
        db_index=True,
        verbose_name="code ID",
        help_text="This should match an IBMData object's IBMIdentifier field.",
        editable=False,
    )
    resNameNo = models.CharField(max_length=100, editable=False)
    actNameNo = models.CharField(max_length=100, editable=False)
    projNameNo = models.CharField(max_length=100, editable=False)
    division = models.CharField(max_length=100, db_index=True, editable=False)
    resourceCategory = models.CharField(max_length=100, verbose_name="resource category", editable=False)
    wildfire = models.CharField(max_length=30, editable=False)
    expenseRevenue = models.CharField(max_length=7, verbose_name="expense revenue", editable=False)
    fireActivities = models.CharField(max_length=50, verbose_name="fire activities", editable=False)
    mPRACategory = models.CharField(max_length=100, editable=False)

    ibmdata = models.ForeignKey(
        IBMData,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="glpivdownload",
        verbose_name="IBM data",
        editable=False,
    )
    department_program = models.ForeignKey(
        DepartmentProgram,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="glpivdownload",
        editable=False,
    )

    class Meta:
        unique_together = [("gLCode", "fy")]
        verbose_name = "GL pivot download"
        verbose_name_plural = "GL pivot downloads"

    def __str__(self):
        return f"{self.fy} {self.gLCode}"

    def save(self, *args, **kwargs):
        """Overide save() to parse string date to a Python date."""
        if self.downloadPeriod:
            self.download_period = datetime.strptime(self.downloadPeriod, "%d/%m/%Y")
        # Set a linked IBMData object, if present.
        if not self.ibmdata:
            self.ibmdata = self.get_ibmdata()
        # Set a linked DepartmentProgram object, if present.
        if not self.department_program:
            self.department_program = self.get_department_program()
        super().save(*args, **kwargs)

    def get_ibmdata(self) -> IBMData | None:
        """Returns a single matched IBMData object, if it exists."""
        if IBMData.objects.filter(fy=self.fy, ibmIdentifier=self.codeID).exists():
            return IBMData.objects.get(fy=self.fy, ibmIdentifier=self.codeID)
        return None

    def get_department_program(self) -> DepartmentProgram | None:
        """Returns a single matched DepartmentProgram object, if it exists."""
        if DepartmentProgram.objects.filter(fy=self.fy, ibmIdentifier=self.codeID).exists():
            return DepartmentProgram.objects.get(fy=self.fy, ibmIdentifier=self.codeID)
        return None

    def get_account_display(self) -> str:
        """The account display value should be returned as a string (integer, left-padded with zeros)."""
        return str(self.account).zfill(2)

    def get_project_display(self) -> str:
        """The project display value should be returned as a string (integer, left-padded with zeros)."""
        if self.project:
            return str(self.project).zfill(4)
        else:
            return ""


class CorporateStrategy(models.Model):
    fy = models.ForeignKey(FinancialYear, on_delete=models.PROTECT, verbose_name="financial year")
    corporateStrategyNo = models.CharField(max_length=100, verbose_name="corporate strategy no")
    description1 = models.TextField(null=True)
    description2 = models.TextField(null=True)

    def __str__(self):
        return f"{self.fy} {self.corporateStrategyNo}"

    class Meta:
        unique_together = [("corporateStrategyNo", "fy")]
        verbose_name_plural = "corporate strategies"


class NCStrategicPlan(models.Model):
    """Notwithstanding the name of this model, all subclasses of ServicePriority may link to it."""

    fy = models.ForeignKey(FinancialYear, on_delete=models.PROTECT, verbose_name="financial year")
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

    def __str__(self):
        return f"{self.fy} {self.strategicPlanNo}"


class ServicePriority(models.Model):
    """
    Abstract base class.
    """

    fy = models.ForeignKey(FinancialYear, on_delete=models.PROTECT, verbose_name="financial year")
    categoryID = models.CharField(max_length=100, null=True, blank=True, db_index=True, verbose_name="category ID")
    servicePriorityNo = models.CharField(max_length=100, null=False, default="-1", db_index=True, verbose_name="service priority no")
    strategicPlanNo = models.CharField(max_length=100, null=True, blank=True, verbose_name="strategic plan no")
    corporateStrategyNo = models.CharField(max_length=100, null=True, blank=True, verbose_name="corporate strategy no")
    description = models.TextField(null=True)
    pvsExampleAnnWP = models.TextField()
    pvsExampleActNo = models.TextField()

    corporate_strategy = models.ForeignKey(
        CorporateStrategy,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        editable=False,
    )
    strategic_plan = models.ForeignKey(
        NCStrategicPlan,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        editable=False,
    )

    class Meta:
        abstract = True
        unique_together = [("servicePriorityNo", "fy")]

    def __str__(self):
        return f"{self.fy} {self.servicePriorityNo}"

    def save(self, *args, **kwargs):
        """Overide save() to parse string date to a Python date."""
        # Set a linked CorporateStrategy object, if present.
        if not self.corporate_strategy:
            self.corporate_strategy = self.get_corporate_strategy()
        # Set a linked NCStrategicPlan object, if present.
        if not self.strategic_plan:
            self.strategic_plan = self.get_strategic_plan()
        super().save(*args, **kwargs)

    def get_corporate_strategy(self) -> CorporateStrategy | None:
        """Returns a single matched CorporateStrategy object, if it exists."""
        if CorporateStrategy.objects.filter(fy=self.fy, corporateStrategyNo=self.corporateStrategyNo).exists():
            return CorporateStrategy.objects.get(fy=self.fy, corporateStrategyNo=self.corporateStrategyNo)
        return None

    def get_strategic_plan(self) -> NCStrategicPlan | None:
        """Returns a single matched NCStrategicPlan object, if it exists."""
        if NCStrategicPlan.objects.filter(fy=self.fy, strategicPlanNo=self.strategicPlanNo).exists():
            return NCStrategicPlan.objects.get(fy=self.fy, strategicPlanNo=self.strategicPlanNo)
        return None

    def get_d1(self) -> str:
        """Child classes should override this method as required."""
        return str(self.description)

    def get_d2(self) -> str:
        """Child classes should override this method as required."""
        return ""


class GeneralServicePriority(ServicePriority):
    description2 = models.TextField(null=True)

    # NOTE: we need to redefine the FK fields on each child model due to Django reverse query name clash.
    corporate_strategy = models.ForeignKey(
        CorporateStrategy,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="generalservicepriority",
        verbose_name="corporate strategy",
        editable=False,
    )
    strategic_plan = models.ForeignKey(
        NCStrategicPlan,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="generalservicepriority",
        verbose_name="strategic plan",
        editable=False,
    )

    class Meta(ServicePriority.Meta):
        verbose_name_plural = "general service priorities"

    def get_d2(self) -> str:
        return str(self.description2)


class NCServicePriority(ServicePriority):
    assetNo = models.CharField(max_length=5, verbose_name="asset no")
    asset = models.TextField()
    targetNo = models.CharField(max_length=30, verbose_name="target no")
    target = models.TextField()
    actionNo = models.CharField(max_length=30, verbose_name="action no")
    action = models.TextField()
    mileNo = models.CharField(max_length=30, verbose_name="mile no")
    milestone = models.TextField()

    # NOTE: we need to redefine the FK fields on each child model due to Django reverse query name clash.
    corporate_strategy = models.ForeignKey(
        CorporateStrategy,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="ncservicepriority",
        verbose_name="corporate strategy",
        editable=False,
    )
    strategic_plan = models.ForeignKey(
        NCStrategicPlan,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="ncservicepriority",
        verbose_name="strategic plan",
        editable=False,
    )

    class Meta(ServicePriority.Meta):
        verbose_name = "NC service priority"
        verbose_name_plural = "NC service priorities"

    def get_d1(self) -> str:
        return str(self.action)

    def get_d2(self) -> str:
        return str(self.milestone)


class PVSServicePriority(ServicePriority):
    servicePriority1 = models.TextField(verbose_name="service priority 1")

    # NOTE: we need to redefine the FK fields on each child model due to Django reverse query name clash.
    corporate_strategy = models.ForeignKey(
        CorporateStrategy,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="pvsservicepriority",
        verbose_name="corporate strategy",
        editable=False,
    )
    strategic_plan = models.ForeignKey(
        NCStrategicPlan,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="pvsservicepriority",
        verbose_name="strategic plan",
        editable=False,
    )

    class Meta(ServicePriority.Meta):
        verbose_name = "PVS service priority"
        verbose_name_plural = "PVS service priorities"

    def get_d1(self) -> str:
        return str(self.servicePriority1)

    def get_d2(self) -> str:
        return str(self.description)


class SFMServicePriority(ServicePriority):
    regionBranch = models.CharField(max_length=20, verbose_name="region branch")
    description2 = models.TextField()

    # NOTE: we need to redefine the FK fields on each child model due to Django reverse query name clash.
    corporate_strategy = models.ForeignKey(
        CorporateStrategy,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="sfmservicepriority",
        verbose_name="corporate strategy",
        editable=False,
    )
    strategic_plan = models.ForeignKey(
        NCStrategicPlan,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="sfmservicepriority",
        verbose_name="strategic plan",
        editable=False,
    )

    class Meta(ServicePriority.Meta):
        verbose_name = "SFM service priority"
        verbose_name_plural = "SFM service priorities"

    def get_d2(self) -> str:
        return str(self.description2)


class ERServicePriority(ServicePriority):
    classification = models.TextField()

    # NOTE: we need to redefine the FK fields on each child model due to Django reverse query name clash.
    corporate_strategy = models.ForeignKey(
        CorporateStrategy,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="erservicepriority",
        verbose_name="corporate strategy",
        editable=False,
    )
    strategic_plan = models.ForeignKey(
        NCStrategicPlan,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="erservicepriority",
        verbose_name="strategic plan",
        editable=False,
    )

    class Meta(ServicePriority.Meta):
        verbose_name = "ER service priority"
        verbose_name_plural = "ER service priorities"

    def get_d1(self) -> str:
        return str(self.classification)

    def get_d2(self) -> str:
        return str(self.description)


class Outcome(models.Model):
    fy = models.ForeignKey(FinancialYear, on_delete=models.PROTECT, verbose_name="financial year")
    q1Input = models.TextField()
    q2Input = models.TextField(blank=True)
    q3Input = models.TextField(blank=True)
    q4Input = models.TextField(blank=True)

    def __str__(self):
        return str(self.fy)


class ServicePriorityMapping(models.Model):
    fy = models.ForeignKey(FinancialYear, on_delete=models.PROTECT, verbose_name="financial year")
    costCentreNo = models.CharField(max_length=4, verbose_name="cost centre no")
    wildlifeManagement = models.CharField(max_length=100, verbose_name="wildlife management")
    parksManagement = models.CharField(max_length=100, verbose_name="parks management")
    forestManagement = models.CharField(max_length=100, verbose_name="forest management")

    def __str__(self):
        return str(self.costCentreNo)
