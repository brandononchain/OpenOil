"""
OpenOil Memory Graph
Lightweight persistent graph for analyses, news, EIA events, and trade outcomes.
Stores nodes with metadata and retrieves similar historical analogs via keyword overlap + recency.
"""

import json
import os
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
import networkx as nx

MEMORY_FILE = os.getenv("MEMORY_FILE", "openoil_memory.json")

class MemoryGraph:
    def __init__(self, path: str = MEMORY_FILE):
        self.path = path
        self.G = nx.DiGraph()
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
        self.G.add_node(
            node_id,
            type=node_type,
            content=content,
            timestamp=ts,
            iso=datetime.utcfromtimestamp(ts).isoformat()
        )
        self.save()

    def add_edge(self, src: str, dst: str, relation: str = "related"):
        if src in self.G and dst in self.G:
            self.G.add_edge(src, dst, relation=relation)
            self.save()

    def query_similar(self, query_text: str, node_type: Optional[str] = None, limit: int = 5) -> List[Dict]:
        """Simple keyword overlap retrieval. Replace with embeddings later."""
        if not query_text:
            return []
        q_words = set(query_text.lower().split())
        candidates = []
        for nid, data in self.G.nodes(data=True):
            if node_type and data.get("type") != node_type:
                continue
            content_str = json.dumps(data.get("content", {})).lower()
            c_words = set(content_str.split())
            overlap = len(q_words & c_words)
            if overlap > 0:
                recency = 1.0 / (1.0 + (time.time() - data.get("timestamp", 0)) / 86400)
                score = overlap * 0.7 + recency * 0.3
                candidates.append({
                    "id": nid,
                    "type": data.get("type"),
                    "score": round(score, 3),
                    "content": data.get("content"),
                    "iso": data.get("iso")
                })
        candidates.sort(key=lambda x: x["score"], reverse=True)
        return candidates[:limit]

    def recent(self, node_type: Optional[str] = None, limit: int = 10) -> List[Dict]:
        nodes = []
        for nid, data in self.G.nodes(data=True):
            if node_type and data.get("type") != node_type:
                continue
            nodes.append({
                "id": nid,
                "type": data.get("type"),
                "content": data.get("content"),
                "iso": data.get("iso"),
                "timestamp": data.get("timestamp")
            })
        nodes.sort(key=lambda x: x.get("timestamp", 0), reverse=True)
        return nodes[:limit]

    def stats(self) -> Dict:
        return {
            "nodes": self.G.number_of_nodes(),
            "edges": self.G.number_of_edges(),
            "types": list(set(nx.get_node_attributes(self.G, "type").values()))
        }
