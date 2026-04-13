from energy import EnergyDisplay


class TestFormatKw:
    # Positive values: 4 digits available
    def test_small_positive(self):
        assert EnergyDisplay.format_kw(1.5) == "1.500"

    def test_small_positive_precision(self):
        assert EnergyDisplay.format_kw(9.999) == "9.999"

    def test_zero(self):
        assert EnergyDisplay.format_kw(0.0) == "0.000"

    def test_boundary_at_10(self):
        assert EnergyDisplay.format_kw(10.0) == "10.00"

    def test_medium_positive(self):
        assert EnergyDisplay.format_kw(45.6) == "45.60"

    def test_boundary_at_100(self):
        assert EnergyDisplay.format_kw(100.0) == "100"

    def test_large_positive(self):
        assert EnergyDisplay.format_kw(999.0) == "999"

    # Negative values: minus sign takes 1 char, leaving 3
    def test_small_negative(self):
        assert EnergyDisplay.format_kw(-0.04) == "-0.04"

    def test_small_negative_boundary(self):
        assert EnergyDisplay.format_kw(-9.99) == "-9.99"

    def test_medium_negative(self):
        assert EnergyDisplay.format_kw(-10.5) == "-10.5"

    def test_medium_negative_boundary(self):
        assert EnergyDisplay.format_kw(-99.9) == "-99.9"

    def test_large_negative(self):
        assert EnergyDisplay.format_kw(-100.0) == "-100"

    def test_large_negative_value(self):
        assert EnergyDisplay.format_kw(-999.0) == "-999"
