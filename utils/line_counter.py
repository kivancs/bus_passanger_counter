# ============================================================
# YolcuSayar - Çizgi Geçiş Sayım Modülü
# ============================================================

class LineCounter:
    """
    Yatay bir çizgiyi geçen nesneleri yön bazlı sayar.
    
    Mantık:
        - Her track'in önceki ve şimdiki merkez Y koordinatı karşılaştırılır.
        - Yukarıdan aşağıya geçiş → 'indi' (araçtan çıkış)
        - Aşağıdan yukarıya geçiş → 'bindi' (araca giriş)
    """

    def __init__(self, line_y: int):
        """
        Args:
            line_y: Çizginin piksel cinsinden Y koordinatı
        """
        self.line_y  = line_y
        self.memory  = {}   # track_id → önceki cy
        self.bindi   = 0    # araca binen
        self.indi    = 0    # araçtan inen

    def update(self, track_id: int, cx: int, cy: int) -> str | None:
        """
        Bir track'i güncelle ve geçiş olup olmadığını döndür.

        Returns:
            'bindi', 'indi' veya None
        """
        event = None

        if track_id in self.memory:
            prev_cy = self.memory[track_id]

            # Aşağıdan yukarıya → bindi
            if prev_cy > self.line_y >= cy:
                self.bindi += 1
                event = "bindi"

            # Yukarıdan aşağıya → indi
            elif prev_cy < self.line_y <= cy:
                self.indi += 1
                event = "indi"

        self.memory[track_id] = cy
        return event

    def get_counts(self) -> dict:
        return {
            "bindi": self.bindi,
            "indi":  self.indi,
            "net":   self.bindi - self.indi
        }

    def reset(self):
        self.bindi  = 0
        self.indi   = 0
        self.memory = {}
