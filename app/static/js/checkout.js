document.addEventListener('DOMContentLoaded', function() {
    const shippingMethodRadios = document.querySelectorAll('input[name="shipping_method"]');
    const omnivaDiv = document.getElementById('omniva_pickup_point_div');
    const shippingCostElement = document.getElementById('shipping-cost');
    const totalPriceElement = document.getElementById('total-price');
    const productTotal = parseFloat(window.orderData.productTotal);
    const omnivaCost = parseFloat(window.orderData.omnivaCost);

    function updatePrices() {
        const selectedMethod = document.querySelector('input[name="shipping_method"]:checked').value;
        let shippingCost = 0;

        if (selectedMethod === 'omniva') {
            shippingCost = omnivaCost;
            omnivaDiv.style.display = 'block';
        } else {
            shippingCost = 0;
            omnivaDiv.style.display = 'none';
        }

        const newTotalPrice = productTotal + shippingCost;

        shippingCostElement.textContent = `€${shippingCost.toFixed(2)}`;
        totalPriceElement.textContent = `€${newTotalPrice.toFixed(2)}`;
    }

    shippingMethodRadios.forEach(radio => {
        radio.addEventListener('change', updatePrices);
    });

    // Initial update to set the correct values on page load
    updatePrices();
});
