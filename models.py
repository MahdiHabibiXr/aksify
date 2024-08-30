import replicate
import os

# domain = os.environ['DOMAIN']

def create_face_to_many(image, style):

    input = {
        "image" : open(image,'rb'),
        "style" : style,
        "prompt" : "a person",
        "prompt_strength": 4.5,
        "denoising_strength": 0.66,
        "instant_id_strength": 0.8
    }
    
    domain = os.environ['DOMAIN']
    callback_url = f'{domain}/webhooks/replicate/face-to-many'

    request = replicate.predictions.create(
        version="a07f252abbbd832009640b27f063ea52d87d7a23a185ca165bec23b5adc8deaf",
        input=input,
        webhook=callback_url,
        webhook_events_filter=["completed"]
    )

    return request
