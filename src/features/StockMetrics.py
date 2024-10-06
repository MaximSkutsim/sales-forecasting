class InventoryMetrics:
    """
    A class to calculate various inventory metrics such as GMV, gross margin, GMROI,
    inventory turnover, and turnover period for a list of products.

    Attributes:
        products (list of dict): List of dictionaries, each representing a product,
        containing price, cost, starting and ending inventory values, and quantities sold.
    """
    def __init__(self, products):
        """
        Initializes the InventoryMetrics object with a list of products, each containing
        price, cost, starting and ending inventory values, and quantities sold.

        Args:
            products (list of dict): List of dictionaries, each representing a product.
            Each dictionary should contain:
                - 'name' (str): Name of the product.
                - 'price' (float): Selling price per unit.
                - 'cost' (float): Cost per unit.
                - 'quantity_sold' (int): Number of units sold.
                - 'inventory_start' (float): Value of inventory at the start of the period.
                - 'inventory_end' (float): Value of inventory at the end of the period.
        """
        self.products = products

    def gmv(self):
        """Calculates the total Gross Merchandise Value (GMV).

        Returns:
            float: The total GMV, which is the sum of the product of price and quantity sold for each product.
        """
        gmv = sum(product['price'] * product['quantity_sold'] for product in self.products)
        return round(gmv, 2)

    def gross_margin(self):
        """Calculates the total Gross Margin.

        Returns:
            tuple: A tuple containing:
                - margin (float): The total Gross Margin, which is the difference between total revenue and total costs.
                - margin_percentage (float): The Gross Margin percentage, calculated as (margin / total revenue) * 100.
                  If total revenue is zero, returns 0 for the percentage.
        """
        gmv = self.gmv()
        total_cost = sum(product['cost'] * product['quantity_sold'] for product in self.products)
        margin = gmv - total_cost
        margin_percentage = (margin / gmv * 100) if gmv > 0 else 0
        return margin, round(margin_percentage, 2)

    def average_inventory_cost(self):
        """Calculates the total Average Inventory Cost.

        Returns:
            float: The total Average Inventory Cost, which is the sum of the average of starting
                   and ending inventory values for each product.
        """
        total_average_inventory = sum((product['inventory_start'] + product['inventory_end']) / 2 for product in self.products)
        return total_average_inventory

    def gmroi(self):
        """Calculates the total Gross Margin Return on Investment (GMROI).

        Returns:
            float: The GMROI, calculated as gross margin divided by average inventory cost.
                   If average inventory cost is zero, returns 0.
        """
        margin, _ = self.gross_margin()
        average_inventory_cost = self.average_inventory_cost()
        gmroi = (margin / average_inventory_cost) if average_inventory_cost > 0 else 0
        return round(gmroi, 2)

    def inventory_turnover(self):
        """Calculates the total Inventory Turnover.

        Returns:
            float: The Inventory Turnover, calculated as total cost of goods sold divided by
                   average inventory cost. If average inventory cost is zero, returns 0.
        """
        cost_of_goods_sold = sum(product['cost'] * product['quantity_sold'] for product in self.products)
        average_inventory_cost = self.average_inventory_cost()
        inventory_turnover = (cost_of_goods_sold / average_inventory_cost) if average_inventory_cost > 0 else 0
        return round(inventory_turnover, 2)

    def turnover_period(self):
        """Calculates the total Turnover Period (in days).

        Returns:
            float: The Turnover Period, calculated as 365 divided by Inventory Turnover.
                   If Inventory Turnover is zero, returns 0.
        """
        inventory_turnover = self.inventory_turnover()
        turnover_period = (365 / inventory_turnover) if inventory_turnover > 0 else 0
        return round(turnover_period, 2)
