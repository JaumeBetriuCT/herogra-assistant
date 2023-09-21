
def is_negative_response(response: str) -> bool:

    negative_responses = [" No sé.", " No se sabe.", " No lo sé."]
    if response in negative_responses:
        return True
    else:
        return False