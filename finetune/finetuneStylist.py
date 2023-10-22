import os
import openai
openai.api_key = os.getenv("OPENAI_API_KEY")
""" response = openai.File.create(
  file=open("fashionFineTunedata.jsonl", "rb"),
  purpose='fine-tune'
)
# Print the response
print(response)

file_id = response['id']
print(file_id)
response = openai.FineTuningJob.create(training_file=file_id, model="gpt-3.5-turbo")
print (response) """

# List 10 fine-tuning jobs
#openai.FineTuningJob.list(limit=10)

# Retrieve the state of a fine-tune
response = openai.FineTuningJob.retrieve("ftjob-JmFEqcy10uJRugGLLbp1ZOGm")
print(response)

# Cancel a job
#openai.FineTuningJob.cancel("ftjob-abc123")

# List up to 10 events from a fine-tuning job
#openai.FineTuningJob.list_events(id="ftjob-4YJToAng1pRvxpt4WjYWUAEF", limit=10)

# Delete a fine-tuned model (must be an owner of the org the model was created in)
#openai.Model.delete("ft:gpt-3.5-turbo:acemeco:suffix:abc123")#

