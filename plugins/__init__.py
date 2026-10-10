"""
OpenOil Plugin Architecture
Simple dynamic discovery for agents and data connectors.
Place plugins in the plugins/ directory.
"""

import os
import importlib.util
import sys
from typing import Dict, List, Any, Callable
from pathlib import Path

PLUGIN_DIR = Path(__file__).parent / "plugins"

class PluginRegistry:
    def __init__(self):
        self.agents: Dict[str, Callable] = {}
        self.connectors: Dict[str, Callable] = {}
        self.load_plugins()

    def load_plugins(self):
        if not PLUGIN_DIR.exists():
            PLUGIN_DIR.mkdir(exist_ok=True)
            return
        for file in PLUGIN_DIR.glob("*.py"):
            if file.name.startswith("_"):
                continue
            try:
                spec = importlib.util.spec_from_file_location(file.stem, file)
                mod = importlib.util.module_from_spec(spec)
                sys.modules[file.stem] = mod
                spec.loader.exec_module(mod)
                if hasattr(mod, "register_agent"):
                    name, fn = mod.register_agent()
                    self.agents[name] = fn
                if hasattr(mod, "register_connector"):
                    name, fn = mod.register_connector()
                    self.connectors[name] = fn
            except Exception as e:
                print(f"Failed to load plugin {file}: {e}")

    def get_agents(self) -> Dict:
        return self.agents

    def get_connectors(self) -> Dict:
        return self.connectors

registry = PluginRegistry()

def register_agent(name: str, fn: Callable):
    registry.agents[name] = fn

def register_connector(name: str, fn: Callable):
    registry.connectors[name] = fn
