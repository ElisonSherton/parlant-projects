# Card Bot

Here we build a basic bot which can help with credit card related information. How to test?

1. Install parlant and from the root of this directory, run the command `parlant-server`
2. Create an agent using the command `parlant agent create --name "John Doe" --description "A helpful assistant to answer questions related to banking"
3. Note down this agent's id. You can get that by running `parlant agent list` and copying the ID corresponding to John Doe
4. Start the tool service at port 8089 with the command `parlant service create --name "card_service" --kind sdk --url http://localhost:8089`
5. Start the tool server by cding into the tool-service folder and running `poetry run python parlant_tool_service_starter/card_service.py`
6. Now come back to the root folder and run `python create_guidelines.py --agent-id <AGENT_ID>` and simultaneously run `python attach_tools.py --agent-id <AGENT_ID>`
7. To add the FAQ service, start the faq service using `parlant-qna serve` or when creating the server, add the qna module as `parlant-server --module parlant_qna.module`
8. Use the `post-questions.py` file to add all the questions
9. Then add the qna service to the guideline which is supposed to answer the FAQs as follows: `parlant guideline tool-enable --agent-id agent_id --service qna --tool find_answer --id guideline_id`
10. Head over to localhost:8800 and you should be able to talk to your bot ! :)