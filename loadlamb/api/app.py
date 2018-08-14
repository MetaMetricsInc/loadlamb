#from functools import singledispatch

from chalice import Chalice
from boto3.dynamodb.conditions import Key, Attr
import boto3

from loadlamb.contrib.db.models import Project, Run, LoadTestResponse

app = Chalice(app_name='loadlambApi')

db = boto3.resource('dynamodb')
table = db.Table('loadlambddb')
# instead of tabl.scan(), use docb


# get_projects, accessible via API /projects GET request, will return
# a list of projects.
@app.route('/projects')
def get_projects():
    project_list = list(Project.all())
    return project_list


@app.route('/projects/slugs')
def get_project_slugs():
    project_list = Project.all()

    return project_list


# get_project_runs, accessible via API /projects/{projectSlug} or 
# /runs/{projectSlug} GET request, will return a list of unique run slugs
# that are linked to the specified project.
@app.route('/projects/{projectSlug}')
@app.route('runs/{projectSlug}')
def get_project_runs(projectSlug):
    run_list = list(Run.objects().filter({"project_slug": projectSlug}))
    return run_list
    
    # scan = table.scan(
    #     FilterExpression=Attr("project_slug").contains(projectSlug),
    #     ProjectionExpression="run_slug"
    # )

    # items = scan["Items"]
    # slugs = []

    # for slug in items:
    #     slugs.append(slug["run_slug"])

    # output = list(set(slugs))

    # return output


# # /runs/{runSlug} should get you the values of a run,
# #  parsed into a sorted dict object. json?
# @app.route('runs/{runSlug}')
# def get_run(runSlug):
#     # Client to dynamoDB, retrieve all values for run-slug, parse into sorted dict.
#     scan = table.scan(
#         FilterExpression=Attr("run_slug").contains(runSlug),
#     )

#     items = scan["Items"]
#     output = sorted(items, key=lambda :)


# # @app.route('runs/summary/{runSlug}')
# # def get_run_summary(runSlug):
# #     # Run get_run(runSlug), then create summary with Average, Low, High, Total Requests. Return as a dict.


# # @app_route('runs/compare/{projectSlug}/{runSlug1}/{runSlug2}')
# # @app_route('runs/compare/{projectSlug}/{runSlug2}')
# # @app_route('runs/compare/{projectSlug}/')
# # def get_run_comparison(projectSlug=None, runSlug1=None, runSlug2=None)

# #     if projectSlug is None:
# #         raise ValueError("No projectSlug specified.")

# #     # Check for the existance of values in runSlug2 and runSlug1.
# #     if runSlug2 is None and runSlug1 is None:
# #         # If neither was specified, default to the 2 most recent runs.
# #         runs = get_project_runs(projectSlug)
# #         run1 = runs[0]
# #         run2 = runs[1]
# #     elif runSlug2 is None:
# #         # If only one is specified, then compare the most recent run with that.
# #         runs = get_project_runs(projectSlug)
# #         run1 = runs[0]
# #         run2 = runSlug2
# #     else:
# #         # If both are specified, then use them as they are.
# #         run1 = runSlug1
# #         run2 = runSlug2

# #     run1Summary = get_run_summary(run1)
# #     run2Summary = get_run_summary(run2)

# #     runComparison = {
# #         "Comparison": {
# #             "Average": run2["Average"] - run1["Average"],
# #             "High": run2["High"] - run1["High"],
# #             "Low": run2["Low"] - run1["Low"],
# #         }
# #     }
# #     runComparison["Run1"] = run1Summary
# #     runComparison["Run2"] = run2Summary

# #     return json.loads(runComparison)
