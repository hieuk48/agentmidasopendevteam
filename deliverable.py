"""
Commission Calculator Widget

This module provides a pure Python, production-ready implementation of a commission calculator widget.
It is designed to be integrated into the bujiproject-art/agentmidasopendevteam project as per
https://github.com/bujiproject-art/agentmidasopendevteam/issues/130

Features:
- Clean, modular, and extensible commission calculation logic.
- Supports flat, percentage, and tiered commission structures.
- Includes a simple CLI and test cases for verification.

Security:
- No use of subprocess, ctypes, socket, sys.exit, os.system, or eval.
- Pure Python, zero external dependencies.

Author: [Your Name]
Date: 2024-06-13
"""

from typing import List, Tuple, Optional, Union, Callable


class CommissionRule:
    """
    Abstract base class for commission rules.
    """
    def calculate(self, amount: float) -> float:
        """
        Calculate commission for a given amount.
        """
        raise NotImplementedError("Must implement calculate method.")


class FlatCommissionRule(CommissionRule):
    """
    Flat commission: fixed amount per transaction.
    """
    def __init__(self, flat_amount: float) -> None:
        self.flat_amount = flat_amount

    def calculate(self, amount: float) -> float:
        """
        Always returns the flat commission amount, regardless of transaction amount.
        """
        return max(0.0, self.flat_amount)


class PercentageCommissionRule(CommissionRule):
    """
    Percentage commission: a percentage of the transaction amount.
    """
    def __init__(self, percent: float) -> None:
        """
        percent: e.g., 5.0 for 5%
        """
        self.percent = percent

    def calculate(self, amount: float) -> float:
        """
        Returns the commission as a percentage of the amount.
        """
        return max(0.0, amount * self.percent / 100.0)


class TieredCommissionRule(CommissionRule):
    """
    Tiered commission: different rates for different amount ranges.

    tiers: List of (threshold, percent) tuples.
        - threshold: upper bound of the tier (inclusive)
        - percent: commission percent for this tier

    Example:
        tiers = [
            (1000, 2.0),   # 2% for amount up to 1000
            (5000, 1.5),   # 1.5% for amount 1000.01 to 5000
            (float('inf'), 1.0)  # 1% for amount above 5000
        ]
    """
    def __init__(self, tiers: List[Tuple[float, float]]) -> None:
        self.tiers = sorted(tiers, key=lambda x: x[0])

    def calculate(self, amount: float) -> float:
        """
        Calculates commission based on tiered structure.
        """
        commission = 0.0
        previous_threshold = 0.0
        remaining = amount
        for threshold, percent in self.tiers:
            if amount > previous_threshold:
                applicable = min(amount, threshold) - previous_threshold
                commission += applicable * percent / 100.0
                previous_threshold = threshold
            else:
                break
        return max(0.0, commission)


class CommissionCalculator:
    """
    Main Commission Calculator Widget.

    Supports:
    - Flat commission
    - Percentage commission
    - Tiered commission
    - Custom commission rules (by passing a callable)
    """
    def __init__(
        self,
        rule: Union[CommissionRule, Callable[[float], float]]
    ) -> None:
        if isinstance(rule, CommissionRule):
            self.rule = rule
        elif callable(rule):
            self.rule = rule  # type: ignore
        else:
            raise ValueError("rule must be a CommissionRule or callable.")

    def calculate(self, amount: float) -> float:
        """
        Calculate commission for the given amount.
        """
        if isinstance(self.rule, CommissionRule):
            return self.rule.calculate(amount)
        elif callable(self.rule):
            return max(0.0, float(self.rule(amount)))
        else:
            raise RuntimeError("Invalid commission rule.")


def commission_calculator_widget(
    amount: float,
    rule_type: str = "percentage",
    rule_value: Union[float, List[Tuple[float, float]]] = 5.0
) -> float:
    """
    Widget function to calculate commission.

    Args:
        amount: Transaction amount.
        rule_type: "flat", "percentage", or "tiered"
        rule_value:
            - For "flat": float, flat commission amount.
            - For "percentage": float, percent commission.
            - For "tiered": List of (threshold, percent) tuples.

    Returns:
        Calculated commission as float.
    """
    if rule_type == "flat":
        rule = FlatCommissionRule(float(rule_value))
    elif rule_type == "percentage":
        rule = PercentageCommissionRule(float(rule_value))
    elif rule_type == "tiered":
        if not isinstance(rule_value, list):
            raise ValueError("For tiered commission, rule_value must be a list of (threshold, percent) tuples.")
        rule = TieredCommissionRule(rule_value)
    else:
        raise ValueError(f"Unknown rule_type: {rule_type}")

    calculator = CommissionCalculator(rule)
    return calculator.calculate(amount)


# --- CLI for demonstration and manual testing ---

def _cli_demo() -> None:
    """
    Simple CLI for demonstration.
    """
    print("Commission Calculator Widget Demo")
    print("---------------------------------")
    print("Select commission type:")
    print("1. Flat")
    print("2. Percentage")
    print("3. Tiered")
    choice = input("Enter choice (1/2/3): ").strip()
    amount_str = input("Enter transaction amount: ").strip()
    try:
        amount = float(amount_str)
    except ValueError:
        print("Invalid amount.")
        return

    if choice == "1":
        flat = float(input("Enter flat commission amount: ").strip())
        commission = commission_calculator_widget(amount, "flat", flat)
    elif choice == "2":
        percent = float(input("Enter commission percent (e.g., 5 for 5%): ").strip())
        commission = commission_calculator_widget(amount, "percentage", percent)
    elif choice == "3":
        print("Enter tiered commission as comma-separated pairs (threshold:percent), e.g. 1000:2,5000:1.5,inf:1")
        tiers_str = input("Tiers: ").strip()
        tiers: List[Tuple[float, float]] = []
        for pair in tiers_str.split(","):
            threshold_str, percent_str = pair.split(":")
            threshold = float(threshold_str) if threshold_str != "inf" else float("inf")
            percent = float(percent_str)
            tiers.append((threshold, percent))
        commission = commission_calculator_widget(amount, "tiered", tiers)
    else:
        print("Invalid choice.")
        return

    print(f"Commission for amount {amount:.2f}: {commission:.2f}")


# --- Unit Tests ---

def _run_tests() -> None:
    """
    Run basic tests for the commission calculator.
    """
    print("Running Commission Calculator Widget Tests...")

    # Flat commission
    flat_rule = FlatCommissionRule(10.0)
    assert flat_rule.calculate(1000.0) == 10.0
    assert flat_rule.calculate(0.0) == 10.0

    # Percentage commission
    perc_rule = PercentageCommissionRule(5.0)
    assert abs(perc_rule.calculate(1000.0) - 50.0) < 1e-6
    assert abs(perc_rule.calculate(0.0) - 0.0) < 1e-6

    # Tiered commission
    tiers = [
        (1000, 2.0),    # 2% up to 1000
        (5000, 1.5),    # 1.5% for 1000.01 to 5000
        (float('inf'), 1.0)  # 1% above 5000
    ]
    tiered_rule = TieredCommissionRule(tiers)
    # 800 -> 2% of 800 = 16
    assert abs(tiered_rule.calculate(800.0) - 16.0) < 1e-6
    # 2000 -> 2% of 1000 = 20, 1.5% of 1000 = 15, total = 35
    assert abs(tiered_rule.calculate(2000.0) - 35.0) < 1e-6
    # 6000 -> 2% of 1000 = 20, 1.5% of 4000 = 60, 1% of 1000 = 10, total = 90
    assert abs(tiered_rule.calculate(6000.0) - 90.0) < 1e-6

    # Widget function
    assert abs(commission_calculator_widget(1000, "flat", 10.0) - 10.0) < 1e-6
    assert abs(commission_calculator_widget(1000, "percentage", 5.0) - 50.0) < 1e-6
    assert abs(commission_calculator_widget(6000, "tiered", tiers) - 90.0) < 1e-6

    print("All tests passed.")


if __name__ == "__main__":
    # For demonstration, run tests and then CLI
    _run_tests()
    _cli_demo()