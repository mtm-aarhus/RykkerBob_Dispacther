from OpenOrchestrator.orchestrator_connection.connection import OrchestratorConnection
from GetKmdAcessToken import GetKMDToken
import requests
import os
import uuid
from datetime import datetime
import json
import pandas as pd
import re
orchestrator_connection = OrchestratorConnection("Henter Assets", os.getenv('OpenOrchestratorSQL'),os.getenv('OpenOrchestratorKey'), None)
# ---- Henter assests og credentials -----
KMDNovaURL = orchestrator_connection.get_constant("KMDNovaURL").value

  # ---- Henter access tokens ----
KMD_access_token = GetKMDToken()


# ---- Opretter predefineret datatabel
dt_Sagsnummer = {
    "Sagsnummer": pd.Series(dtype="string"),
    "TaskUuid": pd.Series(dtype="string"),
    "CaseUuid": pd.Series(dtype="string"),
    "taskStartDate": pd.Series(dtype="string"),
    "TaskDeadline": pd.Series(dtype="string"),
    "CaseWorkerID": pd.Series(dtype="string"),
    "RykkerNummer": pd.Series(dtype="int32"),
}


# ---- Henter Sagsnummer og Sagsbeskrivelse ---- 
TransactionID = str(uuid.uuid4())
CurrentDate = datetime.now().strftime("%Y-%m-%dT00:00:00")

# Construct the JSON payload
payload = {
    "common": {"transactionId": TransactionID},
    "paging": {"startRow": 1, "numberOfRows": 1000},
    "TaskGetListResponse": {
        "caseworkerPersonId": True,
        "taskList": [{"taskDescription": True}]
    },
    "title": "*afventer påbegyndelse*",
    "toDeadlineDate": CurrentDate,
    "statusCode": ["S"],
    "sortOrder": "TaskDateDescending"
}

# Define headers
headers = {
    "Authorization": f"Bearer {KMD_access_token}",
    "Content-Type": "application/json"
}

# Define the API endpoint
url = f"{KMDNovaURL}/Task/GetList?api-version=2.0-Case"
# Make the HTTP request
try:
    response = requests.put(url, headers=headers, json=payload)
    response.raise_for_status()  # Raise an error for non-2xx responses
    data = response.json()
    print("Success:", response.status_code)
    
    # Extract and print number of rows
    number_of_rows = data.get("pagingInformation", {}).get("numberOfRows", 0)
    print("Number of Rows:", number_of_rows)
    
    # Initialize an empty list to store queue items
    queue_items = []
    
    # Iterate through task list
    for task in data.get("taskList", []):
        case_number = task.get("caseNumber", "Unknown")
        task_description = task.get("taskDescription", "")
        RykkerNummer = None

        if not task_description:
            print(f"Anvender: {case_number}")
            RykkerNummer = 1
        elif re.search(r"^Rykkerskrivelse udført af robot$", task_description):
            print("Beskrivelsesfeltet indeholder 1. rykker")
            print(f"Anvender: {case_number} til at udsende 2. rykker")
            RykkerNummer = 2
        elif re.search(r"^2. Rykkerskrivelse udført af robot$", task_description):
            print("Beskrivelsesfeltet indeholder 2. rykker")
            print(f"Anvender: {case_number} til at udsende 3. rykker")
            RykkerNummer = 3
        else:
            print(f"Anvender ikke: {case_number}")

        if RykkerNummer is not None:
            row_data = {
                "caseNumber": case_number,
                "taskUuid": task.get("taskUuid"),
                "caseUuid": task.get("caseUuid"),
                "taskStartDate": task.get("taskStartDate"),
                "taskDeadline": task.get("taskDeadline"),
                "caseWorkerId": task.get("caseworker", {}).get("kspIdentity", {}).get("novaUserId"),
                "RykkerNummer": int(RykkerNummer)
            }
            queue_items.append({
                "SpecificContent": row_data,
                "Reference": case_number  # Assuming case_number provides a unique reference
            })
    
    # Prepare references and data for the bulk creation function
    references = tuple(item["Reference"] for item in queue_items)  # Extract references as a tuple
    data = tuple(json.dumps(item["SpecificContent"]) for item in queue_items)  # Convert SpecificContent to JSON strings
    
    queue_name = "RykkerBob"
    # Bulk add queue items to OpenOrchestrator
    try:
        orchestrator_connection.bulk_create_queue_elements(queue_name, references, data, created_by="RykkerBob_Dispatcher")
        orchestrator_connection.log_info(f"Successfully added {len(queue_items)} items to the queue.")
    except Exception as e:
        print(f"An error occurred while adding items to the queue: {str(e)}")

except requests.exceptions.RequestException as e:
    print("Request Failed:", e)