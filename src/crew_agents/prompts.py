def get_task_prompt():
    prompt = """Process this task: {description}. Output should be only depend on the task. Try to not include descriptions."""

    return prompt.strip()


def get_comment_task_prompt():
    prompt = """Provide exactly one short sentence starting with "Task is successfully completed, and..." that only confirms task completion and information relevance. Do not include details, summaries, or recommendations. Example: "Task is successfully completed, and the gathered data matches the required criteria."
    """
    return prompt.strip()


def get_desc_prompt(agent, description, previous_output, relevant_output):
    prompt = f"""Your primary goal for this task is {agent['goal']}. Please carefully follow these instructions: {description}. Begin by thoroughly reading and analyzing the provided instructions. Your approach should prioritize clarity, precision, and accuracy in gathering and presenting information, while ensuring strict alignment with the specified goal. Focus exclusively on delivering concise, relevant insights that directly address the task requirements."""

    if relevant_output:
        prompt += f"""
            For context, consider the following relevant information from the user-uploaded document: {relevant_output}. """
    
    if agent['is_custom_agent'] :
        prompt += f"""This information exists within the broader context of {agent['context']}. The focus group framework involves a group titled "{agent['focus_group_title']}" with the following description: {agent['focus_group_description']}. The core objective of this group is {agent['focus_group_objective']}. The current discussion centers on {agent['discussion_topic']}, with several top ideas identified: {agent['top_ideas']}. For validation purposes, we are conducting a survey titled "{agent['validation_survey_title']}" which includes the following questions: {agent['questions']}. When formulating your response, ensure that you maintain strict relevance to the instructions, demonstrate clear alignment with the primary goal, and present information in a precise, actionable manner. Every insight provided should contribute directly to achieving the stated objective. Do not provide description. Make sure output is too the point and relevant."""

    if previous_output:
        prompt += f"""To provide additional context, consider the following previous output from other agents: {str(previous_output)}. Use this historical context to inform your analysis, ensuring continuity and building upon existing insights while avoiding redundancy. Your response should acknowledge and integrate relevant aspects of this previous work while maintaining focus on the current objectives."""

    return prompt.strip()
