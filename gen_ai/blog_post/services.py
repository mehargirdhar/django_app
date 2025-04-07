import json

from utils.openai_management import OpenAIClient


def create_title_suggestions(blog: str, num_of_suggestion: int = 3) -> list:

    base_prompt = f"""You are an experienced Blog writer. User has written a blog post.
    Your job is to provide user with title suggestions for the blog.
    Title should be relevant to the blog and use engaging words.
    Title shouldn't be too large or small - keep it brief with action words.
    Number of titles should be {num_of_suggestion}.
    Response should be in JSON format.
    """

    output_format = """\nOutput should be in JSON in following format
        {
            "title" : ["suggestion 1", "suggestion 2", "suggestion 3"] -- array of suggestions
        }
    """

    final_prompt = [
        {"role": "system", "content": base_prompt + output_format},
        {"role": "assistant", "content": f"\nUser's blog -\n {blog}"}
    ]

    client = OpenAIClient()
    gpt_response = client.get_chat_completion(
        model='gpt-4o-mini',
        messages=final_prompt,
        temperature=0.5,
        response_format='json_object'
    )

    return json.loads(gpt_response)
