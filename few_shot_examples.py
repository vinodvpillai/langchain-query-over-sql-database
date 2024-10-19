class SqlSamples:

    examples = {
    
        "order-details": [
            {
                "input": "Get order details along with customer information",
                "query": """SELECT 
                            o.orderNumber,
                            o.orderDate,
                            o.status,
                            c.customerName,
                            c.contactLastName,
                            c.contactFirstName,
                            c.phone,
                            od.productCode,
                            od.quantityOrdered,
                            od.priceEach
                        FROM orders o
                        JOIN customers c ON o.customerNumber = c.customerNumber
                        JOIN orderdetails od ON o.orderNumber = od.orderNumber
                        ORDER BY o.orderDate DESC
                        LIMIT 5
                """
            },
            {
                "input": "Get product sales report per customer",
                "query": """SELECT 
                            c.customerName,
                            p.productName,
                            od.quantityOrdered,
                            od.priceEach,
                            (od.quantityOrdered * od.priceEach) AS totalValue
                        FROM customers c
                        JOIN orders o ON c.customerNumber = o.customerNumber
                        JOIN orderdetails od ON o.orderNumber = od.orderNumber
                        JOIN products p ON od.productCode = p.productCode
                        ORDER BY c.customerName, totalValue DESC
                        LIMIT 5"""
            },
            {
                "input": "Get a list of customers who have not placed any orders",
                "query": """SELECT 
                            c.customerNumber,
                            c.customerName,
                            c.contactLastName,
                            c.contactFirstName
                        FROM customers c
                        LEFT JOIN orders o ON c.customerNumber = o.customerNumber
                        WHERE o.orderNumber IS NULL
                        LIMIT 5"""
            },
            {
                "input": "Find the total sales per product",
                "query": """SELECT 
                            p.productName,
                            SUM(od.quantityOrdered) AS totalQuantitySold,
                            SUM(od.quantityOrdered * od.priceEach) AS totalRevenue
                        FROM products p
                        JOIN orderdetails od ON p.productCode = od.productCode
                        GROUP BY p.productCode
                        ORDER BY totalRevenue DESC
                        LIMIT 5"""
            },
            {
                "input": "Get order information with delayed shipping",
                "query": """SELECT 
                            o.orderNumber,
                            o.orderDate,
                            o.requiredDate,
                            o.shippedDate,
                            c.customerName,
                            c.phone,
                            o.status
                        FROM orders o
                        JOIN customers c ON o.customerNumber = c.customerNumber
                        WHERE o.shippedDate > o.requiredDate
                        ORDER BY o.shippedDate DESC
                        LIMIT 5"""
            }
        ]

    }


order_few_shot = SqlSamples.examples["order-details"]