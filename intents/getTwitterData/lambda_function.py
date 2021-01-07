import json
from pandasticsearch import DataFrame

def build_response(message):
    return {
    "isBase64Encoded": False,
    "statusCode": 200,
    "headers": { "my_header": "my_value"},
    "body": json.dumps(message)
}

def lambda_handler(event, context):
	df = DataFrame.from_es(url='http://35.196.84.204:9200', index='cg_finals_0',compat=5)
	response_dict={}
	input_json=event['body']
	platform=input_json['platform']
	count=input_json['limit']
	response_dict={}
	response=df.filter((df.type==platform)).collect()
	for x in range(0,count):
		resp=response[count]
		response_dict={}
		response_dict['Tweet%s'%(count+1)]={'Tweet Text':resp['tweet'],'Tweet Sentiment': resp['sentiment'],'Retweets':resp['retweet_count'],'Favourites':resp['favourite_count']}
		if 'topics' in resp.keys():
			response_dict['Tweet%s'%(count+1)]['Tweet topics']=resp['topics']
		if 'user' in resp.keys():
			response_dict['Tweet%s'%(count+1)]['Tweet user']=resp['user']
	return build_response(response_dict)