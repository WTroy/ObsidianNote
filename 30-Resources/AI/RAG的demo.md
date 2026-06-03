---
title: RAG的demo
source: 有道云笔记
imported: true
---

Retrieval-Augmented Generation (RAG) 是⼀种结合了检索和⽣成的⽅法。它利⽤⼀个检索器（通常是⼀个向量检
索模型）来从⼀个⼤型⽂档库中找到相关信息，然后使⽤⼀个⽣成模型（如  GPT-3 ）来基于检索到的信息⽣成回答

```bash
conda create -n rag-env python=3.8
conda activate rag-env
pip install transformers==4.10.0
conda install -c pytorch faiss-cpu=1.7.1  # 或者使⽤  faiss-gpu 版本，如果有  GPU
conda install numpy=1.19.2
```

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

```python
from transformers import DPRQuestionEncoder, DPRContextEncoder,
pipeline
import faiss
import numpy as np
# 初始化编码器
question_encoder = DPRQuestionEncoder.from_pretrained("facebook/dpr-
question_encoder-single-nq-base")
context_encoder = DPRContextEncoder.from_pretrained("facebook/dpr-ctx_encoder-
single-nq-base")
# 从⽂件中读取⽂档库
with open('documents.txt', 'r', encoding='utf-8') as f:
documents = [line.strip() for line in f.readlines()]
```

```python
# 编码⽂档库
context_vectors = [context_encoder.encode(doc) for doc in documents]
index = faiss.IndexFlatIP(context_vectors[0].shape[0])
index.add(np.array(context_vectors))
```

步骤  3 ：检索相关⽂档

```python
# 输⼊查询
query = "What is RAG?"
# 将查询编码为向量
query_vector = question_encoder.encode(query)
# 检索最相关的⽂档
D, I = index.search(np.array([query_vector]), k=3)  # 检索前 3 个最相关的⽂档
retrieved_docs = [documents[i] for i in I[0]]
```

步骤  4 ：整合检索到的⽂档

```python
# 将检索到的⽂档整合成⼀个输⼊序列
# 假设我们使⽤简单的拼接⽅式
context = " ".join(retrieved_docs)
```

步骤  5 ：⽣成回答

```python
# 使⽤⽣成模型⽣成回答
reader = pipeline("question-answering", model="facebook/dpr-reader-single-nq-
base")
inputs = {"question": query, "context": context}
answer = reader(inputs)
```

以下是完整代码示例，展示如何从⽂件中读取⽂档库并实现  RAG ：

```python
print(f"Question: {query}")
print(f"Answer: {answer['answer']}")
```

完整代码示例

```python
from transformers import DPRQuestionEncoder, DPRContextEncoder,
pipeline
import faiss
import numpy as np
# 初始化编码器
question_encoder = DPRQuestionEncoder.from_pretrained("facebook/dpr-
question_encoder-single-nq-base")
context_encoder = DPRContextEncoder.from_pretrained("facebook/dpr-ctx_encoder-
single-nq-base")
# 从⽂件中读取⽂档库
with open('documents.txt', 'r', encoding='utf-8') as f:
documents = [line.strip() for line in f.readlines()]
# 编码⽂档库
context_vectors = [context_encoder.encode(doc) for doc in documents]
index = faiss.IndexFlatIP(context_vectors[0].shape[0])
index.add(np.array(context_vectors))
# 输⼊查询
query = "What is RAG?"
# 将查询编码为向量
query_vector = question_encoder.encode(query)
# 检索最相关的⽂档
D, I = index.search(np.array([query_vector]), k=3)  # 检索前 3 个最相关的⽂档
retrieved_docs = [documents[i] for i in I[0]]
# 将检索到的⽂档整合成⼀个输⼊序列
context = " ".join(retrieved_docs)
```

通过上述修改，可以从⽂件中读取⽂档库，并使⽤  RAG 模型进⾏问答。这种⽅式更灵活，可以⽅便地管理和更新⽂档
库。如果有任何问题或需要进⼀步的帮助，请告诉我。

```python
# 使⽤⽣成模型⽣成回答
reader = pipeline("question-answering", model="facebook/dpr-reader-single-nq-
base")
inputs = {"question": query, "context": context}
answer = reader(inputs)
print(f"Question: {query}")
print(f"Answer: {answer['answer']}")
```

总结
