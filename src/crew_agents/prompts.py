def get_task_prompt():
    prompt = """Conduct an web search on {description}, focusing on gathering the most recent and credible data available. Provide a detailed yet concise summary, emphasizing key points, trends, and any notable developments. Ensure that all information is gathered from authoritative, trustworthy sources. Include a valid and working link to each data source in the following format: [http://example.com/dataset], and verify that all insights are precise, relevant, and from reputable publications or datasets."""

    return prompt


def get_comment_task_prompt():
    prompt = "Provide a insightful comment on the previous task performed by another agent. The comment should assess the task's quality, relevance, and outcomes. If the task involved fetching data, summarize the data and offer thoughts on its significance or potential use. Keep output of max 3 sentance. and if task is completed you can start by saying Task is successfully completed and ..., here is the example: The task was successfully completed, and the data fetched is relevant. These articles/data provide valuable insights into the technological advancements in 2024, demonstrating their ongoing influence in the industry. Potential improvements or further analysis could include exploring the current impact of these innovations."

    return prompt


def get_desc_prompt(goal, description):
    prompt = f"""Goal of the task: {goal}. Follow the instruction: {description}. First read and analyze the instruction. Optimize the task by ensuring clarity, precision, and accuracy in the information gathered, while maintaining alignment with the specified goal. Focus on delivering concise insights that meet the task requirements effectively."""

    return prompt
