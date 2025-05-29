'''
Scikitlearn helps with all of this

# What question are we trying ti answer
# Find data to help aswer qeustio
# Process Data
# Build model
# Evaluate Model
# Improve Model

'''
import json
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn import svm
from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score
import random




#Two types of machine learning models
# Neural Netwrk Models / Deeplearning models <-  Tensorflow ,Pytorch
# Traditinal Algorthmic Models   <- Sci-Kit


#enum class
class Sentiment:
    NEGATIVE ="NEGATIVE"
    NEUTRAL = "NUTRAL"
    POSITIVE = "POSITIVE"


class Review:
    def __init__(self,text,score):
        self.text = text
        self.score = score
        self.sentiment = self.get_sentiment()

    #Create sentiment 
    def get_sentiment(self):
        if self.score <=2:
            #return "NEGATIVE"
            return Sentiment.NEGATIVE #more consistant way
        elif self.score == 3:
            #return "NEUTRAL"
            return Sentiment.NEUTRAL
        else: #Score of 4 or 5
            #return "POSITIVE"
            return Sentiment.POSITIVE

class ReviewContianer:
    def __init__(self,reviews):
        self.reviews = reviews

    def get_text(self):
        return [x.text for x in self.reviews]
    
    def get_sentiment(self):
        return [x.sentiment for x in self.reviews]

    def evenly_distribute(self):
        negative = list(filter(lambda x: x.sentiment ==Sentiment.NEGATIVE,self.reviews))
        positive = list(filter(lambda x: x.sentiment ==Sentiment.POSITIVE,self.reviews))
        positive_shrunk = positive[:len(negative)]

        self.reviews = negative +positive_shrunk
        random.shuffle(self.reviews)


#import json

#file_name = './data/Books_small.json'
file_name = './data/Books_small_10000.json'

reviews = []
with open (file_name) as f:
    for line in f:
        review = json.loads(line)
        # print(review['reviewText'])
        # print(review['overall'])
        #reviews.append((review['reviewText'],review['overall']))  ##This line is for #print(reviews[5][0]) #print(reviews[5][1])
        #Create a Revie object to passs text and score
        reviews.append(Review(review['reviewText'],review['overall']))

print(reviews[5].text)         
print(reviews[5].score)    
print(reviews[5].sentiment) 
#print(reviews[5][0])
#print(reviews[5][1])

#Ways to convert text into quantitative vector and we are using bag of words to start

'''
THIS BOOK IS GREAT !
THIS BOOK WAS SO BAD



'''

#Prepare data
#print(len(reviews))
training,test = train_test_split(reviews,test_size=0.33,random_state=42)

#ReviewContainer

train_conainer = ReviewContianer(training)
test_container = ReviewContianer(test)

#cont.evenly_distribute()
#print("#######>>>>>>>>>",len(cont.reviews))

#Identify the length of training and test data
#print(len(training),len(test))

#print(training[0].text,training[0].sentiment)
#lamda expression 

''' OLD
train_x = [x.text for x in training]
train_y = [x.sentiment for x in training]

test_x = [x.text for x in test]
test_y = [x.sentiment for x in test]

'''
#evenly_distribute make the same number of tarin and test data sets

train_conainer.evenly_distribute()

train_x =train_conainer.get_text()
train_y = train_conainer.get_sentiment()

test_container.evenly_distribute()
test_x = test_container.get_text()
test_y = test_container.get_sentiment()

print(">>>>>>>>>|||",train_y.count(Sentiment.POSITIVE))
print(">>>>>>>>>|||",train_y.count(Sentiment.NEGATIVE))

#print(train_x[0])
#print(train_y[0])

'''  BAGS OF WORDS VECTORIZATION'''
#from sklearn.feature_extraction.text import CountVectorizer

vectorizer = CountVectorizer()
''' Lamda expression'''
#train_x_vectors = vectorizer.fit_transform(train_x)
#lamda expression expanded 

vectorizer.fit(train_x)
train_x_vectors = vectorizer.transform(train_x)
test_x_vectors = vectorizer.transform(test_x)


print(train_x[0])
print(train_x_vectors[0].toarray())


#Classification

'''
    "Nearest Neighbors",
    "Linear SVM",
    "RBF SVM",
    "Gaussian Process",
    "Decision Tree",
    "Random Forest",
    "Neural Net",
    "AdaBoost",
    "Naive Bayes",
    "QDA",
    "LogisticRegression"

'''
# Linear SVM
#from sklearn import svm

clf_svm =svm.SVC(kernel='linear')
clf_svm.fit(train_x_vectors,train_y)

print(test_x[0])

print("Linear SVM",clf_svm.predict(test_x_vectors[0]))

# Decision Tree
#from sklearn.tree import DecisionTreeClassifier

clf_dec = DecisionTreeClassifier()
clf_dec.fit(train_x_vectors,train_y)

print("Linear Decition Tree",clf_dec.predict(test_x_vectors[0]))

# Naive Bayes
#from sklearn.naive_bayes import GaussianNB

clf_gnb = GaussianNB()
clf_gnb.fit(train_x_vectors.toarray(),train_y)

print("Naiv based",clf_gnb.predict(test_x_vectors[0].toarray()))


# LogisticRegression
#from sklearn.linear_model import LogisticRegression

clf_log = LogisticRegression()
clf_log.fit(train_x_vectors,train_y)

print("Logistic Regression",clf_log.predict(test_x_vectors[0]))


# Evaluation
#mean Accuracy

print("SVM ",clf_svm.score(test_x_vectors,test_y))
print("Decission Tree ",clf_dec.score(test_x_vectors,test_y))
print("NaiveBase ",clf_gnb.score(test_x_vectors.toarray(),test_y))
print("Logistical Regression ",clf_log.score(test_x_vectors,test_y))


#F1 Score
#from sklearn.metrics import f1_score
print("F1 Score SVM",f1_score(test_y,clf_svm.predict(test_x_vectors),average=None,labels=[Sentiment.POSITIVE,Sentiment.NEUTRAL,Sentiment.NEGATIVE]))
print("F1 Score Decision Tree",f1_score(test_y,clf_dec.predict(test_x_vectors),average=None,labels=[Sentiment.POSITIVE,Sentiment.NEUTRAL,Sentiment.NEGATIVE]))
print("F1 Score Naive Base",f1_score(test_y,clf_gnb.predict(test_x_vectors.toarray()),average=None,labels=[Sentiment.POSITIVE,Sentiment.NEUTRAL,Sentiment.NEGATIVE]))
print("F1 Score Logistic Regression",f1_score(test_y,clf_log.predict(test_x_vectors.toarray()),average=None,labels=[Sentiment.POSITIVE,Sentiment.NEUTRAL,Sentiment.NEGATIVE]))

print(train_y[0:5])
print(train_y.count(Sentiment.NEGATIVE))
print(train_y.count(Sentiment.POSITIVE))


print(">>>>>>>>>>>> PREDICTION <<<<<<<<<<<<<<<<<<<<<<")
test_set = [' Disappointed advertised as adults, older children more like sorry',
            'Pages trop fines, impressions qui dégorgent',
            'Great for beginner colourers as images are less complicated with lots of big spaces. Would also be good for zentangling']
new_test = vectorizer.transform(test_set)
print(clf_svm.predict(new_test))

print(">>>>>>>>>>>> END OF PREDICTION <<<<<<<<<<<<<<<<<<<<<<")


