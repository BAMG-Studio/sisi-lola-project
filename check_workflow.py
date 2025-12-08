import requests
import json

url = "https://api.github.com/repos/BAMG-Studio/sisi-lola-project/actions/runs?per_page=3"
response = requests.get(url)
data = response.json()

print(f"Response status: {response.status_code}")
print(f"Keys in response: {list(data.keys())}")
if 'message' in data:
    print(f"Message: {data['message']}")

if data.get('workflow_runs') and len(data['workflow_runs']) > 0:
    for run in data['workflow_runs']:
        print(f"\n{'='*60}")
        print(f"Workflow: {run['name']}")
        print(f"Status: {run['status']}")
        print(f"Conclusion: {run['conclusion']}")
        print(f"Created: {run['created_at']}")
        print(f"URL: {run['html_url']}")
        
        # Get job details
        jobs_url = run['jobs_url']
        jobs_response = requests.get(jobs_url)
        jobs_data = jobs_response.json()
        
        if jobs_data.get('jobs'):
            print(f"\nJobs:")
            for job in jobs_data['jobs']:
                print(f"  - {job['name']}: {job['conclusion'] or job['status']}")
                if job['conclusion'] == 'failure':
                    print(f"    Steps:")
                    for step in job['steps']:
                        if step['conclusion'] == 'failure':
                            print(f"      ❌ {step['name']}")
else:
    print("No workflow runs found")
