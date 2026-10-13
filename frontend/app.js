// Centralized API configuration
const API_BASE_URL = 'http://127.0.0.1:5000/api';

// Example: Fetching products using the base URL variable
async function fetchProducts() {
    try {
        const response = await fetch(`${API_BASE_URL}/products`);
        const products = await response.json();
        renderProductsTable(products);
    } catch (error) {
        console.error("Error fetching products:", error);
    }
}

// Example: Adding a new product
async function addProduct(productData) {
    try {
        const response = await fetch(`${API_BASE_URL}/products`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(productData)
        });
        const result = await response.json();
        console.log(result.message);
    } catch (error) {
        console.error("Error adding product:", error);
    }
}