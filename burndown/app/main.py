from gql import Client, gql
from gql.transport.aiohttp import AIOHTTPTransport
import pandas as pd
from datetime import datetime

from os import environ

class Issue:
    id:str
    type:str = "DRAFT_ISSUE"
    title:str = ""
    status:str = "None"
    iteration:str = ""
    estimate:float = 0.0
    actual:float = 0.0
    assignees:list[str] = []

    def __init__(self, node:dict):
        self.id = node['id']
        self.type = node['type']
        for field in node['fieldValues']['nodes']:
            if("field" in field):
                name = field["field"]["name"]
                if(name == "Title"): self.title = field['text']
                if(name == "Iteration"): self.iteration = field['title']
                if(name == "Status"): self.status = field['name']
                if(name == "Estimate"): self.estimate = field['number']
                if(name == "Actual"): self.actual = field['number']

        for assignee in node['content']['assignees']['nodes']:
            self.assignees.append(assignee['login'])
    
    def to_dict(self):
        obj = dict({})
        obj['id'] = self.id
        obj['type'] = self.type
        obj['title'] = self.title
        obj['status'] = self.status
        obj['iteration'] = self.iteration
        obj['estimate'] = self.estimate
        obj['actual'] = self.actual
        obj['assignees'] = self.assignees
        return obj

def fetch_issues() -> list[dict]:
    # Select your transport with a defined url endpoint
    transport = AIOHTTPTransport(url="https://api.github.com/graphql", 
                                headers={'Authorization': f"Bearer {environ['GITHUB_TOKEN']}"})

    # Create a GraphQL client using the defined transport
    client = Client(transport=transport, fetch_schema_from_transport=True)
    # Provide a GraphQL query
    request_string = gql(open("./request_string.graphql", "r").read())
    # Init parameters
    issues = []
    hasNextPage = True
    endCursor = "null"
    while hasNextPage:
        params = {"project_id": environ['PROJECT_ID'], "item_number":10, "after":endCursor}
        # Execute the query on the transport
        # result = client.execute(query)
        result = client.execute(request_string, variable_values=params)
        for node in result['node']['items']['nodes']:
            issue = Issue(node)
            issues.append(issue.to_dict())
        # {'endCursor': 'Ng',
        #  'startCursor': 'NA',
        #  'hasNextPage': True,
        #  'hasPreviousPage': True}
        pageInfo = result['node']['items']['pageInfo']
        endCursor = pageInfo['endCursor']
        startCursor = pageInfo['startCursor']
        hasNextPage = pageInfo['hasNextPage']
        hasPreviousPage = pageInfo['hasPreviousPage']
    return issues

def save_json(issues:list[dict]):
    df = pd.DataFrame.from_records(issues, index="id")
    time = datetime.now().strftime("%Y%m%d-%H%M%S")
    df.to_csv(path_or_buf=f"/src/data/{time}.csv")

def main():
    issues = fetch_issues()
    save_json(issues)


if __name__ == "__main__":
    main()