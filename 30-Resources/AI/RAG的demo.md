---
title: RAG的demo
source: 有道云笔记
imported: true
---

Retrieval-Augmented Generation (RAG) 是⼀种结合了检索和⽣成的⽅法。它利⽤⼀个检索器（通常是⼀个向量检
索模型）来从⼀个⼤型⽂档库中找到相关信息，然后使⽤⼀个⽣成模型（如  GPT-3 ）来基于检索到的信息⽣成回答
conda create -n rag-env python=3.8
conda activate rag-env
pip install transformers==4.10.0
conda install -c pytorch faiss-cpu=1.7.1  # 或者使⽤  faiss-gpu 版本，如果有  GPU
conda install numpy=1.19.2
好的，将⽂档库从⽂件中读取是常⻅的需求。我们可以假设⽂档⽂件是⼀个⽂本⽂件，每⼀⾏代表⼀个⽂档。以下是如
何修改之前的示例代码，以从⽂件中读取⽂档库的内容：
假设⽂档⽂件  documents.txt 的格式如下，每⾏⼀个⽂档：
创建并激活  conda 虚拟环境
假设⽂件格式
Document 1 text1
Document 2 text2
Document 3 text3
修改后的代码
步骤  1 和  2 ：初始化编码器和检索器
python 复制代码 from transformers import DPRQuestionEncoder, DPRContextEncoder,
pipeline
1
import faiss2
import numpy as np3
4
# 初始化编码器5
question_encoder = DPRQuestionEncoder.from_pretrained("facebook/dpr-
question_encoder-single-nq-base")
6
context_encoder = DPRContextEncoder.from_pretrained("facebook/dpr-ctx_encoder-
single-nq-base")
7
8
# 从⽂件中读取⽂档库9
with open('documents.txt', 'r', encoding='utf-8') as f:10
documents = [line.strip() for line in f.readlines()]11

12
# 编码⽂档库13
context_vectors = [context_encoder.encode(doc) for doc in documents]14
index = faiss.IndexFlatIP(context_vectors[0].shape[0])15
index.add(np.array(context_vectors))16
17
步骤  3 ：检索相关⽂档
python 复制代码 # 输⼊查询1
query = "What is RAG?"2
3
# 将查询编码为向量4
query_vector = question_encoder.encode(query)5
6
# 检索最相关的⽂档7
D, I = index.search(np.array([query_vector]), k=3)  # 检索前 3 个最相关的⽂档8
retrieved_docs = [documents[i] for i in I[0]]9
10
步骤  4 ：整合检索到的⽂档
python 复制代码 # 将检索到的⽂档整合成⼀个输⼊序列1
# 假设我们使⽤简单的拼接⽅式2
context = " ".join(retrieved_docs)3
4
步骤  5 ：⽣成回答
python 复制代码 # 使⽤⽣成模型⽣成回答1
reader = pipeline("question-answering", model="facebook/dpr-reader-single-nq-
base")
2
inputs = {"question": query, "context": context}3
answer = reader(inputs)4
5

以下是完整代码示例，展示如何从⽂件中读取⽂档库并实现  RAG ：
print(f"Question: {query}")6
print(f"Answer: {answer['answer']}")7
8
完整代码示例
python 复制代码 from transformers import DPRQuestionEncoder, DPRContextEncoder,
pipeline
1
import faiss2
import numpy as np3
4
# 初始化编码器5
question_encoder = DPRQuestionEncoder.from_pretrained("facebook/dpr-
question_encoder-single-nq-base")
6
context_encoder = DPRContextEncoder.from_pretrained("facebook/dpr-ctx_encoder-
single-nq-base")
7
8
# 从⽂件中读取⽂档库9
with open('documents.txt', 'r', encoding='utf-8') as f:10
documents = [line.strip() for line in f.readlines()]11
12
# 编码⽂档库13
context_vectors = [context_encoder.encode(doc) for doc in documents]14
index = faiss.IndexFlatIP(context_vectors[0].shape[0])15
index.add(np.array(context_vectors))16
17
# 输⼊查询18
query = "What is RAG?"19
20
# 将查询编码为向量21
query_vector = question_encoder.encode(query)22
23
# 检索最相关的⽂档24
D, I = index.search(np.array([query_vector]), k=3)  # 检索前 3 个最相关的⽂档25
retrieved_docs = [documents[i] for i in I[0]]26
27
# 将检索到的⽂档整合成⼀个输⼊序列28
context = " ".join(retrieved_docs)29
30

通过上述修改，可以从⽂件中读取⽂档库，并使⽤  RAG 模型进⾏问答。这种⽅式更灵活，可以⽅便地管理和更新⽂档
库。如果有任何问题或需要进⼀步的帮助，请告诉我。
# 使⽤⽣成模型⽣成回答31
reader = pipeline("question-answering", model="facebook/dpr-reader-single-nq-
base")
32
inputs = {"question": query, "context": context}33
answer = reader(inputs)34
35
print(f"Question: {query}")36
print(f"Answer: {answer['answer']}")37
38
总结