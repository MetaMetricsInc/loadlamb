# from functools import singledispatch

from chalice import Chalice

from loadlamb.contrib.db.models import Project, Run, LoadTestResponse

app = Chalice(app_name='loadlambApi')


# get_projects, accessible via API /projects GET request, will return
# a list of projects.
@app.route('/projects')
def get_projects():
    project_list = list(Project.objects().all())
    return project_list


# get_project_runs, accessible via API /projects/{project_slug} or
# /runs/{project_slug} GET request, will return a list of unique run slugs
# that are linked to the specified project.
@app.route('/projects/{project_slug}')
@app.route('runs/{project_slug}')
def get_project_runs(project_slug):
    run_list = list(Run.objects().filter({"project_slug": project_slug}))
    return sorted([i.run_slug for i in run_list], reverse=True)


# get_runs, accessible via API /runs/{run_slug} GET request, will return the
# values from a run. Format TBD.
@app.route('runs/{run_slug}')
def get_run(run_slug):
    run_response = LoadTestResponse.objects().filter(
        {"run_slug": run_slug}
    )

    if len(run_response) > 0:
        return[{
            "elapsed_time": i.elapsed_time,
            "method_type": i.method_type,
            "status_code": i.status_code,
            "path": i.path
        } for i in run_response]
    else:
        return "Run has no responses."


# get_run_summary, accessible via API /runs/summary/{run_slug} GET request,
# will return a dict with the summary of the run, including average, min, max,
# good responses (200), and total responses.
@app.route('runs/summary/{run_slug}')
def get_run_summary(run_slug):
    run = get_run(run_slug)

    average = sum(response['elapsed_time'] for response in run) / len(run)
    minimum = min(response['elapsed_time'] for response in run)
    maximum = max(response['elapsed_time'] for response in run)
    success = sum(str(response['status_code']).count('200')
                  for response in run)
    total = len(run)

    summary = {
        "run_slug": run_slug,
        "Average": average,
        "Minimum": minimum,
        "Maximum": maximum,
        "Successsful": success,
        "Total": total
    }
    return summary


# get_run_comparison has three modes, and three access points in the API via
# GET request.
#
# If run with a single parameter, the {project_slug}, it will compare the two
# most recent runs for that project.
#
# If run with two parameters, the {project_slug} and a single {run_slug}, it
# will compare the most recent run with the specified run.
#
# If run with three parameters, the {project_slug} and two {run_slug}, it will
# compare the two specified slugs as they are input.
@app.route('runs/compare/{project_slug}/{run_slug_1}/{run_slug_2}')
@app.route('runs/compare/{project_slug}/{run_slug_2}')
@app.route('runs/compare/{project_slug}/')
def get_run_comparison(project_slug=None, run_slug_1=None, run_slug_2=None):

    # If no value was specified, then raise an error.
    if project_slug is None:
        raise ValueError("No project_slug specified.")

    # Check for the existance of values in run_slug_2 and run_slug_1.
    if run_slug_2 is None and run_slug_1 is None:
        # If neither was specified, default to the 2 most recent runs.
        try:
            runs = sorted(get_project_runs(project_slug))
            runs.reverse()
        except Exception as e:
            pass
        run1 = runs[0]
        run2 = runs[1]
    elif run_slug_2 is None:
        # If only one is specified, then compare the most recent run with that.
        runs = get_project_runs(project_slug)
        run1 = runs[0]
        run2 = run_slug_1
    else:
        # If both are specified, then rearrange them to have the most recent
        # slug as run_slug_1.
        if run_slug_1 > run_slug_2:
            run1 = run_slug_1
            run2 = run_slug_2
        else:
            run1 = run_slug_2
            run2 = run_slug_1

    run1Summary = get_run_summary(run1)
    run2Summary = get_run_summary(run2)

    runComparison = {
        "Comparison": {
            "Average": (run2Summary['Average'] - run1Summary['Average']),
            "Maximum": run2Summary["Maximum"] - run1Summary["Maximum"],
            "Minimum": run2Summary["Minimum"] - run1Summary["Minimum"],
        }
    }

    runComparison["Run 1"] = run1Summary
    runComparison["Run 2"] = run2Summary

    return runComparison
