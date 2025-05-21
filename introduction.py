'''
Scikitlearn helps with all of this

# What question are we trying ti answer
# Find data to help aswer qeustio
# Process Data
# Build model
# Evaluate Model
# Improve Model

'''

#Two types of machine learning models
# Neural Netwrk Models / Deeplearning models <-  Tensorflow ,Pytorch
# Traditinal Algorthmic Models   <- Sci-Kit

class Sentiment:
    NEGATIVE ="NEGATIVE"
    NEUTRAL = "NUTRAL"
    POSITIVE = "POSITIVE"


class Review:
    def __init__(self,text,score):
        self.text = text
        self.score = score
        self.sentiment = self.get_sentiment()

    def get_sentiment(self):
        if self.score <=2:
            return "NEGATIVE"
        elif self.score == 3:
            return "NEUTRAL"
        else: #Score of 4 or 5
            return "POSITIVE"




import json

file_name = './data/Books_small.json'

reviews = []
with open (file_name) as f:
    for line in f:
        review = json.loads(line)
        # print(review['reviewText'])
        # print(review['overall'])
        reviews.append((review['reviewText'],review['overall']))
        
print(reviews[5].text)        
#print(reviews[5][0])
#print(reviews[5][1])