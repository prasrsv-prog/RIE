class AssetAnalyzer:

    def analyze_size(self, size: int) -> str:

        mb = size / (1024 * 1024)

        if mb < 1:
            return "Small"

        if mb < 10:
            return "Medium"

        if mb < 100:
            return "Large"

        return "Very Large"