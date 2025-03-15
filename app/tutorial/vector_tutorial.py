# 1. HuggingFace 임베딩 모델 불러오기 (예: E5-base 모델 사용)
import os

from dotenv import load_dotenv
from langchain.chains import RetrievalQA
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_groq import ChatGroq

load_dotenv()

groq_key = os.getenv("GROQ_API_KEY")

llm = ChatGroq(groq_api_key=groq_key, model="llama-3.2-3b-preview")

# 로컬에 모델이 있는 경우 경로 입력 가능, 없으면 Hugging Face Hub에서 다운로드
embeddings = HuggingFaceEmbeddings(
    model_name="all-MiniLM-L6-v2", model_kwargs={"device": "cpu"}
)  # GPU 사용 시 'cuda'

texts = [
    "지원자는 카카오페이 소프트웨어 엔지니어입니다.",
    "지원자는 93년생입니다.",
]  # 임베딩할 문서들
# 각 문서를 임베딩하여 FAISS 인덱스 생성
vector_store = FAISS.from_texts(texts, embedding=embeddings)

# 3. 질의에 대한 유사 문서 검색 및 RAG QA 수행
query = "what is the applicant's job?"
# 질의를 임베딩하고 벡터 유사도 검색으로 관련 문서  k개 반환
retrieved_docs = vector_store.similarity_search(query, k=3)


qa_chain = RetrievalQA.from_chain_type(
    llm, chain_type="stuff", retriever=vector_store.as_retriever()
)
answer = qa_chain.invoke(query)
print(answer)
