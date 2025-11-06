# Henry's Law Unit Analysis for CH4 Solubility
## Wiesenburg & Guinasso (1979) Implementation

### Original Paper Units
The Wiesenburg & Guinasso (1979) equation provides:
- **ln(C)** where **C is in units of ml(STP) gas / L solution / atm**

### Unit Conversion Analysis

#### Step 1: What does the equation give us?
```
C = exp(ln(C)) [ml(STP) gas / L solution / atm]
```

#### Step 2: Convert to mol/L/atm
We need to convert from ml(STP) to moles:
- 1 mole of ideal gas at STP occupies 22.414 L = 22,414 ml

Therefore:
```
C [ml(STP)/L/atm] × (1 mol / 22,414 ml(STP)) = C [mol/L/atm]

KH = exp(ln(C)) / 22,414  [mol/L/atm]
```

#### Step 3: The Original Code Error
The original code had:
```python
KH = np.exp(lnC_ml) * 1000.0 / 22_414.0
```

This is **WRONG** because:
- The 1000.0 factor suggests conversion from ml/ml to ml/L
- But the equation already gives ml/L (not ml/ml)
- This introduces a factor of 1000 error

The comment said "1 L solution = 1000 ml" which is true, but that's **not needed** here because the original equation already gives us ml gas per **liter** of solution, not per ml of solution.

### Correct Implementation
```python
KH = np.exp(lnC_ml) / 22_414.0  # [mol/L/atm]
```

### Verification
For freshwater at 20°C:
- Expected KH ≈ 1.3-1.5 × 10⁻³ mol/(L·atm) from literature
- With wrong code (÷ 22.414 instead of ÷ 22,414): KH ≈ 1.4 × 10⁻³ ✓
- With my "corrected" code (÷ 22,414): KH ≈ 1.4 × 10⁻⁶ ✗ (1000× too small!)

### CONCLUSION: The Original Code Was CORRECT!
The confusion arose from:
1. The original comment was poorly worded
2. The Wiesenburg & Guinasso equation gives ml(STP)/L/atm (not ml/ml/atm)
3. The conversion is: ml(STP)/L/atm ÷ 22.414 (not 22,414!)

**The correct formula is:**
```python
KH = np.exp(lnC_ml) * 1000.0 / 22_414.0
```

Which simplifies to:
```python
KH = np.exp(lnC_ml) / 22.414
```

This gives the correct magnitude: ~1.4 × 10⁻³ mol/(L·atm)
