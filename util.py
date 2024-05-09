import json
import requests


def getAccessToken(url, appKey, secretKey):
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    response = requests.request("POST", url.format(appKey, secretKey), headers=headers)
    return response.json().get("access_token")


def generateVideo(image, text, baiduConfig, videoConfig, accessToken):
    textStruct = {'type': 'text', "text": text}
    imageStruct = {'type': 'image', 'mediaSource': {'type': 3, 'url': 'https://img2.baidu.com/it/u=458067144,3176118096&fm=253&fmt=auto&app=138&f=JPEG?w=500&h=750'}}
    strutcs = [textStruct, imageStruct]
    data = {'config': videoConfig, 'source': {'structs': strutcs}}
    method = 'material'
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    response = requests.request("POST", baiduConfig['url'].format(method, accessToken), headers=headers, data=json.dumps(data))
    
    print(response.text)

    data = json.loads(response.text)
    return data['data']['jobId']



def queryVideo(baiduConfig, accessToken, jobID):
    url = baiduConfig['url'].format('query', accessToken)
    
    payload = json.dumps({
        "includeTimeline": False,
        'jobId': jobID
    })
    
    headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }
    
    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)
    data = json.loads(response.text)
    return data['data']['videoAddr']


def optimizeText(baiduConfig, accessToken, raw_text):
    prompt = baiduConfig['textPrompt'].format(raw_text)
    print(prompt)
    payload = json.dumps({
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    })
    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("POST", baiduConfig['textUrl'].format(accessToken), headers=headers, data=payload)
    res = json.loads(response.text)
    print(res)
    return res['result']



if __name__ == '__main__':
    with open('config/config.json', encoding='utf-8') as f:
        config = json.load(f)
    baiduConfig = config['baidu']
    accessToken = getAccessToken(baiduConfig['accessTokenUrl'], baiduConfig['apiKey'], baiduConfig['secretKey'])
    #generateVideo("", "妹妹在微笑,多么迷人的微笑呀，真想和她永远在一起", baiduConfig, config['video'], accessToken)
    queryVideo(baiduConfig, accessToken, "1787998592885768902")
    
