from flask import Flask, render_template, request, jsonify
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
import math
from wtforms.validators import DataRequired


def load_vocabulary():
    vocab = {}
    with open('TF-IDF/vocab.txt', 'r') as f:
        vocab_terms = f.readlines()
    with open('TF-IDF/idf_values.txt', 'r') as f:
        idf_values = f.readlines()
    
    for (term,idf_value) in zip(vocab_terms, idf_values):
        vocab[term.strip()] = int(idf_value.strip())
    
    return vocab


def load_document():
    documents = []
    with open('TF-IDF/document_data.txt', 'r') as f:
        documents = f.readlines()
    documents = [document.strip().split() for document in documents]

    print('Number of documents: ', len(documents))
    print('Sample document: ', documents[0])
    return documents

def load_inverted_index():
    inverted_index={}
    with open('TF-IDF/inverted1.txt', 'r') as f:
        inverted_index_terms = f.readlines()

    for row_num in range(0,len(inverted_index_terms),2):
        term = inverted_index_terms[row_num].strip()
        documents = inverted_index_terms[row_num+1].strip().split()
        inverted_index[term] = documents
    
    print('Size of inverted index: ', len(inverted_index))
    return inverted_index
def load_ques():
    with open("qdata/qData/qlink.txt",'r')as f:
        links=f.readlines()
    return links




vocabularies=load_vocabulary()#dictionary having terms and their idf values
docs=load_document()#name of the question as a string
inverted_indices=load_inverted_index()#dictionary of words mapped into its the docs it is present in
qlinks=load_ques()
#get_tf_dictinary returns the tf value of the term
def get_tf_dictionary(term):
    tf_values = {}
    if term in inverted_indices:
        for document in inverted_indices[term]:
            if document not in tf_values:
                tf_values[document] = 1
            else:
                tf_values[document] += 1
                
    for document in tf_values:
        tf_values[document] /= len(docs[int(document)])
    
    return tf_values

#return the log(number of documents/idf value obtained from idf.txt)
def get_idf_value(term):
     return math.log(len(docs)/vocabularies[term])

    
    
def calculate_sorted_order_of_docs(query_terms):
    potential_documents = {}
    ans=[]
    for term in query_terms:
        if vocabularies[term] == 0:
            continue
        tf_values_by_document = get_tf_dictionary(term)
        idf_value = get_idf_value(term)
        print(term,tf_values_by_document,idf_value)
        for document in tf_values_by_document:
            if document not in potential_documents:
                potential_documents[document] = tf_values_by_document[document] * idf_value
            potential_documents[document] += tf_values_by_document[document] * idf_value

    print(potential_documents)
    # divite by the length of the query terms
    for document in potential_documents:
        potential_documents[document] /= len(query_terms)

    potential_documents = dict(sorted(potential_documents.items(), key=lambda item: item[1], reverse=True))
    if (len(potential_documents) == 0):
            print("No matching question found. Please search with more relevant terms.")

        # Printing ans
        # print("The Question links in Decreasing Order of Relevance are: \n")
    for doc_index in potential_documents:
            # print("Question Link:", Qlink[int(
            #     doc_index) - 1], "\tScore:", potential_docs[doc_index])
            ans.append({"Question Link": qlinks[int(
                doc_index) - 1][:-2], "Score": potential_documents[doc_index]})
    return ans



app = Flask(__name__)
app.config['SECRET_KEY'] = 'subrat4564332'


class SearchForm(FlaskForm):
    search = StringField('Enter your search term', validators=[DataRequired()])
    submit = SubmitField('Search')


@app.route("/search", methods=['POST'])
def search():
    form = SearchForm(request.form)
    if form.validate():
        query = form.search.data.strip()
        query_terms = [term.lower() for term in query.split()]
        results = calculate_sorted_order_of_docs(query_terms)[:20:]
        return render_template('index.html', form=form, results=results, query=query)
    return render_template('index.html', form=form, results=[])


@app.route("/", methods=['GET'])
def home():
    form = SearchForm()
    return render_template('index.html', form=form, results=[])


