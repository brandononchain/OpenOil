"""
OpenOil Memory Graph
Lightweight persistent graph for analyses, news, EIA events, and trade outcomes.
Stores nodes with metadata and retrieves similar historical analogs via keyword + embedding.
"""

import json
import os
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
import networkx as nx

try:
    from sentence_transformers import SentenceTransformer
    HAS_EMBED = True
except Exception:
    HAS_EMBED = False

MEMORY_FILE = os.getenv("MEMORY_FILE", "openoil_memory.json")

class MemoryGraph:
    def __init__(self, path: str = MEMORY_FILE):
        self.path = path
        self.G = nx.DiGraph()
        self.embedder = SentenceTransformer("all-MiniLM-L6-v2") if HAS_EMBED else None
        self.load()

    def load(self):
        if os.path.exists(self.path):
            try:
                with open(self.path, "r") as f:
                    data = json.load(f)
                    self.G = nx.node_link_graph(data)
            except Exception:
                self.G = nx.DiGraph()
        else:
            self.G = nx.DiGraph()

    def save(self):
        try:
            data = nx.node_link_data(self.G)
            with open(self.path, "w") as f:
                json.dump(data, f, default=str, indent=2)
        except Exception as e:
            print(f"Memory save failed: {e}")

    def add_node(self, node_id: str, node_type: str, content: Dict, timestamp: Optional[float] = None):
        ts = timestamp or time.time()
        emb = None
        if self.embedder:
            try:
                text = json.dumps(content)[:512]
                emb = self.embedder.encode(text).tolist()
            except Exception:
                emb = None
        self.G.add_node(
            node_id,
            type=node_type,
            content=content,
            timestamp=ts,
            iso=datetime.utcfromtimestamp(ts).isoformat(),
            embedding=emb
        )
        self.save()

    def add_edge(self, src: str, dst: str, relation: str = "related"):
        if src in self.G and dst in self.G:
            self.G.add_edge(src, dst, relation=relation)
            self.save()

    def query_similar(self, query_text: str, node_type: Optional[str] = None, limit: int = 5) -> List[Dict]:
        if not query_text:
            return []
        q_words = set(query_text.lower().split())
        candidates = []
        query_emb = None
        if self.embedder:
            try:
                query_emb = self.embedder.encode(query_text)
            except Exception:
                query_emb = None
        for nid, data in self.G.nodes(data=True):
            if node_type and data.get("type") != node_type:
                continue
            content_str = json.dumps(data.get("content", {})).lower()
            c_words = set(content_str.split())
            overlap = len(q_words & c_words) / max(1, len(q_words))
            emb_sim = 0.0
            if query_emb is not None and data.get("embedding"):
                try:
                    import numpy as np
                    emb_sim = float(np.dot(query_emb, data["embedding"]) / (np.linalg.norm(query_emb) * np.linalg.norm(data["embedding"]) + 1e-9))
                except Exception:
                    emb_sim = 0.0
            recency = 1.0 / (1.0 + (time.time() - data.get("timestamp", 0)) / 86400)
            score = overlap * 0.3 + emb_sim * 0.5 + recency * 0.2
            if score > 0.05:
                candidates.append({
                    "id": nid,
                    "type": data.get("type"),
                    "content": data.get("content"),
                    "score": round(score, 3),
                    "timestamp": data.get("iso")
                })
        candidates.sort(key=lambda x: x["score"], reverse=True)
        return candidates[:limit]
