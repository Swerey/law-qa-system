import os
import time
from http.client import responses

import requests
from langchain_core.embeddings import Embeddings

class DashScopeEmbeddings(Embeddings):
    def __init__(self, model="text-embedding-v4", api_key=None):
        self.model = model
        self.api_key = api_key or os.getenv("DASHSCOPE_API_KEY")
        if not self.api_key:
            raise ValueError("Please set DASHSCOPE_API_KEY environment variable")

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        BATCH_SIZE = 10
        all_embeddings = []

        for i in range(0, len(texts), BATCH_SIZE):
            batch = texts[i:i + BATCH_SIZE]
            response = requests.post(
                "https://dashscope.aliyuncs.com/api/v1/services/embeddings/text-embedding/text-embedding",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "input": {"texts": batch},
                },
                timeout=60,
            )
            if response.status_code != 200:
                raise Exception(
                    f"Embedding API 返回 {response.status_code}: {response.text}"
                )
            result = response.json()

            items = sorted(
                result["output"]["embeddings"],
                key=lambda x: x["text_index"],
            )
            all_embeddings.extend(item["embedding"] for item in items)

            time.sleep(0.2)

        return all_embeddings

    def embed_query(self, text: str) -> list[float]:
        return self.embed_documents([text])[0]
