import typing as t

import aiohttp

API_BASE_URL = "https://mystb.in/api/pastes"

async def post(content:str, session:aiohttp.ClientSession, syntax:t.Optional[str]=".text") -> str:
    # sourcery skip: raise-specific-error
    """
    Posts the given content with syntax if provided to the mystbin and returns the link.
    """
    mpwrite = aiohttp.MultipartWriter()
    paste_content = mpwrite.append(content)
    paste_content.set_content_disposition('form-data', name='data')
    paste_content = mpwrite.append_json({'meta':[{'index':0, 'syntax':syntax}]})
    paste_content.set_content_disposition('form-data', name='meta')
    async with session.post(
                    API_BASE_URL,
                    data=mpwrite, 
                    timeout=aiohttp.ClientTimeout(15) ) as response:
        status_code = response.status
        if not 200 <= status_code < 300:
            raise Exception(f"<response_text = {response_text}>, <status_code = {status_code}>")
        
        response_text = await response.text()
        response_data = await response.json()
    
        return f"https://mystb.in/{response_data['pastes'][0]['id']}{syntax}"
    

def split_texts(text:str, split_into:int) -> list:
    """
    Given a large text, it splits the text into different parts with 
    each part having characters = `split_into`
    """
    new_texts = []
    length_count = 0

    for l in text.split():
        length_count = len(l) + 1 + length_count
        diff = split_into - length_count
        if diff > 0 and diff < 10:
            new_texts.append(text[:length_count])
            if len(text[length_count:]) > split_into:
                text = text[length_count:]
                length_count = 0
            else:
                new_texts.append(text[length_count:])
                return new_texts
