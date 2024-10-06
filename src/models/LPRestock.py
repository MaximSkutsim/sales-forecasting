from typing import Tuple
import math
import json
import os
import pandas as pd
import pulp

class GreedyRestock:
    """
    A class to allocate a budget for restocking products using a greedy algorithm.
    """
    def __init__(self, json_path: str):
        """
        Initializes the GreedyRestock class by loading products from a JSON file.

        Args:
            json_path (str): The file path to the JSON file containing product data.

        Raises:
            FileNotFoundError: If the provided JSON file does not exist.
            ValueError: If the JSON data cannot be decoded or if the product list is empty.
            RuntimeError: If an unexpected error occurs while reading the JSON file.
        """
        if not os.path.exists(json_path):
            raise FileNotFoundError(f"The provided JSON file '{json_path}' does not exist.")
        try:
            with open(json_path, 'r') as f:
                self.products = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON data could not be decoded: {e}")
        except Exception as e:  # Обработка любых непредвиденных ошибок
            raise RuntimeError(f"An unexpected error occurred while reading the JSON file: {e}")

        if not self.products:
            raise ValueError("The product list is empty.")
        self._validate()

    def _validate(self):
        """
        Validates the structure and data of the products loaded from the JSON file.

        This method checks each product to ensure that:

        1. All required keys are present in each product dictionary.
        2. The `price` is a positive number greater than zero.
        3. The `cost` is a positive number greater than zero.
        4. The `price` is greater than or equal to the `cost`.
        5. The `current_stock` is a non-negative number (i.e., zero or greater).
        6. The `storage_time` is a positive number greater than zero.
        7. The `percentiles` dictionary contains all required week keys (`1w`, `2w`, `3w`, `4w`).
        8. Each week in the `percentiles` dictionary contains all required percentile values
        (`5`, `10`, `25`, `50`, `75`, `90`, `95`).

        Raises:
            ValueError: If any required keys are missing, or if any numeric values
                        (price, cost, current stock, storage time) are invalid according to the rules above.
        """
        # Обязательные ключи для каждого продукта
        required_keys = ['price', 'cost', 'current_stock', 'storage_time', 'percentiles']
        # Обязательные недели и перцентили
        required_weeks = ['1w', '2w', '3w', '4w']
        required_percentiles = ['5', '10', '25', '50', '75', '90', '95']
        for idx, product in enumerate(self.products):
            # Проверяем наличие всех обязательных ключей
            for key in required_keys:
                if key not in product:
                    raise ValueError(f"Missing required key '{key}' in product at index {idx}")
            # Проверка, что price и cost — положительные числа и price >= cost
            if product['price'] <= 0:
                raise ValueError(f"Product at index {idx} has an invalid price: {product['price']}")
            if product['cost'] <= 0:
                raise ValueError(f"Product at index {idx} has an invalid cost: {product['cost']}")
            if product['price'] < product['cost']:
                raise ValueError(f"Product at index {idx} has a price less than the cost.")
            # Проверка, что current_stock — неотрицательное число
            if product['current_stock'] < 0:
                raise ValueError(f"Product at index {idx} has an invalid current stock: {product['current_stock']}")
            # Проверка, что storage_time — положительное число
            if product['storage_time'] <= 0:
                raise ValueError(f"Product at index {idx} has an invalid storage time: {product['storage_time']}")
            # Проверка наличия всех обязательных недель в percentiles
            percentiles = product['percentiles']
            if not isinstance(percentiles, dict):
                raise ValueError(f"Product at index {idx} has an invalid percentiles format. Expected a dictionary.")
            for week in required_weeks:
                if week not in percentiles:
                    raise ValueError(f"Missing required week '{week}' in percentiles for product at index {idx}")
                # Проверка наличия всех обязательных перцентилей для каждой недели
                for perc in required_percentiles:
                    if perc not in percentiles[week]:
                        raise ValueError(f"Missing required percentile '{perc}' for week '{week}' in product at index {idx}")


class LPRestock(GreedyRestock):
    def allocate(
        self, budget: int, weeks: int, optimization_goal: str = "profit"
    ) -> Tuple[pulp.LpProblem, pd.DataFrame]:
        if budget <= 0:
            raise ValueError("Бюджет должен быть положительным числом")
        if weeks < 1 or weeks > 4:
            raise ValueError("Количество недель должно быть от 1 до 4")
        if optimization_goal not in ["profit", "revenue"]:
            raise ValueError("Цель оптимизации должна быть 'profit' или 'revenue'")
        # Создаем задачу линейного программирования
        prob = pulp.LpProblem("Restock_Optimization", pulp.LpMaximize)
        # Создаем переменные решения
        decision_vars = {}
        binary_vars = {}
        for product in self.products:
            sku_id = product["sku_id"]
            current_stock = product["current_stock"]
            for percentile in product["percentiles"][f"{weeks}w"]:
                forecast = product["percentiles"][f"{weeks}w"][percentile]
                if forecast - current_stock > 0:
                    var_name = f"sku_{sku_id}_{percentile}"
                    decision_vars[var_name] = pulp.LpVariable(
                        var_name, 
                        lowBound=0, 
                        upBound=forecast - current_stock,
                        cat='Integer'
                    )
                    binary_vars[f"bin_{var_name}"] = pulp.LpVariable(
                        f"bin_{var_name}", 
                        cat='Binary'
                    )
        # Целевая функция с учетом oos_risk и storage_score
        if optimization_goal == "profit":
            prob += pulp.lpSum(
                round((product["price"] - product["cost"]) / product["cost"] * 
                    (1 - (int(percentile) / 100)) * 
                    math.log10(product['storage_time']), 4) * 
                decision_vars[f"sku_{product['sku_id']}_{percentile}"]
                for product in self.products
                for percentile in product["percentiles"][f"{weeks}w"]
                if product["percentiles"][f"{weeks}w"][percentile] - product["current_stock"] > 0
            )
        else:  # revenue
            prob += pulp.lpSum(
                round((product["price"] / product["cost"]) * 
                    (1 - (int(percentile) / 100)) * 
                    max((product["percentiles"][f"{weeks}w"][percentile] - product['current_stock']), 0) *
                    math.log10(product['storage_time']), 4) * 
                decision_vars[f"sku_{product['sku_id']}_{percentile}"]
                for product in self.products
                for percentile in product["percentiles"][f"{weeks}w"]
                if product["percentiles"][f"{weeks}w"][percentile] - product["current_stock"] > 0
            )
        # Ограничение бюджета
        prob += pulp.lpSum(
            product["cost"] * decision_vars[f"sku_{product['sku_id']}_{percentile}"]
            for product in self.products
            for percentile in product["percentiles"][f"{weeks}w"]
            if product["percentiles"][f"{weeks}w"][percentile] - product["current_stock"] > 0
        ) <= budget, "budget_constraint"
        # Ограничения выбора одного процентиля для каждого SKU
        for product in self.products:
            sku_id = product["sku_id"]
            valid_percentiles = [p for p in product["percentiles"][f"{weeks}w"] if product["percentiles"][f"{weeks}w"][p] - product["current_stock"] > 0]
            if valid_percentiles:
                prob += pulp.lpSum(
                    binary_vars[f"bin_sku_{sku_id}_{percentile}"]
                    for percentile in valid_percentiles
                ) == 1, f"sku_{sku_id}_single_selection_constraint"
            else:
                # Добавляем фиктивное ограничение для SKU без допустимых процентилей
                prob += 0 == 0, f"sku_{sku_id}_single_selection_constraint"
        # Ограничения спроса
        for product in self.products:
            sku_id = product["sku_id"]
            current_stock = product["current_stock"]
            for percentile in product["percentiles"][f"{weeks}w"]:
                forecast = product["percentiles"][f"{weeks}w"][percentile]
                if forecast - current_stock > 0:
                    var_name = f"sku_{sku_id}_{percentile}"
                    prob += decision_vars[var_name] <= (forecast - current_stock) * binary_vars[f"bin_{var_name}"], f"{var_name}_demand_constraint"
        # Решаем задачу
        prob.solve()
        # Создаем DataFrame с результатами
        results = []
        for product in self.products:
            sku_id = product["sku_id"]
            current_stock = product["current_stock"]
            for percentile in product["percentiles"][f"{weeks}w"]:
                forecast = product["percentiles"][f"{weeks}w"][percentile]
                if forecast - current_stock > 0:
                    var_name = f"sku_{sku_id}_{percentile}"
                    if var_name in decision_vars and binary_vars[f"bin_{var_name}"].value() == 1:
                        allocated_qty = int(decision_vars[var_name].value())
                        if allocated_qty > 0:  # Добавлена проверка на положительное количество
                            allocated_budget = allocated_qty * product["cost"]
                            expected_revenue = allocated_qty * product["price"]
                            expected_profit = expected_revenue - allocated_budget
                            results.append({
                                "sku_id": sku_id,
                                "percentile": int(percentile),
                                "price": product["price"],
                                "cost": product["cost"],
                                "allocated_qty": allocated_qty,
                                "allocated_budget": allocated_budget,
                                "expected_profit": expected_profit,
                                "expected_revenue": expected_revenue
                            })

        allocation_df = pd.DataFrame(results)
        # allocation_df["percentile"] = allocation_df["percentile"].astype('int64')
        # allocation_df["percentile"] = allocation_df["percentile"].astype(int)  # Преобразуем столбец в int
        allocation_df = allocation_df.sort_values(["allocated_budget", "sku_id"], ascending=[False, True])
        return prob, allocation_df

# if __name__ == "__main__":

#     from tabulate import tabulate

#     products = [
#         {
#             "sku_id": "0001",
#             "price": 317,
#             "cost": 288,
#             "current_stock": 22,
#             "storage_time": 76,
#             "percentiles": {
#                 "1w": {"5": 3, "10": 9, "25": 16, "50": 19, "75": 22, "90": 28, "95": 35},
#                 "2w": {"5": 9, "10": 10, "25": 22, "50": 28, "75": 31, "90": 37, "95": 43},
#                 "3w": {"5": 11, "10": 14, "25": 32, "50": 36, "75": 43, "90": 53, "95": 62},
#                 "4w": {"5": 12, "10": 24, "25": 33, "50": 46, "75": 53, "90": 60, "95": 71},
#             },
#         },
#         {
#             "sku_id": "0002",
#             "price": 158,
#             "cost": 143,
#             "current_stock": 8,
#             "storage_time": 65,
#             "percentiles": {
#                 "1w": {"5": 6, "10": 7, "25": 9, "50": 19, "75": 23, "90": 25, "95": 32},
#                 "2w": {"5": 12, "10": 18, "25": 24, "50": 27, "75": 29, "90": 30, "95": 39},
#                 "3w": {"5": 17, "10": 24, "25": 34, "50": 37, "75": 47, "90": 54, "95": 62},
#                 "4w": {"5": 23, "10": 33, "25": 42, "50": 45, "75": 51, "90": 58, "95": 65},
#             },
#         },
#     ]

#     lpr = LPRestock("products.json")

#     lpr.products = products

#     lp_prob, allocation_df = lpr.allocate(2000, 1, "profit")

#     print('Allocation df:')
#     print(tabulate(allocation_df, headers="keys", floatfmt="0.2f"))

#     total_cost = allocation_df["allocated_budget"].sum()
#     total_expected_profit = allocation_df["expected_profit"].sum()
#     print(f"\nОбщая сумма закупки: {total_cost}")
#     print(f"Общая ожидаемая прибыль: {total_expected_profit}")

#     print(f"\nЦелевая функция: {lp_prob.objective}")

#     print("\n Переменные решения:")
#     print(lp_prob.variables())

#     print("\nОграничения задачи линейного программирования:")
#     for name, constraint in lp_prob.constraints.items():
#         print(f"{name}: {constraint}")

        ### Output:
# Allocation df:
#   sku_id    percentile    price    cost    allocated_qty    allocated_budget    expected_profit    expected_revenue
# --------  ------------  -------  ------  ---------------  ------------------  -----------------  ------------------
#     0002            50      158     143               11                1573                165                1738
#     0001            90      317     288                1                 288                 29                 317

# Общая сумма закупки: 1861
# Общая ожидаемая прибыль: 194

# Целевая функция: 0.0189*sku_0001_90 + 0.0095*sku_0001_95 + 0.1426*sku_0002_25 + 0.0951*sku_0002_50 + 0.0475*sku_0002_75 + 0.019*sku_0002_90 + 0.0095*sku_0002_95

#  Переменные решения: [
#     bin_sku_0001_90, bin_sku_0001_95, bin_sku_0002_25, bin_sku_0002_50, bin_sku_0002_75, bin_sku_0002_90, bin_sku_0002_95,
#     sku_0001_90, sku_0001_95, sku_0002_25, sku_0002_50, sku_0002_75, sku_0002_90, sku_0002_95
# ]

# Ограничения задачи линейного программирования:
# budget_constraint: 288*sku_0001_90 + 288*sku_0001_95 + 143*sku_0002_25 + 143*sku_0002_50 + 143*sku_0002_75 + 143*sku_0002_90 + 143*sku_0002_95 <= 2000
# sku_0001_single_selection_constraint: bin_sku_0001_90 + bin_sku_0001_95 = 1
# sku_0002_single_selection_constraint: bin_sku_0002_25 + bin_sku_0002_50 + bin_sku_0002_75 + bin_sku_0002_90 + bin_sku_0002_95 = 1
# sku_0001_90_demand_constraint: -6*bin_sku_0001_90 + sku_0001_90 <= 0
# sku_0001_95_demand_constraint: -13*bin_sku_0001_95 + sku_0001_95 <= 0
# sku_0002_25_demand_constraint: -bin_sku_0002_25 + sku_0002_25 <= 0
# sku_0002_50_demand_constraint: -11*bin_sku_0002_50 + sku_0002_50 <= 0
# sku_0002_75_demand_constraint: -15*bin_sku_0002_75 + sku_0002_75 <= 0
# sku_0002_90_demand_constraint: -17*bin_sku_0002_90 + sku_0002_90 <= 0
# sku_0002_95_demand_constraint: -24*bin_sku_0002_95 + sku_0002_95 <= 0