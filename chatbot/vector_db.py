import os
import shutil
from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain.prompts import ChatPromptTemplate

load_dotenv()

# OpenAI API 키 로드
openai_api_key = os.getenv('OPENAI_API_KEY')

if not openai_api_key:
    raise ValueError("OPENAI_API_KEY 환경 변수가 설정되지 않았습니다.")

# 절확한 경로 설정
PROJECT_ROOT = "/Users/parkchangyu/PROJECT/3rd_PROJECT"
TXT_FILE_PATH = os.path.join(PROJECT_ROOT, "recco", "chatbot", "data", "preprocessed_texts.txt")
VECTOR_DB_PATH = os.path.join(PROJECT_ROOT, "recco", "chatbot", "data", "vector_db")

print(f"현재 작업 디렉토리: {os.getcwd()}")
print(f"텍스트 파일 경로: {TXT_FILE_PATH}")
print(f"벡터 DB 경로: {VECTOR_DB_PATH}")

def get_template():
    """프롬프트 템플릿 반환"""
    template = '''
    아래는 인사 및 법률 관련 문서 내용입니다:
    {context}

    위 문서를 기반으로 다음 질문에 답해주세요.
    질문: {question}
    '''
    return template

def recreate_vector_db():
    """기존 벡터 DB를 삭제하고 새로 생성"""
    if os.path.exists(VECTOR_DB_PATH):
        print(f"기존 벡터 DB 삭제: {VECTOR_DB_PATH}")
        shutil.rmtree(VECTOR_DB_PATH)
    return True

class VectorDB:
    _instance = None
    _vectorstore = None
    _embedding_model = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self):
        if VectorDB._instance is not None:
            raise Exception("이 클래스는 싱글톤입니다!")
        else:
            VectorDB._instance = self
            self._initialize()

    def _initialize(self):
        try:
            print("\n=== 벡터 DB 초기화 시작 ===")
            
            # 임베딩 모델 초기화
            if self._embedding_model is None:
                print("임베딩 모델 초기화...")
                self._embedding_model = OpenAIEmbeddings(openai_api_key=openai_api_key)
            
            # 항상 새로운 벡터 DB 생성
            recreate_vector_db()
            self._create_vector_db()
                
        except Exception as e:
            print(f"초기화 중 오류: {str(e)}")
            raise

    def _create_vector_db(self):
        print("\n=== 새로운 벡터 DB 생성 시작 ===")
        try:
            # 텍스트 파일 읽기
            with open(TXT_FILE_PATH, "r", encoding="utf-8") as f:
                raw_text = f.read()
                print(f"로드된 텍스트 크기: {len(raw_text)} 문자")
                if len(raw_text) == 0:
                    raise ValueError("텍스트 파일이 비어있습니다!")

            # 텍스트 분할
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=500,
                chunk_overlap=100,
                separators=["\n\n", "\n", ".", " ", ""]
            )
            docs = text_splitter.create_documents([raw_text])
            print(f"생성된 문서 청크 수: {len(docs)}")
            if len(docs) == 0:
                raise ValueError("문서 청크가 생성되지 않았습니다!")

            # 벡터 DB 생성
            self._vectorstore = Chroma.from_documents(
                documents=docs,
                embedding=self._embedding_model,
                persist_directory=VECTOR_DB_PATH
            )
            self._vectorstore.persist()
            print("벡터 DB 생성 및 저장 완료")
            
            # 테스트 검색
            test_docs = self.similarity_search("휴가", k=3)
            print(f"\n=== 테스트 검색 결과 ===")
            print(f"검색된 문서 수: {len(test_docs)}")
            for i, doc in enumerate(test_docs):
                print(f"\n문서 {i+1}:")
                print(doc.page_content[:200])
            
        except Exception as e:
            print(f"벡터 DB 생성 중 오류: {str(e)}")
            raise

    def similarity_search(self, query: str, k: int = 5):
        if self._vectorstore is None:
            raise ValueError("벡터 DB가 초기화되지 않았습니다")
        return self._vectorstore.similarity_search(query, k=k)

    def get_relevant_documents(self, query: str):
        docs = self.similarity_search(query)
        print(f"\n=== 검색 결과 ===")
        print(f"검색어 '{query}'에 대한 결과 수: {len(docs)}")
        for i, doc in enumerate(docs):
            print(f"\n문서 {i+1}:")
            print(doc.page_content[:200])
        return docs

def get_vector_db():
    instance = VectorDB.get_instance()
    return instance.get_relevant_documents

if __name__ == "__main__":
    # 테스트 실행
    retriever = get_vector_db()
    docs = retriever("휴가")
    print(f"검색된 문서 수: {len(docs)}")