from sentence_transformers import SentenceTransformer
import numpy as np
from sklearn.cluster import KMeans
model=SentenceTransformer('all-MiniLM-L6-v2')

def get_embeddings(keywords):
    try:
        vecs=model.encode(keywords,convert_to_numpy=True,show_progress_bar=False)
        return np.array(vecs)
    except Exception as e:
        print("embedding err:",e)
        return np.zeros((len(keywords),384))

def make_clusters(keywords):
    if len(keywords)==0:
        return {}
    vecs=get_embeddings(keywords)
    n=1
    if len(keywords)<=5: n=1
    elif len(keywords)<=10:n=2
    elif len(keywords)<=20:n=3
    else: n=4

    if n==1:
        return {"cluster_1":keywords}

    k=KMeans(n_clusters=n,random_state=0,n_init="auto")
    k.fit(vecs)
    groups={}
    for i,lab in enumerate(k.labels_):
        key="cluster_"+str(lab+1)
        if key not in groups:
            groups[key]=[]
        groups[key].append(keywords[i])
    return groups
