'use strict';

// Parse additional variables from the DOM element.
const context = JSON.parse(document.getElementById('javascript_context').textContent);

// DOM element selectors
const divOptionOne = document.getElementById('id_option_one');
const divTemplateLink = document.getElementById('id_template_link');
const divOptionTwo = document.getElementById('id_option_two');
const divFilterForm = document.getElementById('id_filter_form');
const divResultTable = document.getElementById('id_result_table');
const fySelectEl = document.getElementById('id_financial_year');
const ccSelectEl = document.getElementById('id_cost_centre');
const regionSelectEl = document.getElementById('id_region');
const budgetSelectEl = document.getElementById('id_budget_area');
const sponsorSelectEl = document.getElementById('id_project_sponsor');
const serviceSelectEl = document.getElementById('id_service');
const projectSelectEl = document.getElementById('id_project');
const jobSelectEl = document.getElementById('id_job');

async function updateBudgetArea(fy, cc = null, region = null) {
  budgetSelectEl.disabled = true;
  budgetSelectEl.selectedIndex = 0;
  budgetSelectEl.options.length = 0;
  budgetSelectEl.options.add(new Option('--------', ''));
  let url;

  if (cc) {
    url = `${context.ajax_ibmdata_budgetarea_url}?financialYear=${fy}&costCentre=${cc}`;
  } else if (region) {
    url = `${context.ajax_ibmdata_budgetarea_url}?financialYear=${fy}&regionBranch=${region}`;
  }

  try {
    const resp = await fetch(url);
    if (!resp.ok) {
      throw new Error(`Response status: ${resp.status}`);
    }
    const data = await resp.json();
    for (const choice of data.choices) {
      budgetSelectEl.options.add(new Option(...choice));
    }
    budgetSelectEl.disabled = false;
  } catch (error) {
    console.error(error.message);
  }
}

async function updateProjectSponsor(fy, cc = null, region = null) {
  sponsorSelectEl.disabled = true;
  sponsorSelectEl.selectedIndex = 0;
  sponsorSelectEl.options.length = 0;
  sponsorSelectEl.options.add(new Option('--------', ''));
  let url;

  if (cc) {
    url = `${context.ajax_ibmdata_projectsponsor_url}?financialYear=${fy}&costCentre=${cc}`;
  } else if (region) {
    url = `${context.ajax_ibmdata_projectsponsor_url}?financialYear=${fy}&regionBranch=${region}`;
  }

  try {
    const resp = await fetch(url);
    if (!resp.ok) {
      throw new Error(`Response status: ${resp.status}`);
    }
    const data = await resp.json();
    for (const choice of data.choices) {
      sponsorSelectEl.options.add(new Option(...choice));
    }
    sponsorSelectEl.disabled = false;
  } catch (error) {
    console.error(error.message);
  }
}

async function updateService(fy, cc = null, region = null) {
  serviceSelectEl.disabled = true;
  serviceSelectEl.selectedIndex = 0;
  serviceSelectEl.options.length = 0;
  serviceSelectEl.options.add(new Option('--------', ''));
  let url;

  if (cc) {
    url = `${context.ajax_ibmdata_service_url}?financialYear=${fy}&costCentre=${cc}`;
  } else if (region) {
    url = `${context.ajax_ibmdata_service_url}?financialYear=${fy}&regionBranch=${region}`;
  }

  try {
    const resp = await fetch(url);
    if (!resp.ok) {
      throw new Error(`Response status: ${resp.status}`);
    }
    const data = await resp.json();
    for (const choice of data.choices) {
      serviceSelectEl.options.add(new Option(...choice));
    }
    serviceSelectEl.disabled = false;
  } catch (error) {
    console.error(error.message);
  }
}

async function updateProject(fy, cc = null, region = null) {
  projectSelectEl.disabled = true;
  projectSelectEl.selectedIndex = 0;
  projectSelectEl.options.length = 0;
  projectSelectEl.options.add(new Option('--------', ''));
  let url;

  if (cc) {
    url = `${context.ajax_ibmdata_project_url}?financialYear=${fy}&costCentre=${cc}`;
  } else if (region) {
    url = `${context.ajax_ibmdata_project_url}?financialYear=${fy}&regionBranch=${region}`;
  }

  try {
    const resp = await fetch(url);
    if (!resp.ok) {
      throw new Error(`Response status: ${resp.status}`);
    }
    const data = await resp.json();
    for (const choice of data.choices) {
      projectSelectEl.options.add(new Option(...choice));
    }
    projectSelectEl.disabled = false;
  } catch (error) {
    console.error(error.message);
  }
}

async function updateJob(fy, cc = null, region = null) {
  jobSelectEl.disabled = true;
  jobSelectEl.selectedIndex = 0;
  jobSelectEl.options.length = 0;
  jobSelectEl.options.add(new Option('--------', ''));
  let url;

  if (cc) {
    url = `${context.ajax_ibmdata_job_url}?financialYear=${fy}&costCentre=${cc}`;
  } else if (region) {
    url = `${context.ajax_ibmdata_job_url}?financialYear=${fy}&regionBranch=${region}`;
  }

  try {
    const resp = await fetch(url);
    if (!resp.ok) {
      throw new Error(`Response status: ${resp.status}`);
    }
    const data = await resp.json();
    for (const choice of data.choices) {
      jobSelectEl.options.add(new Option(...choice));
    }
    jobSelectEl.disabled = false;
  } catch (error) {
    console.error(error.message);
  }
}

// Disable the FY select list (defaults to the newest).
fySelectEl.disabled = true;
const fy = fySelectEl.value;

// If the Cost Centre select list changes, update the Service, Budget Area
// and Project sponsor select lists.
// Also unselect any value in the region/branch select list.
ccSelectEl.addEventListener('change', function () {
  regionSelectEl.selectedIndex = 0;
  const cc = ccSelectEl.value;
  updateBudgetArea(fy, cc, false);
  updateProjectSponsor(fy, cc, false);
  updateService(fy, cc, false);
  updateProject(fy, cc, false);
  updateJob(fy, cc, false);
});

// If the Region/Branch select list changes, update the Service, Budget Area
// and Project sponsor select lists.
// Also unselect any value in the cost centre select list.
regionSelectEl.addEventListener('change', function () {
  ccSelectEl.selectedIndex = 0;
  const region = regionSelectEl.value;
  updateBudgetArea(fy, false, region);
  updateProjectSponsor(fy, false, region);
  updateService(fy, false, region);
  updateProject(fy, false, region);
  updateJob(fy, false, region);
});

// If the filter results table is present, default this div to being visible.
if (divResultTable) {
  divTemplateLink.style.visibility = 'hidden';
  divFilterForm.style.visibility = 'visible';
  divResultTable.style.visibility = 'visible';
}

// Click event listeners for the two options.
divOptionOne.addEventListener('click', function () {
  divTemplateLink.style.visibility = 'visible';
  divFilterForm.style.visibility = 'hidden';
  divResultTable.style.visibility = 'hidden';
});
divOptionTwo.addEventListener('click', function () {
  divTemplateLink.style.visibility = 'hidden';
  divFilterForm.style.visibility = 'visible';
  divResultTable.style.visibility = 'visible';
});
