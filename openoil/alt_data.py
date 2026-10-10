"""Alternative data — AIS, COT proxy, refinery."""

class AlternativeData:
    def pull(self) -> Dict:
        return {"ais_hormuz": 0, "cot_bias": 0.0, "refinery_outages": []}
