# -*- coding: utf-8 -*-


from google.colab import drive
drive.mount('/content/drive')

import pandas as pd
from nltk import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
import nltk
nltk.download()

data = pd.read_csv('Shuffled_FakeJob_.csv',sep=None)
data

#filling null values, 'Not Applicable' and 'Unspecified' with 'Not Specified'
data.fillna('Not Specified', inplace=True)
data = data.replace(['Not Applicable','Unspecified','missing'],'Not Specified')

data['job_description'] = data['title'] + ' ' + data['location'] + ' ' + data['company_profile'] + ' ' + data['description'] + ' ' + data['requirements'] + ' ' + data['benefits'] + ' ' + data['employment_type'] + ' ' + data['required_experience'] + ' ' + data['required_education'] + ' ' + data['industry'] + ' ' + data['function']

print(data['job_description'])

import re
lemmatizer = WordNetLemmatizer()
text=[]
for post in data['job_description']:
  post.lower()
  #Tokenization:
  token=word_tokenize(post)
  #Regular expretion:
  clean_text = re.sub('[^a-zA-Z]', ' ', post)
  #clean_text = re.sub('[*!@#$%^&*+-={}[]|\:;<>,.?/`~()_]', ' ',post) #SYMBOLS TO BE REMOVED

  #stop word removal :
  clean_text = [lemmatizer.lemmatize(word) for word in token if word not in stopwords.words("english")]
  clean_text = ' '.join(clean_text)
  text.append(clean_text)

text

text[0]

text[1]

#Label counts for each attribute
labelcountlist = []
for x in data.columns:
        labelcountlist.append((len(data[x].unique())))
labelcount = pd.DataFrame({'Attribute': data.columns, 'Count': labelcountlist})
print(labelcount)

#STORING ALL THOSE ATTRIBUTES WITH LESS THAN 100 LABELS FOR COMPREHENSIBLE VISUALIZATION USING BAR GRAPHS
#AlSO DISPLAYS THE COUNT OF EVERY LABEL IN EACH ATTRIBUTE
print(labelcount[labelcount['Count'] < 100])
count = 0
label = []
for x in data.columns:
    if len(data[x].unique()) < 100:
        print('\n' + x + '\n----------\n' + str(list(data[x].unique())) + "\n")
        print(data[x].value_counts())
        label.append(x)

data.head(5)

data['job_description'].head(5)

label.remove('fraudulent')
print(label)

#FUNCTION TO PLOT ATTRIBUTE vs KEY LABEL GRAPHS FOR ATTRIBUTES IN label[]
import seaborn as sns
import matplotlib.pyplot as plt
def plots(lab1,lab2):

    #lab1 = label[0]
    #lab2 = 'fraudulent'
    sns.set(rc={'figure.figsize':(20,40)})
    ax = sns.countplot(data = data,x=data[lab1],hue=data[lab2])

    for p in ax.patches:
       ax.annotate('{:.0f}'.format(p.get_height()), (p.get_x()+0.25, p.get_height()+0.01))
    plt.xticks(rotation=90)

plots(label[0],'fraudulent')#telecommuting



plots(label[1],'fraudulent')#has_company_logo

plots(label[2],'fraudulent')#has_questions

plots(label[3],'fraudulent')#employement_type

plots(label[4],'fraudulent')#required_experience

plots(label[5],'fraudulent')#required_education

plots(label[6],'fraudulent')#industry

realcount = (data['fraudulent']==0).sum() #Number of real applications
fakecount = (data['fraudulent']==1).sum() #Number of fake applications


# FUNCTION TO CALCULATE THE NUMBER OF NOT SPECIFIED ENTRIES IN VARIOUS ATTRIBUTES ALONG WITH THE RATIO OF NOT SPECIFIED TO REAL AND FAKE APPLICATIONS

def not_specified(labelname,name):
    df_real = pd.DataFrame(data[labelname].loc[data['fraudulent']==0])
    notspecreal = (df_real[labelname]=='Not Specified').sum()
    print(name +'\n-----------------\n\nREAL\n-----------\nNumber of Real applications that have not specified ' + name + ' = {:.0f}'.format(notspecreal))
    print('Number of Real applications = {:.0f}'.format(realcount))
    print('Ratio (Not Specified Real applications / Real applications) = {:.6f}'.format(notspecreal/realcount))
    df_fake = pd.DataFrame(data[labelname].loc[data['fraudulent']==1])
    notspecfake = (df_fake[labelname]=='Not Specified').sum()
    print('\n\nFAKE\n-----------\nNumber of Fake applications that have not specified ' + name + ' = {:.0f}'.format(notspecfake))
    print('Number of Fake applications = {:.0f}'.format(fakecount))
    print('Ratio (Not Specified Fake applications / Fake applications) = {:.6f}'.format(notspecfake/fakecount))

for i in data.columns:
    not_specified(i,i.upper())
    print('\n')

#FUNCTION TO RETURN THE 20 MOST FREQUENTLY OCCURING WORDS IN REAL/FAKE APPLCATIONS GIVEN THE ATTRIBUTE

#GIVEN WHETHER AN APPLICATION IS REAL OR FAKE, THE PROBABILITY OF THE WORD APPEARING IN THAT CATEGORY IS DIPLAYED

def frequent(lab,key):

    list_of_words = []
    if key == "real":
        f=0
        count = realcount
    else:
        f=1
        count = fakecount

    for i in (data[lab].loc[data['fraudulent']==f]):
        list_of_words.append((' '.join(dict.fromkeys(i.split()))))

    rand = ' '.join(list_of_words)
    listx = list(rand.split(" "))
    ratiolist = list(pd.Series(listx).value_counts()/count)
    _count = pd.DataFrame(pd.Series(listx).value_counts())
    _count. rename(columns = {_count.columns[0]:'Count'}, inplace = True)
    _count['Probability'] = ratiolist
    print("Frequently appearing words in " + lab + " of " + key + " applications")
    print(_count.head(20))
    list_of_words.clear()

frequent('location','real')
frequent('location','fake')

frequent('department','real')
frequent('department','fake')

#frequent('salary_range','real')
#frequent('salary_range','fake')

frequent('company_profile','real')
frequent('company_profile','fake')

frequent('description','real')
frequent('description','fake')

frequent('requirements','real')
frequent('requirements','fake')

frequent('requirements','real')
frequent('requirements','fake')

frequent('industry','real')
frequent('industry','fake')

from sklearn import preprocessing
le = preprocessing.LabelEncoder()
#ASSIGNS NUMBER TO EVERY LABEL
for i in data.columns:
    le.fit(data[i])
    data[i]=le.transform(data[i])

data.head(15)

from sklearn.model_selection import train_test_split
X=data.drop(['fraudulent'],axis=1)
Y=data["fraudulent"]
X_train,X_test,Y_train,Y_test = (train_test_split(X, Y, test_size=0.25, shuffle=True))

#FUNCTION TO TRAIN THE MODEL, PREDICT THE LABELS FOR TEST SAMPLES AND CALCULATE THE ACCURACY AND PRECISION
from sklearn import metrics
import time

def traintest(model,modelname):

    start = time.time()
    print("\n------------------\nMODEL - "+ modelname + "\n-----------------\n")

    #Training the model
    model.fit(X_train, Y_train)

    #Predicting
    Y_pred = model.predict(X_test)

    #Calculating the accuracy
    accuracy = metrics.accuracy_score(Y_test, Y_pred)
    print("Accuracy = " + '{:.2f}%'.format(accuracy*100))

    #Calculating the precision
    precision = metrics.precision_score(Y_test, Y_pred)
    print("Precision = " + '{:.2f}%'.format(precision*100))

    #Total Time
    end = time.time() - start
    print("Time = " + '{:.2f}s'.format(end))

#ACCURACY ALONG WITH THE TIME IS NOTED FOR THIS PURPOSE

from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.ensemble import RandomForestClassifier

import warnings
warnings.filterwarnings('ignore')

traintest(GaussianNB(),"NAIVE BAYES")
traintest(DecisionTreeClassifier(),"DECISION TREE")
traintest(RandomForestClassifier(),"RANDOM FOREST")
traintest(KNeighborsClassifier(),"KNN")
traintest(SVC(),"SVM")
traintest(LogisticRegression(solver='liblinear'),"LOGISITC REGRESSION")
